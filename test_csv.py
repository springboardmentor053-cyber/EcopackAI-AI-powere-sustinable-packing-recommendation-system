import requests

try:
    r = requests.get('http://127.0.0.1:5000/download_report')
    if r.status_code == 200:
        with open('EcoPackAI_Report.csv', 'w', encoding='utf-8') as f:
            f.write(r.text)
        print("CSV Download successful!")
        print(f"File size: {len(r.text)} bytes")
        print(f"\nFirst 30 lines of report:")
        lines = r.text.split('\n')
        for line in lines[:30]:
            if line:
                print(line)
    else:
        print(f"Error: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")
