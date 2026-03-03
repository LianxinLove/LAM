# 测试后端 API 端点的简单脚本
import requests
import json

BASE_URL = 'http://localhost:5000/api'

print("=" * 60)
print("后端 API 测试")
print("=" * 60)
print()

# 测试1：健康检查（如果可用）
print("Test 1: 检查服务器是否运行...")
try:
    response = requests.get(f'{BASE_URL}/auth/me', timeout=2)
    print(f"Status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("服务器未运行或无法访问")
    print("请先启动 Flask 服务器: python run.py")
    exit(1)
except Exception as e:
    print(f"Error: {e}")
    # 继续执行，可能是预期的 401 错误

print()

# 测试2：登录
print("Test 2: 使用管理员凭据登录...")
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

# 测试3：获取类别
print("Test 3: 获取类别...")
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

# 测试4：获取资产
print("Test 4: 获取资产...")
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

# 测试5：获取耗材
print("Test 5: 获取耗材...")
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

# 测试6：获取仪表盘数据
print("Test 6: 获取仪表盘数据...")
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
print("API 测试完成")
print("=" * 60)
