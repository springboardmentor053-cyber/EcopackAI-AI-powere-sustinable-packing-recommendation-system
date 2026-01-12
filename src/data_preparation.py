import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import joblib
import os

# Configuration
DATA_PATH = 'data/feature_engineered_materials.csv'
ARTIFACTS_DIR = 'models_artifacts'
PROCESSED_DATA_DIR = 'data/final'

# Ensure directories exist
os.makedirs(ARTIFACTS_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

def load_data(path):
    print(f"Loading data from {path}...")
    df = pd.read_csv(path)
    return df

def prepare_data(df):
    print("Preprocessing data...")
    
    # Define features and targets
    # Note: 'material_suitability_score' is reserved for the ranking logic, not necessarily a feature for cost/co2 basic prediction unless specified.
    # We excluded 'co2_emission_score' and 'cost_per_unit_inr' from features as they are targets.
    
    feature_cols = [
        'material_type', 
        'strength', 
        'weight_capacity_kg', 
        'biodegradability_score', 
        'recyclability_percent',
        'water_resistance'
    ]
    
    target_cost = 'cost_per_unit_inr'
    target_co2 = 'co2_emission_score'
    
    X = df[feature_cols]
    y_cost = df[target_cost]
    y_co2 = df[target_co2]
    
    # Preprocessing Pipelines
    # Numeric features
    numeric_features = ['strength', 'weight_capacity_kg', 'biodegradability_score', 'recyclability_percent']
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # Categorical features
    categorical_features = ['material_type', 'water_resistance']
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    # Fit the preprocessor
    print("Fitting preprocessor...")
    X_processed = preprocessor.fit_transform(X)
    
    # Save the preprocessor
    joblib.dump(preprocessor, os.path.join(ARTIFACTS_DIR, 'preprocessor.pkl'))
    print("Preprocessor saved.")
    
    # Split data
    # We need to split X, y_cost, and y_co2. 
    # We will just split indices or split X and then split ys using same seed? 
    # Better: Split the dataframe first, then separate.
    
    # However, since we process X, let's split the numpy arrays.
    indices = np.arange(len(df))
    X_train, X_test, idx_train, idx_test = train_test_split(X_processed, indices, test_size=0.2, random_state=42)
    
    y_cost_train = y_cost.iloc[idx_train]
    y_cost_test = y_cost.iloc[idx_test]
    
    y_co2_train = y_co2.iloc[idx_train]
    y_co2_test = y_co2.iloc[idx_test]
    
    # Save processed datasets
    print("Saving processed datasets...")
    np.save(os.path.join(PROCESSED_DATA_DIR, 'X_train.npy'), X_train)
    np.save(os.path.join(PROCESSED_DATA_DIR, 'X_test.npy'), X_test)
    
    y_cost_train.to_csv(os.path.join(PROCESSED_DATA_DIR, 'y_cost_train.csv'), index=False)
    y_cost_test.to_csv(os.path.join(PROCESSED_DATA_DIR, 'y_cost_test.csv'), index=False)
    
    y_co2_train.to_csv(os.path.join(PROCESSED_DATA_DIR, 'y_co2_train.csv'), index=False)
    y_co2_test.to_csv(os.path.join(PROCESSED_DATA_DIR, 'y_co2_test.csv'), index=False)
    
    # Also save the original test partition for validation/viewing purposes
    df_test = df.iloc[idx_test]
    df_test.to_csv(os.path.join(PROCESSED_DATA_DIR, 'test_data_original.csv'), index=False)
    
    print("Data preparation complete.")
    
    # Basic statistical validation
    print("\nDataset Statistics:")
    print(f"Training set size: {X_train.shape[0]}")
    print(f"Test set size: {X_test.shape[0]}")
    print(f"Number of features: {X_train.shape[1]}")

if __name__ == "__main__":
    df = load_data(DATA_PATH)
    prepare_data(df)
