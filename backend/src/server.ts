import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

// Middleware
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/', (req, res) => {
  res.json({
    status: 'running',
    service: 'Blast Radius Backend',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// API routes will be added here
// For now, proxy requests to the AI service
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

// Proxy middleware for AI service
app.use('/api/*', async (req, res) => {
  try {
    const aiServiceUrl = `${AI_SERVICE_URL}${req.originalUrl}`;
    
    const response = await fetch(aiServiceUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...req.headers
      },
      body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined
    });
    
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Proxy error:', error);
    res.status(500).json({
      error: 'Failed to proxy request to AI service',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`⚡️ Blast Radius Backend running on port ${PORT}`);
  console.log(`🔗 AI Service URL: ${AI_SERVICE_URL}`);
});

export default app;
