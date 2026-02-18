from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import joblib
import pandas as pd
import sys
import os
import tempfile
from io import BytesIO

# Add EcopackAI root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
from .db_config import get_db_connection, query_materials, query_products

# web server
app = Flask(__name__)
# Enable CORS for frontend requests (explicit resource/origin policy)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# loading ml models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Go one level up from Backend → project root
PROJECT_ROOT = os.path.dirname(BASE_DIR)

cost_model_path = os.path.join(PROJECT_ROOT, "Models", "cost_model.pkl")
co2_model_path = os.path.join(PROJECT_ROOT, "Models", "co2_model.pkl")

cost_model = joblib.load(cost_model_path)
co2_model = joblib.load(co2_model_path)

# Load materials from database with fallback to hardcoded
def load_materials_from_db():
    """Attempt to load all materials from database; fallback to hardcoded."""
    try:
        materials_dict = query_materials()
        if materials_dict:
            print(f"[OK] Loaded {sum(len(v) for v in materials_dict.values())} materials from database")
            return materials_dict
    except Exception as e:
        print(f"[WARNING] Failed to load materials from DB: {e}")
    
    # Fallback to hardcoded
    return {
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

materials_db = load_materials_from_db()

# Map product categories to DB material categories (preferring categories with 5+ materials)
PRODUCT_TO_MATERIAL_CATEGORY = {
    'electronics': 'Bio-based polysaccharide',      # 16 materials
    'food': 'Agro-waste composite',                  # 11 materials
    'cosmetics': 'Natural fiber',                    # 11 materials
    'pharmaceuticals': 'Agro-waste fiber',           # 9 materials
    'beverages': 'Lignocellulosic',                  # 8 materials
    'textile/apparel': 'Bio-based composite',        # 6 materials
    'personal care/home': 'Agro-waste particle',     # 5 materials
    'household appliances': 'Bio-based starch',      # 5 materials
    'furniture': 'Bio-based polysaccharide',         # 16 materials
    'toys': 'Agro-waste composite',                  # 11 materials
    'baby care': 'Natural fiber',                    # 11 materials
    'industrial/automotive': 'Lignocellulosic',      # 8 materials
    'healthcare/medical devices': 'Agro-waste fiber',# 9 materials
    'stationary': 'Bio-based composite',             # 6 materials
    'sports & outdoor': 'Natural fiber',             # 11 materials
    'home decor': 'Agro-waste composite'             # 11 materials
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
    
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "EcoPack AI Backend is running 🚀",
        "available_endpoints": [
            "/predict",
            "/recommend",
            "/materials",
            "/products",
            "/dashboard/metrics",
            "/health"
        ]
    })

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
        category = data.get('category', 'electronics')
        strength = float(data.get('strength', 5))
        weight = float(data.get('weight', 1))
        bio = float(data.get('bio', 50))
        recycle = float(data.get('recycle', 50))
        
        # Map product category to material category
        db_category = category
        if category.lower() in PRODUCT_TO_MATERIAL_CATEGORY:
            db_category = PRODUCT_TO_MATERIAL_CATEGORY[category.lower()]
        
        # Get materials for this category
        if db_category not in materials_db:
            # Try case-insensitive match
            for key in materials_db.keys():
                if key.lower() == db_category.lower():
                    db_category = key
                    break
        
        if db_category not in materials_db:
            # Fallback to first available category
            db_category = list(materials_db.keys())[0] if materials_db else 'electronics'
        
        materials_list = materials_db.get(db_category, [])
        
        # Create input dataframe for predictions
        input_df = pd.DataFrame([{
            'strength_score': strength,
            'weight_capacity_score': weight * 10,
            'biodegradability_score': bio,
            'recyclability_percent': recycle,
            'cost_efficiency_index': (strength + bio + recycle) / 3
        }])
        
        predicted_cost = float(cost_model.predict(input_df)[0])
        predicted_co2 = float(co2_model.predict(input_df)[0])
        
        # Generate rankings for all materials and pick the best one
        rankings = []
        for material in materials_list:
            eco_score = (bio * 0.5 + recycle * 0.5)
            
            # Add variation per material for cost differentiation
            import hashlib
            material_hash = int(hashlib.md5(material.encode()).hexdigest(), 16) % 100
            cost_variation = 0.7 + (material_hash % 80) / 100.0  # 0.7 to 1.5 variation
            co2_variation = 0.8 + (material_hash % 40) / 100.0   # 0.8 to 1.2 variation
            
            material_cost = int(weight * 12 + predicted_cost * 10 * cost_variation)
            material_co2 = round(predicted_co2 * co2_variation, 2)
            
            rankings.append({
                'material': material,
                'cost': material_cost,
                'co2': material_co2,
                'eco_score': round(eco_score, 1)
            })
        
        # Sort by eco_score (desc) then by cost (asc) and pick top material
        rankings.sort(key=lambda x: (-x['eco_score'], x['cost']))
        
        if rankings:
            top_material = rankings[0]
            material = top_material['material']
            total_cost = top_material['cost']
            co2_emission = top_material['co2']
        else:
            # Fallback
            material = 'Recycled Cardboard'
            total_cost = int(weight * 12 + predicted_cost)
            co2_emission = round(predicted_co2, 2)
        
        return jsonify({
            'material': material,
            'cost': int(total_cost),
            'co2': float(round(co2_emission, 2)),
            'strength': float(strength),
            'category': category
        })
    
    except Exception as e:
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

