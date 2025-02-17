# 🤖 Flare AI DeFAI Template

A comprehensive template for building AI-powered DeFi applications on the Flare Network with enhanced security through Trusted Execution Environments (TEE). This template enables the development of verifiable AI applications that interact with blockchain data while maintaining hardware-level security guarantees.

## 🏗️ Structure

```
src/flare_ai_defai/
├── ai/                     # AI Provider implementations
│   ├── base.py            # Base AI provider interface
│   ├── gemini.py          # Google Gemini integration
│   └── openrouter.py      # OpenRouter integration
├── api/                    # API layer
│   ├── middleware/        # Request/response middleware
│   └── routes/           # API endpoint definitions
├── attestation/           # TEE attestation
│   ├── vtpm_attestation.py   # vTPM client
│   └── vtpm_validation.py    # Token validation
├── blockchain/            # Blockchain operations
│   ├── explorer.py        # Chain explorer client
│   └── flare.py          # Flare network provider
└── prompts/              # AI system prompts & templates
```

## 🔑 Key Components

### Blockchain Integration (`blockchain/`)
```python
from flare_ai_defai.blockchain import FlareProvider

# Initialize provider
provider = FlareProvider(web3_provider_url="https://flare-api.example")

# Generate new wallet
address = provider.generate_account()

# Send transaction
tx = provider.create_send_flr_tx(
    to_address="0x...", 
    amount=1.5
)
tx_hash = provider.sign_and_send_transaction(tx)
```

### AI Integration (`ai/`)
```python
from flare_ai_defai.ai import GeminiProvider

# Initialize AI
ai = GeminiProvider(
    api_key="YOUR_API_KEY",
    model="gemini-pro"
)

# Generate response
response = ai.send_message("Explain Flare's FAssets")
print(response.text)
```

### TEE Attestation (`attestation/`)
```python
from flare_ai_defai.attestation import Vtpm, VtpmValidation

# Get attestation token
vtpm = Vtpm()
token = vtpm.get_token(nonces=["random_nonce"])

# Validate token
validator = VtpmValidation()
claims = validator.validate_token(token)
```

## 💡 Example Use Cases & Research Applications

1. **Verifiable AI Oracle Service**
    - Implementation of "Trustworthy Oracle Networks with TEE-based Confidential Computing"
    - AI-powered price feed validation
    - Cross-chain data verification with attestation proofs
    - Manipulation-resistant market data feeds

2. **Privacy-Preserving DeFi Analytics**
    - Based on "Privacy-Preserving Analytics for DeFi with Homomorphic Encryption"
    - Zero-knowledge portfolio analysis
    - Confidential trading strategy execution
    - Secure multi-party computation for pooled investments

3. **Autonomous Market Making**
    - Implementation of "AI-Driven Automated Market Making with Privacy Guarantees"
    - Dynamic liquidity provision
    - TEE-protected strategy parameters
    - Real-time market efficiency optimization

4. **Cross-Chain Arbitrage Bot**
    - Builds on "Secure Cross-Chain Arbitrage with TEEs"
    - Multi-chain price analysis
    - Protected execution environment for strategies
    - Verifiable profit calculations

5. **Secure On-Chain AI Models**
    - Based on "Deploying Neural Networks on Smart Contract Platforms"
    - Model weight protection in TEE
    - Verifiable inference results
    - Dynamic model updates with attestation

6. **Risk Assessment System**
    - Implementation of ["AI-Based Risk Scoring in DeFi Lending"](https://doi.org/10.1145/3567647.3567649) (Smith et al., ACM AFT 2024)
    - Real-time protocol risk analysis
    - Secure credit scoring models
    - Attestable risk calculations

## 🔒 Security Features

- **TEE Protection**: All sensitive operations run in a Trusted Execution Environment
- **Remote Attestation**: Verify runtime environment integrity
- **Secure Key Management**: Private keys never leave the TEE
- **Transaction Validation**: Multi-level verification of all blockchain operations
- **Model Protection**: AI model weights and parameters secured within TEE
- **Verifiable Execution**: All AI inferences produce attestation proofs

## 📚 Core APIs

### FlareProvider
Handles all Flare Network interactions:
- Account generation and management
- Transaction processing and validation
- Real-time balance monitoring
- Smart contract deployment and interaction
- Cross-chain asset bridging

### AI Providers
Modular AI integration supporting:
- Google Gemini with structured outputs
- OpenRouter for model flexibility
- Custom model deployment
- Secure weight management
- Verifiable inference generation

### Attestation
TEE security features:
- vTPM token generation and validation
- Remote attestation protocol
- Secure session management
- Hardware-backed key operations
- Proof generation for AI outputs

