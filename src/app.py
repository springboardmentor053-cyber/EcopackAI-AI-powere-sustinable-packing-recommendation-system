from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os
import psycopg2
from psycopg2.extras import RealDictCursor

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file

# Configuration
ARTIFACTS_DIR = 'models_artifacts'
DATA_PATH = 'data/feature_engineered_materials.csv'

# Configure Gemini
# In a real dep, use: os.getenv('GEMINI_API_KEY')
# For now, we will try to look for it, or handle the case where it's missing gracefully.
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
else:
    print("Warning: GEMINI_API_KEY not found in environment variables. AI Insights will be disabled.")

class PackagingRecommender:
    def __init__(self):
        self.preprocessor = joblib.load(os.path.join(ARTIFACTS_DIR, 'preprocessor.pkl'))
        self.cost_model = joblib.load(os.path.join(ARTIFACTS_DIR, 'cost_model.pkl'))
        self.co2_model = joblib.load(os.path.join(ARTIFACTS_DIR, 'co2_model.pkl'))
        
    def predict_metrics(self, df):
        # Transform features
        # We need to ensure the dataframe matches the training structure
        X_processed = self.preprocessor.transform(df)
        
        predicted_cost = self.cost_model.predict(X_processed)
        predicted_co2 = self.co2_model.predict(X_processed)
        
        return predicted_cost, predicted_co2

    def rank_materials(self, df, preferred_category=None, weights={'sustainability': 0.4, 'cost': 0.3, 'co2': 0.3}):
        """
        Ranks materials based on Sustainability Score, Predicted Cost, and Predicted CO2.
        """
        # Filter by category if provided and it exists in the data
        # Note: 'material_type' is a feature, but maybe 'category' implies a broader filter?
        # The prompt asks for "product category" input, but our dataset has 'material_type'.
        # We will assume the user might want to filter by valid material types if they specify one,
        # OR we just rank everything suitable for the use-case.
        # For this milestone, we'll rank the provided dataframe (which represents our catalog).
        
        # Get predictions
        pred_cost, pred_co2 = self.predict_metrics(df)
        
        df = df.copy()
        df['predicted_cost'] = pred_cost
        df['predicted_co2'] = pred_co2
        
        # Normalize to 0-1 range for fair weighting
        # Sustainability (Higher is better)
        sus_min = df['sustainability_score'].min()
        sus_max = df['sustainability_score'].max()
        sus_denom = sus_max - sus_min if sus_max != sus_min else 1
        
        sus_norm = (df['sustainability_score'] - sus_min) / sus_denom
                   
        # Cost (Lower is better) -> Invert
        cost_min = df['predicted_cost'].min()
        cost_max = df['predicted_cost'].max()
        cost_denom = cost_max - cost_min if cost_max != cost_min else 1
        
        cost_norm = (df['predicted_cost'] - cost_min) / cost_denom
        cost_score = 1 - cost_norm
        
        # CO2 (Lower is better) -> Invert
        co2_min = df['predicted_co2'].min()
        co2_max = df['predicted_co2'].max()
        co2_denom = co2_max - co2_min if co2_max != co2_min else 1
        
        co2_norm = (df['predicted_co2'] - co2_min) / co2_denom
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

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize Recommender
recommender = PackagingRecommender()

# Load Data (Catalog)
# In a real scenario, we might fetch this from DB.
# We will implement a function to try DB, else CSV.
def get_catalog_data():
    # Try Database Connection
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="echo_pack",
            user="postgres",
            password="123456"
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM ml.material_features") 
        data = cur.fetchall()
        df = pd.DataFrame(data)
        conn.close()
        print("Loaded data from Database (ml.material_features).")
        return df
    except Exception as e:
        print(f"Database connection failed: {e}. Falling back to CSV.")
        return pd.read_csv(DATA_PATH)

catalog_df = get_catalog_data()

