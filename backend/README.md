# XenArch Backend

This is the backend API and core analysis module for the XenArch terrain analysis web application. It provides endpoints for uploading GeoTIFF files, running the analysis pipeline, and retrieving the results.

## Directory Structure

```
backend/
├── app.py              # Flask API server
├── cli.py              # Command line interface for pipeline
├── core/               # Core analysis modules
│   ├── utils/          # Utility functions (e.g., terrain splitting)
│   ├── metrics/        # Metrics generation (e.g., fractal dimensions)
│   ├── analyzers/      # Analytical processing modules
│   └── data/           # Data management utilities
├── scripts/            # Utility scripts
│   └── analyze_results.py  # Result analysis and visualization
├── logs/               # Application logs
└── requirements.txt    # Python dependencies
```

## Setup

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- GeoTIFF dependencies:
  - On macOS: `brew install gdal`
  - On Ubuntu: `sudo apt install gdal-bin libgdal-dev`

### Installation

1. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Create necessary directories:

```bash
mkdir -p logs
```

## Running the API

Start the Flask development server:

```bash
python app.py
```

The API will be available at http://localhost:5001.

For production deployment, it's recommended to use Gunicorn or uWSGI instead:

```bash
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

## Using the CLI

The CLI provides direct access to the XenArch terrain analysis pipeline:

```bash
# Run the complete pipeline
python cli.py complete -i terrain.tif -o output_dir

# Only split terrain
python cli.py split -i terrain.tif -o output_dir

# Generate metrics for existing splits
python cli.py metrics -i split_dir

# Analyze existing metrics
python cli.py analyze -i metrics_dir
```

## API Endpoints

### Health Check
- `GET /api/health` - Check if the API is running

### File Upload
- `POST /api/upload` - Upload a GeoTIFF file and start analysis
  - Content-Type: multipart/form-data
  - Parameters:
    - `file`: GeoTIFF file (required)
    - `grid_size`: Size of grid cells (default: 512)
    - `overlap`: Overlap between grids (default: 64)
    - `fd_min`: Min fractal dimension (default: 0.0)
    - `fd_max`: Max fractal dimension (default: 0.8)
    - `r2_min`: Min R-squared value (default: 0.8)
    - `max_samples`: Max samples to display (default: 16)
    - `cpu_fraction`: CPU usage fraction (default: 0.8)

### Job Status and Results
- `GET /api/jobs/<job_id>/status` - Check the status of an analysis job
- `GET /api/jobs/<job_id>/results` - Get the results of a completed job

### Images and Raw Data
- `GET /api/jobs/<job_id>/thumbnail/<grid_id>` - Get a PNG thumbnail of a terrain grid
- `GET /api/jobs/<job_id>/raw/<grid_id>` - Download the raw GeoTIFF file for a grid

## Error Handling

The API returns appropriate HTTP status codes:
- 200: Success
- 400: Bad request (e.g., invalid file format)
- 404: Not found (e.g., job or grid not found)
- 500: Server error (with error details in the response)

Error responses include a JSON object with `status` and `message` fields. 