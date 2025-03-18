/**
 * XenArch Frontend Main JavaScript
 * This file contains the main functionality for the XenArch frontend application.
 */

// Global variables to store the current job ID and status
let currentJobId = null;
let statusPollInterval = null;
let statusPollRetries = 0;

// DOM elements
const uploadForm = document.getElementById('upload-form');
const terrainFileInput = document.getElementById('terrain-file');
const submitButton = document.getElementById('submit-button');
const cpuFractionInput = document.getElementById('cpu-fraction');
const cpuFractionValue = document.getElementById('cpu-fraction-value');
const statusCard = document.getElementById('status-card');
const statusMessage = document.getElementById('status-message');
const jobIdElement = document.getElementById('job-id');
const resultsCard = document.getElementById('results-card');
const resultsSummary = document.getElementById('results-summary');
const resultsGrid = document.getElementById('results-grid');
const detailModal = new bootstrap.Modal(document.getElementById('detail-modal'));
const detailModalLabel = document.getElementById('detail-modal-label');
const detailModalContent = document.getElementById('detail-modal-content');
const downloadTifButton = document.getElementById('download-tif');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize event listeners
    uploadForm.addEventListener('submit', handleFormSubmit);
    cpuFractionInput.addEventListener('input', updateCpuFractionDisplay);
    
    // Initialize CPU fraction display
    updateCpuFractionDisplay();
    
    // Check API health on page load
    checkApiHealth();
});

/**
 * Update the displayed CPU fraction value
 */
function updateCpuFractionDisplay() {
    const value = cpuFractionInput.value;
    cpuFractionValue.textContent = `${Math.round(value * 100)}%`;
}

/**
 * Check if the API is available
 */
async function checkApiHealth() {
    try {
        const response = await fetch(`${CONFIG.API.BASE_URL}${CONFIG.API.HEALTH}`);
        if (!response.ok) {
            console.error('API health check failed:', response.statusText);
            // Could display a toast or alert here
        }
    } catch (error) {
        console.error('API health check error:', error);
        // Could display a toast or alert here
    }
}

/**
 * Handle form submission for file upload and analysis
 */
async function handleFormSubmit(event) {
    event.preventDefault();
    
    // Validate inputs
    if (!terrainFileInput.files || terrainFileInput.files.length === 0) {
        alert('Please select a GeoTIFF file to upload.');
        return;
    }
    
    // Get form data
    const formData = new FormData(uploadForm);
    
    // Disable submit button and show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...`;
    
    try {
        // Upload file and start analysis
        const response = await fetch(`${CONFIG.API.BASE_URL}${CONFIG.API.UPLOAD}`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error uploading file');
        }
        
        // Store job ID and show status
        currentJobId = data.job_id;
        showStatusCard(currentJobId);
        
        // Start polling for job status
        startStatusPolling(currentJobId);
        
    } catch (error) {
        console.error('Upload error:', error);
        alert(`Upload failed: ${error.message}`);
        
        // Reset submit button
        submitButton.disabled = false;
        submitButton.innerHTML = `<i class="fas fa-play-circle me-2"></i>Start Analysis`;
    }
}

/**
 * Display the status card with job ID
 */
function showStatusCard(jobId) {
    // Show status card and hide results
    statusCard.style.display = 'block';
    resultsCard.style.display = 'none';
    
    // Update job ID display
    jobIdElement.textContent = `Job ID: ${jobId}`;
    
    // Update status message
    statusMessage.textContent = 'Analysis in progress...';
}

/**
 * Start polling for job status updates
 */
function startStatusPolling(jobId) {
    // Clear any existing interval
    if (statusPollInterval) {
        clearInterval(statusPollInterval);
    }
    
    // Reset retry counter
    statusPollRetries = 0;
    
    // Start polling
    statusPollInterval = setInterval(() => {
        pollJobStatus(jobId);
    }, CONFIG.SETTINGS.STATUS_POLL_INTERVAL);
}

/**
 * Poll the API for job status
 */
async function pollJobStatus(jobId) {
    // Increment retry counter
    statusPollRetries++;
    
    // Check if max retries reached
    if (statusPollRetries > CONFIG.SETTINGS.MAX_STATUS_RETRIES) {
        clearInterval(statusPollInterval);
        statusMessage.textContent = 'Analysis timed out. Please check back later.';
        return;
    }
    
    try {
        const response = await fetch(`${CONFIG.API.BASE_URL}${CONFIG.API.JOB_STATUS(jobId)}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error checking job status');
        }
        
        // Update status based on response
        statusMessage.textContent = data.message;
        
        // If job is complete, fetch and display results
        if (data.status === 'complete') {
            clearInterval(statusPollInterval);
            fetchJobResults(jobId);
        }
        
    } catch (error) {
        console.error('Status polling error:', error);
        statusMessage.textContent = `Error checking status: ${error.message}`;
    }
}

/**
 * Fetch job results and display them
 */
async function fetchJobResults(jobId) {
    try {
        const response = await fetch(`${CONFIG.API.BASE_URL}${CONFIG.API.JOB_RESULTS(jobId)}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Error fetching results');
        }
        
        // Display results
        displayResults(data);
        
        // Reset submit button
        submitButton.disabled = false;
        submitButton.innerHTML = `<i class="fas fa-play-circle me-2"></i>Start Analysis`;
        
    } catch (error) {
        console.error('Results fetch error:', error);
        statusMessage.textContent = `Error fetching results: ${error.message}`;
    }
}

