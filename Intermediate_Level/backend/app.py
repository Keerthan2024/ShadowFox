from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)

# Global storage for prediction analytics
prediction_analytics = {
    'total_predictions': 0,
    'price_history': [],
    'model_usage': {},
    'fuel_type_stats': {},
    'year_stats': {},
    'daily_stats': {}
}

# Load model and components
model = None
scaler = None
feature_names = None
label_encoders = None

model_files = [
    'best_car_price_model.pkl',
    'best_car_price_model_tuned.pkl',
    'best_car_price_model_random_forest.pkl',
    'best_car_price_model_lasso_regression.pkl'
]

print("🔍 Looking for trained models...")
for model_file in model_files:
    if os.path.exists(model_file):
        try:
            model = joblib.load(model_file)
            print(f"✅ Model loaded from: {model_file}")
            print(f"🤖 Model type: {type(model).__name__}")
            break
        except Exception as e:
            print(f"❌ Failed to load {model_file}: {e}")

# Load preprocessing components
try:
    preprocessing_data = joblib.load('car_data_preprocessed.pkl')
    if len(preprocessing_data) >= 5:
        scaler = preprocessing_data[4]
        feature_names = preprocessing_data[5]
        print("✅ Scaler and feature names loaded")
except Exception as e:
    print(f"⚠️ Could not load preprocessing data: {e}")

try:
    label_encoders = joblib.load('label_encoders.pkl')
    print("✅ Label encoders loaded")
except Exception as e:
    print(f"⚠️ Could not load label encoders: {e}")

# Load model evaluation results for EXACT accuracy
model_performance = {}
actual_accuracy = 85.35  # Your actual model accuracy

try:
    evaluation_results = joblib.load('model_evaluation_results.pkl')
    model_performance = evaluation_results
    
    # Get the EXACT test R² score
    if 'test_metrics' in evaluation_results:
        test_r2 = evaluation_results['test_metrics'].get('R² Score', 0.8535)
        actual_accuracy = round(test_r2 * 100, 2)  # Convert to percentage with 2 decimal places
        print(f"✅ Loaded actual model accuracy: {actual_accuracy}%")
    
except Exception as e:
    print(f"⚠️ Could not load evaluation results: {e}")

# Alternative: Try to load from model results
try:
    model_results = joblib.load('car_model_results.pkl')
    if 'Lasso Regression' in model_results:
        test_r2 = model_results['Lasso Regression']['Test R²']
        actual_accuracy = round(test_r2 * 100, 2)
        print(f"✅ Loaded Lasso model accuracy: {actual_accuracy}%")
except Exception as e:
    print(f"⚠️ Could not load model results: {e}")

def format_accuracy(accuracy_value):
    """Format accuracy to exactly 2 decimal places"""
    if isinstance(accuracy_value, str):
        # Extract number from string like "85.4%"
        import re
        match = re.search(r'(\d+\.?\d*)', accuracy_value)
        if match:
            accuracy_value = float(match.group(1))
        else:
            accuracy_value = 85.35
    
    return f"{accuracy_value:.2f}%"

# Feature information
FEATURE_INFO = {
    'car_name': {
        'name': 'Car Name/Model',
        'type': 'select',
        'options': ['city', 'corolla altis', 'verna', 'brio', 'fortuner', 'swift', 'dzire', 'i20', 'innova', 'baleno'],
        'description': 'Car model name'
    },
    'year': {
        'name': 'Year of Manufacture',
        'type': 'number',
        'min': 2003,
        'max': 2024,
        'description': 'Year when the car was manufactured'
    },
    'present_price': {
        'name': 'Present Price (₹ Lakh)',
        'type': 'number',
        'min': 0.32,
        'max': 92.6,
        'description': 'Current showroom price in lakhs'
    },
    'kms_driven': {
        'name': 'KM Driven',
        'type': 'number',
        'min': 500,
        'max': 500000,
        'description': 'Total kilometers driven'
    },
    'fuel_type': {
        'name': 'Fuel Type',
        'type': 'select',
        'options': ['Petrol', 'Diesel', 'CNG'],
        'description': 'Type of fuel used'
    },
    'seller_type': {
        'name': 'Seller Type',
        'type': 'select',
        'options': ['Dealer', 'Individual'],
        'description': 'Type of seller'
    },
    'transmission': {
        'name': 'Transmission',
        'type': 'select',
        'options': ['Manual', 'Automatic'],
        'description': 'Transmission type'
    },
    'owner': {
        'name': 'Number of Owners',
        'type': 'number',
        'min': 0,
        'max': 3,
        'description': 'Number of previous owners'
    }
}

