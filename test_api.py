import requests
import json

# Test data
product_data = {
    "id": "test1",
    "name": "Test Product",
    "categoryName": "Electronics",
    "description": "A test product",
    "basePrice": 29.99
}

# Post the product
response = requests.post(
    "http://127.0.0.1:8000/product",
    headers={"Content-Type": "application/json"},
    data=json.dumps(product_data)
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")