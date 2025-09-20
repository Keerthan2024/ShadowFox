import pandas as pd
import numpy as np
import joblib
import time
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("=== Car Price Prediction - Phase 4: Hyperparameter Tuning ===\n")

# Load preprocessed data
try:
    X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_names = joblib.load('car_data_preprocessed.pkl')
    print("✅ Preprocessed data loaded successfully")
    print(f"Training set: {X_train_scaled.shape}")
    print(f"Testing set: {X_test_scaled.shape}")
except Exception as e:
    print(f"❌ Error loading preprocessed data: {e}")
    print("Please run 'python feature_engineering.py' first")
    exit()

# Define parameter grids for hyperparameter tuning
param_grids = {
    'Random Forest': {
        'model': RandomForestRegressor(random_state=42, n_jobs=-1),
        'params': {
            'n_estimators': [50, 100, 200, 300],
            'max_depth': [5, 10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2', None]
        }
    },
    'Gradient Boosting': {
        'model': GradientBoostingRegressor(random_state=42),
        'params': {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'max_depth': [3, 5, 7, 9],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'subsample': [0.8, 0.9, 1.0]
        }
    },
    'Ridge Regression': {
        'model': Ridge(random_state=42),
        'params': {
            'alpha': [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0],
            'solver': ['auto', 'svd', 'cholesky', 'lsqr', 'sparse_cg', 'sag', 'saga']
        }
    },
    'Lasso Regression': {
        'model': Lasso(random_state=42, max_iter=2000),
        'params': {
            'alpha': [0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0],
            'selection': ['cyclic', 'random']
        }
    },
    'Support Vector Regression': {
        'model': SVR(),
        'params': {
            'C': [0.1, 1, 10, 100],
            'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1],
            'epsilon': [0.01, 0.1, 0.2, 0.5],
            'kernel': ['rbf', 'poly', 'sigmoid']
        }
    }
}

# Perform hyperparameter tuning
tuning_results = {}
best_models = {}

print("🔄 Starting Hyperparameter Tuning...\n")
print("This may take 10-20 minutes depending on your system.")
print("-" * 80)

for model_name, config in param_grids.items():
    print(f"\n🚀 Tuning {model_name}...")
    start_time = time.time()
    
    try:
        # Use RandomizedSearchCV for faster tuning (or GridSearchCV for exhaustive search)
        if model_name in ['Random Forest', 'Gradient Boosting', 'Support Vector Regression']:
            # Use RandomizedSearchCV for complex models
            search = RandomizedSearchCV(
                estimator=config['model'],
                param_distributions=config['params'],
                n_iter=50,  # Number of parameter combinations to try
                cv=5,
                scoring='r2',
                n_jobs=-1,
                random_state=42,
                verbose=0
            )
        else:
            # Use GridSearchCV for simpler models
            search = GridSearchCV(
                estimator=config['model'],
                param_grid=config['params'],
                cv=5,
                scoring='r2',
                n_jobs=-1,
                verbose=0
            )
        
        # Fit the search
        search.fit(X_train_scaled, y_train)
        
        # Get best model
        best_model = search.best_estimator_
        best_models[model_name] = best_model
        
        # Make predictions
        y_pred_train = best_model.predict(X_train_scaled)
        y_pred_test = best_model.predict(X_test_scaled)
        
        # Calculate metrics
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        test_mse = mean_squared_error(y_test, y_pred_test)
        test_rmse = np.sqrt(test_mse)
        test_mae = mean_absolute_error(y_test, y_pred_test)
        
        # Cross-validation score
        cv_scores = cross_val_score(best_model, X_train_scaled, y_train, cv=5, scoring='r2')
        
        # Store results
        tuning_results[model_name] = {
            'best_params': search.best_params_,
            'best_cv_score': search.best_score_,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'test_mse': test_mse,
            'test_rmse': test_rmse,
            'test_mae': test_mae,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'training_time': time.time() - start_time,
            'predictions': y_pred_test
        }
        
        print(f"   ✅ Best CV Score: {search.best_score_:.4f}")
        print(f"   ✅ Test R²: {test_r2:.4f}")
        print(f"   ✅ Test RMSE: ₹{test_rmse:.2f}K")
        print(f"   ✅ Test MAE: ₹{test_mae:.2f}K")
        print(f"   ⏱️  Training Time: {time.time() - start_time:.1f}s")
        print(f"   🎯 Best Parameters: {search.best_params_}")
        
    except Exception as e:
        print(f"   ❌ Error tuning {model_name}: {e}")
        continue

# Results Analysis
if tuning_results:
    print("\n" + "="*100)
    print("🏆 HYPERPARAMETER TUNING RESULTS")
    print("="*100)
    
    # Create results DataFrame
    results_data = {}
    for model_name, results in tuning_results.items():
        results_data[model_name] = {
            'Best CV Score': results['best_cv_score'],
            'Train R²': results['train_r2'],
            'Test R²': results['test_r2'],
            'Test RMSE': results['test_rmse'],
            'Test MAE': results['test_mae'],
            'CV Mean': results['cv_mean'],
            'CV Std': results['cv_std'],
            'Training Time (s)': results['training_time']
        }
    
    results_df = pd.DataFrame(results_data).T.round(4)
    print(results_df)
    
    # Find overall best model
    best_model_name = results_df['Test R²'].idxmax()
    best_score = results_df.loc[best_model_name, 'Test R²']
    best_model = best_models[best_model_name]
    
    print(f"\n🏆 BEST TUNED MODEL: {best_model_name}")
    print(f"   📈 Test R²: {best_score:.4f} ({best_score*100:.1f}% accuracy)")
    print(f"   📉 Test RMSE: ₹{tuning_results[best_model_name]['test_rmse']:.2f}K")
    print(f"   📊 Test MAE: ₹{tuning_results[best_model_name]['test_mae']:.2f}K")
    print(f"   🎯 Best Parameters:")
    for param, value in tuning_results[best_model_name]['best_params'].items():
        print(f"      • {param}: {value}")
    
    # Comparison with base models
    try:
        base_results = joblib.load('car_model_results.pkl')
        print(f"\n📊 IMPROVEMENT COMPARISON:")
        print(f"{'Model':<25} {'Base R²':<10} {'Tuned R²':<10} {'Improvement'}")
        print("-" * 55)
        
        for model_name in tuning_results.keys():
            if model_name.replace(' ', '_').lower() in [k.replace(' ', '_').lower() for k in base_results.keys()]:
                # Find matching base model
                base_key = None
                for k in base_results.keys():
                    if k.replace(' ', '_').lower() == model_name.replace(' ', '_').lower():
                        base_key = k
                        break
                
                if base_key:
                    base_r2 = base_results[base_key]['Test R²']
                    tuned_r2 = tuning_results[model_name]['test_r2']
                    improvement = tuned_r2 - base_r2
                    print(f"{model_name:<25} {base_r2:<10.4f} {tuned_r2:<10.4f} {improvement:+.4f}")
    except:
        print("   ℹ️  Base model results not found for comparison")
    
    # Visualizations
    print(f"\n📊 Creating Visualization...")
    
    # Performance comparison plot
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Model Performance Comparison
    plt.subplot(2, 2, 1)
    models = list(tuning_results.keys())
    test_r2_scores = [tuning_results[model]['test_r2'] for model in models]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    bars = plt.bar(models, test_r2_scores, color=colors[:len(models)], alpha=0.8)
    plt.title('Model Performance (Test R²)', fontweight='bold')
    plt.ylabel('R² Score')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, score in zip(bars, test_r2_scores):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005, 
                f'{score:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: RMSE Comparison
    plt.subplot(2, 2, 2)
    rmse_scores = [tuning_results[model]['test_rmse'] for model in models]
    bars = plt.bar(models, rmse_scores, color=colors[:len(models)], alpha=0.8)
    plt.title('Model Error (Test RMSE)', fontweight='bold')
    plt.ylabel('RMSE (₹K)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    for bar, rmse in zip(bars, rmse_scores):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
                f'{rmse:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 3: Training Time Comparison
    plt.subplot(2, 2, 3)
    training_times = [tuning_results[model]['training_time'] for model in models]
    bars = plt.bar(models, training_times, color=colors[:len(models)], alpha=0.8)
    plt.title('Training Time Comparison', fontweight='bold')
    plt.ylabel('Time (seconds)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    for bar, time_val in zip(bars, training_times):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(training_times)*0.01, 
                f'{time_val:.1f}s', ha='center', va='bottom', fontweight='bold')
    
    # Plot 4: Best Model Predictions vs Actual
    plt.subplot(2, 2, 4)
    best_predictions = tuning_results[best_model_name]['predictions']
    plt.scatter(y_test, best_predictions, alpha=0.6, color='blue')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel('Actual Price (₹ Lakh)')
    plt.ylabel('Predicted Price (₹ Lakh)')
    plt.title(f'Best Model: {best_model_name}\nActual vs Predicted', fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('hyperparameter_tuning_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Save tuned models
    print(f"\n💾 Saving Results...")
    
    # Save best tuned model
    best_model_filename = f'best_tuned_model_{best_model_name.lower().replace(" ", "_")}.pkl'
    joblib.dump(best_model, best_model_filename)
    joblib.dump(best_model, 'best_car_price_model_tuned.pkl')  # Generic name
    
    # Save all tuning results
    joblib.dump(tuning_results, 'hyperparameter_tuning_results.pkl')
    joblib.dump(best_models, 'all_tuned_models.pkl')
    joblib.dump(results_df, 'tuning_comparison.pkl')
    
    print(f"   ✅ Best tuned model: {best_model_filename}")
    print(f"   ✅ Generic tuned model: best_car_price_model_tuned.pkl")
    print(f"   ✅ All results: hyperparameter_tuning_results.pkl")
    print(f"   ✅ Comparison table: tuning_comparison.pkl")
    print(f"   ✅ Visualization: hyperparameter_tuning_results.png")
    
    # Performance interpretation
    print(f"\n🎯 TUNED MODEL PERFORMANCE:")
    if best_score >= 0.95:
        print("🟢 EXCELLENT: Hypertuning achieved exceptional performance (>95%)")
    elif best_score >= 0.90:
        print("🟢 VERY GOOD: Hypertuning significantly improved performance (90-95%)")
    elif best_score >= 0.85:
        print("🟡 GOOD: Hypertuning provided solid improvement (85-90%)")
    else:
        print("🟠 FAIR: Consider more advanced techniques or feature engineering")
    
    print(f"\n💰 Expected Prediction Accuracy:")
    mae = tuning_results[best_model_name]['test_mae']
    print(f"   • Average error: ±₹{mae:.2f}K")
    print(f"   • For ₹5L car: ±₹{mae:.1f}K ({(mae/5)*100:.1f}% error)")
    print(f"   • For ₹15L car: ±₹{mae:.1f}K ({(mae/15)*100:.1f}% error)")

else:
    print("❌ No models were successfully tuned")

print(f"\n" + "="*60)
print("🎉 HYPERPARAMETER TUNING COMPLETE!")
print("="*60)
print("🚀 Next: Run 'python model_evaluation.py' for detailed evaluation")
print("💡 Tip: Use the best tuned model in your Flask API for better accuracy")
