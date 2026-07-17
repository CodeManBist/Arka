import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import { createProxyMiddleware } from 'http-proxy-middleware';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

// Middleware
app.use(cors({
  origin: '*', // Allow all origins for development
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Health check endpoint
app.get('/', (req, res) => {
  res.json({
    status: 'running',
    service: 'Blast Radius Backend',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    endpoints: {
      health: '/',
      proxy: '/api/*',
    }
  });
});

// AI Service URL - can be configured via environment variable
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

// Request logging middleware
app.use((req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`${req.method} ${req.originalUrl} ${res.statusCode} - ${duration}ms`);
  });
  
  next();
});

// Error handling middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Error:', err);
  
  res.status(err.status || 500).json({
    success: false,
    error: err.message || 'Internal Server Error',
    error_type: err.name || 'internal_error',
    timestamp: new Date().toISOString()
  });
});

// Proxy middleware for AI service
// This proxies all /api/* requests to the AI service
app.use('/api/*', createProxyMiddleware({
  target: AI_SERVICE_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/api': '', // Remove /api prefix when forwarding
  },
  onError: (err, req, res) => {
    console.error('Proxy error:', err);
    res.status(500).json({
      success: false,
      error: 'Failed to proxy request to AI service',
      error_type: 'proxy_error',
      details: err.message || 'Unknown error'
    });
  },
  onProxyReq: (proxyReq, req, res) => {
    // Add headers if needed
    if (req.headers.authorization) {
      proxyReq.setHeader('Authorization', req.headers.authorization);
    }
  },
}));

// Health check for AI service
app.get('/health/ai-service', async (req, res) => {
  try {
    const response = await fetch(`${AI_SERVICE_URL}/`);
    const data = await response.json();
    
    res.json({
      status: response.ok ? 'healthy' : 'unhealthy',
      ai_service: data,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      error: 'Cannot connect to AI service',
      timestamp: new Date().toISOString()
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`\u26a1\ufe0f Blast Radius Backend running on port ${PORT}`);
  console.log(`\ud83d\udd17 AI Service URL: ${AI_SERVICE_URL}`);
  console.log(`\ud83d\udc85 CORS: All origins allowed`);
  console.log(`\ud83d\udcc3 Health check: http://localhost:${PORT}/`);
});

export default app;
