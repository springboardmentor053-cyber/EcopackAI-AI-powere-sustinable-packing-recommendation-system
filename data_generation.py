import pandas as pd
import numpy as np

def generate_datasets():
    np.random.seed(42)  # reproducibility

    # Material types and product categories
    material_types = [
        "Corrugated Cardboard", "Molded Pulp", "Biodegradable Plastic",
        "Recycled Paper", "Plant Fiber", "Starch-based Plastic"
    ]
    product_categories = ["Electronics", "Food", "Cosmetics", "Clothing", "Furniture"]

    # Generate materials dataset with **logical numeric ranges**
    materials_data = {
        "material_id": np.arange(1, 81),
        "material_type": np.random.choice(material_types, 80),
        "strength": np.round(np.random.uniform(5, 10, 80), 2),             # 5-10 realistic
        "weight_capacity": np.round(np.random.uniform(5, 25, 80), 2),       # 5-25 kg
        "cost_per_unit": np.round(np.random.uniform(10, 50, 80), 2),        # cost units
        "biodegradability_score": np.round(np.random.uniform(5, 10, 80), 2),# 1-10
        "co2_emission_score": np.round(np.random.uniform(1, 5, 80), 2),    # >0
        "recyclability_percentage": np.round(np.random.uniform(50, 100, 80), 2), # %
        "product_category": np.random.choice(product_categories, 80)
    }

    df_materials = pd.DataFrame(materials_data)

    # Product dataset
    fragility_levels = ["Low", "Medium", "High"]
    shipping_types = ["Air", "Sea", "Road"]

    products_data = {
        "product_id": np.arange(1, 81),
        "product_name": ["Product_" + str(i) for i in range(1, 81)],
        "product_category": np.random.choice(product_categories, 80),
        "fragility_level": np.random.choice(fragility_levels, 80),
        "shipping_type": np.random.choice(shipping_types, 80)
    }

    df_products = pd.DataFrame(products_data)

    return df_materials, df_products

