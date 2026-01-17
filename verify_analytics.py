
import sys
import os
import pandas as pd

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from app.services.analytics_service import analytics_service

app = create_app('dev')

with app.app_context():
    print("Testing Analytics Service...")
    try:
        print("1. Fetching CO2...")
        df_co2 = analytics_service.get_avg_co2_by_material()
        print(f"   Rows: {len(df_co2)}")
        print(df_co2.head())
        
        print("\n2. Fetching Category Counts...")
        df_cat = analytics_service.get_material_category_counts()
        print(f"   Rows: {len(df_cat)}")
        print(df_cat.head())
        
        print("\n3. Fetching Sustainability Scores...")
        df_sust = analytics_service.get_sustainability_distribution()
        print(f"   Rows: {len(df_sust)}")

        print("\n4. Fetching Cost Data...")
        df_cost = analytics_service.get_cost_distribution()
        print(f"   Rows: {len(df_cost)}")
        
        print("\n✅ Analytics Service looks healthy.")
    except Exception as e:
        print(f"\n❌ Error in Analytics Service: {e}")
        import traceback
        traceback.print_exc()
