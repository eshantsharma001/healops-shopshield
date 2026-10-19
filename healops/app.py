import os
import sys
import time
import json
import urllib.request
import urllib.error
import subprocess
from flask import Flask, render_template, jsonify, request
from database import log_incident, get_recent_incidents, get_summary_metrics

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

app = Flask(__name__)

# Master autonomous healing toggle
CONFIG = {
    "auto_heal_enabled": True
}

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOPSHIELD_PATH = os.path.join(PROJECT_ROOT, "shopshield", "app.py")

def check_http(url, timeout=1.0):
    """Pings a local HTTP service and returns status and latency."""
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'HealOps-Monitor'})
        with urllib.request.urlopen(req, timeout=timeout) as res:
            latency = round((time.time() - start) * 1000, 1)
            return res.status == 200, res.status, latency
    except urllib.error.HTTPError as e:
        latency = round((time.time() - start) * 1000, 1)
        return False, e.code, latency
    except Exception:
        latency = round((time.time() - start) * 1000, 1)
        return False, 0, latency


@app.route('/')
def dashboard():
    """Renders the HealOps Control Room UI."""
    return render_template('dashboard.html')


@app.route('/api/status')
def get_status():
    """Returns current real-time health across all components."""
    # Check ShopShield (5000)
    ss_healthy, ss_code, ss_lat = check_http("http://127.0.0.1:5000/health", timeout=0.8)
    
    # Check Product Service (5001)
    ps_healthy, ps_code, ps_lat = check_http("http://127.0.0.1:5001/health", timeout=0.8)

    # Fetch Rate Limiter Metrics from ShopShield if alive
    traffic_metrics = {"total_received": 0, "allowed": 0, "shed_blocked": 0}
    if ss_healthy:
        try:
            with urllib.request.urlopen("http://127.0.0.1:5000/api/metrics", timeout=0.5) as res:
                traffic_metrics = json.loads(res.read().decode('utf-8'))
        except Exception:
            pass

    return jsonify({
        "auto_heal_enabled": CONFIG["auto_heal_enabled"],
        "shopshield": {
            "status": "HEALTHY" if ss_healthy else "DOWN",
            "code": ss_code,
            "latency_ms": ss_lat
        },
        "product_service": {
            "status": "HEALTHY" if ps_healthy else ("UNHEALTHY" if ps_code == 500 else "DOWN"),
            "code": ps_code,
            "latency_ms": ps_lat
        },
        "traffic_metrics": traffic_metrics,
        "summary": get_summary_metrics()
    })


@app.route('/api/mode/toggle', methods=['POST'])
def toggle_mode():
    """Toggles autonomous self-healing on or off."""
    CONFIG["auto_heal_enabled"] = not CONFIG["auto_heal_enabled"]
    mode_str = "ENABLED (Autonomous)" if CONFIG["auto_heal_enabled"] else "DISABLED (Manual Diagnosis Only)"
    return jsonify({
        "auto_heal_enabled": CONFIG["auto_heal_enabled"],
        "message": f"Autonomous healing is now {mode_str}"
    })


@app.route('/api/incidents')
def get_incidents():
    """Returns recent incident history."""
    return jsonify({
        "incidents": get_recent_incidents(15),
        "summary": get_summary_metrics()
    })


# -------------------------------------------------------------------------
# CHAOS INJECTION TRIGGERS
# -------------------------------------------------------------------------

@app.route('/api/chaos/crash', methods=['POST'])
def chaos_crash():
    """Crashes the ShopShield patient app."""
    try:
        urllib.request.urlopen("http://127.0.0.1:5000/chaos/crash", timeout=0.5)
    except Exception:
        pass
    return jsonify({"message": "ShopShield process crash injected!"})


@app.route('/api/chaos/toggle-slow', methods=['POST'])
def chaos_slow():
    """Toggles latency in Product Service."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:5001/chaos/set-delay?seconds=1.2", timeout=2.0) as res:
            data = json.loads(res.read().decode('utf-8'))
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chaos/toggle-fail', methods=['POST'])
def chaos_fail():
    """Toggles outage in Product Service."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:5001/chaos/toggle-fail", timeout=2.0) as res:
            data = json.loads(res.read().decode('utf-8'))
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/chaos/traffic-spike', methods=['POST'])
def chaos_spike():
    """Fires 20 rapid requests to simulate a traffic surge."""
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
        problem_type="Traffic Surge / Load Spike",
        detection_time=0.05,
        recovery_time=0.00,
        action_taken=f"Load Shedder triggered: {allowed} allowed, {shed} shed (HTTP 429)",
        status="PROTECTED"
    )
    return jsonify({"allowed": allowed, "shed": shed, "total": 20})


