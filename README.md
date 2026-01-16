# EcoPackAI - AI-Powered Sustainable Packaging Recommender

EcoPackAI is an intelligent system designed to recommend sustainable packaging materials based on product specifications (category, weight, fragility). It balances cost efficiency with environmental impact (CO₂ emissions) to help businesses make greener choices.

## 🚀 Features implemented

### 1. Data & Database
*   **PostgreSQL Integration**: Centralized database (`ecopackai_db`) storing material properties, product categories, and engineered features.
*   **Feature Engineering**: Automated Python scripts to calculate metrics like `sustainability_score`, `co2_impact_index`, and `cost_efficiency_index`.

### 2. Machine Learning
*   **Predictive Models**:
    *   **Cost Predictor**: Random Forest Regressor to estimate `cost_per_unit_inr`.
    *   **CO₂ Predictor**: XGBoost Regressor to estimate `co2_emission_score`.
*   **Recommendation Engine**: A hybrid ranking system that filters candidates by weight capacity and scores them based on a weighted average of cost and eco-impact.

### 3. Backend (Flask API)
*   **Modular Architecture**: Clean separation of routes, services, and configuration.
*   **REST API**:
    *   `POST /api/recommend`: Core endpoint receiving product details and returning ranked material recommendations.
    *   `GET /api/health`: System health check.
*   **Services**:
    *   `MLService`: Handles model loading and real-time predictions.
    *   `AnalyticsService`: Aggregates data for business intelligence.

### 4. Frontend & Cashboard
*   **Recommendation UI**: A responsive, dark-themed web interface for users to input product details and view recommendations.
*   **BI Dashboard**: An interactive analytics dashboard (using Plotly.js) visualizing:
    *   Average CO₂ Emissions by Material.
    *   Cost Analysis.
    *   Sustainability Score Distributions.

## 📂 Project Structure

```
Infosys/
├── backend/                # Flask Application
│   ├── app/
│   │   ├── routes/         # API & Web Routes (api.py, analytics.py)
│   │   ├── services/       # Business Logic (ml_service.py, db_service.py)
│   │   ├── templates/      # HTML Templates (index.html, dashboard.html)
│   │   └── __init__.py     # App Factory
│   ├── config.py           # App Configuration
│   └── run.py              # Entry Point
├── data/                   # Raw Data & Upload Scripts
├── database/               # Feature Engineering Scripts
├── models/                 # Trained ML Models (.pkl)
├── notebooks/              # Jupyter Notebooks mainly for Model Training
└── requirements.txt        # Python Dependencies
```

## 🛠️ Setup & Usage

### Prerequisites
*   Python 3.8+
*   PostgreSQL

### Installation
1.  **Activate Virtual Environment**:
    ```bash
    env\Scripts\activate
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Database Setup**:
    Ensure PostgreSQL is running and `upload_db.py` / `feature_eng.py` have been executed to populate the data.

### Running the Application
```bash
python backend/run.py
```
*   **Main Interface**: [http://localhost:5000](http://localhost:5000)
*   **Analytics Dashboard**: [http://localhost:5000/dashboard](http://localhost:5000/dashboard)

## 📡 API Usage Example

**Request:** `POST /api/recommend`
```json
{
    "product_category": "Electronics",
    "weight_kg": 2.5,
    "fragility": "High"
}
```

**Response:**
```json
{
    "product_context": { ... },
    "recommendations": [
        {
            "material_type": "Molded Pulp",
            "final_rank_score": 28.5,
            "predicted_cost_inr": 15.0,
            "predicted_co2_score": 1.2
        },
        ...
    ]
}
```
