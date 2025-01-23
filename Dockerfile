# Build stage for frontend
FROM node:18-slim AS frontend-builder
WORKDIR /app/frontend

# Copy package files and install dependencies
COPY chat-ui/package*.json ./
RUN npm ci --only=production

# Copy source and build
COPY chat-ui/ ./
RUN npm run build && \
    rm -rf node_modules  # Clean up after build

# Build stage for backend
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS backend-builder
WORKDIR /app/backend

# Copy only necessary files for dependency installation
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# Install dependencies
RUN uv sync --frozen --no-editable

# Final stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    supervisor \
    nginx \
    ca-certificates \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    # Create necessary directories
    mkdir -p /var/log/nginx /var/lib/nginx /run/nginx

# Copy Python dependencies and backend code
COPY --from=backend-builder /app/backend /app
ENV PATH="/app/.venv/bin:$PATH"

# Copy frontend build files
COPY --from=frontend-builder /app/frontend/build /usr/share/nginx/html

# Configure nginx with security headers
COPY default.conf /etc/nginx/sites-available/default
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create log directories
RUN mkdir -p /var/log/supervisor

# Expose ports
EXPOSE 80 8001

# Allow workload operator to override environment variables
LABEL "tee.launch_policy.allow_env_override"="GEMINI_API_KEY,GEMINI_MODEL,WEB3_PROVIDER_URL,WEB3_EXPLORER_URL,SIMULATE_ATTESTATION,REACT_APP_API_URL"
LABEL "tee.launch_policy.log_redirect"="always"

# Start supervisor
ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]