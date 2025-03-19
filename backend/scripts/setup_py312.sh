#!/bin/bash

# XenArch Python 3.12 Setup Script
# This script sets up the environment for XenArch to run with Python 3.12

echo "Setting up XenArch for Python 3.12..."

# Check if Python 3.12 is installed
if command -v python3.12 &> /dev/null; then
    echo "Python 3.12 found!"
    PYTHON_CMD="python3.12"
else
    echo "Python 3.12 not found. Attempting to install..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Check if we're running as root
        if [ "$EUID" -ne 0 ]; then
            echo "Please run as root or with sudo to install Python 3.12."
            exit 1
        fi
        
        # Install Python 3.12 on Ubuntu/Debian
        echo "Adding deadsnakes PPA for Python 3.12..."
        apt update
        apt install -y software-properties-common
        add-apt-repository -y ppa:deadsnakes/ppa
        apt update
        apt install -y python3.12 python3.12-venv python3.12-dev python3.12-distutils
        
        if command -v python3.12 &> /dev/null; then
            echo "Python 3.12 successfully installed!"
            PYTHON_CMD="python3.12"
        else
            echo "Failed to install Python 3.12. Please install it manually."
            exit 1
        fi
    # elif [[ "$OSTYPE" == "darwin"* ]]; then
    #     # Install Python 3.12 on macOS
    #     echo "Checking Homebrew..."
    #     if ! command -v brew &> /dev/null; then
    #         echo "Homebrew not found. Please install Homebrew first:"
    #         echo "/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    #         exit 1
    #     fi
        
    #     echo "Installing Python 3.12 via Homebrew..."
    #     brew install python@3.12
        
    #     if command -v python3.12 &> /dev/null; then
    #         echo "Python 3.12 successfully installed!"
    #         PYTHON_CMD="python3.12"
    #     else
    #         echo "Failed to install Python 3.12. Please install it manually."
    #         exit 1
    #     fi
    # else
    #     echo "Unsupported OS. Please install Python 3.12 manually."
    #     exit 1
    fi
fi

# Verify Python version
python_version=$($PYTHON_CMD --version)
echo "Using $python_version"

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
echo "Setting up Python virtual environment with Python 3.12..."
cd "$(dirname "$0")/.."
$PYTHON_CMD -m venv venv
source venv/bin/activate

# Verify venv Python version
python_venv_version=$(python --version)
echo "Virtual environment using $python_venv_version"

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