import pandas as pd

df = pd.read_csv("data/feature_engineered_materials.csv")

print(df.isnull().sum())
print(df.describe())
