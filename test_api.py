import requests
import json

# More comprehensive test data to understand the JSON structure
product_data = {
    "id": "test1",
    "name": "Premium Concrete Mixer 200L",
    "barcode": "1234567890123",
    "description": "Heavy-duty concrete mixer with 200-liter capacity, ideal for construction sites and large DIY projects",
    "basePrice": 299.99,
    "categoryName": "Construction Equipment",
    "brand": "Holcim",
    "tags": ["construction", "mixer", "concrete", "power-tools"],
    "variants": [
        {
            "id": "variant1",
            "sku": "CM-200L-BLK",
            "price": 299.99,
            "stock": 15,
            "images": [
                {
                    "id": "img1",
                    "url": "https://example.com/images/cm-200l-blk-1.jpg"
                }
            ],
            "attributes": [
                {
                    "id": "attr1",
                    "templateId": "color",
                    "name": "Color",
                    "dataType": "string",
                    "stringValue": "Black"
                },
                {
                    "id": "attr2",
                    "templateId": "power",
                    "name": "Power",
                    "dataType": "number",
                    "numberValue": 1500
                },
                {
                    "id": "attr3",
                    "templateId": "warranty",
                    "name": "Warranty",
                    "dataType": "number",
                    "numberValue": 2
                }
            ]
        }
    ],
    "metadata": {
        "weight": "45kg",
        "dimensions": "80x60x60cm",
        "manufacturer": "Holcim Tools Ltd"
    }
}

service_data = {
    "id": "serv1",
    "name": "Professional Construction Consultation",
    "description": "Expert consultation services for residential and commercial construction projects",
    "basePrice": 150.00,
    "categoryName": "Construction Services",
    "tags": ["consultation", "construction", "planning", "expert"],
    "packages": [
        {
            "id": "pkg1",
            "name": "Basic Consultation",
            "price": 150.00,
            "description": "2-hour consultation session with expert advice",
            "images": [
                {
                    "id": "img1",
                    "url": "https://example.com/images/consult-basic.jpg"
                }
            ],
            "attributes": [
                {
                    "id": "attr1",
                    "templateId": "duration",
                    "name": "Duration",
                    "dataType": "number",
                    "numberValue": 2
                },
                {
                    "id": "attr2",
                    "templateId": "expertise",
                    "name": "Expertise Level",
                    "dataType": "string",
                    "stringValue": "Senior Consultant"
                }
            ]
        }
    ],
    "metadata": {
        "certifications": ["Licensed Contractor", "Certified Engineer"],
        "experience": "10+ years"
    }
}

# Test posting product
print("Posting product...")
response = requests.post(
    "http://127.0.0.1:8000/product",
    headers={"Content-Type": "application/json"},
    data=json.dumps(product_data)
)

print(f"Product Status Code: {response.status_code}")
print(f"Product Response: {response.text}")

# Test posting service
print("\nPosting service...")
response = requests.post(
    "http://127.0.0.1:8000/service",
    headers={"Content-Type": "application/json"},
    data=json.dumps(service_data)
)

print(f"Service Status Code: {response.status_code}")
print(f"Service Response: {response.text}")

# Test search
print("\nTesting search...")
response = requests.get("http://127.0.0.1:8000/search?query=construction")

print(f"Search Status Code: {response.status_code}")
print(f"Search Response: {response.text}")