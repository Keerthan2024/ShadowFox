
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Load the cleaned data

try:
    data = pd.read_csv('BostonHousing.csv', header=0)
    data.columns = data.iloc[0]
    data = data.drop(data.index[0]).reset_index(drop=True)
    data = data.apply(pd.to_numeric, errors='coerce')
    print("Successfully loaded cleaned Boston Housing data for Phase 2")
except Exception as e:
    print(f"Error loading data : {e}")
    exit()

# Exploratory Data Analysis & Visualization

print("Summary Statistics:", data.describe())

# Check for outliers using boxplots
plt.figure(figsize=(15,10))
sns.boxplot(data=data)
plt.title('Boxplot for Boston Housing Features')
plt.xticks(rotation=45)
plt.show()

# Check correlation with heatmap
plt.figure(figsize=(12,10))
corr = data.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Heatmap')
plt.show()

# Drop any duplicate rows if present
data = data.drop_duplicates()

# Target variable
target = 'MEDV'

# Feature and target separation
X = data.drop(columns=[target])
y = data[target]

# Split data into train and test sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature scaling with StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"Training data shape: {X_train_scaled.shape}")
print(f"Testing data shape: {X_test_scaled.shape}")

# Save the processed data for next phases
import joblib
joblib.dump((X_train_scaled, X_test_scaled, y_train, y_test), 'boston_data_preprocessed.pkl')

print("Data is preprocessed and saved for modeling.")