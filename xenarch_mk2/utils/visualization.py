from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class Visualizer:
    """Visualization utilities for highlighting and displaying regions of interest"""
    
    @staticmethod
    def save_metrics(metrics: Dict, output_path: str):
        """Save metrics to CSV file"""
        try:
            # Convert all_regions to DataFrame
            df = pd.DataFrame(metrics['all_regions'])
            
            # Add a column to mark interesting regions
            interesting_ids = {r['grid_id'] for r in metrics['interesting_regions']}
            df['is_interesting'] = df['grid_id'].isin(interesting_ids)
            
            # Add global statistics
            df['global_mean_fd'] = metrics['stats']['mean_fractal_dim']
            df['global_std_fd'] = metrics['stats']['std_fractal_dim']
            
            # Save to CSV
            df.to_csv(output_path, index=False)
            logger.info(f"Saved metrics to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving metrics: {str(e)}")
    
    @staticmethod
    def highlight_regions(image: np.ndarray, regions: List[Dict], title: str = "Regions of Interest"):
        """Highlight regions of interest on the image"""
        aspect_ratio = image.shape[1] / max(image.shape[0], 1)
        
        base_size = 8
        if aspect_ratio > 10:
            fig_width = base_size * 2
            fig_height = base_size / 2
        else:
            fig_width = min(base_size * 2, base_size * aspect_ratio)
            fig_height = base_size
            
        plt.figure(figsize=(fig_width, fig_height))
        plt.imshow(image, cmap='terrain', aspect='auto')
        
        # Plot rectangles for interesting regions
        for region in regions:
            x, y = region['position']
            size = region['size']
            fd = region['fractal_dimension']
            grid_id = region['grid_id']
            
            rect = plt.Rectangle((x, y), size, size, 
                               fill=False, 
                               color='red', 
                               linewidth=1)
            plt.gca().add_patch(rect)
            
            # Only add labels if there's enough space
            if size > image.shape[1] / 100:
                plt.text(x, y-size/10, 
                        f'ID: {grid_id}\nFD: {fd:.2f}', 
                        color='white', 
                        bbox=dict(facecolor='red', alpha=0.5),
                        fontsize=8)
        
        plt.title(title)
        plt.colorbar(label='Elevation')
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        plt.show()
    
    @staticmethod
    def plot_metrics(metrics: Dict):
        """Plot computed metrics"""
        regions = metrics['all_regions']
        interesting = metrics['interesting_regions']
        
        if not regions:  # Check if we have any regions to plot
            logger.warning("No regions to plot metrics for")
            return
            
        # Plot fractal dimension distribution
        plt.figure(figsize=(10, 6))
        fd_values = [r['fractal_dimension'] for r in regions]
        plt.hist(fd_values, bins=30, alpha=0.7)
        
        if metrics['stats'].get('mean_fractal_dim') is not None:
            plt.axvline(metrics['stats']['mean_fractal_dim'], 
                       color='r', linestyle='--', 
                       label='Mean')
            
        plt.title('Distribution of Fractal Dimensions')
        plt.xlabel('Fractal Dimension')
        plt.ylabel('Count')
        plt.legend()
        
        # Adjust layout without tight_layout
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        plt.show() 