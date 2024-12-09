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

python -m xenarch_mk2.main -f input.tif -o metrics.csv --grid-size 512 -v