def update_analytics(prediction_data, input_data):
    """Update prediction analytics"""
    try:
        prediction_analytics['total_predictions'] += 1
        
        # Store price history (keep last 100)
        prediction_analytics['price_history'].append({
            'price': prediction_data['prediction'],
            'timestamp': datetime.now().isoformat(),
            'car_name': input_data.get('car_name', 'unknown'),
            'year': input_data.get('year', 2018),
            'fuel_type': input_data.get('fuel_type', 'unknown')
        })
        
        if len(prediction_analytics['price_history']) > 100:
            prediction_analytics['price_history'] = prediction_analytics['price_history'][-100:]
        
        # Update other stats...
        model_name = input_data.get('car_name', 'unknown')
        prediction_analytics['model_usage'][model_name] = prediction_analytics['model_usage'].get(model_name, 0) + 1
        
    except Exception as e:
        print(f"Error updating analytics: {e}")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'model_type': str(type(model).__name__) if model else None,
        'scaler_loaded': scaler is not None,
        'encoders_loaded': label_encoders is not None,
        'message': 'Car Price Prediction API is running!',
        'features_available': len(feature_names) if feature_names else 0,
        'model_accuracy': format_accuracy(actual_accuracy),  # ✅ Fixed to 2 decimals
        'total_predictions': prediction_analytics['total_predictions'],
        'api_version': '2.0'
    })

