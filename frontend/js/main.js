/**
 * XenArch Frontend Main JavaScript
 * This file contains the main functionality for the XenArch frontend application.
 */

// Global variables to store the current job ID and status
let currentJobId = null;
let statusPollInterval = null;
let statusPollRetries = 0;
let currentProgress = 0;

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

// Progress elements
const progressBar = document.getElementById('progress-bar');
const progressPercentage = document.getElementById('progress-percentage');
const stageUpload = document.getElementById('stage-upload');
const stageProcessing = document.getElementById('stage-processing');
const stageResults = document.getElementById('stage-results');
const stageUploadStatus = document.getElementById('stage-upload-status');
const stageProcessingStatus = document.getElementById('stage-processing-status');
const stageResultsStatus = document.getElementById('stage-results-status');
const toggleDetailsBtn = document.getElementById('toggle-details');
const statusDetails = document.getElementById('status-details');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize event listeners
    uploadForm.addEventListener('submit', handleFormSubmit);
    cpuFractionInput.addEventListener('input', updateCpuFractionDisplay);
    toggleDetailsBtn.addEventListener('click', toggleDetailsVisibility);
    
    // Initialize CPU fraction display
    updateCpuFractionDisplay();
    
    // Check API health on page load
    checkApiHealth();
    
    // Check for existing results (for when the page loads with results already showing)
    checkForExistingResults();
});

/**
 * Toggle the visibility of the status details
 */
function toggleDetailsVisibility() {
    const icon = toggleDetailsBtn.querySelector('i');
    const isCollapsed = icon.classList.contains('fa-chevron-down');
    
    if (isCollapsed) {
        // Expand
        statusDetails.style.maxHeight = '500px';
        icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
    } else {
        // Collapse
        statusDetails.style.maxHeight = '0';
        icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
    }
}

/**
 * Update the progress bar and percentage display
 */
function updateProgress(percent, stage) {
    // Update progress bar
    currentProgress = percent;
    progressBar.style.width = `${percent}%`;
    progressBar.setAttribute('aria-valuenow', percent);
    progressPercentage.textContent = `${percent}%`;
    
    // Update stage indicators based on current stage
    if (stage) {
        updateStageIndicators(stage);
    }
}

/**
 * Update stage indicators based on current processing stage
 */
