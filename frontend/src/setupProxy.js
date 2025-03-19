const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  console.log('Setting up development proxy to backend');
  
  // Detect if we're in a Vercel environment
  const isVercel = process.env.VERCEL === '1';
  console.log('Vercel environment detected:', isVercel);
  
  // Only apply proxy in local development
  if (!isVercel) {
    app.use(
      '/api',
      createProxyMiddleware({
        target: 'http://localhost:5001',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'
        },
        logLevel: 'debug',
        // Add error handling for the proxy
        onError: (err, req, res) => {
          console.log('Proxy error:', err);
          res.writeHead(500, {
            'Content-Type': 'application/json'
          });
          res.end(JSON.stringify({
            error: 'Backend service is not available',
            message: 'The API server may still be starting up, please try again in a moment',
            details: err.message
          }));
        }
      })
    );
    console.log('Development proxy middleware configured');
  } else {
    console.log('Skipping proxy setup in Vercel environment');
  }
}; 