from pathlib import Path
import rasterio
import json
import logging
from typing import Dict
from .fractal import FractalAnalyzer
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from tqdm import tqdm

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
    
    def process_file(self, tiff_path: Path) -> Dict:
        """Process a single TIFF file (for parallel processing)"""
        try:
            with rasterio.open(tiff_path) as src:
                grid = src.read(1)
            
            metrics = self.compute_metrics(grid)
            
            result = {
                'grid_id': tiff_path.stem,
                'metrics': metrics,
                'metadata': {
                    'crs': str(src.crs),
                    'transform': src.transform.to_gdal(),
                    'size': grid.shape
                }
            }
            
            # Save metrics JSON
            json_path = tiff_path.with_suffix('.json')
            with open(json_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Processed {tiff_path.name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process {tiff_path.name}: {str(e)}")
            return None

    def process_directory(self, input_dir: Path, cpu_fraction: float = 0.5):
        """Generate metrics for all TIFF files in directory using parallel processing"""
        input_dir = Path(input_dir)
        tiff_files = list(input_dir.glob("*.tif"))
        
        n_workers = max(1, int(multiprocessing.cpu_count() * cpu_fraction))
        logger.info(f"Processing {len(tiff_files)} files using {n_workers} workers")
        
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            results = list(tqdm(
                executor.map(self.process_file, tiff_files),
                total=len(tiff_files),
                desc="Generating metrics",
                unit="file"
            ))
        
        successful = [r for r in results if r is not None]
        logger.info(f"Processing complete. Successfully processed: {len(successful)}/{len(tiff_files)}")