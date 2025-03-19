#!/usr/bin/env python3

import os
import sys
import uuid
import json
import logging
from pathlib import Path
from io import BytesIO
import subprocess
from datetime import datetime
from typing import Dict, List, Any
import warnings
from dotenv import load_dotenv

# Handle deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load environment variables from .env file
load_dotenv()

# Add the current directory to sys.path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import Flask after environment setup
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Set environment variables for scientific libraries
# This helps with compatibility issues in Python 3.12
os.environ["OPENBLAS_NUM_THREADS"] = "1"  # Prevent numpy/scipy threading issues
os.environ["MKL_NUM_THREADS"] = "1"  

# Now import scientific libraries
try:
    import numpy as np
    import rasterio
    from PIL import Image
except ImportError as e:
    print(f"Error importing scientific libraries: {e}")
    print("Please ensure all required dependencies are installed.")
    print("If using Python 3.12, make sure you've upgraded setuptools and wheel.")
    sys.exit(1)

# Configuration
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = Path(os.environ.get('UPLOAD_FOLDER', BASE_DIR / '../uploads'))
RESULTS_FOLDER = Path(os.environ.get('RESULTS_FOLDER', BASE_DIR / '../analysis_results'))
LOGS_DIR = Path(os.environ.get('LOGS_DIR', BASE_DIR / 'logs'))
ALLOWED_EXTENSIONS = {'tif', 'tiff'}

