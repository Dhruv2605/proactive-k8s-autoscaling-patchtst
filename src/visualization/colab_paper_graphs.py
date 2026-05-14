"""
IC2E 2026 Paper - Publication-Ready Graphs
Run this in Colab AFTER training both models (Base Transformer + PatchTST).
Assumes: X_test, y_test, predictions (base), patch_preds (PatchTST),
         mse_ai, mse_patch, mse_hpa, history, patch_history are all in scope.
"""
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from scipy import stats

matplotlib.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'legend.fontsize': 10,
    'figure.dpi': 300
})

# ============================================================
# FIGURE 1: Multi-Model Prediction Comparison (Main Result)
# ============================================================
fig, ax = plt.subplots(figsize=(12, 5))
t = np.arange(400)
hpa_sim = np.roll(y_test[:400], 15)

ax.plot(t, y_test[:400], label='Ground Truth (Actual CPU)', color='#333333', alpha=0.4, linewidth=1)
ax.plot(t, predictions[:400].flatten(), label=f'Base Transformer (MSE={mse_ai:.5f})', color='#2196F3', linewidth=1.5)
ax.plot(t, patch_preds[:400].flatten(), label=f'PatchTST (MSE={mse_patch:.5f})', color='#4CAF50', linewidth=1.5)
ax.plot(t, hpa_sim, label=f'Reactive HPA (MSE={mse_hpa:.5f})', color='#F44336', linestyle='--', linewidth=1.5)

