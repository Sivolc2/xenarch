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

## Usage

XenArch now provides a unified command-line interface through `main.py` that supports running the complete pipeline or individual components.

### Complete Pipeline
Run the entire analysis pipeline in one command:
```bash
python main.py complete -i terrain.tif -o output_dir [options]
```

Options:
- `--grid-size`: Size of grid cells (default: 512)
- `--overlap`: Overlap between grids (default: 64)
- `--fd-min`: Minimum fractal dimension (default: 0.0)
- `--fd-max`: Maximum fractal dimension (default: 0.8)
- `--r2-min`: Minimum R-squared value (default: 0.8)
- `--max-samples`: Maximum samples to display (default: 16)
- `--plot-output`: Output directory for plots
- `--cpu-fraction`: CPU usage fraction (default: 0.8)
- `-v, --verbose`: Enable verbose output

### Individual Components

#### 1. Split Terrain
Split terrain file into analysis grids:
```bash
python main.py split -i terrain.tif -o output_dir [options]
```

Options:
- `--grid-size`: Size of grid cells
- `--overlap`: Overlap between grids
- `--cpu-fraction`: CPU usage fraction
- `-v, --verbose`: Enable verbose output

#### 2. Generate Metrics
Generate metrics for existing grid files:
```bash
python main.py metrics -i split_dir [options]
```

Options:
- `--cpu-fraction`: CPU usage fraction
- `-v, --verbose`: Enable verbose output

#### 3. Analyze Results
Analyze and visualize the results:
```bash
python main.py analyze -i metrics_dir [options]
```

Options:
- `--fd-min`: Minimum fractal dimension
- `--fd-max`: Maximum fractal dimension
- `--r2-min`: Minimum R-squared value
- `--max-samples`: Maximum samples to display
- `--plot-output`: Output directory for plots
- `--cpu-fraction`: CPU usage fraction
- `-v, --verbose`: Enable verbose output

## Example Workflows

### Basic Analysis
Process the Lunar Reconnaissance Orbiter (LRO) data with default parameters:
```bash
# Run the complete pipeline with defaults
python main.py complete \
    -i ./scripts/processed_data/Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013_sample10.tif \
    -o ./results/lunar_analysis \
    -v

# The above command is equivalent to running these steps separately:
python main.py split \
    -i ./scripts/processed_data/Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013_sample10.tif \
    -o ./results/lunar_analysis/grids \
    -v
python main.py metrics -i ./results/lunar_analysis/grids -v
python main.py analyze -i ./results/lunar_analysis/grids --plot-output ./results/lunar_analysis/plots -v
```

### High-Resolution Analysis
For detailed analysis of the lunar terrain data:
```bash
python main.py complete \
    -i ./scripts/processed_data/Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013_sample10.tif \
    -o ./results/lunar_detailed \
    --grid-size 4048 \
    --overlap 128 \
    --fd-min 0.1 \
    --fd-max 0.9 \
    --r2-min 0.95 \
    --max-samples 25 \
    --cpu-fraction 0.9 \
    -v
```

### Resource-Constrained Processing
For processing on machines with limited resources:
```bash
# Split the terrain with smaller grids
python main.py split \
    -i ./scripts/processed_data/Lunar_LRO_LROC-WAC_Mosaic_global_100m_June2013_sample10.tif \
    -o ./results/lunar_lowres/grids \
    --grid-size 256 \
    --overlap 32 \
    --cpu-fraction 0.5

# Generate metrics with lower CPU usage
python main.py metrics \
    -i ./results/lunar_lowres/grids \
    --cpu-fraction 0.4

# Analyze with stricter filtering
python main.py analyze \
    -i ./results/lunar_lowres/grids \
    --fd-min 0.3 \
    --fd-max 0.7 \
    --r2-min 0.85 \
    --max-samples 9 \
    --plot-output ./results/lunar_lowres/plots
```

### Batch Processing
Example shell script for processing multiple terrain files (when you have more samples):
```bash
#!/bin/bash
for terrain in ./scripts/processed_data/*.tif; do
    filename=$(basename "$terrain" .tif)
    python main.py complete \
        -i "$terrain" \
        -o "./results/${filename}" \
        --grid-size 512 \
        --overlap 64 \
        --fd-min 0.2 \
        --fd-max 0.8 \
        --plot-output "./results/${filename}/plots" \
        -v
done
```

## Dependencies
- numpy
- matplotlib
- rasterio
- scipy
- pandas
- seaborn
- tqdm

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
