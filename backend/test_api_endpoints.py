# 测试后端 API 端点（带认证）
import json

# 从登录获取的 token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc3MjUwMzkxMiwianRpIjoiYmFjMDYyNjktNTE0ZS00YjY5LTgwYzctYTA4ZDQ3MWEzYmZmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzcyNTAzOTEyLCJleHAiOjE3NzI1OTAzMTJ9.vJHdNmzvcfJZ19GyW7pzjIhElHg3KOvBooe0ZcoJSvU"

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}

import requests

BASE_URL = 'http://localhost:5000/api'

print("=" * 60)
print("后端 API 端点测试")
print("=" * 60)
print()

# 测试1：获取类别
print("Test 1: GET /api/categories")
try:
    response = requests.get(f'{BASE_URL}/categories', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        categories = data.get('data', [])
        print(f"Success! Found {len(categories)} categories")
        for cat in categories[:3]:
            print(f"  - {cat.get('name')}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
print()

# 测试2：获取资产
print("Test 2: GET /api/assets")
try:
    response = requests.get(f'{BASE_URL}/assets', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        assets = data.get('data', {}).get('items', [])
        print(f"Success! Found {len(assets)} assets")
        for asset in assets[:3]:
            print(f"  - {asset.get('name')} ({asset.get('code')})")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
print()

# 测试3：获取耗材
print("Test 3: GET /api/consumables")
try:
    response = requests.get(f'{BASE_URL}/consumables', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        consumables = data.get('data', {}).get('items', [])
        print(f"Success! Found {len(consumables)} consumables")
        for item in consumables[:3]:
            print(f"  - {item.get('name')} (Stock: {item.get('stock')})")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
print()

# 测试4：获取仪表盘
print("Test 4: GET /api/dashboard")
try:
    response = requests.get(f'{BASE_URL}/dashboard', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        dashboard_data = data.get('data', {})
        print(f"Success! Dashboard data received:")
        print(f"  - Asset count: {dashboard_data.get('asset_count')}")
        print(f"  - Consumable count: {dashboard_data.get('consumable_count')}")
        print(f"  - Low stock items: {len(dashboard_data.get('low_stock_items', []))}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
print()

# 测试5：获取供应商
print("Test 5: GET /api/suppliers")
try:
    response = requests.get(f'{BASE_URL}/suppliers', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        suppliers = data.get('data', [])
        print(f"Success! Found {len(suppliers)} suppliers")
        for supplier in suppliers[:3]:
            print(f"  - {supplier.get('name')}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
print()

print("=" * 60)
print("API 端点测试完成")
print("=" * 60)
