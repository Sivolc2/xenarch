from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np

class Visualizer:
    """Visualization utilities for highlighting and displaying regions of interest"""
    
    @staticmethod
    def highlight_regions(image: np.ndarray, regions: List[Dict], title: str = "Regions of Interest"):
        """Highlight regions of interest on the image"""
        plt.figure(figsize=(12, 8))
        plt.imshow(image, cmap='terrain')
        
        # Plot rectangles for interesting regions
        for region in regions:
            x, y = region['position']
            size = region['size']
            fd = region['fractal_dimension']
            
            rect = plt.Rectangle((x, y), size, size, 
                               fill=False, 
                               color='red', 
                               linewidth=2)
            plt.gca().add_patch(rect)
            plt.text(x, y-10, f'FD: {fd:.2f}', color='white', 
                    bbox=dict(facecolor='red', alpha=0.5))
        
        plt.title(title)
        plt.colorbar(label='Elevation')
        plt.show()
    
    @staticmethod
    def plot_metrics(metrics: Dict):
        """Plot computed metrics"""
        regions = metrics['all_regions']
        interesting = metrics['interesting_regions']
        
        # Plot fractal dimension distribution
        plt.figure(figsize=(10, 6))
        fd_values = [r['fractal_dimension'] for r in regions]
        plt.hist(fd_values, bins=30, alpha=0.7)
        plt.axvline(metrics['stats']['mean_fractal_dim'], 
                   color='r', linestyle='--', 
                   label='Mean')
        plt.title('Distribution of Fractal Dimensions')
        plt.xlabel('Fractal Dimension')
        plt.ylabel('Count')
        plt.legend()
        plt.show() 