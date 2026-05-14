"""
Train PatchTST on Sock Shop data for cross-application comparison.
Uses the synchronized 7,147 row dataset.
"""
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model
from sklearn.preprocessing import MinMaxScaler

# 1. Custom Patching Layer (Same as before)
class PatchingLayer(layers.Layer):
    def __init__(self, patch_size, stride):
        super(PatchingLayer, self).__init__()
        self.patch_size = patch_size
        self.stride = stride

    def call(self, x):
        # x shape: (batch, seq_len, features)
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
    
    # Patching
    patches = PatchingLayer(patch_size=patch_size, stride=patch_size)(inputs)
    
    # Transformer Encoder
    x = layers.Dense(128)(patches)
    x = layers.LayerNormalization()(x)
    x = layers.MultiHeadAttention(num_heads=4, key_dim=32)(x, x)
    x = layers.GlobalAveragePooling1D()(x)
    
    # Output
    outputs = layers.Dense(1)(x)
    return Model(inputs, outputs)

# 2. Data Preparation
df = pd.read_csv("final_sockshop_dataset.csv")
df.columns = df.columns.str.strip()
df = df.dropna()

# Map expected features to actual columns (case-insensitive)
feature_map = {
    'user count': 'User Count',
    'request count': 'Request Count',
    'average response time': 'Average Response Time',
    'cpu': 'cpu'
}
actual_features = [feature_map[f] for f in feature_map]
data = df[actual_features].values
print(f"Loaded {len(data)} rows with features: {actual_features}")

scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

def create_sequences(data, seq_len=30):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i:i+seq_len])
        y.append(data[i+seq_len, 3]) # Predicting CPU
    return np.array(X), np.array(y)

X, y = create_sequences(data_scaled)
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# 3. Train
model = build_patchtst(30, 5, 4)
model.compile(optimizer='adam', loss='mse', metrics=['mae'])
print("Training PatchTST on Sock Shop data...")
history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=15, batch_size=64, verbose=0)

# 4. Evaluate
eval_res = model.evaluate(X_test, y_test, verbose=0)
print(f"Sock Shop PatchTST Results: MSE={eval_res[0]:.6f}, MAE={eval_res[1]:.6f}")

# Save results for comparison
with open("sockshop_results.txt", "w") as f:
    f.write(f"MSE: {eval_res[0]}\nMAE: {eval_res[1]}\n")
