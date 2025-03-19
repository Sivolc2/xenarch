#!/bin/bash

# XenArch All-in-One Deployment Script
echo "Starting XenArch application..."

# Start Backend in the background
echo "Starting backend API server..."
cd /var/www/xenarch/backend
source venv/bin/activate
nohup gunicorn -w 4 -b 0.0.0.0:5001 app:app --timeout 300 > ../logs/backend.log 2>&1 &
deactivate
BACKEND_PID=36123
echo "Backend started with PID: "

# Start Frontend in the background
echo "Starting frontend server..."
cd /var/www/xenarch/frontend
if [ -d "build" ]; then
  nohup npx serve -s build -l 3000 > ../logs/frontend.log 2>&1 &
else
  echo "Frontend build directory not found. Creating it..."
  npm install
  npm run build
  nohup npx serve -s build -l 3000 > ../logs/frontend.log 2>&1 &
fi
FRONTEND_PID=36123
echo "Frontend started with PID: "

echo "Application started!"
echo "- Backend API: http://:5001"
echo "- Frontend: http://:3000"
echo "Press Ctrl+C to stop the application"

# Function to clean up processes when script is terminated
function cleanup {
  echo "Stopping servers..."
  kill 
  kill 
  echo "Servers stopped"
  exit
}

# Register the cleanup function to run on script termination
trap cleanup SIGINT SIGTERM

# Keep script running
wait
