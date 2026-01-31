# 📦 EcoPackAI: AI-Powered Sustainable Packaging Recommendation System

## 📘 Introduction

**EcoPackAI** is a data-driven system designed to optimize packaging material choices by balancing environmental sustainability, cost-efficiency, and material suitability. In contrast to traditional heuristic-based approaches, EcoPackAI leverages structured data, engineered features, and composite scoring to recommend the most effective and eco-friendly packaging materials for diverse products.

---


## 🎯 Project Objectives

- Design a validated, production-ready relational database
- Engineer sustainability and cost-related features
- Compute composite indices:
  - CO₂ Impact Index
  - Cost Efficiency Index
  - Material Suitability Score
- Enable future ML model and dashboard integration
- Maintain real-world alignment and scalability

---

## 🧱 System Architecture Overview

The pipeline is modular and production-focused:

1. Raw data ingestion (CSV → PostgreSQL)
2. Schema validation & referential integrity checks
3. Data validation & cleaning
4. Feature engineering & scoring
5. Recommendation logic (planned)
6. Dashboard visualization (Tableau / Power BI)

---

## 🗃️ Database Design

- **Database:** PostgreSQL  
- **Name:** `ecopack_ai`

Key principles:
- Schema enforcement
- Data integrity via constraints and foreign keys
- Clean joins and production-grade readiness

---

## 📋 Table Schema Design

### 🔹 `materials` Table

Stores physical, environmental, and economic attributes of packaging materials.

- **Primary Key:** `material_id`
- **Columns:**
  - `material_type`
  - `strength_mpa`
  - `weight_capacity`
  - `co2_emission_per_kg`
  - `biodegradability_score`
  - `recyclability_pct`
  - `cost_inr_per_kg`
  - `material_category`

**Constraints:**
- Numeric range checks
- Binary biodegradability
- Recyclability: 0–100
- Unique material identifiers

---

### 🔹 `products` Table

Captures product-specific packaging needs.

- **Primary Key:** `product_id`
- **Foreign Key:** `current_packaging_material → materials.material_type`
- **Columns:**
  - `product_name`
  - `product_category`
  - `product_weight_g`
  - `product_volume_cm3`
  - `price_inr`
  - `fragility_level` (Low/Medium/High)
  - `temperature_sensitivity` (Low/Medium/High)
  - `moisture_sensitivity` (Low/Medium/High)
  - `shelf_life_days`
  - `packaging_format`

**Constraints:**
- Categorical value control
- Positive numeric enforcement
- Referential integrity

---

## 🧩 Entity-Relationship (ER) Diagram

![ER Diagram](screenshots/er_diagram.png)

**Relationship:**
- One material → many products  
- Each product uses one material  
**Type:** One-to-Many (1:N)

This ensures minimal redundancy and scalable recommendations.

---

## 🔄 Data Engineering Process

### 📂 Data Sources

- Material properties inspired by real-world data
- Product attributes aligned with market categories

### 📈 Data Flow

- CSV ingestion → PostgreSQL via `COPY`
- Schema and referential checks at DB level
- Exported for Python-based processing

---

## ✅ Data Validation

Performed prior to transformation to ensure raw data quality:

- Row & column shape checks
- Type verification
- Null & duplicate checks (0 found)
- Range sanity checks
- Foreign key validation

**Result:** Passed all checks and marked ready for cleaning.

---

## 🧹 Data Cleaning

Focused on preserving integrity while correcting inconsistencies.

### Cleaning Steps:

- String normalization (trim, case)
- Type enforcement
- Categorical constraints
- Logical range checks
- Outlier flagging (1%–99%)

### Outlier Handling:

Outliers were **flagged, not removed** using:
- `flag_weight_outlier`
- `flag_volume_outlier`
- `flag_price_outlier`

---

## 🛠️ Feature Engineering

### Key Engineered Features:

- **Strength Level:** Categorized from `strength_mpa` (Low/Med/High)
- **Emission Score:** Inverted, normalized CO₂ emissions
- **Recyclability Index:** `recyclability_pct / 100`
- **CO₂ Impact Index:** Weighted score from emission, recyclability, biodegradability
- **Cost Efficiency Index:** Inverse cost × normalized strength
- **Material Suitability Score:** Composite of all indices for final ranking

These metrics enable objective, scalable recommendations.

---

## 📁 Project Folder Structure

