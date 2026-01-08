import pandas as pd

def clean_materials(df):
    numeric_cols = [
        'strength', 'weight_capacity', 'cost_per_unit',
        'biodegradability_score', 'co2_emission_score', 'recyclability_percentage'
    ]

    # Ensure numeric
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    # Fill NaN with mean
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

    # Replace any value <= 0 with realistic minimums
    min_values = {
        'strength': 5.0,
        'weight_capacity': 5.0,
        'cost_per_unit': 10.0,
        'biodegradability_score': 5.0,
        'co2_emission_score': 1.0,
        'recyclability_percentage': 50.0
    }

    for col in numeric_cols:
        df.loc[df[col] <= 0, col] = min_values[col]

    return df

