from flask import Flask, request, jsonify, render_template, send_file
from recommender import recommend_materials
from openpyxl import Workbook
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/recommend", methods=["POST"])
def recommend():

    data = request.get_json()

    results = recommend_materials(
        product_category=data["product_category"],
        weight=float(data["weight"]),
        fragility=data["fragility"],
        budget=float(data["budget"]),
        eco_priority=data["eco_priority"],
        recommendations=int(data["recommendations"])
    )

    return jsonify(results)


@app.route("/export_excel", methods=["POST"])
def export_excel():

    data = request.get_json()

    results = recommend_materials(
        product_category=data["product_category"],
        weight=float(data["weight"]),
        fragility=data["fragility"],
        budget=float(data["budget"]),
        eco_priority=data["eco_priority"],
        recommendations=int(data["recommendations"])
    )

    wb = Workbook()
    ws = wb.active
    ws.title = "Sustainability Report"

    ws.append(["Material", "Cost (₹)", "CO2", "Cost Savings %", "CO2 Reduction %"])

    for row in results:
        ws.append([
            row["Material"],
            row["final_cost"],
            row["final_co2"],
            row["cost_savings_percent"],
            row["co2_reduction_percent"]
        ])

    file_path = os.path.join(os.getcwd(), "sustainability_report.xlsx")
    wb.save(file_path)

    return send_file(
        file_path,
        as_attachment=True,
        download_name="sustainability_report.xlsx"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)