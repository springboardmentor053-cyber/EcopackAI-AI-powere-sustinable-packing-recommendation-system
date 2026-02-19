from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import joblib
import pandas as pd
import sys
import os
import tempfile
import importlib.util
from io import BytesIO

# ── Paths ──────────────────────────────────────────────────────────────────────
# Backend/ is the working directory (rootDir in render.yaml)
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))   # .../Backend
REPO_ROOT    = os.path.abspath(os.path.join(BASE_DIR, "..")) # .../EcopackAI

sys.path.insert(0, BASE_DIR)

from db_config import get_db_connection, query_materials, query_products

# ── Frontend: one level up from Backend/ ──────────────────────────────────────
FRONTEND_DIR = os.path.join(REPO_ROOT, "Frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# ── Serve frontend at root ─────────────────────────────────────────────────────
@app.route("/", defaults={"path": ""})
@app.route("/ui/<path:path>")
def serve_frontend(path=""):
    target = os.path.join(FRONTEND_DIR, path) if path else None
    if path and target and os.path.exists(target):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

# ── Models ─────────────────────────────────────────────────────────────────────
MODELS_DIR      = os.path.join(BASE_DIR, "Models")
cost_model_path = os.path.join(MODELS_DIR, "cost_model.pkl")
co2_model_path  = os.path.join(MODELS_DIR, "co2_model.pkl")

if not os.path.exists(cost_model_path):
    raise FileNotFoundError(f"Cost model not found at {cost_model_path}")
if not os.path.exists(co2_model_path):
    raise FileNotFoundError(f"CO2 model not found at {co2_model_path}")

cost_model = joblib.load(cost_model_path)
co2_model  = joblib.load(co2_model_path)

# ── Dashboard loader ───────────────────────────────────────────────────────────
def _find_dashboard_path():
    candidates = [
        os.path.join(BASE_DIR, "dashboard.py"),
        os.path.join(BASE_DIR, "Dashboard", "dashboard.py"),
        os.path.join(REPO_ROOT, "dashboard.py"),
        os.path.join(REPO_ROOT, "Dashboard", "dashboard.py"),
    ]
    for path in candidates:
        normalized = os.path.normpath(path)
        if os.path.exists(normalized):
            print(f"[OK] Found dashboard.py at: {normalized}")
            return normalized
    raise FileNotFoundError("dashboard.py not found. Place it in Backend/ folder.")

DASHBOARD_PATH = _find_dashboard_path()

def load_dashboard():
    spec   = importlib.util.spec_from_file_location("dashboard", DASHBOARD_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.EcopackDashboard()

# ── Materials ──────────────────────────────────────────────────────────────────
def load_materials_from_db():
    try:
        materials_dict = query_materials()
        if materials_dict:
            print(f"[OK] Loaded {sum(len(v) for v in materials_dict.values())} materials from DB")
            return materials_dict
    except Exception as e:
        print(f"[WARNING] DB load failed: {e}")
    return {
        'electronics':               ['Recycled Cardboard', 'Foam Padding', 'Plastic Film'],
        'food':                      ['Biodegradable Plastic', 'Paper', 'Glass'],
        'cosmetics':                 ['Glass', 'Recyclable Plastic', 'Cardboard'],
        'Pharmaceuticals':           ['Blister Packs', 'Glass Bottles', 'Cardboard'],
        'Beverages':                 ['Aluminum', 'Glass', 'Paper'],
        'Textile/Apparel':           ['Recycled Cardboard', 'Paper', 'Biodegradable Plastic'],
        'Personal Care/Home':        ['Recyclable Plastic', 'Glass', 'Cardboard'],
        'Household Appliances':      ['Recycled Cardboard', 'Foam', 'Plastic'],
        'Furniture':                 ['Recycled Cardboard', 'Paper', 'Foam'],
        'Toys':                      ['Recyclable Plastic', 'Cardboard', 'Paper'],
        'Baby Care':                 ['Biodegradable Plastic', 'Cardboard', 'Paper'],
        'Industrial/Automotive':     ['Metal', 'Recycled Cardboard', 'Plastic'],
        'Healthcare/Medical Devices':['Sterilizable Plastic', 'Cardboard', 'Paper'],
        'Stationary':                ['Recycled Cardboard', 'Paper', 'Plastic'],
        'Sports & Outdoor':          ['Recycled Cardboard', 'Plastic', 'Foam'],
        'Home Decor':                ['Recycled Cardboard', 'Paper', 'Plastic'],
    }

materials_db = load_materials_from_db()

PRODUCT_TO_MATERIAL_CATEGORY = {
    'electronics':'Bio-based polysaccharide','food':'Agro-waste composite',
    'cosmetics':'Natural fiber','pharmaceuticals':'Agro-waste fiber',
    'beverages':'Lignocellulosic','textile/apparel':'Bio-based composite',
    'personal care/home':'Agro-waste particle','household appliances':'Bio-based starch',
    'furniture':'Bio-based polysaccharide','toys':'Agro-waste composite',
    'baby care':'Natural fiber','industrial/automotive':'Lignocellulosic',
    'healthcare/medical devices':'Agro-waste fiber','stationary':'Bio-based composite',
    'sports & outdoor':'Natural fiber','home decor':'Agro-waste composite',
}

def _resolve_material_category(category):
    db_category = PRODUCT_TO_MATERIAL_CATEGORY.get(category.lower(), category)
    if db_category not in materials_db:
        for key in materials_db:
            if key.lower() == db_category.lower():
                return key
        return list(materials_db.keys())[0] if materials_db else 'electronics'
    return db_category

def _build_input_df(strength, weight, bio, recycle):
    return pd.DataFrame([{
        'strength_score': strength, 'weight_capacity_score': weight * 10,
        'biodegradability_score': bio, 'recyclability_percent': recycle,
        'cost_efficiency_index': (strength + bio + recycle) / 3,
    }])

def _rank_materials(materials_list, predicted_cost, predicted_co2, bio, recycle, weight):
    import hashlib
    rankings = []
    for material in materials_list:
        eco_score      = bio * 0.5 + recycle * 0.5
        material_hash  = int(hashlib.md5(material.encode()).hexdigest(), 16) % 100
        cost_variation = 0.7 + (material_hash % 80) / 100.0
        co2_variation  = 0.8 + (material_hash % 40) / 100.0
        rankings.append({
            'material': material,
            'cost':     int(weight * 12 + predicted_cost * 10 * cost_variation),
            'co2':      round(predicted_co2 * co2_variation, 2),
            'eco_score':round(eco_score, 1),
        })
    rankings.sort(key=lambda x: (-x['eco_score'], x['cost']))
    return rankings

# ── API routes ─────────────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({'status': 'ok', 'service': 'ecopack-backend', 'version': '1.0'})

@app.route('/api/predict', methods=['POST'])
def predict():
    input_df = pd.DataFrame([request.json])
    return jsonify({'predicted_cost': float(cost_model.predict(input_df)[0]),
                    'predicted_co2':  float(co2_model.predict(input_df)[0])})

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data     = request.json
        category = data.get('category', 'electronics')
        strength = float(data.get('strength', 5))
        weight   = float(data.get('weight', 1))
        bio      = float(data.get('bio', 50))
        recycle  = float(data.get('recycle', 50))
        db_category    = _resolve_material_category(category)
        materials_list = materials_db.get(db_category, [])
        input_df       = _build_input_df(strength, weight, bio, recycle)
        predicted_cost = float(cost_model.predict(input_df)[0])
        predicted_co2  = float(co2_model.predict(input_df)[0])
        rankings       = _rank_materials(materials_list, predicted_cost, predicted_co2, bio, recycle, weight)
        if rankings:
            top = rankings[0]
            material, total_cost, co2_emission = top['material'], top['cost'], top['co2']
        else:
            material, total_cost, co2_emission = 'Recycled Cardboard', int(weight*12+predicted_cost), round(predicted_co2,2)
        return jsonify({'material': material, 'cost': int(total_cost),
                        'co2': float(round(co2_emission,2)), 'strength': float(strength), 'category': category})
    except Exception as e:
        return jsonify({'error': str(e), 'material': 'Recycled Cardboard', 'cost': 150, 'co2': 2.5}), 400

@app.route('/api/materials', methods=['GET'])
def get_materials():
    try:
        materials = query_materials()
        return jsonify(materials) if materials else (jsonify({'error': 'No materials found'}), 404)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        products = query_products()
        return jsonify(products) if products else (jsonify({'error': 'No products found'}), 404)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/environment-score', methods=['POST'])
def environment_score():
    try:
        data = request.json or {}
        if 'predicted_co2' in data and 'baseline_co2' in data:
            predicted_co2 = float(data['predicted_co2'])
            baseline_co2  = float(data['baseline_co2'])
        else:
            input_df      = _build_input_df(float(data.get('strength',5)), float(data.get('weight',1.0)),
                                            float(data.get('bio',50)), float(data.get('recycle',50)))
            predicted_co2 = float(co2_model.predict(input_df)[0])
            baseline_co2  = float(data.get('baseline_co2', predicted_co2 * 1.1))
        reduction_pct = ((baseline_co2 - predicted_co2) / baseline_co2 * 100.0) if baseline_co2 else 0.0
        return jsonify({'predicted_co2': float(round(predicted_co2,4)),
                        'baseline_co2': float(round(baseline_co2,4)),
                        'reduction_percent': float(round(reduction_pct,2))})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/ranked-materials/<path:category>', methods=['POST', 'OPTIONS'])
def ranked_materials(category):
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        data     = request.json or {}
        strength = float(data.get('strength', 5))
        weight   = float(data.get('weight', 1.0))
        bio      = float(data.get('bio', 50))
        recycle  = float(data.get('recycle', 50))
        db_category = _resolve_material_category(category)
        if db_category not in materials_db:
            return jsonify({'error': f'Category "{category}" not found', 'materials': []}), 404
        input_df       = _build_input_df(strength, weight, bio, recycle)
        predicted_cost = float(cost_model.predict(input_df)[0])
        predicted_co2  = float(co2_model.predict(input_df)[0])
        rankings       = _rank_materials(materials_db[db_category], predicted_cost, predicted_co2, bio, recycle, weight)
        for idx, r in enumerate(rankings):
            r['rank'] = idx + 1
        return jsonify({'category': category, 'materials': rankings})
    except Exception as e:
        return jsonify({'error': str(e), 'materials': []}), 400

@app.route('/api/dashboard/metrics', methods=['GET'])
def get_dashboard_metrics():
    try:
        return jsonify(load_dashboard().get_all_metrics_json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/export/excel', methods=['GET', 'POST'])
def export_excel():
    try:
        dashboard = load_dashboard()
        temp_file = os.path.join(tempfile.gettempdir(), 'ecopack_excel_export.xlsx')
        dashboard.export_to_excel(temp_file)
        if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
            return jsonify({'error': 'Excel file creation failed'}), 500
        with open(temp_file, 'rb') as f:
            output = BytesIO(f.read())
        output.seek(0)
        try: os.remove(temp_file)
        except: pass
        return send_file(output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True, download_name='Sustainability_Report.xlsx')
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': f'Excel export failed: {str(e)}'}), 500

@app.route('/api/dashboard/export/pdf', methods=['GET', 'POST'])
def export_pdf():
    try:
        dashboard = load_dashboard()
        temp_file = os.path.join(tempfile.gettempdir(), 'ecopack_pdf_export.pdf')
        dashboard.export_to_pdf(temp_file)
        if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
            return jsonify({'error': 'PDF file creation failed'}), 500
        with open(temp_file, 'rb') as f:
            output = BytesIO(f.read())
        output.seek(0)
        try: os.remove(temp_file)
        except: pass
        return send_file(output, mimetype='application/pdf',
            as_attachment=True, download_name='Sustainability_Report.pdf')
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': f'PDF export failed: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)