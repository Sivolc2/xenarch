import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Alert } from 'react-bootstrap';
import './styles/App.css';

// Import components
import AnalysisForm from './components/AnalysisForm';
import ProcessingStatusCard from './components/ProcessingStatusCard';
import ResultsCard from './components/ResultsCard';

// Import custom hooks
import useAnalysisForm from './hooks/useAnalysisForm';
import useJobStatus from './hooks/useJobStatus';

// Import services
import ApiService from './services/api';

function App() {
  // State to control which view is active
  const [showResults, setShowResults] = useState(false);
  const [apiError, setApiError] = useState(null);

  // Initialize job status hook
  const jobStatus = useJobStatus({
    initialJobId: null,
    autoStart: false,
    onComplete: (results) => {
      console.log('onComplete callback fired in App with results:', results);
      if (results) {
        console.log('Setting showResults to true from onComplete');
        // Use setTimeout to ensure this happens after state updates
        setTimeout(() => {
          setShowResults(true);
        }, 200);
      }
    },
  });

  // Monitor status changes
  useEffect(() => {
    console.log(`Status changed: ${jobStatus.status}, hasResults: ${!!jobStatus.results}`);
    
    if (jobStatus.status === 'complete' && jobStatus.results) {
      console.log('Setting showResults to true from status effect');
      setShowResults(true);
    }
    
    if (jobStatus.status === 'error') {
      console.error('Job failed with error:', jobStatus.error);
    }
  }, [jobStatus.status, jobStatus.results, jobStatus.error]);

  // Initialize form hook
  const form = useAnalysisForm({
    onUploadStart: () => {
      // Reset any previous results and show status card
      console.log('Upload starting, hiding results');
      setShowResults(false);
      setApiError(null);
      jobStatus.resetJob();
    },
    onUploadSuccess: (response, fileSize) => {
      console.log('Upload successful, starting job polling:', response.job_id);
      // Start polling for job status
      jobStatus.startJob(response.job_id, fileSize);
    },
    onUploadError: (error) => {
      console.error('Upload error in App:', error);
      setApiError(`Upload failed: ${error.message}`);
    },
  });

  // Check API health on mount
  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        const isHealthy = await ApiService.checkHealth();
        if (!isHealthy) {
          console.warn('API health check failed. The backend may not be running.');
          setApiError('Warning: The analysis backend might not be running.');
        } else {
          console.log('API health check passed');
          setApiError(null);
        }
      } catch (error) {
        console.error('Error checking API health:', error);
        setApiError('Error: Cannot connect to the analysis backend.');
      }
    };

    checkApiHealth();
    // This effect runs only once on component mount
  }, []);

  // Debug: Log when showResults changes
  useEffect(() => {
    console.log('showResults changed to:', showResults);
  }, [showResults]);

  // Force-toggle view for debugging if needed
  const debugToggleView = () => {
    if (process.env.NODE_ENV === 'development') {
      setShowResults(prev => !prev);
      console.log('Debug: Manually toggled view');
    }
  };

  // Determine which component to display in the right column
  const renderRightColumn = () => {
    if (showResults && jobStatus.results) {
      console.log('Rendering ResultsCard');
      return <ResultsCard results={jobStatus.results} visible={true} />;
    } else if (jobStatus.status !== 'idle') {
      console.log('Rendering ProcessingStatusCard');
      return <ProcessingStatusCard jobStatus={jobStatus} visible={true} />;
    } else {
      console.log('Rendering default message');
      return (
        <div className="text-center p-5 bg-light rounded">
          <h4 className="text-muted">Upload a file to begin analysis</h4>
        </div>
      );
    }
  };

  return (
    <div className="App">
      <Container>
        {/* Header */}
        <header className="my-4 text-center App-header">
          <h1 onClick={debugToggleView}>XenArch Terrain Analysis</h1>
          <p className="lead">Upload a GeoTIFF file to analyze terrain patterns using fractal dimensions</p>
          
          {apiError && (
            <Alert variant="warning" className="mt-2">
              {apiError}
            </Alert>
          )}
        </header>

        {/* Main Content */}
        <main>
          <Row>
            {/* Left Column - Always show the form */}
            <Col lg={6}>
              <AnalysisForm 
                form={form} 
                disabled={jobStatus.status === 'processing'} 
              />
            </Col>

            {/* Right Column - Use the function to determine what to show */}
            <Col lg={6}>
              {renderRightColumn()}
            </Col>
          </Row>
        </main>

        {/* Footer */}
        <footer className="mt-5 mb-3 text-center text-muted">
          <p>XenArch Terrain Analysis Tool &copy; {new Date().getFullYear()}</p>
        </footer>
      </Container>
    </div>
  );
}

export default App; 