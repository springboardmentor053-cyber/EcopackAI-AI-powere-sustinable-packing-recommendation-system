# EcopackAI - AI-Powered Sustainable Packaging Recommendation System

**Overview**

EcoPackAI is an AI-powered sustainable packaging recommendation system that helps businesses select eco-friendly packaging materials based on product attributes, sustainability parameters, and industry standards. The platform analyzes factors such as product type, weight, and fragility to deliver data-driven packaging recommendations that balance environmental impact, functionality, and efficiency.


**Features**

1. AI-driven sustainable packaging recommendations.

2. Matching product requirements with material properties using structured scorings.

3. Evaluation of strength, weight, barrier, and environmental impact.

4. Sustainability-focused analysis including biodegradability, CO₂ emissions, and recyclability.
   
5. Support for multiple industry sectors such as food, electronics, cosmetics, and pharmaceuticals.

6. PostgreSQL-backed structured data management.

7. Scalable and extensible full-stack design.
   

**Project Workflow**

***Dataset :*** The EcoPackAI dataset consists of two tables: Material and Product.

   The Material table stores packaging material properties such as strength, weight capacity, biodegradability, CO₂ emissions, and recyclability.

   The Product table captures product packaging requirements including sector, strength, weight capacity, barrier needs, sustainability scores, cost, and reuse potential.

   These tables together enable data-driven sustainable packaging recommendations.

***Database schema :***  EcoPackAI uses a PostgreSQL database with two core tables:

   material – Stores packaging material properties including strength, weight capacity, biodegradability, CO₂ emission score, and recyclability.

   product – Stores product packaging requirements such as sector, strength, weight capacity, barrier needs, sustainability preferences, cost sensitivity, and reuse potential.

   The schema supports efficient matching between product requirements and material capabilities for sustainable packaging recommendations.

***Data Cleaning :*** Missing values are handled, numerical scores are standardized, duplicates are removed, and data types are validated to ensure accurate and reliable recommendations.

***Feature Engineering :***  Created indices like CO₂ Impact, Cost Efficiency, and Material Suitability to measure environmental impact, cost, and compatibility.

### Database
- PostgreSQL

### Tools & Platforms
- Git & GitHub
- Jupyter Notebook
- VS Code
