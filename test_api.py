import requests
import json

try:
    # Test summary endpoint
    r = requests.get('http://127.0.0.1:5000/api/dashboard/summary')
    print("Summary API Response:")
    print(json.dumps(r.json(), indent=2))
    print("\n" + "="*50 + "\n")
    
    # Test charts endpoint
    r = requests.get('http://127.0.0.1:5000/api/dashboard/charts')
    data = r.json()
    print("Charts API Response:")
    print(f"CO2 Reduction by Material: {len(data['co2_reduction_by_material'])} items")
    print(f"Cost Savings by Material: {len(data['cost_savings_by_material'])} items")
    print(f"Material Usage Trends: {len(data['material_usage_trends'])} items")
    
except Exception as e:
    print(f"Error: {e}")
