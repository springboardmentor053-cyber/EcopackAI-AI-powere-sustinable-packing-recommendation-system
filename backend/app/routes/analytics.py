
from flask import Blueprint, jsonify, render_template
from ..services.analytics_service import analytics_service
import json

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard')
def dashboard():
    """Render the dashboard page."""
    return render_template('dashboard.html')

@analytics_bp.route('/api/analytics/data')
def get_analytics_data():
    """Return JSON data for frontend plotting."""
    try:
        # 1. CO2 Emissions
        df_co2 = analytics_service.get_avg_co2_by_material()
        co2_data = df_co2.to_dict(orient='records')
        
        # 2. Material Counts by Category
        df_cat = analytics_service.get_material_category_counts()
        category_data = df_cat.to_dict(orient='records')
        
        # 3. Sustainability Scores (for Histogram)
        df_sust = analytics_service.get_sustainability_distribution()
        sust_scores = df_sust['sustainability_score'].tolist()
        
        # 4. Cost Data
        df_cost = analytics_service.get_cost_distribution()
        cost_data = df_cost.to_dict(orient='records')

        return jsonify({
            "co2_emissions": co2_data,
            "category_counts": category_data,
            "sustainability_scores": sust_scores,
            "cost_data": cost_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
