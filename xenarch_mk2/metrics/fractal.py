import numpy as np
from typing import Tuple, List
from scipy.stats import linregress

class FractalAnalyzer:
    """Compute fractal dimension using box-counting method"""
    
    @staticmethod
    def box_count(image: np.ndarray, box_size: int) -> int:
        """
        Count boxes needed to cover the terrain at given box size
        
        Args:
            image: 2D numpy array of height data
            box_size: Size of boxes to use for counting
        """
        # Reshape array into boxes
        shape = (image.shape[0]//box_size, image.shape[1]//box_size, box_size, box_size)
        boxes = image[:shape[0]*box_size, :shape[1]*box_size].reshape(shape)
        
        # Count boxes that contain variation (non-flat terrain)
        return np.sum(np.ptp(boxes, axis=(-1,-2)) > 0)
    
    @staticmethod
    def compute_fractal_dimension(image: np.ndarray) -> Tuple[float, float]:
        """
        Compute fractal dimension using box-counting method
        
        Returns:
            Tuple of (fractal_dimension, r_squared)
        """
        # Use box sizes that are powers of 2
        box_sizes = [2**i for i in range(2, 8)]
        counts = []
        
        for size in box_sizes:
            if size < min(image.shape):
                count = FractalAnalyzer.box_count(image, size)
                counts.append(count)
        
        # Compute fractal dimension from log-log plot
        coeffs = np.polyfit(np.log(box_sizes[:len(counts)]), 
                          np.log(counts), 1)
        
        # R-squared calculation
        _, _, r_value, _, _ = linregress(np.log(box_sizes[:len(counts)]), 
                                       np.log(counts))
        
        return -coeffs[0], r_value**2 