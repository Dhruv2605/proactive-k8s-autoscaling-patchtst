import pandas as pd

def finalize():
    print("Loading datasets...")
    m_df = pd.read_csv('giant_thesis_dataset_raw.csv')
    t_df = pd.read_csv('giant_traffic_stats_history.csv')
    
    # Time Aligment
    m_df['td'] = pd.to_datetime(m_df['timestamp'])
    t_df['td'] = pd.to_datetime(t_df['Timestamp'], unit='s') + pd.Timedelta(hours=5, minutes=30)
    
    m_df = m_df.sort_values('td')
    t_df = t_df.sort_values('td')
    
    print("Merging...")
    merged = pd.merge_asof(
        m_df, 
        t_df, 
        on='td', 
        direction='nearest', 
        tolerance=pd.Timedelta('15s')
    )
    
    # Check what columns we actually have
    print(f"Available Columns: {merged.columns.tolist()}")
    
    # Use dynamic selection to handle different naming conventions
    qps_col = 'Requests/s' if 'Requests/s' in merged.columns else 'Current Requests/s'
    lat_col = '95%' if '95%' in merged.columns else 'Total 95%'
    avg_col = 'Average Response Time' if 'Average Response Time' in merged.columns else 'Total Average Response Time'
    
    print(f"Mapping: QPS={qps_col}, P95={lat_col}, AVG={avg_col}")
    
    final = merged[['timestamp', qps_col, lat_col, avg_col, 'cpu_usage', 'memory_usage', 'replicas']]
    final.columns = ['timestamp', 'qps', 'p95_latency', 'avg_latency', 'cpu', 'memory', 'replicas']
    
    final = final.dropna()
    # Filter for active load only
    final = final[final['qps'] > 0]
    
    print(f"Final Count: {len(final)}")
    final.to_csv('final_giant_thesis_dataset.csv', index=False)
    print("Saved to final_giant_thesis_dataset.csv")

if __name__ == "__main__":
    finalize()
