import pandas as pd
import numpy as np
import joblib
import os

# Configuration
DATA_PATH = 'data/feature_engineered_materials.csv'
ARTIFACTS_DIR = 'models_artifacts'

class PackagingRecommender:
    def __init__(self):
        self.preprocessor = joblib.load(os.path.join(ARTIFACTS_DIR, 'preprocessor.pkl'))
        self.cost_model = joblib.load(os.path.join(ARTIFACTS_DIR, 'cost_model.pkl'))
        self.co2_model = joblib.load(os.path.join(ARTIFACTS_DIR, 'co2_model.pkl'))
        
    def predict_metrics(self, df):
        # We need to preprocess strictly the features expected by the pipeline
        # The preprocessor expects a DataFrame with specific columns.
        
        # Ensure input df has necessary columns, else fail or fill
        # This assumes df is raw data format
        
        X_processed = self.preprocessor.transform(df)
        
        predicted_cost = self.cost_model.predict(X_processed)
        predicted_co2 = self.co2_model.predict(X_processed)
        
        return predicted_cost, predicted_co2

    def rank_materials(self, df, weights={'sustainability': 0.4, 'cost': 0.3, 'co2': 0.3}):
        """
        Ranks materials based on Sustainability Score, Predicted Cost, and Predicted CO2.
        Higher Rank Score is better.
        """
        # Get predictions
        pred_cost, pred_co2 = self.predict_metrics(df)
        
        df = df.copy()
        df['predicted_cost'] = pred_cost
        df['predicted_co2'] = pred_co2
        
        # Normalize to 0-1 range for fair weighting
        # Sustainability (Higher is better)
        sus_norm = (df['sustainability_score'] - df['sustainability_score'].min()) / \
                   (df['sustainability_score'].max() - df['sustainability_score'].min())
                   
        # Cost (Lower is better) -> Invert
        cost_norm = (df['predicted_cost'] - df['predicted_cost'].min()) / \
                    (df['predicted_cost'].max() - df['predicted_cost'].min())
        cost_score = 1 - cost_norm
        
        # CO2 (Lower is better) -> Invert
        co2_norm = (df['predicted_co2'] - df['predicted_co2'].min()) / \
                   (df['predicted_co2'].max() - df['predicted_co2'].min())
        co2_score = 1 - co2_norm
        
        # Calculate Composite Score
        df['rank_score'] = (
            weights['sustainability'] * sus_norm + 
            weights['cost'] * cost_score + 
            weights['co2'] * co2_score
        )
        
        # Sort
        ranked_df = df.sort_values(by='rank_score', ascending=False)
        return ranked_df

if __name__ == "__main__":
    print("Initializing Recommender...")
    recommender = PackagingRecommender()
    
    # Load sample data (Treating the full dataset as our catalog for this demo)
    print(f"Loading catalog from {DATA_PATH}...")
    catalog_df = pd.read_csv(DATA_PATH)
    
    # Let's say we filter for a specific use-case first, e.g., "Food Delivery" if we had a category col
    # For now, we rank the top 10 materials from the entire dataset.
    
    print("\nRanking Materials...")
    ranked_materials = recommender.rank_materials(catalog_df)
    
    print("\nTop 5 Recommended Materials:")
    print(ranked_materials[['material_id', 'material_type', 'sustainability_score', 'predicted_cost', 'predicted_co2', 'rank_score']].head(5))
    
    # Validate logic with a specific single sample (Hypothetical)
    print("\nEvaluating Hypothetical New Material:")
    sample_data = pd.DataFrame([{
        'material_type': 'Bioplastic',
        'strength': 50,
        'weight_capacity_kg': 5,
        'biodegradability_score': 80,
        'recyclability_percent': 90,
        'water_resistance': 1, # High resistance
        'material_suitability_score': 85 # Assuming we calculated this separately
    }])
    
    # Note: water_resistance in training data was likely 0/1 or True/False? 
    # In my inspect, it showed '0.5' etc? No, `inspect_columns` just listed columns.
    # The `validate_data` head output was truncated.
    # I should check the unique values of water_resistance to be safe in the sample.
    # But for now I'll assume numeric/boolean. The preprocessor handles it.
    
    pred_cost, pred_co2 = recommender.predict_metrics(sample_data)
    print(f"Predicted Cost: {pred_cost[0]:.2f}")
    print(f"Predicted CO2: {pred_co2[0]:.2f}")
