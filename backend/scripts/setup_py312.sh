#!/bin/bash

# XenArch Python 3.12 Setup Script
# This script sets up the environment for XenArch to run with Python 3.12

echo "Setting up XenArch for Python 3.12..."

# Ensure we have Python 3.12
python_version=$(python3 --version)
if [[ $python_version != *"3.12"* ]]; then
    echo "Warning: Python 3.12 not found. Current version: $python_version"
    echo "You may need to install Python 3.12 first."
    echo ""
    echo "On Ubuntu: sudo apt install python3.12 python3.12-venv python3.12-dev"
    echo "On macOS: brew install python@3.12"
    echo ""
    read -p "Continue with current Python version? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install required system dependencies
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux system, installing dependencies..."
    
    # Check if we're running as root
    if [ "$EUID" -ne 0 ]; then
        echo "Please run as root or with sudo to install system dependencies."
        exit 1
    fi
    
    # Install dependencies
    apt update
    apt install -y build-essential python3-dev gdal-bin libgdal-dev python3-gdal
    apt install -y libatlas-base-dev gfortran
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS, installing dependencies with Homebrew..."
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Please install Homebrew first:"
        echo "/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    brew install gdal
else
    echo "Unsupported OS. Please install dependencies manually:"
    echo "- GDAL"
    echo "- Python development tools"
    echo "- Atlas and Fortran for scientific computing"
fi

# Set up virtual environment
echo "Setting up Python virtual environment..."
cd "$(dirname "$0")/.."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install critical packages
echo "Upgrading pip and installing setuptools..."
pip install --upgrade pip setuptools wheel

# Install GDAL if needed
if python -c "import rasterio" &> /dev/null; then
    echo "Rasterio already installed."
else
    echo "Installing GDAL and rasterio..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        export GDAL_CONFIG=/usr/bin/gdal-config
        pip install --no-binary :all: rasterio
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        export GDAL_CONFIG=$(brew --prefix)/bin/gdal-config
        pip install --no-binary :all: rasterio
    else
        echo "WARNING: Installing rasterio requires GDAL. May fail on your system."
        pip install rasterio
    fi
fi

# Install other requirements
echo "Installing project requirements..."
pip install -r requirements.txt

echo ""
echo "Setup complete! Activate the environment with:"
echo "source venv/bin/activate"
echo ""
echo "Start the application with:"
echo "python app.py" 