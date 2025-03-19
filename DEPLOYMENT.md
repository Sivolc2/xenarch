# XenArch Deployment Guide

This guide explains how to deploy the XenArch Terrain Analysis Web Application to Vercel. This application consists of a React frontend and a Flask API backend.

## Deployment to Vercel

### Prerequisites

1. Node.js and npm installed locally
2. Vercel CLI: `npm install -g vercel`
3. Vercel account

### Deployment Steps

1. **Login to Vercel:**
   ```
   vercel login
   ```

2. **Deploy the project:**
   ```
   vercel
   ```

   During the deployment process, Vercel will ask:
   - Set up and deploy: Yes
   - Link to existing project: No (create a new one)
   - Project name: xenarch (or your preferred name)
   - Directory to deploy: . (root directory)

3. **Environment Variables:**
   If needed, set environment variables in the Vercel dashboard:
   - Go to your project settings
   - Navigate to Environment Variables
   - Add any required variables

4. **Production Deployment:**
   After testing on the preview URL, deploy to production:
   ```
   vercel --prod
   ```

## Local Development Setup

### Install Dependencies

1. **Root level dependencies:**
   ```
   npm install
   ```

2. **Frontend dependencies:**
   ```
   cd frontend && npm install
   ```

3. **Backend dependencies:**
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Running the Development Environment

1. **Start both frontend and backend together:**
   ```
   npm run dev
   ```

   This will start:
   - Frontend on http://localhost:3000
   - Backend on http://localhost:5001

2. **To run separately:**
   ```
   npm run dev:frontend  # Start only the frontend
   npm run dev:backend   # Start only the backend
   ```

## Current Limitations in Vercel Deployment

Since Vercel runs serverless functions with stateless execution, some features have been adapted:

1. **File Storage:** The demo deployment uses temporary storage in `/tmp` which is cleared between function invocations. For production use, you would need to implement cloud storage (AWS S3, Azure Blob Storage, etc.).

2. **Long-running Tasks:** Vercel functions have a maximum execution time (default 10s, up to 60s with configuration). The terrain analysis processing might exceed this, so in production, you would need:
   - Offload processing to a dedicated service
   - Implement a webhook or polling system for status updates
   - Consider using a background job queue service

3. **Demo Mode:** The current deployment is in demo mode, with placeholder responses for API endpoints. To implement full functionality, you would need to adapt the processing pipeline to work within the constraints of serverless functions or connect to external services.

## Next Steps for Production Deployment

1. **Cloud Storage Integration:**
   - Implement AWS S3 or similar for storing uploaded terrain files and results
   - Update file paths in the `api/index.py` file

2. **Processing Pipeline:**
   - Create a serverless pipeline or use a third-party service for terrain analysis
   - Implement job status tracking across invocations

3. **Authentication:**
   - Add user authentication if needed
   - Control access to uploaded files and results 