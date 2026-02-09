from flask import Flask, render_template, request, jsonify
from recommender import recommend_materials

app = Flask(__name__, template_folder="../templates", static_folder="../static")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.json

    results = recommend_materials(
        category=data["product_category"],
        weight=float(data["weight"]),
        fragility=data["fragility"],
        budget=float(data["budget"]),
        eco_priority=data["eco_priority"],
        top_n=int(data["recommendations"])
    )

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
