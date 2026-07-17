# Backend Development Skills

## 🎯 Overview

Skills for developing the Blast Radius backend using Node.js and Express.

## 📋 Prerequisites

- Node.js 22+
- npm or yarn
- TypeScript knowledge
- Express.js framework
- REST API design principles

## 🏗️ Core Concepts

### Project Structure

```
backend/
├── src/
│   ├── server.ts              # Main server file
│   ├── controllers/          # Route controllers
│   ├── routes/               # Route definitions
│   └── services/             # Business logic
├── package.json
├── tsconfig.json
└── Dockerfile
```

### Server Architecture

```
Express Server
    ↓
CORS Middleware
    ↓
JSON Body Parser
    ↓
API Routes
    ↓
Proxy to AI Service
    ↓
Response
```

## 🛠️ Required Tools

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start
```

## 📚 Common Patterns

### 1. Basic Server Setup

```typescript
// src/server.ts
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

// Middleware
app.use(cors());
app.use(express.json());

// Health check
app.get('/', (req, res) => {
  res.json({
    status: 'running',
    service: 'Blast Radius Backend',
    version: '1.0.0'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`⚡️ Backend running on port ${PORT}`);
});
```

### 2. API Routes

```typescript
// src/routes/blastRadius.ts
import { Router } from 'express';

const router = Router();

router.post('/analyze', async (req, res) => {
  try {
    const { repository_path, symbol_name, symbol_type } = req.body;
    
    // Validate input
    if (!repository_path || !symbol_name) {
      return res.status(400).json({
        error: 'repository_path and symbol_name are required'
      });
    }
    
    // Proxy to AI service
    const aiServiceUrl = `${process.env.AI_SERVICE_URL}/api/blast-radius/analyze`;
    const response = await fetch(aiServiceUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body)
    });
    
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

export default router;
```

### 3. Middleware

```typescript
// src/middleware/errorHandler.ts
import { Request, Response, NextFunction } from 'express';

export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  console.error('Error:', err);
  
  res.status(500).json({
    error: 'Internal server error',
    message: err.message,
    stack: process.env.NODE_ENV === 'development' ? err.stack : undefined
  });
}

// src/middleware/logger.ts
export function logger(req: Request, res: Response, next: NextFunction) {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
}
```

### 4. Environment Configuration

```typescript
// .env
PORT=4000
NODE_ENV=development
AI_SERVICE_URL=http://localhost:8000

// In server.ts
const PORT = process.env.PORT || 4000;
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';
```

### 5. Proxy to AI Service

```typescript
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
```

### 6. Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later'
});

app.use('/api/', limiter);
```

### 7. Request Validation

```typescript
import { body, validationResult } from 'express-validator';

app.post('/analyze', [
  body('repository_path').isString().notEmpty(),
  body('symbol_name').isString().notEmpty(),
  body('symbol_type').isString().optional(),
  body('max_depth').isInt({ min: 1, max: 10 }).optional()
], async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  
  // Process request...
});
```

## 🎯 Best Practices

### 1. Error Handling

- Always catch errors in async routes
- Return appropriate HTTP status codes
- Include error details in development mode
- Log errors for debugging

### 2. Security

- Validate all user input
- Sanitize request data
- Use HTTPS in production
- Set proper CORS headers
- Rate limit API endpoints

### 3. Performance

- Use connection pooling for databases
- Implement caching for frequent requests
- Optimize JSON serialization
- Use compression middleware

### 4. Logging

- Log requests and responses
- Include timestamps and request IDs
- Log errors with stack traces
- Use structured logging (JSON)

### 5. Configuration

- Use environment variables for sensitive data
- Provide default values for optional settings
- Validate configuration on startup
- Use different configs for development vs production

## 🧪 Testing

### Test API Endpoints

```typescript
// __tests__/api/blastRadius.test.ts
import request from 'supertest';
import app from '@/server';

describe('Blast Radius API', () => {
  it('should return health status', async () => {
    const res = await request(app)
      .get('/')
      .expect(200);
    
    expect(res.body.status).toBe('running');
    expect(res.body.service).toBe('Blast Radius Backend');
  });

  it('should proxy to AI service', async () => {
    // Mock fetch
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ success: true })
    });
    
    const res = await request(app)
      .post('/api/blast-radius/analyze')
      .send({ repository_path: '/test', symbol_name: 'test' })
      .expect(200);
    
    expect(res.body.success).toBe(true);
  });
});
```

### Test Middleware

```typescript
// __tests__/middleware/errorHandler.test.ts
import { errorHandler } from '@/middleware/errorHandler';
import { Request, Response, NextFunction } from 'express';

describe('errorHandler', () => {
  it('should handle errors', () => {
    const mockReq = {} as Request;
    const mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    } as unknown as Response;
    const mockNext = jest.fn() as NextFunction;
    
    const error = new Error('Test error');
    errorHandler(error, mockReq, mockRes, mockNext);
    
    expect(mockRes.status).toHaveBeenCalledWith(500);
    expect(mockRes.json).toHaveBeenCalledWith({
      error: 'Internal server error',
      message: 'Test error',
      stack: expect.any(String)
    });
  });
});
```

## 📖 Resources

- [Express Documentation](https://expressjs.com)
- [Node.js Documentation](https://nodejs.org/en/docs/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [REST API Design Best Practices](https://restfulapi.net)

## 🚨 Troubleshooting

### CORS Issues
- Verify CORS middleware is configured
- Check allowed origins
- Ensure credentials are handled correctly

### Connection Issues
- Verify AI service is running
- Check network connectivity
- Test with curl or Postman

### TypeScript Errors
- Check type definitions
- Verify module imports
- Ensure @types packages are installed

### Memory Leaks
- Monitor memory usage
- Check for event listener leaks
- Use proper cleanup in tests

### Performance Issues
- Profile API endpoints
- Check database query performance
- Optimize JSON serialization