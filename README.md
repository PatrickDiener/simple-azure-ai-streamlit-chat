# Simple Azure AI Streamlit Chat Template

This project provides a simple Streamlit chat app to get you started with Azure AI Foundry, Azure AI Inference client library for Python, and Palo Alto Networks AI Runtime Security (AIRS).

![Screenshot](docs/media/screenshot.png)

## 📝 Overview

This template provides a secure, interactive web-based chat experience. It integrates with Azure AI for state-of-the-art model inference and incorporates robust real-time security scanning of both prompts and responses using Palo Alto Networks AIRS API.

### Features

- **AnyWeb AI Assistant**: Customized system prompt tailored for visitors and customers inquiring about AnyWeb (www.anyweb.ch) services and products (Enterprise Networking, Cybersecurity, Cloud, Automation, and Consulting).
- **Azure AI Inference Integration**: Powered by state-of-the-art Azure AI Foundry models.
- **Multimodal & File Support**: Supports uploading images and attaching text files (`.txt`, `.log`, `.md`, `.json`, etc.) alongside chat prompts.
- **Palo Alto Networks AIRS Security Checks**:
  - **Prompt Scanning**: Every user prompt and text attachment is scanned before being forwarded to Azure AI. Unsafe prompts are blocked safely without contacting the LLM.
  - **Response Scanning**: Every AI-generated response can be scanned upon completion. If a response violates security policy, it is intercepted, blocked, and replaced with a secure warning.
- **Granular Security Controls**: Dedicated sidebar toggles to turn AIRS scanning on/off and inspect detailed security scan JSON payloads directly below prompts and responses.
- **Chat History Management**: Clear or view full session state at any time via sidebar controls.

---

## ⚙️ Configuration & Environment Variables

To run the application, configure your `.env` file with both Azure AI Inference and Palo Alto AIRS credentials:

```bash
# Azure AI Inference Settings
AZURE_INFERENCE_SDK_ENDPOINT=https://<your-azure-ai-inference-endpoint>
AZURE_INFERENCE_SDK_KEY=<your-azure-key>
AZURE_INFERENCE_DEPLOYED_MODELS=gpt-5-mini

# Palo Alto Networks AI Runtime Security (AIRS) Settings
AIRS_API_URL=https://service-de.api.aisecurity.paloaltonetworks.com/v1/scan/sync/request
AIRS_API_KEY=<your-airs-api-key>
AIRS_PROFILE_NAME=<your-airs-security-profile-name>
```

---

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gerbermarco/simple-azure-ai-streamlit-chat.git
   cd simple-azure-ai-streamlit-chat
   ```

2. **Setup environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and fill in your Azure AI and Palo Alto AIRS details
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

---

## 🛡️ Security Inspection Controls

The sidebar includes intuitive toggles for scanning and auditing security verdicts:
- **Enable AIRS scanning**: Master toggle to turn Palo Alto AIRS scanning on or off for all chat interactions.
  - **Enable response scanning**: (Available when AIRS is enabled) Selectively turn AI response scanning on or off.
  - **Display AIRS verdicts for prompts**: Toggles display of the prompt security audit report.
  - **Display AIRS verdicts for responses**: (Available when response scanning is enabled) Toggles display of the response security audit report.

When verdict display is turned on, an expander box labeled `🛡️ AIRS Prompt Verdict` or `🛡️ AIRS Response Verdict` will appear below the respective chat messages, rendering the raw JSON verdict containing details such as toxicity levels, policy actions, and risk categories.
