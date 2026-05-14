"""
HPA System-Level Metrics Calculation (Fixed for accurate result reporting)
"""
import pandas as pd
import numpy as np
import os

def calculate_hpa_system_metrics(csv_path, name, interval_sec):
    if not os.path.exists(csv_path):
        return None
    
    # Load with low_memory to avoid dtype warnings
    df = pd.read_csv(csv_path, low_memory=False)
    
    # Clean up column names (handle duplicates and spaces)
    df.columns = [c.strip() for c in df.columns]
    
    # Locate the CPU column (usually the last one in our merged sets)
    cpu_candidates = [c for c in df.columns if 'cpu' == c.lower()]
    if not cpu_candidates:
        cpu_candidates = [c for c in df.columns if 'cpu' in c.lower()]
    
    cpu_col = cpu_candidates[-1]
    cpu_vals = pd.to_numeric(df[cpu_col], errors='coerce').dropna().values
    
    if len(cpu_vals) == 0:
        return {"Name": name, "Error": "No CPU data found"}

    # Simulate HPA with 60s lag
    lag_steps = 60 // interval_sec
    if lag_steps < 1: lag_steps = 1
    
    # HPA decision is "Demand from T-lag"
    hpa_provisioning = np.pad(cpu_vals[:-lag_steps], (lag_steps, 0), mode='edge')
    actual_demand = cpu_vals
    
    # 1. RMSE
    rmse = np.sqrt(np.mean((actual_demand - hpa_provisioning)**2))
    
    # 2. Scaling Events
    scaling_events = np.sum(np.abs(np.diff(hpa_provisioning)) > (0.1 * np.std(cpu_vals)))
    
    # 3. Spike Detection Recall
    threshold = np.mean(cpu_vals) + 1.0 * np.std(cpu_vals)
    spikes_actual = actual_demand > threshold
    
    if np.sum(spikes_actual) == 0:
        recall = 1.0
    else:
        covered_spikes = (spikes_actual & (hpa_provisioning > threshold))
        recall = np.sum(covered_spikes) / np.sum(spikes_actual)
    
    # 4. False Positives
    hpa_says_spike = hpa_provisioning > threshold
    if np.sum(hpa_says_spike) == 0:
        false_positives = 0.0
    else:
        waste = np.sum(hpa_says_spike & (~spikes_actual))
        false_positives = waste / np.sum(hpa_says_spike)
    
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
