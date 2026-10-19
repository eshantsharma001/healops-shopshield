#step 1 import standard py libraries
import time             #measure recovery tume and pause bw checks
import subprocess       #start and restart the shopshield process
import urllib.request   #built-in tool to send http reqs (no pip install needed!)
import urllib.error     #to catch network and HTTP errors
import json             #to parse dashboard status config
import sys              #to catch network errors when the app is down
import os               #for directory and file operations
from database import log_incident

# Configure Windows console for UTF-8 emoji support
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

#step 2 - configuration 
# 
# The healthcheck URL for shopshield 
SHOPSHIELD_HEALTH_URL = "http://127.0.0.1:5000/health"

#how often to check if shopshield is alive (in seconds)
CHECK_INTERVAL_SECONDS = 1.0

#path to shopshield app.py file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
SHOPSHIELD_PATH = os.path.join(PROJECT_ROOT, "shopshield", "app.py")

#var to hold our running shopshield process
shopshiel_process = None

#step 3 - function to start shopshield as a backgrounf process
def start_shopshield():
    """Starts Shopshield in the background using the current python enviornment"""
    global shopshiel_process

    print("\n[WATCHDOG ACTION] Starting ShopShield application...")

    #sys.executable uses the exact same python.exe from my virtual env
    #subprocess.Popen runs it in the background without blocking this script
    shopshiel_process = subprocess.Popen([sys.executable, SHOPSHIELD_PATH])

    #give the server 1.5 sec to bind to port 5000
    time.sleep(1.5)
    print(f"[WATCHDOG ACTION] 🚀 Shopshield launched with Process ID (PID): {shopshiel_process.pid}")

#step 4 func to check if shopshield is alive
def is_shopshiel_healthy():
    """Sends an HTTP GET req to /health. returns true if alive else false if down"""
    try:
        #send a req with a short 1-sec timeout
        with urllib.request.urlopen(SHOPSHIELD_HEALTH_URL, timeout=1.0) as response:
            #if status is 200 , its alive
            return response.status == 200
    except (urllib.error.URLError, ConnectionResetError, TimeoutError, ConnectionAbortedError):
        #if connection is refused or timed out, the app is DOWN.
        return False

def is_auto_heal_enabled():
    """Checks HealOps Dashboard to see if autonomous healing is enabled."""
    try:
        with urllib.request.urlopen("http://127.0.0.1:5050/api/status", timeout=0.4) as res:
            data = json.loads(res.read().decode('utf-8'))
            return data.get("auto_heal_enabled", True)
    except Exception:
        # Default to True if dashboard is not currently open
        return True

#step 5 the self healing supervisor loop
def run_watchdog():
    """Continuously monitors shopshield and auto restart it if it crashse"""
    print("=" * 60)
    print("🛡️ HEALOPS WATCHDOG - SELF HEALING SUPERVISOR ACTIVE")
    print(f"Monitoring: {SHOPSHIELD_HEALTH_URL}")
    print("Press ctrl+c to stop the watchdog.\n")

    #start shopshield initially if it is not already running
    if not is_shopshiel_healthy():
        start_shopshield()
          
    while True:
        # Sleep for our interval (1 second)
        time.sleep(CHECK_INTERVAL_SECONDS)

        #check health
        if is_shopshiel_healthy():
            #all good ! print green heartbeat
            print("[STATUS] 🟢 Shopshield is HEALTHY", flush=True)
        else:
            #incident detected : shopshield has crashed
            crash_detected_time = time.time()
            print("\n" + "!" * 60)
            print("[INCIDENT DETECTED] 🔴 ShopShield is DOWN / CRASHED!")
            print("[DIAGNOSIS] Connection refused on port 5000. Process died.")
            
            # Check if autonomous healing is enabled
            if is_auto_heal_enabled():
                print("[HEALING ACTION] ⚡ Autonomous Mode: Initiating automatic restart sequence...")
                print("!" * 60)            
                
                # Healing step: restart the application
                start_shopshield()
                
                # Verification step: loop until it passes the health check
                recovered = False
                while not recovered:
                    time.sleep(0.5)
                    recovered = is_shopshiel_healthy()

                # Measure real recovery time
                recovery_duration = round(time.time() - crash_detected_time, 2)
                print("*" * 60)
                print(f"[RECOVERED] 🟢 ShopShield restored to HEALTHY status!")
                print(f"[METRIC] ⏱️ Total Recovery Time: {recovery_duration} seconds")
                print("*" * 60 + "\n", flush=True)

                # Persist to SQLite incident ledger
                try:
                    log_incident(
                        problem_type="Application Process Crash",
                        detection_time=0.8,
                        recovery_time=recovery_duration,
                        action_taken="Autonomous Watchdog reboot & verification",
                        status="RESOLVED"
                    )
                except Exception:
                    pass
            else:
                print("[MANUAL MODE ACTIVE] ⏸ Automatic healing paused.")
                print("[ACTION REQUIRED] Awaiting manual approval on HealOps Control Room (http://127.0.0.1:5050)")
                print("!" * 60)
                # Wait until either auto-heal is re-enabled or manual recovery happens
                while not is_shopshiel_healthy() and not is_auto_heal_enabled():
                    time.sleep(1.0)        

#step 6 script entry point
if __name__ == '__main__':
    try:
        run_watchdog()
    except KeyboardInterrupt:
        print("\n[WATCHDOG] Stopping supervisor..")
        if shopshiel_process:
            shopshiel_process.terminate()
        print("[WATCHDOG] Stopped.")
