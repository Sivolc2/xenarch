import CONFIG from './config';

/**
 * API service for the XenArch frontend
 * Handles all communication with the backend API
 */
const ApiService = {
  /**
   * Check if the API is available
   * @returns {Promise<boolean>} True if API is available
   */
  checkHealth: async () => {
    try {
      console.log('Checking API health at:', `${CONFIG.API.BASE_URL}${CONFIG.API.HEALTH}`);
      const response = await fetch(`${CONFIG.API.BASE_URL}${CONFIG.API.HEALTH}`);
      if (!response.ok) {
        console.warn('API health check failed with status:', response.status);
        return false;
      }
      return true;
    } catch (error) {
      console.error('API health check error:', error);
      return false;
    }
  },

  /**
   * Upload a file and start the analysis
   * @param {FormData} formData Form data containing the file and analysis parameters
   * @returns {Promise<Object>} Response data with job ID
   */
  uploadFile: async (formData) => {
    console.log('Uploading file to:', `${CONFIG.API.BASE_URL}${CONFIG.API.UPLOAD}`);
    try {
      const response = await fetch(`${CONFIG.API.BASE_URL}${CONFIG.API.UPLOAD}`, {
        method: 'POST',
        body: formData,
      });

      console.log('Upload response status:', response.status);
      const text = await response.text();
      console.log('Upload response text:', text);
      
      try {
        // Try to parse as JSON
        const data = JSON.parse(text);
        
        if (!response.ok) {
          throw new Error(data.message || 'Error uploading file');
        }
        
        return data;
      } catch (jsonError) {
        console.error('JSON parsing error:', jsonError);
        // If not valid JSON, check if there are success indicators in the raw response
        if (text.includes('success') || text.includes('job_id') || text.includes('id')) {
          // Try to extract a job ID
          const idMatch = text.match(/['"]([\w\d-]{8,})['"]/);
          if (idMatch && idMatch[1]) {
            return { job_id: idMatch[1], raw_response: text };
          }
        }
        
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Upload network error:', error);
      throw error;
    }
  },

  /**
   * Check the status of a job
   * @param {string} jobId The job ID to check
   * @returns {Promise<Object>} Status information
   */
  checkJobStatus: async (jobId) => {
    try {
      const response = await fetch(`${CONFIG.API.BASE_URL}${CONFIG.API.JOB_STATUS(jobId)}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error: ${response.status} - ${errorText}`);
      }
      
      const text = await response.text();
      
      try {
        // Try to parse as JSON
        const data = JSON.parse(text);
        return data;
      } catch (jsonError) {
        console.warn('Non-JSON response from status endpoint:', text);
        
        // If not valid JSON, check if it indicates completion
        if (text.includes('complete')) {
          return { status: 'complete', raw_response: text };
        }
        
        return { status: 'processing', message: 'Processing', raw_response: text };
      }
    } catch (error) {
      console.error('Network or parsing error:', error);
      throw error;
    }
  },

  /**
   * Get the results of a job
   * @param {string} jobId The job ID to get results for
   * @returns {Promise<Object>} Job results
   */
  getJobResults: async (jobId) => {
    try {
      const response = await fetch(`${CONFIG.API.BASE_URL}${CONFIG.API.JOB_RESULTS(jobId)}`);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error: ${response.status} - ${errorText}`);
      }
      
      const text = await response.text();
      
      try {
        // Try to parse as JSON
        const data = JSON.parse(text);
        return data;
      } catch (jsonError) {
        console.warn('Non-JSON response from results endpoint:', text);
        // Return raw response if not valid JSON
        return { raw_response: text };
      }
    } catch (error) {
      console.error('Network or parsing error:', error);
      throw error;
    }
  },

  /**
   * Get the thumbnail URL for a grid
   * @param {string} jobId The job ID
   * @param {string} gridId The grid ID
   * @returns {string} Thumbnail URL
   */
  getThumbnailUrl: (jobId, gridId) => {
    return `${CONFIG.API.BASE_URL}${CONFIG.API.THUMBNAIL(jobId, gridId)}`;
  },

  /**
   * Get the raw GeoTIFF URL for a grid
   * @param {string} jobId The job ID
   * @param {string} gridId The grid ID
   * @returns {string} Raw GeoTIFF URL
   */
  getRawTifUrl: (jobId, gridId) => {
    return `${CONFIG.API.BASE_URL}${CONFIG.API.RAW_TIF(jobId, gridId)}`;
  }
};

export default ApiService; 