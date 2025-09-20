import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (mean_squared_error, r2_score, mean_absolute_error, 
                           mean_absolute_percentage_error, max_error)
from sklearn.model_selection import learning_curve, cross_val_score
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("=== Car Price Prediction - Phase 5: Model Evaluation ===\n")

# Load data and models
try:
    X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_names = joblib.load('car_data_preprocessed.pkl')
    print("✅ Preprocessed data loaded")
except Exception as e:
    print(f"❌ Error loading preprocessed data: {e}")
    exit()

# Try to load tuned model first, then base model
best_model = None
model_name = "Unknown"

try:
    tuning_results = joblib.load('hyperparameter_tuning_results.pkl')
    best_tuned_model_name = max(tuning_results.keys(), 
                               key=lambda k: tuning_results[k]['test_r2'])
    best_model = joblib.load('best_car_price_model_tuned.pkl')
    model_name = f"Tuned {best_tuned_model_name}"
    print(f"✅ Loaded tuned model: {model_name}")
except:
    try:
        best_model = joblib.load('best_car_price_model.pkl')
        model_name = "Base Model"
        print(f"✅ Loaded base model: {model_name}")
    except:
        print("❌ No trained model found. Please run model training first.")
        exit()

# Make predictions
print(f"\n🔮 Making Predictions...")
y_pred_train = best_model.predict(X_train_scaled)
y_pred_test = best_model.predict(X_test_scaled)

# Calculate comprehensive metrics
def calculate_metrics(y_true, y_pred):
    """Calculate comprehensive regression metrics"""
    metrics = {
        'R² Score': r2_score(y_true, y_pred),
        'MSE': mean_squared_error(y_true, y_pred),
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'MAE': mean_absolute_error(y_true, y_pred),
        'MAPE': mean_absolute_percentage_error(y_true, y_pred) * 100,
        'Max Error': max_error(y_true, y_pred),
        'Mean Residual': np.mean(y_true - y_pred),
        'Std Residual': np.std(y_true - y_pred)
    }
    return metrics

train_metrics = calculate_metrics(y_train, y_pred_train)
test_metrics = calculate_metrics(y_test, y_pred_test)

print(f"\n📊 COMPREHENSIVE MODEL EVALUATION")
print("="*80)
print(f"Model: {model_name}")
print(f"Model Type: {type(best_model).__name__}")
print("="*80)

print(f"\n📈 TRAINING METRICS:")
for metric, value in train_metrics.items():
    if metric == 'MAPE':
        print(f"   {metric:<15}: {value:.2f}%")
    elif metric in ['R² Score']:
        print(f"   {metric:<15}: {value:.4f} ({value*100:.1f}%)")
    else:
        print(f"   {metric:<15}: ₹{value:.3f}K")

print(f"\n🎯 TESTING METRICS:")
for metric, value in test_metrics.items():
    if metric == 'MAPE':
        print(f"   {metric:<15}: {value:.2f}%")
    elif metric in ['R² Score']:
        print(f"   {metric:<15}: {value:.4f} ({value*100:.1f}%)")
    else:
        print(f"   {metric:<15}: ₹{value:.3f}K")

# Cross-validation evaluation
print(f"\n🔄 Cross-Validation Analysis:")
cv_scores = cross_val_score(best_model, X_train_scaled, y_train, cv=5, scoring='r2')
print(f"   CV R² Scores: {[f'{score:.3f}' for score in cv_scores]}")
print(f"   CV Mean: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")

# Residual Analysis
residuals_train = y_train - y_pred_train
residuals_test = y_test - y_pred_test

print(f"\n📊 RESIDUAL ANALYSIS:")
print(f"   Training Residuals - Mean: {residuals_train.mean():.3f}, Std: {residuals_train.std():.3f}")
print(f"   Testing Residuals - Mean: {residuals_test.mean():.3f}, Std: {residuals_test.std():.3f}")

# Normality test for residuals
shapiro_stat, shapiro_p = stats.shapiro(residuals_test)
print(f"   Residual Normality (Shapiro-Wilk): p-value = {shapiro_p:.4f}")
if shapiro_p > 0.05:
    print("   ✅ Residuals appear normally distributed")
else:
    print("   ⚠️ Residuals may not be normally distributed")

