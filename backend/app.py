import sys
import os
import time
import logging
from datetime import datetime
from functools import wraps
from collections import defaultdict

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from ml.recommendation_engine import EcoPackRecommender
import traceback

# ============================================================
# Logging Configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('EcoPackAI')

# ============================================================
# Initialize Flask App
# ============================================================

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'templates'),
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'static')
)
CORS(app)

# ============================================================
# Configuration
# ============================================================

API_KEY = os.getenv('ECOPACKAI_API_KEY', 'ecopackai_dev_key_2025')
RATE_LIMIT_MAX = 60          # Max requests per window
RATE_LIMIT_WINDOW = 60       # Window in seconds (1 minute)
API_KEY_REQUIRED = False      # Set True in production

# ============================================================
# Rate Limiter (In-Memory Sliding Window)
# ============================================================

request_counts = defaultdict(list)

def rate_limit_check(client_ip):
    """
    Simple sliding window rate limiter.
    Returns True if request is allowed, False if rate limit exceeded.
    """
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW

    # Remove old timestamps outside the window
    request_counts[client_ip] = [
        t for t in request_counts[client_ip] if t > window_start
    ]

    if len(request_counts[client_ip]) >= RATE_LIMIT_MAX:
        return False

    request_counts[client_ip].append(now)
    return True

# ============================================================
# API Key Authentication Decorator
# ============================================================

def require_api_key(f):
    """Decorator to check API key in request headers"""
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

# ============================================================
# Request Tracking (Before/After each request)
# ============================================================

@app.before_request
def before_request_handler():
    """Log incoming request and check rate limit"""
    request.start_time = time.time()

    # Skip rate limit for static files and frontend
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
    """Log response time and add custom headers"""
    if hasattr(request, 'start_time'):
        duration = round((time.time() - request.start_time) * 1000, 1)
        logger.info(f"Response: {response.status_code} in {duration}ms")

        # Add custom headers
        response.headers['X-Response-Time'] = f"{duration}ms"
        response.headers['X-Powered-By'] = 'EcoPackAI'
    return response

# ============================================================
# Initialize ML Engine
# ============================================================

logger.info("Loading ML models and recommendation engine...")
recommender = EcoPackRecommender()
logger.info("Recommendation engine ready.")

# ============================================================
# Input Validation Helpers
# ============================================================

def validate_recommend_input(data):
    """Validate recommendation request data. Returns (is_valid, errors_list)."""
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

    # Validate fragility_override if provided
    if 'fragility_override' in data and data['fragility_override']:
        valid_values = ['auto', 'low', 'medium', 'high']
        if data['fragility_override'] not in valid_values:
            errors.append(f"fragility_override must be one of: {valid_values}")

    # Validate budget_limit if provided
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
    """Validate comparison request data. Returns (is_valid, errors_list)."""
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

# ============================================================
# ROUTE 0: Serve Frontend
# ============================================================

@app.route('/')
def home():
    """Serve the main frontend page"""
    return render_template('index.html')

# ============================================================
# ROUTE 1: Health Check
# ============================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if the API is running and models are loaded"""
    return jsonify({
        'status': 'healthy',
        'message': 'EcoPackAI API is running',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': {
            'suitability': recommender.rf_suitability is not None,
            'co2': recommender.xgb_co2 is not None,
            'cost': recommender.rf_cost is not None
        }
    }), 200

# ============================================================
# ROUTE 2: Get All Product Categories
# ============================================================

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Return all available product categories"""
    try:
        categories = recommender.get_categories()
        return jsonify({
            'status': 'success',
            'count': len(categories),
            'categories': categories
        }), 200
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch categories'
        }), 500

# ============================================================
# ROUTE 3: Get All Materials
# ============================================================

@app.route('/api/materials', methods=['GET'])
def get_materials():
    """Return all available packaging materials"""
    try:
        materials = recommender.get_materials()
        return jsonify({
            'status': 'success',
            'count': len(materials),
            'materials': materials
        }), 200
    except Exception as e:
        logger.error(f"Error fetching materials: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch materials'
        }), 500

# ============================================================
# ROUTE 4: Get Material Details
# ============================================================

@app.route('/api/materials/<material_name>', methods=['GET'])
@require_api_key
def get_material_details(material_name):
    """Return detailed info about a specific material"""
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
        logger.error(f"Error fetching material details: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

# ============================================================
# ROUTE 5: Get AI Recommendations (CORE ENDPOINT)
# ============================================================

@app.route('/api/recommend', methods=['POST'])
@require_api_key
def get_recommendations():
    """
    Get AI-powered packaging material recommendations.

    Expected JSON body:
    {
        "category": "Electronics",
        "weight": 3.5,
        "top_n": 5  (optional, default 5)
    }
    """
    try:
        data = request.get_json()

        # Validate input
        is_valid, errors = validate_recommend_input(data)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'errors': errors
            }), 400
        
        weight = float(data['weight'])
        top_n = int(data.get('top_n', 5))

        # Extract optional parameters
        fragility_override = data.get('fragility_override', 'auto')
        budget_limit = data.get('budget_limit', None)
        if budget_limit is not None:
            budget_limit = float(budget_limit)

        logger.info(f"Recommendation: category={data['category']}, weight={weight}, "
                     f"top_n={top_n}, fragility={fragility_override}, budget={budget_limit}")

        # Get recommendations from ML model
        results_df = recommender.get_recommendations(
            category_name=data['category'],
            product_weight_kg=weight,
            top_n=top_n,
            fragility_override=fragility_override,
            budget_limit=budget_limit
        )

        recommendations = results_df.to_dict(orient='records')

        logger.info(f"Returned {len(recommendations)} results. Top: {recommendations[0]['material_name']}")

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

# ============================================================
# ROUTE 6: Compare Materials
# ============================================================

@app.route('/api/compare', methods=['POST'])
@require_api_key
def compare_materials():
    """
    Compare current material with AI recommendation.

    Expected JSON body:
    {
        "category": "Electronics",
        "weight": 3.5,
        "current_material": "EPS (Expanded Polystyrene)"
    }
    """
    try:
        data = request.get_json()

        # Validate input
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

# ============================================================
# ROUTE 7: Environmental Score
# ============================================================

@app.route('/api/eco-score', methods=['POST'])
@require_api_key
def get_eco_score():
    """
    Get environmental score for a specific material.

    Expected JSON body:
    {
        "material_name": "Recycled PET (rPET)"
    }
    """
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

# ============================================================
# Error Handlers (Global)
# ============================================================

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

# ============================================================
# Run Server
# ============================================================

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  EcoPackAI API Server v1.0.0")
    print("=" * 50)
    print(f"\n  API Key Auth: {'ENABLED' if API_KEY_REQUIRED else 'DISABLED (dev mode)'}")
    print(f"  Rate Limit:   {RATE_LIMIT_MAX} requests / {RATE_LIMIT_WINDOW}s")
    print("\n  Endpoints:")
    print("  GET  /                        - Web Interface")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/categories          - List categories")
    print("  GET  /api/materials           - List materials")
    print("  GET  /api/materials/<name>    - Material details")
    print("  POST /api/recommend           - Get recommendations")
    print("  POST /api/compare             - Compare materials")
    print("  POST /api/eco-score           - Environmental score")
    print("\n" + "=" * 50)

    app.run(debug=True, host='0.0.0.0', port=5000)
