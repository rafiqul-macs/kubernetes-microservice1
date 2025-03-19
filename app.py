from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Define persistent volume directory
PV_DIR = "/rafiqul_PV_dir"
os.makedirs(PV_DIR, exist_ok=True)

# Microservice 2 connection details - use Kubernetes DNS
MS2_URL = "http://microservice2:5000"

@app.route('/start', methods=['GET', 'POST'])
def start():
    if request.method == 'GET':
        return jsonify({"message": "Service is running"}), 200
        
    data = request.get_json()
    if not data or 'banner' not in data or 'ip' not in data:
        return jsonify({"error": "Invalid JSON input."}), 400
        
    return jsonify({
        "banner": data['banner'],
        "ip": data['ip']
    })

@app.route('/store-file', methods=['POST'])
def store_file():
    data = request.get_json()
    
    # Validate input
    if not data or 'file' not in data or not data['file']:
        return jsonify({"file": None, "error": "Invalid JSON input."}), 400
        
    if 'data' not in data:
        return jsonify({"file": data['file'], "error": "Invalid JSON input."}), 400
        
    file_name = data['file']
    file_content = data['data']
    file_path = os.path.join(PV_DIR, file_name)
    
    # Store file
    try:
        with open(file_path, 'w') as f:
            f.write(file_content)
        
        return jsonify({
            "file": file_name,
            "message": "Success."
        })
    except Exception as e:
        print(f"Error storing file: {e}")
        return jsonify({
            "file": file_name,
            "error": "Error while storing the file to the storage."
        }), 500

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    
    # Validate input
    if not data or 'file' not in data or not data['file']:
        return jsonify({"file": None, "error": "Invalid JSON input."}), 400
        
    if 'product' not in data:
        return jsonify({"file": data['file'], "error": "Invalid JSON input."}), 400
        
    file_name = data['file']
    product = data['product']
    file_path = os.path.join(PV_DIR, file_name)
    
    # Check if file exists
    if not os.path.exists(file_path):
        return jsonify({
            "file": file_name,
            "error": "File not found."
        }), 404
    
    # Forward request to microservice2
    try:
        response = requests.post(f"{MS2_URL}/calculate-product", 
                                json={"file": file_name, "product": product},
                                timeout=5)
        return response.json(), response.status_code
    except requests.RequestException as e:
        print(f"Error communicating with microservice2: {e}")
        return jsonify({
            "file": file_name,
            "error": "Error communicating with calculation service."
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
