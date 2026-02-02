from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import sys
import os

# Add EcopackAI root to path for imports
sys.path.insert(0, 'c:/EcopackAI')
from db_config import get_db_connection, query_materials, query_products

# web server
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# loading ml models
cost_model = joblib.load('c:/EcopackAI/ML model/cost_model.pkl')
co2_model = joblib.load('c:/EcopackAI/ML model/co2_model.pkl')

# Load materials from database (with fallback to hardcoded)
try:
    materials_db = query_materials()
    if not materials_db:
        raise Exception("No materials found in database")
    print(f"✓ Loaded {sum(len(v) for v in materials_db.values())} materials from database")
except Exception as e:
    print(f"⚠️  Could not load from database: {e}")
    print("  Using fallback materials...")
    materials_db = {
        'electronics': ['Recycled Cardboard', 'Foam Padding', 'Plastic Film'],
        'food': ['Biodegradable Plastic', 'Paper', 'Glass'],
        'cosmetics': ['Glass', 'Recyclable Plastic', 'Cardboard'],
        'Pharmaceuticals': ['Blister Packs', 'Glass Bottles', 'Cardboard'],
        'Beverages': ['Aluminum', 'Glass', 'Paper'],
        'Textile/Apparel': ['Recycled Cardboard', 'Paper', 'Biodegradable Plastic'],
        'Personal Care/Home': ['Recyclable Plastic', 'Glass', 'Cardboard'],
        'Household Appliances': ['Recycled Cardboard', 'Foam', 'Plastic'],
        'Furniture': ['Recycled Cardboard', 'Paper', 'Foam'],
        'Toys': ['Recyclable Plastic', 'Cardboard', 'Paper'],
        'Baby Care': ['Biodegradable Plastic', 'Cardboard', 'Paper'],
        'Industrial/Automotive': ['Metal', 'Recycled Cardboard', 'Plastic'],
        'Healthcare/Medical Devices': ['Sterilizable Plastic', 'Cardboard', 'Paper'],
        'Stationary': ['Recycled Cardboard', 'Paper', 'Plastic'],
        'Sports & Outdoor': ['Recycled Cardboard', 'Plastic', 'Foam'],
        'Home Decor': ['Recycled Cardboard', 'Paper', 'Plastic']
    }

def select_best_material(category,strength_score,biodegradability_score,recyclability_percent):
    """Select best material based on category and properties"""
    if category not in materials_db:
        category = 'electronics'
    
    materials = materials_db[category]
    
    # Score materials based on biodegradability and recyclability
    bio_weight = biodegradability_score/ 100 if biodegradability_score else 0.5
    recycle_weight = recyclability_percent / 100 if recyclability_percent else 0.5
    
    # Prefer high biodegradability and recyclability
    if bio_weight > 0.7 and recycle_weight > 0.7:
        return materials[0]  # Best option
    elif bio_weight > 0.5 or recycle_weight > 0.5:
        return materials[1] if len(materials) > 1 else materials[0]
    else:
        return materials[-1] if len(materials) > 1 else materials[0]

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    input_df = pd.DataFrame([data])
    predicted_cost = cost_model.predict(input_df)[0]
    predicted_co2 = co2_model.predict(input_df)[0]
    return jsonify({
        'predicted_cost': float(predicted_cost),
        'predicted_co2': float(predicted_co2)
    })

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        category = data.get('category', 'Electronics')
        strength = float(data.get('strength', 5))
        weight = float(data.get('weight', 1))
        bio = float(data.get('bio', 50))
        recycle = float(data.get('recycle', 50))
        
        # Try to get materials from database, fallback to hardcoded
        materials_list = None
        try:
            all_materials = query_materials()
            # Try to match category to a material_type
            for material_type in all_materials.keys():
                if category.lower() in material_type.lower() or material_type.lower() in category.lower():
                    materials_list = all_materials[material_type]
                    break
        except Exception as e:
            print(f"Could not query materials for category {category}: {e}")
        
        # If no materials found, use default recommendations
        if not materials_list or not materials_list:
            if category in materials_db:
                materials_list = materials_db[category]
            else:
                # Use Fiber-based as fallback
                materials_list = materials_db.get('electronics', ['Recycled Cardboard'])
        
        # Select best material based on scores
        if bio > 0.7 and recycle > 0.7:
            material = materials_list[0] if materials_list else 'Recycled Cardboard'
        elif bio > 0.5 or recycle > 0.5:
            material = materials_list[min(1, len(materials_list)-1)] if len(materials_list) > 1 else (materials_list[0] if materials_list else 'Recycled Cardboard')
        else:
            material = materials_list[-1] if len(materials_list) > 1 else (materials_list[0] if materials_list else 'Recycled Cardboard')
        
        # Create input dataframe with correct feature names used during training
        input_df = pd.DataFrame([{
            'strength_score': strength,
            'weight_capacity_score': weight * 10,
            'biodegradability_score': bio,
            'recyclability_percent': recycle,
            'cost_efficiency_index': (strength + bio + recycle) / 3
        }])
        
        predicted_cost = cost_model.predict(input_df)[0]
        predicted_co2 = co2_model.predict(input_df)[0]
        
        # Calculate cost based on weight
        base_cost = weight * 12
        total_cost = int(base_cost + predicted_cost)
        
        return jsonify({
            'material': material,
            'cost': int(total_cost),
            'co2': float(round(float(predicted_co2), 2)),
            'strength': float(strength),
            'category': category
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'error': str(e),
            'material': 'Recycled Cardboard',
            'cost': 150,
            'co2': 2.5
        }), 400

@app.route('/materials', methods=['GET'])
def get_materials():
    """Get all materials from database grouped by category"""
    try:
        materials = query_materials()
        if not materials:
            return jsonify({'error': 'No materials found'}), 404
        return jsonify(materials)
    except Exception as e:
        print(f"Error fetching materials: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/products', methods=['GET'])
def get_products():
    """Get all products from database"""
    try:
        products = query_products()
        if not products:
            return jsonify({'error': 'No products found'}), 404
        return jsonify(products)
    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/materials/<category>', methods=['GET'])
def get_materials_by_category(category):
    """Get materials for a specific material type"""
    try:
        materials = query_materials()
        # Case-insensitive category matching
        matching_category = None
        for cat in materials.keys():
            if cat.lower() == category.lower():
                matching_category = cat
                break
        
        if not matching_category:
            available = list(materials.keys())[:5]
            return jsonify({
                'error': f'Material type "{category}" not found',
                'available_types': available
            }), 404
        return jsonify({'type': matching_category, 'materials': materials[matching_category]})
    except Exception as e:
        print(f"Error fetching materials: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'ecopack-backend', 'version': '1.0'})

if __name__ == '__main__':
    app.run(debug=True)