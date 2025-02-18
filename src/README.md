# 🤖 Flare AI DeFAI Template

A comprehensive template for building autonomous AI agents for decentralized finance (DeFi) applications with enhanced security provided by Trusted Execution Environments (TEE). This template enables AI agents to securely manage wallets, execute token transfers, and interact with smart contracts while producing verifiable attestation proofs.

## 📖 Overview

TODO

## 🚀 Key Features

- **TEE-Enabled Secure Operations**  
  All critical processes—from AI inference to blockchain transactions—are executed within a Trusted Execution Environment, ensuring robust security with verifiable remote attestation.

- **Integrated Interactive Chat UI**  
  Engage with your AI agent through a built-in chat interface, designed to provide seamless and secure real-time interaction directly from the TEE.

- **Native Flare Blockchain & Wallet Support**  
  Securely manage wallets and perform token operations on the Flare blockchain, with cryptographic assurances that your transactions and key management remain within the TEE.

- **Cutting-Edge AI Capabilities**  
  Leverage the power of Gemini 2.0 and access a wide range of over 300 LLMs, enabling advanced, structured query support and versatile AI-driven functionalities.

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

The following scripts are the crucial parts of this template and provide a strong base for building and customizing your autonomous AI agent. You can tweak these components to extend functionality, integrate additional features, or adapt them to your project's specific needs.

### Blockchain Integration (`blockchain/`)
This module handles interactions with the Flare blockchain. The `FlareProvider` class abstracts operations such as wallet creation, transaction construction, and secure transaction submission.

```python
from flare_ai_defai.blockchain import FlareProvider

# Initialize provider
provider = FlareProvider(web3_provider_url="https://flare-api.example")

# Generate a new wallet address
address = provider.generate_account()
print("New wallet address:", address)

# Create a token transfer transaction
tx = provider.create_send_flr_tx(
    to_address="0xRecipientAddress", 
    amount=1.5
)

# Sign and send the transaction
tx_hash = provider.sign_and_send_transaction(tx)
print("Transaction Hash:", tx_hash)
```

### AI Integration (`ai/`)
The AI integration layer allows you to interact with various AI providers through a unified interface. The architecture is modular enough to support alternative providers.

```python
from flare_ai_defai.ai import GeminiProvider

# Initialize the AI provider with required credentials and model settings
ai = GeminiProvider(
    api_key="YOUR_API_KEY",
    model="gemini-pro"
)

# Generate a response from the AI based on your prompt
response = ai.send_message("Explain Flare's FAssets")
print("AI Response:", response.text)
```

### TEE Attestation (`attestation/`)
The attestation module ensures that critical operations run securely within a Trusted Execution Environment.

```python
from flare_ai_defai.attestation import Vtpm, VtpmValidation

# Obtain an attestation token from the TEE
vtpm = Vtpm()
token = vtpm.get_token(nonces=["random_nonce"])
print("Attestation Token:", token)

# Validate the attestation token to ensure secure execution
validator = VtpmValidation()
claims = validator.validate_token(token)
print("Token Claims:", claims)
```


## 💡 Example Use Cases & Project Ideas

Below are several detailed project ideas demonstrating how the template can be used to build autonomous AI agents for Flare's DeFi ecosystem. Each idea outlines the practical use of the template's components and usability.

### Autonomous Wallet Manager

**Idea**: An AI agent that automatically creates wallets, monitors balances, and manages keys securely.

**Usage Details**:
- **Wallet Creation & Backup**: Use the blockchain module to generate new wallet addresses while securely storing private keys within the TEE. The template allows you to integrate backup mechanisms with attestation proofs that confirm key security.
- **Real-time Monitoring**: Leverage the blockchain explorer integration to monitor wallet activity continuously. The AI agent can analyze transaction data and trigger alerts or automated security actions if anomalies are detected.
- **TEE Integration**: All sensitive wallet operations are executed within the TEE, ensuring keys remain isolated. The template's attestation mechanisms provide verifiable logs for every wallet creation and management operation.

### Token Transfer Optimizer

**Idea**: An agent that analyzes market conditions in real time to execute token transfers for liquidity optimization or arbitrage.

**Usage Details**:
- **Market Analysis**: Integrate external data feeds into the AI provider module for real-time market insights. The agent can decide optimal moments for transfers based on analyzed market conditions.
- **Secure Transaction Execution**: Use the blockchain module to handle token transfers. With TEE-backed transaction signing, every transfer is secured and accompanied by attestation proofs for independent verification.
- **Verifiable Operations**: The template ensures that all transfers are logged with cryptographic proofs, enabling third-party verification of the autonomous decision-making process.

### Smart Contract Interaction Bot

