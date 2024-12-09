from pathlib import Path
from typing import Union, List, Dict
from xenarch_mk2.analyzers.terrain import TerrainAnalyzer
from xenarch_mk2.utils.visualization import Visualizer
import rasterio

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

def main():
    analyzer = XenArchAnalyzer("./data")
    # Test with sample file
    results = analyzer.analyze_region("./data/test.tif")
    print(f"Found {len(results['interesting_regions'])} regions of interest")

if __name__ == "__main__":
    main()
