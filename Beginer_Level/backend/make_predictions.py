
import pandas as pd
import joblib
import numpy as np

def predict_house_price(crim, zn, indus, chas, nox, rm, age, dis, rad, tax, ptratio, b, lstat):
    """
    Predict house price using the trained model
    """
    # Load the trained model
    try:
        model = joblib.load('best_gradient_boosting_model_tuned.pkl')
    except:
        print("❌ Could not load the trained model!")
        return None

    # Create input DataFrame with proper feature names
    features = pd.DataFrame({
        'CRIM': [crim],
        'ZN': [zn],
        'INDUS': [indus],
        'CHAS': [chas],
        'NOX': [nox],
        'RM': [rm],
        'AGE': [age],
        'DIS': [dis],
        'RAD': [rad],
        'TAX': [tax],
        'PTRATIO': [ptratio],
        'B': [b],
        'LSTAT': [lstat]
    })

    # Make prediction
    prediction = model.predict(features)[0]
    return prediction

# Example usage
if __name__ == "__main__":
    print("=== Boston House Price Predictor ===")

    # Example 1: Average Boston house
    print("Example 1 - Average Boston house:")
    price1 = predict_house_price(
        crim=0.26, zn=0, indus=9.69, chas=0, nox=0.538, rm=6.2, 
        age=77.5, dis=3.2, rad=5, tax=330, ptratio=19.05, b=391.44, lstat=11.36
    )
    print(f"Predicted price: ${price1:.1f}K")

    # Example 2: High-end house (more rooms, low crime, river view)
    print("Example 2 - High-end house:")
    price2 = predict_house_price(
        crim=0.01, zn=25, indus=2.3, chas=1, nox=0.4, rm=8.0, 
        age=30, dis=6.0, rad=1, tax=200, ptratio=15.0, b=396, lstat=3.0
    )
    print(f"Predicted price: ${price2:.1f}K")

    # Example 3: Lower-end house (high crime, fewer rooms)
    print("Example 3 - Lower-end house:")
    price3 = predict_house_price(
        crim=15.0, zn=0, indus=18.1, chas=0, nox=0.7, rm=4.5, 
        age=95, dis=1.5, rad=24, tax=666, ptratio=20.2, b=350, lstat=25.0
    )
    print(f"Predicted price: ${price3:.1f}K")

    print("Prediction system ready for use!")