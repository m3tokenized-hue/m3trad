# E1 Assistant - Frontend Dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Set environment variable for build
ENV REACT_APP_BACKEND_URL=http://localhost:8001

# Build for production
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

RUN npm install -g serve

COPY --from=build /app/build ./build

# Expose port
EXPOSE 3000

# Start the server
CMD ["serve", "-s", "build", "-l", "3000"]
