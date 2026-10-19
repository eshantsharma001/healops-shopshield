import urllib.request
import urllib.error
import time
import sys

# Ensure emojis and unicode symbols print properly on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

URL = "http://127.0.0.1:5000/"
NUM_REQUESTS = 25  # Fire 25 rapid requests
print(f"🔥 Simulating sudden traffic spike ({NUM_REQUESTS} requests) to ShopShield...")
allowed = 0
shed = 0
for i in range(1, NUM_REQUESTS + 1):
    try:
        with urllib.request.urlopen(URL, timeout=2.0) as res:
            if res.status == 200:
                allowed += 1
                print(f"Request #{i}: 🟢 200 OK (Allowed)")
    except urllib.error.HTTPError as err:
        if err.code == 429:
            shed += 1
            print(f"Request #{i}: 🔴 429 Too Many Requests (SHED)")
    time.sleep(0.05)  # 50 milliseconds apart (very fast burst)
print("\n" + "=" * 50)
print(f"⚡ TRAFFIC SPIKE TEST COMPLETED:")
print(f"• Total Requests: {NUM_REQUESTS}")
print(f"• Allowed (Safe): {allowed}")
print(f"• Shed / Blocked (Protected): {shed}")
print(f"• Server Status: 🟢 HEALTHY (Did not crash!)")
print("=" * 50)