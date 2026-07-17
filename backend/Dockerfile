# Backend Dockerfile for Node.js/Express

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
