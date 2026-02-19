🌱 EcoPackAI – AI Powered Sustainable Packaging Recommendation System

EcoPackAI is an intelligent web-based application that recommends eco-friendly packaging materials based on product requirements, sustainability priorities, and cost constraints.

This project combines data engineering, machine learning concepts, backend development, and frontend UI design to build a complete sustainable packaging recommendation system.

The goal of EcoPackAI is to help industries make environmentally responsible and cost-effective packaging decisions.

🎯 Project Objective

The main objective of this project is to:

Recommend sustainable packaging materials

Reduce CO₂ emissions

Optimize packaging cost

Rank materials based on environmental impact

Generate downloadable sustainability reports

The system analyzes material properties and ranks them using a weighted sustainability scoring mechanism.

📦 Dataset Description

The system uses a structured eco-friendly material dataset containing:

Material ID

Material Type

Strength

Weight Capacity

Cost per Unit

Biodegradability Score

CO₂ Emission Score

Recyclability Percentage

Product Category (Electronics, Food, Cosmetics, etc.)

All numeric features are normalized and prepared for intelligent scoring.

The cleaned ML-ready dataset is stored as:

data/materials_ml_ready.csv

🛠 Data Processing

Before building the recommendation system, the dataset was:

Cleaned to handle missing and zero values

Normalized using Min-Max Scaling

One-hot encoded for categorical features

Enhanced with engineered features like:

CO₂ Impact Index

Cost Efficiency Index

Sustainability Score

The processed data was stored in PostgreSQL and exported as structured CSV files for model development.

🤖 Recommendation Logic

The recommendation system works using a weighted sustainability scoring approach.

When a user inputs:

Product category

Product weight

Fragility level

Budget

Eco-priority level

Number of recommendations

The system:

Filters materials by product category

Filters by budget

Applies eco-priority weight

Adjusts score based on fragility protection requirement

Calculates final sustainability score

Ranks materials in descending order

Returns top N recommendations

Final Score is calculated using:

Biodegradability

Recyclability

CO₂ emission (inverted impact)

Fragility-based protection weight

This ensures materials with better environmental performance and affordability rank higher.

🌐 Web Application

The project includes a complete Flask-based web application.

Backend

Built using:

Flask

Pandas

OpenPyXL

APIs:

/ → Loads UI

/recommend → Returns recommendations

/export_excel → Downloads sustainability report

The backend dynamically reads the dataset and generates ranked results in real time.

Frontend

Built using:

HTML

CSS

Bootstrap

Features:

User input form

Dynamic recommendation table

Cost and CO₂ comparison

Download Excel Report button

The UI is simple, clean, and evaluation-ready.

📊 Sustainability Report

Users can download a generated Excel file containing:

Material ID

Final Cost (₹)

CO₂ Impact

Cost Savings %

CO₂ Reduction %

The report is generated dynamically using OpenPyXL.

🗂 Project Structure
EcoPackAI/
│
├── backend/
│   ├── app.py
│   ├── recommender.py
│   ├── templates/
│   │    └── index.html
│
├── data/
│   └── materials_ml_ready.csv
│
├── scripts/
│   ├── data_generation.py
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── db_connection.py
│
└── README.md

⚙️ Technologies Used

Python

Pandas

NumPy

Scikit-Learn

XGBoost

Flask

PostgreSQL

SQLAlchemy

OpenPyXL

HTML / CSS / Bootstrap

🚀 How to Run the Project

Install required libraries:

pip install flask pandas openpyxl scikit-learn xgboost psycopg2


Navigate to backend folder:

cd backend


Run the application:

python app.py


Open in browser:

http://127.0.0.1:5000/

📈 Output

The system provides:

Ranked sustainable material recommendations

CO₂ reduction percentage

Cost savings percentage

Downloadable Excel sustainability report

🌍 Impact

EcoPackAI demonstrates how AI and data-driven decision making can support sustainable packaging solutions by balancing environmental responsibility and cost efficiency.

👩‍💻 Developed By

Reddi Rani

🏁 Conclusion

EcoPackAI is a complete AI-powered sustainable packaging recommendation system that integrates:

Data preprocessing

Feature engineering

Intelligent ranking logic

Backend API development

Frontend user interface

Sustainability reporting

This project showcases how artificial intelligence can be applied to solve real-world environmental challenges in the packaging industry.