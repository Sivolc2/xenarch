from pathlib import Path
from typing import Union, Dict, List, Tuple
import numpy as np
from xenarch_mk2.metrics.fractal import FractalAnalyzer
import rasterio
from rasterio.windows import Window

class TerrainAnalyzer:
    """Analyzes terrain features and identifies regions of interest"""
    
    def __init__(self, grid_size: int = 256):
        self.grid_size = grid_size
        self.fractal_analyzer = FractalAnalyzer()
    
    def load_terrain(self, data_source: Union[str, Path]) -> np.ndarray:
        """Load terrain data from file"""
        with rasterio.open(data_source) as src:
            return src.read(1)  # Read first band
    
    def grid_search(self, data: np.ndarray) -> List[Dict]:
        """
        Perform grid search over terrain data
        
        Returns:
            List of dictionaries containing grid information and metrics
        """
        height, width = data.shape
        results = []
        
        for y in range(0, height - self.grid_size + 1, self.grid_size // 2):
            for x in range(0, width - self.grid_size + 1, self.grid_size // 2):
                # Extract grid
                grid = data[y:y + self.grid_size, x:x + self.grid_size]
                
                # Compute metrics
                fractal_dim, r_squared = self.fractal_analyzer.compute_fractal_dimension(grid)
                
                # Store results
                results.append({
                    'position': (x, y),
                    'size': self.grid_size,
                    'fractal_dimension': fractal_dim,
                    'r_squared': r_squared,
                    'mean_elevation': np.mean(grid),
                    'std_elevation': np.std(grid)
                })
        
        return results
    
    def analyze(self, data_source: Union[str, Path]) -> Dict:
        """
        Analyze terrain features
        
        Args:
            data_source: Path to terrain data
            
        Returns:
            Dictionary containing identified features and their locations
        """
        # Load data
        data = self.load_terrain(data_source)
        
        # Perform grid search
        grid_results = self.grid_search(data)
        
        # Find interesting regions (unusual fractal dimensions)
        fractal_dims = [r['fractal_dimension'] for r in grid_results]
        mean_fd = np.mean(fractal_dims)
        std_fd = np.std(fractal_dims)
        
        interesting_regions = [
            r for r in grid_results 
            if abs(r['fractal_dimension'] - mean_fd) > 2 * std_fd  # 2 sigma threshold
            and r['r_squared'] > 0.9  # Good fit only
        ]
        
        return {
            'all_regions': grid_results,
            'interesting_regions': interesting_regions,
            'stats': {
                'mean_fractal_dim': mean_fd,
                'std_fractal_dim': std_fd
            }
        } 