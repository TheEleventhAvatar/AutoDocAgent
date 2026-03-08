import requests
import os

# Test the upload endpoint
url = "http://localhost:8001/upload"

# Path to sample document
document_path = "sample_documents/sample_invoice.txt"

# Upload the file
with open(document_path, 'rb') as f:
    files = {'files': f}
    response = requests.post(url, files=files)

print("Upload Response:")
print(response.status_code)
print(response.json())

# Test templates endpoint
templates_url = "http://localhost:8001/templates"
templates_response = requests.get(templates_url)

print("\nAvailable Templates:")
print(templates_response.json())
