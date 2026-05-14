import requests
import pandas as pd
import time
import datetime

PROMETHEUS_URL = "http://localhost:9090/api/v1/query_range"
# Time window: last 17 hours
DURATION_HOURS = 18
END_TIME = time.time()
START_TIME = END_TIME - (DURATION_HOURS * 3600)
FILENAME = "giant_thesis_dataset_raw.csv"
CHUNK_SIZE_SECONDS = 3 * 3600  

QUERIES = {
    'cpu': 'sum(rate(container_cpu_usage_seconds_total{namespace="default"}[1m]))',
    'mem': 'sum(container_memory_usage_bytes{namespace="default"})',
    'rep': 'sum(kube_deployment_status_replicas{namespace="default"})'
}

def fetch_metric_in_chunks(metric_name, query, start, end):
    print(f"Fetching {metric_name} in chunks...")
    all_values = []
    current_start = start
    
    while current_start < end:
        current_end = min(current_start + CHUNK_SIZE_SECONDS, end)
        params = {
            'query': query,
            'start': current_start,
            'end': current_end,
            'step': '2s'
        }
        try:
            r = requests.get(PROMETHEUS_URL, params=params, timeout=30)
            res = r.json()
            if res['status'] == 'success' and res['data']['result']:
                chunk_values = res['data']['result'][0]['values']
                all_values.extend(chunk_values)
        except Exception as e:
            print(f"  ERROR: {e}")
        current_start = current_end
        
    if not all_values: return None
    df = pd.DataFrame(all_values, columns=['timestamp', metric_name])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df['timestamp'] = df['timestamp'].dt.floor('S')
    # CRITICAL: ENSURE NUMERIC
    df[metric_name] = pd.to_numeric(df[metric_name], errors='coerce')
    return df.drop_duplicates(subset='timestamp')

def backfill():
    all_dfs = {}
    for key, query in QUERIES.items():
        all_dfs[key] = fetch_metric_in_chunks(key, query, START_TIME, END_TIME)
        if all_dfs[key] is None:
            print(f"CRITICAL: Failed to fetch {key} history.")
            return

    print("Merging metrics...")
    final_df = all_dfs['cpu']
    for key in ['mem', 'rep']:
        final_df = pd.merge(final_df, all_dfs[key], on='timestamp', how='outer')
    
    final_df = final_df.sort_values('timestamp').ffill().fillna(0)
    
    # Filter non-zero
    final_df = final_df[(final_df['cpu'] > 0) | (final_df['mem'] > 0)]
    
    print(f"SUCCESS! Reconstructed {len(final_df)} rows.")
    final_df.columns = ['timestamp', 'cpu_usage', 'memory_usage', 'replicas']
    final_df.to_csv(FILENAME, index=False)
    print(f"Saved to {FILENAME}")

if __name__ == "__main__":
    backfill()
