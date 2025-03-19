import argparse
from pathlib import Path
import json
import os
import sys
import logging

def main():
    """Simple stub version of analyze_results for debugging"""
    print("STUB: analyze_results.py executed")
    
    parser = argparse.ArgumentParser(description='Analyze terrain metrics (STUB)')
    parser.add_argument('-i', '--input-dir', type=str, required=True,
                      help='Input directory containing JSON metrics')
    parser.add_argument('--fd-range', type=float, nargs=2, default=[0, 0.8],
                      help='Fractal dimension range (min max)')
    parser.add_argument('--r2-min', type=float, default=0.8,
                      help='Minimum R-squared value')
    parser.add_argument('--max-samples', type=int, default=16,
                      help='Maximum number of samples to display')
    parser.add_argument('-o', '--output', type=str, help='Output dir for plots')
    parser.add_argument('--cpu-fraction', type=float, default=0.5,
                      help='CPU fraction (ignored in stub)')
    
    args = parser.parse_args()
    
    # Create a summary JSON for debugging
    output_path = Path(args.output) if args.output else Path(args.input_dir)
    os.makedirs(output_path, exist_ok=True)
    
    with open(output_path / "filtered_results_stub.json", 'w') as f:
        json.dump({
            "status": "success",
            "message": "This is a stub result for debugging"
        }, f, indent=2)
    
    print(f"STUB: Created debug file at {output_path / 'filtered_results_stub.json'}")
    
    # Log the arguments received
    print(f"STUB: Arguments received:")
    print(f"  - input_dir: {args.input_dir}")
    print(f"  - fd_range: {args.fd_range}")
    print(f"  - r2_min: {args.r2_min}")
    print(f"  - max_samples: {args.max_samples}")
    print(f"  - output: {args.output}")
    print(f"  - cpu_fraction: {args.cpu_fraction}")
    
if __name__ == '__main__':
    main() 