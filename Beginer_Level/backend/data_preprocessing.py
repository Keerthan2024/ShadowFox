
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

print("=== Boston House Price Prediction - Data Loading ===")

# Load CSV with the first row as header
try:
    data = pd.read_csv('BostonHousing.csv', header=0)
    # The first row contains real headers, so reset the dataframe columns with the first row and drop it from data
    data.columns = data.iloc[0]
    data = data.drop(data.index[0])
    # Reset index
    data = data.reset_index(drop=True)

    # Convert all columns to numeric type, coercing errors (due to header row that was mixed)
    data = data.apply(pd.to_numeric, errors='coerce')

    print("✓ Successfully loaded and cleaned data from BostonHousing.csv")
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# Dataset overview
print(f"Dataset shape: {data.shape}")
print(f"Columns: {list(data.columns)}")
print(f"First 5 rows:", data.head())

print(f"Dataset Info:")
print(data.info())

print(f"Missing Values Check:")
print(data.isnull().sum())

print(f"Basic Statistics:")
print(data.describe())

# Check for target variable
if 'MEDV' in data.columns:
    print(f"Target variable identified: MEDV")
    print(data['MEDV'].describe())
else:
    print("Could not identify target variable automatically.")
