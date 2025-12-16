# ===================
# Stage 1: Build
# ===================
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files first (layer caching, same as Python)
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code and build
COPY . .
RUN npm run build

# ===================
# Stage 2: Production
# ===================
# nginx:alpine is tiny (~20MB) and perfect for serving static files
FROM nginx:alpine

# Copy the built files from Stage 1 into nginx's serve directory
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config (we'll create this next)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# nginx runs automatically, no CMD needed
