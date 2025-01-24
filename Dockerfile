# Stage 1: Build Stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ADD . /flare-ai-core
WORKDIR /flare-ai-core
RUN uv sync --frozen

# Stage 2: Production Stage (Final Image)
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY --from=builder /flare-ai-core/.venv ./.venv
COPY --from=builder /flare-ai-core/src ./src
COPY --from=builder /flare-ai-core/pyproject.toml .
COPY --from=builder /flare-ai-core/README.md .

# Allow workload operator to override environment variables
LABEL "tee.launch_policy.allow_env_override"="GEMINI_API_KEY,GEMINI_MODEL,WEB3_PROVIDER_URL,WEB3_EXPLORER_URL,SIMULATE_ATTESTATION"
LABEL "tee.launch_policy.log_redirect"="always"

EXPOSE 8000

# Define the entrypoint
ENTRYPOINT ["uv", "run", "start-backend"]