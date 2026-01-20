🌱 EcoPackAI
AI Framework for Sustainable Packaging Design and Material Optimization

📌 Project Overview

EcoPackAI is an AI-driven system designed to recommend sustainable packaging materials based on product requirements, cost constraints, and environmental impact.
The project integrates data engineering, machine learning, and intelligent scoring logic to support eco-friendly and cost-effective packaging decisions.

This repository documents the implementation from Module 1 to Module 4, covering dataset preparation, feature engineering, machine learning models, and AI-based recommendation logic.


📘 Module 1: Dataset Creation & Understanding
Objective

To create a structured dataset representing packaging materials and their sustainability-related properties.

Key Activities
->Identified relevant packaging attributes:

1.Material strength
2.Weight capacity
3.Biodegradability
4.Recyclability
5.CO₂ emission impact
6.Cost per unit

->Created a CSV-based dataset for packaging materials.

->Ensured data consistency and real-world relevance.

Output

materials_dataset.csv

Clear understanding of material properties and sustainability metrics.

📘 Module 2: Data Cleaning & Feature Engineering
Objective

To prepare raw data for machine learning by cleaning, transforming, and normalizing features.

Key Activities

1.Handled missing and inconsistent values.
2.Converted categorical values (e.g., strength levels) into numerical format.
3.Normalized numeric attributes using scaling techniques.
4.Created engineered features such as:
    1.Durability score
    2.Material suitability score

Techniques Used
1.Pandas for data processing
2.Scikit-learn scalers for normalization

Output
1.Cleaned and feature-engineered dataset
2.materials_module2_final.csv

📘 Module 3: Machine Learning Preparation
Objective

To prepare the dataset for predictive modeling.

Key Activities
1.Selected relevant features for model training.
2.Split dataset into training and testing sets.
3.Applied feature scaling for model stability.
4.Prepared input matrices (X) and target variables (y).

Models Prepared For
1.Cost prediction
2.CO₂ emission prediction

Output
1.Scaled feature sets
2.Train-test datasets
3.Ready-to-train ML pipeline

📘 Module 4: AI Recommendation Logic
Objective

To design an AI-based recommendation mechanism that ranks packaging materials based on sustainability and cost criteria.

Key Activities
1.Integrated ML model outputs with material-level attributes.
2.Designed a composite AI recommendation score using:
    1.Material suitability
    2.Predicted environmental impact
    3.Cost efficiency
3.Ranked materials dynamically based on user/product requirements.

Core Outcome
1.Intelligent ranking of packaging materials.
2.Foundation for API-based and frontend-based recommendations.

📘 Module 5: Backend API Development
Objective
To expose AI recommendation logic through a backend service.

Key Activities
1.Developed a Flask-based REST API.
2.Loaded trained ML models for prediction.
3.Designed /recommend endpoint to:
    1.Accept structured JSON input
    2.Predict CO₂ impact
    3.Calculate total cost based on quantity
    4.Generate ranked material recommendations
4.Enabled cross-origin requests using CORS.
5.Tested API using Thunder Client/Postman.

Outcome
1.Fully functional backend API
2.Scalable and frontend-ready architecture

📘 Module 6: Frontend UI & Dashboard
Objective

To build a professional, interactive user interface for EcoPackAI.

->Technologies Used
1.HTML
2.CSS 
3.JavaScript
4.Bootstrap
5.Chart.js

Key Features
1.Dark-themed dashboard UI
2.Input form for product parameters:
    1.Product name
    2.Quantity
    3.Strength
    4.Sustainability preferences
3.Real-time API integration using fetch()
4.Dynamic visualization of results:
    1.Top recommended material
    2.Total cost
    3.AI score
    4.Ranked materials table
    5.Cost comparison chart
    6.AI score comparison chart

User Experience Enhancements
1.Responsive layout
2.Dashboard-style presentation
3.Graphical insights for decision-making

Outcome
1.End-to-end interaction between frontend and backend
2.Clear visualization of AI-driven recommendations