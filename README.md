EcoPackAI – AI-Powered Sustainable Packaging Recommendation System
Project Overview

EcoPackAI is an AI-driven decision support system that recommends optimal and sustainable packaging materials for different products.
The system evaluates cost, strength, recyclability, biodegradability, and CO₂ footprint using machine learning models and ranks materials using an AI-based suitability score.

Objectives

Promote eco-friendly packaging decisions

Reduce packaging cost and carbon footprint

Apply machine learning for data-driven recommendations

Build an end-to-end system (Database → ML → API → UI)

Tech Stack

Backend: Python, Flask, Flask-CORS

Database: PostgreSQL

ML: Pandas, NumPy, Scikit-learn, XGBoost

Frontend: HTML, CSS, Bootstrap, JavaScript

Tools: Jupyter Notebook, GitHub, VS Code

Project Architecture
EcoPackAI/
│
├── data/
│   └── processed/
│       ├── materials_dataset.csv
│       └── products_dataset.csv
│
├── src/
│   └── feature_engineering.py
│
├── models/
│   ├── rf_cost_model.pkl
│   ├── xgb_co2_model.pkl
│   └── scaler.pkl
│
├── backend/
│   ├── app.py
│   └── db.py
│
├── frontend/
│   ├── templates/
│   │   ├── index.html
│   │   └── results.html
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/script.js
│
├── notebooks/
│   ├── module1_data_collection.ipynb
│   ├── module2_data_cleaning_feature_engineering.ipynb
│   ├── module3_ml_preparation.ipynb
│   ├── module4_model_training.ipynb
│   ├── module5_flask_backend_api.ipynb
│   └── module6_frontend_ui_development.ipynb
│
└── README.md

Module-wise Progress
 Module 1 – Data Collection & Database Setup

Created Materials dataset (120 records)

Created Products dataset (175 records)

Designed PostgreSQL schema

Imported datasets into PostgreSQL

 Module 2 – Data Cleaning & Feature Engineering

Verified no missing values or duplicates

Standardized numerical features

Engineered features:

Cost score

CO₂ score

Sustainability score

Material suitability score

Implemented feature logic in src/feature_engineering.py

 Module 3 – Machine Learning Dataset Preparation

Cross-joined products and materials

Generated ~21,000 product–material combinations

Created ML targets:

target_cost_inr

target_co2_kg

Selected ML features (9 key attributes)

Split data into 80% train / 20% test

Applied StandardScaler

 Module 4 – AI Recommendation Models

Cost Prediction

Model: Random Forest Regressor

Metrics:

RMSE ≈ 0.48

MAE ≈ 0.12

R² ≈ 0.999

CO₂ Prediction

Model: XGBoost Regressor

Metrics:

RMSE ≈ 0.017

MAE ≈ 0.009

R² ≈ 1.0

Outputs

Trained models saved as .pkl

Integrated predictions into ranking logic

 Module 5 – Flask Backend API

Built Flask REST API

Endpoints:

/api/health

/api/recommend (POST)

Features:

Product input handling

Material filtering

Feature engineering

ML-based cost & CO₂ prediction

Final ranking logic

Connected backend to PostgreSQL

Implemented structured JSON responses

Added basic API key security

 Module 6 – Frontend UI Development

Built UI using HTML, CSS, Bootstrap

Pages:

Product input page

Results page

Features:

Input form with validations

API integration using Fetch

Display ranked recommendations in table

Comparison metrics:

Cost

CO₂

Recyclability

Biodegradability

Suitability score

Improved layout using Bootstrap cards & tables



## ML Models (Not Tracked in Git)

Trained ML models are intentionally excluded from version control due to size limits.

Models used:
- Random Forest (Cost Prediction)
- XGBoost (CO₂ Prediction)
- StandardScaler

To regenerate models:
1. Run `module3_ml_preparation.ipynb`
2. Run `module4_model_training.ipynb`
3. Models will be saved locally under `/models`
