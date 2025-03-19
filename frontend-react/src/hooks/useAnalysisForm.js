import { useState, useCallback } from 'react';
import CONFIG from '../services/config';
import ApiService from '../services/api';

/**
 * Custom hook to manage the analysis form state
 * @param {Object} options Configuration options
 * @param {Function} options.onUploadStart Callback for when the upload starts
 * @param {Function} options.onUploadSuccess Callback for when the upload succeeds
 * @param {Function} options.onUploadError Callback for when the upload fails
 * @returns {Object} Form state and control functions
 */
const useAnalysisForm = ({ onUploadStart, onUploadSuccess, onUploadError }) => {
  // Form field states with default values
  const [fileInput, setFileInput] = useState(null);
  const [fileName, setFileName] = useState('');
  const [gridSize, setGridSize] = useState(CONFIG.SETTINGS.DEFAULT_PARAMETERS.grid_size);
  const [overlap, setOverlap] = useState(CONFIG.SETTINGS.DEFAULT_PARAMETERS.overlap);
  const [fdMin, setFdMin] = useState(CONFIG.SETTINGS.DEFAULT_PARAMETERS.fd_min);
  const [fdMax, setFdMax] = useState(CONFIG.SETTINGS.DEFAULT_PARAMETERS.fd_max);
  const [r2Min, setR2Min] = useState(CONFIG.SETTINGS.DEFAULT_PARAMETERS.r2_min);
  const [maxSamples, setMaxSamples] = useState(CONFIG.SETTINGS.DEFAULT_PARAMETERS.max_samples);
  const [cpuFraction, setCpuFraction] = useState(CONFIG.SETTINGS.DEFAULT_PARAMETERS.cpu_fraction);
  
  // Form submission state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);
  
  /**
   * Handle file input change
   */
  const handleFileChange = useCallback((event) => {
    const file = event.target.files[0];
    if (file) {
      setFileInput(file);
      setFileName(file.name);
    } else {
      setFileInput(null);
      setFileName('');
    }
  }, []);
  
  /**
   * Reset the form to default values
   */
  const resetForm = useCallback(() => {
    setFileInput(null);
    setFileName('');
    setGridSize(CONFIG.SETTINGS.DEFAULT_PARAMETERS.grid_size);
    setOverlap(CONFIG.SETTINGS.DEFAULT_PARAMETERS.overlap);
    setFdMin(CONFIG.SETTINGS.DEFAULT_PARAMETERS.fd_min);
    setFdMax(CONFIG.SETTINGS.DEFAULT_PARAMETERS.fd_max);
    setR2Min(CONFIG.SETTINGS.DEFAULT_PARAMETERS.r2_min);
    setMaxSamples(CONFIG.SETTINGS.DEFAULT_PARAMETERS.max_samples);
    setCpuFraction(CONFIG.SETTINGS.DEFAULT_PARAMETERS.cpu_fraction);
    setFormError(null);
  }, []);
  
  /**
   * Validate the form data
   */
  const validateForm = useCallback(() => {
    if (!fileInput) {
      setFormError('Please select a GeoTIFF file to upload.');
      return false;
    }
    
    if (fdMin >= fdMax) {
      setFormError('Fractal Dimension Min must be less than Fractal Dimension Max.');
      return false;
    }
    
    if (r2Min < 0 || r2Min > 1) {
      setFormError('R² Minimum must be between 0 and 1.');
      return false;
    }
    
    setFormError(null);
    return true;
  }, [fileInput, fdMin, fdMax, r2Min]);
  
  /**
   * onUploadStart handler function
   */
  const handleUploadStart = () => {
    setIsSubmitting(true);
    setFormError(null);
    if (onUploadStart) onUploadStart();
  };
  
  /**
   * onUploadSuccess handler function
   * @param {Object} response - Response from the server
   */
  const handleUploadSuccess = (response) => {
    setIsSubmitting(false);
    
    // Log the successful response
    console.log('Upload success response:', response);
    
    // Get the file size if available
    const fileSize = fileInput ? fileInput.size : null;
    
    // Call the provided callback
    if (onUploadSuccess) onUploadSuccess(response, fileSize);
  };
  
  /**
   * onUploadError handler function
   * @param {Error} error - Error object
   */
  const handleUploadError = (error) => {
    console.error('Upload error:', error);
    setIsSubmitting(false);
    setFormError(`Error: ${error.message}`);
    if (onUploadError) onUploadError(error);
  };
  
  /**
   * Submit the form data to the API
   */
  const submitForm = useCallback(async (event) => {
    if (event) event.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      handleUploadStart();
      
      // Create form data
      const formData = new FormData();
      formData.append('file', fileInput);
      formData.append('grid_size', gridSize);
      formData.append('overlap', overlap);
      formData.append('fd_min', fdMin);
      formData.append('fd_max', fdMax);
      formData.append('r2_min', r2Min);
      formData.append('max_samples', maxSamples);
      formData.append('cpu_fraction', cpuFraction);
      
      // Upload file and start analysis
      const response = await ApiService.uploadFile(formData);
      
      handleUploadSuccess(response);
    } catch (error) {
      handleUploadError(error);
    }
  }, [
    fileInput, 
    gridSize, 
    overlap, 
    fdMin, 
    fdMax, 
    r2Min, 
    maxSamples, 
    cpuFraction, 
    onUploadStart, 
    onUploadSuccess, 
    onUploadError,
    validateForm
  ]);
  
  return {
    // Form fields
    fileInput,
    fileName,
    gridSize,
    overlap,
    fdMin,
    fdMax,
    r2Min,
    maxSamples,
    cpuFraction,
    
    // Form state
    isSubmitting,
    formError,
    
    // Handler functions
    handleFileChange,
    setGridSize,
    setOverlap,
    setFdMin,
    setFdMax,
    setR2Min,
    setMaxSamples,
    setCpuFraction,
    
    // Form actions
    submitForm,
    resetForm,
    validateForm
  };
};

export default useAnalysisForm; 