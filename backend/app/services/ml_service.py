
import pandas as pd
import joblib
import os
from .db_service import db_service
import google.generativeai as genai
import json
import re


class MLService:
    def __init__(self):
        self.cost_model = None
        self.co2_model = None
        self.tavily = None
        self._setup_apis()
        self._load_models()

    def _setup_apis(self):
        """Initialize external APIs."""
        try:
            # You should set these in your .env / environment variables
            google_key = os.getenv("GOOGLE_API_KEY")
            
            if google_key:
                genai.configure(api_key=google_key)
            else:
                print("⚠️ GOOGLE_API_KEY not found in environment.")
                
        except Exception as e:
            print(f"⚠️ Error setting up APIs: {e}")

    def _load_models(self):
        """Load trained ML models from .pkl files."""
        try:
            # Path relative to this file: backend/app/services/ml_service.py
            # Models are in: models/
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up 3 levels to reach project root (backend/app/services -> backend/app -> backend -> root)
            model_dir = os.path.abspath(os.path.join(base_dir, '..', '..', '..', 'models'))
            
            cost_model_path = os.path.join(model_dir, 'cost_predictor_model.pkl')
            co2_model_path = os.path.join(model_dir, 'co2_predictor_model.pkl')
            
            if not os.path.exists(cost_model_path) or not os.path.exists(co2_model_path):
                print(f"⚠️ Models not found at {model_dir}")
                # Don't return, just run without models (Gemini only)
                # return

            else:
                self.cost_model = joblib.load(cost_model_path)
                self.co2_model = joblib.load(co2_model_path)
                print("✅ ML Models loaded successfully.")
        except Exception as e:
            print(f"❌ Error loading ML models: {e}")

    def get_recommendations(self, product_weight_kg, product_category, fragility='Medium', water_resistant=False, top_n=5, force_gemini=False):
        """Recommend materials based on product constraints and ML predictions."""
        engine = db_service.get_engine()
        
        candidates_df = pd.DataFrame()

        if engine and not force_gemini:
            # 1. Fetch Candidate Materials from DB
            # Try to find materials specifically recommended for this category first
            query = f"""
            SELECT DISTINCT
                fe.material_id, 
                fe.material_type, 
                fe.strength, 
                fe.weight_capacity_kg, 
                fe.biodegradability_score, 
                fe.recyclability_percent, 
                fe.water_resistance,
                fe.manufacturing_place
            FROM features_engineering fe
            JOIN product_material pm ON fe.material_id = pm.material_id
            WHERE pm.category = '{product_category}' 
            AND fe.weight_capacity_kg >= {product_weight_kg}
            """
            
            try:
                candidates_df = pd.read_sql(query, engine)
            except Exception as e:
                print(f"❌ Error fetching candidates: {e}")
                candidates_df = pd.DataFrame()

            # 1.5 Filter Initial Candidates
            if not candidates_df.empty:
                candidates_filtered = candidates_df.copy()

                # Debug: Print found candidates
                print(f"🔍 Candidates for '{product_category}': {len(candidates_df)} found in DB.")

                # Filter by Water Resistance
                if water_resistant:
                     candidates_filtered = candidates_filtered[candidates_filtered['water_resistance'] >= 1]
                     print(f"   Shape after water_resistance filter: {candidates_filtered.shape}")

                # Filter by Fragility
                if fragility == 'High':
                     candidates_filtered = candidates_filtered[candidates_filtered['strength'] >= 7]
                     print(f"   Shape after fragility filter: {candidates_filtered.shape}")
                
                candidates_df = candidates_filtered


            # LOGIC UPDATE: Fallback Mechanism (Broad Search in DB)
            # If strict category filtering leaves us with nothing, try finding ANY material that fits the physical specs
            if candidates_df.empty and engine:
                print(f"⚠️ No exact category matches found for '{product_category}' with constraints. Attempting broad search...")
                
                # Construct broad query based on physical constraints
                broad_conditions = [f"weight_capacity_kg >= {product_weight_kg}"]
                
                if water_resistant:
                    broad_conditions.append("water_resistance >= 1")
                
                if fragility == 'High':
                    broad_conditions.append("strength >= 7")
                    
                where_clause = " AND ".join(broad_conditions)
                
                broad_query = f"""
                SELECT * FROM features_engineering 
                WHERE {where_clause}
                """
                
                try:
                    candidates_df = pd.read_sql(broad_query, engine)
                    print(f"   Broad search found {len(candidates_df)} candidates.")
                except Exception as e:
                    print(f"❌ Error in broad search: {e}")
                    candidates_df = pd.DataFrame()


        # 1.8 Add Source Tag
        if not candidates_df.empty:
            candidates_df['source'] = 'database'

        # 2. Gemini Fallback
        if candidates_df.empty:
            print("⚠️ Database yielded no results. Initiating Gemini AI Generation...")
            candidates_df = self._generate_gemini_recommendations(product_category, product_weight_kg)
            if candidates_df.empty:
                return pd.DataFrame() # Give up

        # 3. Prepare Features for Prediction
        # Ensure columns exist (Tavily might return different set, need to normalize)
        required_cols = [
            'strength', 'weight_capacity_kg', 'biodegradability_score', 
            'recyclability_percent', 'water_resistance', 'material_type'
        ]
        
        # If from Tavily, we might need to rely on the model or Gemini's estimates
        # If the model fails, we might just return the Gemini data with fake scores
        
        try:
            X = candidates_df[required_cols]
            
            # 4. Generate Predictions
            if self.cost_model and self.co2_model:
                try:
                    pred_cost = self.cost_model.predict(X)
                    pred_co2 = self.co2_model.predict(X)
                    
                    # Update scores in DF
                    candidates_df['predicted_cost_inr'] = pred_cost
                    candidates_df['predicted_co2_score'] = pred_co2
                except Exception as e:
                    print(f"⚠️ ML Prediction failed (possibly unseen categories): {e}")
                    # If ML fails, use defaults or what Gemini provided
                    if 'predicted_cost_inr' not in candidates_df.columns:
                        candidates_df['predicted_cost_inr'] = candidates_df.get('estimated_cost', 50.0)
                    if 'predicted_co2_score' not in candidates_df.columns:
                        candidates_df['predicted_co2_score'] = 50.0

            # 5. Calculate Scores
            results_df = candidates_df.copy()
            
            # Ensure columns exist if ML skipped
            if 'predicted_cost_inr' not in results_df.columns:
                 results_df['predicted_cost_inr'] = 50.0
            if 'predicted_co2_score' not in results_df.columns:
                 results_df['predicted_co2_score'] = 50.0

            results_df['cost_efficiency_score'] = 100 / (results_df['predicted_cost_inr'] + 1e-5)
            results_df['eco_impact_score'] = 100 / (results_df['predicted_co2_score'] + 1e-5)
            
            results_df['final_rank_score'] = (
                0.5 * results_df['cost_efficiency_score'] + 
                0.5 * results_df['eco_impact_score']
            )

            return results_df.sort_values(by='final_rank_score', ascending=False).head(top_n)
            
        except Exception as e:
            print(f"❌ Error in recommendation flow: {e}")
            return pd.DataFrame()

    def _generate_gemini_recommendations(self, category, weight):
        """
        Generate sustainable packaging recommendations using Gemini (Generative AI)
        when database results are insufficient.
        """
        try:
            print(f"🧠 Generating recommendations with Gemini for: {category}, {weight}kg")
            
            prompt = f"""
            You are an expert in sustainable packaging and materials science.
            Identify 5 suitable, specifically eco-friendly packaging materials for a '{category}' product weighing {weight}kg.

            Focus on materials that are biodegradable, recyclable, or compostable.
            
            For each material, estimate realistic technical values:
            - material_type (Use standard names like 'Corrugated Cardboard', 'Bioplastic', 'Mushroom Packaging', 'Kraft Paper', 'Cornstarch Packing Peanuts')
            - strength (1-10 scale, integer, where 10 is strongest)
            - weight_capacity_kg (float, must be at least {weight} * 1.2 safety factor)
            - biodegradability_score (1-100 scale, integer)
            - recyclability_percent (0-100, float)
            - water_resistance (0 for No, 1 for Yes)
            - estimated_cost (in INR, approx value per unit/box)
            - manufacturing_place (e.g., 'India', 'Global', 'USA')

            Return strictly a JSON list of objects. Do not include markdown formatting like ```json ... ```. Just the raw JSON array.
            
            Example format:
            [
                {{"material_type": "Kraft Paper", "strength": 5, "weight_capacity_kg": 5.0, "biodegradability_score": 90, "recyclability_percent": 100, "water_resistance": 0, "estimated_cost": 20.0, "manufacturing_place": "India"}}
            ]
            """
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            text = response.text
            # Clean potential markdown wrapping
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                 text = text.split("```")[0]
            
            data = json.loads(text.strip())
            
            df = pd.DataFrame(data)
            df['source'] = 'gemini_ai'
            # Add missing columns expected by ML model or view
            df['material_id'] = -1 
            
            print(f"✅ Gemini generated {len(df)} candidates.")
            return df
            
        except Exception as e:
            print(f"❌ Gemini generation failed: {e}")
            return pd.DataFrame()

# Global Instance
ml_service = MLService()