# Create visualizations with proper spacing
print(f"\n📊 Creating Model Evaluation Visualizations...")

# Set style for better appearance
plt.style.use('default')
plt.rcParams.update({
    'font.size': 9,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8
})

# FIGURE 1: Main Performance Plots (2x2)
fig1 = plt.figure(figsize=(16, 12))
fig1.suptitle(f'Model Performance Analysis: {model_name}', fontsize=18, fontweight='bold', y=0.96)

# Plot 1: Training Performance
ax1 = fig1.add_subplot(2, 2, 1)
ax1.scatter(y_train, y_pred_train, alpha=0.6, s=30, color='blue', edgecolor='navy', linewidth=0.5)
ax1.plot([y_train.min(), y_train.max()], [y_train.min(), y_train.max()], 'r--', lw=2)
ax1.set_xlabel('Actual Price (₹ Lakh)', fontsize=10, fontweight='bold')
ax1.set_ylabel('Predicted Price (₹ Lakh)', fontsize=10, fontweight='bold')
ax1.set_title(f'Training Set Performance\nR² = {train_metrics["R² Score"]:.4f}', fontsize=11, fontweight='bold', pad=20)
ax1.grid(True, alpha=0.3)
ax1.legend(['Perfect Prediction', 'Predictions'], loc='lower right', fontsize=8)

# Add text box with metrics
textstr = f'MAE: ₹{train_metrics["MAE"]:.2f}K\nRMSE: ₹{train_metrics["RMSE"]:.2f}K'
props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=8,
         verticalalignment='top', bbox=props)

# Plot 2: Testing Performance
ax2 = fig1.add_subplot(2, 2, 2)
ax2.scatter(y_test, y_pred_test, alpha=0.6, s=30, color='green', edgecolor='darkgreen', linewidth=0.5)
ax2.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
ax2.set_xlabel('Actual Price (₹ Lakh)', fontsize=10, fontweight='bold')
ax2.set_ylabel('Predicted Price (₹ Lakh)', fontsize=10, fontweight='bold')
ax2.set_title(f'Testing Set Performance\nR² = {test_metrics["R² Score"]:.4f}', fontsize=11, fontweight='bold', pad=20)
ax2.grid(True, alpha=0.3)
ax2.legend(['Perfect Prediction', 'Predictions'], loc='lower right', fontsize=8)

# Add text box with metrics
textstr = f'MAE: ₹{test_metrics["MAE"]:.2f}K\nRMSE: ₹{test_metrics["RMSE"]:.2f}K'
props = dict(boxstyle='round', facecolor='lightgreen', alpha=0.8)
ax2.text(0.05, 0.95, textstr, transform=ax2.transAxes, fontsize=8,
         verticalalignment='top', bbox=props)

# Plot 3: Residual Analysis
ax3 = fig1.add_subplot(2, 2, 3)
ax3.scatter(y_pred_test, residuals_test, alpha=0.6, s=30, color='orange', edgecolor='darkorange', linewidth=0.5)
ax3.axhline(y=0, color='red', linestyle='--', linewidth=2)
ax3.set_xlabel('Predicted Price (₹ Lakh)', fontsize=10, fontweight='bold')
ax3.set_ylabel('Residuals (₹ Lakh)', fontsize=10, fontweight='bold')
ax3.set_title('Residual Analysis', fontsize=11, fontweight='bold', pad=20)
ax3.grid(True, alpha=0.3)

# Add text box with residual stats
textstr = f'Mean: {residuals_test.mean():.3f}\nStd: {residuals_test.std():.3f}'
props = dict(boxstyle='round', facecolor='lightyellow', alpha=0.8)
ax3.text(0.05, 0.95, textstr, transform=ax3.transAxes, fontsize=8,
         verticalalignment='top', bbox=props)

