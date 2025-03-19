import numpy as np
from typing import Tuple, List
from scipy.stats import linregress
import logging

logger = logging.getLogger(__name__)

class FractalAnalyzer:
    """Compute fractal dimension using box-counting method"""
    
    @staticmethod
    def box_count(image: np.ndarray, box_size: int) -> int:
        """Count boxes needed to cover the terrain at given box size"""
        try:
            if np.all(np.isnan(image)):
                return 0
                
            # Normalize image to 0-1 range
            image = (image - np.nanmin(image)) / (np.nanmax(image) - np.nanmin(image))
            image = np.nan_to_num(image, nan=0.0)
            
            # Reshape array into boxes
            shape = (image.shape[0]//box_size, image.shape[1]//box_size, box_size, box_size)
            if any(s == 0 for s in shape):
                return 0
                
            boxes = image[:shape[0]*box_size, :shape[1]*box_size].reshape(shape)
            
            # Count boxes with significant variation
            variation = np.ptp(boxes, axis=(-1,-2))
            threshold = np.nanstd(image) * 0.1
            return np.sum(variation > threshold)
            
        except Exception as e:
            logger.error(f"Error in box_count: {str(e)}")
            raise
    
    @staticmethod
    def compute_fractal_dimension(image: np.ndarray) -> Tuple[float, float]:
        """Compute fractal dimension using box-counting method"""
        try:
            if image.size == 0:
                raise ValueError("Empty image provided")
            
            # Use box sizes that are powers of 2
            max_power = int(np.log2(min(image.shape)))
            box_sizes = [2**i for i in range(2, max_power)]
            
            if not box_sizes:
                raise ValueError("No valid box sizes for image dimensions")
            
            counts = []
            valid_sizes = []
            
            for size in box_sizes:
                count = FractalAnalyzer.box_count(image, size)
                if count > 0:
                    counts.append(count)
                    valid_sizes.append(size)
            
            if len(counts) < 2:
                raise ValueError("Not enough valid counts for regression")
            
            # Compute fractal dimension from log-log plot
            log_sizes = np.log(valid_sizes)
            log_counts = np.log(counts)
            
            slope, intercept, r_value, p_value, std_err = linregress(log_sizes, log_counts)
            
            return -slope, r_value**2
            
        except Exception as e:
            logger.error(f"Error computing fractal dimension: {str(e)}")
            raise