import pandas as pd
import numpy as np

M_FILE = 'giant_thesis_dataset_raw.csv'
T_FILE = 'giant_traffic_stats_history.csv'
OUT = 'final_giant_thesis_dataset.csv'

def smart_merge():
    print(f"Loading files...")
    m_df = pd.read_csv(M_FILE)
    t_df = pd.read_csv(T_FILE)
    
    # Pre-process Metrics
    m_df['dt'] = pd.to_datetime(m_df['timestamp'])
    
    # Pre-process Traffic (Handle potential weirdness in Timestamp column)
    # Check if Timestamp is in standard Unix or whatever
    # We will use the system time calibration if needed.
    t_df['dt_utc'] = pd.to_datetime(t_df['Timestamp'], unit='s')
    t_df['dt_ist'] = t_df['dt_utc'] + pd.Timedelta(hours=5, minutes=30)
    
    # ALIGNMENT CHECK:
    # If the overlap is 0, we try to align based on MAX timestamp (assuming they ran until "now")
    m_max = m_df['dt'].max()
    t_max = t_df['dt_ist'].max()
    
    offset = m_max - t_max
    print(f"Time Drift detected: {offset}")
    
    # Calibrate Traffic IST to match Metric IST
    t_df['dt_calibrated'] = t_df['dt_ist'] + offset
    
    # Sort
    m_df = m_df.sort_values('dt')
    t_df = t_df.sort_values('dt_calibrated')
    
    print("Merging with relative alignment...")
    merged = pd.merge_asof(
        m_df,
        t_df[['dt_calibrated', 'Requests/s', '95%', 'Average Latency']],
        left_on='dt',
        right_on='dt_calibrated',
        direction='nearest',
        tolerance=pd.Timedelta('15s')
    )
    
    final = merged[['timestamp', 'Requests/s', '95%', 'Average Latency', 'cpu_usage', 'memory_usage', 'replicas']]
    final.columns = ['timestamp', 'qps', 'p95_latency', 'avg_latency', 'cpu', 'memory', 'replicas']
    
    clean_final = final.dropna()
    print(f"SUCCESS! Merged Rows: {len(clean_final)}")
    clean_final.to_csv(OUT, index=False)
    print(f"File saved: {OUT}")

if __name__ == "__main__":
    smart_merge()
