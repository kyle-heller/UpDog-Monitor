# ===================
# Stage 1: Build
# ===================
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files first (layer caching)
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code and build
COPY . .
RUN npm run build

# ===================
# Stage 2: Production
# ===================
FROM nginx:alpine

# Copy the built files from Stage 1
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config template
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Railway sets PORT dynamically
ENV PORT=80

# nginx:alpine with /etc/nginx/templates/ auto-runs envsubst on startup
EXPOSE $PORT
