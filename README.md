# Flare AI DeFAI

Flare AI SDK template for AI x DeFi (DeFAI).

### 🚀 Key Features

- **Secure AI Execution** – Runs within a Trusted Execution Environment (TEE) with remote attestation support.
- **Built-in Chat UI** – Interact with AI securely, served directly from TEE.
- **Flare Blockchain Integration** – Native support for token transactions and operations.
- **Gemini AI Model Support** – Seamlessly integrates with Google's Gemini AI.

<img width="500" alt="Artemis" src="https://github.com/user-attachments/assets/921fbfe2-9d52-496c-9b48-9dfc32a86208" />

## 📌 Prerequisites

Before starting, ensure you have:

- A **Google Cloud Platform** account with access to `google-hackathon-project`.
- A **Gemini API Key** linked to the same project.
- The **`gcloud` CLI** installed and configured on your system.

## ⚙️ Environment Setup

### Step 1: Configure Environment Variables

Add the following lines to your shell configuration file (`~/.bashrc` or `~/.zshrc`):

```bash
export TEE_IMAGE_REFERENCE=ghcr.io/flare-foundation/flare-ai-defai:main
export GEMINI_API_KEY=<your-gemini-api-key>
export WEB3_PROVIDER_URL=https://coston2-api.flare.network/ext/C/rpc
export WEB3_EXPLORER_URL=https://coston2-explorer.flare.network/
export TEAM_NAME=<your-team-name>
```

### Step 2: Apply Configuration

```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Step 3: Verify Setup

```bash
echo $TEE_IMAGE_REFERENCE
# Expected output: ghcr.io/flare-foundation/flare-ai-defai:main
```

## 🚀 Deployment

You can deploy Flare AI DeFAI on **Confidential Compute Instances** using either **AMD SEV** or **Intel TDX**.

### 🔹 Option 1: AMD SEV (Recommended)

Deploy on **AMD Secure Encrypted Virtualization (SEV)**:

```bash
gcloud compute instances create defai-$TEAM_NAME \
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
  --tags=flare-ai-defai,http-server,https-server \
  --create-disk=auto-delete=yes,\
boot=yes,\
device-name=defai-$TEAM_NAME,\
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

### Option 2: Intel TDX

Deploy on **Intel Trust Domain Extensions (TDX)**:

```bash
gcloud compute instances create defai-$TEAM_NAME \
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
  --tags=flare-ai-defai,http-server,https-server \
  --create-disk=auto-delete=yes,\
boot=yes,\
device-name=defai-$TEAM_NAME,\
image=projects/confidential-space-images/global/images/confidential-space-debug-0-tdxpreview-c38b622,\
mode=rw,\
size=11,\
type=pd-balanced \
  --shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --confidential-compute-type=TDX
```

## 🔜 Next Steps

Once your instance is running, access the Chat UI via the instance's **public IP address**.

### Example Interactions

💬 **"Create an account for me"**  
💬 **"Show me your remote attestation"**  
💬 **"Transfer 10 C2FLR to 0x000000000000000000000000000000000000dEaD"**

Enjoy secure AI-powered DeFi with **Flare AI DeFAI**! 🚀

### 🔧 Troubleshooting

If you encounter issues:

1. **Check logs**

   ```bash
   gcloud compute instances get-serial-port-output defai-$TEAM_NAME --project=google-hackathon-project
   ```

2. **Verify API Key** – Ensure `GEMINI_API_KEY` is correctly set.
3. **Check Firewall** – Ensure your instance has public access.