@app.route('/api/features', methods=['GET'])
def get_features():
    return jsonify({
        'features': FEATURE_INFO,
        'total_features': len(FEATURE_INFO),
        'model_features': feature_names if feature_names else [],
        'required_features': ['present_price', 'kms_driven', 'fuel_type', 'seller_type', 'transmission']
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        if model is None:
            return jsonify({'error': 'Model not loaded. Please train the model first.'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        print(f"📥 Received prediction request: {data}")
        
        # Create feature vector matching your trained model
        feature_vector = []
        
        if feature_names and scaler:
            for feature_name in feature_names:
                if feature_name == 'present_price':
                    feature_vector.append(float(data.get('present_price', 5.0)))
                elif feature_name == 'kms_driven':
                    feature_vector.append(float(data.get('kms_driven', 30000)))
                elif feature_name == 'owner':
                    feature_vector.append(float(data.get('owner', 0)))
                elif feature_name == 'car_age':
                    year = int(data.get('year', 2015))
                    car_age = 2024 - year
                    feature_vector.append(float(car_age))
                elif feature_name == 'price_per_km':
                    present_price = float(data.get('present_price', 5.0))
                    kms_driven = float(data.get('kms_driven', 30000))
                    price_per_km = present_price / (kms_driven + 1)
                    feature_vector.append(price_per_km)
                elif feature_name == 'depreciation_rate':
                    present_price = float(data.get('present_price', 5.0))
                    estimated_selling = present_price * 0.7
                    depreciation_rate = (present_price - estimated_selling) / present_price
                    feature_vector.append(depreciation_rate)
                elif feature_name.endswith('_encoded') and label_encoders:
                    original_name = feature_name.replace('_encoded', '')
                    if original_name in data and original_name in label_encoders:
                        try:
                            encoded_value = label_encoders[original_name].transform([str(data[original_name])])[0]
                            feature_vector.append(float(encoded_value))
                        except Exception as e:
                            print(f"Warning: Could not encode {original_name}: {e}")
                            # Use default values
                            default_values = {
                                'fuel_type': 2.0,  # Petrol
                                'seller_type': 0.0,  # Dealer
                                'transmission': 1.0,  # Manual
                                'car_name': 69.0  # city
                            }
                            feature_vector.append(default_values.get(original_name, 0.0))
                    else:
                        default_values = {
                            'fuel_type_encoded': 2.0,
                            'seller_type_encoded': 0.0,
                            'transmission_encoded': 1.0,
                            'car_name_encoded': 69.0
                        }
                        feature_vector.append(default_values.get(feature_name, 0.0))
                else:
                    feature_vector.append(0.0)
            
            # Convert to numpy array and scale
            input_array = np.array([feature_vector])
            input_scaled = scaler.transform(input_array)
            
            # Make prediction
            prediction = model.predict(input_scaled)[0]
            prediction = max(0.1, prediction)  # Ensure positive prediction
            
        else:
            return jsonify({'error': 'Model components not properly loaded'}), 500
        
        # Calculate confidence
        present_price = float(data.get('present_price', 5.0))
        confidence = 85
        
        if 0.5 <= prediction <= present_price * 1.2:
            confidence = min(95, confidence + 5)
        elif prediction > present_price:
            confidence = max(60, confidence - 15)
        
        # Create response with EXACT accuracy
        response_data = {
            'prediction': round(prediction, 2),
            'price_formatted': f"₹{prediction:.2f} Lakh",
            'confidence': int(confidence),
            'model': str(type(model).__name__),
            'model_accuracy': format_accuracy(actual_accuracy),  # ✅ Fixed to 2 decimals
            'input_features': data,
            'message': f"Predicted selling price: ₹{prediction:.2f} Lakh",
            'prediction_id': prediction_analytics['total_predictions'] + 1,
            'timestamp': datetime.now().isoformat()
        }
        
        # Update analytics
        update_analytics(response_data, data)
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/api/model-info', methods=['GET'])
def model_info():
    if model is None:
        return jsonify({'error': 'No model loaded'}), 404
    
    try:
        model_stats = {
            'model_type': str(type(model).__name__),
            'model_name': 'Lasso Regression' if 'Lasso' in str(type(model).__name__) else str(type(model).__name__),
            'feature_count': len(feature_names) if feature_names else 0,
            'features': feature_names if feature_names else [],
            'training_samples': 239,
            'testing_samples': 60,
            'accuracy': format_accuracy(actual_accuracy)  # ✅ Fixed to 2 decimals
        }
        
        # Add model performance metrics if available
        if model_performance and 'test_metrics' in model_performance:
            test_metrics = model_performance['test_metrics']
            model_stats.update({
                'test_r2': round(test_metrics.get('R² Score', 0.8535), 4),
                'test_mae': f"₹{test_metrics.get('MAE', 1.16):.2f}K",
                'test_rmse': f"₹{test_metrics.get('RMSE', 1.94):.2f}K",
                'cv_mean': round(np.mean(model_performance.get('cv_scores', [0.88])), 4) if model_performance.get('cv_scores') else 0.88
            })
        
        return jsonify(model_stats)
        
    except Exception as e:
        print(f"Error in model-info: {e}")
        return jsonify({
            'model_type': str(type(model).__name__) if model else 'Unknown',
            'model_name': 'Lasso Regression',
            'accuracy': format_accuracy(actual_accuracy),  # ✅ Fixed to 2 decimals
            'feature_count': len(feature_names) if feature_names else 0,
            'features': feature_names if feature_names else []
        })

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get comprehensive prediction analytics"""
    try:
        if prediction_analytics['price_history']:
            prices = [p['price'] for p in prediction_analytics['price_history']]
            analytics_summary = {
                'total_predictions': prediction_analytics['total_predictions'],
                'average_price': round(np.mean(prices), 2) if prices else 0,
                'price_range': {
                    'min': round(min(prices), 2) if prices else 0,
                    'max': round(max(prices), 2) if prices else 0
                },
                'price_history': prediction_analytics['price_history'][-50:],
                'model_accuracy': format_accuracy(actual_accuracy),  # ✅ Fixed to 2 decimals
                'model_usage': prediction_analytics['model_usage'],
                'fuel_type_stats': prediction_analytics['fuel_type_stats'],
                'year_stats': prediction_analytics['year_stats'],
                'daily_stats': prediction_analytics['daily_stats']
            }
        else:
            analytics_summary = {
                'total_predictions': 0,
                'average_price': 0,
                'price_range': {'min': 0, 'max': 0},
                'price_history': [],
                'model_accuracy': format_accuracy(actual_accuracy),  # ✅ Fixed to 2 decimals
                'model_usage': {},
                'fuel_type_stats': {},
                'year_stats': {},
                'daily_stats': {}
            }
        
        return jsonify(analytics_summary)
        
    except Exception as e:
        print(f"Error in analytics: {e}")
        return jsonify({'error': 'Failed to fetch analytics'}), 500

if __name__ == '__main__':
    print("\n🚗 Starting Enhanced Car Price Prediction API...")
    
    if model is None:
        print("❌ NO MODEL LOADED!")
    else:
        print("✅ Enhanced API loaded successfully!")
        print(f"🤖 Model type: {type(model).__name__}")
        print(f"📊 Model accuracy: {format_accuracy(actual_accuracy)}")  # ✅ Fixed display
        print(f"📏 Features: {len(feature_names) if feature_names else 'Unknown'}")
    
    print("\n🔗 Enhanced API endpoints:")
    print("   - GET  /api/health")
    print("   - GET  /api/features") 
    print("   - GET  /api/model-info")
    print("   - GET  /api/analytics")
    print("   - POST /api/predict")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
