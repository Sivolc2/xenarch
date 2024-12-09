# XenArch - Terrain Anomaly Detection

A tool for analyzing terrain data to identify regions of interest using fractal analysis and other metrics.

## Current Implementation

### Input
- GeoTIFF terrain data
- Configurable grid size and processing parameters

### Processing Pipeline
1. **Chunked Processing**
   - Processes large terrain files in manageable chunks
   - Adaptive grid sizing based on terrain dimensions
   - Overlapping grids for continuous analysis

2. **Fractal Analysis**
   - Box-counting method for fractal dimension calculation
   - Adaptive thresholding for terrain variation
   - R-squared validation for fit quality

3. **Output Organization**
   - Processed grid slices saved as individual TIFFs
   - Corresponding metrics stored in JSON files
   - Unique grid IDs for easy cross-referencing
   - Summary statistics for each chunk

### Output Structure
./data/processed_tiffs/
├── chunk_000_grid_00000_00000.tif
├── chunk_000_grid_00000_00000.json
└── ...


Each JSON contains:
- Grid identifier
- Fractal dimension
- R-squared value
- Elevation statistics
- Position information
- Grid size

## Next Steps

### Phase 2: Enhanced Analysis
1. **Additional Metrics**
   - Implement local contrast measures
   - Add texture analysis
   - Consider topographic position index (TPI)
   - Calculate slope and aspect variations

2. **Machine Learning Integration**
   - Train models on known anomalous features
   - Implement unsupervised clustering
   - Add feature importance analysis

3. **Visualization Improvements**
   - Interactive visualization dashboard
   - 3D terrain rendering
   - Overlay capabilities for multiple metrics
   - Time series support for temporal analysis

4. **Performance Optimization**
   - Parallel processing for chunks
   - GPU acceleration for fractal calculations
   - Memory optimization for large datasets
   - Caching system for intermediate results

5. **Validation Tools**
   - Ground truth comparison tools
   - Statistical validation methods
   - Cross-validation with known features
   - Uncertainty quantification

### Phase 3: Feature Enhancement
1. **Data Sources**
   - Support for multiple data formats
   - Integration with online terrain databases
   - Multi-spectral data support
   - Point cloud data handling

2. **Analysis Tools**
   - Automated report generation
   - Batch processing capabilities
   - Custom metric definition interface
   - Region comparison tools

3. **User Interface**
   - Command-line interface improvements
   - Web interface for visualization
   - API for external integration
   - Configuration management system

## Usage

### Split Dataset
python scripts/split_terrain.py -i ./xenarch_mk2/data/Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013.tif -o ./data/grids --cpu-fraction 0.8

### Compute Metrics
python scripts/generate_metrics.py -i ./data/grids -v

### Analyze Results
python scripts/analyze_results.py -i ./data/grids --fd-range 0.2 0.6 --r2-min 0.9 --cpu-fraction 0.8

### Parameters
- `-f, --file`: Input terrain file (GeoTIFF)
- `-d, --data-dir`: Data directory
- `--grid-size`: Size of analysis grid cells
- `-v, --verbose`: Enable verbose output
- `-o, --output`: Output path for metrics

## Dependencies
- numpy
- matplotlib
- rasterio
- scipy
- pandas