# =====================================================================
# PRASHANTH HOSPITALS — VITE REACT FRONTEND MULTI-STAGE DOCKERFILE
# =====================================================================

# ---------------------------------------------------------------------
# STAGE 1: Build Stage (Compiles React Vite Production Static Bundle)
# ---------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY frontend/package.json frontend/package-lock.json ./

# Install Node dependencies
RUN npm ci

# Copy frontend source code
COPY frontend/ ./

# Compile production static bundle to /app/dist
RUN npm run build

# ---------------------------------------------------------------------
# STAGE 2: Production Lightweight Nginx Stage
# ---------------------------------------------------------------------
FROM nginx:alpine AS runner

# Remove default Nginx welcome site
RUN rm -rf /etc/nginx/conf.d/default.conf /usr/share/nginx/html/*

# Copy custom Nginx Docker configuration
COPY frontend/nginx.docker.conf /etc/nginx/conf.d/default.conf

# Copy compiled static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

# Health check to ensure Nginx web server is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

# Start Nginx in foreground mode
CMD ["nginx", "-g", "daemon off;"]
