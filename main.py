#!/usr/bin/env python3

import argparse
from pathlib import Path
import logging
from typing import Optional
import sys

from xenarch_mk2.utils.splitter import TerrainSplitter
from xenarch_mk2.metrics.generator import MetricsGenerator
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
    
    # Import here to avoid loading visualization dependencies unless needed
    from scripts.analyze_results import main as analyze_main
    
    try:
        sys.argv = [
            'analyze_results.py',
            '-i', str(input_dir),
            '--fd-range', str(args.fd_min), str(args.fd_max),
            '--r2-min', str(args.r2_min),
            '--max-samples', str(args.max_samples),
            '--cpu-fraction', str(args.cpu_fraction)
        ]
        
        if args.plot_output:
            sys.argv.extend(['-o', args.plot_output])
        
        analyze_main()
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
  python main.py complete -i terrain.tif -o output_dir
  
  # Only split terrain
  python main.py split -i terrain.tif -o output_dir
  
  # Generate metrics for existing splits
  python main.py metrics -i split_dir
  
  # Analyze existing metrics
  python main.py analyze -i metrics_dir
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