ax.set_xlabel('Time Steps (2s intervals)')
ax.set_ylabel('Normalized CPU Utilization')
ax.set_title('Proactive vs Reactive Autoscaling: CPU Prediction Accuracy')
ax.legend(loc='upper right', framealpha=0.9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('fig1_prediction_comparison.png', dpi=300, bbox_inches='tight')
plt.show()
print("Saved: fig1_prediction_comparison.png")

# ============================================================
# FIGURE 2: Training Loss Convergence
# ============================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

ax1.plot(history.history['loss'], label='Train Loss', color='#2196F3')
ax1.plot(history.history['val_loss'], label='Val Loss', color='#F44336', linestyle='--')
ax1.set_title('Base Transformer')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('MSE Loss')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(patch_history.history['loss'], label='Train Loss', color='#4CAF50')
ax2.plot(patch_history.history['val_loss'], label='Val Loss', color='#FF9800', linestyle='--')
ax2.set_title('PatchTST')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('MSE Loss')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.suptitle('Training Convergence Comparison', fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig('fig2_training_convergence.png', dpi=300, bbox_inches='tight')
plt.show()
print("Saved: fig2_training_convergence.png")

# ============================================================
# FIGURE 3: Error Distribution (Box Plot)
# ============================================================
errors_base = np.abs(y_test - predictions.flatten())
errors_patch = np.abs(y_test - patch_preds.flatten())
errors_hpa = np.abs(y_test - hpa_sim)

fig, ax = plt.subplots(figsize=(8, 5))
bp = ax.boxplot([errors_hpa, errors_base, errors_patch],
                labels=['Reactive HPA', 'Base Transformer', 'PatchTST'],
                patch_artist=True,
                boxprops=dict(linewidth=1.5),
                medianprops=dict(color='black', linewidth=2))

colors = ['#F44336', '#2196F3', '#4CAF50']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.6)

ax.set_ylabel('Absolute Prediction Error')
ax.set_title('Prediction Error Distribution Across Models')
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('fig3_error_distribution.png', dpi=300, bbox_inches='tight')
plt.show()
print("Saved: fig3_error_distribution.png")

# ============================================================
# FIGURE 4: Bar Chart — Final Metrics Summary
# ============================================================
models = ['Reactive HPA', 'Base Transformer', 'PatchTST']
mse_vals = [mse_hpa, mse_ai, mse_patch]
mae_vals = [np.mean(errors_hpa), np.mean(errors_base), np.mean(errors_patch)]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
colors = ['#F44336', '#2196F3', '#4CAF50']

bars1 = ax1.bar(models, mse_vals, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
ax1.set_ylabel('Mean Squared Error (MSE)')
ax1.set_title('MSE Comparison')
ax1.grid(True, alpha=0.3, axis='y')
for bar, val in zip(bars1, mse_vals):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.00005,
             f'{val:.5f}', ha='center', va='bottom', fontsize=9)

bars2 = ax2.bar(models, mae_vals, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
ax2.set_ylabel('Mean Absolute Error (MAE)')
ax2.set_title('MAE Comparison')
ax2.grid(True, alpha=0.3, axis='y')
for bar, val in zip(bars2, mae_vals):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.0005,
             f'{val:.4f}', ha='center', va='bottom', fontsize=9)

plt.suptitle('Multi-Model Performance Benchmark', fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig('fig4_metrics_summary.png', dpi=300, bbox_inches='tight')
plt.show()
print("Saved: fig4_metrics_summary.png")

# ============================================================
# ABLATION STUDY: Sequence Length Impact
# ============================================================
print("\n--- Running Ablation Study ---")
print("Testing sequence lengths: [10, 20, 30, 40, 60]")
# Note: This requires re-creating sequences and re-training.
# Below is the code structure; uncomment and run in Colab.
"""
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf

seq_lengths = [10, 20, 30, 40, 60]
ablation_results = []

for sl in seq_lengths:
    X_abl, y_abl = create_sequences(scaled_data, sl)
    split = int(len(X_abl) * 0.8)
    X_tr, X_te = X_abl[:split], X_abl[split:]
    y_tr, y_te = y_abl[:split], y_abl[split:]

    model_abl = build_patch_tst((sl, 4), patch_size=max(4, sl//5), stride=max(2, sl//10))
    model_abl.compile(optimizer="adam", loss="mse", metrics=["mae"])
    model_abl.fit(X_tr, y_tr, epochs=10, batch_size=64, validation_split=0.1, verbose=0)
    
    preds_abl = model_abl.predict(X_te, verbose=0)
    mse_abl = np.mean((y_te - preds_abl.flatten())**2)
    mae_abl = np.mean(np.abs(y_te - preds_abl.flatten()))
    ablation_results.append({'seq_len': sl, 'mse': mse_abl, 'mae': mae_abl})
    print(f"  Seq Length {sl}: MSE={mse_abl:.6f}, MAE={mae_abl:.4f}")

# Plot ablation
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
sls = [r['seq_len'] for r in ablation_results]
ax1.plot(sls, [r['mse'] for r in ablation_results], 'o-', color='#2196F3')
ax1.set_xlabel('Sequence Length')
ax1.set_ylabel('MSE')
ax1.set_title('Effect of Sequence Length on MSE')
ax1.grid(True, alpha=0.3)

ax2.plot(sls, [r['mae'] for r in ablation_results], 's-', color='#4CAF50')
ax2.set_xlabel('Sequence Length')
ax2.set_ylabel('MAE')
ax2.set_title('Effect of Sequence Length on MAE')
ax2.grid(True, alpha=0.3)

plt.suptitle('Ablation Study: Sequence Length', fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig('fig5_ablation_seq_length.png', dpi=300, bbox_inches='tight')
plt.show()
print("Saved: fig5_ablation_seq_length.png")
"""

# ============================================================
# STATISTICAL SIGNIFICANCE (t-test placeholder)
# ============================================================
print("\n--- Statistical Significance ---")
print("For formal t-test, use the n=5 run data from Thesis Archive/")
print("Example code:")
print("""
hpa_latencies = [1020, 1015, 1025, 1018, 1022]  # Replace with actual n=5 values
ai_latencies  = [215, 218, 212, 220, 210]        # Replace with actual n=5 values

t_stat, p_value = stats.ttest_ind(hpa_latencies, ai_latencies)
print(f"t-statistic: {t_stat:.4f}")
print(f"p-value: {p_value:.8f}")
print(f"Significant at p<0.05: {p_value < 0.05}")
""")

print("\n=== All publication figures generated! ===")
print("Files: fig1_prediction_comparison.png, fig2_training_convergence.png,")
print("       fig3_error_distribution.png, fig4_metrics_summary.png")
