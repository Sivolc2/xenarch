from pathlib import Path
import rasterio
from rasterio.windows import Window
import logging
import numpy as np
import multiprocessing
import os

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
    
    def split_terrain(self, input_file: Path, output_dir: Path):
        """Split large terrain file into overlapping grids"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with rasterio.open(input_file) as src:
            height, width = src.height, src.width
            logger.debug(f"Input image dimensions: {width}x{height}")
            
            # Adjust grid size if needed
            adjusted_grid_size = min(self.grid_size, height)
            if adjusted_grid_size != self.grid_size:
                logger.info(f"Adjusting grid size from {self.grid_size} to {adjusted_grid_size} due to image height")
            
            # Adjust overlap proportionally
            overlap_ratio = self.overlap / self.grid_size
            adjusted_overlap = int(adjusted_grid_size * overlap_ratio)
            
            # Calculate steps with overlap
            step_size = adjusted_grid_size - adjusted_overlap
            logger.debug(f"Adjusted grid size: {adjusted_grid_size}, Overlap: {adjusted_overlap}, Step size: {step_size}")
            
            # Calculate number of grids
            n_grids_y = max(1, (height - adjusted_grid_size) // step_size + 1)
            n_grids_x = max(1, (width - adjusted_grid_size) // step_size + 1)
            logger.debug(f"Expected number of grids: {n_grids_x}x{n_grids_y}")
            
            grid_count = 0
            
            for y in range(0, height - adjusted_grid_size + 1, step_size):
                for x in range(0, width - adjusted_grid_size + 1, step_size):
                    # Generate unique grid ID
                    grid_id = f"grid_{x:05d}_{y:05d}"
                    logger.debug(f"Processing grid at position ({x}, {y})")
                    
                    # Read window
                    window = Window(x, y, adjusted_grid_size, adjusted_grid_size)
                    grid = src.read(1, window=window)
                    
                    logger.debug(f"Grid shape: {grid.shape}")
                    
                    # Skip if empty or all zeros (assuming 0 is background)
                    if grid.size == 0 or np.all(grid == 0):
                        logger.debug(f"Skipping grid {grid_id} - empty or background")
                        continue
                    
                    # Save grid
                    output_path = output_dir / f"{grid_id}.tif"
                    
                    try:
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
                            grid_count += 1
                            logger.info(f"Saved grid {grid_id}")
                    except Exception as e:
                        logger.error(f"Failed to save grid {grid_id}: {str(e)}")
            
            logger.info(f"Processing complete. Total grids saved: {grid_count}") 