from pathlib import Path
from typing import Union, List, Dict
from xenarch_mk2.analyzers.terrain import TerrainAnalyzer
from xenarch_mk2.utils.visualization import Visualizer
import rasterio
import argparse
import logging
import numpy as np

class XenArchAnalyzer:
    def __init__(self, data_dir: Union[str, Path]):
        self.data_dir = Path(data_dir)
        self.validate_data_directory()
        self.terrain_analyzer = TerrainAnalyzer()
        self.visualizer = Visualizer()
    
    def validate_data_directory(self):
        """Ensure data directory exists, create if not"""
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True)
    
    def analyze_region(self, input_source: Union[str, Path]) -> Dict:
        """
        Analyze a region for anomalies/interesting features
        
        Args:
            input_source: Path to image/data file or URL
            
        Returns:
            Dictionary containing analysis results
        """
        # Analyze terrain
        results = self.terrain_analyzer.analyze(input_source)
        
        # Visualize results
        with rasterio.open(input_source) as src:
            data = src.read(1)
            self.visualizer.highlight_regions(data, results['interesting_regions'])
            self.visualizer.plot_metrics(results)
        
        return results

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Analyze terrain data for anomalous features using fractal analysis'
    )
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='Path to input terrain file (GeoTIFF)',
        default='./data/test.tif'
    )
    parser.add_argument(
        '-d', '--data-dir',
        type=str,
        help='Path to data directory',
        default='./data'
    )
    parser.add_argument(
        '--grid-size',
        type=int,
        help='Size of grid cells for analysis',
        default=256
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output path for metrics CSV file',
        default=None
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Initialize analyzer
    analyzer = XenArchAnalyzer(args.data_dir)
    analyzer.terrain_analyzer = TerrainAnalyzer(grid_size=args.grid_size)
    
    # Ensure input file exists
    input_file = Path(args.file)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Process chunks
    print(f"Analyzing file: {input_file}")
    
    total_interesting = 0
    all_results = []
    
    for chunk_result in analyzer.terrain_analyzer.analyze(input_file):
        chunk_id = chunk_result['chunk_id']
        
        # Save chunk metrics
        if args.output:
            chunk_output = Path(args.output).with_stem(f"{Path(args.output).stem}_chunk_{chunk_id}")
        else:
            chunk_output = input_file.with_suffix(f'.chunk_{chunk_id}.metrics.csv')
        
        analyzer.visualizer.save_metrics(chunk_result, chunk_output)
        
        # Update totals
        total_interesting += len(chunk_result['interesting_regions'])
        all_results.append(chunk_result)
        
        print(f"Chunk {chunk_id}: Found {len(chunk_result['interesting_regions'])} regions of interest")
    
    # Compute global statistics
    if all_results:
        all_fds = [r['fractal_dimension'] for chunk in all_results 
                  for r in chunk['all_regions']]
        global_mean = np.mean(all_fds)
        global_std = np.std(all_fds)
        
        print(f"\nAnalysis complete:")
        print(f"Total regions of interest: {total_interesting}")
        print(f"Global mean fractal dimension: {global_mean:.3f}")
        print(f"Global standard deviation: {global_std:.3f}")

if __name__ == "__main__":
    main()