# Create required directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.environ.get('FLASK_ENV') != 'production' else logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Log Python version info
logger.info(f"Python version: {sys.version}")
logger.info(f"NumPy version: {np.__version__}")
logger.info(f"Rasterio version: {rasterio.__version__}")

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
allowed_origins = os.environ.get('ALLOWED_ORIGINS', '*')
CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['RESULTS_FOLDER'] = str(RESULTS_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_UPLOAD_SIZE', 32 * 1024 * 1024))  # Default 32MB

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', allowed_origins)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "numpy_version": np.__version__,
        "rasterio_version": rasterio.__version__,
        "pil_version": Image.__version__
    })


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload and parameter configuration
    Expects a multipart form with a GeoTIFF file and analysis parameters
    """
    logger.info("Received file upload request")
    
    # Check if a file was provided
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    # Check if the file was selected
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Validate file extension
    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Create job directory structure
    job_upload_dir = UPLOAD_FOLDER / job_id
    job_results_dir = RESULTS_FOLDER / job_id
    
    os.makedirs(job_upload_dir, exist_ok=True)
    os.makedirs(job_results_dir, exist_ok=True)
    
    # Save the uploaded file with a secure filename
    filename = secure_filename(file.filename)
    file_path = job_upload_dir / filename
    file.save(file_path)
    
    logger.info(f"File saved to {file_path}")
    
    # Get analysis parameters from the form with defaults
    params = {
        'grid_size': request.form.get('grid_size', '512'),
        'overlap': request.form.get('overlap', '64'),
        'fd_min': request.form.get('fd_min', '0.0'),
        'fd_max': request.form.get('fd_max', '0.8'),
        'r2_min': request.form.get('r2_min', '0.8'),
        'max_samples': request.form.get('max_samples', '16'),
        'cpu_fraction': request.form.get('cpu_fraction', '0.8'),
    }
    
    # Save the parameters for later reference
    with open(job_results_dir / 'params.json', 'w') as f:
        json.dump(params, f)
    
    # Run the XenArch pipeline command
    try:
        cli_script = BASE_DIR / 'cli.py'
        
        command = [
            'python', str(cli_script), 'complete',
            '-i', str(file_path),
            '-o', str(job_results_dir),
            '--grid-size', params['grid_size'],
            '--overlap', params['overlap'],
            '--fd-min', params['fd_min'],
            '--fd-max', params['fd_max'],
            '--r2-min', params['r2_min'],
            '--max-samples', params['max_samples'],
            '--cpu-fraction', params['cpu_fraction'],
            '--plot-output', str(job_results_dir),
            '-v'
        ]
        
        logger.info(f"Running command: {' '.join(command)}")
        
        # Run the command as a subprocess
        process = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info(f"Command completed successfully: {process.stdout}")
        
        # Return the job ID so the frontend can request results
        return jsonify({
            "status": "success",
            "job_id": job_id,
            "message": "Analysis started successfully"
        })
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {e.stderr}")
        return jsonify({
            "status": "error",
            "message": f"Error processing file: {e.stderr}"
        }), 500
    except Exception as e:
        logger.exception("Unexpected error during file processing")
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500


@app.route('/api/jobs/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """Check the status of an analysis job"""
    job_results_dir = RESULTS_FOLDER / job_id
    
    # Check if job directory exists
    if not job_results_dir.exists():
        return jsonify({
            "status": "not_found",
            "message": "Job not found"
        }), 404
    
    # Check for params.json (job started)
    if not (job_results_dir / 'params.json').exists():
        return jsonify({
            "status": "error",
            "message": "Job parameters not found"
        }), 500
    
    # Check for metrics JSON files (processing complete)
    json_files = list(job_results_dir.glob('*.json'))
    metrics_files = [f for f in json_files if f.name != 'params.json']
    
    if not metrics_files:
        return jsonify({
            "status": "processing",
            "message": "Analysis in progress"
        })
    
    return jsonify({
        "status": "complete",
        "message": "Analysis complete",
        "metrics_count": len(metrics_files)
    })


@app.route('/api/jobs/<job_id>/results', methods=['GET'])
def get_job_results(job_id):
    """Get the analysis results for a completed job"""
    job_results_dir = RESULTS_FOLDER / job_id
    
    # Check if job directory exists
    if not job_results_dir.exists():
        return jsonify({
            "status": "not_found",
            "message": "Job not found"
        }), 404
    
    # Gather all JSON files (except params.json)
    json_files = list(job_results_dir.glob('*.json'))
    metrics_files = [f for f in json_files if f.name != 'params.json']
    
    if not metrics_files:
        return jsonify({
            "status": "processing",
            "message": "Analysis in progress or no results available"
        }), 404
    
    # Load metrics data from JSON files
    metrics_data = []
    for path in metrics_files:
        with open(path) as f:
            try:
                data = json.load(f)
                # Add the filename to the data
                data['filename'] = path.stem
                metrics_data.append(data)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse JSON file: {path}")
    
    # Sort by fractal dimension (descending)
    metrics_data.sort(
        key=lambda x: (
            x.get('metrics', {}).get('fractal_dimension', 0),
            x.get('metrics', {}).get('r_squared', 0)
        ),
        reverse=True
    )
    
    # Load parameters
    params = {}
    params_file = job_results_dir / 'params.json'
    if params_file.exists():
        with open(params_file) as f:
            try:
                params = json.load(f)
            except json.JSONDecodeError:
                logger.warning("Could not parse params.json")
    
    # Get the number of top samples to return
    max_samples = int(params.get('max_samples', 16))
    top_results = metrics_data[:max_samples]
    
    return jsonify({
        "status": "success",
        "job_id": job_id,
        "params": params,
        "total_grids": len(metrics_data),
        "results": top_results
    })


@app.route('/api/jobs/<job_id>/thumbnail/<grid_id>', methods=['GET'])
def get_thumbnail(job_id, grid_id):
    """Generate and return a thumbnail for a terrain grid"""
    job_results_dir = RESULTS_FOLDER / job_id
    
    # Look for TIF file with the grid ID
    tif_files = list(job_results_dir.glob(f"{grid_id}*.tif"))
    
    if not tif_files:
        return jsonify({
            "status": "error",
            "message": "Grid TIF file not found"
        }), 404
    
    tif_path = tif_files[0]
    
    try:
        # Generate thumbnail from TIF
        with rasterio.open(tif_path) as src:
            # Read the first band
            data = src.read(1)
            
            # Handle no data values
            if src.nodata is not None:
                mask = data != src.nodata
                if mask.any():
                    data = np.ma.array(data, mask=~mask)
            
            # Normalize data for visualization
            data_min, data_max = np.nanpercentile(data, [2, 98])
            data_clipped = np.clip(data, data_min, data_max)
            
            # Scale to 0-255 range for image
            data_norm = ((data_clipped - data_min) / (data_max - data_min) * 255).astype(np.uint8)
            
            # Create a grayscale image
            img = Image.fromarray(data_norm)
            
            # Resize if needed
            max_size = 512
            if max(img.width, img.height) > max_size:
                if img.width > img.height:
                    new_size = (max_size, int(img.height * max_size / img.width))
                else:
                    new_size = (int(img.width * max_size / img.height), max_size)
                img = img.resize(new_size)
            
            # Convert to RGB for better display
            img = img.convert('RGB')
            
            # Save to memory buffer
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            
            return send_file(
                buf,
                mimetype='image/png',
                as_attachment=False,
                download_name=f"{grid_id}.png"
            )
            
    except Exception as e:
        logger.exception(f"Error generating thumbnail for {tif_path}")
        return jsonify({
            "status": "error",
            "message": f"Error generating thumbnail: {str(e)}"
        }), 500


@app.route('/api/jobs/<job_id>/raw/<grid_id>', methods=['GET'])
def get_raw_tif(job_id, grid_id):
    """Return the raw GeoTIFF file for a grid"""
    job_results_dir = RESULTS_FOLDER / job_id
    
    # Look for TIF file with the grid ID
    tif_files = list(job_results_dir.glob(f"{grid_id}*.tif"))
    
    if not tif_files:
        return jsonify({
            "status": "error",
            "message": "Grid TIF file not found"
        }), 404
    
    tif_path = tif_files[0]
    
    return send_file(
        tif_path,
        mimetype='image/tiff',
        as_attachment=True,
        download_name=tif_path.name
    )


if __name__ == '__main__':
    # In production, this should be run with gunicorn instead
    is_prod = os.environ.get('FLASK_ENV') == 'production'
    debug = not is_prod
    host = os.environ.get('HOST', '0.0.0.0' if is_prod else '127.0.0.1')
    port = int(os.environ.get('PORT', 5001))
    
    logger.info(f"Starting Flask app with: host={host}, port={port}, debug={debug}")
    app.run(host=host, port=port, debug=debug) 
