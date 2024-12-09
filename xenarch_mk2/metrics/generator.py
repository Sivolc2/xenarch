from pathlib import Path
import rasterio
import json
import logging
from typing import Dict
from .fractal import FractalAnalyzer
import numpy as np

logger = logging.getLogger(__name__)

class MetricsGenerator:
    def __init__(self):
        self.fractal_analyzer = FractalAnalyzer()
    
    def compute_metrics(self, grid: np.ndarray) -> Dict:
        """Compute metrics for a single grid"""
        try:
            fractal_dim, r_squared = self.fractal_analyzer.compute_fractal_dimension(grid)
            
            return {
                'fractal_dimension': fractal_dim,
                'r_squared': r_squared,
                'mean_elevation': float(np.nanmean(grid)),
                'std_elevation': float(np.nanstd(grid)),
                'min_elevation': float(np.nanmin(grid)),
                'max_elevation': float(np.nanmax(grid))
            }
        except Exception as e:
            logger.error(f"Error computing metrics: {str(e)}")
            raise
    
    def process_directory(self, input_dir: Path):
        """Generate metrics for all TIFF files in directory"""
        input_dir = Path(input_dir)
        
        for tiff_file in input_dir.glob("*.tif"):
            try:
                # Read TIFF
                with rasterio.open(tiff_file) as src:
                    grid = src.read(1)
                
                # Compute metrics
                metrics = self.compute_metrics(grid)
                
                # Save metrics JSON
                json_path = tiff_file.with_suffix('.json')
                with open(json_path, 'w') as f:
                    json.dump({
                        'grid_id': tiff_file.stem,
                        'metrics': metrics,
                        'metadata': {
                            'crs': str(src.crs),
                            'transform': src.transform.to_gdal(),
                            'size': grid.shape
                        }
                    }, f, indent=2)
                
                logger.info(f"Processed {tiff_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to process {tiff_file.name}: {str(e)}")
                continue 