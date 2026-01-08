🌱 EcopackAI-powered Sustainable Packaging Recommendations

EcopackAI is a Python-based project that builds a clean and structured data pipeline for sustainable packaging materials.
The system generates, cleans, processes, and stores data into PostgreSQL, forming the foundation for AI-based eco-friendly packaging recommendations.

1️⃣ Objective

The goal of this project is to prepare high-quality, structured datasets for sustainable packaging recommendations using automated data engineering techniques.
This ensures reliable input for future AI models focused on eco-friendly materials.

2️⃣ Datasets

The project uses three main datasets, all stored in PostgreSQL.

📦 Materials Table (materials)
Column	Description
material_id	Unique material identifier
material_type	Type of eco-friendly material
strength	Normalized strength value
weight_capacity	Normalized weight capacity
cost_per_unit	Normalized cost
biodegradability_score	Normalized biodegradability
co2_emission_score	Normalized CO₂ emission
recyclability_percentage	Normalized recyclability
product_category	Target product category
📦 Products Table (products)
Column	Description
product_id	Unique product identifier
product_name	Name of the product
product_category	Category of the product
fragility_level	Low, Medium, or High
shipping_type	Air, Sea, or Road
📦 Material Product Scores Table (material_product_scores)
Column	Description
score_id	Unique score identifier
material_id	Foreign key from materials
product_id	Foreign key from products
material_sustainability_score	Sustainability metric
co2_impact_index	CO₂ impact metric
cost_efficiency_index	Cost efficiency metric
3️⃣ Data Processing Pipeline

✅ Generate datasets for materials and products using Python and NumPy

✅ Clean datasets to remove zeros and missing values

✅ Normalize numeric columns using Min-Max scaling

✅ One-Hot Encode categorical columns

✅ Calculate feature engineering scores (sustainability, CO₂ impact, cost efficiency)

✅ Store the data in PostgreSQL tables

✅ Export datasets as CSV files for analysis

4️⃣ Database

PostgreSQL is used to store all processed data.

Tables created automatically:

materials

products

material_product_scores

5️⃣ Technologies Used

🐍 Python

🐼 Pandas

🔢 NumPy

🗄 PostgreSQL

🔗 SQLAlchemy

🖥 VS Code

6️⃣ Project Structure
EcoPackAI/
├── scripts/
│   ├── main.py
│   ├── data_generation.py
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── db_connection.py
│   ├── config.py
├── data/
│   ├── materials_80rows.csv
│   ├── products_80rows.csv
│   ├── materials_processed_80rows.csv
│   ├── material_product_scores_80rows.csv
└── README.md

7️⃣ How to Run

Open VS Code

Open Terminal and navigate to the scripts folder:

cd EcoPackAI/scripts


Run the main script:

python main.py

8️⃣ Output

💾 CSV datasets generated in the data folder

🗄 PostgreSQL tables created and populated

📊 Dataset ready for machine learning or sustainability analysis

9️⃣ Key Features

⚡ Fully automated data pipeline

📊 Clean and normalized numeric and categorical data

🗄 PostgreSQL integration for structured storage

🌱 Sustainability-focused feature engineering

🔧 Easy to extend for AI-based recommendation systems

🔟 Future Scope

🤖 Develop AI recommendation models for packaging

🌐 Build a web interface for product input

📈 Create dashboards for visualization and analysis

♻️ Expand datasets with additional eco-friendly materials

1️⃣1️⃣ Developer

Reddi Rani

1️⃣2️⃣ Conclusion

EcopackAI provides a robust foundation for sustainable packaging recommendations, combining data engineering, feature engineering, and database management to support eco-friendly and cost-efficient packaging decisions.

