
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
        water_resistant = data.get('water_resistant', False)
        force_gemini = data.get('force_gemini', False)
        
        logger.info(f"Request: Weight={weight_kg}, Category={category}, WaterResist={water_resistant}, ForceAI={force_gemini}")
        
        recommendations = ml_service.get_recommendations(
            product_weight_kg=weight_kg, 
            product_category=category,
            fragility=fragility,
            water_resistant=water_resistant,
            force_gemini=force_gemini
        )
        
        if recommendations.empty:
            return jsonify({
                "source": "unknown",
                "recommended_materials": [],
                "confidence_score": 0,
                "notes": "No materials found."
            }), 200
            
        # Determine source (all rows should have same source)
        source = recommendations.iloc[0].get('source', 'database')
        
        results = []
        for _, row in recommendations.iterrows():
            # Map CO2 Score (High score = Low Impact) to Label
            co2_score = row.get('eco_impact_score', 0)
            if co2_score > 70:
                co2_impact = "Low"
            elif co2_score > 40:
                co2_impact = "Medium"
            else:
                co2_impact = "High"
                
            results.append({
                "material_name": row.get('material_type', 'Unknown'),
                "biodegradability_score": row.get('biodegradability_score', 'N/A'),
                "co2_impact": co2_impact,
                "recyclability_percent": f"{row.get('recyclability_percent', 0)}%",
                "estimated_cost": f"₹{row.get('predicted_cost_inr', 0):.2f}",
                "suitability_reason": "Selected for high structural integrity and environmental compliance." if source == 'database' else "AI-recommended based on web availability and sustainability criteria.",
                "weight_capacity_kg": row.get('weight_capacity_kg', 'N/A'),
                "manufacturing_place": row.get('manufacturing_place', 'Global'),
                "final_rank_score": row.get('final_rank_score', 0)
            })

        # Calculate confidence (avg of final scores normalized to 0-1 range usually, here just taking mean)
        avg_score = recommendations['final_rank_score'].mean()
        
        return jsonify({
            "source": source,
            "recommended_materials": results,
            "confidence_score": f"{avg_score:.2f}",
            "notes": "Values predicted by ML models." if source == 'database' else "Values estimated by AI from web data."
        }), 200

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
