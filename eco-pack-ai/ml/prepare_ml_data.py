import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os

# Load training data
df = pd.read_csv('E:/Data Science/EcoPackAI/data/processed/ml_training_data.csv')

print(f"Total samples: {len(df)}")

# ============ ENCODE CATEGORICAL VARIABLES ============

# Columns to encode
categorical_cols = ['fragility_level', 'material_type']

# Create label encoders
encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[f'{col}_encoded'] = le.fit_transform(df[col])
    encoders[col] = le
    print(f"{col}: {dict(zip(le.classes_, le.transform(le.classes_)))}")

# Convert boolean columns to int
bool_cols = ['requires_cushioning', 'moisture_sensitive', 'temperature_sensitive']
for col in bool_cols:
    df[col] = df[col].astype(int)

# ============ SELECT FEATURES ============

# Features for ML model
feature_columns = [
    # Category features
    'fragility_level_encoded',
    'requires_cushioning',
    'moisture_sensitive', 
    'temperature_sensitive',
    
    # Product features
    'product_weight_kg',
    
    # Material features
    'material_type_encoded',
    'strength_score',
    'weight_capacity_kg',
    'biodegradability_score',
    'moisture_resistance',
    'co2_emission_kg',
    'cost_per_kg',
    
    # Engineered features
    'co2_impact_index',
    'cost_efficiency_index',
    'eco_score'
]

# Target columns
target_columns = ['suitability_score', 'predicted_co2', 'predicted_cost']

X = df[feature_columns]
y = df[target_columns]

print(f"\nFeatures: {len(feature_columns)}")
print(f"Targets: {len(target_columns)}")

# ============ TRAIN/TEST SPLIT ============

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nTraining samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")

# ============ SCALE FEATURES ============

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Convert back to DataFrame for clarity
X_train_scaled = pd.DataFrame(X_train_scaled, columns=feature_columns)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=feature_columns)

# ============ SAVE EVERYTHING ============

os.makedirs('ml/models', exist_ok=True)

# Save processed data
X_train_scaled.to_csv('data/processed/X_train.csv', index=False)
X_test_scaled.to_csv('data/processed/X_test.csv', index=False)
y_train.to_csv('data/processed/y_train.csv', index=False)
y_test.to_csv('data/processed/y_test.csv', index=False)

# Save encoders and scaler for later use
joblib.dump(encoders, 'ml/models/encoders.pkl')
joblib.dump(scaler, 'ml/models/scaler.pkl')

# Save feature column names
joblib.dump(feature_columns, 'ml/models/feature_columns.pkl')

print("\n✓ Saved X_train.csv, X_test.csv, y_train.csv, y_test.csv")
print("✓ Saved encoders.pkl, scaler.pkl, feature_columns.pkl")
print("\nData preparation complete. Ready for model training.")