@app.route('/materials/<path:category>', methods=['GET'])
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


@app.route('/product-input', methods=['POST'])
def product_input():
    """Accepts basic product info and returns a recommended packaging strength score"""
    try:
        data = request.json or {}
        product_category = data.get('product_category') or data.get('category') or 'general'
        fragility_level = float(data.get('fragility_level', 3))
        weight = float(data.get('weight', 1.0))

        # Simple heuristic: fragility contributes strongly, weight less so
        recommended_strength = fragility_level * 1.5 + weight * 0.5
        # Clamp to 1-10
        recommended_strength = max(1.0, min(10.0, recommended_strength))

        return jsonify({
            'product_category': product_category,
            'recommended_strength': float(round(recommended_strength, 2))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/environment-score', methods=['POST'])
def environment_score():
    """Return predicted CO2 and percent reduction versus a baseline.
    Accepts either explicit `predicted_co2` and `baseline_co2`, or feature inputs
    (`strength`, `weight`, `bio`, `recycle`) to run the `co2_model`.
    """
    try:
        data = request.json or {}

        if 'predicted_co2' in data and 'baseline_co2' in data:
            predicted_co2 = float(data.get('predicted_co2', 0))
            baseline_co2 = float(data.get('baseline_co2', predicted_co2))
        else:
            # Build feature dataframe expected by the model
            strength = float(data.get('strength', 5))
            weight = float(data.get('weight', 1.0))
            bio = float(data.get('bio', 50))
            recycle = float(data.get('recycle', 50))

            input_df = pd.DataFrame([{
                'strength_score': strength,
                'weight_capacity_score': weight * 10,
                'biodegradability_score': bio,
                'recyclability_percent': recycle,
                'cost_efficiency_index': (strength + bio + recycle) / 3
            }])

            predicted_co2 = float(co2_model.predict(input_df)[0])
            # If baseline not supplied, assume baseline is 10% worse than predicted
            baseline_co2 = float(data.get('baseline_co2', predicted_co2 * 1.1))

        reduction_pct = 0.0
        if baseline_co2:
            reduction_pct = (baseline_co2 - predicted_co2) / baseline_co2 * 100.0

        return jsonify({
            'predicted_co2': float(round(predicted_co2, 4)),
            'baseline_co2': float(round(baseline_co2, 4)),
            'reduction_percent': float(round(reduction_pct, 2))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/ranked-materials/<path:category>', methods=['POST', 'OPTIONS'])
def ranked_materials(category):
    """Return ranked materials for a given category based on eco-friendliness and cost.
    Request body: {"strength": 5, "weight": 1, "bio": 50, "recycle": 50}
    Maps product categories (food, electronics, etc.) to DB material categories.
    Returns: [{"rank": 1, "material": "name", "cost": int, "co2": float, "eco_score": float}, ...]
    """
    # Preflight handling: return 200 for OPTIONS
    if request.method == 'OPTIONS':
        return ('', 200)

    try:
        data = request.json or {}
        strength = float(data.get('strength', 5))
        weight = float(data.get('weight', 1.0))
        bio = float(data.get('bio', 50))
        recycle = float(data.get('recycle', 50))

        # Map product category to material category
        db_category = category
        if category.lower() in PRODUCT_TO_MATERIAL_CATEGORY:
            db_category = PRODUCT_TO_MATERIAL_CATEGORY[category.lower()]
        
        # Get materials for this category
        if db_category not in materials_db:
            # Try case-insensitive match
            for key in materials_db.keys():
                if key.lower() == db_category.lower():
                    db_category = key
                    break
        
        if db_category not in materials_db:
            return jsonify({'error': f'Category "{category}" not found', 'materials': []}), 404

        materials_list = materials_db[db_category]

        # Build feature dataframe for predictions
        input_df = pd.DataFrame([{
            'strength_score': strength,
            'weight_capacity_score': weight * 10,
            'biodegradability_score': bio,
            'recyclability_percent': recycle,
            'cost_efficiency_index': (strength + bio + recycle) / 3
        }])

        predicted_cost = float(cost_model.predict(input_df)[0])
        predicted_co2 = float(co2_model.predict(input_df)[0])

        # Generate rankings for all materials with individual predictions
        rankings = []
        for material in materials_list:
            # Eco-friendliness score: based on bio and recycle inputs
            eco_score = (bio * 0.5 + recycle * 0.5)
            
            # Add variation per material for differentiation (material-specific traits)
            import hashlib
            material_hash = int(hashlib.md5(material.encode()).hexdigest(), 16) % 100
            cost_variation = 0.7 + (material_hash % 80) / 100.0  # 0.7 to 1.5 variation for visible differentiation
            co2_variation = 0.8 + (material_hash % 40) / 100.0   # 0.8 to 1.2 variation
            
            material_cost = int(weight * 12 + predicted_cost * 10 * cost_variation)
            material_co2 = round(predicted_co2 * co2_variation, 2)
            
            rankings.append({
                'material': material,
                'cost': material_cost,
                'co2': material_co2,
                'eco_score': round(eco_score, 1)
            })
        
        # Sort by eco_score (desc) then by cost (asc)
        rankings.sort(key=lambda x: (-x['eco_score'], x['cost']))
        
        # Add rank numbers after sorting
        for idx, ranking in enumerate(rankings):
            ranking['rank'] = idx + 1

        return jsonify({'category': category, 'materials': rankings})
    except Exception as e:
        return jsonify({'error': str(e), 'materials': []}), 400

@app.route('/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    """Get all dashboard metrics for BI dashboard"""
    try:
        from dashboard import EcopackDashboard
        dashboard = EcopackDashboard()
        metrics = dashboard.get_all_metrics_json()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard/co2', methods=['GET'])
def get_co2_metrics():
    """Get CO2 reduction metrics"""
    try:
        from dashboard import EcopackDashboard
        dashboard = EcopackDashboard()
        return jsonify(dashboard.get_co2_metrics())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard/cost', methods=['GET'])
def get_cost_metrics():
    """Get cost savings metrics"""
    try:
        from dashboard import EcopackDashboard
        dashboard = EcopackDashboard()
        return jsonify(dashboard.get_cost_metrics())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard/materials', methods=['GET'])
def get_material_trends():
    """Get material usage trends"""
    try:
        from dashboard import EcopackDashboard
        dashboard = EcopackDashboard()
        return jsonify(dashboard.get_material_trends())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard/sustainability-score', methods=['GET'])
def get_sustainability_score():
    """Get overall sustainability score"""
    try:
        from dashboard import EcopackDashboard
        dashboard = EcopackDashboard()
        score = dashboard.get_sustainability_score()
        return jsonify({'sustainability_score': score})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/dashboard/export/excel', methods=['GET', 'POST'])
def export_excel():
    """Export sustainability report as Excel"""
    try:
        print("\n" + "="*60)
        print("EXCEL EXPORT STARTED")
        print("="*60)
        
        from dashboard import EcopackDashboard
        
        dashboard = EcopackDashboard()
        
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, 'ecopack_excel_export.xlsx')
        
        print(f"Temp directory: {temp_dir}")
        print(f"Output file: {temp_file}")
        
        # Call dashboard export function
        print("Calling dashboard.export_to_excel()...")
        result_msg = dashboard.export_to_excel(temp_file)
        print(f"Export result: {result_msg}")
        
        # Verify file was created
        if not os.path.exists(temp_file):
            print(f"✗ ERROR: File not created at {temp_file}")
            return jsonify({'error': 'Excel file creation failed'}), 500
        
        # Get file size
        file_size = os.path.getsize(temp_file)
        print(f"✓ File created successfully: {file_size} bytes")
        
        # Read file content
        print("Reading file content...")
        with open(temp_file, 'rb') as f:
            file_content = f.read()
        print(f"✓ File read successfully: {len(file_content)} bytes")
        
        # Create BytesIO object
        output = BytesIO(file_content)
        output.seek(0)
        
        # Delete temp file
        try:
            os.remove(temp_file)
            print("✓ Temp file cleaned up")
        except Exception as e:
            print(f"⚠ Warning: Could not delete temp file: {e}")
        
        # Send file
        print("Sending file to client...")
        print("="*60 + "\n")
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='Sustainability_Report.xlsx'
        )
    
    except Exception as e:
        print(f"\n✗ EXCEL EXPORT FAILED")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        
        return jsonify({'error': f'Excel export failed: {str(e)}'}), 500


@app.route('/dashboard/export/pdf', methods=['GET', 'POST'])
def export_pdf():
    """Export sustainability report as PDF"""
    try:
        print("\n" + "="*60)
        print("PDF EXPORT STARTED")
        print("="*60)
        
        from dashboard import EcopackDashboard
        
        dashboard = EcopackDashboard()
        
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, 'ecopack_pdf_export.pdf')
        
        print(f"Temp directory: {temp_dir}")
        print(f"Output file: {temp_file}")
        
        # Call dashboard export function
        print("Calling dashboard.export_to_pdf()...")
        result_msg = dashboard.export_to_pdf(temp_file)
        print(f"Export result: {result_msg}")
        
        # Verify file was created
        if not os.path.exists(temp_file):
            print(f"✗ ERROR: File not created at {temp_file}")
            return jsonify({'error': 'PDF file creation failed'}), 500
        
        # Get file size
        file_size = os.path.getsize(temp_file)
        print(f"✓ File created successfully: {file_size} bytes")
        
        # Read file content
        print("Reading file content...")
        with open(temp_file, 'rb') as f:
            file_content = f.read()
        print(f"✓ File read successfully: {len(file_content)} bytes")
        
        # Create BytesIO object
        output = BytesIO(file_content)
        output.seek(0)
        
        # Delete temp file
        try:
            os.remove(temp_file)
            print("✓ Temp file cleaned up")
        except Exception as e:
            print(f"⚠ Warning: Could not delete temp file: {e}")
        
        # Send file
        print("Sending file to client...")
        print("="*60 + "\n")
        
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='Sustainability_Report.pdf'
        )
    
    except Exception as e:
        print(f"\n✗ PDF EXPORT FAILED")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        
        return jsonify({'error': f'PDF export failed: {str(e)}'}), 500


@app.route('/dashboard/download/<path:filename>', methods=['GET'])
def download_dashboard_file(filename):
    """Serve exported dashboard files from the server output folder."""
    try:
        output_dir = 'c:/EcopackAI/Dashboard'
        # send file as attachment
        return send_from_directory(output_dir, filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'ecopack-backend', 'version': '1.0'})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)