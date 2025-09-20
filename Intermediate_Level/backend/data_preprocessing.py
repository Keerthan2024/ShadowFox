import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler
import warnings
warnings.filterwarnings('ignore')

print("=== Car Selling Price Prediction - Phase 1: Data Loading ===\n")

# Load the dataset
try:
    # Download the dataset from Google Drive manually and place it in data folder
    data = pd.read_csv('data/car_data.csv')
    print("✅ Dataset loaded successfully")
    print(f"Dataset shape: {data.shape}")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    print("Please download the dataset from the provided Google Drive link")
    print("and save it as 'data/car_data.csv'")
    exit()

# Display basic information
print(f"\n📊 Dataset Overview:")
print(f"Rows: {data.shape[0]}")
print(f"Columns: {data.shape[1]}")
print(f"\nColumn names:")
print(data.columns.tolist())

print(f"\n🔍 First 5 rows:")
print(data.head())

print(f"\n📈 Dataset Info:")
print(data.info())

print(f"\n❓ Missing Values:")
missing_values = data.isnull().sum()
print(missing_values[missing_values > 0])
if missing_values.sum() == 0:
    print("✅ No missing values found!")

print(f"\n📊 Basic Statistics:")
print(data.describe())

# Identify categorical and numerical columns
categorical_cols = data.select_dtypes(include=['object']).columns.tolist()
numerical_cols = data.select_dtypes(include=['int64', 'float64']).columns.tolist()

print(f"\n🏷️  Categorical columns: {categorical_cols}")
print(f"🔢 Numerical columns: {numerical_cols}")

# Display unique values for categorical columns
print(f"\n🎯 Unique values in categorical columns:")
for col in categorical_cols:
    print(f"{col}: {data[col].nunique()} unique values")
    print(f"   Values: {data[col].unique()[:10]}")  # Show first 10 unique values
    print()

print("=== Phase 1 Complete ===")
