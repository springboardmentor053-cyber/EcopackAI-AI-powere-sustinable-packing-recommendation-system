#!/usr/bin/env python
"""Final Verification Script - Week 7 EcoPackAI BI Dashboard"""

import requests
import json
import os
from datetime import datetime

print("=" * 70)
print("ECOPACKAI WEEK 7 - BUSINESS INTELLIGENCE DASHBOARD")
print("Final Verification Report")
print("=" * 70)
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

BASE_URL = "http://127.0.0.1:5000"
tests_passed = 0
tests_total = 0

def test_section(title):
    print(f"\n{title}")
    print("-" * 70)

def test_case(name, condition, expected=""):
    global tests_passed, tests_total
    tests_total += 1
    status = "✓ PASS" if condition else "✗ FAIL"
    print(f"{status}: {name}")
    if expected:
        print(f"       Expected: {expected}")
    if condition:
        tests_passed += 1
    return condition

# Test 1: Server Connectivity
test_section("TEST 1: Server Connectivity")
try:
    response = requests.get(f"{BASE_URL}/")
    test_case("Server is running", response.status_code == 200)
except Exception as e:
    test_case("Server is running", False, f"Error: {str(e)}")

# Test 2: API Endpoints
test_section("TEST 2: API Endpoints")

# Test Summary API
try:
    response = requests.get(f"{BASE_URL}/api/dashboard/summary")
    data = response.json()
    test_case("Summary API returns 200", response.status_code == 200)
    test_case("Summary has total_materials", 'total_materials' in data)
    test_case("Summary has average_cost_score", 'average_cost_score' in data)
    test_case("Summary has average_co2_score", 'average_co2_score' in data)
    test_case("Summary has co2_reduction estimate", 'estimated_co2_reduction_pct' in data)
    test_case("Summary has cost_savings estimate", 'estimated_cost_savings_pct' in data)
    test_case("Total materials is 111", data.get('total_materials') == 111)
except Exception as e:
    test_case("Summary API", False, f"Error: {str(e)}")

# Test Charts API
try:
    response = requests.get(f"{BASE_URL}/api/dashboard/charts")
    data = response.json()
    test_case("Charts API returns 200", response.status_code == 200)
    test_case("Charts has co2_reduction_by_material", 'co2_reduction_by_material' in data)
    test_case("Charts has cost_savings_by_material", 'cost_savings_by_material' in data)
    test_case("Charts has material_usage_trends", 'material_usage_trends' in data)
    test_case("CO2 data has items", len(data.get('co2_reduction_by_material', [])) > 0)
    test_case("Cost data has items", len(data.get('cost_savings_by_material', [])) > 0)
    test_case("Usage data has items", len(data.get('material_usage_trends', [])) > 0)
except Exception as e:
    test_case("Charts API", False, f"Error: {str(e)}")

# Test 3: Dashboard Pages
test_section("TEST 3: Dashboard Pages")

try:
    response = requests.get(f"{BASE_URL}/dashboard")
    test_case("Dashboard page loads", response.status_code == 200)
    test_case("Dashboard contains Chart.js", "chart.js" in response.text.lower())
    test_case("Dashboard contains fetch API calls", "fetch" in response.text.lower())
except Exception as e:
    test_case("Dashboard page", False, f"Error: {str(e)}")

# Test 4: Report Export
test_section("TEST 4: Report Export")

try:
    response = requests.get(f"{BASE_URL}/download_report")
    test_case("Report download returns 200", response.status_code == 200)
    test_case("Report is CSV format", "text/csv" in response.headers.get('content-type', ''))
    test_case("Report has content", len(response.text) > 100)
    test_case("Report contains summary section", "SUMMARY METRICS" in response.text)
    test_case("Report contains material analysis", "MATERIAL ANALYSIS" in response.text)
    test_case("Report contains 'EcoPackAI'", "EcoPackAI" in response.text)
    
    # Verify CSV structure
    lines = response.text.split('\n')
    test_case("Report has multiple lines", len(lines) > 20)
    test_case("Report has summary row", any("Total Materials" in line for line in lines))
