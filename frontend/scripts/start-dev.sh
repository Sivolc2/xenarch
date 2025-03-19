#!/bin/bash

# XenArch Frontend Development Server Startup Script
# This script installs dependencies and starts the development server

echo "Setting up XenArch Frontend Development Server..."

# Ensure we're in the frontend directory
cd "$(dirname "$0")/.."

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Install cross-env if not installed
if ! npm list cross-env &>/dev/null; then
    echo "Installing cross-env..."
    npm install --save cross-env
fi

# Create development environment file if it doesn't exist
if [ ! -f ".env.development" ]; then
    echo "Creating .env.development file..."
    cat > .env.development << EOF
HOST=0.0.0.0
PORT=3000
BROWSER=none
WDS_SOCKET_HOST=0.0.0.0
DANGEROUSLY_DISABLE_HOST_CHECK=true
CHOKIDAR_USEPOLLING=true
EOF
fi

# Start the development server
echo "Starting development server..."
npm run start 