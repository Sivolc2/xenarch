#!/usr/bin/env python3

import argparse
from pathlib import Path
import logging
from typing import Optional
import sys
import os

# Add the current directory to sys.path if not already there
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Ensure scripts module is available
scripts_dir = os.path.join(current_dir, 'scripts')
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from core.utils.splitter import TerrainSplitter
from core.metrics.generator import MetricsGenerator
import multiprocessing

def setup_logging(verbose: bool) -> None:
    """Configure logging level based on verbosity"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def get_cpu_count(max_fraction: float = 0.8) -> int:
    """Calculate number of CPUs to use based on fraction"""
    cpu_count = multiprocessing.cpu_count()
    return max(1, int(cpu_count * max_fraction))

def split_terrain(args) -> Optional[Path]:
    """Split terrain into grids"""
    logging.info("Starting terrain splitting...")
    
    splitter = TerrainSplitter(
        grid_size=args.grid_size,
        overlap=args.overlap,
        cpu_fraction=args.cpu_fraction
    )
    
    output_dir = Path(args.output_dir)
    splitter.split_terrain(Path(args.input), output_dir)
    return output_dir

def generate_metrics(input_dir: Path, cpu_fraction: float) -> None:
    """Generate metrics for split terrain"""
    logging.info("Generating metrics...")
    
    generator = MetricsGenerator()
    generator.process_directory(input_dir, cpu_fraction=cpu_fraction)

def analyze_results(input_dir: Path, args) -> None:
    """Analyze and visualize results"""
    logging.info("Analyzing results...")
    
    # Import the necessary libraries here instead of trying to import the analyze_results module
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    import seaborn as sns
    from tqdm import tqdm
    import json
    
    # Function to load metrics from the JSON files
    def load_metrics(input_dir):
        metrics = []
        json_files = list(input_dir.glob("*.json"))
        for json_file in tqdm(json_files, desc="Loading metrics", unit="file"):
            if json_file.name == 'params.json':
                continue
            with open(json_file, 'r') as f:
                try:
                    metrics.append(json.load(f))
                except json.JSONDecodeError:
                    logging.warning(f"Could not parse JSON file: {json_file}")
        return metrics
    
    # Function to filter metrics based on conditions
    def filter_metrics(metrics, fd_min, fd_max, r2_min):
        filtered = []
        for metric in metrics:
            if 'metrics' not in metric:
                continue
                
            fd = metric['metrics'].get('fractal_dimension')
            r2 = metric['metrics'].get('r_squared')
            
            if (fd is not None and fd >= fd_min and fd <= fd_max and 
                r2 is not None and r2 >= r2_min):
                filtered.append(metric)
        return filtered
    
    # Set up output directory
    output_dir = Path(args.plot_output) if args.plot_output else input_dir
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Load and filter metrics
        all_metrics = load_metrics(input_dir)
        logging.info(f"Loaded {len(all_metrics)} total samples")
        
        filtered_metrics = filter_metrics(all_metrics, args.fd_min, args.fd_max, args.r2_min)
        logging.info(f"Found {len(filtered_metrics)} samples meeting conditions")
        
        if not filtered_metrics:
            logging.warning("No samples meet the filtering criteria")
            return
        
        # Set seaborn style
        sns.set_theme(style="whitegrid")
        
        # Plot histogram of fractal dimensions
        plt.figure(figsize=(10, 7))
        all_values = [m['metrics']['fractal_dimension'] for m in all_metrics if 'metrics' in m and 'fractal_dimension' in m['metrics']]
        filtered_values = [m['metrics']['fractal_dimension'] for m in filtered_metrics]
        
        plt.hist(all_values, bins=50, alpha=0.5, label='All samples', color='blue')
        plt.hist(filtered_values, bins=50, alpha=0.7, label='Filtered samples', color='red')
        
        plt.xlabel('Fractal Dimension')
        plt.ylabel('Count')
        plt.title('Distribution of Fractal Dimensions')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / 'fractal_histogram.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Sort filtered metrics by fractal dimension
        filtered_metrics.sort(key=lambda x: x['metrics']['fractal_dimension'], reverse=True)
        
        # Get top N samples to display
        max_samples = min(args.max_samples, len(filtered_metrics))
        top_metrics = filtered_metrics[:max_samples]
        
        # Create a summary file with the top results
        with open(output_dir / 'filtered_results.json', 'w') as f:
            json.dump({
                'total_samples': len(all_metrics),
                'filtered_samples': len(filtered_metrics),
                'top_samples': top_metrics
            }, f, indent=2)
        
        logging.info(f"Analysis complete. Results saved to {output_dir}")
        
    except KeyError as e:
        logging.error(f"Error in analyze_results - missing key: {str(e)}")
        logging.info("This is likely due to an inconsistent JSON structure. Continuing with partial results.")
    except Exception as e:
        logging.error(f"Error in analyze_results: {str(e)}")
        if getattr(args, 'verbose', False):
            logging.exception("Detailed error trace:")

def main():
    parser = argparse.ArgumentParser(
        description='XenArch - Terrain Anomaly Detection Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run the complete pipeline
  python cli.py complete -i terrain.tif -o output_dir
  
  # Only split terrain
  python cli.py split -i terrain.tif -o output_dir
  
  # Generate metrics for existing splits
  python cli.py metrics -i split_dir
  
  # Analyze existing metrics
  python cli.py analyze -i metrics_dir
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Complete pipeline command
    complete_parser = subparsers.add_parser('complete', help='Run complete pipeline')
    complete_parser.add_argument('-i', '--input', required=True, help='Input terrain file (GeoTIFF)')
    complete_parser.add_argument('-o', '--output-dir', default='./data/grids', help='Output directory')
    complete_parser.add_argument('--grid-size', type=int, default=512, help='Size of grid cells')
    complete_parser.add_argument('--overlap', type=int, default=64, help='Overlap between grids')
    complete_parser.add_argument('--fd-min', type=float, default=0.0, help='Min fractal dimension')
    complete_parser.add_argument('--fd-max', type=float, default=0.8, help='Max fractal dimension')
    complete_parser.add_argument('--r2-min', type=float, default=0.8, help='Min R-squared value')
    complete_parser.add_argument('--max-samples', type=int, default=16, help='Max samples to display')
    complete_parser.add_argument('--plot-output', help='Output directory for plots')
    complete_parser.add_argument('--cpu-fraction', type=float, default=0.8, help='CPU usage fraction')
    complete_parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    # Split command
    split_parser = subparsers.add_parser('split', help='Split terrain into grids')
    split_parser.add_argument('-i', '--input', required=True, help='Input terrain file')
    split_parser.add_argument('-o', '--output-dir', default='./data/grids', help='Output directory')
    split_parser.add_argument('--grid-size', type=int, default=512, help='Size of grid cells')
    split_parser.add_argument('--overlap', type=int, default=64, help='Overlap between grids')
    split_parser.add_argument('--cpu-fraction', type=float, default=0.8, help='CPU usage fraction')
    split_parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Generate metrics for terrain grids')
    metrics_parser.add_argument('-i', '--input-dir', required=True, help='Input directory with splits')
    metrics_parser.add_argument('--cpu-fraction', type=float, default=0.8, help='CPU usage fraction')
    metrics_parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze and visualize results')
    analyze_parser.add_argument('-i', '--input-dir', required=True, help='Input directory with metrics')
    analyze_parser.add_argument('--fd-min', type=float, default=0.0, help='Min fractal dimension')
    analyze_parser.add_argument('--fd-max', type=float, default=0.8, help='Max fractal dimension')
    analyze_parser.add_argument('--r2-min', type=float, default=0.8, help='Min R-squared value')
    analyze_parser.add_argument('--max-samples', type=int, default=16, help='Max samples to display')
    analyze_parser.add_argument('--plot-output', help='Output directory for plots')
    analyze_parser.add_argument('--cpu-fraction', type=float, default=0.8, help='CPU usage fraction')
    analyze_parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Setup logging
    setup_logging(getattr(args, 'verbose', False))
    
    try:
        if args.command == 'complete':
            # Run complete pipeline
            output_dir = split_terrain(args)
            generate_metrics(output_dir, args.cpu_fraction)
            analyze_results(output_dir, args)
            
        elif args.command == 'split':
            split_terrain(args)
            
        elif args.command == 'metrics':
            generate_metrics(Path(args.input_dir), args.cpu_fraction)
            
        elif args.command == 'analyze':
            analyze_results(Path(args.input_dir), args)
            
    except Exception as e:
        logging.error(f"Error during execution: {str(e)}")
        if getattr(args, 'verbose', False):
            logging.exception("Detailed error trace:")
        sys.exit(1)

if __name__ == '__main__':
    main() 