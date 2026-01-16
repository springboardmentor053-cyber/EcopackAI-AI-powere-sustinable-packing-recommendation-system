
from flask import Blueprint, request, jsonify, render_template
from ..services.ml_service import ml_service
import logging

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "healthy", "service": "EcoPackAI Backend"}), 200

@api_bp.route('/recommend', methods=['POST'])
def recommend_materials():
    """
    Endpoint to get material recommendations.
    """
    try:
        data = request.get_json()
        if not data or 'weight_kg' not in data:
            return jsonify({"error": "Invalid input. 'weight_kg' is required."}), 400
            
        weight_kg = float(data.get('weight_kg'))
        category = data.get('product_category', 'General')
        fragility = data.get('fragility', 'Medium')
        
        logger.info(f"Request: Weight={weight_kg}, Category={category}")
        
        recommendations = ml_service.get_recommendations(
            product_weight_kg=weight_kg, 
            product_category=category,
            fragility=fragility
        )
        
        if recommendations.empty:
            return jsonify({
                "message": "No suitable materials found.",
                "recommendations": []
            }), 200
            
        results = recommendations.to_dict(orient='records')
        
        return jsonify({
            "product_context": {
                "category": category,
                "weight_kg": weight_kg
            },
            "recommendations": results
        }), 200

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
