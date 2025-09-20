import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

print("=== Final Model Evaluation & Prediction System ===\n")

# Load data
try:
    data = pd.read_csv('BostonHousing.csv', header=0)
    data.columns = data.iloc[0]
    data = data.drop(data.index[0]).reset_index(drop=True)
    data = data.apply(pd.to_numeric, errors='coerce')
    print("✓ Data loaded successfully")
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# Prepare features and target
X = data.drop(columns=['MEDV'])
y = data['MEDV']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Load the best tuned model
try:
    best_model = joblib.load('best_gradient_boosting_model_tuned.pkl')
    print("✓ Best tuned model loaded successfully")
except:
    print("❌ Could not load tuned model")
    exit()

# Make predictions
y_pred = best_model.predict(X_test)

# Final evaluation
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mse)

print(f"\n🏆 FINAL MODEL PERFORMANCE:")
print(f"   R² Score: {r2:.4f} ({r2*100:.2f}% variance explained)")
print(f"   MSE: {mse:.4f}")
print(f"   RMSE: {rmse:.4f}")
print(f"   MAE: ${mae:.2f}K")

# Residual Analysis
residuals = y_test - y_pred
plt.figure(figsize=(12, 8))

# Subplot 1: Actual vs Predicted
plt.subplot(2, 2, 1)
plt.scatter(y_test, y_pred, alpha=0.6, color='blue')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
plt.xlabel('Actual Price ($K)')
plt.ylabel('Predicted Price ($K)')
plt.title('Actual vs Predicted Prices')
plt.grid(True, alpha=0.3)

# Subplot 2: Residuals vs Predicted
plt.subplot(2, 2, 2)
plt.scatter(y_pred, residuals, alpha=0.6, color='green')
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted Price ($K)')
plt.ylabel('Residuals')
plt.title('Residuals vs Predicted')
plt.grid(True, alpha=0.3)

# Subplot 3: Residual Distribution
plt.subplot(2, 2, 3)
plt.hist(residuals, bins=20, alpha=0.7, color='orange', edgecolor='black')
plt.xlabel('Residuals')
plt.ylabel('Frequency')
plt.title('Distribution of Residuals')
plt.grid(True, alpha=0.3)

# Subplot 4: Feature Importance
plt.subplot(2, 2, 4)
feature_names = X.columns
importances = best_model.feature_importances_
indices = np.argsort(importances)[::-1][:8]  # Top 8 features

plt.bar(range(len(indices)), importances[indices], color='purple', alpha=0.7)
plt.xlabel('Features')
plt.ylabel('Importance')
plt.title('Top 8 Feature Importances')
plt.xticks(range(len(indices)), [feature_names[i] for i in indices], rotation=45)
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Feature importance table
feature_importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': importances
}).sort_values('Importance', ascending=False)

print(f"\n📊 FEATURE IMPORTANCE RANKING:")
print(feature_importance_df)

# Sample predictions
print(f"\n🔮 SAMPLE PREDICTIONS:")
sample_indices = np.random.choice(len(X_test), 5, replace=False)
for i, idx in enumerate(sample_indices):
    actual = y_test.iloc[idx]
    predicted = y_pred[idx]
    error = abs(actual - predicted)
    print(f"   Sample {i+1}: Actual=${actual:.1f}K, Predicted=${predicted:.1f}K, Error=${error:.1f}K")

# Model summary
print(f"\n📋 MODEL SUMMARY:")
print(f"   Algorithm: Gradient Boosting Regressor (Optimized)")
print(f"   Training Data: 404 samples")
print(f"   Test Data: 102 samples") 
print(f"   Features: 13")
print(f"   Hyperparameters: learning_rate=0.05, max_depth=3, n_estimators=200")

print(f"\n✅ FINAL EVALUATION COMPLETE!")
print(f"   Your model achieves {r2*100:.2f}% accuracy in predicting Boston house prices!")
print(f"   Average prediction error: ${mae:.2f}K")
