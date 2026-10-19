import time #to track requests timestamps and cleaning up old records
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Allow at most 10 requests per 5-second window from a single IP
RATE_LIMIT_MAX_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 5.0

#in-memeory dictionary tracking IP address -> list of req stamps
# Ex : {"127.0.0.1": [171000.1,171000.4, 171001.2]}
CLIENT_REQUEST_LOG = {}

#Real time metrics counters to display to judges
METRICS = {
    "total_received": 0,
    "allowed": 0,
    "shed_blocked": 0
}

#step 3 rate limiter logic (sliding window)

def is_request_allowed(client_ip):
    """
    checks if a request from client_ip is within the allowed rate limit.
    Returns:
      (True, metrics) -> Req allowed
      (false, metrics) -> traffic spike detected, req SHED (HTTP 429)
    """
    current_time = time.time()
    METRICS["total_received"] += 1

    #get the list of past req timestamps for this IP
    timestamps = CLIENT_REQUEST_LOG.get(client_ip, [])

    #filter out timestamp olderthan our 5-sec window (sliding windo algo)
    cutoff_time = current_time - RATE_LIMIT_WINDOW_SECONDS
    active_timestamps = [t for t in timestamps if t > cutoff_time]

    #check if client has exceed the limit
    if len(active_timestamps) >= RATE_LIMIT_MAX_REQUESTS:

        #spike detected : Load Shedding Activated!
        METRICS["shed_blocked"] += 1
        print(f"[LOAD SHEDDER] 🔴 SPIKE! IP {client_ip} sent {len(active_timestamps)} requests in {RATE_LIMIT_WINDOW_SECONDS}s. Request SHED (429).")
        CLIENT_REQUEST_LOG[client_ip] = active_timestamps
        return False, METRICS

    # req is within safe limits :allow it
    active_timestamps.append(current_time)
    CLIENT_REQUEST_LOG[client_ip] = active_timestamps
    METRICS ["allowed"] += 1
    return True, METRICS



def get_rate_limiter_metrics():
    """ Returns the current traffic metrics for the dashboard."""
    return METRICS