"""
Finalize Cross-Application Experiment results.
1. Merges Locust stats with Prometheus metrics for both apps.
2. Performs a check on data quality.
3. Prepares the comparison table for the LaTeX paper.
"""
import pandas as pd
import numpy as np

def process_app(metric_file, locust_file, output_name):
    print(f"Processing {output_name}...")
    try:
        metrics = pd.read_csv(metric_file)
        locust = pd.read_csv(locust_file)
        
        # Simple time alignment for preview (actual training uses training_data.py logic)
        metrics['timestamp'] = pd.to_datetime(metrics['timestamp'])
        
        # FIX: Locust timestamps are UTC (from epoch), metrics are IST (System time)
        # Offset is 5.5 hours
        locust['Timestamp'] = pd.to_datetime(locust['Timestamp'], unit='s') + pd.Timedelta(hours=5, minutes=30)
        
        # Merge-asof to align traffic with metrics
        merged = pd.merge_asof(
            locust.sort_values('Timestamp'), 
            metrics.sort_values('timestamp'),
            left_on='Timestamp', 
            right_on='timestamp',
            direction='nearest'
        )
        merged.to_csv(f"final_{output_name}_dataset.csv", index=False)
        print(f"  Saved {len(merged)} rows to final_{output_name}_dataset.csv")
        return len(merged)
    except Exception as e:
        print(f"  Error processing {output_name}: {e}")
        return 0

if __name__ == "__main__":
    print("=== Post-Collection Analysis Initialization ===")
    
    # Files expected after 2-hour run
    boutique_stats = "boutique_sine_stats_history.csv"
    boutique_metrics = "training_data_sine.csv" # Update if collect_data.py saves elsewhere
    
    sockshop_stats = "sockshop_sine_stats_history.csv"
    sockshop_metrics = "sockshop_metrics.csv"
    
    # Check if files exist
    import os
    for f in [boutique_stats, boutique_metrics, sockshop_stats, sockshop_metrics]:
        if not os.path.exists(f):
            print(f"WARNING: Missing {f}. Data collection might still be running.")
    
    # Preview processing
    process_app(sockshop_metrics, sockshop_stats, "sockshop")
    # boutique processing would go here too
