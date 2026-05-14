"""
Cross-Domain Transfer Learning Evaluation (FOOLPROOF HEADERS)
Manual mapping to bypass all character encoding issues.
"""
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model
from sklearn.preprocessing import MinMaxScaler
import os

# 1. Custom Patching Layer
class PatchingLayer(layers.Layer):
    def __init__(self, patch_size, stride):
        super(PatchingLayer, self).__init__()
        self.patch_size = patch_size
        self.stride = stride

    def call(self, x):
        patches = tf.image.extract_patches(
            images=tf.expand_dims(x, axis=-1),
            sizes=[1, self.patch_size, x.shape[-1], 1],
            strides=[1, self.stride, x.shape[-1], 1],
            rates=[1, 1, 1, 1],
            padding='VALID'
        )
        return tf.squeeze(patches, axis=2)

def build_patchtst(seq_len, patch_size, num_features):
    num_patches = (seq_len - patch_size) // patch_size + 1
    inputs = layers.Input(shape=(seq_len, num_features))
    patches = PatchingLayer(patch_size=patch_size, stride=patch_size)(inputs)
    x = layers.Dense(128)(patches)
    x = layers.LayerNormalization()(x)
    x = layers.MultiHeadAttention(num_heads=4, key_dim=32)(x, x)
    x = layers.GlobalAveragePooling1D()(x)
    outputs = layers.Dense(1)(x)
    model = Model(inputs, outputs)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

# 2. Load Google Dataset
print("Loading Google Boutique training data...")
df_google = pd.read_csv("final_giant_thesis_dataset.csv")

# Find indices based on position because the names are corrupted
# google_cols: ['timestamp', 'qps', 'p99', 'p50', 'cpu', 'memory', 'replicas']
# Positions: 1(qps), 3(p50), 2(p99), 4(cpu)
data_google = df_google.iloc[:, [1, 3, 2, 4]].dropna().values
print(f"Google data shape: {data_google.shape}")

# 3. Load Sock Shop Dataset
print("Loading Sock Shop evaluation data...")
df_sock = pd.read_csv("final_sockshop_dataset_final.csv")
# Mapping: Requests/s (4), 50% (12), 99% (20), cpu (25)
# Using names for Sock Shop because they were recently sanitized by clean_csv_headers.py
# Verify indices: Timestamp(0), User Count(1)...
try:
    data_sock = df_sock[['Requests/s', '50%', '99%', 'cpu']].dropna().values
except KeyError:
    # Fallback to indices if names fail
    data_sock = df_sock.iloc[:, [4, 12, 20, 25]].dropna().values
print(f"Sock Shop data shape: {data_sock.shape}")

# 4. Scaling
scaler = MinMaxScaler()
data_google_scaled = scaler.fit_transform(data_google)
data_sock_scaled = scaler.transform(data_sock)

def create_sequences(data, seq_len=30):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i:i+seq_len])
        y.append(data[i+seq_len, 3]) # Target is CPU
    return np.array(X), np.array(y)

X_train, y_train = create_sequences(data_google_scaled)
X_test, y_test = create_sequences(data_sock_scaled)

# 5. Training
print(f"Training on {len(X_train)} Google samples...")
model = build_patchtst(30, 5, 4)
model.fit(X_train, y_train, epochs=5, batch_size=128, verbose=1)

# 6. Evaluation
eval_res = model.evaluate(X_test, y_test, verbose=0)
print(f"TRANSFER_RESULTS_MARKER:MSE={eval_res[0]:.6f},MAE={eval_res[1]:.6f}")

with open("transfer_learning_results.txt", "w") as f:
    f.write(f"Source: Google Boutique (28k)\nTarget: Sock Shop\nMSE: {eval_res[0]:.6f}\nMAE: {eval_res[1]:.6f}\n")
