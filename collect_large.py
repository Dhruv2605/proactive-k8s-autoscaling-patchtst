import time
import csv
import requests
import datetime
import os

# --- CONFIGURATION ---
PROMETHEUS_URL = "http://localhost:9090/api/v1/query"
FILENAME = "giant_thesis_dataset_raw.csv"
LOGFILE = "collector.log"
INTERVAL = 2  

# Bulk Query: Union of 3 metrics
BULK_QUERY = (
    'sum(rate(container_cpu_usage_seconds_total{namespace="default", container!=""}[1m])) or '
    'sum(container_memory_usage_bytes{namespace="default", container!=""}) or '
    'sum(kube_deployment_status_replicas{namespace="default"})'
)

def log(msg):
    with open(LOGFILE, "a") as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def collect_bulk():
    try:
        response = requests.get(PROMETHEUS_URL, params={'query': BULK_QUERY}, timeout=5)
        results = response.json()['data']['result']
        
        if len(results) >= 3:
            cpu = float(results[0]['value'][1])
            mem = float(results[1]['value'][1])
            rep = float(results[2]['value'][1])
            # GUARD: Only return non-zero metrics
            if cpu > 0 or mem > 0 or rep > 0:
                return cpu, mem, rep
        return None
    except Exception as e:
        log(f"Connection Error: {e}")
        return None

print(f"STARTING ROBUST BULK COLLECTION...")
file_exists = os.path.exists(FILENAME)

with open(FILENAME, mode='a', newline='') as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow(["timestamp", "cpu_usage", "memory_usage", "replicas"])

    try:
        while True:
            start_loop = time.time()
            data = collect_bulk()
            
            if data:
                cpu, mem, rep = data
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow([timestamp, cpu, mem, rep])
                file.flush()
                if int(time.time()) % 300 == 0: # Status every 5m
                    print(f"[{timestamp}] Active | CPU: {cpu:.2f}")
            else:
                # No new pulse during debug
                pass
            
            elapsed = time.time() - start_loop
            sleep_time = max(0.1, INTERVAL - elapsed)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\nStopped.")
