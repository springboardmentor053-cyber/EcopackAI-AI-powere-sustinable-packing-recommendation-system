import pandas as pd
import psycopg2
import numpy as np
import os

# Database connection
conn = psycopg2.connect(
    host="localhost",
    database="ecopackai",
    user="postgres",
    password="Manikanta@3",
    port="5432"
)

# Load data
materials_df = pd.read_sql("SELECT * FROM materials", conn)
categories_df = pd.read_sql("SELECT * FROM product_categories", conn)

# Load engineered features
engineered_df = pd.read_csv('E:/Data Science/EcoPackAI/data/processed/materials_engineered.csv')

# Merge engineered features with materials
materials_df = materials_df.merge(
    engineered_df[['material_id', 'co2_impact_index', 'cost_efficiency_index', 'eco_score']],
    on='material_id'
)

print(f"Materials: {len(materials_df)}")
print(f"Categories: {len(categories_df)}")

# Weight variations for each category (relative to typical_weight)
weight_multipliers = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]

# Packaging factor: packaging weight is ~15% of product weight on average
PACKAGING_FACTOR = 0.15

# ============ GENERATE TRAINING DATA ============

training_data = []

for _, category in categories_df.iterrows():
    for _, material in materials_df.iterrows():
        for multiplier in weight_multipliers:
            
            # Calculate actual weight for this sample
            product_weight = category['typical_weight_kg'] * multiplier
            
            # ----- CALCULATE SUITABILITY SCORE -----
            # Base score starts at 0.5 (neutral)
            suitability_score = 0.5
            
            # Factor 1: Cushioning requirement
            # If category requires cushioning, reward high strength_score
            if category['requires_cushioning']:
                suitability_score += material['strength_score'] * 0.2  # +0 to +0.2
            else:
                suitability_score += 0.1  # Small bonus if cushioning not needed
            
            # Factor 2: Moisture sensitivity
            # If category is moisture sensitive, reward high moisture_resistance
            if category['moisture_sensitive']:
                suitability_score += material['moisture_resistance'] * 0.15  # +0 to +0.15
            else:
                suitability_score += 0.075  # Small bonus if moisture not a concern
            
            # Factor 3: Fragility level
            # High fragility needs high strength, low fragility is flexible
            fragility_map = {'high': 1.0, 'medium': 0.5, 'low': 0.2}
            fragility_value = fragility_map.get(category['fragility_level'], 0.5)
            # Reward strength for fragile items
            suitability_score += (material['strength_score'] * fragility_value) * 0.15  # +0 to +0.15
            
            # Factor 4: Weight capacity check
            # Material must be able to handle the product weight
            if material['weight_capacity_kg'] >= product_weight:
                # Bonus based on how much headroom we have (but not too much - waste)
                capacity_ratio = product_weight / material['weight_capacity_kg']
                if capacity_ratio >= 0.5:  # Good utilization (50-100%)
                    suitability_score += 0.1
                else:  # Over-engineered (using heavy-duty for light items)
                    suitability_score += 0.05
            else:
                # Penalty: material can't handle the weight
                suitability_score -= 0.3
            
            # Factor 5: Eco bonus (prefer sustainable materials)
            suitability_score += material['eco_score'] * 0.1  # +0 to +0.1
            
            # Clamp to 0-1 range
            suitability_score = max(0, min(1, suitability_score))
            
            # ----- CALCULATE PREDICTED CO2 -----
            # CO2 = material_co2_emission_kg × product_weight × packaging_factor
            # packaging_factor accounts for packaging being ~15% of product weight
            packaging_weight = product_weight * PACKAGING_FACTOR
            predicted_co2 = material['co2_emission_kg'] * packaging_weight
            
            # ----- CALCULATE PREDICTED COST -----
            # Cost = material_cost_per_kg × packaging_weight
            predicted_cost = material['cost_per_kg'] * packaging_weight
            
            # Create training row
            row = {
                # Category features
                'category_id': category['category_id'],
                'category_name': category['category_name'],
                'fragility_level': category['fragility_level'],
                'requires_cushioning': category['requires_cushioning'],
                'moisture_sensitive': category['moisture_sensitive'],
                'temperature_sensitive': category['temperature_sensitive'],
                
                # Product features
                'product_weight_kg': product_weight,
                
                # Material features
                'material_id': material['material_id'],
                'material_name': material['material_name'],
                'material_type': material['material_type'],
                'strength_score': material['strength_score'],
                'weight_capacity_kg': material['weight_capacity_kg'],
                'biodegradability_score': material['biodegradability_score'],
                'moisture_resistance': material['moisture_resistance'],
                'co2_emission_kg': material['co2_emission_kg'],
                'cost_per_kg': material['cost_per_kg'],
                
                # Engineered features
                'co2_impact_index': material['co2_impact_index'],
                'cost_efficiency_index': material['cost_efficiency_index'],
                'eco_score': material['eco_score'],
                
                # TARGET VALUES
                'suitability_score': round(suitability_score, 4),
                'predicted_co2': round(predicted_co2, 4),
                'predicted_cost': round(predicted_cost, 2)
            }
            
            training_data.append(row)

# Create DataFrame
training_df = pd.DataFrame(training_data)

print(f"\nTotal training samples: {len(training_df)}")
print(f"Expected: {len(categories_df)} categories × {len(materials_df)} materials × {len(weight_multipliers)} weights = {len(categories_df) * len(materials_df) * len(weight_multipliers)}")

# ============ DATA SUMMARY ============
print("\n" + "=" * 70)
print("TRAINING DATA SUMMARY")
print("=" * 70)

print("\nSuitability Score Distribution:")
print(f"  Min: {training_df['suitability_score'].min():.3f}")
print(f"  Max: {training_df['suitability_score'].max():.3f}")
print(f"  Mean: {training_df['suitability_score'].mean():.3f}")

print("\nPredicted CO2 Distribution:")
print(f"  Min: {training_df['predicted_co2'].min():.3f} kg")
print(f"  Max: {training_df['predicted_co2'].max():.3f} kg")
print(f"  Mean: {training_df['predicted_co2'].mean():.3f} kg")

print("\nPredicted Cost Distribution:")
print(f"  Min: ₹{training_df['predicted_cost'].min():.2f}")
print(f"  Max: ₹{training_df['predicted_cost'].max():.2f}")
print(f"  Mean: ₹{training_df['predicted_cost'].mean():.2f}")

# Top 5 most suitable material-category combinations
print("\n" + "=" * 70)
print("TOP 10 MATERIAL-CATEGORY COMBINATIONS (by suitability):")
print("=" * 70)
top_combos = training_df.nlargest(10, 'suitability_score')[
    ['category_name', 'material_name', 'product_weight_kg', 'suitability_score', 'predicted_co2', 'predicted_cost']
]
print(top_combos.to_string(index=False))

# Save to CSV
os.makedirs('E:/Data Science/EcoPackAI/data/processed', exist_ok=True)
training_df.to_csv('E:/Data Science/EcoPackAI/data/processed/ml_training_data.csv', index=False)

print(f"\n✓ Saved to: data/processed/ml_training_data.csv")
print(f"✓ Total columns: {len(training_df.columns)}")
print(f"✓ Total rows: {len(training_df)}")

conn.close()