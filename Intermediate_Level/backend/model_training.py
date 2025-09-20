import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("=== Car Price Prediction - Phase 3: Model Training ===\n")

# Load preprocessed data
try:
    X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_names = joblib.load('car_data_preprocessed.pkl')
    print("✅ Preprocessed data loaded successfully")
    print(f"Training set: {X_train_scaled.shape}")
    print(f"Testing set: {X_test_scaled.shape}")
    print(f"Features: {feature_names}")
except Exception as e:
    print(f"❌ Error loading preprocessed data: {e}")
    print("Please run 'python feature_engineering.py' first")
    exit()

# Initialize models with optimized parameters
models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Lasso Regression': Lasso(alpha=0.1, max_iter=2000),
    'Decision Tree': DecisionTreeRegressor(
        random_state=42, 
        max_depth=10, 
        min_samples_split=5,
        min_samples_leaf=2
    ),
    'Random Forest': RandomForestRegressor(
        n_estimators=100, 
        random_state=42,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        n_jobs=-1
    ),
    'Gradient Boosting': GradientBoostingRegressor(
        n_estimators=100, 
        random_state=42,
        learning_rate=0.1,
        max_depth=6,
        min_samples_split=5,
        min_samples_leaf=2
    ),
    'Support Vector Regression': SVR(
        kernel='rbf', 
        C=100, 
        gamma='scale',
        epsilon=0.1
    )
}

# Train and evaluate models
results = {}
trained_models = {}
print("🚀 Training Models...")
print("-" * 80)

for name, model in models.items():
    print(f"\n🔄 Training {name}...")
    
    try:
        # Train model
        model.fit(X_train_scaled, y_train)
        trained_models[name] = model
        
        # Predictions
        y_pred_train = model.predict(X_train_scaled)
        y_pred_test = model.predict(X_test_scaled)
        
        # Calculate metrics
        train_mse = mean_squared_error(y_train, y_pred_train)
        test_mse = mean_squared_error(y_test, y_pred_test)
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        test_mae = mean_absolute_error(y_test, y_pred_test)
        test_rmse = np.sqrt(test_mse)
        
        # Cross-validation
        try:
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
        except:
            cv_mean, cv_std = 0, 0
        
        results[name] = {
            'Train MSE': train_mse,
            'Test MSE': test_mse,
            'Train R²': train_r2,
            'Test R²': test_r2,
            'Test MAE': test_mae,
            'Test RMSE': test_rmse,
            'CV R² Mean': cv_mean,
            'CV R² Std': cv_std,
            'Predictions': y_pred_test
        }
        
        print(f"   ✅ Train R²: {train_r2:.4f}")
        print(f"   ✅ Test R²: {test_r2:.4f}")
        print(f"   ✅ Test RMSE: ₹{test_rmse:.2f}K")
        print(f"   ✅ Test MAE: ₹{test_mae:.2f}K")
        if cv_mean > 0:
            print(f"   ✅ CV R² Mean: {cv_mean:.4f} (±{cv_std:.4f})")
        
    except Exception as e:
        print(f"   ❌ Error training {name}: {e}")
        continue

