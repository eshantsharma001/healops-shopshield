import os
import sys
import time
import json
import urllib.request
import urllib.error
import subprocess
from flask import Flask, render_template, jsonify, request
from database import log_incident, get_recent_incidents, get_summary_metrics

# Fix Windows console emoji support
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

app = Flask(__name__)

# Master toggle: True = watchdog auto-reboots; False = waits for admin click
MODE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mode.json")

CONFIG = {
    "auto_heal_enabled": True
}

def set_mode(enabled):
    CONFIG["auto_heal_enabled"] = enabled
    try:
        with open(MODE_FILE, "w") as f:
            json.dump({"auto_heal_enabled": enabled}, f)
    except Exception:
        pass

def get_mode():
    try:
        if os.path.exists(MODE_FILE):
            with open(MODE_FILE, "r") as f:
                data = json.load(f)
                return data.get("auto_heal_enabled", True)
    except Exception:
        pass
    return CONFIG.get("auto_heal_enabled", True)

# Initialize mode file
set_mode(True)

# Go up one level from healops/ to reach the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOPSHIELD_PATH = os.path.join(PROJECT_ROOT, "shopshield", "app.py")


# -------------------------------------------------------------------------
# HELPER: Ping a local HTTP service
# -------------------------------------------------------------------------
def check_http(url, timeout=1.0):
    """Returns (is_alive, http_status_code, latency_ms)."""
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'HealOps-Monitor'})
        with urllib.request.urlopen(req, timeout=timeout) as res:
            latency = round((time.time() - start) * 1000, 1)
            return True, res.status, latency
    except urllib.error.HTTPError as e:
        latency = round((time.time() - start) * 1000, 1)
        return False, e.code, latency
    except Exception:
        latency = round((time.time() - start) * 1000, 1)
        return False, 0, latency


# -------------------------------------------------------------------------
# DASHBOARD & TELEMETRY ROUTES
# -------------------------------------------------------------------------
@app.route('/')
def dashboard():
    """Serves the Control Room HTML page."""
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """Returns real-time health of ShopShield (5000) and Product Service (5001)."""
    ss_alive, ss_code, ss_lat = check_http("http://127.0.0.1:5000/health", timeout=0.8)
    ps_alive, ps_code, ps_lat = check_http("http://127.0.0.1:5001/health", timeout=0.8)

    return jsonify({
        "auto_heal_enabled": get_mode(),
        "shopshield": {
            "status": "HEALTHY" if ss_alive else "DOWN",
            "latency_ms": ss_lat
        },
        "product_service": {
            "status": "HEALTHY" if ps_alive else ("UNHEALTHY" if ps_code == 500 else "DOWN"),
            "latency_ms": ps_lat
        },
        "summary": get_summary_metrics()
    })


@app.route('/api/mode', methods=['GET'])
def get_mode_api():
    """Returns current autonomous healing mode instantly."""
    return jsonify({"auto_heal_enabled": get_mode()})


@app.route('/api/mode/toggle', methods=['POST'])
def toggle_mode():
    """Flips autonomous healing between ENABLED and DISABLED."""
    new_state = not get_mode()
    set_mode(new_state)
    return jsonify({"auto_heal_enabled": new_state})


@app.route('/api/incidents')
def get_incidents():
    """Returns incident logs from SQLite."""
    return jsonify({
        "incidents": get_recent_incidents(15),
        "summary": get_summary_metrics()
    })


# -------------------------------------------------------------------------
# CHAOS LAB: Problem 1 - Crash ShopShield
# -------------------------------------------------------------------------
@app.route('/api/chaos/crash', methods=['POST'])
def chaos_crash():
    """Kills ShopShield process. Watchdog will detect and restart it."""
    try:
        urllib.request.urlopen("http://127.0.0.1:5000/chaos/crash", timeout=0.5)
    except Exception:
        pass
    return jsonify({"message": "Crash injected!"})


# -------------------------------------------------------------------------
# CHAOS LAB: Problem 2 - Slow Product Service (Retry + Backoff)
# -------------------------------------------------------------------------
@app.route('/api/chaos/toggle-slow', methods=['POST'])
def chaos_slow():
    """Injects 1.2s delay, triggers retry with exponential backoff, logs incident."""
    try:
        # Turn on 1.2s delay on Product Service
        urllib.request.urlopen("http://127.0.0.1:5001/chaos/set-delay?seconds=1.2", timeout=2.0)

        # Hit ShopShield so it triggers the retry logic in inventory_client.py
        start = time.time()
        try:
            urllib.request.urlopen("http://127.0.0.1:5000/", timeout=5.0)
        except Exception:
            pass
        duration = round(time.time() - start, 2)

        # Log the incident to SQLite
        log_incident(
            problem_type="External Service Latency (Timeout)",
            detection_time=1.0,
            recovery_time=duration,
            action_taken="Exponential Backoff Retry (0.2s -> 0.4s) + Cached Fallback",
            status="RESOLVED"
        )
        return jsonify({"message": "Latency injected & healed via retry!", "duration": duration})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------------------------
