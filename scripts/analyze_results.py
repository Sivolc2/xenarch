import argparse
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import rasterio
from typing import Dict, List, Tuple
import seaborn as sns
import multiprocessing
import os
from tqdm import tqdm

def get_cpu_count(max_fraction=0.5):
    """Get number of CPUs to use (default: half of available)"""
    cpu_count = multiprocessing.cpu_count()
    return max(1, int(cpu_count * max_fraction))

def load_metrics(input_dir: Path) -> List[Dict]:
    """Load all JSON metrics from directory"""
    metrics = []
    json_files = list(input_dir.glob("*.json"))
    for json_file in tqdm(json_files, desc="Loading metrics", unit="file"):
        with open(json_file, 'r') as f:
            metrics.append(json.load(f))
    return metrics

def filter_metrics(metrics: List[Dict], 
                  conditions: Dict[str, Tuple[float, float]]) -> List[Dict]:
    """Filter metrics based on conditions dictionary
    Example conditions: {'fractal_dimension': (0, 0.8), 'r_squared': (0.8, 1.0)}
    """
    filtered = []
    for metric in metrics:
        meets_conditions = True
        
        # Skip metrics without the required keys
        if 'metrics' not in metric:
            continue
            
        for key, (min_val, max_val) in conditions.items():
            value = metric['metrics'].get(key)
            if value is None or not (min_val <= value <= max_val):
                meets_conditions = False
                break
        if meets_conditions:
            filtered.append(metric)
    return filtered

def plot_histogram_comparison(all_metrics: List[Dict], 
                            filtered_metrics: List[Dict],
                            metric_name: str,
                            title: str = None):
    """Plot histogram with filtered values highlighted"""
    # Increase figure height slightly to accommodate legend below
    plt.figure(figsize=(10, 7))
    
    # Get values
    all_values = [m['metrics'][metric_name] for m in all_metrics]
    filtered_values = [m['metrics'][metric_name] for m in filtered_metrics]
    
    # Plot histograms
    plt.hist(all_values, bins=50, alpha=0.5, label='All samples', color='blue')
    plt.hist(filtered_values, bins=50, alpha=0.7, label='Filtered samples', color='red')
    
    plt.xlabel(metric_name.replace('_', ' ').title())
    plt.ylabel('Count')
    plt.title(title or f'Distribution of {metric_name}')
    
    # Place legend below the plot
    plt.legend(bbox_to_anchor=(0.5, -0.15), 
              loc='upper center', 
              ncol=2,  # Place legend items side by side
              borderaxespad=0.)
    
    plt.grid(True, alpha=0.3)
    
    # Adjust layout to prevent legend cutoff
    plt.tight_layout()

def plot_grid_samples(filtered_metrics: List[Dict], 
                     input_dir: Path,
                     max_samples: int = 16,
                     max_tiff_files: int = 10):
    """Plot grid of filtered TIFF samples, capped at max_tiff_files"""
    n_samples = min(len(filtered_metrics), max_samples)
    if n_samples == 0:
        return
    
    # Calculate grid dimensions
    n_cols = int(np.ceil(np.sqrt(n_samples)))
    n_rows = int(np.ceil(n_samples / n_cols))
    
    fig = plt.figure(figsize=(15, 15))
    gs = GridSpec(n_rows, n_cols, figure=fig)
    
    # Find global min/max for consistent scaling with progress
    all_values = []
    tiff_count = 0
    for metric in tqdm(filtered_metrics[:max_samples], desc="Loading samples", unit="file"):
        if tiff_count >= max_tiff_files:
            break
        tiff_path = input_dir / f"{metric['grid_id']}.tif"
        if tiff_path.exists():
            with rasterio.open(tiff_path) as src:
                data = src.read(1)
                all_values.extend(data.flatten())
            tiff_count += 1
    
    vmin, vmax = np.percentile(all_values, [2, 98])  # Use percentiles to avoid outliers
    
    tiff_count = 0  # Reset counter for plotting
    for idx, metric in enumerate(filtered_metrics[:max_samples]):
        if tiff_count >= max_tiff_files:  # Check if limit is reached
            break
        row = idx // n_cols
        col = idx % n_cols
        
        # Load corresponding TIFF
        tiff_path = input_dir / f"{metric['grid_id']}.tif"
        if not tiff_path.exists():
            continue
            
        with rasterio.open(tiff_path) as src:
            data = src.read(1)
            
            ax = fig.add_subplot(gs[row, col])
            im = ax.imshow(data, 
                         cmap='gray',  # Use grayscale for lunar terrain
                         vmin=vmin,
                         vmax=vmax)
            ax.set_title(f"FD: {metric['metrics']['fractal_dimension']:.3f}\n"
                        f"R²: {metric['metrics']['r_squared']:.3f}")
            ax.axis('off')
            tiff_count += 1  # Increment counter
    
    # Add colorbar
    plt.colorbar(im, ax=fig.axes, label='Elevation', orientation='horizontal', 
                pad=0.02, fraction=0.05)
    
    plt.suptitle('Filtered Terrain Samples', y=1.02)
    plt.tight_layout()

def main():
    parser = argparse.ArgumentParser(description='Analyze and visualize terrain metrics')
    parser.add_argument('-i', '--input-dir', type=str, required=True,
                      help='Input directory containing TIFFs and JSONs')
    parser.add_argument('--fd-range', type=float, nargs=2, default=[0, 0.8],
                      help='Fractal dimension range (min max)')
    parser.add_argument('--r2-min', type=float, default=0.8,
                      help='Minimum R-squared value')
    parser.add_argument('--max-samples', type=int, default=16,
                      help='Maximum number of samples to display')
    parser.add_argument('-o', '--output', type=str,
                      help='Output directory for plots (default: ./data/plots)')
    parser.add_argument('--cpu-fraction', type=float, default=0.5,
                      help='Fraction of CPUs to use (default: 0.5)')
    
    args = parser.parse_args()
    
    # Set number of CPUs to use
    n_cpus = get_cpu_count(args.cpu_fraction)
    os.environ["OMP_NUM_THREADS"] = str(n_cpus)
    os.environ["OPENBLAS_NUM_THREADS"] = str(n_cpus)
    os.environ["MKL_NUM_THREADS"] = str(n_cpus)
    os.environ["VECLIB_MAXIMUM_THREADS"] = str(n_cpus)
    os.environ["NUMEXPR_NUM_THREADS"] = str(n_cpus)
    
    print(f"Using {n_cpus} CPU cores")
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output) if args.output else Path('./data/plots')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load and filter metrics
    all_metrics = load_metrics(input_dir)
    print(f"Loaded {len(all_metrics)} total samples")
    
    conditions = {
        'fractal_dimension': (args.fd_range[0], args.fd_range[1]),
        'r_squared': (args.r2_min, 1.0)
    }
    
    filtered_metrics = filter_metrics(all_metrics, conditions)
    print(f"Found {len(filtered_metrics)} samples meeting conditions")
    
    # Set seaborn style
    sns.set_theme(style="whitegrid")
    
    # Plot fractal dimension histogram
    plot_histogram_comparison(all_metrics, filtered_metrics, 'fractal_dimension',
                            'Distribution of Fractal Dimensions')
    plt.savefig(output_dir / 'fractal_histogram.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Plot grid of samples
    plot_grid_samples(filtered_metrics, input_dir, args.max_samples)
    plt.savefig(output_dir / 'filtered_samples.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    main() 