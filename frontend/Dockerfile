# Multi-stage build for Vue.js frontend
FROM node:18-alpine as build-stage

# Set build arguments
ARG VITE_API_BASE_URL
ARG VITE_SYNOLOGY_DRIVE_URL

# Set environment variables
ENV NODE_ENV=development
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_SYNOLOGY_DRIVE_URL=$VITE_SYNOLOGY_DRIVE_URL

WORKDIR /app

# Copy package files
COPY package*.json ./

# Clear npm cache and install dependencies with verbose error handling
RUN npm cache clean --force && \
    npm config set registry https://registry.npmjs.org/ && \
    npm install --no-optional --verbose

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine as production-stage

# Install wget for health check
RUN apk add --no-cache wget

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S appuser -u 1001

# Set permissions
RUN chown -R appuser:nodejs /usr/share/nginx/html && \
    chown -R appuser:nodejs /var/cache/nginx && \
    chown -R appuser:nodejs /var/log/nginx && \
    chown -R appuser:nodejs /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R appuser:nodejs /var/run/nginx.pid

USER appuser

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]