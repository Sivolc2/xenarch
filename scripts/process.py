import argparse
import numpy as np
import tifffile

def filter_first_n_samples(tiff_file_path, n, output_file_path):
    # Open the .tiff file using tifffile
    with tifffile.TiffFile(tiff_file_path) as tif:
        # Access the first page of the TIFF file
        page = tif.pages[0]
        
        # Read the image data
        img_array = page.asarray()
        
        # Check if n is greater than the number of samples
        if n > img_array.shape[0]:
            raise ValueError("n is greater than the number of samples in the image")
        
        # Filter the first n samples
        filtered_array = img_array[:n]
        
        # Save the filtered array to a new .tiff file
        tifffile.imwrite(output_file_path, filtered_array)
        
        # Print the shape of the filtered array
        print(f"Filtered array shape: {filtered_array.shape}")
        print(f"Filtered data saved to: {output_file_path}")

def main():
    parser = argparse.ArgumentParser(description='Filter the first n samples from a .tiff file.')
    parser.add_argument('tiff_file_path', type=str, help='Path to the .tiff file')
    parser.add_argument('n', type=int, help='Number of samples to filter')
    parser.add_argument('output_file_path', type=str, help='Path to save the filtered .tiff file')
    
    args = parser.parse_args()
    
    filter_first_n_samples(args.tiff_file_path, args.n, args.output_file_path)

if __name__ == '__main__':
    main()

"python process.py path/to/your/image.tiff 10 path/to/save/filtered_image.tiff"