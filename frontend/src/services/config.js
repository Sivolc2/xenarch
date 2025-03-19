/**
 * XenArch Frontend Configuration
 * This file contains configuration settings for the XenArch frontend application.
 */

// Determine if we're in production based on environment variable or hostname
const isProduction = process.env.NODE_ENV === 'production' || 
    window.location.hostname !== 'localhost';

// Base URL configuration for different environments
const getBaseUrl = () => {
    if (isProduction) {
        // In production, API requests are relative to the current domain
        // This works with the nginx configuration that proxies /api requests
        return '/api';
    } else {
        // In development, connect to local backend server
        return 'http://localhost:5001/api';
    }
};

const CONFIG = {
    // API endpoints
    API: {
        // Base URL for the API - changes based on environment
        BASE_URL: getBaseUrl(),
        
        // Health check endpoint
        HEALTH: '/health',
        
        // File upload endpoint
        UPLOAD: '/upload',
        
        // Job status endpoint (requires job_id)
        JOB_STATUS: (jobId) => `/jobs/${jobId}/status`,
        
        // Job results endpoint (requires job_id)
        JOB_RESULTS: (jobId) => `/jobs/${jobId}/results`,
        
        // Thumbnail image endpoint (requires job_id and grid_id)
        THUMBNAIL: (jobId, gridId) => `/jobs/${jobId}/thumbnail/${gridId}`,
        
        // Raw GeoTIFF download endpoint (requires job_id and grid_id)
        RAW_TIF: (jobId, gridId) => `/jobs/${jobId}/raw/${gridId}`
    },
    
    // Application settings
    SETTINGS: {
        // Polling interval for job status (in milliseconds)
        STATUS_POLL_INTERVAL: 5000,
        
        // Maximum retries for polling job status
        MAX_STATUS_RETRIES: 60,  // 5 minutes at 5-second intervals
        
        // Default parameters (these should match the backend defaults)
        DEFAULT_PARAMETERS: {
            grid_size: 512,
            overlap: 64,
            fd_min: 0.0,
            fd_max: 0.8,
            r2_min: 0.8,
            max_samples: 16,
            cpu_fraction: 0.8
        }
    }
};

export default CONFIG; 