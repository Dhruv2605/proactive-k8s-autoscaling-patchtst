import pandas as pd

# Load files
print("Loading files...")
traffic_df = pd.read_csv('traffic_data_stats_history.csv')
training_df = pd.read_csv('training_data.csv')

# 1. Convert Timestamps
# Locust uses Unix Timestamp (UTC), Python uses Local Time strings
traffic_df['timestamp_dt'] = pd.to_datetime(traffic_df['Timestamp'], unit='s')

# ADJUST THIS: Add 5.5 hours to Locust time to match IST (if needed)
traffic_df['timestamp_dt'] = traffic_df['timestamp_dt'] + pd.Timedelta(hours=5, minutes=30)

training_df['timestamp_dt'] = pd.to_datetime(training_df['timestamp'])

# 2. Sort
traffic_df = traffic_df.sort_values('timestamp_dt')
training_df = training_df.sort_values('timestamp_dt')

# 3. Merge (Find nearest timestamp within 10 seconds)
print("Merging data...")
merged_df = pd.merge_asof(
    training_df,
    traffic_df[['timestamp_dt', 'Requests/s', '95%']],
    on='timestamp_dt',
    direction='nearest',
    tolerance=pd.Timedelta('10s')
)

# 4. Clean and Rename
final_df = merged_df[['timestamp', 'Requests/s', '95%', 'cpu_usage', 'memory_usage', 'replicas']]
final_df.columns = ['timestamp', 'qps', 'latency', 'cpu', 'memory', 'replicas']

# 5. Save
final_df.to_csv('final_dataset.csv', index=False)
print("Success! Saved to final_dataset.csv")
print(final_df.head())