
# 🌍 EcoPackAI Full-Stack Deployment Report

## 1. System Architecture

EcoPackAI is a **full-stack web application** designed to recommend sustainable packaging solutions.

### **Tech Stack**
*   **Frontend**: HTML5, CSS3 (Modern Dark/Light Theme), Vanilla JavaScript, Bootstrap 5.
*   **Backend**: Flask (Python) following the Application Factory pattern.
*   **Database**: PostgreSQL (Relational Data Store).
*   **AI/ML**: Scikit-learn (Random Forest), XGBoost (Gradient Boosting) for cost/CO₂ prediction.
*   **Deployment**: Render (Cloud Platform).

### **High-Level Flow Code**
1.  **User Input** (Category, Weight, Fragility, Water Resistance) -> **Frontend (JS)**
2.  **API Request** (`POST /api/recommend`) -> **Flask Backend**
3.  **Data Retrieval**: Backend queries **PostgreSQL** for candidate materials.
    *   *Logic*: Filters by Category & Weight Capacity first.
    *   *Fallback*: If no category match, searches broader inventory.
4.  **AI Prediction**:
    *   `Cost Predictor Model` -> Estimates Cost.
    *   `CO2 Predictor Model` -> Estimates Emission Score.
5.  **Ranking**: A composite score (Cost Efficiency + Eco Impact) is calculated.
6.  **Response**: JSON data sent back to Frontend -> **Rendered in Table**.

---

## 2. Database Design

The system uses a centralized PostgreSQL database `ecopackai_db`.

### **Tables**
1.  `materials` (Raw Data):
    *   `material_id` (PK), `material_type`, `strength`, `weight_capacity_kg`, `water_resistance`, `manufacturing_place`.
2.  `product_material` (Mapping):
    *   Maps materials to specific product categories (e.g., "Corrugated Box" -> "Electronics").
3.  `features_engineering` (Analytics & ML):
    *   Pre-computed metrics used for fast API retrieval.
    *   Columns: `co2_emission_score`, `biodegradability_score`, `recyclability_percent`, `cost_per_unit_inr`.

---

## 3. Machine Learning Workflow

The recommendation engine is a hybrid of **Rule-Based Filtering** and **ML Scoring**.

### **Models**
1.  **Cost Predictor (`cost_predictor_model.pkl`)**:
    *   Algorithm: Random Forest Regressor.
    *   Inputs: Strength, Weight Capacity, Material Type (Encoded).
    *   Output: Estimated Cost (INR).
2.  **CO₂ Predictor (`co2_predictor_model.pkl`)**:
    *   Algorithm: XGBoost Regressor.
    *   Inputs: Transport Distance (proxy), Manufacturing Method, Recyclability.
    *   Output: CO₂ Impact Score.

### **Pipeline**
*   **Training**: Notebooks in `notebooks/` trained models on historical packaging data.
*   **Inference**: Models are loaded into memory on server start (`MLService`).
*   **Real-time Scoring**: Every recommendation request triggers live predictions for candidate materials.

---

## 4. API Endpoints

### **1. Get Recommendations**
*   **URL**: `/api/recommend`
*   **Method**: `POST`
*   **Payload**:
    ```json
    {
      "product_category": "Electronics",
      "weight_kg": 2.5,
      "fragility": "High",
      "water_resistant": true
    }
    ```
*   **Response**: List of ranked materials with scores, cost, and origin.

### **2. Analytics Data**
*   **URL**: `/api/analytics/data`
*   **Method**: `GET`
*   **Response**: Aggregated data for dashboard charts (CO₂ avg, Category counts).

---

## 5. Deployment Guide (Render)

### **Prerequisites**
*   GitHub Repository with this code.
*   Render Account.

### **Step 1: Database Setup**
1.  Create a **New PostgreSQL** on Render.
2.  Name: `ecopackai-db`.
3.  Copy the **Internal Database URL**.

### **Step 2: Web Service Setup**
1.  Create a **New Web Service** connected to your GitHub repo.
2.  **Runtime**: Python 3.
3.  **Build Command**: `pip install -r requirements.txt`.
4.  **Start Command**: `gunicorn wsgi:app`.
5.  **Environment Variables**:
    *   `DATABASE_URL`: *[Paste Internal DB URL here]*
    *   `FLASK_ENV`: `prod`
    *   `PYTHON_VERSION`: `3.10.0` (ensure this matches your dev env roughly)

### **Step 3: Data Seeding**
Since the cloud DB starts empty, you must upload data.
*   *Option A*: Connect to remote DB from local machine using `upload_db.py` (requires External DB URL).
*   *Option B*: Add a build script command `python data/upload_db.py` (ensure CSVs are in repo).

---

## 6. User Instructions

1.  **Home Page**:
    *   Select a **Category** (e.g., Food).
    *   Enter **Weight** (e.g., 1.5 kg).
    *   Toggle **Water Resistance** if needed.
    *   Click **Get Recommendations**.
2.  **Dashboard**:
    *   Click "Analytics Dashboard" in the navbar.
    *   View charts for Sustainability Scores and Cost Analysis.
3.  **Theme**:
    *   Toggle between 🌙 Dark and ☀️ Light mode using the icon in the top right.

---

## 7. Demo Explanation (For Presentation)

"Good morning. This is EcoPackAI.
In a world fighting plastic waste, businesses struggle to match their products with eco-friendly packaging.

Our solution is a **Full-Stack AI System**.
1.  **The Database** holds a rich inventory of materials like Mushroom Packaging and Recycled Cardboard.
2.  **The AI Engine** predicts the real-world cost and carbon footprint dynamically.
3.  **The Interface** is seamless—let's demonstrate.

*   *Scenario*: I'm shipping 'Perishable Food'. I need it 'Water Resistant'.
*   *Action*: I select the options. The system filters standard boxes but finds they aren't waterproof.
*   *Intelligence*: It auto-switches to a broader search and recommends 'Bio-plastic' or 'Waxed Carton', showing me the exact carbon score.

This system empowers decision-makers to choose green alternatives without sacrificing utility."