@app.route('/')
def home():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../frontend', path)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "EcoPackAI Backend"})

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        
        # Inputs (Features expected for new inferences, or just user preference to filter catalog)
        # The prompt says: "Accept prod input parameters (weight, durability...)" and 
        # "Invoking trained ML models ... Generating recommendations"
        
        # Option A: The user is specifying a NEW material configuration to predict? 
        # Option B: The user is specifying requirements (Weight > 5kg) and we filter the catalog and rank?
        
        # Given "Recommendation System", usually we rank EXISTING inventory (Catalog).
        # However, the models (Cost/CO2) are predictive. 
        # If we just rank the catalog, we can pre-calculate cost/co2.
        # But maybe the cost depends on specific shipment parameters? 
        # The trained models take: material_type, strength, weight_capacity, etc.
        
        # Let's assume the user enters requirements (e.g. "I need 10kg capacity").
        # The logic should be:
        # 1. Filter catalog for materials that meets HARD constraints (e.g. weight_capacity >= 10)
        # 2. For the remaining candidates, use value-add of models if dynamic? 
        #    Actually, the models predict Cost/CO2 based on material attributes. 
        #    If attributes are fixed per material_id, predictions are static.
        
        # Let's Implement: Filter Catalog -> Rank.
        
        weight_req = float(data.get('weight_capacity_kg', 0))
        strength_req = float(data.get('strength', 0))
        water_res_req = int(data.get('water_resistance', 0)) # 0 or 1
        
        # Filter Logic
        filtered_df = catalog_df.copy()
        
        # Filter by capacity (Allowing some buffer or strict?) -> Strict for validated safety
        if weight_req > 0:
            filtered_df = filtered_df[filtered_df['weight_capacity_kg'] >= weight_req]
            
        if strength_req > 0:
            filtered_df = filtered_df[filtered_df['strength'] >= strength_req]
            
        if water_res_req == 1:
            # Assuming water_resistance is 0/1 or similar.
            # Check data type
            filtered_df = filtered_df[filtered_df['water_resistance'] >= 1]

        if filtered_df.empty:
            return jsonify({"message": "No materials found matching requirements", "recommendations": []})

        # Rank candidates
        ranked_df = recommender.rank_materials(filtered_df)
        
        # Format response
        results = []
        top_materials_context = []
        
        for index, row in ranked_df.head(10).iterrows():
            item_desc = f"{row.get('material_type', 'Unknown')} (Cost: {round(row['predicted_cost'], 2)}, CO2: {round(row['predicted_co2'], 2)}, Score: {row.get('sustainability_score', 0)})"
            if len(top_materials_context) < 3:
                top_materials_context.append(item_desc)
                
            results.append({
                "material_id": row.get('material_id', 'N/A'),
                "material_name": row.get('material_type', 'Unknown'),
                "predicted_cost": round(row['predicted_cost'], 2),
                "predicted_co2": round(row['predicted_co2'], 2),
                "sustainability_score": row.get('sustainability_score', 0),
                "rank_score": round(row['rank_score'], 4),
                "description": f"Strength: {row.get('strength')}, Max Load: {row.get('weight_capacity_kg')}kg"
            })
            
        # Generate AI Insight
        ai_insight = "Gemini API Key missing. Enable to see AI insights."
        if GEMINI_KEY and top_materials_context:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = (
                    f"You are an expert in sustainable packaging. "
                    f"The user needs packaging for a product weighing {weight_req}kg with strength {strength_req}. "
                    f"Our system recommended these top 3 materials based on Cost, CO2, and Sustainability: {'; '.join(top_materials_context)}. "
                    f"Provide a brief, professional summary (max 2 sentences) explaining WHY these are good sustainability choices."
                )
                response = model.generate_content(prompt)
                ai_insight = response.text
            except Exception as e:
                ai_insight = f"AI Insight unavailable: {str(e)}"

        return jsonify({
            "count": len(results),
            "ai_insight": ai_insight,
            "recommendations": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
