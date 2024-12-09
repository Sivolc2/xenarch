import argparse
from pathlib import Path
from xenarch_mk2.metrics.generator import MetricsGenerator
import logging

def main():
    parser = argparse.ArgumentParser(description='Generate metrics for terrain grids')
    parser.add_argument('-i', '--input-dir', type=str, required=True,
                      help='Input directory containing TIFF files')
    parser.add_argument('-v', '--verbose', action='store_true',
                      help='Enable verbose output')
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    
    generator = MetricsGenerator()
    generator.process_directory(Path(args.input_dir))

if __name__ == '__main__':
    main() 