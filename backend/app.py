
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from recommendation_engine import MaterialRecommender
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Initialize Recommender Engine
try:
    recommender = MaterialRecommender()
    logger.info("MaterialRecommender initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MaterialRecommender: {e}")
    recommender = None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "healthy", "service": "EcoPackAI Backend"}), 200

@app.route('/', methods=['GET'])
def home():
    """Root endpoint serving the testing UI."""
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def recommend_materials():
    """
    Endpoint to get material recommendations.
    Expected JSON body:
    {
        "product_category": "Electronics",
        "weight_kg": 2.5,
        "fragility": "High" (Optional)
    }
    """
    if not recommender:
        return jsonify({"error": "Recommendation service unavailable"}), 503

    try:
        data = request.get_json()
        
        # Validate Input
        if not data or 'weight_kg' not in data:
            return jsonify({"error": "Invalid input. 'weight_kg' is required."}), 400
            
        weight_kg = float(data.get('weight_kg'))
        category = data.get('product_category', 'General')
        fragility = data.get('fragility', 'Medium')
        
        logger.info(f"Received recommendation request: Weight={weight_kg}, Category={category}, Fragility={fragility}")
        
        # Get Recommendations
        recommendations = recommender.get_recommendations(
            product_weight_kg=weight_kg, 
            product_category=category,
            top_n=5
        )
        
        if recommendations.empty:
            return jsonify({
                "message": "No suitable materials found for the given criteria.",
                "recommendations": []
            }), 200
            
        # Convert DataFrame to JSON serializable list
        results = recommendations.to_dict(orient='records')
        
        return jsonify({
            "product_context": {
                "category": category,
                "weight_kg": weight_kg,
                "fragility": fragility
            },
            "recommendations": results
        }), 200

    except Exception as e:
        logger.error(f"Error processing recommendation request: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
