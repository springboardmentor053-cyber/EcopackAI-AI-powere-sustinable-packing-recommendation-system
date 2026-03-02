import requests

try:
    # Test CSV download
    r = requests.get('http://127.0.0.1:5000/download_report')
    if r.status_code == 200:
        # Save the CSV file
        with open('EcoPackAI_Sustainability_Report.csv', 'w') as f:
            f.write(r.text)
        print("✓ CSV Download successful!")
        print("\nFirst 20 lines of the report:")
        lines = r.text.split('\n')
        for i, line in enumerate(lines[:20]):
            print(f"{i+1}: {line}")
    else:
        print(f"Error: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")