# Results summary
if results:
    print("\n" + "="*90)
    print("📊 MODEL COMPARISON SUMMARY")
    print("="*90)
    
    results_df = pd.DataFrame({k: {metric: v[metric] for metric in v.keys() if metric != 'Predictions'} 
                              for k, v in results.items()}).T
    results_df = results_df.round(4)
    print(results_df)
    
    # Find best model
    best_model_name = results_df['Test R²'].idxmax()
    best_score = results_df.loc[best_model_name, 'Test R²']
    best_model = trained_models[best_model_name]
    
    print(f"\n🏆 BEST MODEL: {best_model_name}")
    print(f"   📈 Test R²: {best_score:.4f} ({best_score*100:.1f}% accuracy)")
    print(f"   📉 Test RMSE: ₹{results[best_model_name]['Test RMSE']:.2f}K")
    print(f"   📊 Test MAE: ₹{results[best_model_name]['Test MAE']:.2f}K")
    
    # Feature importance analysis
    if hasattr(best_model, 'feature_importances_'):
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n📊 Top 10 Feature Importances ({best_model_name}):")
        for idx, row in importance_df.head(10).iterrows():
            print(f"   {row['feature']:20s}: {row['importance']:.4f}")
        
        # Plot feature importance
        plt.figure(figsize=(10, 6))
        top_features = importance_df.head(10)
        plt.barh(range(len(top_features)), top_features['importance'], 
                color='skyblue', edgecolor='navy', alpha=0.7)
        plt.yticks(range(len(top_features)), top_features['feature'])
        plt.xlabel('Feature Importance')
        plt.title(f'Top 10 Feature Importances - {best_model_name}')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()
    
    # Create prediction vs actual plot
    plt.figure(figsize=(12, 5))
    
    # Plot 1: Actual vs Predicted
    plt.subplot(1, 2, 1)
    y_pred_best = results[best_model_name]['Predictions']
    plt.scatter(y_test, y_pred_best, alpha=0.6, color='blue', s=30)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel('Actual Price (₹ Lakh)')
    plt.ylabel('Predicted Price (₹ Lakh)')
    plt.title(f'Actual vs Predicted Prices\n{best_model_name} (R² = {best_score:.3f})')
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Residuals
    plt.subplot(1, 2, 2)
    residuals = y_test - y_pred_best
    plt.scatter(y_pred_best, residuals, alpha=0.6, color='green', s=30)
    plt.axhline(y=0, color='red', linestyle='--')
    plt.xlabel('Predicted Price (₹ Lakh)')
    plt.ylabel('Residuals (₹ Lakh)')
    plt.title(f'Residual Plot\n{best_model_name}')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Save best model with correct filename for Flask API
    model_filename = 'best_car_price_model_random_forest.pkl'  # Fixed filename
    if 'random forest' in best_model_name.lower():
        model_filename = 'best_car_price_model_random_forest.pkl'
    elif 'gradient' in best_model_name.lower():
        model_filename = 'best_car_price_model_gradient_boosting.pkl'
    elif 'linear' in best_model_name.lower():
        model_filename = 'best_car_price_model_linear_regression.pkl'
    else:
        model_filename = f'best_car_price_model_{best_model_name.lower().replace(" ", "_")}.pkl'
    
    # Save all important files
    joblib.dump(best_model, model_filename)
    joblib.dump(best_model, 'best_car_price_model.pkl')  # Generic name
    joblib.dump(results, 'car_model_results.pkl')
    joblib.dump(results_df, 'model_comparison.pkl')
    
    print(f"\n💾 Files Saved:")
    print(f"   ✅ Best model: {model_filename}")
    print(f"   ✅ Generic model: best_car_price_model.pkl")
    print(f"   ✅ All results: car_model_results.pkl")
    print(f"   ✅ Comparison: model_comparison.pkl")
    
    # Performance interpretation
    print(f"\n🎯 MODEL PERFORMANCE INTERPRETATION:")
    if best_score >= 0.95:
        print("🟢 EXCELLENT: Model is highly accurate (>95%)")
    elif best_score >= 0.90:
        print("🟢 VERY GOOD: Model performs very well (90-95%)")
    elif best_score >= 0.85:
        print("🟡 GOOD: Model performs well (85-90%)")
    elif best_score >= 0.75:
        print("🟠 FAIR: Model has decent performance (75-85%)")
    else:
        print("🔴 NEEDS IMPROVEMENT: Consider feature engineering or different algorithms")
    
    avg_error = results[best_model_name]['Test MAE']
    print(f"💰 Average prediction error: ₹{avg_error:.2f}K")
    print(f"📊 For a ₹10L car, typical error: ±₹{avg_error:.1f}K")
    
    # Sample predictions
    print(f"\n🔮 SAMPLE PREDICTIONS:")
    sample_indices = np.random.choice(len(y_test), 5, replace=False)
    for i, idx in enumerate(sample_indices):
        actual = y_test.iloc[idx]
        predicted = y_pred_best[idx]
        error = abs(actual - predicted)
        print(f"   Sample {i+1}: Actual=₹{actual:.1f}K, Predicted=₹{predicted:.1f}K, Error=₹{error:.1f}K")

else:
    print("❌ No models trained successfully")
    print("Check your data preprocessing and feature engineering steps")

print(f"\n" + "="*60)
print("🎉 MODEL TRAINING COMPLETE!")
print("="*60)
if results:
    print("🚀 Next: Your Flask API should now work!")
    print("   Run: python app.py")
else:
    print("❌ Please fix the errors above before proceeding")