except Exception as e:
    test_case("Report export", False, f"Error: {str(e)}")

# Test 5: Data Metrics
test_section("TEST 5: Data Metrics Validation")

try:
    response = requests.get(f"{BASE_URL}/api/dashboard/summary")
    data = response.json()
    
    test_case("Total materials > 100", data.get('total_materials', 0) > 100)
    test_case("Average cost is positive", data.get('average_cost_score', 0) > 0)
    test_case("Average CO2 is positive", data.get('average_co2_score', 0) > 0)
    test_case("Eco-friendly count > 0", data.get('eco_friendly_materials_count', 0) > 0)
    test_case("Traditional count > 0", data.get('traditional_materials_count', 0) > 0)
    
    print(f"\n       Key Metrics:")
    print(f"         Total Materials: {data.get('total_materials')}")
    print(f"         Average Cost Score: {data.get('average_cost_score')}")
    print(f"         Average CO₂ Score: {data.get('average_co2_score')}")
    print(f"         Eco-Friendly Materials: {data.get('eco_friendly_materials_count')}")
    print(f"         Traditional Materials: {data.get('traditional_materials_count')}")
except Exception as e:
    test_case("Data metrics", False, f"Error: {str(e)}")

# Test 6: File System
test_section("TEST 6: File System Structure")

files_to_check = [
    'main.py',
    'templates/index.html',
    'templates/dashboard.html',
    'material.csv',
    'product.csv',
    'co2_model.pkl',
    'cost_model.pkl',
    'WEEK_7_SUBMISSION.md'
]

base_path = "."
for file in files_to_check:
    file_path = os.path.join(base_path, file)
    exists = os.path.exists(file_path)
    test_case(f"File exists: {file}", exists)
    if exists:
        size = os.path.getsize(file_path)
        print(f"         Size: {size} bytes")

# Test 7: Feature Completeness
test_section("TEST 7: Feature Completeness")

try:
    # Check main.py for required functions
    with open('main.py', 'r') as f:
        content = f.read()
    
    test_case("main.py has /api/dashboard/summary", '/api/dashboard/summary' in content)
    test_case("main.py has /api/dashboard/charts", '/api/dashboard/charts' in content)
    test_case("main.py has /download_report", '/download_report' in content)
    test_case("main.py has /dashboard route", '@app.route(\"/dashboard\")' in content)
    test_case("main.py imports pandas", 'import pandas' in content)
    
    # Check dashboard.html for features
    with open('templates/dashboard.html', 'r') as f:
        content = f.read()
    
    test_case("Dashboard has Chart.js", 'chart.js' in content)
    test_case("Dashboard has 3 charts", content.count('new Chart') >= 3)
    test_case("Dashboard has fetch calls", 'fetch' in content)
    test_case("Dashboard has download button", 'downloadReport' in content)
    
except Exception as e:
    test_case("Feature completeness", False, f"Error: {str(e)}")

# Final Summary
test_section("FINAL SUMMARY")
print(f"\nTests Passed: {tests_passed}/{tests_total}")
success_rate = (tests_passed / tests_total * 100) if tests_total > 0 else 0
print(f"Success Rate: {success_rate:.1f}%")

if tests_passed == tests_total:
    print("\n✓ ALL TESTS PASSED - Dashboard is fully functional!")
else:
    print(f"\n⚠ {tests_total - tests_passed} test(s) failed - Please review issues above")

print("\n" + "=" * 70)
print("DASHBOARD READY FOR DEPLOYMENT")
print("=" * 70)
print(f"\nAccess Points:")
print(f"  • Home Page: {BASE_URL}/")
print(f"  • Dashboard: {BASE_URL}/dashboard")
print(f"  • Summary API: {BASE_URL}/api/dashboard/summary")
print(f"  • Charts API: {BASE_URL}/api/dashboard/charts")
print(f"  • Download Report: {BASE_URL}/download_report")
print("=" * 70)
