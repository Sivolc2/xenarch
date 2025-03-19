import { useState, useEffect, useCallback, useRef } from 'react';
import ApiService from '../services/api';
import CONFIG from '../services/config';

/**
 * Custom hook to manage job status polling and progress tracking
 * @param {Object} options Configuration options
 * @param {String} options.initialJobId Initial job ID (optional)
 * @param {Boolean} options.autoStart Whether to start polling automatically
 * @param {Function} options.onComplete Callback for when the job completes
 * @returns {Object} Job status state and control functions
 */
const useJobStatus = ({ initialJobId = null, autoStart = false, onComplete = null }) => {
  const [jobId, setJobId] = useState(initialJobId);
  const [status, setStatus] = useState('idle'); // idle, loading, processing, complete, error
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState(null); // upload, processing, results
  const [message, setMessage] = useState('');
  const [error, setError] = useState(null);
  const [debugDetails, setDebugDetails] = useState('Initializing debug mode...');
  const [results, setResults] = useState(null);
  
  // Use refs to preserve values in the interval callback
  const retryCountRef = useRef(0);
  const jobIdRef = useRef(initialJobId);
  const statusRef = useRef('idle');
  const intervalRef = useRef(null);
  
  // Update refs when state changes
  useEffect(() => {
    jobIdRef.current = jobId;
    statusRef.current = status;
  }, [jobId, status]);

  // Helper function to add debug messages
  const addDebugMessage = useCallback((message) => {
    console.log(`Debug: ${message}`);
    setDebugDetails(prev => {
      // Add timestamp to message
      const timestamp = new Date().toLocaleTimeString();
      return `${prev}\n[${timestamp}] ${message}`;
    });
  }, []);

  /**
   * Fetch job results from the API
   */
  const fetchResults = useCallback(async (jobId) => {
    if (!jobId) return;
    
    try {
      console.log('Fetching results for job:', jobId);
      addDebugMessage(`Fetching results for job: ${jobId}`);
      setCurrentStage('results');
      setProgress(75);
      
      // Try fetching results
      let resultsData = null;
      try {
        resultsData = await ApiService.getJobResults(jobId);
        console.log('Results data received:', resultsData);
      } catch (fetchError) {
        console.error('Error in initial results fetch:', fetchError);
        addDebugMessage(`Initial results fetch failed - retrying in 1 second...`);
        
        // Try once more after a delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        try {
          resultsData = await ApiService.getJobResults(jobId);
          console.log('Results data received on retry:', resultsData);
        } catch (retryError) {
          console.error('Error in retry fetch:', retryError);
          throw new Error('Failed to fetch results after multiple attempts');
        }
      }
      
      // Handle raw response or missing structure
      if (resultsData && typeof resultsData === 'object') {
        // If the data is missing required structure, try to fix it
        if (!resultsData.job_id) {
          resultsData.job_id = jobId;
        }
        
        if (!resultsData.results && resultsData.metrics) {
          // This might be a direct metrics object, wrap it
          resultsData = {
            ...resultsData,
            job_id: jobId,
            results: [{ 
              grid_id: 'grid_00000_00000', 
              metrics: resultsData.metrics 
            }]
          };
          console.log('Restructured results data:', resultsData);
        }
        
        // For single grid result where the server returns it directly
        if (!resultsData.results && resultsData.grid_id) {
          resultsData = {
            job_id: jobId,
            results: [resultsData],
            total_grids: 1
          };
          console.log('Wrapped single grid result:', resultsData);
        }
      } else {
        // Create minimal valid structure if we got something else
        addDebugMessage('Warning: Unexpected results format - creating placeholder');
        resultsData = {
          job_id: jobId,
          results: [],
          total_grids: 0,
          status: 'success',
          message: 'Results processed with warnings'
        };
      }
      
      // Add short summary of results to debug details
      const resultsSummary = resultsData.results && resultsData.results.length 
        ? `Found ${resultsData.results.length} grid(s) with valid fractal dimensions.` 
        : 'No valid results found.';
      
      addDebugMessage(`Results received: ${resultsSummary}`);
      
      setProgress(100);
      setStatus('complete');
      setMessage('Analysis complete');
      
      // Store results and force a re-render
      setResults(null); // Clear first to ensure state change is detected
      setTimeout(() => {
        setResults(resultsData);
        console.log('Results state updated');
      }, 50);
      
      console.log('Job status hook: Setting complete status and calling onComplete callback');
      addDebugMessage('Analysis complete - showing results');
      
      // Make sure onComplete is called for valid results
      if (onComplete) {
        console.log('Calling onComplete with results');
        setTimeout(() => {
          onComplete(resultsData);
        }, 200); // Longer delay to ensure state updates first
      }
    } catch (error) {
      console.error('Error fetching results:', error);
      setStatus('error');
      setMessage(`Error fetching results: ${error.message}`);
      setError(error.message);
      addDebugMessage(`Error fetching results: ${error.message}`);
    }
  }, [onComplete, addDebugMessage]);

  /**
   * Poll job status from the API
   */
  const pollJobStatus = useCallback(async () => {
    const currentJobId = jobIdRef.current;
    if (!currentJobId) return;
    
    try {
      retryCountRef.current++;
      
      // Add debug info about polling
      console.log(`Polling attempt #${retryCountRef.current} for job: ${currentJobId}`);
      
      if (retryCountRef.current === 1) {
        addDebugMessage(`Starting status polling for job: ${currentJobId}`);
      } else if (retryCountRef.current % 3 === 0) {
        // Add message every 3 attempts instead of 5 for more frequent updates
        addDebugMessage(`Checking job status (attempt #${retryCountRef.current})`);
      }
      
      // Update progress based on retry count (simulated progress)
      const calculatedProgress = Math.min(
        5 + (retryCountRef.current / Math.min(5, CONFIG.SETTINGS.MAX_STATUS_RETRIES)) * 90, 
        95
      );
      setProgress(Math.round(calculatedProgress));
      
      // Check if max retries reached
      if (retryCountRef.current > CONFIG.SETTINGS.MAX_STATUS_RETRIES) {
        setStatus('error');
        setMessage('Analysis timed out. Please try again.');
        setError('Timeout error: Maximum polling attempts exceeded');
        addDebugMessage(`Status polling timed out after ${CONFIG.SETTINGS.MAX_STATUS_RETRIES} retries.`);
        
        clearInterval(intervalRef.current);
        intervalRef.current = null;
        return;
      }
      
      // Make the API request
      const statusData = await ApiService.checkJobStatus(currentJobId);
      console.log('Status response:', statusData);
      
      // Update message if provided
      if (statusData.message) {
        setMessage(statusData.message);
        
        // Only add message to debug if it's new
        if (statusData.message !== message) {
          addDebugMessage(`Status update: ${statusData.message}`);
        }
      }
      
      // Check for specific conditions that indicate completion
      const isCompleteByStatus = statusData.status === 'complete';
      const isCompleteByMessage = statusData.message && 
        (statusData.message.toLowerCase().includes('complete') || 
         statusData.message.toLowerCase().includes('finished'));
      
      // If job is complete by either condition, fetch results
      if (isCompleteByStatus || isCompleteByMessage) {
        console.log(`Job is complete (by ${isCompleteByStatus ? 'status' : 'message'}), clearing interval and fetching results`);
        addDebugMessage(`Server reports job is complete - retrieving results`);
        
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        
        setProgress(95);
        setCurrentStage('results');
        
        // For 1-grid case, add small delay before fetching results 
        // to make sure all server processing is done
        setTimeout(() => {
          // Fetch results immediately
          fetchResults(currentJobId);
        }, 500);
      }
      
      // Special case: If we've polled a few times and still not seeing completion,
      // but we have a metric_count > 0, we should try to fetch results anyway
      if (retryCountRef.current >= 5 && statusData.metrics_count > 0) {
        console.log(`Job has ${statusData.metrics_count} metrics but status not complete, trying to fetch results anyway`);
        addDebugMessage(`Found ${statusData.metrics_count} metrics - attempting to retrieve results`);
        
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        
        setProgress(90);
        setCurrentStage('results');
        
        setTimeout(() => {
          fetchResults(currentJobId);
        }, 500);
      }
    } catch (error) {
      console.error('Error polling job status:', error);
      addDebugMessage(`Error during polling: ${error.message}`);
      
      // Even if there's an error, increment progress to show movement
      setProgress(prev => Math.min(prev + 5, 95));
      
      // If we've had multiple polling errors, try fetching results anyway
      if (retryCountRef.current >= 10) {
        addDebugMessage('Multiple polling errors - attempting to retrieve results anyway');
        clearInterval(intervalRef.current);
        intervalRef.current = null;
        fetchResults(currentJobId);
      }
    }
  }, [fetchResults, message, addDebugMessage]);
  
  /**
   * Start a new job with the given job ID
   */
  const startJob = useCallback((newJobId, fileSize) => {
    if (!newJobId) return;
    
    console.log('Starting job tracking for:', newJobId);
    
    // Clean up any existing polling
    if (intervalRef.current) {
      console.log('Clearing existing interval');
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    // Set new job ID and reset state
    setJobId(newJobId);
    setStatus('processing');
    setProgress(5);
    setCurrentStage('processing');
    setMessage('Analysis in progress...');
    setError(null);
    setDebugDetails(`Job started: ${newJobId}\n`);
    addDebugMessage(`File uploaded successfully, job ID: ${newJobId}`);
    retryCountRef.current = 0;
    
    const isSmallFile = fileSize && fileSize < 1024 * 1024; // Less than 1MB is small
    const pollInterval = isSmallFile ? 1000 : CONFIG.SETTINGS.STATUS_POLL_INTERVAL;
    console.log(`Using poll interval: ${pollInterval}ms (small file: ${isSmallFile})`);
    addDebugMessage(`Starting analysis with ${isSmallFile ? 'small' : 'standard'} file mode`);
    
    // Start polling immediately
    pollJobStatus();
    
    // Then continue polling at regular intervals
    console.log('Setting up polling interval');
    intervalRef.current = setInterval(() => {
      pollJobStatus();
    }, pollInterval);
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [pollJobStatus, addDebugMessage]);
  
  /**
   * Reset job status state
   */
  const resetJob = useCallback(() => {
    console.log('Resetting job status');
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    setJobId(null);
    setStatus('idle');
    setProgress(0);
    setCurrentStage(null);
    setMessage('');
    setError(null);
    setDebugDetails('Ready to process a new terrain file...');
    retryCountRef.current = 0;
    setResults(null);
  }, []);
  
  // Auto-start polling if autoStart is true and we have a job ID
  useEffect(() => {
    if (autoStart && initialJobId) {
      console.log('Auto-starting job tracking');
      startJob(initialJobId);
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [autoStart, initialJobId, startJob]);
  
  return {
    jobId,
    status,
    progress,
    currentStage,
    message,
    error,
    debugDetails,
    results,
    startJob,
    resetJob,
    fetchResults
  };
};

export default useJobStatus; 