import pandas as pd
from sqlalchemy import create_engine


engine = create_engine(
    "postgresql+psycopg2://postgres:1234@localhost:5432/ecopackai"
)


products = pd.read_sql("SELECT * FROM products", engine)
materials = pd.read_sql("SELECT * FROM materials", engine)


text_cols_products = [
    "product_name", "product_category", "fragility_level",
    "moisture_sensitivity", "temperature_sensitivity",
    "food_grade_required", "shape_type", "value_category"
]

for col in text_cols_products:
    products[col] = products[col].str.strip().str.lower()


products["food_grade_required"] = products["food_grade_required"].map({
    "yes": True,
    "no": False
})


products = products[
    (products["weight_kg"] > 0) &
    (products["shelf_life_days"] > 0)
]


text_cols_materials = [
    "material_name", "material_type", "flexibility"
]

for col in text_cols_materials:
    materials[col] = materials[col].str.strip().str.lower()


materials["biodegradability_score"] = materials["biodegradability_score"].clip(0, 100)
materials["recyclability_percent"] = materials["recyclability_percent"].clip(0, 100)



products.to_csv("clean_products.csv", index=False)
materials.to_csv("clean_materials.csv", index=False)

print("✅ Data cleaned successfully")
print("📁 Files saved: clean_products.csv, clean_materials.csv")