**Idea**: An AI agent that interacts with smart contracts for activities like yield farming, staking, or decentralized lending.

**Usage Details**:
- **Automated Contract Calls**: Extend the blockchain integration with methods for interacting with smart contracts. The agent can autonomously call functions like deposit, withdraw, or claim rewards based on market signals.
- **Secure and Verifiable Interactions**: Execute all contract calls within the TEE, generating attestation proofs that validate each interaction. This ensures that the operations are secure and can be audited independently.
- **Real-time Feedback**: Incorporate a verification layer to monitor the outcomes of smart contract interactions and adjust the agent's behavior accordingly.

### DeFi Risk Management Agent

**Idea**: An autonomous agent that continuously assesses risk across multiple DeFi protocols and initiates risk mitigation strategies.

**Usage Details**:
- **Risk Analytics**: Utilize the AI provider module to integrate risk scoring algorithms and gather on-chain data from multiple protocols. The agent can calculate real-time risk scores and identify potential vulnerabilities.
- **Automated Portfolio Rebalancing**: Use the blockchain module to trigger asset rebalancing operations when predefined risk thresholds are met. These actions are executed within the TEE for enhanced security.
- **Transparent Reporting**: Generate verifiable attestation reports that detail the risk assessments and the agent's corresponding actions, building trust in the autonomous risk management process.

### Cross-Protocol Aggregator

**Idea**: An AI agent that aggregates data from various DeFi protocols, compares yields, and executes cross-chain asset management strategies.

**Usage Details**:
- **Data Aggregation**: Modify the AI provider layer to fetch data from multiple blockchain networks. The agent can compare performance metrics and yield information across different protocols.
- **Cross-Chain Operations**: Extend the blockchain module to support multi-chain interactions. Secure cross-chain transfers are managed within the TEE, with each operation generating an attestation proof.
- **Verifiable Cross-Chain Actions**: The template's design allows you to implement audit trails for every cross-chain action, ensuring that asset management decisions are both secure and transparent.

### Autonomous Investment Advisor

**Idea**: An AI-driven advisor that monitors market trends, suggests asset allocations, and executes trades autonomously.

**Usage Details**:
- **Market Trend Analysis**: Integrate additional AI models or external data feeds to analyze market trends. The agent can use these insights to recommend strategic asset reallocations.
- **Automated Trade Execution**: Leverage the wallet management and token transfer modules to execute trades automatically. All trade executions occur within the TEE, ensuring secure and attested transactions.
- **Transparency & Verification**: Each trade recommendation and execution is accompanied by an attestation proof, providing a verifiable record of the decision-making process.

## 🔒 Security Features

* **TEE Protection**: All sensitive operations—including key management and transaction signing—are executed within a Trusted Execution Environment, ensuring that critical data remains isolated.
* **Remote Attestation**: vTPM-based attestation generates verifiable proofs for each operation, allowing for independent audits and trust verification.
* **Certificate-Based Validation**: Robust validation mechanisms check the integrity of certificates and fingerprints to guard against tampering.
* **Secure Key Management**: Private keys and sensitive data are confined within the TEE, preventing exposure to insecure environments.
* **Verifiable Execution**: Every autonomous operation produces an attestation log, offering a transparent audit trail for all critical actions.

## 📚 Core APIs

### FlareProvider
Manages all Flare Network operations:
- **Account Generation & Management**: Create and manage secure wallet addresses.
- **Transaction Processing & Validation**: Build, sign, and submit transactions with built-in verification.
- **Real-time Balance Monitoring**: Continuously track account balances.
- **Smart Contract Deployment & Interaction**: Deploy and interact with smart contracts securely.
- **Cross-chain Asset Bridging**: Facilitate asset transfers across multiple blockchain networks.

### AI Providers
Flexible, modular integration of AI services:
- **Google Gemini**: Leverage structured outputs from Gemini’s latest models.
- **OpenRouter Support**: Enable access to a variety of LLMs for diverse use cases.
- **Custom Model Deployment**: Integrate your own AI models seamlessly.
- **Secure Weight Management**: Protect model parameters within a TEE.
- **Verifiable Inference Generation**: Produce AI outputs with cryptographic attestation for auditability.

### Attestation
Robust TEE-based security mechanisms:
- **vTPM Token Generation & Validation**: Generate cryptographic tokens confirming secure execution.
- **Remote Attestation Protocol**: Ensure that operations occur in a trusted execution environment.
- **Secure Session Management**: Maintain isolated and secure communication sessions.
- **Hardware-Backed Key Operations**: Manage keys with hardware-level security guarantees.
- **Proof Generation for AI Outputs**: Produce verifiable proofs for every critical AI inference.

