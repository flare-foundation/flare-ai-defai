# Flare AI DeFAI

Flare AI Kit template for AI x DeFi (DeFAI).

## 🚀 Key Features

- **Secure AI Execution**  
  Runs within a Trusted Execution Environment (TEE) with remote attestation support for enhanced security.

- **Built-in Chat UI**  
  Interact with your AI securely—the chat interface is served directly from the TEE.

- **Flare Blockchain Integration**  
  Enjoy native support for token operations on the Flare blockchain.

- **Gemini 2.0 Support**  
  Leverage Google Gemini with structured query support for advanced AI capabilities.

<img width="500" alt="Artemis" src="https://github.com/user-attachments/assets/921fbfe2-9d52-496c-9b48-9dfc32a86208" />

## 🏗️ Build Instructions

You can build and run Flare AI DeFAI using Docker (recommended) or set up the backend and frontend manually.

### Setup .env

1. Rename `.env.example` to `env` and set all the variables.

2. Make sure `SIMULATE_ATTESTATION=true` for local testing

### With Docker (Recommended)

The Docker build is optimized for local testing and mimics the TEE environment with minimal adjustments. It includes an Nginx server for routing and uses Supervisor to manage both backend and frontend services within a single container.

1. **Build the Docker image:**

   ```bash
   docker build -t flare-ai-defai .
   ```

2. **Run the Docker container:**

   ```bash
   docker run -p 80:80 -it --env-file .env flare-ai-defai
   ```

3. **Open frontend in browser**

   To open the frontend, navigate to [http://localhost:80](http://localhost:80)

### Manual Setup

Flare AI DeFAI consists of a Python-based backend and a JavaScript frontend.

#### Backend Setup

1. **Install Dependencies:**  
   Backend dependencies are managed using [uv](https://docs.astral.sh/uv/getting-started/installation/):

   ```bash
   uv sync --all-extras
   ```

2. **Start the Backend:**  
   By default, the backend is served on `0.0.0.0:8080`.

   ```bash
   uv run start-backend
   ```

#### Frontend Setup

1. **Install Dependencies:**  
   Navigate to the `chat-ui/` directory and install the necessary packages via [npm](https://nodejs.org/en/download):

   ```bash
   cd chat-ui/
   npm install
   ```

2. **Configure the Frontend:**  
   Modify `chat-ui/src/App.js` to update the backend URL during testing:

   ```js
   const BACKEND_ROUTE = "http://localhost:8080/api/routes/chat/";
   ```

   **Note:** Remember to revert `BACKEND_ROUTE` back to `'api/routes/chat/'` after testing.

3. **Start the Frontend:**

   ```bash
   npm start
   ```

## 🚀 Deploy on TEE

Deploy Flare AI DeFAI on Confidential Compute Instances using either AMD SEV or Intel TDX.

### 📌 Prerequisites

- **Google Cloud Platform Account:**  
  Ensure you have access to the `verifiable-ai-hackathon`.

- **Gemini API Key:**  
  Link your Gemini API key to the same project.

- **gcloud CLI:**  
  Install and authenticate the [gcloud CLI](https://cloud.google.com/sdk/docs/install) on your system.

### ⚙️ Environment Setup

#### Step 1: Configure Environment Variables

Make sure the following variables are set in `.env`:

```bash
TEE_IMAGE_REFERENCE=ghcr.io/flare-foundation/flare-ai-defai:main # set this your repo build image
INSTANCE_NAME=<PROJECT_NAME-TEAM-_NAME
```

#### Step 2: Apply the Configuration

Add the environment variables to your current shell:

```bash
source .env
```

**Note:** If you open a new shell you will need to run this command again.

#### Step 3: Verify the Setup

Confirm that the environment variable is set correctly:

```bash
echo $TEE_IMAGE_REFERENCE
# Expected output: ghcr.io/flare-foundation/flare-ai-defai:main
```

### Deploying on Confidential Space

Choose your deployment option based on your hardware preference.

#### 🔹 Option 1: AMD SEV (Recommended)

Deploy on AMD Secure Encrypted Virtualization (SEV):

```bash
gcloud compute instances create $INSTANCE_NAME \
  --project=verifiable-ai-hackathon \
  --zone=us-central1-c \
  --machine-type=n2d-standard-2 \
  --network-interface=network-tier=PREMIUM,nic-type=GVNIC,stack-type=IPV4_ONLY,subnet=default \
  --metadata=tee-image-reference=$TEE_IMAGE_REFERENCE,\
tee-container-log-redirect=true,\
tee-env-GEMINI_API_KEY=$GEMINI_API_KEY,\
tee-env-GEMINI_MODEL=$GEMINI_MODEL,\
tee-env-WEB3_PROVIDER_URL=$WEB3_PROVIDER_URL,\
tee-env-SIMULATE_ATTESTATION=false \
  --maintenance-policy=MIGRATE \
  --provisioning-model=STANDARD \
  --service-account=confidential-sa@flare-network-sandbox.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --min-cpu-platform="AMD Milan" \
  --tags=flare-ai,http-server,https-server \
  --create-disk=auto-delete=yes,\
boot=yes,\
device-name=$INSTANCE_NAME,\
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

#### Option 2: Intel TDX

Deploy on Intel Trust Domain Extensions (TDX):

```bash
gcloud compute instances create $INSTANCE_NAME \
  --project=verifiable-ai-hackathon \
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
  --tags=flare-ai,http-server,https-server \
  --create-disk=auto-delete=yes,\
boot=yes,\
device-name=$INSTANCE_NAME,\
image=projects/confidential-space-images/global/images/confidential-space-debug-0-tdxpreview-c38b622,\
mode=rw,\
size=11,\
type=pd-balanced \
  --shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --confidential-compute-type=TDX
```

### Post-deployment

Once the instance is deploying and started you should be able to access it
at the IP address of instance, you can find the IP address by going to the GCP
Console and finding your instance.

## 🔜 Next Steps

Once your instance is running, access the Chat UI via the instance's public IP address.

### Example Interactions

- **"Create an account for me"**
- **"Show me your remote attestation"**
- **"Transfer 10 C2FLR to 0x000000000000000000000000000000000000dEaD"**

## Future Upgrades

- **TLS Communication:**  
  Encrypt communications with a RA-TLS scheme for enhanced security.

- **Expanded Flare Ecosystem Support:**
  - Token swaps through [SparkDEX](http://sparkdex.ai)
  - Borrow-lend via [Kinetic](https://linktr.ee/kinetic.market)
  - Trading strategies with [RainDEX](https://www.rainlang.xyz)

## 🔧 Troubleshooting

If you encounter issues, try the following steps:

1. **Check Logs:**

   ```bash
   gcloud compute instances get-serial-port-output defai-$TEAM_NAME --project=google-hackathon-project
   ```

2. **Verify API Key:**  
   Ensure the `GEMINI_API_KEY` environment variable is correctly set.

3. **Check Firewall Settings:**  
   Confirm that your instance is accessible publicly on port `80`.
