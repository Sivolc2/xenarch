import argparse
import rasterio
import logging
import numpy as np

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_tiff(file_path):
    """Check TIFF file properties"""
    with rasterio.open(file_path) as src:
        logger.info(f"File: {file_path}")
        logger.info(f"Dimensions: {src.width}x{src.height}")
        logger.info(f"Bands: {src.count}")
        logger.info(f"Data type: {src.dtypes[0]}")
        logger.info(f"CRS: {src.crs}")
        logger.info(f"Transform: {src.transform}")
        
        # Read a sample
        data = src.read(1)
        logger.info(f"Data shape: {data.shape}")
        logger.info(f"Value range: [{data.min()}, {data.max()}]")
        logger.info(f"NaN count: {np.isnan(data).sum()}")

def main():
    parser = argparse.ArgumentParser(description='Check TIFF file properties')
    parser.add_argument('file', type=str, help='Path to TIFF file')
    args = parser.parse_args()
    
    check_tiff(args.file)

if __name__ == '__main__':
    main() 