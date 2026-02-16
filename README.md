# EcoPackAI
## AI-Powered Sustainable Packaging Recommendation System


### Live Deployment

* Production URL:
https://ecopackai-qj2j.onrender.com



### Project Overview

EcoPackAI is a full-stack AI-driven decision support system that recommends the most sustainable and cost-efficient packaging material for a given product.

The system evaluates:
* Product weight
* Fragility level
* Product category
* Maximum packaging cost constraint
* Environmental sustainability parameters

Using machine learning models, EcoPackAI predicts packaging cost and CO₂ emissions, then ranks materials using a composite suitability and environmental score.

This project demonstrates a complete end-to-end AI system:

* Database → Feature Engineering → ML Models → REST API → Dashboard → Cloud Deployment



### System Architecture

Frontend (HTML / CSS / JS)
        ↓
Flask Backend (REST API Layer)
        ↓
Machine Learning Models (RF + XGBoost + Scaler)
        ↓
PostgreSQL Database (Products, Materials, Logs)
        ↓
Business Intelligence Dashboard + Reports



### Machine Learning Models
| Model | Purpose|
|-------|--------|
| Random Forest Regressor | Predict Packaging Cost |
|XGBoost Regressor | Predict CO₂ Emission |
| StandardScaler | Feature Normalization |

Model Details:

* Models trained in Jupyter Notebooks
* ~21,000 product–material combinations generated
* 80/20 train-test split
* High R² performance on both models
* Exported as .pkl files
* Deployment environment library versions aligned with training environment to ensure prediction consistency



### Database Schema

1. products

Stores product specifications:
* product_id
* product_name
* product_category
* product_weight_kg
* fragility_level
* required_strength_score
* preferred_biodegradability_score
* max_packaging_cost_inr
* temperature_sensitive


2. materials

Stores packaging material attributes:
* material_id
* material_name
* strength_score
* weight_capacity_kg
* biodegradability_score
* co2_emission_kg
* recyclability_percent
* cost_per_unit_inr
* product_category
* used_for_products


3. recommendation_logs

Stores generated predictions for analytics:
* predicted_cost
* predicted_co2
* material_name
* suitability_score
* category
* timestamp
Used for dashboard visualizations and reporting.



### Core Features Implemented

1. Intelligent Recommendation Engine

Ranks materials based on:
* Predicted packaging cost
* Predicted CO₂ emission
* Suitability score
* Environmental sustainability score
* Recyclability percentage
* Biodegradability score


2. Interactive BI Dashboard

Displays:
* Total recommendations generated
* Average predicted cost
* Average predicted CO₂ emission
* Category-wise cost & emission insights
* Top recommended materials
* Material comparison analytics
All charts are dynamic and data-driven from PostgreSQL.


3. Export Functionality

Supports:
* CSV export (Excel compatible)
* PDF report export
* Comparison report export
* Dashboard analytics export
PDF generation implemented using:
* ReportLab (backend)
* jsPDF (frontend)


4. API Security

* API protected using header-based API key authentication
* Unauthorized requests return 401
* Secrets managed via environment variables



### Tech Stack

Backend
* Python
* Flask
* Flask-CORS
* Gunicorn (Production WSGI server)

Machine Learning
* Pandas
* NumPy
* Scikit-learn
* XGBoost

Database
* PostgreSQL (Cloud-hosted on Render)

Frontend
* HTML
* CSS
* Bootstrap
* JavaScript (Fetch API)
* Chart.js

Deployment
* Render Cloud
* Managed PostgreSQL
* Production environment configuration



### Key Technical Highlights

* End-to-end AI pipeline implementation
* Cross-joined ML dataset (~21K combinations)
* Version-controlled ML training notebooks
* Dependency alignment between training and production
* Production-grade WSGI deployment via Gunicorn
* Cloud-hosted PostgreSQL integration
* Secure API key authentication
* Responsive UI with structured ranking logic
* Real-time BI dashboard built from prediction logs
* Automated PDF report generation



### Business Value

EcoPackAI can be applied in:
* E-commerce packaging optimization
* Sustainable manufacturing decision systems
* ESG reporting frameworks
* Carbon footprint reduction strategies
* Supply chain optimization

It demonstrates practical AI application in sustainability-focused decision making.

### Project Information

Project Type: AI Virtual Internship Project
Developed By: Varshitha Tummala
