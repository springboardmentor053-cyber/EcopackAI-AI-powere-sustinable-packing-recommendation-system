# 🌿 EcoPackAI: AI-Powered Sustainable Packaging Recommendation System

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10-blue)
![Flask](https://img.shields.io/badge/flask-2.2-lightgrey)
![Status](https://img.shields.io/badge/status-deployment--ready-success)

EcoPackAI is an intelligent web application designed to help businesses transition to sustainable packaging. By leveraging Machine Learning (Random Forest & XGBoost), the system analyzes product requirements (weight, category, fragility) and recommends optimal packaging materials that balance **Cost Efficiency** with **Environmental Impact (CO₂)**.

---

## 🚀 Key Features

*   **🌱 AI-Driven Recommendations**: Predicts cost and carbon footprint for materials dynamically.
*   **📊 Interactive BI Dashboard**: Real-time analytics on material usage, CO₂ reduction, and sustainability scores.
*   **🎨 Premium UI**: Modern, glassmorphism-inspired design with Dark/Light mode support.
*   **☁️ Cloud Ready**: Configured for seamless deployment on Render/Heroku.
*   **📱 Responsive**: Fully optimized for desktop and mobile devices.

---

## 📸 Screenshots

### 1. Landing Page
*A modern, eco-friendly entry point guiding users to sustainability.*
![Landing Page](docs/landing_page_mockup.png)

### 2. Recommendation Engine
*Input product details and get ranked, AI-scored suggestions.*
![Recommendations](docs/recommendation_results_mockup.png)

### 3. Analytics Dashboard
*Visualize your environmental impact and cost savings.*
![Dashboard](docs/dashboard_analytics_mockup.png)

*(Note: Please ensure the images from the 'artifacts' folder are moved to a `docs/` folder in your repository to verify these links.)*

---

## 🛠️ System Architecture

### Technology Stack
*   **Frontend**: HTML5, CSS3 (Custom Design System), JavaScript (ES6+), Bootstrap 5, Plotly.js.
*   **Backend**: Flask (Python Application Factory Pattern).
*   **Database**: PostgreSQL (Relational Data Store).
*   **Machine Learning**: Scikit-Learn (Cost Model), XGBoost (CO₂ Model).

### Application Flow
1.  **User Input**: User provides product metadata (Category: *Electronics*, Weight: *2.5kg*, etc.).
2.  **Constraint Filtering**: System filters materials by physical capabilities (Strength, Weight Capacity).
3.  **ML Inference**:
    *   `Cost Model` predicts the market cost per unit.
    *   `CO₂ Model` predicts the environmental impact score.
4.  **Ranking Algorithm**: Calculates a composite `Sustainability Score` based on customizable weights (50% Eco / 50% Cost).
5.  **Visualization**: Results are presented with "Suitability Badges" and detailed metrics.

---

## 💻 Installation & Setup

### Prerequisites
*   Python 3.8+
*   PostgreSQL installed and running
*   Git

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/EcoPackAI.git
cd EcoPackAI
```

### 2. Virtual Environment
```bash
# Windows
python -m venv env
.\env\Scripts\activate

# Mac/Linux
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
Ensure PostgreSQL is running. Create a database named `ecopackai_db`.
Then, create a `.env_db` file in the root directory:
```
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecopackai_db
```

Run the initialization scripts:
```bash
# Upload initial data
python data/upload_db.py

# Generate engineering features
python database/feature_eng.py
```

### 5. Run Locally
```bash
python wsgi.py
```
Visit `http://localhost:5000` in your browser.

---

## ☁️ Deployment (Render/Heroku)

This project is configured for **Render**.

1.  **New Web Service**: Connect your GitHub repo.
2.  **Runtime**: Python 3.
3.  **Build Command**: `pip install -r requirements.txt`
4.  **Start Command**: `gunicorn wsgi:app`
5.  **Environment Variables**:
    *   Set `DATABASE_URL` to your Render PostgreSQL Internal URL.
    *   Set `FLASK_ENV` to `prod`.

---

## 📂 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── routes/      # API Blueprints (main, analytics, api)
│   │   ├── services/    # Business Logic & DB Interactions
│   │   ├── static/      # CSS, JS, Images
│   │   └── templates/   # HTML Files
│   ├── recommendation_engine.py  # ML Logic
│   └── config.py        # App Configuration
├── data/                # CSV Datasets & Upload Scripts
├── database/            # Feature Engineering & Test Scripts
├── models/              # Trained .pkl Models
├── notebooks/           # Jupyter Notebooks for Training
├── Procfile             # Deployment Instruction
├── requirements.txt     # Python Dependencies
└── wsgi.py              # Entry Point
```

---

## 📜 License
This project is licensed under the MIT License.
