#!/bin/bash
# Test backend API endpoints using curl

BASE_URL="http://localhost:5000/api"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc3MjUwMzkxMiwianRpIjoiYmFjMDYyNjktNTE0ZS00YjY5LTgwYzctYTA4ZDQ3MWEzYmZmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzcyNTAzOTEyLCJleHAiOjE3NzI1OTAzMTJ9.vJHdNmzvcfJZ19GyW7pzjIhElHg3KOvBooe0ZcoJSvU"

echo "============================================================"
echo "Backend API Endpoint Tests"
echo "============================================================"
echo ""

# Test 1: Get categories
echo "Test 1: GET /api/categories"
curl -s -X GET "$BASE_URL/categories" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo ""

# Test 2: Get assets
echo "Test 2: GET /api/assets"
curl -s -X GET "$BASE_URL/assets" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo ""

# Test 3: Get consumables
echo "Test 3: GET /api/consumables"
curl -s -X GET "$BASE_URL/consumables" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo ""

# Test 4: Get dashboard
echo "Test 4: GET /api/dashboard"
curl -s -X GET "$BASE_URL/dashboard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo ""

# Test 5: Get suppliers
echo "Test 5: GET /api/suppliers"
curl -s -X GET "$BASE_URL/suppliers" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo ""

echo "============================================================"
echo "API Endpoint Tests Completed"
echo "============================================================"
