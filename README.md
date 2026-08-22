# Simple Azure AI Streamlit Chat Template

This project provides a simple Streamlit chat app to get you started with Azure AI Foundry, Azure AI Inference client library for Python, and Palo Alto Networks AI Runtime Security (AIRS).

![Screenshot](docs/media/screenshot.png)

## 📝 Overview

This template provides a secure, interactive web-based chat experience. It integrates with Azure AI for state-of-the-art model inference and incorporates robust real-time security scanning of both prompts and responses using Palo Alto Networks AIRS API.

### Features

- **Azure AI Inference Integration**: Seamlessly switch between preconfigured AI models (e.g. `gpt-5-mini`) via a dropdown menu.
- **System Prompt Templates**: Choose from preconfigured personalities (Funny Cowboy, Technical, etc.) or write your own custom system instructions.
- **Multimodal Support**: Supports uploading images alongside text prompts.
- **Palo Alto Networks AIRS Security Checks**:
  - **Prompt Scanning**: Every user prompt is scanned before being forwarded to Azure AI. Unsafe prompts are blocked safely without contacting the LLM.
  - **Response Scanning**: Every AI-generated response is scanned upon completion. If a response violates security policy, it is intercepted, blocked, and replaced with a secure warning.
- **Security Verdict Toggles**: Dedicated sidebar toggles allow users to easily display or hide detailed AIRS security scan JSON payloads directly below prompts and responses in the chat window.
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

The sidebar includes two toggles for auditing security verdicts:
- **Display AIRS verdicts for prompts**: Toggles display of the prompt security audit report.
- **Display AIRS verdicts for responses**: Toggles display of the response security audit report.

When turned on, an expander box labeled `🛡️ AIRS Prompt Verdict` or `🛡️ AIRS Response Verdict` will appear below the respective chat messages, rendering the raw JSON verdict containing details such as toxicity levels, policy actions, and risk categories.
