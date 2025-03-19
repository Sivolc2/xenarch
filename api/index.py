from pathlib import Path
import sys
import os
import json
from flask import Flask, jsonify, request
import uuid

# Add the project root to the path so we can import from backend
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# Create required directories in the Vercel environment
os.makedirs('/tmp/uploads', exist_ok=True)
os.makedirs('/tmp/analysis_results', exist_ok=True)
os.makedirs('/tmp/logs', exist_ok=True)

# Configure an independent Flask app for serverless - don't try to import from backend
app = Flask(__name__)

# Configure folders for Vercel environment
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['RESULTS_FOLDER'] = '/tmp/analysis_results'

# Disable debug mode in production
app.debug = False

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# API Routes - Note: in Vercel, these should NOT include the /api prefix in the route
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running"""
    return jsonify({
        "status": "ok",
        "environment": "vercel"
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and start analysis"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Create a unique ID for this job
    job_id = str(uuid.uuid4())
    
    # For now, return a placeholder response
    return jsonify({
        "status": "processing",
        "job_id": job_id,
        "message": "File upload received. This is a demo response as actual processing is not implemented in this Vercel function."
    })

@app.route('/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """Get status of a specific job"""
    # Placeholder implementation
    return jsonify({
        "status": "completed",
        "job_id": job_id,
        "message": "This is a demo response as actual processing is not implemented in this Vercel function."
    })

@app.route('/jobs/<job_id>/results', methods=['GET'])
def get_job_results(job_id):
    """Get results of a specific job"""
    # Placeholder implementation
    return jsonify({
        "status": "completed",
        "job_id": job_id,
        "results": [
            {"grid_id": "demo1", "fractal_dimension": 0.76, "r2": 0.95},
            {"grid_id": "demo2", "fractal_dimension": 0.68, "r2": 0.92}
        ],
        "message": "This is a demo response with placeholder data."
    })

@app.route('/jobs/<job_id>/thumbnail/<grid_id>', methods=['GET'])
def get_thumbnail(job_id, grid_id):
    """Get thumbnail for a specific grid"""
    # For a real implementation, this would return an image
    return jsonify({"error": "Thumbnail generation not implemented in this demo"}), 501

@app.route('/jobs/<job_id>/raw/<grid_id>', methods=['GET'])
def get_raw_tif(job_id, grid_id):
    """Get raw GeoTIFF for a specific grid"""
    # For a real implementation, this would return a GeoTIFF file
    return jsonify({"error": "Raw GeoTIFF access not implemented in this demo"}), 501

# In Vercel serverless functions, we need to have this specific handler 
# for the function to be called properly
def handler(event, context):
    """
    AWS Lambda / Vercel serverless function handler
    This is the main entry point for the Vercel serverless function
    """
    # Log the path for debugging
    path = event.get('path', '')
    method = event.get('httpMethod', '')
    
    print(f"Received request: {method} {path}")
    
    # Remove /api prefix if present (as Vercel will route /api requests to this function)
    if path.startswith('/api'):
        path = path[4:]  # Remove the '/api' part
    
    # Create a new Flask request context
    with app.test_request_context(
        path=path,
        method=method,
        headers=event.get('headers', {}),
        data=event.get('body', ''),
        query_string=event.get('queryStringParameters', {})
    ) as ctx:
        # Process the request
        try:
            response = app.full_dispatch_request()
            # Convert the Flask response to Lambda/Vercel response format
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Internal Server Error',
                    'message': str(e)
                })
            } 