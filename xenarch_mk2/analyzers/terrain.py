from pathlib import Path
import numpy as np
import rasterio
import logging
from typing import Union, Dict, List, Generator
from xenarch_mk2.metrics.fractal import FractalAnalyzer

logger = logging.getLogger(__name__)

class TerrainAnalyzer:
    def __init__(self, grid_size: int = 256, chunk_size: int = 1000):
        self.grid_size = grid_size
        self.chunk_size = chunk_size
        self.fractal_analyzer = FractalAnalyzer()
        
    def process_chunk(self, data: np.ndarray, start_y: int, chunk_id: int) -> List[Dict]:
        """Process a single chunk of data"""
        height, width = data.shape
        stride = max(self.grid_size // 4, 1)
        results = []
        
        for y in range(0, height - self.grid_size + 1, stride):
            for x in range(0, width - self.grid_size + 1, stride):
                abs_y = start_y + y
                grid_id = f"chunk_{chunk_id:03d}_grid_{x:05d}_{abs_y:05d}"
                
                grid = data[y:y + self.grid_size, x:x + self.grid_size]
                
                if grid.size == 0 or np.all(np.isnan(grid)):
                    continue
                
                try:
                    fractal_dim, r_squared = self.fractal_analyzer.compute_fractal_dimension(grid)
                    
                    if not np.isnan(fractal_dim) and r_squared > 0.5:
                        results.append({
                            'grid_id': grid_id,
                            'position': (x, abs_y),
                            'size': self.grid_size,
                            'fractal_dimension': fractal_dim,
                            'r_squared': r_squared,
                            'mean_elevation': np.nanmean(grid),
                            'std_elevation': np.nanstd(grid)
                        })
                        
                        # Save grid slice
                        self.save_grid_slice(grid, grid_id)
                        
                except Exception as e:
                    logger.warning(f"Failed to process grid {grid_id}: {str(e)}")
                    continue
                    
        return results
    
    def save_grid_slice(self, grid: np.ndarray, grid_id: str):
        """Save a grid slice as a TIFF file"""
        output_dir = Path("./data/processed_tiffs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{grid_id}.tif"
        
        with rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=grid.shape[0],
            width=grid.shape[1],
            count=1,
            dtype=grid.dtype
        ) as dst:
            dst.write(grid, 1)
    
    def analyze(self, data_source: Union[str, Path]) -> Generator[Dict, None, None]:
        """Analyze terrain features in chunks"""
        with rasterio.open(data_source) as src:
            total_height = src.height
            chunk_id = 0
            
            for start_y in range(0, total_height, self.chunk_size):
                end_y = min(start_y + self.chunk_size + self.grid_size, total_height)
                
                # Read chunk with overlap
                window = rasterio.windows.Window(0, start_y, src.width, end_y - start_y)
                chunk = src.read(1, window=window)
                
                logger.info(f"Processing chunk {chunk_id} ({start_y}-{end_y})")
                
                # Process chunk
                results = self.process_chunk(chunk, start_y, chunk_id)
                
                if results:
                    fractal_dims = [r['fractal_dimension'] for r in results]
                    mean_fd = np.mean(fractal_dims)
                    std_fd = np.std(fractal_dims)
                    
                    interesting_regions = [
                        r for r in results 
                        if abs(r['fractal_dimension'] - mean_fd) > 2 * std_fd
                        and r['r_squared'] > 0.9
                    ]
                    
                    yield {
                        'chunk_id': chunk_id,
                        'start_y': start_y,
                        'end_y': end_y,
                        'all_regions': results,
                        'interesting_regions': interesting_regions,
                        'stats': {
                            'mean_fractal_dim': mean_fd,
                            'std_fractal_dim': std_fd
                        }
                    }
                
                chunk_id += 1 