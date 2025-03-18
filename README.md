# XenArch Terrain Analysis Web Application

This web application provides a user-friendly interface for the XenArch terrain analysis pipeline, allowing users to upload GeoTIFF files, configure analysis parameters, and view the most interesting terrain patches based on fractal dimension metrics.

## Project Overview

The XenArch Terrain Analysis tool processes digital elevation models (DEMs) to identify interesting terrain formations using fractal dimension analysis. This web application adds a user-friendly frontend to the existing command-line tools, making it accessible to non-technical users.

The application consists of two main components:
1. **Frontend**: A responsive web interface for file upload, parameter configuration, and results visualization
2. **Backend**: A Flask API that interfaces with the XenArch pipeline to process terrain data

## Directory Structure

```
xenarch/
├── frontend/               # Frontend web application
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   ├── index.html          # Main HTML page
│   └── README.md           # Frontend documentation
├── backend/                # Backend API service
│   ├── app.py              # Flask application
│   ├── logs/               # API logs
│   └── README.md           # Backend documentation
├── xenarch_mk2/            # Core XenArch analysis library
├── uploads/                # Uploaded terrain files (created at runtime)
├── analysis_results/       # Analysis results (created at runtime)
├── scripts/                # Utility scripts
├── main.py                 # Command-line entry point
└── requirements.txt        # Python dependencies
```

## Setup and Installation

### Prerequisites

- Python 3.8+
- Node.js (optional, for development)
- GDAL dependencies for GeoTIFF processing:
  - On macOS: `brew install gdal`
  - On Ubuntu: `sudo apt install gdal-bin libgdal-dev`

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the Flask API:
   ```bash
   python app.py
   ```

   The API will be available at http://localhost:5000

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. For local development, start a simple HTTP server:
   ```bash
   python -m http.server 8000
   ```

3. Open your browser to http://localhost:8000

## Usage

1. Open the web application in your browser
2. Upload a GeoTIFF terrain file
3. Configure the analysis parameters:
   - Grid Size: Size of terrain patches (e.g., 512x512 pixels)
   - Overlap: Overlap between adjacent grids
   - Fractal Dimension Range: Min and max thresholds
   - R² Minimum: Statistical significance threshold
   - Max Samples: Number of top results to display
   - CPU Usage: Fraction of CPU cores to use for processing
4. Click "Start Analysis" to begin processing
5. View the results, sorted by fractal dimension
6. Click on any terrain patch to view detailed metrics and download options

## Development

### Backend Development

The backend is built with Flask and provides a RESTful API:

- `/api/health` - Health check endpoint
- `/api/upload` - File upload and processing
- `/api/jobs/<job_id>/status` - Check job status
- `/api/jobs/<job_id>/results` - Get analysis results
- `/api/jobs/<job_id>/thumbnail/<grid_id>` - Get grid thumbnails
- `/api/jobs/<job_id>/raw/<grid_id>` - Download raw GeoTIFF

### Frontend Development

The frontend is built with HTML, CSS, and JavaScript, using Bootstrap for responsive design:

- `index.html` - Main page with upload form and results display
- `js/config.js` - Configuration settings
- `js/main.js` - Application logic
- `css/style.css` - Custom styles

## License

[Your license information here]

## Acknowledgments

- [Your acknowledgments here]
