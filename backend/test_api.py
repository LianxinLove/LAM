"""
Simple script to test backend API endpoints
"""
import requests
import json

BASE_URL = 'http://localhost:5000/api'

print("=" * 60)
print("Backend API Test")
print("=" * 60)
print()

# Test 1: Health check (if available)
print("Test 1: Checking if server is running...")
try:
    response = requests.get(f'{BASE_URL}/auth/me', timeout=2)
    print(f"Status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("Server is not running or not accessible")
    print("Please start the Flask server first: python run.py")
    exit(1)
except Exception as e:
    print(f"Error: {e}")
    # Continue anyway, might be 401 which is expected

print()

# Test 2: Login
print("Test 2: Login with admin credentials...")
login_data = {
    'username': 'admin',
    'password': 'admin123'
}
try:
    response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('message', 'Login successful')}")
        token = data.get('data', {}).get('token')
        if token:
            print(f"Token received: {token[:50]}...")
            headers = {'Authorization': f'Bearer {token}'}
        else:
            print("No token received")
            headers = {}
    else:
        print(f"Response: {response.text}")
        headers = {}
except Exception as e:
    print(f"Error: {e}")
    headers = {}

print()

# Test 3: Get categories
print("Test 3: Get categories...")
try:
    response = requests.get(f'{BASE_URL}/categories', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        categories = data.get('data', [])
        print(f"Found {len(categories)} categories")
        for cat in categories[:3]:
            print(f"  - {cat.get('name')}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 4: Get assets
print("Test 4: Get assets...")
try:
    response = requests.get(f'{BASE_URL}/assets', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        assets = data.get('data', {}).get('items', [])
        print(f"Found {len(assets)} assets")
        for asset in assets[:3]:
            print(f"  - {asset.get('name')} ({asset.get('code')})")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 5: Get consumables
print("Test 5: Get consumables...")
try:
    response = requests.get(f'{BASE_URL}/consumables', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        consumables = data.get('data', {}).get('items', [])
        print(f"Found {len(consumables)} consumables")
        for item in consumables[:3]:
            print(f"  - {item.get('name')} (Stock: {item.get('stock')})")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 6: Get dashboard data
print("Test 6: Get dashboard data...")
try:
    response = requests.get(f'{BASE_URL}/dashboard', headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        dashboard_data = data.get('data', {})
        print(f"Dashboard data received:")
        print(f"  - Asset count: {dashboard_data.get('asset_count')}")
        print(f"  - Consumable count: {dashboard_data.get('consumable_count')}")
        print(f"  - Low stock items: {len(dashboard_data.get('low_stock_items', []))}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print()
print("=" * 60)
print("API Test Completed")
print("=" * 60)
