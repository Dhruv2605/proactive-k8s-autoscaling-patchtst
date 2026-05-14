"""
HPA Baseline Validation Script
Calculates HPA Error (MAE/MSE) across different systemic lags.
"""
import pandas as pd
import numpy as np

def validate_hpa(csv_path, name, interval_sec):
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().replace("'", "").replace('"', '') for c in df.columns]
    
    # Fuzzy find CPU column
    cpu_col = [c for c in df.columns if 'cpu' in c.lower()][0]
    cpu_vals = df[cpu_col].dropna().values
    
    # We simulate HPA by shifting the demand. 
    # Standard HPA Lag = Scraping (15s) + Decision (15s) + Startup (30-60s) = 60-90s
    lags_to_test = [15, 30, 60, 90] # in seconds
    results = []
    
    for lag_sec in lags_to_test:
        shift_steps = lag_sec // interval_sec
        if shift_steps < 1: shift_steps = 1
        
        # HPA decision at time 't' is actually the demand at time 't - lag'
        hpa_provisioning = cpu_vals[:-shift_steps]
        actual_demand = cpu_vals[shift_steps:]
        
        mae = np.mean(np.abs(actual_demand - hpa_provisioning))
        mse = np.mean((actual_demand - hpa_provisioning)**2)
        
        results.append({
            "Lag": f"{lag_sec}s",
            "MAE": round(mae, 4),
            "MSE": round(mse, 6)
        })
        
    return results

print("=== Google Boutique HPA Validation (15s Interval) ===")
print(pd.DataFrame(validate_hpa("final_giant_thesis_dataset.csv", "Google", 15)))

print("\n=== Sock Shop HPA Validation (5s Interval) ===")
print(pd.DataFrame(validate_hpa("final_sockshop_dataset_final.csv", "SockShop", 5)))