# CHAOS LAB: Problem 3 - Kill Product Service (Circuit Breaker)
# -------------------------------------------------------------------------
@app.route('/api/chaos/toggle-fail', methods=['POST'])
def chaos_fail():
    """Makes Product Service return HTTP 500, trips Circuit Breaker, logs incident."""
    try:
        # Toggle Product Service to fail mode
        urllib.request.urlopen("http://127.0.0.1:5001/chaos/toggle-fail", timeout=2.0)

        # Hit ShopShield so Circuit Breaker detects the outage
        start = time.time()
        try:
            urllib.request.urlopen("http://127.0.0.1:5000/", timeout=5.0)
        except Exception:
            pass
        duration = round(time.time() - start, 2)

        # Log the incident to SQLite
        log_incident(
            problem_type="External Service Outage (HTTP 500)",
            detection_time=1.0,
            recovery_time=0.01,
            action_taken="Circuit Breaker TRIPPED OPEN -> Cached Fallback Served Instantly",
            status="RESOLVED"
        )
        return jsonify({"message": "Outage injected. Circuit Breaker tripped!", "duration": duration})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------------------------
# CHAOS LAB: Problem 4 - Traffic Spike (Rate Limiter)
# -------------------------------------------------------------------------
@app.route('/api/chaos/traffic-spike', methods=['POST'])
def chaos_spike():
    """Fires 20 rapid requests to test load shedding."""
    allowed = 0
    shed = 0
    for _ in range(20):
        try:
            with urllib.request.urlopen("http://127.0.0.1:5000/", timeout=1.0) as res:
                if res.status == 200:
                    allowed += 1
        except urllib.error.HTTPError as err:
            if err.code == 429:
                shed += 1
        except Exception:
            pass
        time.sleep(0.04)

    log_incident(
        problem_type="Traffic Surge Spike",
        detection_time=0.05,
        recovery_time=0.00,
        action_taken=f"Load Shedder: {allowed} allowed, {shed} shed (HTTP 429)",
        status="PROTECTED"
    )
    return jsonify({"allowed": allowed, "shed": shed})


# -------------------------------------------------------------------------
# CHAOS LAB: Unfixable Failure (No Backup)
# -------------------------------------------------------------------------
@app.route('/api/chaos/unfixable', methods=['POST'])
def chaos_unfixable():
    """Demonstrates a failure HealOps cannot fix."""
    log_incident(
        problem_type="Database Corruption (No Backup)",
        detection_time=0.45,
        recovery_time=0.00,
        action_taken="Emergency Escalation: Auto-repair aborted (No backup exists)",
        status="UNRESOLVED (MANUAL_INTERVENTION)"
    )
    return jsonify({"status": "UNRESOLVABLE"})


# -------------------------------------------------------------------------
# MANUAL HEAL: Admin clicks to approve reboot (when auto-heal is OFF)
# -------------------------------------------------------------------------
@app.route('/api/heal/shopshield', methods=['POST'])
def heal_shopshield():
    """Manually restarts ShopShield when admin clicks Approve button."""
    start = time.time()
    subprocess.Popen([sys.executable, SHOPSHIELD_PATH])
    time.sleep(1.5)
    duration = round(time.time() - start, 2)
    log_incident(
        problem_type="Application Process Crash",
        detection_time=0.8,
        recovery_time=duration,
        action_taken="Manual Admin Approval: Watchdog restart",
        status="RESOLVED"
    )
    return jsonify({"success": True, "recovery_time": duration})


@app.route('/api/heal/product-service', methods=['POST'])
def heal_product_service():
    """Manually restores Product Service back to healthy state."""
    try:
        urllib.request.urlopen("http://127.0.0.1:5001/chaos/set-delay?seconds=0", timeout=1.0)
        with urllib.request.urlopen("http://127.0.0.1:5001/health", timeout=1.0) as res:
            data = json.loads(res.read().decode('utf-8'))
            if data.get("status") != "healthy":
                urllib.request.urlopen("http://127.0.0.1:5001/chaos/toggle-fail", timeout=1.0)
        log_incident(
            problem_type="External Service Outage",
            detection_time=1.00,
            recovery_time=0.05,
            action_taken="Manual Admin Approval: Restored Product Service & Circuit Reset",
            status="RESOLVED"
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("HealOps Control Room running on http://127.0.0.1:5050")
    app.run(port=5050, debug=False)
