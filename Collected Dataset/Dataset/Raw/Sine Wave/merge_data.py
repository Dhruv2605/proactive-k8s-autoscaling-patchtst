import pandas as pd

# 1. Load the files (Update filenames for Day 2/3 later)
print("Loading files...")
traffic_df = pd.read_csv('data_sine_stats_history.csv')  # Locust File
training_df = pd.read_csv('training_data.csv')           # Python Collector File

# 2. Fix Timestamps
# Convert Locust (Unix) to Datetime + Add 5h 30m for IST
traffic_df['timestamp_dt'] = pd.to_datetime(traffic_df['Timestamp'], unit='s')
traffic_df['timestamp_dt'] = traffic_df['timestamp_dt'] + pd.Timedelta(hours=5, minutes=30)

# Convert Python Collector to Datetime
training_df['timestamp_dt'] = pd.to_datetime(training_df['timestamp'])

# 3. Sort both
traffic_df = traffic_df.sort_values('timestamp_dt')
training_df = training_df.sort_values('timestamp_dt')

# 4. Merge (Find nearest match within 10 seconds)
print("Merging data...")
merged_df = pd.merge_asof(
    training_df,
    traffic_df[['timestamp_dt', 'Requests/s', 'Failures/s', '95%', 'User Count']],
    on='timestamp_dt',
    direction='nearest',
    tolerance=pd.Timedelta('10s')
)

# 5. Clean up columns
final_df = merged_df[['timestamp', 'Requests/s', 'Failures/s', '95%', 'cpu_usage', 'memory_usage', 'replicas', 'User Count']]
final_df.columns = ['timestamp', 'rps', 'failures_per_sec', 'latency_p95', 'cpu', 'memory', 'replicas', 'users']

# 6. Save
final_df.to_csv('final_dataset_day1.csv', index=False)
print("Success! Saved to final_dataset_day1.csv")
print(final_df.head())