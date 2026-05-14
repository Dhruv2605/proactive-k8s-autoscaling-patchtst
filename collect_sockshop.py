"""
Prometheus metric collector for Sock Shop (namespace: sock-shop).
Collects CPU, Memory, Replicas for the 'front-end' deployment.
Saves to sockshop_metrics.csv every 2 seconds.
"""
import requests, csv, time, os
from datetime import datetime

PROMETHEUS_URL = "http://localhost:9090/api/v1/query"
OUTPUT_FILE = "sockshop_metrics.csv"
NAMESPACE = "sock-shop"
CONTAINER = "front-end"
INTERVAL = 2  # seconds

QUERIES = {
    "cpu": f'sum(rate(container_cpu_usage_seconds_total{{namespace="{NAMESPACE}", container="{CONTAINER}"}}[1m]))',
    "memory": f'sum(container_memory_working_set_bytes{{namespace="{NAMESPACE}", container="{CONTAINER}"}})',
    "replicas": f'count(kube_pod_info{{namespace="{NAMESPACE}", created_by_name=~"front-end.*"}})',
}

def query_prometheus(query):
    try:
        r = requests.get(PROMETHEUS_URL, params={"query": query}, timeout=5)
        data = r.json()
        if data["status"] == "success" and data["data"]["result"]:
            return float(data["data"]["result"][0]["value"][1])
    except Exception as e:
        print(f"  Query error: {e}")
    return 0.0

def main():
    file_exists = os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 0
    with open(OUTPUT_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "cpu", "memory", "replicas"])

        print(f"Collecting Sock Shop metrics every {INTERVAL}s -> {OUTPUT_FILE}")
        count = 0
        while True:
            ts = datetime.now().isoformat()
            cpu = query_prometheus(QUERIES["cpu"])
            mem = query_prometheus(QUERIES["memory"])
            rep = query_prometheus(QUERIES["replicas"])

            if cpu > 0 or mem > 0:
                writer.writerow([ts, round(cpu, 6), round(mem, 2), int(rep)])
                f.flush()
                count += 1
                if count % 30 == 0:
                    print(f"  [{count}] cpu={cpu:.4f}, mem={mem:.0f}, replicas={int(rep)}")
            else:
                print(f"  [{ts}] Waiting for non-zero metrics...")

            time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
