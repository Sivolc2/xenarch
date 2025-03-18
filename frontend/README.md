# XenArch Frontend

This is the frontend web application for XenArch, providing a user-friendly interface for uploading GeoTIFF files, configuring terrain analysis parameters, and viewing results.

## Features

- Upload GeoTIFF files for terrain analysis
- Configure analysis parameters (grid size, overlap, fractal dimension thresholds, etc.)
- View analysis results with thumbnails of the most interesting terrain patches
- Detailed view for each terrain grid with metrics and download options

## Project Structure

```
frontend/
├── css/                # Stylesheets
│   └── style.css       # Custom styles
├── js/                 # JavaScript
│   ├── config.js       # Configuration (API endpoints, etc.)
│   └── main.js         # Main application logic
├── index.html          # Main HTML page
└── README.md           # This file
```

## Setup

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, Edge)
- The XenArch backend API must be running and accessible

### Configuration

Edit `js/config.js` to set the correct API endpoint:

```javascript
const CONFIG = {
    API: {
        BASE_URL: 'http://localhost:5000/api',
        // ... other settings ...
    },
    // ... other settings ...
};
```

Change the `BASE_URL` to match your backend API's address and port.

## Deployment Options

### Option 1: Simple Local Development

For local development, you can use Python's built-in HTTP server:

```bash
# Navigate to the frontend directory
cd frontend

# Start a simple HTTP server on port 8000
python -m http.server 8000
```

Then open your browser to `http://localhost:8000`

### Option 2: Using a Web Server

For production, deploy the frontend files to a web server like Nginx or Apache.

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/xenarch/frontend;
    index index.html;
    
    # Serve static files
    location / {
        try_files $uri $uri/ =404;
    }
}
```

### Option 3: Using Docker

A simple Dockerfile for the frontend might look like:

```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
```

Build and run:

```bash
docker build -t xenarch-frontend .
docker run -d -p 8080:80 xenarch-frontend
```

## Browser Compatibility

The frontend is compatible with:
- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)

## Development Notes

- The frontend uses Bootstrap 5 for responsive design
- Custom CSS is in `css/style.css`
- JavaScript follows a modular approach with configuration separated from business logic 