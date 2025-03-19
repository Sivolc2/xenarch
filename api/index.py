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

# Import the Flask app from backend and modify it for serverless
from backend.app import app

# Configure folders for Vercel environment
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['RESULTS_FOLDER'] = '/tmp/analysis_results'

# Disable debug mode in production
app.debug = False

# Import serverless handler
from api.serverless_wsgi import handle_request

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Remove existing routes that we'll replace
# Find all registered routes for the '/api/' prefix
routes_to_remove = []
for rule in app.url_map.iter_rules():
    if rule.rule.startswith('/api/'):
        routes_to_remove.append(rule)

# Remove those routes
for rule in routes_to_remove:
    app.url_map._rules.remove(rule)
    app.url_map._rules_by_endpoint.pop(rule.endpoint, None)

# API Routes - needs to match what the backend expects but with proper handlers
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running"""
    return jsonify({
        "status": "ok",
        "environment": "vercel"
    })

@app.route('/api/upload', methods=['POST'])
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

@app.route('/api/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """Get status of a specific job"""
    # Placeholder implementation
    return jsonify({
        "status": "completed",
        "job_id": job_id,
        "message": "This is a demo response as actual processing is not implemented in this Vercel function."
    })

@app.route('/api/jobs/<job_id>/results', methods=['GET'])
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

@app.route('/api/jobs/<job_id>/thumbnail/<grid_id>', methods=['GET'])
def get_thumbnail(job_id, grid_id):
    """Get thumbnail for a specific grid"""
    # For a real implementation, this would return an image
    return jsonify({"error": "Thumbnail generation not implemented in this demo"}), 501

@app.route('/api/jobs/<job_id>/raw/<grid_id>', methods=['GET'])
def get_raw_tif(job_id, grid_id):
    """Get raw GeoTIFF for a specific grid"""
    # For a real implementation, this would return a GeoTIFF file
    return jsonify({"error": "Raw GeoTIFF access not implemented in this demo"}), 501

# Vercel serverless function handler
def handler(request, context):
    """Vercel serverless function handler"""
    return handle_request(app, request, context) 