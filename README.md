# Flare AI DeFAI

Flare AI Kit template for AI x DeFi (DeFAI).

## 🚀 Key Features

- **Secure AI Execution**  
  Runs within a Trusted Execution Environment (TEE) featuring remote attestation support for robust security.

- **Built-in Chat UI**  
  Interact with your AI via a TEE-served chat interface.

- **Flare Blockchain and Wallet Integration**  
  Perform token operations and generate wallets from within the TEE.

- **Gemini 2.0 Support**  
  Utilize Google Gemini’s structured query support for advanced AI functionalities.

<img width="500" alt="Artemis" src="https://github.com/user-attachments/assets/921fbfe2-9d52-496c-9b48-9dfc32a86208" />

## 🏗️ Build & Run Instructions

You can deploy Flare AI DeFAI using Docker (recommended) or set up the backend and frontend manually.

### Environment Setup

1. **Prepare the Environment File:**  
   Rename `.env.example` to `.env` and update the variables accordingly.
   > **Tip:** Set `SIMULATE_ATTESTATION=true` for local testing.

### Build using Docker (Recommended)

The Docker setup mimics a TEE environment and includes an Nginx server for routing, while Supervisor manages both the backend and frontend services in a single container.

1. **Build the Docker Image:**

   ```bash
   docker build -t flare-ai-defai .
   ```

2. **Run the Docker Container:**

   ```bash
   docker run -p 80:80 -it --env-file .env flare-ai-defai
   ```

3. **Access the Frontend:**  
   Open your browser and navigate to [http://localhost:80](http://localhost:80) to interact with the Chat UI.

### Build manually

Flare AI DeFAI is composed of a Python-based backend and a JavaScript frontend. Follow these steps for manual setup:

#### Backend Setup

1. **Install Dependencies:**  
   Use [uv](https://docs.astral.sh/uv/getting-started/installation/) to install backend dependencies:

   ```bash
   uv sync --all-extras
   ```

2. **Start the Backend:**  
   The backend runs by default on `0.0.0.0:8080`:

   ```bash
   uv run start-backend
   ```

#### Frontend Setup

1. **Install Dependencies:**  
   In the `chat-ui/` directory, install the required packages using [npm](https://nodejs.org/en/download):

   ```bash
   cd chat-ui/
   npm install
   ```

2. **Configure the Frontend:**  
   Update the backend URL in `chat-ui/src/App.js` for testing:

   ```js
   const BACKEND_ROUTE = "http://localhost:8080/api/routes/chat/";
   ```

   > **Note:** Remember to change `BACKEND_ROUTE` back to `'api/routes/chat/'` after testing.

3. **Start the Frontend:**

   ```bash
   npm start
   ```

## 🚀 Deploy on TEE

Deploy Flare AI DeFAI on a Confidential Space Instances (using AMD SEV or Intel TDX) to benefit from enhanced hardware-backed security.

### Prerequisites

- **Google Cloud Platform Account:**  
  Access to the `verifiable-ai-hackathon` project is required.

- **Gemini API Key:**  
  Ensure your [Gemini API key](https://aistudio.google.com/app/apikey) is linked to the project.

- **gcloud CLI:**  
  Install and authenticate the [gcloud CLI](https://cloud.google.com/sdk/docs/install).

### Environment Configuration

1. **Set Environment Variables:**  
   Update your `.env` file with:

   ```bash
   TEE_IMAGE_REFERENCE=ghcr.io/flare-foundation/flare-ai-defai:main  # Replace with your repo build image
   INSTANCE_NAME=<PROJECT_NAME-TEAM_NAME>
   ```

2. **Load Environment Variables:**

   ```bash
   source .env
   ```

   > **Reminder:** Run the above command in every new shell session.

3. **Verify the Setup:**

   ```bash
   echo $TEE_IMAGE_REFERENCE
   # Expected output: ghcr.io/flare-foundation/flare-ai-defai:main
   ```

### Deploying to Confidential Space

For deployment on Confidential Space (AMD SEV):

```bash
gcloud compute instances create $INSTANCE_NAME \
  --project=pacific-smile-435514-h4 \
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
  --service-account=magureanuhoria@pacific-smile-435514-h4.iam.gserviceaccount.com \
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
  --reservation-affinity=any \
  --confidential-compute-type=SEV
```

#### Post-deployment

After deployment, you should see an output similar to:

```plaintext
NAME          ZONE           MACHINE_TYPE    PREEMPTIBLE  INTERNAL_IP  EXTERNAL_IP    STATUS
defai-team1   us-central1-c  n2d-standard-2               10.128.0.18  34.41.127.200  RUNNING
```

It may take a few minutes for Confidential Space to complete startup checks. You can monitor progress via the GCP Console by clicking **Serial port 1 (console)**. When you see a message like:

```plaintext
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

the container is ready. Navigate to the external IP to access the Chat UI.

## 🔜 Next Steps

Once your instance is running, access the Chat UI using its public IP address. Here are some example interactions to try:

- **"Create an account for me"**
- **"Transfer 10 C2FLR to 0x000000000000000000000000000000000000dEaD"**
- **"Show me your remote attestation"**

## Future Upgrades

- **TLS Communication:**  
  Implement RA-TLS for encrypted communication.

- **Expanded Flare Ecosystem Support:**
  - **Token Swaps:** via [SparkDEX](http://sparkdex.ai)
  - **Borrow-Lend:** via [Kinetic](https://linktr.ee/kinetic.market)
  - **Trading Strategies:** via [RainDEX](https://www.rainlang.xyz)

## 🔧 Troubleshooting

If you encounter issues, follow these steps:

1. **Check Logs:**

   ```bash
   gcloud compute instances get-serial-port-output defai-$TEAM_NAME --project=google-hackathon-project
   ```

2. **Verify API Key:**  
   Ensure that the `GEMINI_API_KEY` environment variable is set correctly.

3. **Check Firewall Settings:**  
   Confirm that your instance is publicly accessible on port `80`.
