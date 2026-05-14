import requests
import time

PROMETHEUS_URL = "http://localhost:9090/api/v1/query"
QUERY = 'sum(rate(container_cpu_usage_seconds_total{namespace="default"}[1m]))'

def test():
    print(f"Testing Prometheus at {PROMETHEUS_URL}...")
    try:
        r = requests.get(PROMETHEUS_URL, params={'query': QUERY}, timeout=10)
        data = r.json()
        result = data.get('data', {}).get('result', [])
        if result:
            val = result[0]['value'][1]
            print(f"SUCCESS! CPU Usage: {val}")
            return True
        else:
            print("WARNING: Query returned no results. Check namespace/labels.")
            return False
    except Exception as e:
        print(f"FAILURE: {e}")
        return False

if __name__ == "__main__":
    test()
