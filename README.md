# Flare AI Core

A modular SDK for confidential AI workloads, running on Trusted Execution Environments (TEE) with support for AMD SEV and Intel TDX architectures.

<img width="500" alt="Artemis (built with flare-ai-core)" src="https://github.com/user-attachments/assets/921fbfe2-9d52-496c-9b48-9dfc32a86208" />

## Prerequisites

- Google Cloud Platform account with access to the `google-hackathon-project`
- Gemini API key
- `gcloud` CLI installed and configured

## Environment Setup

1. Add the following environment variables to your shell configuration file (`~/.bashrc` or `~/.zshrc`):

```bash
export TEE_IMAGE_REFERENCE=ghcr.io/flare-foundation/flare-ai-core:main
export GEMINI_API_KEY=<your-gemini-api-key>
export WEB3_PROVIDER_URL=https://coston2-api.flare.network/ext/C/rpc
export WEB3_EXPLORER_URL=https://coston2-explorer.flare.network/
export TEAM_NAME=<your-team-name>
```

2. Reload your shell configuration:

```bash
source ~/.bashrc  # or ~/.zshrc
```

3. Verify the configuration:

```bash
echo $TEE_IMAGE_REFERENCE  # Should output: ghcr.io/flare-foundation/flare-ai-core:main
```

## Deployment

### AMD SEV Deployment

Deploy an AMD SEV-enabled instance with the following configuration:

```bash
gcloud compute instances create ai-core-$TEAM_NAME \
  --project=google-hackathon-project \
  --zone=us-central1-c \
  --machine-type=n2d-standard-2 \
  --network-interface=network-tier=PREMIUM,nic-type=GVNIC,stack-type=IPV4_ONLY,subnet=default \
  --metadata=tee-image-reference=$TEE_IMAGE_REFERENCE,\
tee-container-log-redirect=true,\
tee-env-GEMINI_API_KEY=$GEMINI_API_KEY,\
tee-env-GEMINI_MODEL=gemini-1.5-flash,\
tee-env-WEB3_PROVIDER_URL=$WEB3_PROVIDER_URL,\
tee-env-SIMULATE_ATTESTATION=false \
  --maintenance-policy=MIGRATE \
  --provisioning-model=STANDARD \
  --service-account=confidential-sa@flare-network-sandbox.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --min-cpu-platform="AMD Milan" \
  --tags=flare-ai-core,http-server,https-server \
  --create-disk=auto-delete=yes,\
boot=yes,\
device-name=ai-core-$TEAM_NAME,\
image=projects/confidential-space-images/global/images/confidential-space-debug-250100,\
mode=rw,\
size=11,\
type=pd-standard \
  --shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --labels=goog-ec-src=vm_add-gcloud \
  --reservation-affinity=any \
  --confidential-compute-type=SEV
```

### Intel TDX Deployment

For Intel TDX machines, use this alternative configuration:

```bash
gcloud compute instances create ai-core-$TEAM_NAME \
  --project=google-hackathon-project \
  --machine-type=c3-standard-4 \
  --maintenance-policy=TERMINATE \
  --zone=us-central1-c \
  --network-interface=network-tier=PREMIUM,nic-type=GVNIC,stack-type=IPV4_ONLY,subnet=default \
  --metadata=tee-image-reference=$TEE_IMAGE_REFERENCE,\
tee-container-log-redirect=true,\
tee-env-GEMINI_API_KEY=$GEMINI_API_KEY,\
tee-env-GEMINI_MODEL=gemini-1.5-flash,\
tee-env-WEB3_PROVIDER_URL=$WEB3_PROVIDER_URL,\
tee-env-SIMULATE_ATTESTATION=false \
  --provisioning-model=STANDARD \
  --service-account=confidential-sa@flare-network-sandbox.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --tags=flare-ai-core,http-server,https-server \
  --create-disk=auto-delete=yes,\
boot=yes,\
device-name=ai-core-$TEAM_NAME,\
image=projects/confidential-space-images/global/images/confidential-space-debug-0-tdxpreview-c38b622,\
mode=rw,\
size=11,\
type=pd-balanced \
  --shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --confidential-compute-type=TDX
```
