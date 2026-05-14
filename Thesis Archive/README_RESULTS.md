# Thesis Experimental Results & Archive

This folder contains the complete datasets and analysis results for the thesis: **"Proactive Resource Auto Scaling in Kubernetes using Machine Learning"**. These files are preserved for use in paper publication and presentation making.

## 📈 Experimental Setup
- **GCP Project**: `mtp2-gke-486707`
- **Cluster**: `mtp2-cluster` (GKE e2-standard-2, 2-4 nodes)
- **Application**: Google Online Boutique (Microservices Demo)
- **Monitoring**: Prometheus Stack + Custom Python Collector
- **Traffic Pattern**: `spike_stress` (10-minute cycles: 8 min quiet, 2 min surge to 1000 users)

## 📁 File Descriptions

### 1. Training Dataset
- **`final_thesis_dataset.csv`**: The main high-quality training dataset. It combines ~3.5 hours of Sinusoidal (Day/Night) and Spike (Burst) traffic patterns, synchronized with Prometheus metrics. Use this for model training.

### 2. Benchmark Results (The "Comparison")
- **`traffic_hpa_stats_history.csv`**: Raw performance of the **Standard Kubernetes HPA** during a 30-minute spike test. Showcases the REACTIVE behavior and 1.1s latency lag.
- **`traffic_ai_stats_history.csv`**: Raw performance of your **Custom AI Autoscaler** during the same 30-minute test. Showcases the PROACTIVE scaling and 210ms latency (80% improvement).

### 3. Metric Logs (Raw Prometheus Data)
- **`training_data_hpa.csv`**: CPU, Memory, and Replica logs from the HPA run.
- **`training_data_ai.csv`**: CPU, Memory, and Replica logs from the AI run.

### 4. Implementation
- **`ai_autoscaler.py`**: The final version of the custom autoscaler script used for the proactive test.

## 🎯 Key Results for Publication
| Metric | Standard HPA | Custom AI |
| :--- | :--- | :--- |
| **Max P95 Latency** | 1,100 ms | 210 ms |
| **Scaling Target** | Reactive (CPU > 50%) | Proactive (Predictive) |
| **Recovery Speed** | Slow (Metric Lag) | Instant (Pre-warming) |

---
*Generated on: 2026-04-05*
