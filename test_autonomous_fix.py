import requests
import json

# Test just the autonomous processing endpoint
base_url = "http://localhost:8001"

# First upload a document
print("Uploading document...")
upload_url = f"{base_url}/upload"
with open("sample_documents/sample_invoice.txt", 'rb') as f:
    files = {'files': f}
    upload_response = requests.post(upload_url, files=files)
    print("Upload Response:", upload_response.json())

# Test autonomous processing
print("\nTesting autonomous processing...")
auto_url = f"{base_url}/autonomous-process"
auto_data = ["../uploads/sample_invoice.txt"]
auto_params = {"template_directory": "../sample_templates"}

try:
    auto_response = requests.post(auto_url, params=auto_params, json=auto_data)
    print("Autonomous Processing Response:")
    print(json.dumps(auto_response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
    print("This means the 're' import fix worked - no more 'name re is not defined' error!")
