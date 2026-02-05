import pandas as pd
import psycopg2
import os

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="ecopackai",
    user="postgres",
    password="Manikanta@3",
    port="5432"
)

# Load materials data
df = pd.read_sql("SELECT * FROM materials", conn)

# 1. CO2 Impact Index (0-1, lower is better)
# Formula: co2_index = co2_emission_kg / max_co2_emission
max_co2 = df['co2_emission_kg'].max()
# CO2 Impact Index: emissions + recyclability (as mentor specified)
df['co2_impact_index'] = (
    (df['co2_emission_kg'] / max_co2) * 0.7 +           # 70% weight - direct emissions
    (1 - df['recyclability_percent'] / 100) * 0.3       # 30% weight - low recyclability adds to impact
)

# 2. Cost Efficiency Index (0-1, higher is better)
# Logic: High performance (strength + biodegradability) at low cost = efficient
max_cost = df['cost_per_kg'].max()

# Performance score: average of strength and biodegradability (both 0-1)
df['performance_score'] = (df['strength_score'] + df['biodegradability_score']) / 2

# Normalized cost (0-1, where 1 is most expensive)
df['normalized_cost'] = df['cost_per_kg'] / max_cost

# Cost efficiency: high performance at low cost
# We use (1 - normalized_cost) so lower cost = higher value
# Then multiply by performance to reward good materials
raw_efficiency = df['performance_score'] * (1 - df['normalized_cost'] + 0.1)  # +0.1 to avoid zero
# Normalize to 0-1 range
df['cost_efficiency_index'] = (raw_efficiency - raw_efficiency.min()) / (raw_efficiency.max() - raw_efficiency.min())

# 3. Eco Score (combined sustainability metric, 0-1, higher is better)
# Combines: low CO2 (inverted) + high biodegradability + high recyclability
# Weights: CO2 impact (40%), biodegradability (35%), recyclability (25%)
df['eco_score'] = (
    (1 - df['co2_impact_index']) * 0.40 +  # Invert CO2 so lower emissions = higher score
    df['biodegradability_score'] * 0.35 +
    (df['recyclability_percent'] / 100) * 0.25
)

# ============ SAVE RESULTS ============

# Ensure output directory exists
os.makedirs('E:/Data Science/EcoPackAI/data/processed', exist_ok=True)

# Save to CSV for ML training
df.to_csv('E:/Data Science/EcoPackAI/data/processed/materials_engineered.csv', index=False)

# Display results
print("=" * 70)
print("FEATURE ENGINEERING RESULTS")
print("=" * 70)
print("\nEngineered Features Summary:")
print("-" * 70)
print(df[['material_name', 'co2_impact_index', 'cost_efficiency_index', 'eco_score']]
      .sort_values('eco_score', ascending=False)
      .round(3)
      .to_string(index=False))

print("\n" + "=" * 70)
print("TOP 5 MATERIALS BY ECO SCORE:")
print("-" * 70)
top_eco = df.nlargest(5, 'eco_score')[['material_name', 'eco_score', 'co2_impact_index', 'cost_efficiency_index']]
print(top_eco.round(3).to_string(index=False))

print("\n" + "=" * 70)
print("TOP 5 MATERIALS BY COST EFFICIENCY:")
print("-" * 70)
top_cost = df.nlargest(5, 'cost_efficiency_index')[['material_name', 'cost_efficiency_index', 'cost_per_kg', 'performance_score']]
print(top_cost.round(3).to_string(index=False))

print("\n" + "=" * 70)
print(f"Data saved to: data/processed/materials_engineered.csv")
print(f"Total materials processed: {len(df)}")
print("=" * 70)

conn.close()