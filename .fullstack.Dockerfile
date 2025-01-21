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
RUN echo '\
    server { \n\
    listen 3000; \n\
    server_tokens off; \n\
    \n\
    # Security headers \n\
    add_header X-Frame-Options "SAMEORIGIN"; \n\
    add_header X-Content-Type-Options "nosniff"; \n\
    add_header X-XSS-Protection "1; mode=block"; \n\
    \n\
    location / { \n\
    root /usr/share/nginx/html; \n\
    try_files $uri $uri/ /index.html; \n\
    \n\
    # Cache static assets \n\
    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ { \n\
    expires 30d; \n\
    add_header Cache-Control "public, no-transform"; \n\
    } \n\
    } \n\
    \n\
    location /api { \n\
    proxy_pass http://localhost:8000; \n\
    proxy_set_header Host $host; \n\
    proxy_set_header X-Real-IP $remote_addr; \n\
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \n\
    proxy_set_header X-Forwarded-Proto $scheme; \n\
    \n\
    # Timeouts \n\
    proxy_connect_timeout 60s; \n\
    proxy_send_timeout 60s; \n\
    proxy_read_timeout 60s; \n\
    } \n\
    }' > /etc/nginx/sites-available/default

# Configure supervisor with proper logging
RUN echo '\
    [supervisord] \n\
    user=root \n\
    nodaemon=true \n\
    logfile=/var/log/supervisor/supervisord.log \n\
    pidfile=/var/run/supervisord.pid \n\
    \n\
    [program:nginx] \n\
    command=/usr/sbin/nginx -g "daemon off;" \n\
    autostart=true \n\
    autorestart=true \n\
    startretries=5 \n\
    numprocs=1 \n\
    startsecs=0 \n\
    process_name=%(program_name)s_%(process_num)02d \n\
    stderr_logfile=/var/log/supervisor/%(program_name)s_stderr.log \n\
    stderr_logfile_maxbytes=10MB \n\
    stdout_logfile=/var/log/supervisor/%(program_name)s_stdout.log \n\
    stdout_logfile_maxbytes=10MB \n\
    \n\
    [program:backend] \n\
    command=uv run start-backend \n\
    directory=/app \n\
    autostart=true \n\
    autorestart=true \n\
    startretries=5 \n\
    numprocs=1 \n\
    startsecs=0 \n\
    process_name=%(program_name)s_%(process_num)02d \n\
    stdout_logfile=/dev/stdout \n\
    stdout_logfile_maxbytes=0 \n\
    stderr_logfile=/dev/stderr \n\
    stderr_logfile_maxbytes=0' > /etc/supervisor/conf.d/supervisord.conf

# Create log directories
RUN mkdir -p /var/log/supervisor

# Expose ports
EXPOSE 3000 8000

# Allow workload operator to override environment variables
LABEL "tee.launch_policy.allow_env_override"="gemini_api_key,gemini_model,web3_provider_url,web3_explorer_url,simulate_attestation"

# Start supervisor
ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]