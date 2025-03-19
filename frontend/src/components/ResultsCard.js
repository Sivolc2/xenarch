import React, { useEffect } from 'react';
import { Card, Row, Col, Alert, Badge } from 'react-bootstrap';
import ApiService from '../services/api';

/**
 * ResultsCard component for displaying analysis results
 */
const ResultsCard = ({ results, visible = false }) => {
  // Log when visibility or results change
  useEffect(() => {
    console.log(`ResultsCard: visible=${visible}, hasResults=${!!results}`);
    if (results) {
      console.log('Results data summary:', { 
        job_id: results.job_id, 
        total_grids: results.total_grids,
        result_count: results.results?.length || 0
      });
    }
  }, [visible, results]);

  if (!visible || !results) {
    console.log('ResultsCard not rendering: visible=', visible, 'results=', !!results);
    return null;
  }

  // Format metrics for display
  const formatMetric = (value, precision = 3) => {
    return typeof value === 'number' ? value.toFixed(precision) : 'N/A';
  };
  
  // Extract metrics safely from grid data
  const getMetrics = (grid) => {
    if (!grid) return {};
    
    if (grid.metrics) {
      return {
        fractalDimension: grid.metrics.fractal_dimension,
        r2: grid.metrics.r_squared,
        minElevation: grid.metrics.min_elevation,
        maxElevation: grid.metrics.max_elevation,
        meanElevation: grid.metrics.mean_elevation
      };
    }
    
    // Handle flat structure (for legacy or different formats)
    return {
      fractalDimension: grid.fractal_dimension,
      r2: grid.r_squared,
      minElevation: grid.min_elevation,
      maxElevation: grid.max_elevation,
      meanElevation: grid.mean_elevation
    };
  };

  // Make sure results array exists and has items
  const resultsArray = results.results || [];
  const hasResults = resultsArray.length > 0;

  return (
    <Card className="shadow-sm">
      <Card.Header className="bg-success text-white">
        <h3 className="card-title mb-0">Analysis Results</h3>
      </Card.Header>
      <Card.Body>
        {/* Results Summary */}
        <div className="mb-4">
          <h4>Summary</h4>
          <p>
            Found {results.total_grids || 0} total grid cells, 
            {' '}{results.results?.length || 0} matched your criteria.
          </p>

          <Alert variant="info">
            <strong>Job ID: </strong> {results.job_id}
          </Alert>
        </div>

        {/* Results Grid */}
        {hasResults ? (
          <div>
            <h5 className="mb-3">Analysis Results</h5>
            {resultsArray.map((grid, index) => {
              const metrics = getMetrics(grid);
              return (
                <Card key={grid.grid_id || `grid-${index}`} className="mb-3">
                  <Card.Header>
                    <div className="d-flex justify-content-between align-items-center">
                      <h6 className="mb-0">Grid {index + 1}: {grid.grid_id || 'unnamed'}</h6>
                      <Badge bg="primary">FD: {formatMetric(metrics.fractalDimension, 4)}</Badge>
                    </div>
                  </Card.Header>
                  <Card.Body>
                    <Row>
                      <Col md={6}>
                        <p><strong>R² Value:</strong> {formatMetric(metrics.r2, 4)}</p>
                        <p><strong>Min Elevation:</strong> {formatMetric(metrics.minElevation, 1)}</p>
                        <p><strong>Max Elevation:</strong> {formatMetric(metrics.maxElevation, 1)}</p>
                      </Col>
                      <Col md={6}>
                        <div className="text-center">
                          {grid.grid_id && results.job_id ? (
                            <img 
                              src={ApiService.getThumbnailUrl(results.job_id, grid.grid_id)}
                              alt={`Grid ${index + 1}`}
                              className="img-thumbnail"
                              style={{ maxHeight: '150px' }}
                              onError={(e) => {
                                console.log(`Image load error for grid ${grid.grid_id}`);
                                e.target.src = 'https://via.placeholder.com/150?text=No+Image';
                              }}
                            />
                          ) : (
                            <div className="bg-light p-4 text-center text-muted">
                              <em>No thumbnail available</em>
                            </div>
                          )}
                        </div>
                      </Col>
                    </Row>
                  </Card.Body>
                </Card>
              );
            })}
          </div>
        ) : (
          <Alert variant="warning">
            No matching grid cells found that meet the analysis criteria.
          </Alert>
        )}
      </Card.Body>
    </Card>
  );
};

export default ResultsCard; 