function updateStageIndicators(stage) {
    // Get all stage elements
    const stages = [
        { elem: stageUpload, status: stageUploadStatus },
        { elem: stageProcessing, status: stageProcessingStatus },
        { elem: stageResults, status: stageResultsStatus }
    ];
    
    // Reset all stages to waiting first
    stages.forEach(s => {
        s.elem.classList.remove('active');
        s.status.className = 'badge bg-secondary';
        s.status.textContent = 'Waiting';
    });
    
    // Mark completed stages
    if (stage === 'upload' || stage === 'processing' || stage === 'results') {
        stages[0].elem.classList.add('active');
        stages[0].status.className = 'badge bg-success';
        stages[0].status.textContent = 'Complete';
    }
    
    if (stage === 'processing' || stage === 'results') {
        stages[1].elem.classList.add('active');
        stages[1].status.className = 'badge bg-success';
        stages[1].status.textContent = 'Complete';
    }
    
    if (stage === 'results') {
        stages[2].elem.classList.add('active');
        stages[2].status.className = 'badge bg-success';
        stages[2].status.textContent = 'Complete';
    }
    
    // Mark current stage as in progress
    if (stage === 'upload') {
        stages[0].elem.classList.add('active');
        stages[0].status.className = 'badge bg-info';
        stages[0].status.textContent = 'In Progress';
    } else if (stage === 'processing') {
        stages[1].elem.classList.add('active');
        stages[1].status.className = 'badge bg-info';
        stages[1].status.textContent = 'In Progress';
    } else if (stage === 'results') {
        stages[2].elem.classList.add('active');
        stages[2].status.className = 'badge bg-info';
        stages[2].status.textContent = 'In Progress';
    }
}

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
    
    // Update UI for debugging - don't disable the button in debug mode
    // but do disable it in normal operation to prevent duplicate submissions
    submitButton.disabled = true;
    submitButton.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>Uploading...`;
    
    // Reset progress indicators
    resetProgressIndicators();
    
    // Show status card 
    statusCard.style.display = 'block';
    resultsCard.style.display = 'none';
    statusDetails.textContent = "Preparing to upload file...";
    
    // Update stage to upload
    updateProgress(10, 'upload');
    
    try {
        // Gather file information
        const file = terrainFileInput.files[0];
        const isSmallFile = file.size < 1024 * 1024; // Less than 1MB is considered "small"
        
        // Display form data being sent
        let formDataDebug = "Form data being sent:\n";
        for (let [key, value] of formData.entries()) {
            if (key === 'file') {
                formDataDebug += `${key}: ${value.name} (${value.size} bytes, ${value.type})\n`;
            } else {
                formDataDebug += `${key}: ${value}\n`;
            }
        }
        statusDetails.textContent = formDataDebug;
        
        // Update progress
        updateProgress(25, 'upload');
        
        // Upload file and start analysis
        const response = await fetch(`${CONFIG.API.BASE_URL}${CONFIG.API.UPLOAD}`, {
            method: 'POST',
            body: formData
        });
        
        // Update progress
        updateProgress(75, 'upload');
        
        // Show raw response for debugging
        const rawResponse = await response.text();
        
        try {
            // Try to parse as JSON
            const data = JSON.parse(rawResponse);
            statusDetails.textContent += "\n\nAPI Response:\n" + JSON.stringify(data, null, 2);
            
            if (!response.ok) {
                throw new Error(data.message || 'Error uploading file');
            }
            
            // Store job ID and show status
            currentJobId = data.job_id;
            jobIdElement.textContent = `Job ID: ${currentJobId}`;
            statusMessage.textContent = 'Analysis in progress...';
            
            // Update to processing stage
            updateProgress(100, 'upload');
            
            // If we know it's a small file, move more quickly to processing stage
            const initialProcessingProgress = isSmallFile ? 20 : 5;
            
            // Short delay before moving to processing stage
            setTimeout(() => {
                updateProgress(initialProcessingProgress, 'processing');
                
                // Start polling for job status
                startStatusPolling(currentJobId);
                
                // For small files, use faster polling interval
                if (isSmallFile && CONFIG.SETTINGS.STATUS_POLL_INTERVAL > 1000) {
                    clearInterval(statusPollInterval);
                    statusPollInterval = setInterval(() => {
                        pollJobStatus(currentJobId);
                    }, 1000); // Poll every second for small files
                }
            }, 500);
            
        } catch (jsonError) {
            // If we couldn't parse the response as JSON, show the raw response
            statusDetails.textContent += "\n\nRaw API Response (not valid JSON):\n" + rawResponse;
            
            // Check if raw response contains common success patterns
            if (rawResponse.includes('success') || rawResponse.includes('job_id') || rawResponse.includes('id')) {
                // Try to extract a job ID if possible
                const idMatch = rawResponse.match(/['"]([\w\d-]{8,})['"]/);
                if (idMatch && idMatch[1]) {
                    currentJobId = idMatch[1];
                    jobIdElement.textContent = `Job ID: ${currentJobId}`;
                    
                    // Continue with processing
                    updateProgress(100, 'upload');
                    setTimeout(() => {
                        updateProgress(5, 'processing');
                        startStatusPolling(currentJobId);
                    }, 500);
                    
                    return; // Exit early
                }
            }
            
            throw new Error('Invalid JSON response from server');
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        statusMessage.textContent = `Error: ${error.message}`;
        statusDetails.textContent += "\n\nError occurred:\n" + error.stack;
        
        // Mark upload as failed
        stageUploadStatus.className = 'badge bg-danger';
        stageUploadStatus.textContent = 'Failed';
        
        // Reset submit button
        submitButton.disabled = false;
        submitButton.innerHTML = `<i class="fas fa-play-circle me-2"></i>Start Analysis`;
    }
}

/**
 * Reset all progress indicators to initial state
 */
function resetProgressIndicators() {
    // Reset progress bar
    updateProgress(0);
    
    // Reset stage indicators
    [stageUploadStatus, stageProcessingStatus, stageResultsStatus].forEach(el => {
        el.className = 'badge bg-secondary';
        el.textContent = 'Waiting';
    });
    
    // Clear status details
    statusDetails.textContent = 'Debug mode - Status details will appear here';
    statusDetails.style.maxHeight = '200px';
    
    // Reset toggle button
    toggleDetailsBtn.querySelector('i').className = 'fas fa-chevron-down';
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
    
    // Get status details element
    const statusDetails = document.getElementById('status-details');
    
    // Check if max retries reached
    if (statusPollRetries > CONFIG.SETTINGS.MAX_STATUS_RETRIES) {
        clearInterval(statusPollInterval);
        statusMessage.textContent = 'Analysis timed out. Please check back later.';
        statusDetails.textContent += "\n\nStatus polling timed out after " + CONFIG.SETTINGS.MAX_STATUS_RETRIES + " retries.";
        
        // Mark processing as failed
        stageProcessingStatus.className = 'badge bg-danger';
        stageProcessingStatus.textContent = 'Failed';
        return;
    }
    
    try {
        // Update status to show we're polling
        statusDetails.textContent += "\n\nPolling attempt #" + statusPollRetries + "...";
        
        // Calculate and update progress based on retry count
        // This is a simulation since we don't have real progress data
        // For small images with only 1 grid, increase progress more aggressively
        const calculatedProgress = Math.min(5 + (statusPollRetries / Math.min(5, CONFIG.SETTINGS.MAX_STATUS_RETRIES)) * 90, 95);
        updateProgress(Math.round(calculatedProgress), 'processing');
        
        // Make the request
        const response = await fetch(`${CONFIG.API.BASE_URL}${CONFIG.API.JOB_STATUS(jobId)}`);
        
        // Get the raw response
        const rawResponse = await response.text();
        
        try {
            // Try parsing as JSON
            const data = JSON.parse(rawResponse);
            statusDetails.textContent += "\nStatus response: " + JSON.stringify(data, null, 2);
            
            if (!response.ok) {
                throw new Error(data.message || 'Error checking job status');
            }
            
            // Update status based on response
            statusMessage.textContent = data.message || 'Analysis in progress...';
            
            // Check if the response contains progress information directly
            if (data.progress !== undefined) {
                // If the API provides progress info, use it directly
                updateProgress(data.progress, 'processing');
            }
            
            // If job is complete, fetch and display results
            if (data.status === 'complete') {
                clearInterval(statusPollInterval);
                updateProgress(100, 'processing');
                setTimeout(() => {
                    updateProgress(50, 'results');
                    fetchJobResults(jobId);
                }, 500);
            }
            
        } catch (jsonError) {
            // If we couldn't parse the response as JSON, show the raw response
            statusDetails.textContent += "\nRaw status response (not valid JSON):\n" + rawResponse;
            
            // Even for non-JSON responses, check if "complete" is mentioned and process
            if (rawResponse.includes('complete')) {
                clearInterval(statusPollInterval);
                updateProgress(100, 'processing');
                setTimeout(() => {
                    updateProgress(50, 'results');
                    fetchJobResults(jobId);
                }, 500);
            } else {
                throw new Error('Invalid JSON response from server');
            }
        }
        
    } catch (error) {
        console.error('Status polling error:', error);
        statusMessage.textContent = `Error checking status: ${error.message}`;
        statusDetails.textContent += "\n\nError during polling:\n" + error.stack;
        
        // Even if there's an error, increment the progress a bit to show some movement
        const currentWidth = parseInt(progressBar.style.width) || 0;
        if (currentWidth < 90) {
            updateProgress(currentWidth + 5, 'processing');
        }
    }
}

/**
 * Fetch job results from the API
 */
async function fetchJobResults(jobId) {
    // Get status details element
    const statusDetails = document.getElementById('status-details');
    statusDetails.textContent += "\n\nFetching results...";
    
    // Force update progress to show results stage is active
    updateProgress(75, 'results');
    
    try {
        // Make the request
        statusDetails.textContent += "\nRequesting: " + CONFIG.API.BASE_URL + CONFIG.API.JOB_RESULTS(jobId);
        const response = await fetch(`${CONFIG.API.BASE_URL}${CONFIG.API.JOB_RESULTS(jobId)}`);
        
        // Get the raw response
        const rawResponse = await response.text();
        
        try {
            // Try parsing as JSON
            const data = JSON.parse(rawResponse);
            statusDetails.textContent += "\nResults response: " + JSON.stringify(data, null, 2);
            
            if (!response.ok) {
                throw new Error(data.message || 'Error fetching results');
            }
            
            // Update progress to completion
            updateProgress(100, 'results');
            
            // Small delay before showing results to ensure UI updates are visible
            setTimeout(() => {
                // Display results
                displayResults(data);
                
                // Update status message
                statusMessage.textContent = 'Analysis complete';
            }, 500);
            
        } catch (jsonError) {
            // If we couldn't parse the response as JSON, show the raw response
            statusDetails.textContent += "\nRaw results response (not valid JSON):\n" + rawResponse;
            
            // If we get any response, still try to mark as complete
            updateProgress(100, 'results');
            
            // Update message based on error
            statusMessage.textContent = 'Analysis complete (with format issues)';
            
            // Display an error-handling version of results
            displayErrorResults(rawResponse);
            
            // Log the error
            throw new Error('Invalid JSON response from server');
        }
        
    } catch (error) {
        console.error('Error fetching results:', error);
        statusMessage.textContent = `Error fetching results: ${error.message}`;
        statusDetails.textContent += "\n\nError fetching results:\n" + error.stack;
        
        // Mark results as failed
        stageResultsStatus.className = 'badge bg-danger';
        stageResultsStatus.textContent = 'Failed';
    }
}

/**
 * Display error-state results in case of API issues
 */
function displayErrorResults(rawResponse) {
    // Show results card
    statusCard.style.display = 'none';
    resultsCard.style.display = 'block';
    
    // Get the necessary elements
    const resultsSummary = document.getElementById('results-summary');
    const resultsGrid = document.getElementById('results-grid');
    
    // Clear previous results
    resultsSummary.innerHTML = '';
    resultsGrid.innerHTML = '';
    
    // Add error summary
    resultsSummary.innerHTML = `
        <div class="alert alert-warning">
            <h4>Results Format Issue</h4>
            <p>The server returned results in an unexpected format. Some visualizations may not be available.</p>
            <p>If this persists, please contact support with Job ID: ${currentJobId || 'Unknown'}</p>
        </div>
    `;
    
    // Try to display any information we can extract from the raw response
    if (rawResponse && rawResponse.includes('grid')) {
        resultsGrid.innerHTML = `
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Raw Response Data</h5>
                        <pre class="bg-light p-3" style="max-height: 300px; overflow-y: auto;">${rawResponse}</pre>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Reset submit button
    submitButton.disabled = false;
    submitButton.innerHTML = `<i class="fas fa-play-circle me-2"></i>Start Analysis`;
}

