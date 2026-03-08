import requests
import json

# Base URL
base_url = "http://localhost:8001"

# 1. Upload document
print("1. Uploading document...")
upload_url = f"{base_url}/upload"
with open("sample_documents/sample_invoice.txt", 'rb') as f:
    files = {'files': f}
    upload_response = requests.post(upload_url, files=files)
    print("Upload Response:", upload_response.json())

# 2. Extract data from document
print("\n2. Extracting data from document...")
extract_url = f"{base_url}/extract"
params = {"file_path": "../uploads/sample_invoice.txt"}
extract_response = requests.post(extract_url, params=params)
print("Extract Response:", json.dumps(extract_response.json(), indent=2))

# 3. Fill a form with extracted data
print("\n3. Filling Tax Form with extracted data...")
fill_url = f"{base_url}/fill-form"
fill_params = {
    "template_path": "../sample_templates/Tax_Form.xlsx"
}
fill_data = extract_response.json().get("structured_data", {})
fill_response = requests.post(fill_url, params=fill_params, json=fill_data)
print("Form Fill Response:", json.dumps(fill_response.json(), indent=2))

# 4. Run autonomous processing
print("\n4. Running autonomous document processing...")
auto_url = f"{base_url}/autonomous-process"
auto_data = ["../uploads/sample_invoice.txt"]  # Should be a list, not dict
auto_params = {"template_directory": "../sample_templates"}
auto_response = requests.post(auto_url, params=auto_params, json=auto_data)
print("Autonomous Processing Response:", json.dumps(auto_response.json(), indent=2))
