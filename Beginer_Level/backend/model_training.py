import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

print("=== Boston House Price Prediction: Complete Pipeline ===\n")

# Step 1: Load and preprocess data
print("Step 1: Loading and preprocessing data...")
try:
    data = pd.read_csv('BostonHousing.csv', header=0)
    data.columns = data.iloc[0]
    data = data.drop(data.index[0]).reset_index(drop=True)
    data = data.apply(pd.to_numeric, errors='coerce')
    print("✓ Data loaded and cleaned successfully")
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# Step 2: Prepare features and target
X = data.drop(columns=['MEDV'])
y = data['MEDV']

# Step 3: Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Training data shape: {X_train_scaled.shape}")
print(f"Testing data shape: {X_test_scaled.shape}")

# Step 5: Initialize models
models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Lasso Regression': Lasso(alpha=1.0),
    'Decision Tree': DecisionTreeRegressor(random_state=42),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
}

# Step 6: Train and evaluate models
results = {}
print("\n=== Model Training and Evaluation ===")

for name, model in models.items():
    print(f"\nTraining {name}...")
    
    # Train the model
    model.fit(X_train_scaled, y_train)
    
    # Make predictions
    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)
    
    # Calculate metrics
    train_mse = mean_squared_error(y_train, y_pred_train)
    test_mse = mean_squared_error(y_test, y_pred_test)
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    
    # Cross-validation score
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
    
    results[name] = {
        'Train MSE': train_mse,
        'Test MSE': test_mse,
        'Train R²': train_r2,
        'Test R²': test_r2,
        'Test MAE': test_mae,
        'CV R² Mean': cv_scores.mean(),
        'CV R² Std': cv_scores.std()
    }
    
    print(f"  Train R²: {train_r2:.4f}")
    print(f"  Test R²: {test_r2:.4f}")
    print(f"  Test MSE: {test_mse:.4f}")
    print(f"  Test MAE: {test_mae:.4f}")
    print(f"  CV R² Mean: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")

# Step 7: Results summary
print("\n" + "="*60)
print("MODEL COMPARISON SUMMARY")
print("="*60)
results_df = pd.DataFrame(results).T
results_df = results_df.round(4)
print(results_df)

# Step 8: Find best model
best_model_name = results_df['Test R²'].idxmax()
best_model = models[best_model_name]

print(f"\n🏆 BEST MODEL: {best_model_name}")
print(f"   Test R²: {results[best_model_name]['Test R²']:.4f}")
print(f"   Test MSE: {results[best_model_name]['Test MSE']:.4f}")
print(f"   Test MAE: {results[best_model_name]['Test MAE']:.4f}")
print(f"   CV R² Score: {results[best_model_name]['CV R² Mean']:.4f}")

# Step 9: Feature importance (if available)
if hasattr(best_model, 'feature_importances_'):
    feature_names = X.columns
    importances = best_model.feature_importances_
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    print(f"\n📊 Feature Importance for {best_model_name}:")
    print(feature_importance)

# Step 10: Save results
joblib.dump(best_model, f'best_model_{best_model_name.lower().replace(" ", "_")}.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(results, 'model_results.pkl')

print(f"✓ Best model saved: best_model_{best_model_name.lower().replace(' ', '_')}.pkl")
print("✓ Scaler saved: scaler.pkl")
print("✓ Results saved: model_results.pkl")

# Step 11: Model interpretation
print(f"\n📈 MODEL PERFORMANCE INTERPRETATION:")
if results[best_model_name]['Test R²'] >= 0.8:
    print("🟢 EXCELLENT: The model explains >80% of price variance")
elif results[best_model_name]['Test R²'] >= 0.7:
    print("🟡 GOOD: The model explains >70% of price variance")
elif results[best_model_name]['Test R²'] >= 0.6:
    print("🟠 FAIR: The model explains >60% of price variance")
else:
    print("🔴 POOR: Model needs improvement")

rmse = np.sqrt(results[best_model_name]['Test MSE'])
print(f"📊 Average prediction error: ${rmse:.2f}K")
print(f"📊 Mean absolute error: ${results[best_model_name]['Test MAE']:.2f}K")