/**
 * Display analysis results in the UI
 */
function displayResults(data) {
    // Show results card
    resultsCard.style.display = 'block';
    
    // Display summary
    resultsSummary.innerHTML = `
        <div class="alert alert-info">
            <h4>Analysis Complete</h4>
            <p><strong>Total Grids Processed:</strong> ${data.total_grids}</p>
            <p><strong>Showing Top:</strong> ${data.results.length} results</p>
        </div>
    `;
    
    // Clear existing results
    resultsGrid.innerHTML = '';
    
    // Add result items to grid
    data.results.forEach((result, index) => {
        const gridId = result.filename || result.grid_id;
        const fractalDimension = result.metrics?.fractal_dimension || 'N/A';
        const rSquared = result.metrics?.r_squared || 'N/A';
        
        const gridItem = document.createElement('div');
        gridItem.className = 'col-md-6 col-lg-4';
        gridItem.innerHTML = `
            <div class="card h-100">
                <img src="${CONFIG.API.BASE_URL}${CONFIG.API.THUMBNAIL(data.job_id, gridId)}" 
                     class="card-img-top" alt="Terrain Grid ${index + 1}"
                     style="height: 200px; object-fit: cover;">
                <div class="card-body">
                    <h5 class="card-title">Grid ${index + 1}</h5>
                    <p class="card-text">
                        <strong>FD:</strong> ${fractalDimension.toFixed(3)}<br>
                        <strong>R²:</strong> ${rSquared.toFixed(3)}
                    </p>
                    <button class="btn btn-sm btn-outline-primary view-details" 
                            data-grid-id="${gridId}" 
                            data-job-id="${data.job_id}"
                            data-index="${index}">
                        View Details
                    </button>
                </div>
            </div>
        `;
        
        // Attach click handler to the "View Details" button
        const detailsButton = gridItem.querySelector('.view-details');
        detailsButton.addEventListener('click', () => {
            openDetailModal(result, data.job_id, index);
        });
        
        resultsGrid.appendChild(gridItem);
    });
}

/**
 * Open the detail modal for a specific grid
 */
function openDetailModal(result, jobId, index) {
    const gridId = result.filename || result.grid_id;
    
    // Set modal title
    detailModalLabel.textContent = `Terrain Grid ${index + 1} Details`;
    
    // Generate modal content
    let modalContent = `
        <div class="text-center mb-4">
            <img src="${CONFIG.API.BASE_URL}${CONFIG.API.THUMBNAIL(jobId, gridId)}" 
                 class="img-fluid border" alt="Terrain Grid ${index + 1}"
                 style="max-height: 300px;">
        </div>
        <div class="row">
            <div class="col-md-6">
                <h5>Fractal Analysis</h5>
                <ul class="list-group mb-3">
                    <li class="list-group-item d-flex justify-content-between">
                        <span>Fractal Dimension:</span>
                        <strong>${result.metrics?.fractal_dimension.toFixed(4) || 'N/A'}</strong>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                        <span>R² Value:</span>
                        <strong>${result.metrics?.r_squared.toFixed(4) || 'N/A'}</strong>
                    </li>
                </ul>
            </div>
            <div class="col-md-6">
                <h5>Grid Information</h5>
                <ul class="list-group mb-3">
                    <li class="list-group-item d-flex justify-content-between">
                        <span>Grid ID:</span>
                        <strong>${gridId}</strong>
                    </li>
    `;
    
    // Add elevation stats if available
    if (result.metrics?.elevation_stats) {
        const stats = result.metrics.elevation_stats;
        modalContent += `
                    <li class="list-group-item d-flex justify-content-between">
                        <span>Min Elevation:</span>
                        <strong>${stats.min.toFixed(2) || 'N/A'}</strong>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                        <span>Max Elevation:</span>
                        <strong>${stats.max.toFixed(2) || 'N/A'}</strong>
                    </li>
                    <li class="list-group-item d-flex justify-content-between">
                        <span>Mean Elevation:</span>
                        <strong>${stats.mean.toFixed(2) || 'N/A'}</strong>
                    </li>
        `;
    }
    
    // Add any other available metrics
    if (result.position) {
        modalContent += `
                    <li class="list-group-item d-flex justify-content-between">
                        <span>Position:</span>
                        <strong>Row ${result.position.row}, Col ${result.position.col}</strong>
                    </li>
        `;
    }
    
    modalContent += `
                </ul>
            </div>
        </div>
    `;
    
    // Set modal content
    detailModalContent.innerHTML = modalContent;
    
    // Configure download button
    downloadTifButton.href = `${CONFIG.API.BASE_URL}${CONFIG.API.RAW_TIF(jobId, gridId)}`;
    downloadTifButton.download = `${gridId}.tif`;
    
    // Show modal
    detailModal.show();
}

/**
 * Reset the UI to initial state
 */
function resetUI() {
    // Clear job ID
    currentJobId = null;
    
    // Clear any polling interval
    if (statusPollInterval) {
        clearInterval(statusPollInterval);
        statusPollInterval = null;
    }
    
    // Hide status and results cards
    statusCard.style.display = 'none';
    resultsCard.style.display = 'none';
    
    // Reset form (optional)
    // uploadForm.reset();
    
    // Reset submit button
    submitButton.disabled = false;
    submitButton.innerHTML = `<i class="fas fa-play-circle me-2"></i>Start Analysis`;
} 