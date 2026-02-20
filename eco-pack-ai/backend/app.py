import sys
import os
import time
import logging
import streamlit as st
from datetime import datetime
from functools import wraps
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from ml.recommendation_engine import EcoPackRecommender
import traceback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('EcoPackAI')

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'templates'),
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'static')
)
CORS(app)

API_KEY = os.getenv('ECOPACKAI_API_KEY', 'ecopackai_dev_key_2025')
RATE_LIMIT_MAX = 60
RATE_LIMIT_WINDOW = 60
API_KEY_REQUIRED = False

request_counts = defaultdict(list)

def rate_limit_check(client_ip):
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW

    request_counts[client_ip] = [
        t for t in request_counts[client_ip] if t > window_start
    ]

    if len(request_counts[client_ip]) >= RATE_LIMIT_MAX:
        return False

    request_counts[client_ip].append(now)
    return True

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not API_KEY_REQUIRED:
            return f(*args, **kwargs)

        provided_key = request.headers.get('x-api-key', '')
        if provided_key != API_KEY:
            logger.warning(f"Unauthorized access attempt from {request.remote_addr}")
            return jsonify({
                'status': 'error',
                'message': 'Unauthorized. Provide valid x-api-key header.'
            }), 401
        return f(*args, **kwargs)
    return decorated

@app.before_request
def before_request_handler():
    request.start_time = time.time()

    if request.path.startswith('/static') or request.path == '/':
        return

    client_ip = request.remote_addr
    if not rate_limit_check(client_ip):
        logger.warning(f"Rate limit exceeded for {client_ip}")
        return jsonify({
            'status': 'error',
            'message': 'Rate limit exceeded. Max 60 requests per minute.',
            'retry_after_seconds': RATE_LIMIT_WINDOW
        }), 429

    logger.info(f"Request: {request.method} {request.path} from {client_ip}")

@app.after_request
def after_request_handler(response):
    if hasattr(request, 'start_time'):
        duration = round((time.time() - request.start_time) * 1000, 1)
        logger.info(f"Response: {response.status_code} in {duration}ms")

        response.headers['X-Response-Time'] = f"{duration}ms"
        response.headers['X-Powered-By'] = 'EcoPackAI'
    return response

logger.info("Loading ML models and recommendation engine...")
recommender = EcoPackRecommender()
logger.info("Recommendation engine ready.")

def validate_recommend_input(data):
    errors = []

    if not data:
        return False, ['Request body must be JSON']

    if 'category' not in data or not data['category']:
        errors.append('Missing required field: category')

    if 'weight' not in data:
        errors.append('Missing required field: weight')
    else:
        try:
            weight = float(data['weight'])
            if weight <= 0:
                errors.append('weight must be a positive number')
            if weight > 500:
                errors.append('weight exceeds maximum limit (500 kg)')
        except (ValueError, TypeError):
            errors.append('weight must be a valid number')

    if 'top_n' in data:
        try:
            top_n = int(data['top_n'])
            if top_n < 1 or top_n > 25:
                errors.append('top_n must be between 1 and 25')
        except (ValueError, TypeError):
            errors.append('top_n must be a valid integer')

    if 'fragility_override' in data and data['fragility_override']:
        valid_values = ['auto', 'low', 'medium', 'high']
        if data['fragility_override'] not in valid_values:
            errors.append(f"fragility_override must be one of: {valid_values}")

    if 'budget_limit' in data and data['budget_limit'] is not None:
        try:
            budget = float(data['budget_limit'])
            if budget <= 0:
                errors.append('budget_limit must be a positive number')
        except (ValueError, TypeError):
            errors.append('budget_limit must be a valid number')

    if errors:
        return False, errors
    return True, []

def validate_compare_input(data):
    errors = []

    if not data:
        return False, ['Request body must be JSON']

    required = ['category', 'weight', 'current_material']
    for field in required:
        if field not in data or not data[field]:
            errors.append(f'Missing required field: {field}')

    if 'weight' in data:
        try:
            weight = float(data['weight'])
            if weight <= 0:
                errors.append('weight must be a positive number')
        except (ValueError, TypeError):
            errors.append('weight must be a valid number')

    if errors:
        return False, errors
    return True, []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'EcoPackAI API is running',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': {
            'suitability': recommender.rf_suitability is not None,
            'co2': recommender.xgb_co2 is not None,
            'eco_score': recommender.lr_eco_score is not None
        }
    }), 200

