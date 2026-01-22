# EcoPackAI ♻️  
**AI-Powered Sustainable Packaging Recommendation System**

EcoPackAI is an end-to-end machine learning project that recommends sustainable packaging materials by balancing **cost efficiency** and **environmental impact (CO₂ footprint)**.  
The system goes beyond simple prediction by combining multiple ML models into an **explainable recommendation engine**.

---

##  Problem Statement

Choosing sustainable packaging is a complex decision involving:
- Material strength and load capacity
- Cost constraints
- Biodegradability and recyclability
- Carbon emissions
- Product fragility and shipping requirements

Traditional rule-based systems fail to capture these **non-linear trade-offs**.  
EcoPackAI solves this using **machine learning–driven decision intelligence**.

---

##  Project Objectives

- Predict **packaging cost** using material and product properties
- Predict **CO₂ environmental impact**
- Combine ML predictions to **rank and recommend materials**
- Provide an explainable, configurable recommendation framework

---

##  Project Structure

EcopackAI/
├── assets/
│ └── ER-Diagram.png
├── data/
│ ├── raw/
│ └── processed/
├── notebooks/
│ ├── 01_data_cleaning.ipynb
│ ├── 02_data_processing.ipynb
│ ├── 03_feature_engineering.ipynb
│ ├── 05_ml_data_preparation.ipynb
│ ├── 06_rf_cost_model.ipynb
│ ├── 07_xgb_co2_model.ipynb
│ └── 08_recommendation_logic.ipynb
├── src/
│ ├── data_loader.py
│ ├── preprocessing.py
│ ├── feature_engineering.py
│ └── recommendation.py
├── models/
│ ├── rf_cost_model.pkl
│ └── xgb_co2_model.pkl
├── requirements.txt
└── README.md


---

##  Milestone 1: Data Engineering & Database Setup

###  Data Cleaning
- Handled missing values
- Standardized column names
- Removed inconsistencies
- Validated realistic value ranges

###  Feature Engineering
Engineered domain-specific features:
- **Cost_Efficiency_Index**
- **CO2_Impact_Index**
- **Material_Suitability_Score**

###  Database Design (PostgreSQL)
- `materials` table
- `products` table
- `material_product_scores` (junction table)

Data was loaded using SQLAlchemy with proper relationships and constraints.

---

##  Milestone 2: Machine Learning & Recommendation Engine

###  Module 3: ML Dataset Preparation

- Train–test split with reproducibility
- Feature selection based on real-world causality
- Two prediction targets:
  - **Cost Prediction**
  - **CO₂ Impact Prediction**
- One-hot encoding for categorical variables
- Feature scaling for stable ML pipelines
- Saved processed datasets for reuse

---

###  Module 4: AI Recommendation Model (ML-Based)

####  Cost Prediction
- **Model**: Random Forest Regressor
- **Metrics**:
  - RMSE ≈ 0.076
  - MAE ≈ 0.058
  - R² ≈ 0.66
- Feature importance showed cost is mainly driven by:
  - Biodegradability
  - Recyclability
  - Strength & weight capacity

####  CO₂ Impact Prediction
- **Model**: XGBoost Regressor
- **Metrics**:
  - RMSE ≈ 0.143
  - MAE ≈ 0.081
  - R² ≈ 0.76
- CO₂ impact driven primarily by:
  - Biodegradability
  - Material type (plastic, glass, metal)

####  ML-Based Material Ranking System
- Combined ML-predicted **cost** and **CO₂**
- Normalized predictions
- Configurable scoring function:
  - Cost-first strategy
  - Sustainability-first strategy
- Generated **material-level recommendations**
- Fully explainable and policy-adjustable

---

##  Key Design Insight

> ML models generate objective predictions, while final recommendations are controlled by a configurable policy layer — allowing business or sustainability priorities to change **without retraining models**.

---

##  Tech Stack

- Python
- Pandas, NumPy
- Scikit-learn
- XGBoost
- PostgreSQL
- SQLAlchemy
- Jupyter Notebook

---

##  Current Status

 Milestone 1 completed  
 Milestone 2 completed  
 Milestone 3: API & Dashboard (upcoming)

---

##  Future Enhancements

- FastAPI-based recommendation service
- Streamlit dashboard for decision-makers
- Policy-based constraints (e.g., plastic penalties)
- Model monitoring & drift detection

---
