# Development Dockerfile for AI Model Improver Frontend

FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 80

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "80"] 