/**
 * Display results in the UI
 */
function displayResults(data) {
    // Get status details element
    const statusDetails = document.getElementById('status-details');
    statusDetails.textContent += "\n\nDisplaying results...";
    
    // Show results card and hide status
    statusCard.style.display = 'none';
    resultsCard.style.display = 'block';
    
    // Get the necessary elements
    const resultsSummary = document.getElementById('results-summary');
    const resultsGrid = document.getElementById('results-grid');
    
    // Clear previous results
    resultsSummary.innerHTML = '';
    resultsGrid.innerHTML = '';
    
    // Add summary
    resultsSummary.innerHTML = `
        <h4>Summary</h4>
        <p>Found ${data.total_grids} total grid cells, ${data.results.length} matched your criteria.</p>
        <p>Showing top ${data.results.length} results sorted by fractal dimension.</p>
    `;
    
    // Add grid items
    data.results.forEach((result, index) => {
        // Create grid item
        const gridItem = document.createElement('div');
        gridItem.className = 'col-md-6 col-lg-3';
        gridItem.innerHTML = `
            <div class="card h-100">
                <img src="${CONFIG.API.BASE_URL}${CONFIG.API.THUMBNAIL(data.job_id, result.grid_id)}" 
                     class="card-img-top" alt="Terrain Grid ${result.grid_id}">
                <div class="card-body">
                    <h5 class="card-title">${result.grid_id}</h5>
                    <p class="card-text">
                        <strong>FD:</strong> ${result.metrics.fractal_dimension.toFixed(3)}<br>
                        <strong>R²:</strong> ${result.metrics.r_squared.toFixed(3)}
                    </p>
                </div>
                <div class="card-footer">
                    <button class="btn btn-sm btn-outline-primary view-details" data-index="${index}">View Details</button>
                </div>
            </div>
        `;
        
        resultsGrid.appendChild(gridItem);
        
        // Add event listener to view details button
        gridItem.querySelector('.view-details').addEventListener('click', () => {
            openDetailModal(result, data.job_id, index);
        });
    });
    
    // Log debug info
    statusDetails.textContent += "\nDisplayed " + data.results.length + " results.";
    
    // Reset submit button
    submitButton.disabled = false;
    submitButton.innerHTML = `<i class="fas fa-play-circle me-2"></i>Start Analysis`;
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
    
    // Reset status poll retries
    statusPollRetries = 0;
    
    // Reset progress indicators
    resetProgressIndicators();
    
    // Hide status and results cards
    statusCard.style.display = 'none';
    resultsCard.style.display = 'none';
    
    // Reset form (optional)
    // uploadForm.reset();
    
    // Reset submit button
    submitButton.disabled = false;
    submitButton.innerHTML = `<i class="fas fa-play-circle me-2"></i>Start Analysis`;
}

/**
 * Check if results are already loaded/visible when the page first loads
 * This handles the case where the page refreshes but results are already displayed
 */
function checkForExistingResults() {
    // Check if results card is visible
    if (resultsCard.style.display === 'block' || getComputedStyle(resultsCard).display !== 'none') {
        // Results are already showing, update progress indicators to reflect completed state
        updateProgress(100, 'results');
        statusMessage.textContent = 'Analysis complete';
        
        // Get any job ID if available
        const jobIdText = jobIdElement.textContent;
        if (jobIdText) {
            const match = jobIdText.match(/Job ID: ([\w-]+)/);
            if (match && match[1]) {
                currentJobId = match[1];
            }
        }
    }
} 