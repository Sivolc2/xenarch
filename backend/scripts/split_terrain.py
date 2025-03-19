import argparse
from pathlib import Path
import os
import sys

# Add the backend directory to the path if it's not there
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from core.utils.splitter import TerrainSplitter
import logging

def main():
    parser = argparse.ArgumentParser(description='Split terrain file into grids')
    parser.add_argument('-i', '--input', type=str, required=True,
                      help='Input terrain file')
    parser.add_argument('-o', '--output-dir', type=str, default='./data/grids',
                      help='Output directory for grid files')
    parser.add_argument('--grid-size', type=int, default=512,
                      help='Size of grid cells')
    parser.add_argument('--overlap', type=int, default=64,
                      help='Overlap between grids')
    parser.add_argument('-v', '--verbose', action='store_true',
                      help='Enable verbose output')
    parser.add_argument('--cpu-fraction', type=float, default=0.5,
                      help='Fraction of CPUs to use (default: 0.5)')
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    
    splitter = TerrainSplitter(
        grid_size=args.grid_size, 
        overlap=args.overlap,
        cpu_fraction=args.cpu_fraction
    )
    splitter.split_terrain(Path(args.input), Path(args.output_dir))

if __name__ == '__main__':
    main() 