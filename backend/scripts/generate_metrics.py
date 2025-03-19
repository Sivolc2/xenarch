import argparse
from pathlib import Path
import os
import sys

# Add the backend directory to the path if it's not there
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from core.metrics.generator import MetricsGenerator
import logging

def main():
    parser = argparse.ArgumentParser(description='Generate metrics for terrain grids')
    parser.add_argument('-i', '--input-dir', type=str, required=True,
                      help='Input directory containing TIFF files')
    parser.add_argument('-v', '--verbose', action='store_true',
                      help='Enable verbose output')
    parser.add_argument('--cpu-fraction', type=float, default=0.8,
                      help='Fraction of CPUs to use (default: 0.8)')
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    
    generator = MetricsGenerator()
    generator.process_directory(Path(args.input_dir), cpu_fraction=args.cpu_fraction)

if __name__ == '__main__':
    main() 