@app.route('/api/categories', methods=['GET'])
@require_api_key
def list_categories():
    try:
        categories = recommender.get_categories()
        return jsonify({
            'status': 'success',
            'count': len(categories),
            'categories': categories
        }), 200
    except Exception as e:
        logger.error(f"Categories error: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/materials', methods=['GET'])
@require_api_key
def list_materials():
    try:
        materials = recommender.get_materials()
        return jsonify({
            'status': 'success',
            'count': len(materials),
            'materials': materials
        }), 200
    except Exception as e:
        logger.error(f"Materials error: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/materials/<material_name>', methods=['GET'])
@require_api_key
def get_material_details_route(material_name):
    try:
        details = recommender.get_material_details(material_name)
        return jsonify({
            'status': 'success',
            'material': details
        }), 200
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Material details error: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/recommend', methods=['POST'])
@require_api_key
def get_recommendations():
    try:
        data = request.get_json()

        is_valid, errors = validate_recommend_input(data)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'errors': errors
            }), 400
        
        weight = float(data['weight'])
        top_n = int(data.get('top_n', 5))

        fragility_override = data.get('fragility_override', 'auto')
        budget_limit = data.get('budget_limit', None)
        if budget_limit is not None:
            budget_limit = float(budget_limit)

        logger.info(f"Recommendation: category={data['category']}, weight={weight}, "
                     f"top_n={top_n}, fragility={fragility_override}, budget={budget_limit}")

        results_df = recommender.get_recommendations(
            category_name=data['category'],
            product_weight_kg=weight,
            top_n=top_n,
            fragility_override=fragility_override,
            budget_limit=budget_limit
        )
        
        recommendations = results_df.to_dict(orient='records')

        logger.info(f"Returned {len(recommendations)} results. Top: {recommendations[0]['material_name']}")

        try:
            recommender.save_recommendation(
                category_name=data['category'],
                product_weight_kg=weight,
                fragility_level=fragility_override,
                budget_limit=budget_limit,
                current_material_name=data.get('current_material', None),
                recommendation=recommendations[0],
                comparison=None
            )
        except Exception as e:
            logger.warning(f"Failed to save recommendation to database: {e}")

        return jsonify({
            'status': 'success',
            'category': data['category'],
            'product_weight_kg': weight,
            'count': len(recommendations),
            'recommendations': recommendations
        }), 200

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Recommendation error: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/compare', methods=['POST'])
@require_api_key
def compare_materials():
    try:
        data = request.get_json()

        is_valid, errors = validate_compare_input(data)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'errors': errors
            }), 400

        weight = float(data['weight'])

        logger.info(f"Compare: {data['current_material']} vs best for {data['category']} ({weight}kg)")

        comparison = recommender.compare_with_current(
            category_name=data['category'],
            product_weight_kg=weight,
            current_material_name=data['current_material']
        )
        
        logger.info(f"Result: {comparison['co2_reduction_percent']}% CO2 reduction")

        try:
            recommender.update_recommendation_with_comparison(
                category_name=data['category'],
                product_weight_kg=weight,
                comparison=comparison
            )
        except Exception as e:
            logger.warning(f"Failed to update recommendation with comparison: {e}")

        return jsonify({
            'status': 'success',
            'comparison': comparison
        }), 200

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Comparison error: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/eco-score', methods=['POST'])
@require_api_key
def get_eco_score():
    try:
        data = request.get_json()

        if not data or 'material_name' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: material_name'
            }), 400

        details = recommender.get_material_details(data['material_name'])

        return jsonify({
            'status': 'success',
            'material_name': details['material_name'],
            'environmental_scores': {
                'eco_score': details['eco_score'],
                'co2_emission_kg': details['co2_emission_kg'],
                'co2_impact_index': details['co2_impact_index'],
                'biodegradability_score': details['biodegradability_score'],
                'recyclability_percent': details['recyclability_percent']
            }
        }), 200

    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Eco-score error: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'status': 'error',
        'message': 'HTTP method not allowed for this endpoint'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)