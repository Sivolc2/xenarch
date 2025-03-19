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
│   ├── app.py              # Flask API server
│   ├── cli.py              # Command line interface
│   ├── core/               # Core analysis modules
│   │   ├── utils/          # Utility functions (e.g., terrain splitting)
│   │   ├── metrics/        # Metrics generation (e.g., fractal dimensions)
│   │   ├── analyzers/      # Analytical processing modules
│   │   └── data/           # Data management utilities
│   ├── scripts/            # Utility scripts
│   ├── logs/               # API logs
│   └── README.md           # Backend documentation
├── uploads/                # Uploaded terrain files (created at runtime)
├── analysis_results/       # Analysis results (created at runtime)
├── deployment.md           # Deployment guide
└── README.md               # Project documentation
```

## Setup and Installation

### Prerequisites

- Python 3.8+ (compatible with Python 3.12)
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

3. Upgrade pip and install setuptools (critical for Python 3.12+):
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Start the Flask API:
   ```bash
   python app.py
   ```

   The API will be available at http://localhost:5001

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

## Command Line Interface

The backend also provides a command-line interface for direct access to the pipeline:

```bash
cd backend

# Run the complete pipeline
python cli.py complete -i terrain.tif -o output_dir

# Only split terrain
python cli.py split -i terrain.tif -o output_dir

# Generate metrics for existing splits
python cli.py metrics -i split_dir

# Analyze existing metrics
python cli.py analyze -i metrics_dir
```

## Production Deployment

For production deployment, refer to the detailed deployment guide in [deployment.md](deployment.md). Key steps include:

1. Setting up a server (e.g., Digital Ocean droplet)
2. Configuring Nginx as a reverse proxy
3. Running the backend with Gunicorn
4. Configuring environment variables for production
5. Setting up SSL for secure connections

To deploy in production mode:

1. Set the environment variables in `.env.production`
2. Build the React frontend if applicable
3. Set up Nginx using the provided configuration
4. Use Supervisor to manage the Gunicorn process

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
