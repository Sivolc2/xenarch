from pathlib import Path
import rasterio
from rasterio.windows import Window
import logging
import numpy as np
import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from tqdm import tqdm

logger = logging.getLogger(__name__)

class TerrainSplitter:
    def __init__(self, grid_size: int = 512, overlap: int = 64, cpu_fraction: float = 0.5):
        self.grid_size = grid_size
        self.overlap = overlap
        
        # Set CPU limits
        n_cpus = max(1, int(multiprocessing.cpu_count() * cpu_fraction))
        os.environ["OMP_NUM_THREADS"] = str(n_cpus)
        os.environ["OPENBLAS_NUM_THREADS"] = str(n_cpus)
        os.environ["MKL_NUM_THREADS"] = str(n_cpus)
        os.environ["VECLIB_MAXIMUM_THREADS"] = str(n_cpus)
        os.environ["NUMEXPR_NUM_THREADS"] = str(n_cpus)
        logger.info(f"Using {n_cpus} CPU cores")
    
    def process_grid(self, params):
        """Process a single grid (for parallel processing)"""
        x, y, adjusted_grid_size, adjusted_overlap, src_path, output_dir = params
        
        grid_id = f"grid_{x:05d}_{y:05d}"
        
        try:
            with rasterio.open(src_path) as src:
                window = Window(x, y, adjusted_grid_size, adjusted_grid_size)
                grid = src.read(1, window=window)
                
                if grid.size == 0 or np.all(grid == 0):
                    return None
                
                output_path = output_dir / f"{grid_id}.tif"
                with rasterio.open(
                    output_path,
                    'w',
                    driver='GTiff',
                    height=adjusted_grid_size,
                    width=adjusted_grid_size,
                    count=1,
                    dtype=grid.dtype,
                    crs=src.crs,
                    transform=src.window_transform(window)
                ) as dst:
                    dst.write(grid, 1)
                    return grid_id
        except Exception as e:
            logger.error(f"Failed to process grid {grid_id}: {str(e)}")
            return None

    def split_terrain(self, input_file: Path, output_dir: Path):
        """Split large terrain file into overlapping grids using parallel processing"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with rasterio.open(input_file) as src:
            height, width = src.height, src.width
            logger.debug(f"Input image dimensions: {width}x{height}")
            
            adjusted_grid_size = min(self.grid_size, height)
            if adjusted_grid_size != self.grid_size:
                logger.info(f"Adjusting grid size from {self.grid_size} to {adjusted_grid_size}")
            
            overlap_ratio = self.overlap / self.grid_size
            adjusted_overlap = int(adjusted_grid_size * overlap_ratio)
            step_size = adjusted_grid_size - adjusted_overlap
            
            # Generate parameters for all grids
            grid_params = []
            for y in range(0, height - adjusted_grid_size + 1, step_size):
                for x in range(0, width - adjusted_grid_size + 1, step_size):
                    grid_params.append((x, y, adjusted_grid_size, adjusted_overlap, 
                                     str(input_file), output_dir))
            
            n_workers = max(1, int(multiprocessing.cpu_count() * self.cpu_fraction))
            logger.info(f"Processing {len(grid_params)} grids using {n_workers} workers")
            
            # Process grids in parallel with progress bar
            with ProcessPoolExecutor(max_workers=n_workers) as executor:
                results = list(tqdm(
                    executor.map(self.process_grid, grid_params),
                    total=len(grid_params),
                    desc="Splitting terrain",
                    unit="grid"
                ))
            
            successful = [r for r in results if r is not None]
            logger.info(f"Processing complete. Total grids saved: {len(successful)}") 