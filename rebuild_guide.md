This is the most important question you have asked. **Do not worry.**

In Cloud Engineering, we treat infrastructure like **cattle, not pets**. You don't "save" a server; you keep the **recipe** to create it.

You already have the hard part (the Python scripts) saved on your laptop. The "config" you are worried about is just a standard set of commands.

**Action:** Copy the content below and save it as a text file named **`REBUILD_GUIDE.txt`** on your laptop. This is your insurance policy. When you are ready to work again, you just follow these 5 steps, and you will be back up in 15 minutes.

---

### **📄 REBUILD_GUIDE.txt (Save this file!)**

**Prerequisites:**

1. Open Terminal as Administrator.
2. Navigate to the folder containing your `locustfile.py` and `collect_data.py`.

#### **Step 1: Create the Cluster (7 mins)**

*This spins up fresh hardware.*

```cmd
gcloud container clusters create mtp2-cluster ^
    --zone us-central1-a ^
    --machine-type e2-standard-2 ^
    --num-nodes 2 ^
    --enable-autoscaling --min-nodes 1 --max-nodes 4 ^
    --disk-size 30 ^
    --disk-type pd-standard

```

#### **Step 2: Connect & Install Helm (1 min)**

*This connects your local `kubectl` to the new cluster.*

```cmd
gcloud container clusters get-credentials mtp2-cluster --zone us-central1-a

```

#### **Step 3: Deploy Online Boutique (2 mins)**

*This downloads the shop from Google.*

```cmd
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/main/release/kubernetes-manifests.yaml

```

#### **Step 4: Install Prometheus Stack (2 mins)**

*This installs the monitoring tools.*

```cmdT
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

```

#### **Step 5: Get Ready for Data Collection (1 min)**

*Port-forward the new services so your local scripts can talk to them.*

**Window 1 (Prometheus Tunnel):**
*(Wait a minute for pods to be 'Running' first)*

```cmd
kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 -n monitoring

```

**Window 2 (Grafana Tunnel - Optional, login: admin / prom-operator):**

```cmd
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring

```
Run in a different terminal (to reset Grafana pwd):

kubectl exec -it -n monitoring deploy/monitoring-grafana -c grafana -- grafana-cli admin reset-admin-password admin


To be put in Grafana for query:

sum(rate(container_cpu_usage_seconds_total{namespace="default", container!=""}[1m])) by (pod)

---
kubectl get service frontend-external
python -m locust -f locust_patterns.py --host http://<IP> --headless --csv=data_sine

**You are now safe to delete the cluster.**

```cmd
gcloud container clusters delete mtp2-cluster --zone us-central1-a

```

