import subprocess
import time
import os
import pandas as pd

# CONFIG
HOST = "http://34.59.137.202"
LOCUST_FILE = "locust_patterns.py"
COLLECT_SCRIPT = "collect_data.py"
AI_SCRIPT = "ai_autoscaler.py"
ITERATIONS = 5
CYCLE_TIME = "10m"

def run_command(cmd, wait=True):
    print(f"Running: {cmd}")
    if wait:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True)
    else:
        return subprocess.Popen(cmd, shell=True)

def reset_cluster():
    print("Resetting cluster...")
    run_command("kubectl delete hpa frontend")
    run_command("kubectl scale deployment frontend --replicas=12")
    time.sleep(30) # Let it settle

def run_iteration(mode, iter_num):
    print(f"\n--- STARTING {mode} ITERATION {iter_num} ---")
    reset_cluster()
    
    # 1. Start Autoscaler
    autoscaler_proc = None
    if mode == "HPA":
        run_command("kubectl autoscale deployment frontend --cpu-percent=50 --min=12 --max=40")
    else:
        # Start AI in background
        print("Starting AI Autoscaler...")
        os.chdir("Collected Dataset/Dataset")
        autoscaler_proc = subprocess.Popen(["python", "ai_autoscaler.py"])
        os.chdir("../..")
    
    # 2. Start Metric Collector
    # Modify collect_data.py to save to specific filename via env var or arg (Simplifying here by just copying)
    filename = f"stats_{mode.lower()}_iter{iter_num}.csv"
    # We overwrite the filename in collect_data.py briefly or use a temporary version
    with open(COLLECT_SCRIPT, 'r') as f:
        content = f.read()
    with open("collect_temp.py", 'w') as f:
        f.write(content.replace('FILENAME = "training_data_ai.csv"', f'FILENAME = "{filename}"'))
    
    collector_proc = subprocess.Popen(["python", "collect_temp.py"])
    
    # 3. Start Locust
    locust_cmd = f"python -m locust -f {LOCUST_FILE} --host {HOST} --headless --csv=traffic_{mode.lower()}_iter{iter_num} -u 1000 -r 100 --run-time {CYCLE_TIME}"
    run_command(locust_cmd)
    
    # 4. Cleanup
    print("Cleaning up iteration...")
    collector_proc.terminate()
    if autoscaler_proc:
        autoscaler_proc.terminate()
    
    print(f"Iteration {iter_num} complete. Cooling down for 60s...")
    time.sleep(60)

# --- MAIN EXECUTION ---
print("Starting Statistical Significance Automation (n=5)...")
for i in range(1, ITERATIONS + 1):
    run_iteration("HPA", i)

for i in range(1, ITERATIONS + 1):
    run_iteration("AI", i)

print("\n--- ALL ITERATIONS COMPLETE! ---")
