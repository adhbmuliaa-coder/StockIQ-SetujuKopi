#!/usr/bin/env python3
"""
Start Flask app and run the workflow tests
"""

import subprocess
import sys
import time
import requests
import os
import io

# Fix encoding
if sys.stdout.encoding is None or sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Start Flask app in background
print("="*70)
print("Starting Flask app on http://localhost:5000...")
print("="*70)

flask_process = subprocess.Popen(
    [sys.executable, 'run.py'],
    cwd='c:\\Users\\hp\\OneDrive\\Desktop\\STOCKIQ-SETUJUKOPI',
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

print(f"Flask app process started with PID: {flask_process.pid}")

# Wait for app to start
print("Waiting for Flask app to become ready...")
max_attempts = 30
for attempt in range(max_attempts):
    try:
        response = requests.get('http://localhost:5000/login', timeout=2)
        print(f"[OK] Flask app is ready! (Status: {response.status_code})")
        break
    except:
        if attempt < max_attempts - 1:
            if attempt % 5 == 0:
                print(f"  Waiting... ({attempt+1}/{max_attempts})")
            time.sleep(1)
        else:
            print(f"[FAIL] Flask app did not start within {max_attempts} seconds")
            sys.exit(1)

print("\n")
time.sleep(1)  # Extra wait to ensure DB is ready

# Now run the tests
print("="*70)
print("Running workflow tests...")
print("="*70 + "\n")

test_process = subprocess.run([sys.executable, 'test_workflow.py'], cwd='c:\\Users\\hp\\OneDrive\\Desktop\\STOCKIQ-SETUJUKOPI')

# Kill the Flask app
print("\n" + "="*70)
print("Cleaning up: Stopping Flask app...")
print("="*70)
try:
    flask_process.terminate()
    flask_process.wait(timeout=5)
    print("Flask app stopped")
except:
    flask_process.kill()
    print("Flask app killed")

sys.exit(test_process.returncode)
