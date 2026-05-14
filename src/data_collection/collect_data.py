import time
import csv
import requests
import datetime

# --- CONFIGURATION ---
# We ONLY talk to Prometheus now. Locust data comes from the separate CSV.
PROMETHEUS_URL = "http://localhost:9090/api/v1/query"
FILENAME = "training_data_ai.csv"
INTERVAL = 5  # Collect data every 5 seconds

# PromQL Queries
QUERY_CPU = 'sum(rate(container_cpu_usage_seconds_total{namespace="default", container!=""}[1m]))'
QUERY_MEM = 'sum(container_memory_usage_bytes{namespace="default", container!=""})'
QUERY_REPLICAS = 'sum(kube_deployment_status_replicas{namespace="default"})'

def get_prometheus_metric(query):
    try:
        response = requests.get(PROMETHEUS_URL, params={'query': query})
        result = response.json()['data']['result']
        if result:
            return float(result[0]['value'][1])
        return 0.0
    except Exception as e:
        print(f"Error fetching Prometheus data: {e}")
        return 0.0

# --- MAIN LOOP ---
print(f"Starting CPU/Mem collection... Saving to {FILENAME}")
print("Press Ctrl+C to stop.")

with open(FILENAME, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Header (Only Resource Metrics)
    writer.writerow(["timestamp", "cpu_usage", "memory_usage", "replicas"])

    try:
        while True:
            # 1. Get Metrics from Prometheus
            cpu = get_prometheus_metric(QUERY_CPU)
            mem = get_prometheus_metric(QUERY_MEM)
            replicas = get_prometheus_metric(QUERY_REPLICAS)
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 2. Print to console
            print(f"[{timestamp}] CPU: {cpu:.4f} | Mem: {mem/1024/1024:.2f}MB | Replicas: {int(replicas)}")

            # 3. Save to CSV
            writer.writerow([timestamp, cpu, mem, replicas])
            
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        print("\nData collection stopped.")