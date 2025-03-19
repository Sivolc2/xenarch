import React, { useEffect } from 'react';
import { Card, ListGroup, Badge, Spinner } from 'react-bootstrap';
import { FaFileUpload, FaCogs, FaChartBar } from 'react-icons/fa';

/**
 * ProcessingStatusCard component for displaying job status and progress
 */
const ProcessingStatusCard = ({ 
  jobStatus, 
  visible = false 
}) => {
  const {
    progress,
    currentStage,
    message,
    jobId,
    debugDetails,
    status
  } = jobStatus;

  // Log visibility and status changes for debugging
  useEffect(() => {
    console.log(`ProcessingStatusCard: visible=${visible}, status=${status}, currentStage=${currentStage}`);
  }, [visible, status, currentStage]);

  if (!visible) {
    console.log('ProcessingStatusCard not visible, returning null');
    return null;
  }

  // Define stage indicators
  const stages = [
    { id: 'upload', label: 'File Upload', icon: <FaFileUpload className="me-2" /> },
    { id: 'processing', label: 'Processing', icon: <FaCogs className="me-2" /> },
    { id: 'results', label: 'Results', icon: <FaChartBar className="me-2" /> }
  ];

  // Get stage status
  const getStageStatus = (stageId) => {
    if (currentStage === stageId) {
      return { className: 'badge bg-info', text: 'In Progress' };
    } else if (
      (currentStage === 'processing' && stageId === 'upload') ||
      (currentStage === 'results' && (stageId === 'upload' || stageId === 'processing'))
    ) {
      return { className: 'badge bg-success', text: 'Complete' };
    } else {
      return { className: 'badge bg-secondary', text: 'Waiting' };
    }
  };

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="bg-info text-white">
        <h3 className="card-title mb-0">Processing Status</h3>
      </Card.Header>
      <Card.Body>
        <div className="my-4">
          {/* Spinner instead of Progress Bar */}
          <div className="text-center mb-4">
            <Spinner 
              animation="border" 
              variant="primary" 
              style={{ width: '4rem', height: '4rem' }}
            />
            <h5 className="mt-3">Processing your terrain data...</h5>
          </div>
          
          {/* Processing Stages */}
          <div className="mb-3">
            <ListGroup className="processing-stages">
              {stages.map(stage => {
                const { className, text } = getStageStatus(stage.id);
                return (
                  <ListGroup.Item 
                    key={stage.id}
                    className={currentStage === stage.id ? 'active' : ''}
                    id={`stage-${stage.id}`}
                  >
                    <div className="d-flex justify-content-between align-items-center">
                      <span>{stage.icon} {stage.label}</span>
                      <Badge className={className}>{text}</Badge>
                    </div>
                  </ListGroup.Item>
                );
              })}
            </ListGroup>
          </div>
          
          {/* Debug Details */}
          <h5 className="mb-2">Status Details</h5>
          <div className="bg-light border rounded">
            <pre className="status-details p-3 mb-0" 
                style={{ 
                  maxHeight: '200px', 
                  overflowY: 'auto',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}>
              {debugDetails || 'Waiting for status updates...'}
            </pre>
          </div>

          <h4 className="mt-3">{message}</h4>
          {jobId && <p className="text-muted">Job ID: {jobId}</p>}
        </div>
      </Card.Body>
    </Card>
  );
};

export default ProcessingStatusCard; 