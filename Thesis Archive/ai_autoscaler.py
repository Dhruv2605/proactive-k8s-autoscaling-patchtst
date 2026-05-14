import time
import requests
import numpy as np
import pandas as pd
import subprocess
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# --- CONFIGURATION ---
PROMETHEUS_URL = "http://localhost:9090/api/v1/query"
MODEL_FILE = "thesis_model.keras"
DATA_FILE = "thesis_ready_data.csv"  # Needed to calibrate the scaler
DEPLOYMENT_NAME = "frontend"    # The microservice to scale
NAMESPACE = "default"
TARGET_CPU = 0.10                # We want to keep CPU at 50%
MIN_REPLICAS = 12               # Never go below this
MAX_REPLICAS = 40               # Safety limit
CHECK_INTERVAL = 5              # How often to check (seconds)

# --- 1. LOAD MODEL & SCALER ---
print("Loading AI Brain...")
model = load_model(MODEL_FILE)

print("Calibrating Scaler...")
# We fit the scaler on the original data so it knows what "0.5" means
df = pd.read_csv(DATA_FILE)
scaler = MinMaxScaler()
# We trained on [cpu, rps, latency], so we must scale exactly the same way
scaler.fit(df[['cpu', 'rps', 'latency_p95']]) 

# --- HELPER FUNCTIONS ---

def get_prometheus_data():
    """Fetches the last 60 seconds of data for CPU, RPS, and Latency"""
    # 1. CPU Query (Last 1m)
    query_cpu = 'sum(rate(container_cpu_usage_seconds_total{namespace="default", container!=""}[1m]))'
    # 2. RPS Query (Last 1m) - Approximate via inbound traffic
    query_rps = 'sum(rate(container_network_receive_bytes_total{namespace="default"}[1m])) / 1024' 
    # 3. Latency (Use a dummy value if real latency is hard to query quickly, or refine query)
    # For thesis demo, CPU and RPS are the dominant factors.
    
    # Execute Queries
    cpu = fetch_metric(query_cpu)
    rps = fetch_metric(query_rps)
    latency = 0.0 # Placeholder or fetch real query if available
    
    return cpu, rps, latency

def fetch_metric(query):
    try:
        response = requests.get(PROMETHEUS_URL, params={'query': query})
        result = response.json()['data']['result']
        if result:
            return float(result[0]['value'][1])
        return 0.0
    except Exception as e:
        print(f"Prometheus Error: {e}")
        return 0.0

def scale_deployment(replicas):
    """Runs the kubectl command to scale"""
    cmd = f"kubectl scale deployment {DEPLOYMENT_NAME} --replicas={replicas} -n {NAMESPACE}"
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL)
    print(f" -> 🚀 Scaled to {replicas} replicas")

# --- MAIN LOOP ---
print("✅ AI Autoscaler Started! Press Ctrl+C to stop.")

# Buffer to store the last 60 seconds of data (Moving Window)
history_window = []

while True:
    # 1. Get Live Data
    cpu, rps, lat = get_prometheus_data()
    
    # 2. Add to history
    history_window.append([cpu, rps, lat])
    
    # Keep only last 60 seconds
    if len(history_window) > 60:
        history_window.pop(0)
        
    # 3. If we have enough data (60s), Ask the AI
    if len(history_window) == 60:
        # Prepare data structure for model (1, 60, 3)
        live_data = np.array(history_window)
        
        # Normalize (Scale 0-1) using the calibrated scaler
        live_data_scaled = scaler.transform(live_data)
        
        # Reshape for LSTM/Transformer: (1 batch, 60 steps, 3 features)
        model_input = live_data_scaled.reshape(1, 60, 3)
        
        # PREDICT!
        prediction_scaled = model.predict(model_input, verbose=0)
        
        # Inverse transform to get real CPU number
        # (We create a dummy matrix to reverse the scaling)
        dummy_matrix = np.zeros((12, 3)) 
        dummy_matrix[:, 0] = prediction_scaled[0] # Fill CPU column
        prediction_real = scaler.inverse_transform(dummy_matrix)[:, 0]
        
        # Take the average predicted CPU for the next minute
        predicted_cpu_avg = np.mean(prediction_real)
        
        # 4. DECIDE: Calculate needed replicas
        # Formula: New = Current * (Predicted / Target)
        current_replicas = 12 # Start assumption (or query kubectl for real count)
        
        if predicted_cpu_avg > TARGET_CPU:
            # AI says: "Load is spiking!" -> Scale UP
            ratio = predicted_cpu_avg / TARGET_CPU
            new_replicas = int(current_replicas * ratio)
        else:
            # AI says: "Chilling." -> Scale DOWN (slowly)
            new_replicas = int(current_replicas * 0.9) # Gradual scale down
            
        # Bounds Check
        new_replicas = max(MIN_REPLICAS, min(new_replicas, MAX_REPLICAS))
        
        print(f"Live CPU: {cpu:.3f} | AI Predicts: {predicted_cpu_avg:.3f} | Action: {new_replicas} Replicas")
        
        # 5. ACT
        scale_deployment(new_replicas)
        
    else:
        print(f"Gathering data... ({len(history_window)}/60)")

    time.sleep(CHECK_INTERVAL)