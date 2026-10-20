# -------------------------------------------------------------------------
# STEP 1: IMPORTS
# -------------------------------------------------------------------------
import time              # For measuring timeouts, backoff sleeps, and cooldowns
import json              # To parse the JSON returned by Product Service
import urllib.request    # Built-in HTTP client
import urllib.error      # To catch connection and HTTP errors

# -------------------------------------------------------------------------
# STEP 2: CONFIGURATION
# -------------------------------------------------------------------------
PRODUCT_SERVICE_URL = "http://127.0.0.1:5001/api/stock"
PRODUCT_SERVICE_DECREMENT_URL = "http://127.0.0.1:5001/api/stock/decrement"
PRODUCT_SERVICE_BATCH_DECREMENT_URL = "http://127.0.0.1:5001/api/stock/decrement/batch"
REQUEST_TIMEOUT_SECONDS = 1.0
MAX_RETRIES = 2
BASE_BACKOFF_SECONDS = 0.2

# In-memory cache storing last known good data for fallback
LOCAL_STOCK_CACHE = {}


# -------------------------------------------------------------------------
# STEP 3: THE CIRCUIT BREAKER CLASS (PROBLEM 3)
# -------------------------------------------------------------------------
class CircuitBreaker:
    """
    Protects the system when Product Service has a prolonged outage.
    States:
      - CLOSED: Service is healthy. All requests flow normally.
      - OPEN: Service has failed repeatedly. Block calls, return fallback instantly.
      - HALF-OPEN: Cooldown passed. Send 1 trial request to check if it recovered.
    """
    def __init__(self, failure_threshold=3, recovery_cooldown=10.0):
        self.state = "CLOSED"                       # Start in healthy CLOSED state
        self.failure_count = 0                      # Count of consecutive errors
        self.failure_threshold = failure_threshold  # Trip after 3 errors
        self.recovery_cooldown = recovery_cooldown  # Wait 10s before testing
        self.last_failure_time = 0.0                # When the circuit tripped OPEN

    def can_request(self):
        """Returns True if request is allowed, False if blocked by Circuit Breaker."""
        # State 1: CLOSED -> Everything is healthy, send request
        if self.state == "CLOSED":
            return True

        current_time = time.time()

        # State 2: OPEN -> Check if 10-second cooldown has passed
        if self.state == "OPEN":
            if current_time - self.last_failure_time >= self.recovery_cooldown:
                print("\n" + "=" * 60)
                print("[CIRCUIT BREAKER] 🟡 Cooldown over! Transitioning to HALF-OPEN (Testing health)...")
                print("=" * 60)
                self.state = "HALF-OPEN"
                return True
            else:
                remaining = round(self.recovery_cooldown - (current_time - self.last_failure_time), 1)
                print(f"[CIRCUIT BREAKER] 🔴 OPEN. Blocking network call. Cooldown: {remaining}s")
                return False

        # State 3: HALF-OPEN -> Allow 1 trial request
        return True

    def record_success(self):
        """Called when a request succeeds to reset the circuit."""
        if self.state in ["HALF-OPEN", "OPEN"]:
            print("\n" + "*" * 60)
            print("[CIRCUIT BREAKER] 🟢 Trial request succeeded! State is now CLOSED.")
            print("*" * 60)
        self.state = "CLOSED"
        self.failure_count = 0

    def record_failure(self):
        """Called when a request fails to track threshold and trip OPEN."""
        self.failure_count += 1
        print(f"[CIRCUIT BREAKER] Failure count: {self.failure_count}/{self.failure_threshold}")

        if self.failure_count >= self.failure_threshold or self.state == "HALF-OPEN":
            self.state = "OPEN"
            self.last_failure_time = time.time()
            print("\n" + "!" * 60)
            print("[CIRCUIT BREAKER] 🔴 CIRCUIT TRIPPED TO OPEN!")
            print(f"[CIRCUIT BREAKER] Blocking external requests for {self.recovery_cooldown}s.")
            print("!" * 60)


# Single global Circuit Breaker instance
circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_cooldown=10.0)


# -------------------------------------------------------------------------
# STEP 4: FETCH FUNCTION USING RETRY + CIRCUIT BREAKER
# -------------------------------------------------------------------------
def fetch_stock_with_retry(product_id):
    """Fetches stock protected by Circuit Breaker, with Retry and Fallback."""
    url = f"{PRODUCT_SERVICE_URL}/{product_id}"

    # 1. Circuit Breaker Guard: Skip network if circuit is OPEN!
    if not circuit_breaker.can_request():
        return get_fallback(product_id)

    # 2. Retry Loop: Try up to 2 times
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'ShopShield-Client'})
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    # Notify circuit breaker that request succeeded
                    circuit_breaker.record_success()

                    # Save in cache for future outages
                    LOCAL_STOCK_CACHE[product_id] = {
                        "stock": data.get("stock", 10),
                        "status": data.get("status", "In Stock"),
                        "source": "LIVE"
                    }
                    return LOCAL_STOCK_CACHE[product_id]

        except (urllib.error.URLError, TimeoutError) as error:
            print(f"[CLIENT] 🟡 Attempt #{attempt} failed: {error}")
            if attempt < MAX_RETRIES:
                sleep_duration = BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
                time.sleep(sleep_duration)

    # If all retries failed, record failure in circuit breaker
    circuit_breaker.record_failure()
    return get_fallback(product_id)


def get_fallback(product_id):
    """Instantly serves cached data or safe default."""
    fallback = LOCAL_STOCK_CACHE.get(
        product_id, 
        {"stock": "Available", "status": "In Stock", "source": "CACHED"}
    ).copy()
    fallback["source"] = "CACHED"
    return fallback


def _post_stock_update(url, payload):
    """Send a purchase update and surface Product Service errors to checkout."""
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "ShopShield-Client"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=3.0) as response:
            data = json.loads(response.read().decode("utf-8"))
            if response.status != 200:
                raise RuntimeError(data.get("error", "Product Service rejected the stock update."))
            return data
    except urllib.error.HTTPError as error:
        try:
            message = json.loads(error.read().decode("utf-8")).get("error", str(error))
        except (ValueError, UnicodeDecodeError):
            message = str(error)
        raise RuntimeError(message) from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise RuntimeError("Product Service is unavailable. Your order was not placed.") from error


def decrement_stock(product_id, quantity):
    """Decrease stock for one purchased product through Product Service."""
    return _post_stock_update(PRODUCT_SERVICE_DECREMENT_URL, {
        "product_id": product_id,
        "quantity": quantity,
    })


def decrement_stock_batch(items):
    """Atomically decrease stock for all items in one order."""
    return _post_stock_update(PRODUCT_SERVICE_BATCH_DECREMENT_URL, {"items": items})