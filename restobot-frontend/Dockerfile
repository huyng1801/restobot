# Stage 1: Build
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY public ./public
COPY src ./src
COPY tsconfig.json .
COPY *.json ./

# Build the application
RUN npm run build

# Stage 2: Runtime
FROM node:18-alpine

WORKDIR /app

# Install serve to run the application
RUN npm install -g serve

# Copy built application from builder
COPY --from=builder /app/build ./build
COPY --from=builder /app/package.json ./


# Create non-root user only if not exists (avoid gid/uid conflict)
RUN (getent group appuser || addgroup -g 1001 appuser) && \
    (id -u appuser || adduser -D -u 1001 -G appuser appuser) && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://103.56.160.107:3000', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})" || exit 1

# Start application
CMD ["serve", "-s", "build", "-l", "3000"]
