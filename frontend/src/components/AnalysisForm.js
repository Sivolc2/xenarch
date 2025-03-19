import React from 'react';
import { Card, Form, Button, InputGroup, Alert, Row, Col } from 'react-bootstrap';
import { FaPlayCircle } from 'react-icons/fa';

/**
 * AnalysisForm component for configuring and starting terrain analysis
 */
const AnalysisForm = ({ form, disabled = false }) => {
  const {
    fileName,
    gridSize,
    overlap,
    fdMin,
    fdMax,
    r2Min,
    maxSamples,
    cpuFraction,
    isSubmitting,
    formError,
    handleFileChange,
    setGridSize,
    setOverlap,
    setFdMin,
    setFdMax,
    setR2Min,
    setMaxSamples,
    setCpuFraction,
    submitForm
  } = form;

  // Update CPU Fraction display text
  const cpuFractionText = `${Math.round(cpuFraction * 100)}%`;

  return (
    <Card className="shadow-sm mb-4">
      <Card.Header className="bg-primary text-white">
        <h3 className="card-title mb-0">Upload & Configure</h3>
      </Card.Header>
      <Card.Body>
        <Form onSubmit={submitForm}>
          {/* Show form errors if any */}
          {formError && (
            <Alert variant="danger" className="mb-3">
              {formError}
            </Alert>
          )}

          {/* File Upload */}
          <Form.Group className="mb-3">
            <Form.Label>GeoTIFF Terrain File</Form.Label>
            <Form.Control
              type="file"
              onChange={handleFileChange}
              accept=".tif,.tiff"
              disabled={disabled || isSubmitting}
              required
            />
            <Form.Text className="text-muted">
              Upload a GeoTIFF terrain elevation file.
            </Form.Text>
            {fileName && (
              <Alert variant="info" className="mt-2 p-2 small">
                Selected file: {fileName}
              </Alert>
            )}
          </Form.Group>

          <h4 className="mt-4 mb-3">Analysis Parameters</h4>

          {/* Grid Size */}
          <Form.Group className="mb-3">
            <Form.Label>Grid Size</Form.Label>
            <InputGroup>
              <Form.Control
                type="number"
                value={gridSize}
                onChange={(e) => setGridSize(parseInt(e.target.value, 10))}
                min="128"
                max="2048"
                step="64"
                disabled={disabled || isSubmitting}
                required
              />
              <InputGroup.Text>pixels</InputGroup.Text>
            </InputGroup>
            <Form.Text className="text-muted">
              Size of each terrain patch (larger = more detail but slower).
            </Form.Text>
          </Form.Group>

          {/* Overlap */}
          <Form.Group className="mb-3">
            <Form.Label>Overlap</Form.Label>
            <InputGroup>
              <Form.Control
                type="number"
                value={overlap}
                onChange={(e) => setOverlap(parseInt(e.target.value, 10))}
                min="0"
                max="256"
                step="16"
                disabled={disabled || isSubmitting}
                required
              />
              <InputGroup.Text>pixels</InputGroup.Text>
            </InputGroup>
            <Form.Text className="text-muted">
              Overlap between adjacent grid cells.
            </Form.Text>
          </Form.Group>

          <Row>
            {/* Fractal Dimension Min */}
            <Col md={6} className="mb-3">
              <Form.Group>
                <Form.Label>Fractal Dimension Min</Form.Label>
                <Form.Control
                  type="number"
                  value={fdMin}
                  onChange={(e) => setFdMin(parseFloat(e.target.value))}
                  min="0.0"
                  max="3.0"
                  step="0.1"
                  disabled={disabled || isSubmitting}
                  required
                />
                <Form.Text className="text-muted">
                  Minimum fractal dimension threshold.
                </Form.Text>
              </Form.Group>
            </Col>

            {/* Fractal Dimension Max */}
            <Col md={6} className="mb-3">
              <Form.Group>
                <Form.Label>Fractal Dimension Max</Form.Label>
                <Form.Control
                  type="number"
                  value={fdMax}
                  onChange={(e) => setFdMax(parseFloat(e.target.value))}
                  min="0.0"
                  max="3.0"
                  step="0.1"
                  disabled={disabled || isSubmitting}
                  required
                />
                <Form.Text className="text-muted">
                  Maximum fractal dimension threshold.
                </Form.Text>
              </Form.Group>
            </Col>
          </Row>

          {/* R² Minimum */}
          <Form.Group className="mb-3">
            <Form.Label>R² Minimum</Form.Label>
            <Form.Control
              type="number"
              value={r2Min}
              onChange={(e) => setR2Min(parseFloat(e.target.value))}
              min="0.0"
              max="1.0"
              step="0.05"
              disabled={disabled || isSubmitting}
              required
            />
            <Form.Text className="text-muted">
              Minimum R-squared value for statistical significance.
            </Form.Text>
          </Form.Group>

          {/* Max Samples */}
          <Form.Group className="mb-3">
            <Form.Label>Max Samples to Display</Form.Label>
            <Form.Control
              type="number"
              value={maxSamples}
              onChange={(e) => setMaxSamples(parseInt(e.target.value, 10))}
              min="1"
              max="100"
              step="1"
              disabled={disabled || isSubmitting}
              required
            />
            <Form.Text className="text-muted">
              Maximum number of top samples to display in results.
            </Form.Text>
          </Form.Group>

          {/* CPU Fraction */}
          <Form.Group className="mb-3">
            <Form.Label>CPU Usage</Form.Label>
            <InputGroup>
              <Form.Control
                type="range"
                value={cpuFraction}
                onChange={(e) => setCpuFraction(parseFloat(e.target.value))}
                min="0.1"
                max="1.0"
                step="0.1"
                disabled={disabled || isSubmitting}
                required
              />
              <InputGroup.Text>{cpuFractionText}</InputGroup.Text>
            </InputGroup>
            <Form.Text className="text-muted">
              Fraction of CPU cores to use for processing.
            </Form.Text>
          </Form.Group>

          {/* Submit Button */}
          <div className="mt-4">
            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-100"
              disabled={disabled || isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Uploading...
                </>
              ) : (
                <>
                  <FaPlayCircle className="me-2" />
                  Start Analysis
                </>
              )}
            </Button>
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default AnalysisForm; 