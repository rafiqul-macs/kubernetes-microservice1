from flask import Flask, request, jsonify
import os
import requests
import csv
import json

app = Flask(__name__)

# Define the persistent volume directory path
PV_DIR = "/john_PV_dir"  # Replace with your first name

# Create the directory if it doesn't exist (for local testing)
os.makedirs(PV_DIR, exist_ok=True)

# Microservice 2 connection details
MS2_HOST = os.environ.get("MS2_SERVICE_HOST", "microservice2")
MS2_PORT = os.environ.get("MS2_SERVICE_PORT", "5000")
MS2_URL = f"http://{MS2_HOST}:{MS2_PORT}"

@app.route('/store-file', methods=['POST'])
def store_file():
    try:
        # Parse request JSON
        data = request.get_json()
        
        # Validate JSON input
        if not data or 'file' not in data or not data['file']:
            return jsonify({
                "file": None,
                "error": "Invalid JSON input."
            }), 400
            
        if 'data' not in data:
            return jsonify({
                "file": data['file'],
                "error": "Invalid JSON input."
            }), 400
            
        file_name = data['file']
        file_content = data['data']
        file_path = os.path.join(PV_DIR, file_name)
        
        # Store the file in the persistent volume
        try:
            with open(file_path, 'w') as f:
                f.write(file_content)
            
            # Return success response
            return jsonify({
                "file": file_name,
                "message": "Success."
            })
        except Exception as e:
            app.logger.error(f"Error while storing file: {str(e)}")
            return jsonify({
                "file": file_name,
                "error": "Error while storing the file to the storage."
            }), 500
            
    except Exception as e:
        app.logger.error(f"Error in store_file: {str(e)}")
        return jsonify({
            "file": None,
            "error": "Invalid JSON input."
        }), 400

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        # Parse request JSON
        data = request.get_json()
        
        # Validate JSON input
        if not data or 'file' not in data or not data['file']:
            return jsonify({
                "file": None,
                "error": "Invalid JSON input."
            }), 400
            
        if 'product' not in data:
            return jsonify({
                "file": data['file'],
                "error": "Invalid JSON input."
            }), 400
            
        file_name = data['file']
        product = data['product']
        file_path = os.path.join(PV_DIR, file_name)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({
                "file": file_name,
                "error": "File not found."
            }), 404
            
        # Forward the request to microservice2 for calculation
        try:
            response = requests.post(f"{MS2_URL}/calculate-product", json={
                "file": file_name,
                "product": product
            })
            
            return response.json(), response.status_code
            
        except Exception as e:
            app.logger.error(f"Error communicating with microservice2: {str(e)}")
            return jsonify({
                "file": file_name,
                "error": "Error communicating with calculation service."
            }), 500
            
    except Exception as e:
        app.logger.error(f"Error in calculate: {str(e)}")
        return jsonify({
            "file": None,
            "error": "Invalid JSON input."
        }), 400

@app.route('/start', methods=['POST'])
def start():
    try:
        # Parse request JSON
        data = request.get_json()
        
        # Validate JSON input
        if not data or 'banner' not in data or 'ip' not in data:
            return jsonify({
                "error": "Invalid JSON input."
            }), 400
            
        # Return success response
        return jsonify({
            "banner": data['banner'],
            "ip": data['ip']
        })
            
    except Exception as e:
        app.logger.error(f"Error in start: {str(e)}")
        return jsonify({
            "error": "Invalid JSON input."
        }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)