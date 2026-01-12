@recommend_bp.route("/recommend", methods=["POST"])
def recommend():
    data = request.json
    result = recommend_material(data, top_n=5)
    return jsonify(result)
