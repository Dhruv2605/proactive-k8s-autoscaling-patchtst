"""
HPA System-Level Metrics Calculation
Calculates Recall, False Positives, Scaling Events, and RMSE for the HPA baseline (60s Lag).
"""
import pandas as pd
import numpy as np
import os

def calculate_hpa_system_metrics(csv_path, name, interval_sec):
    if not os.path.exists(csv_path):
        return None
    
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().replace("'", "").replace('"', '') for c in df.columns]
    
    cpu_col = [c for c in df.columns if 'cpu' in c.lower()][0]
    cpu_vals = df[cpu_col].dropna().values
    
    # Simulate HPA with 60s lag
    lag_steps = 60 // interval_sec
    hpa_provisioning = np.pad(cpu_vals[:-lag_steps], (lag_steps, 0), mode='edge')
    actual_demand = cpu_vals
    
    # 1. RMSE
    rmse = np.sqrt(np.mean((actual_demand - hpa_provisioning)**2))
    
    # 2. Scaling Events (Transitions in HPA decision)
    # HPA decision is just the shifted demand, so any change in shifted demand counts.
    # We round to nearest integer 'replica' equivalent if necessary, but here we use CPU cores.
    scaling_events = np.sum(np.abs(np.diff(hpa_provisioning)) > 0.05) # 0.05 threshold for significant scaling
    
    # 3. Spike Detection Recall
    # Threshold for a spike
    threshold = np.mean(cpu_vals) + 1.5 * np.std(cpu_vals)
    spikes_actual = actual_demand > threshold
    
    # HPA "Recall" at spike onset T.
    # HPA fails to scale UP at the start of a spike due to lag.
    # We measure how many actual spike points were covered by HPA provisioning > threshold at that exact time.
    covered_spikes = (spikes_actual & (hpa_provisioning > threshold))
    recall = np.sum(covered_spikes) / np.sum(spikes_actual)
    
    # 4. False Positives
    # HPA says spike (hpa > threshold) but demand is low (demand < threshold).
    # This happens during the "trailing edge" of a spike where HPA is still high but traffic dropped.
    false_positives = np.sum((hpa_provisioning > threshold) & (~spikes_actual)) / np.sum(hpa_provisioning > threshold)
    
    return {
        "Name": name,
        "HPA RMSE": round(rmse, 4),
        "HPA Recall": f"{recall*100:.1f}%",
        "HPA False Positives (Waste)": f"{false_positives*100:.1f}%",
        "HPA Scaling Events": int(scaling_events)
    }

print("Calculating HPA Baseline Operational Metrics...")
hpa_google = calculate_hpa_system_metrics("final_giant_thesis_dataset.csv", "Google", 15)
hpa_sock = calculate_hpa_system_metrics("final_sockshop_dataset_final.csv", "SockShop", 5)

import json
print(json.dumps([hpa_google, hpa_sock], indent=2))