@app.route('/api/chaos/unfixable', methods=['POST'])
def chaos_unfixable():
    """Demonstrates a failure HealOps cannot repair (Missing DB without backup)."""
    log_incident(
        problem_type="Fatal Database Corruption",
        detection_time=0.45,
        recovery_time=0.00,
        action_taken="Emergency Escalation: Auto-repair aborted (No valid backup snapshot found)",
        status="UNRESOLVED (MANUAL_INTERVENTION_REQUIRED)"
    )
    return jsonify({
        "status": "UNRESOLVABLE",
        "diagnosis": "Missing database tables / corrupted schema.",
        "repair_status": "NOT AVAILABLE",
        "reason": "No valid backup snapshot exists. Auto-healing aborted to prevent data destruction."
    })


# -------------------------------------------------------------------------
# MANUAL HEAL ACTIONS (FOR WHEN AUTO-HEAL IS TURNED OFF)
# -------------------------------------------------------------------------

@app.route('/api/heal/shopshield', methods=['POST'])
def heal_shopshield():
    """Manually restarts ShopShield and logs the recovery."""
    start = time.time()
    subprocess.Popen([sys.executable, SHOPSHIELD_PATH])
    
    # Wait until healthy
    time.sleep(1.5)
    recovered = False
    for _ in range(10):
        alive, _, _ = check_http("http://127.0.0.1:5000/health", timeout=0.5)
        if alive:
            recovered = True
            break
        time.sleep(0.5)

    duration = round(time.time() - start, 2)
    if recovered:
        log_incident(
            problem_type="Application Process Crash",
            detection_time=0.8,
            recovery_time=duration,
            action_taken="Watchdog process reboot & health verification",
            status="RESOLVED"
        )
        return jsonify({"success": True, "recovery_time": duration})
    return jsonify({"success": False, "message": "Failed to restart ShopShield"}), 500


@app.route('/api/heal/product-service', methods=['POST'])
def heal_product_service():
    """Restores Product Service to healthy."""
    try:
        # Reset delay to 0 and ensure healthy
        urllib.request.urlopen("http://127.0.0.1:5001/chaos/set-delay?seconds=0", timeout=1.0)
        with urllib.request.urlopen("http://127.0.0.1:5001/health", timeout=1.0) as res:
            data = json.loads(res.read().decode('utf-8'))
            if not data.get("is_healthy", True):
                urllib.request.urlopen("http://127.0.0.1:5001/chaos/toggle-fail", timeout=1.0)
        
        log_incident(
            problem_type="External Service Outage",
            detection_time=1.0,
            recovery_time=0.01,
            action_taken="Circuit Breaker cached fallback served; external service restored",
            status="RESOLVED"
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -------------------------------------------------------------------------
# PUBLIC WEBSITE HEALTH CHECKER (HACKATHON REQUIREMENT #12)
# -------------------------------------------------------------------------

@app.route('/api/tools/check-website', methods=['POST'])
def check_website():
    """Inspects an external public website without attempting unauthorized repairs."""
    target_url = request.json.get('url', '').strip()
    if not target_url.startswith('http'):
        target_url = 'https://' + target_url

    start = time.time()
    try:
        req = urllib.request.Request(target_url, headers={'User-Agent': 'HealOps-Public-Checker'})
        with urllib.request.urlopen(req, timeout=4.0) as res:
            duration = round((time.time() - start) * 1000, 1)
            return jsonify({
                "url": target_url,
                "status": "ONLINE 🟢",
                "http_code": res.status,
                "response_time_ms": duration,
                "repair_permission": "NOT AVAILABLE (External domain - no authorization)"
            })
    except urllib.error.HTTPError as e:
        duration = round((time.time() - start) * 1000, 1)
        return jsonify({
            "url": target_url,
            "status": "ERROR 🔴",
            "http_code": e.code,
            "response_time_ms": duration,
            "repair_permission": "NOT AVAILABLE (No management access provided)"
        })
    except Exception as e:
        return jsonify({
            "url": target_url,
            "status": "UNREACHABLE 🔴",
            "http_code": 0,
            "response_time_ms": 0,
            "repair_permission": "NOT AVAILABLE (No management access provided)"
        })


if __name__ == '__main__':
    print("🛡️ HealOps Control Room running on http://127.0.0.1:5050")
    app.run(port=5050, debug=False)