```bash
EcoPackAI/
│
├── data/
│   ├── raw/
│   │   ├── materials.csv              # Original materials dataset
│   │   └── products.csv               # Original products dataset 
│   │
│   └── processed/
│       ├── materials_cleaned.csv      # Cleaned materials dataset
│       ├── products_cleaned.csv       # Cleaned products dataset
│       └── materials_featured.csv     # Featured dataset
│
├── notebooks/
│   ├── 01_data_validation.ipynb        # Sanity checks, schema validation
│   ├── 02_data_cleaning.ipynb          # Cleaning, unit fixes, encoding prep
│   ├── 03_feature_engineering.ipynb    # CO₂, cost, suitability Indexes
│   └── 04_summary_validation.ipynb     # Post-FE stats & checks
│
├── models/
│   ├── baseline/                       # Baseline ML models 
│
├── src/
│   ├── pipelines/
│   │   ├── __init__.py
│   │   ├── data_preprocessing.py       # Reusable cleaning logic
│   │   ├── feature_engineering.py      # Index calculations
│   │   └── model_training.py           # Recommendation / ML logic
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── recommend.py                # Packaging recommendation API
│   │
│   └── utils/
│       ├── constants.py                # Category lists, mappings, weights
│       └── validators.py               # Data validation helpers
│
├── sql/
│   └── EcoPackAI_Database.sql          # PostgreSQL schema (materials + products)
├── screenshots/
├── dashboard/
│   ├── EcoPackAI_Dashboard.twbx        # Tableau OR Power BI file
│   └── screenshots/                    # Dashboard images for README
│
├── app.py                              # Flask app entry point
├── requirements.txt
├── .gitignore
├── README.md
└── deployment/                         # Render / Heroku configs



```

---

## 📊 Dataset

EcoPackAI is trained on an **engineered materials dataset** that contains physical, sustainability, and economic attributes for packaging materials.

The ML layer is designed to be **material-centric**, meaning it predicts outcomes for materials directly rather than relying on product IDs or product tables.

---

## 🧩 ML Features

The model uses a compact, decision-oriented feature set aligned with real packaging trade-offs:

- **`strength_encoded`**  
  Encoded strength requirement (e.g., Low/Medium/High mapped to ordinal values)

- **`weight_capacity`**  
  Load-bearing capability used to ensure feasibility for shipping/handling needs

- **`biodegradability_score`**  
  Sustainability measure representing how biodegradable the material is

- **`recyclability_pct`**  
  Recyclability percentage used as a circular-economy indicator

- **`cost_efficiency_index`**  
  Engineered score representing cost-performance preference for decision-making

All features are numeric and ML-ready after preprocessing. This feature set is intentionally kept small to remain explainable and stable on a limited dataset.

---

## 🎯 Prediction Targets

EcoPackAI models two independent numeric targets:

- **Cost Prediction**  
  A continuous cost value (e.g., cost per unit mass / cost score depending on dataset)

- **CO₂ Impact Prediction**  
  A continuous environmental impact value (e.g., CO₂ footprint / emission score depending on dataset)

Targets are trained separately to keep predictions interpretable and to reflect that cost and CO₂ are influenced differently.

---

## 🔄 Modeling Pipeline

A reproducible pipeline is used to ensure consistency between training and inference:

- Train/test split
- Preprocessing pipeline (scaling / transformations)
- Model training (two independent regressors)
- Evaluation on held-out test data
- Saving artifacts for reuse in APIs/UI workflows

### 📈 Evaluation Metrics

- **MAE (Mean Absolute Error)** – average magnitude of prediction error  
- **RMSE (Root Mean Squared Error)** – penalizes larger errors more strongly  
- **R² Score (Coefficient of Determination)** – explained variance (interpreted cautiously for small datasets)

---

## 🤖 Machine Learning Models

EcoPackAI trains two baseline models:

### 1) Random Forest Regressor — Cost Prediction
- Robust for non-linear relationships
- Stable on small structured datasets
- Low tuning overhead for a reliable baseline

### 2) XGBoost Regressor — CO₂ Impact Prediction
- Strong for complex patterns and noisy targets
- Boosting learns residual errors iteratively
- Regularization helps generalization

Hyperparameters are kept near standard defaults to prioritize reproducibility and reduce overfitting risk.

---

## 🏆 From Predictions to Recommendations

Model outputs are converted into actionable recommendations:

1. Predict cost and CO₂ impact for candidate materials
2. Rank materials based on:
   - lower predicted cost
   - lower predicted CO₂ impact
3. Combine rankings into a suitability score to recommend top materials

This approach avoids rigid thresholds and supports real-world trade-offs.

---

## 🧠 Design Considerations & Limitations

- The current dataset is small, so the focus is on building a **correct end-to-end ML workflow**
- Model performance metrics are informative but not treated as production-grade benchmarks
- The system is structured to scale naturally as more materials data becomes available

Future improvements can include:
- larger datasets
- more detailed lifecycle CO₂ information
- user-controlled weighting between cost vs sustainability 

---

## ✅ Current Status

EcoPackAI currently includes:

- ✅ engineered ML-ready dataset for materials  
- ✅ preprocessing + training pipeline  
- ✅ cost prediction model (Random Forest)  
- ✅ CO₂ prediction model (XGBoost)  
- ✅ ranking-based recommendation logic  
- ✅ artifacts saved for backend/frontend integration  
Done

---