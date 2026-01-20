
from flask import Blueprint, jsonify, render_template, request
from sqlalchemy import text
from ..services.db_service import db_service
from ..services.feature_service import feature_service
from ..services.training_service import training_service

learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/data-enhancement')
def page():
    """Render the Adaptive Learning page."""
    return render_template('learning.html')

@learning_bp.route('/api/learning/update-material', methods=['POST'])
def update_material():
    """Update or Insert Material Data."""
    data = request.json
    try:
        # Validate Required Fields
        required = ['material_id', 'material_type', 'strength', 'weight_capacity_kg']
        for field in required:
            if field not in data:
                return jsonify({"success": False, "message": f"Missing field: {field}"}), 400

        engine = db_service.get_engine()
        with engine.connect() as conn:
            # Check existence
            check_query = text("SELECT 1 FROM materials WHERE material_id = :mid")
            exists = conn.execute(check_query, {"mid": data['material_id']}).fetchone()

            if exists:
                # Update
                query = text("""
                    UPDATE materials SET
                        material_type = :mtype,
                        strength = :strength,
                        weight_capacity_kg = :wcap,
                        biodegradability_score = :bio,
                        co2_emission_score = :co2,
                        recyclability_percent = :recycle,
                        cost_per_unit_inr = :cost,
                        water_resistance = :water,
                        recycle_time_days = :days,
                        manufacturing_place = :place
                    WHERE material_id = :mid
                """)
                action = "Updated"
            else:
                # Insert
                query = text("""
                    INSERT INTO materials (
                        material_id, material_type, strength, weight_capacity_kg,
                        biodegradability_score, co2_emission_score, recyclability_percent,
                        cost_per_unit_inr, water_resistance, recycle_time_days, manufacturing_place
                    ) VALUES (
                        :mid, :mtype, :strength, :wcap, :bio, :co2, :recycle, :cost, :water, :days, :place
                    )
                """)
                action = "Inserted"

            conn.execute(query, {
                "mid": data['material_id'],
                "mtype": data.get('material_type'),
                "strength": data.get('strength'),
                "wcap": data.get('weight_capacity_kg'),
                "bio": data.get('biodegradability_score'),
                "co2": data.get('co2_emission_score'),
                "recycle": data.get('recyclability_percent'),
                "cost": data.get('cost_per_unit_inr'),
                "water": data.get('water_resistance'),
                "days": data.get('recycle_time_days'),
                "place": data.get('manufacturing_place')
            })
            conn.commit()

        return jsonify({"success": True, "message": f"Successfully {action} material ID {data['material_id']}"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@learning_bp.route('/api/learning/update-product', methods=['POST'])
def update_product():
    """Update or Insert Product Mapping."""
    data = request.json
    try:
        if 'material_id' not in data or 'category' not in data:
            return jsonify({"success": False, "message": "Missing material_id or category"}), 400

        engine = db_service.get_engine()
        with engine.connect() as conn:
            # 1. Check referential integrity
            mat_check = text("SELECT 1 FROM materials WHERE material_id = :mid")
            if not conn.execute(mat_check, {"mid": data['material_id']}).fetchone():
                return jsonify({"success": False, "message": f"Material ID {data['material_id']} does not exist."}), 400

            # 2. Check existence in product_material
            # Assuming (material_id, category) should be unique for logical update
            check_query = text("SELECT 1 FROM product_material WHERE material_id = :mid AND category = :cat")
            exists = conn.execute(check_query, {"mid": data['material_id'], "cat": data['category']}).fetchone()

            if exists:
                query = text("""
                    UPDATE product_material SET
                        eco_alternative = :eco,
                        weight_capacity_upto = :upto
                    WHERE material_id = :mid AND category = :cat
                """)
                action = "Updated"
            else:
                query = text("""
                    INSERT INTO product_material (material_id, category, eco_alternative, weight_capacity_upto)
                    VALUES (:mid, :cat, :eco, :upto)
                """)
                action = "Inserted"

            conn.execute(query, {
                "mid": data['material_id'],
                "cat": data['category'],
                "eco": data.get('eco_alternative'),
                "upto": data.get('weight_capacity_upto')
            })
            conn.commit()

        return jsonify({"success": True, "message": f"Successfully {action} mapping for {data['category']}"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@learning_bp.route('/api/learning/retrain', methods=['POST'])
def retrain_system():
    """Run Feature Engineering and Retrain Models."""
    try:
        # 1. Run Feature Engineering
        fe_res = feature_service.run_feature_engineering()
        if not fe_res['success']:
            return jsonify(fe_res), 500
        
        # 2. Retrain Models
        train_res = training_service.retrain_models()
        if not train_res['success']:
            return jsonify(train_res), 500

        return jsonify({"success": True, "message": "System successfully updated and retrained!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@learning_bp.route('/api/learning/next-id', methods=['GET'])
def get_next_id():
    """Get the next available Material ID."""
    try:
        engine = db_service.get_engine()
        with engine.connect() as conn:
            query = text("SELECT MAX(material_id) FROM materials")
            max_id = conn.execute(query).scalar()
            next_id = (max_id or 0) + 1
            return jsonify({"success": True, "next_id": next_id})
    except Exception as e:
         return jsonify({"success": False, "message": str(e)}), 500
