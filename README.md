# EcoPackAI

**AI-Powered Sustainable Packaging Material Recommendation System**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-EcoPackAI-brightgreen)](https://ecopackai-q982.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://postgresql.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3-orange)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-red)](https://xgboost.ai)

EcoPackAI is a full-stack web platform that recommends optimal eco-friendly packaging materials to businesses based on product attributes, sustainability parameters, and cost constraints. The system uses machine learning models to predict material suitability, environmental impact (CO₂ footprint), and cost efficiency.

## 🌐 Live Demo

**🔗 [https://ecopackai-q982.onrender.com/](https://ecopackai-q982.onrender.com/)**

| Page | URL |
|------|-----|
| Recommendations | [https://ecopackai-q982.onrender.com/](https://ecopackai-q982.onrender.com/) |
| Dashboard | [https://ecopackai-q982.onrender.com/dashboard](https://ecopackai-q982.onrender.com/dashboard) |

---

## 📑 Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Key Features](#key-features)
- [Screenshots](#screenshots)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Machine Learning Models](#machine-learning-models)
- [API Documentation](#api-documentation)
- [Frontend Interface](#frontend-interface)
- [Installation & Setup](#installation--setup)
- [Deployment](#deployment)
- [Usage Guide](#usage-guide)
- [Sample Results](#sample-results)
- [Future Enhancements](#future-enhancements)

---

## ❓ Problem Statement

Traditional packaging used in industries and e-commerce heavily relies on non-biodegradable and costly materials, causing increasing environmental damage and financial inefficiency. Businesses lack intelligent decision-support systems that can help them evaluate and adopt eco-friendly alternative packaging materials without compromising durability, product safety, or cost-efficiency.

---

## 💡 Solution Overview

EcoPackAI solves this challenge by:

1. Analyzing 25 different packaging materials across multiple sustainability metrics
2. Using ML models to predict material suitability for specific product categories
3. Providing ranked recommendations based on suitability, cost, and environmental impact
4. Enabling comparison with current packaging to show potential CO₂ and cost savings
5. Storing recommendation history for business intelligence analytics
6. Providing a BI Dashboard for tracking environmental impact over time

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **AI-Powered Recommendations** | Random Forest and XGBoost models predict optimal materials |
| **25 Packaging Materials** | Comprehensive database covering paper, plastic, foam, fiber, and organic materials |
| **13 Product Categories** | From Electronics to Pharmaceuticals, each with specific requirements |
| **Real-time Predictions** | Suitability score, CO₂ impact, and cost predictions in seconds |
| **Comparison Analysis** | Compare current material vs recommended to see exact savings |
| **Budget Filtering** | Filter recommendations by maximum cost constraint |
| **Fragility Override** | Override category defaults for specific product needs |
| **BI Dashboard** | Analytics dashboard with KPIs, charts, and insights |
| **Recommendation Logging** | All recommendations saved for analytics |
| **REST API** | 10+ endpoints for integration with other systems |
| **Responsive UI** | Works on desktop and mobile devices |
| **Cloud Deployed** | Live on Render with PostgreSQL database |

---

## 📸 Screenshots

### Recommendation Interface
![Recommendation Interface](screenshots/recommendation-interface.png)
*AI-powered material recommendations with suitability scores, cost, and CO₂ impact*

### Comparison Chart
![Comparison Chart](screenshots/comparison-chart.png)
*Dual-axis bar chart comparing Cost (INR) vs CO₂ Impact (kg)*

### Savings Analysis
![Savings Analysis](screenshots/savings-analysis.png)
*CO₂ reduction and cost savings when switching from current material*

### BI Dashboard
![Dashboard](screenshots/dashboard.png)
*Business Intelligence dashboard with KPIs, charts, and recent activity*

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interface Layer                       │
│              (HTML + CSS + JavaScript + Chart.js)               │
│         ┌─────────────────┐    ┌─────────────────┐              │
│         │  Recommendations│    │    Dashboard    │              │
│         │      Page       │    │      Page       │              │
│         └─────────────────┘    └─────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Flask Backend API                          │
│         (REST Endpoints + Rate Limiting + Validation)           │
│                                                                 │
│   /api/recommend    /api/compare    /api/analytics/summary      │
│   /api/categories   /api/materials  /api/analytics/by-material  │
│   /api/health       /api/eco-score  /api/analytics/by-category  │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼                               ▼
┌───────────────────────────┐   ┌───────────────────────────────┐
│     AI/ML Layer           │   │     PostgreSQL Database       │
│  - Random Forest (2x)     │   │  - packaging_materials        │
│  - XGBoost                │   │  - product_categories         │
│  - StandardScaler         │   │  - recommendations            │
│  - LabelEncoders          │   │                               │
└───────────────────────────┘   └───────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | HTML5, CSS3, JavaScript (ES6), Chart.js |
| **Backend** | Python 3.11, Flask 3.0, Flask-CORS |
| **Database** | PostgreSQL 16 |
| **ML/AI** | scikit-learn 1.3, XGBoost 2.0, pandas, numpy |
| **ORM** | SQLAlchemy 2.0 |
| **Deployment** | Render (Web Service + PostgreSQL) |
| **Model Serialization** | joblib |
| **Version Control** | Git, GitHub |

---

## 📁 Project Structure

```
EcoPackAI/
│
├── backend/
│   └── app.py                    # Flask API server (10+ endpoints)
│
├── frontend/
│   ├── templates/
│   │   ├── index.html            # Recommendations page
│   │   └── dashboard.html        # BI Dashboard page
│   └── static/
│       ├── css/
│       │   ├── style.css         # Recommendations styling
│       │   └── dashboard.css     # Dashboard styling
│       └── js/
│           ├── app.js            # Recommendations logic
│           └── dashboard.js      # Dashboard logic
│
├── ml/
│   ├── models/
│   │   ├── rf_suitability.pkl    # Random Forest - Suitability prediction
│   │   ├── rf_cost.pkl           # Random Forest - Cost prediction
│   │   ├── xgb_co2.pkl           # XGBoost - CO₂ prediction
│   │   ├── encoders.pkl          # Label encoders for categorical features
│   │   ├── scaler.pkl            # StandardScaler for feature normalization
│   │   └── feature_columns.pkl   # Feature column order
│   ├── recommendation_engine.py  # Core ML recommendation logic
│   ├── train_models.py           # Model training script
│   ├── generate_training_data.py # Training data generation
│   ├── feature_engineering.py    # Feature engineering pipeline
│   └── prepare_ml_data.py        # Data preparation utilities
│
├── data/
│   ├── raw/
│   │   └── materials.csv         # Raw material data (25 materials)
│   └── processed/
│       └── materials_engineered.csv  # Feature-engineered data
│
├── database/
│   └── init_schema.sql           # PostgreSQL table definitions
│
├── requirements.txt              # Python dependencies
├── Procfile                      # Render deployment config
├── render.yaml                   # Render blueprint
├── runtime.txt                   # Python version specification
└── README.md                     # This file
```

---

## 🗄️ Database Schema

### ER Diagram

![ER Diagram](screenshots/er-diagram.png)

*Entity Relationship Diagram showing the database structure*

<!-- 
ER Diagram placeholder - Replace with actual diagram
Tables: packaging_materials, product_categories, recommendations
-->

---

### Table: `packaging_materials`

Stores 25 packaging materials with their properties.

| Column | Type | Description |
|--------|------|-------------|
| material_id | SERIAL | Primary key |
| material_name | VARCHAR(100) | Unique material name |
| material_type | VARCHAR(50) | Category: Paper-based, Plastic-based, Foam-based, Fiber/Fabric, Organic |
| strength_score | DECIMAL(3,2) | 0-1 scale, higher = stronger |
| weight_capacity_kg | DECIMAL(6,2) | Maximum weight the material can handle |
| biodegradability_score | DECIMAL(3,2) | 0-1 scale, higher = more biodegradable |
| recyclability_percent | DECIMAL(5,2) | Percentage that can be recycled |
| moisture_resistance | DECIMAL(3,2) | 0-1 scale, higher = more resistant |
| co2_emission_kg | DECIMAL(6,4) | CO₂ emitted per kg of material production |
| cost_per_kg | DECIMAL(8,2) | Cost in INR per kg |
| eco_score | DECIMAL(4,3) | Computed sustainability score |
| created_at | TIMESTAMP | Record creation time |

### Table: `product_categories`

Stores 13 product categories with their packaging requirements.

| Column | Type | Description |
|--------|------|-------------|
| category_id | SERIAL | Primary key |
| category_name | VARCHAR(100) | Unique category name |
| fragility_level | VARCHAR(20) | low, medium, high |
| requires_cushioning | BOOLEAN | Whether products need cushioning |
| moisture_sensitive | BOOLEAN | Whether products are moisture sensitive |
| temperature_sensitive | BOOLEAN | Whether products are temperature sensitive |
| typical_weight_range | VARCHAR(50) | Typical product weight range |
| created_at | TIMESTAMP | Record creation time |

### Table: `recommendations`

Logs all recommendations for analytics.

| Column | Type | Description |
|--------|------|-------------|
| recommendation_id | SERIAL | Primary key |
| category_name | VARCHAR(100) | Product category |
| product_weight_kg | DECIMAL(8,2) | User-entered weight |
| fragility_level | VARCHAR(20) | Fragility used (auto or override) |
| budget_limit | DECIMAL(10,2) | Budget constraint if provided |
| current_material_name | VARCHAR(100) | User's current material (optional) |
| recommended_material_name | VARCHAR(100) | AI recommended material |
| recommended_material_type | VARCHAR(50) | Type of recommended material |
| suitability_score | DECIMAL(5,3) | Predicted suitability (0-1) |
| predicted_cost_inr | DECIMAL(10,2) | Predicted cost in INR |
| predicted_co2_kg | DECIMAL(8,4) | Predicted CO₂ emission in kg |
| eco_score | DECIMAL(4,3) | Environmental score (0-1) |
| co2_savings_kg | DECIMAL(8,4) | CO₂ saved vs current material |
| cost_savings_inr | DECIMAL(10,2) | Cost saved vs current material |
| created_at | TIMESTAMP | When recommendation was made |

---

## 🤖 Machine Learning Models

### Model Performance

| Model | Algorithm | Target | R² Score | RMSE |
|-------|-----------|--------|----------|------|
| Suitability | Random Forest Regressor | suitability_score | 0.97+ | 0.02 |
| CO₂ Prediction | XGBoost Regressor | predicted_co2_kg | 0.98+ | 0.03 |
| Cost Prediction | Random Forest Regressor | predicted_cost_inr | 0.95+ | 5.2 |

### Feature Importance (Suitability Model)

| Feature | Importance |
|---------|------------|
| product_weight_kg | 51.5% |
| material_type_encoded | 12.3% |
| strength_score | 9.8% |
| moisture_resistance | 7.2% |
| fragility_level_encoded | 6.1% |
| Other features | 13.1% |

### Training Data

- **Samples**: 2,275 (13 categories × 25 materials × 7 weight variations)
- **Features**: 15 (5 product attributes + 10 material properties)
- **Train/Test Split**: 80/20

### Engineered Features

| Feature | Formula | Purpose |
|---------|---------|---------|
| eco_score | (biodegradability × 0.40) + (recyclability/100 × 0.25) + ((1 - co2_impact_index) × 0.35) | Overall sustainability metric |
| co2_impact_index | Normalized CO₂ emission (0-1) | Standardized emission comparison |
| cost_efficiency_index | Normalized cost (0-1) | Standardized cost comparison |

---

## 📡 API Documentation

### Base URL
```
Production: https://ecopackai-q982.onrender.com
Local:      http://localhost:5000
```

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/categories` | List all categories |
| GET | `/api/materials` | List all materials |
| GET | `/api/materials/<name>` | Get material details |
| POST | `/api/recommend` | Get AI recommendations |
| POST | `/api/compare` | Compare materials |
| POST | `/api/eco-score` | Get eco score |
| GET | `/api/analytics/summary` | Dashboard summary |
| GET | `/api/analytics/by-material` | Stats by material |
| GET | `/api/analytics/by-category` | Stats by category |
| GET | `/api/analytics/recent` | Recent recommendations |

### Core Endpoints

#### 1. Health Check
```
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "message": "EcoPackAI API is running",
  "version": "1.0.0",
  "models_loaded": {
    "suitability": true,
    "co2": true,
    "cost": true
  }
}
```

#### 2. Get Recommendations
```
POST /api/recommend
```
**Request Body:**
```json
{
  "category": "Electronics",
  "weight": 3.5,
  "top_n": 5,
  "fragility_override": "auto",
  "budget_limit": 100
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| category | string | Yes | Product category name |
| weight | float | Yes | Product weight in kg |
| top_n | int | No | Number of results (default: 5) |
| fragility_override | string | No | "auto", "low", "medium", "high" |
| budget_limit | float | No | Max cost in INR |

**Response:**
```json
{
  "status": "success",
  "category": "Electronics",
  "product_weight_kg": 3.5,
  "count": 5,
  "recommendations": [
    {
      "material_id": 7,
      "material_name": "Recycled PET (rPET)",
      "material_type": "Plastic-based",
      "suitability_score": 1.0,
      "predicted_co2_kg": 0.0325,
      "predicted_cost_inr": 80.02,
      "eco_score": 0.513,
      "can_handle_weight": true,
      "weight_capacity_kg": 35.0
    }
  ]
}
```

#### 3. Compare Materials
```
POST /api/compare
```
**Request Body:**
```json
{
  "category": "Electronics",
  "weight": 3.5,
  "current_material": "EPS (Expanded Polystyrene)"
}
```

**Response:**
```json
{
  "status": "success",
  "comparison": {
    "current_material": "EPS (Expanded Polystyrene)",
    "current_co2_kg": 0.1785,
    "current_cost_inr": 110.25,
    "recommended_material": "Recycled PET (rPET)",
    "recommended_co2_kg": 0.0325,
    "recommended_cost_inr": 80.02,
    "recommended_eco_score": 0.513,
    "co2_savings_kg": 0.146,
    "co2_reduction_percent": 81.8,
    "cost_difference_inr": 30.23
  }
}
```

#### 4. Analytics Summary (Dashboard)
```
GET /api/analytics/summary
```
**Response:**
```json
{
  "status": "success",
  "analytics": {
    "total_recommendations": 50,
    "categories_served": 11,
    "unique_materials_recommended": 8,
    "total_co2_saved_kg": 3.53,
    "total_cost_saved_inr": 245.67,
    "avg_suitability_score": 0.93,
    "avg_eco_score": 0.72
  }
}
```

### Error Responses

All endpoints return errors in this format:
```json
{
  "status": "error",
  "message": "Description of the error"
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

### Rate Limiting

- **Limit**: 60 requests per minute per IP
- **Window**: Sliding window algorithm
- **Response when exceeded**: 429 status with retry time

---

## 🖥️ Frontend Interface

### Pages

| Page | Path | Description |
|------|------|-------------|
| Recommendations | `/` | Main recommendation interface |
| Dashboard | `/dashboard` | BI Analytics dashboard |

### Recommendation Page - Input Parameters

| Input | Type | Purpose |
|-------|------|---------|
| **Product Category** | Dropdown | Determines fragility, cushioning, moisture, temperature needs |
| **Product Weight (kg)** | Number | Primary ML feature, filters by weight capacity |
| **Fragility Level** | Dropdown | Override category default (Auto/Low/Medium/High) |
| **Budget Limit (Rs.)** | Number | Post-prediction filter, removes expensive materials |
| **Number of Recommendations** | Dropdown | Controls output size (3/5/10) |
| **Current Material** | Dropdown | Enables comparison to show savings |

### Recommendation Page - Output Sections

1. **Recommended Materials** - Cards showing top materials with scores
2. **Recommendation Analytics** - Lowest cost, lowest CO₂, best overall
3. **Comparison Chart** - Dual-axis bar chart (Cost vs CO₂)
4. **Material Comparison Table** - Full details with ranking
5. **Savings vs Current** - CO₂ and cost savings (if current material selected)

### Dashboard Page - KPIs & Charts

| Component | Description |
|-----------|-------------|
| **Total Recommendations** | Count of all recommendations made |
| **CO₂ Saved** | Total environmental impact saved |
| **Avg Suitability** | Average recommendation quality |
| **Cost Impact** | Total cost implications |
| **Top Materials Chart** | Bar chart of most recommended materials |
| **CO₂ by Category Chart** | Environmental impact by industry |
| **Recent Activity** | Latest recommendation history |
| **Quick Insights** | AI-generated observations |

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- pip (Python package manager)
- Git

### Step 1: Clone Repository

```bash
git clone https://github.com/mani9kanta3/EcoPackAI-AI-Powered-Sustainable-Packaging-Recommendation-System.git
cd EcoPackAI-AI-Powered-Sustainable-Packaging-Recommendation-System
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install flask flask-cors pandas numpy scikit-learn xgboost sqlalchemy psycopg2-binary joblib gunicorn
```

### Step 4: Setup PostgreSQL Database

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ecopackai;

# Connect to database
\c ecopackai

# Run schema from database/init_schema.sql
```

### Step 5: Configure Environment

Create `.env` file or set environment variable:
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/ecopackai
```

### Step 6: Run Application

```bash
cd backend
python app.py
```

### Step 7: Access Application

Open browser: `http://localhost:5000`

---

## 🚀 Deployment

### Deployed On: Render

| Service | Type | URL |
|---------|------|-----|
| Web Service | Python | https://ecopackai-q982.onrender.com |
| Database | PostgreSQL | Render Managed PostgreSQL |

### Deployment Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies |
| `Procfile` | Start command for Render |
| `render.yaml` | Render blueprint configuration |
| `runtime.txt` | Python version (3.11.6) |

### Deploy Your Own

1. Fork this repository
2. Create account on [Render](https://render.com)
3. Create PostgreSQL database
4. Create Web Service connected to your repo
5. Add `DATABASE_URL` environment variable
6. Deploy!

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |

---

## 📖 Usage Guide

### Basic Recommendation

1. Select **Product Category** (e.g., "Electronics")
2. Enter **Product Weight** (e.g., 3.5 kg)
3. Click **"Run Recommendation Engine"**
4. View ranked materials with scores

### With Budget Constraint

1. Select category and enter weight
2. Enter **Budget Limit** (e.g., Rs. 100)
3. Click run — materials above budget are filtered out

### With Fragility Override

1. Select category (e.g., "Electronics" defaults to High fragility)
2. Change **Fragility Level** to "Low" (for USB cables, non-fragile items)
3. Results will change based on reduced protection needs

### With Comparison

1. Select all inputs as above
2. Select **Current Packaging Material** (e.g., "EPS (Expanded Polystyrene)")
3. Click run
4. View **Savings vs Current Material** section showing CO₂ and cost differences

### Using the Dashboard

1. Navigate to `/dashboard`
2. View KPI cards for overall metrics
3. Analyze Top Materials and CO₂ by Category charts
4. Check Recent Activity for recommendation history
5. Use Export PDF to download reports

---

## 📊 Sample Results

### Example: Electronics, 3.5 kg, Auto Fragility, No Budget

| Rank | Material | Suitability | Cost (INR) | CO₂ (kg) | Eco Score |
|------|----------|-------------|------------|----------|-----------|
| #1 | Recycled PET (rPET) | 100.0% | 80.02 | 0.0325 | 0.513 |
| #2 | Hemp Packaging | 94.3% | 222.02 | 0.0236 | 0.787 |
| #3 | Honeycomb Cardboard | 94.0% | 98.94 | 0.0394 | 0.849 |
| #4 | Bamboo Fiber | 91.8% | 106.93 | 0.0341 | 0.713 |
| #5 | PLA Bioplastic | 91.6% | 198.66 | 0.0630 | 0.505 |

### Example: Comparison Result

**Current:** EPS (Expanded Polystyrene)
- CO₂: 0.1785 kg
- Cost: Rs. 110.25

**Recommended:** Recycled PET (rPET)
- CO₂: 0.0325 kg
- Cost: Rs. 80.02

**Savings:**
- CO₂ Reduction: **81.8%**
- CO₂ Saved: **0.146 kg**
- Cost Saved: **Rs. 30.23**

---

## 📈 Understanding the Scores

### Eco Score (0 to 1)

**Higher is better.** Composite sustainability metric.

| Range | Meaning | Examples |
|-------|---------|----------|
| 0.80 - 1.00 | Excellent | Mushroom Foam, Cornstarch Peanuts |
| 0.60 - 0.79 | Good | Jute Fiber, Corrugated Cardboard |
| 0.40 - 0.59 | Moderate | Recycled PET, PLA Bioplastic |
| 0.00 - 0.39 | Poor | EPS, Air Pillows |

### CO₂ Impact (kg)

**Lower is better.** Actual kg of CO₂ emitted per shipment.

| Range | Meaning |
|-------|---------|
| Below 0.05 kg | Excellent |
| 0.05 - 0.10 kg | Good |
| 0.10 - 0.20 kg | Moderate |
| Above 0.20 kg | High |

### Suitability Score (0 to 1)

**Higher is better.** How well the material protects this specific product.

- 1.0 (100%) = Perfect match
- 0.5 (50%) = Material penalized (can't handle weight)
- Considers: strength, moisture resistance, cushioning needs, weight capacity

---

## 🔮 Future Enhancements

- [ ] **PDF/Excel Export** - Download detailed sustainability reports
- [ ] **User Authentication** - Login system for businesses
- [ ] **Historical Trends** - Track recommendations over time with graphs
- [ ] **Multi-language Support** - Hindi, regional languages
- [ ] **Mobile App** - React Native version
- [ ] **Supplier Integration** - Direct ordering from material suppliers
- [ ] **Carbon Footprint Calculator** - Annual emissions tracking
- [ ] **Email Reports** - Automated weekly sustainability reports
- [ ] **API Key Management** - Secure API access for integrations

---

## 🏆 Project Info

| | |
|---|---|
| **Project Name** | EcoPackAI - AI-Powered Sustainable Packaging Recommendation System |
| **Domain** | AI/ML, Sustainability, Full-Stack Development |
| **Platform** | Infosys Springboard |
| **Duration** | 8 Weeks |
| **Author** | Manikanta Pudi |
| **Live Demo** | [https://ecopackai-q982.onrender.com/](https://ecopackai-q982.onrender.com/) |

---

## 📄 License

This project is developed as part of an educational internship program at Infosys Springboard.

---

## 🙏 Acknowledgments

- Infosys Springboard for the internship opportunity
- Open source community for the amazing tools and libraries
- Environmental research papers for sustainability metrics

---

<p align="center">
  <b>Built with 💚 for a sustainable future</b>
</p>