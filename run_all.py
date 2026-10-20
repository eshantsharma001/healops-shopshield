import subprocess
import sys
import time
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

print("=" * 65)
print("🛡️  HEALOPS — LAUNCHING COMPLETE ECOSYSTEM")
print("=" * 65)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 1. Start Product Service (5001)
print("1. Starting Product Service (Port 5001)...")
ps = subprocess.Popen([sys.executable, os.path.join(PROJECT_ROOT, "product_service", "app.py")])
time.sleep(1.0)

# 2. Start HealOps Control Room Dashboard (5050)
print("2. Starting HealOps Control Room (Port 5050)...")
dashboard = subprocess.Popen([sys.executable, os.path.join(PROJECT_ROOT, "healops", "app.py")])
time.sleep(1.0)

# 3. Start Watchdog (Supervises ShopShield on 5000)
print("3. Starting Watchdog & ShopShield (Port 5000)...")
watchdog = subprocess.Popen([sys.executable, os.path.join(PROJECT_ROOT, "healops", "watchdog.py")])

print("\n" + "=" * 65)
print("🚀 ALL SYSTEMS ONLINE!")
print("• Live Storefront:    http://127.0.0.1:5000/")
print("• Product Service:    http://127.0.0.1:5001/")
print("• Control Room:       http://127.0.0.1:5050/")
print("Press Ctrl+C to gracefully shut down all services.")
print("=" * 65 + "\n")

try:
    watchdog.wait()
except KeyboardInterrupt:
    print("\nShutting down all HealOps services...")
    watchdog.terminate()
    dashboard.terminate()
    ps.terminate()
    print("All services stopped.")
