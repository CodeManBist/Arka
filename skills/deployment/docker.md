# Docker Deployment Skills

## 🎯 Overview

Skills for containerizing and deploying the Blast Radius project using Docker.

## 📋 Prerequisites

- Docker installed
- Docker Compose installed
- Understanding of containerization concepts
- Basic Linux commands

## 🏗️ Core Concepts

### Architecture

```
Host Machine
    ↓
Docker Engine
    ↓
Docker Compose
    ↓
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Frontend    │ │   Backend    │ │  AI Service  │
│  (Next.js)   │ │  (Node.js)   │ │  (FastAPI)   │
└─────────────┘ └─────────────┘ └─────────────┘
    ↓              ↓              ↓
 Port 3000     Port 4000     Port 8000
```

### Docker Network

- All services communicate via a shared Docker network
- Services can reference each other by service name
- Example: `http://ai-service:8000` from backend

## 🛠️ Required Tools

```bash
# Install Docker
# Linux
sudo apt-get install docker-ce docker-ce-cli containerd.io

# macOS
# Download Docker Desktop from https://www.docker.com/products/docker-desktop

# Windows
# Download Docker Desktop from https://www.docker.com/products/docker-desktop

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

## 📚 Common Patterns

### 1. Dockerfile for Frontend (Next.js)

```dockerfile
# frontend/Dockerfile

# Stage 1: Build
FROM node:22-alpine AS base

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source files
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production
FROM node:22-alpine AS production

WORKDIR /app

# Copy built files
COPY --from=base /app/.next ./.next
COPY --from=base /app/public ./public
COPY --from=base /app/package.json ./package.json
COPY --from=base /app/node_modules ./node_modules

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]

# Stage 3: Development (for hot reloading)
FROM node:22-alpine AS development

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
```

### 2. Dockerfile for Backend (Node.js/Express)

```dockerfile
# backend/Dockerfile

FROM node:22-alpine AS base

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm ci

# Copy source files
COPY . .

# Build TypeScript
RUN npm run build

# Production stage
FROM node:22-alpine AS production

WORKDIR /app

# Copy built files
COPY --from=base /app/dist ./dist
COPY --from=base /app/package.json ./package.json
COPY --from=base /app/node_modules ./node_modules

# Expose port
EXPOSE 4000

# Set environment variables
ENV NODE_ENV=production
ENV AI_SERVICE_URL=http://ai-service:8000

# Start the application
CMD ["node", "dist/server.js"]

# Development stage
FROM node:22-alpine AS development

WORKDIR /app

COPY package.json ./

RUN npm ci

COPY . .

EXPOSE 4000

CMD ["npm", "run", "dev"]
```

### 3. Dockerfile for AI Service (FastAPI)

```dockerfile
# ai-service/Dockerfile

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Tree-sitter CLI
RUN npm install -g tree-sitter-cli

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM python:3.11-slim AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy built parsers and source
COPY --from=base /app/analysis /app/analysis
COPY --from=base /app/api /app/api
COPY --from=base /app/graph /app/graph
COPY --from=base /app/models /app/models
COPY --from=base /app/app.py /app/app.py

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev
    depends_on:
      - ai-service
    networks:
      - blast-radius-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "4000:4000"
    environment:
      - NODE_ENV=development
      - AI_SERVICE_URL=http://ai-service:8000
    volumes:
      - ./backend:/app
      - /app/node_modules
    command: npm run dev
    depends_on:
      - ai-service
    networks:
      - blast-radius-network

  ai-service:
    build:
      context: ./ai-service
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - GITHUB_TOKEN=${GITHUB_TOKEN:-}
    volumes:
      - ./ai-service:/app
      - /app/venv
    command: sh -c "pip install -r requirements.txt && uvicorn app:app --host 0.0.0.0 --port 8000 --reload"
    networks:
      - blast-radius-network

networks:
  blast-radius-network:
    driver: bridge
```

### 5. .dockerignore

```dockerignore
# Dependencies
node_modules/
venv/
.env
.env.local

# Build outputs
dist/
.next/
__pycache__/
*.pyc

# IDE
.idea/
.vscode/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*

# Temporary files
tmp/
temp/
*.tmp

# Local repository clones
repositories/
cloned_repos/
```

## 🎯 Best Practices

### 1. Image Optimization

- Use multi-stage builds to reduce image size
- Clean up apt cache after installing packages
- Use alpine-based images when possible
- Remove unnecessary files

### 2. Layer Caching

- Order Dockerfile commands to maximize cache hits
- Copy files that change less frequently first
- Install dependencies before copying source code

### 3. Environment Variables

- Use `.env` files for development
- Pass sensitive variables at runtime
- Use Docker secrets for production
- Set default values for optional variables

### 4. Health Checks

```yaml
# In docker-compose.yml
services:
  ai-service:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 5. Resource Limits

```yaml
# In docker-compose.yml
services:
  ai-service:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## 🧪 Testing

### 1. Build Images

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build frontend

# Build with no cache
docker-compose build --no-cache
```

### 2. Run Services

```bash
# Start all services
docker-compose up

# Start in detached mode
docker-compose up -d

# Start specific service
docker-compose up frontend

# View logs
docker-compose logs
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### 3. Debugging

```bash
# Enter a running container
docker-compose exec frontend sh

# View running containers
docker-compose ps

# View container logs
docker logs <container_id>

# Inspect container
docker inspect <container_id>

# View resource usage
docker stats
```

### 4. Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale ai-service=3
```

## 📖 Resources

- [Docker Documentation](https://docs.docker.com)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)

## 🚨 Troubleshooting

### Build Failures
- Check Dockerfile syntax
- Verify all files exist
- Check for missing dependencies
- View build logs for errors

### Container Won't Start
- Check port conflicts
- Verify volume mounts
- Check environment variables
- View container logs

### Network Issues
- Verify services are on the same network
- Check service names are correct
- Test connectivity between containers
- Check firewall settings

### Performance Issues
- Check resource limits
- Monitor container resource usage
- Optimize Dockerfile
- Use appropriate base images

### Permission Issues
- Check volume mount permissions
- Verify user permissions in containers
- Use proper UID/GID settings

### Memory Issues
- Increase Docker memory allocation
- Optimize application memory usage
- Use swap space if needed
- Limit concurrent containers