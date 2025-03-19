# XenArch Web Application Troubleshooting Guide

This guide covers common issues that might arise when setting up and running the XenArch web application.

## Backend Issues

### 1. Logging Directory Error

**Error**: 
```
FileNotFoundError: [Errno 2] No such file or directory: '/path/to/backend/backend/logs/app.log'
```

**Solution**:
This error occurs when the logging directory structure is incorrect. The latest version fixes this by creating the proper directory structure. Make sure you're using the updated backend/app.py file.

### 2. CORS Issues

**Error**:
```
Access to fetch at 'http://localhost:5001/api/health' from origin 'http://[::]:8000' has been blocked by CORS policy
```

**Solution**:
The backend includes CORS configuration, but it may need adjustments depending on your environment:

1. Ensure the backend has the correct CORS configuration:
   ```python
   CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
   
   @app.after_request
   def after_request(response):
       response.headers.add('Access-Control-Allow-Origin', '*')
       response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
       response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
       return response
   ```

2. If you continue to have CORS issues, you might need to install a CORS browser extension for development.

### 3. Port Mismatch

**Error**:
```
Failed to fetch: http://localhost:5000/api/health
```

**Solution**:
Ensure that the port in your frontend config matches the port your backend is running on:

1. The backend runs on port 5001 by default (set in app.py)
2. Update the frontend/js/config.js file to use port 5001:
   ```javascript
   BASE_URL: 'http://localhost:5001/api',
   ```

### 4. KeyError in Analysis

**Error**:
```
KeyError: 'metrics'
Error processing file: ... Traceback (most recent call last): ... KeyError: 'metrics'
```

**Solution**:
This error occurs during the analysis phase when the JSON metrics files don't have the expected structure. The issue has been fixed in two ways:

1. The `filter_metrics` function in `scripts/analyze_results.py` now checks if the 'metrics' key exists before trying to access it.
2. Error handling has been added to `main.py` to gracefully handle this error.

If you encounter this error, make sure you're using the latest versions of these files.

### 5. Watchdog Import Error

**Error**:
```
ImportError: cannot import name 'EVENT_TYPE_OPENED' from 'watchdog.events'
```

**Solution**:
This error occurs when Flask's debug mode tries to use the watchdog library but encounters a version incompatibility. There are two ways to fix it:

1. Force Flask to use the basic stat reloader instead of watchdog by changing the app.run() call:
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=True, reloader_type='stat')
   ```

2. Install a compatible version of watchdog:
   ```bash
   pip install watchdog==2.1.9
   ```

The current version of the application uses the first approach for simplicity.

## Frontend Issues

### 1. JavaScript Errors

**Error**:
```
API health check error: TypeError: Failed to fetch
```

**Solution**:
1. Make sure the backend server is running
2. Check that the port in config.js matches the backend port
3. Verify there are no CORS issues (see above)

### 2. Missing Images or Thumbnails

**Error**:
Images not loading in the results view.

**Solution**:
1. Check the browser console for errors
2. Ensure the thumbnail endpoint is working correctly
3. Make sure necessary Python libraries (rasterio, numpy, PIL) are installed

## Setup Steps for a Clean Run

If you're having persistent issues, follow these steps for a clean setup:

1. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   python -m http.server 8000
   ```

3. Open your browser to http://localhost:8000

## Testing the Setup

1. After starting both servers, open your browser's developer tools (F12)
2. Navigate to the Network tab
3. Load the frontend page (http://localhost:8000)
4. Check if the health check request to the backend succeeds
5. If there are any failed requests, check their status and error messages for clues

## Common Installation Issues

### GDAL Installation Problems

If you encounter issues installing the GDAL dependency:

**macOS**:
```bash
brew install gdal
pip install gdal==<version matching the brew installation>
```

**Ubuntu/Debian**:
```bash
sudo apt install gdal-bin libgdal-dev
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip install gdal==<version matching the apt installation>
```

### Python Version Compatibility

This application has been tested with Python 3.8+. If you're using an older version, you might encounter compatibility issues. 