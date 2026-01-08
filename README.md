EcoPackAI – Sustainable Packaging Recommendation System
Project Overview

EcoPackAI is an AI-powered system designed to recommend sustainable packaging materials based on product requirements. The project combines environmental impact metrics, cost constraints, and physical feasibility to support data-driven packaging decisions.


Module 1 – Data Collection & Dataset Preparation
Objective

To create structured, realistic datasets representing packaging materials and products used across different industries.

Key Activities

Designed two datasets:

Materials dataset: strength, biodegradability, CO₂ emission, recyclability, cost, and weight capacity.

Products dataset: product weight, fragility, required strength, cost limits, and temperature sensitivity.

Ensured data values reflect real-world packaging scenarios.

Organized datasets into raw and processed folders.

Imported datasets into PostgreSQL for structured storage and validation.

Outcome

A clean, scalable data foundation ready for analysis and recommendation logic.

Module 2 – Data Cleaning, Feature Engineering & Material Ranking
Objective

To clean and validate the datasets, engineer meaningful features, and rank packaging materials for a selected product.

Key Activities

Loaded datasets using pandas and validated schema and data types.

Performed data cleaning checks:

Missing values

Duplicate records

Value range validation

Selected a target product and extracted packaging requirements.

Applied rule-based filtering to shortlist feasible materials.

Engineered sustainability and cost-related features such as:

CO₂ score

Cost score

Sustainability score

Final material suitability score

Ranked materials based on the engineered suitability score.

Modularized feature engineering logic into a reusable Python module.

Outcome

A ranked list of sustainable packaging materials tailored to product requirements, forming a strong foundation for machine learning in future modules.