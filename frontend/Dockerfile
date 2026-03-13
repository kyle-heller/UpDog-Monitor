FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .
RUN npm run build

FROM nginxinc/nginx-unprivileged:alpine

# Patch OS-level packages to clear known CVEs
USER root
RUN apk update && apk upgrade --no-cache && rm -rf /var/cache/apk/*
USER nginx

COPY --from=build /app/dist /usr/share/nginx/html

COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# nginx-unprivileged cannot bind to port 80
ENV PORT=8080

EXPOSE $PORT
