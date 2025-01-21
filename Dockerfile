# Stage 1: Build Stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ADD . /flare-ai-core
WORKDIR /flare-ai-core
RUN uv sync --frozen

# Stage 2: Production Stage (Final Image)
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
COPY --from=builder /flare-ai-core /app
WORKDIR /app

# Allow workload operator to override environment variables
LABEL "tee.launch_policy.allow_env_override"="gemini_api_key,gemini_model,web3_provider_url,web3_explorer_url,simulate_attestation"

EXPOSE 8000

# Define the entrypoint
ENTRYPOINT ["uv", "run", "start-backend"]