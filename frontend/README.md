# XenArch React Frontend

This is the React-based frontend for the XenArch Terrain Analysis tool. It provides a modern, responsive user interface for uploading GeoTIFF files, configuring analysis parameters, and viewing results.

## Features

- Modern React component architecture
- Responsive UI using React Bootstrap
- Real-time progress tracking with animated indicators
- Detailed debug information for troubleshooting
- Modal-based detailed view for analysis results

## Project Structure

```
frontend-react/
├── public/                  # Static files
├── src/
│   ├── components/          # React components
│   │   ├── AnalysisForm.js  # Form for uploading and configuring analysis
│   │   ├── ProcessingStatusCard.js  # Status display with progress tracking
│   │   └── ResultsCard.js   # Results display component
│   ├── hooks/               # Custom React hooks
│   │   ├── useAnalysisForm.js  # Form state management
│   │   └── useJobStatus.js  # Job status and polling management
│   ├── services/            # API and configuration
│   │   ├── api.js           # API service for backend communication
│   │   └── config.js        # Configuration settings
│   ├── styles/              # CSS files
│   │   ├── App.css          # App-specific styles 
│   │   └── index.css        # Global styles
│   ├── App.js               # Main application component
│   └── index.js             # Application entry point
├── package.json             # Dependencies and scripts
└── README.md                # This file
```

## Prerequisites

- Node.js 14.x or higher
- npm 6.x or higher

## Installation

1. Install dependencies:

```bash
cd frontend-react
npm install
```

## Development

To run the development server:

```bash
npm start
```

This will start the development server on [http://localhost:3000](http://localhost:3000).

## Building for Production

To build the application for production:

```bash
npm run build
```

This will create a `build` directory with optimized production build.

## Configuration

Edit `src/services/config.js` to configure the backend API endpoints and other settings.

By default, the application expects the backend to be running at `http://localhost:5001/api`.

## Backend Integration

This frontend is designed to work with the XenArch backend API. Make sure the backend is running before using this application.

## Contributing

1. Follow the project's code style and organization
2. Keep components focused on a single responsibility
3. Maintain separation between UI components and business logic

## License

Copyright © 2023 XenArch Project 