"""
Refined Training Script for Sock Shop Data.
Uses exact column names verified from the merged CSV.
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
    return Model(inputs, outputs)

# 2. Data Preparation
if not os.path.exists("final_sockshop_dataset_final.csv"):
    print("Error: Definitive Dataset not found.")
    exit(1)

df = pd.read_csv("final_sockshop_dataset_final.csv")
# Features verified from sanitized CSV headers
features = ['User Count', 'Total Request Count', 'Total Average Response Time', 'cpu']
data = df[features].dropna().values

if len(data) < 100:
    print(f"Error: Insufficient data samples after dropna: {len(data)}")
    exit(1)

scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

def create_sequences(data, seq_len=30):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i:i+seq_len])
        y.append(data[i+seq_len, 3]) # Target is CPU (index 3)
    return np.array(X), np.array(y)

X, y = create_sequences(data_scaled)
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# 3. Training
print(f"Starting training on {len(X_train)} samples across {len(features)} features...")
model = build_patchtst(30, 5, len(features))
model.compile(optimizer='adam', loss='mse', metrics=['mae'])
history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=10, batch_size=64, verbose=0)

# 4. Final Evaluation
eval_res = model.evaluate(X_test, y_test, verbose=0)
print(f"RESULTS_MARKER:MSE={eval_res[0]:.6f},MAE={eval_res[1]:.6f}")

# Save results for artifact update
with open("sockshop_final_metrics.txt", "w") as f:
    f.write(f"MSE: {eval_res[0]:.6f}\nMAE: {eval_res[1]:.6f}\n")
