# Build stage for frontend
FROM node:18 AS frontend-builder
WORKDIR /app/frontend
COPY chat-ui/package*.json ./
RUN npm install
COPY chat-ui/ ./
RUN npm run build

# Build stage for backend
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS backend-builder
WORKDIR /app/backend
COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./
COPY src/ ./
RUN uv sync --frozen --no-editable

# Final stage
FROM python:3.12-slim-bookworm
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && \
    apt-get install -y supervisor nginx && \
    rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from backend builder
COPY --from=backend-builder /app/backend/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy backend source code
COPY src/ ./src/

# Copy frontend build files
COPY --from=frontend-builder /app/frontend/build /usr/share/nginx/html

# Configure nginx
RUN echo '\
    server { \n\
    listen 3000; \n\
    location / { \n\
    root /usr/share/nginx/html; \n\
    try_files $uri $uri/ /index.html; \n\
    } \n\
    location /api { \n\
    proxy_pass http://localhost:8000; \n\
    proxy_set_header Host $host; \n\
    proxy_set_header X-Real-IP $remote_addr; \n\
    } \n\
    }' > /etc/nginx/sites-available/default

# Configure supervisor
RUN echo '\
    [supervisord] \n\
    nodaemon=true \n\
    \n\
    [program:nginx] \n\
    command=/usr/sbin/nginx -g "daemon off;" \n\
    autostart=true \n\
    autorestart=true \n\
    \n\
    [program:backend] \n\
    command=python -m src.main \n\
    directory=/app \n\
    autostart=true \n\
    autorestart=true' > /etc/supervisor/conf.d/supervisord.conf

# Expose ports
EXPOSE 3000 8000

# Start supervisor
CMD ["/usr/bin/supervisord"]