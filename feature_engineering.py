import pandas as pd

def normalize(df, num_cols):
    df[num_cols] = (df[num_cols] - df[num_cols].min()) / (df[num_cols].max() - df[num_cols].min())
    return df

def encode_materials(df):
    return pd.get_dummies(df, columns=['material_type', 'product_category'])

def generate_scores(df_materials, df_products):
    df_scores = pd.DataFrame()
    df_scores['score_id'] = df_materials['material_id']
    df_scores['material_id'] = df_materials['material_id']
    df_scores['product_id'] = df_products['product_id']
    df_scores['material_sustainability_score'] = df_materials['biodegradability_score'] * df_materials['recyclability_percentage']
    df_scores['co2_impact_index'] = df_materials['co2_emission_score'] * df_materials['weight_capacity']
    df_scores['cost_efficiency_index'] = df_materials['strength'] / (df_materials['weight_capacity'] + 1)
    return df_scores