# Plot 4: Residual Distribution
ax4 = fig1.add_subplot(2, 2, 4)
n, bins, patches = ax4.hist(residuals_test, bins=12, alpha=0.7, color='purple', edgecolor='black', linewidth=1)
ax4.axvline(residuals_test.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {residuals_test.mean():.3f}')
ax4.axvline(residuals_test.median(), color='blue', linestyle='--', linewidth=2, label=f'Median: {residuals_test.median():.3f}')
ax4.set_xlabel('Residuals (₹ Lakh)', fontsize=10, fontweight='bold')
ax4.set_ylabel('Frequency', fontsize=10, fontweight='bold')
ax4.set_title('Residual Distribution', fontsize=11, fontweight='bold', pad=20)
ax4.legend(fontsize=8)
ax4.grid(True, alpha=0.3)

# Adjust spacing
plt.tight_layout()
plt.subplots_adjust(top=0.92, hspace=0.3, wspace=0.25)
plt.savefig('model_performance_4plots.png', dpi=300, bbox_inches='tight')
plt.show()

# FIGURE 2: Advanced Analysis Plots (2x2)
fig2 = plt.figure(figsize=(16, 12))
fig2.suptitle(f'Advanced Model Analysis: {model_name}', fontsize=18, fontweight='bold', y=0.96)

# Plot 1: Learning Curve
ax1 = fig2.add_subplot(2, 2, 1)
train_sizes, train_scores, val_scores = learning_curve(
    best_model, X_train_scaled, y_train, cv=5, 
    train_sizes=np.linspace(0.1, 1.0, 8), scoring='r2', n_jobs=-1)

train_mean = np.mean(train_scores, axis=1)
train_std = np.std(train_scores, axis=1)
val_mean = np.mean(val_scores, axis=1)
val_std = np.std(val_scores, axis=1)

ax1.plot(train_sizes, train_mean, 'o-', color='blue', label='Training', markersize=6, linewidth=2)
ax1.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.2, color='blue')
ax1.plot(train_sizes, val_mean, 'o-', color='red', label='Validation', markersize=6, linewidth=2)
ax1.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.2, color='red')
ax1.set_xlabel('Training Set Size', fontsize=10, fontweight='bold')
ax1.set_ylabel('R² Score', fontsize=10, fontweight='bold')
ax1.set_title('Learning Curve', fontsize=11, fontweight='bold', pad=20)
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# Plot 2: Feature Importance
ax2 = fig2.add_subplot(2, 2, 2)
if hasattr(best_model, 'feature_importances_'):
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=True)
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(importance_df)))
    bars = ax2.barh(range(len(importance_df)), importance_df['importance'], 
                   color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
    
    ax2.set_yticks(range(len(importance_df)))
    ax2.set_yticklabels([feat.replace('_', ' ').title()[:12] + ('...' if len(feat) > 12 else '') 
                        for feat in importance_df['feature']], fontsize=8)
    ax2.set_xlabel('Feature Importance', fontsize=10, fontweight='bold')
    ax2.set_title('Feature Importance', fontsize=11, fontweight='bold', pad=20)
    ax2.grid(axis='x', alpha=0.3)

elif hasattr(best_model, 'coef_'):
    coef_df = pd.DataFrame({
        'feature': feature_names,
        'coefficient': np.abs(best_model.coef_)
    }).sort_values('coefficient', ascending=True)
    
    colors = plt.cm.plasma(np.linspace(0, 1, len(coef_df)))
    bars = ax2.barh(range(len(coef_df)), coef_df['coefficient'], 
                   color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
    
    ax2.set_yticks(range(len(coef_df)))
    ax2.set_yticklabels([feat.replace('_', ' ').title()[:12] + ('...' if len(feat) > 12 else '') 
                        for feat in coef_df['feature']], fontsize=8)
    ax2.set_xlabel('|Coefficient|', fontsize=10, fontweight='bold')
    ax2.set_title('Feature Coefficients', fontsize=11, fontweight='bold', pad=20)
    ax2.grid(axis='x', alpha=0.3)

# Plot 3: Cross-Validation Scores
ax3 = fig2.add_subplot(2, 2, 3)
bp = ax3.boxplot([cv_scores], labels=['CV Scores'], patch_artist=True,
                boxprops=dict(facecolor='lightblue', alpha=0.8),
                medianprops=dict(color='red', linewidth=2),
                whiskerprops=dict(linewidth=2),
                capprops=dict(linewidth=2))
ax3.scatter([1], [cv_scores.mean()], color='red', s=100, zorder=5, marker='D')
ax3.set_ylabel('R² Score', fontsize=10, fontweight='bold')
ax3.set_title(f'Cross-Validation Scores\nMean: {cv_scores.mean():.3f} (±{cv_scores.std():.3f})', 
              fontsize=11, fontweight='bold', pad=20)
ax3.grid(True, alpha=0.3)

# Plot 4: Error Distribution
ax4 = fig2.add_subplot(2, 2, 4)
abs_errors = np.abs(residuals_test)
n, bins, patches = ax4.hist(abs_errors, bins=12, alpha=0.7, color='gold', edgecolor='black', linewidth=1)
ax4.axvline(abs_errors.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: ₹{abs_errors.mean():.2f}K')
ax4.axvline(abs_errors.median(), color='blue', linestyle='--', linewidth=2, label=f'Median: ₹{abs_errors.median():.2f}K')
ax4.set_xlabel('Absolute Error (₹ Lakh)', fontsize=10, fontweight='bold')
ax4.set_ylabel('Frequency', fontsize=10, fontweight='bold')
ax4.set_title('Prediction Error Distribution', fontsize=11, fontweight='bold', pad=20)
ax4.legend(fontsize=8)
ax4.grid(True, alpha=0.3)

# Adjust spacing
plt.tight_layout()
plt.subplots_adjust(top=0.92, hspace=0.3, wspace=0.25)
plt.savefig('model_analysis_4plots.png', dpi=300, bbox_inches='tight')
plt.show()

# Prediction Examples
print(f"\n🔮 PREDICTION EXAMPLES:")
print("-" * 70)
sample_indices = np.random.choice(len(y_test), min(10, len(y_test)), replace=False)

for i, idx in enumerate(sample_indices, 1):
    actual = y_test.iloc[idx]
    predicted = y_pred_test[idx]
    error = abs(actual - predicted)
    error_pct = (error / actual) * 100
    
    print(f"Sample {i:2d}: Actual=₹{actual:5.1f}K, Predicted=₹{predicted:5.1f}K, "
          f"Error=₹{error:4.2f}K ({error_pct:4.1f}%)")

# Model Performance Interpretation
print(f"\n🎯 MODEL PERFORMANCE INTERPRETATION:")
test_r2 = test_metrics['R² Score']
test_mae = test_metrics['MAE']

if test_r2 >= 0.95:
    print("🟢 EXCELLENT: Model performance is outstanding (>95%)")
elif test_r2 >= 0.90:
    print("🟢 VERY GOOD: Model performs exceptionally well (90-95%)")
elif test_r2 >= 0.85:
    print("🟡 GOOD: Model has solid predictive performance (85-90%)")
elif test_r2 >= 0.75:
    print("🟠 FAIR: Model shows decent performance (75-85%)")
else:
    print("🔴 NEEDS IMPROVEMENT: Consider model refinement or more data")

print(f"\n💰 BUSINESS IMPACT:")
print(f"   • Average prediction error: ±₹{test_mae:.2f}K")
print(f"   • For budget cars (₹2-5K): ~{(test_mae/3.5)*100:.1f}% error")
print(f"   • For mid-range cars (₹5-15K): ~{(test_mae/10)*100:.1f}% error") 
print(f"   • For luxury cars (₹15K+): ~{(test_mae/25)*100:.1f}% error")

# Save evaluation results
print(f"\n💾 Saving Evaluation Results...")
evaluation_results = {
    'model_name': model_name,
    'model_type': type(best_model).__name__,
    'train_metrics': train_metrics,
    'test_metrics': test_metrics,
    'cv_scores': cv_scores.tolist(),
    'residual_analysis': {
        'shapiro_statistic': shapiro_stat,
        'shapiro_p_value': shapiro_p,
        'residual_mean': residuals_test.mean(),
        'residual_std': residuals_test.std()
    },
    'feature_names': feature_names
}

joblib.dump(evaluation_results, 'model_evaluation_results.pkl')
print(f"   ✅ Evaluation results: model_evaluation_results.pkl")
print(f"   ✅ Performance plots: model_performance_4plots.png")
print(f"   ✅ Analysis plots: model_analysis_4plots.png")

print(f"\n" + "="*60)
print("🎉 MODEL EVALUATION COMPLETE!")
print("="*60)
print("📊 Generated 2 clean files with 4 plots each")
print("🚀 No more overlapping - perfect for presentations!")
