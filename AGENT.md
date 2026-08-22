# AGENT.md - Developer & AI Agent Guide

This document provides architectural context, codebase conventions, and operational workflows for AI agents and developers working on the **AnyChat by AnyWeb** project.

---

## 1. Project Overview & Architecture

- **Framework**: [Streamlit](https://streamlit.io/) (`app.py`) for interactive conversational UI.
- **LLM Backend**: Azure AI Foundry using `azure-ai-inference` (`ChatCompletionsClient`) with model streaming.
- **Security Engine**: [Palo Alto Networks AI Runtime Security (AIRS)](https://www.paloaltonetworks.com/) synchronous scan API (`/v1/scan/sync/request`) for real-time prompt and response filtering.
- **Persona / System Prompt**: Dedicated corporate assistant for **AnyWeb (www.anyweb.ch)**, Switzerland-based enterprise networking, cybersecurity, cloud, and automation provider.

---

## 2. Core Architectural Components (`app.py`)

### A. AIRS Security Interface (`makeRequest`)
- **Function**: `makeRequest(prompt=None, response_text=None)`
- **Endpoint**: Configured via `AIRS_API_URL`, authenticated with `x-pan-token: AIRS_API_KEY`.
- **Payload Schema**:
  ```json
  {
    "ai_profile": { "profile_name": "<AIRS_PROFILE_NAME>" },
    "metadata": {
      "app_user": "AnyWeb-Sample-Chat",
      "ai_model": "gpt-5-mini"
    },
    "contents": [
      {
        "prompt": "<combined user text and attachments>",
        "response": "<streamed model output>"
      }
    ]
  }
  ```
- **Response Handling**:
  - `action`: `"allow"` or `"block"`.
  - `category`: Risk classification (e.g. `benign`, `toxic_content`, etc.).
  - `response_detected` / `prompt_detected`: Specific threat detections.

---

### B. Security Toggle Hierarchy (Sidebar)

```
AIRS settings (Sidebar Header)
├── Enable AIRS scanning (Master Toggle, default: True)
│   ├── Enable response scanning (Sub-toggle, default: True)
│   ├── Display AIRS verdicts for prompts (Toggle, default: True)
│   └── Display AIRS verdicts for responses (Toggle, shown if response scanning is ON)
```

- When **AIRS Scanning is OFF**: Bypasses all prompt/response scans and hides verdict widgets.
- When **Response Scanning is OFF**: Prompts are scanned, but generated responses bypass AIRS scanning to reduce latency and API calls.

---

### C. Input & Multimodal File Processing

When users submit input via `st.chat_input(..., accept_file=True)`:
1. **Images** (`.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.bmp`):
   - Encoded to base64 (`images_b64`).
   - Transmitted to Azure AI using multimodal `image_url` objects.
2. **Text Documents** (`.txt`, `.log`, `.md`, `.json`, `.csv`, `.xml`, `.yaml`, `.yml`):
   - Decoded as UTF-8 strings.
   - Appended to `full_text` under an annotated delimiter (`--- Attachment: <filename> ---`).
   - Displayed in chat UI using expandable `📄 Attached File: <name>` widgets.
3. **Security Pre-check**:
   - `makeRequest(full_text)` checks the unified text (prompt + file contents).
   - If blocked: Prompt execution aborts without making an Azure AI API call.

---

### D. Streaming & Response Security Interception

1. The response is streamed to the UI via `client.complete(..., stream=True)` and captured into `response = st.write_stream(text_stream())`.
2. **Post-generation scan** (`if enable_airs and enable_response_scanning`):
   - Invokes `makeRequest(response_text=response)`.
   - If **allowed**: Message is committed to `st.session_state.chat_history` alongside its `airs_verdict`.
   - If **blocked**:
     - Displays error reasons with `st.error(...)`.
     - Appends a sanitized placeholder `⚠️ Response blocked by Palo Alto Prisma AIRS API.` and `airs_verdict` to history.
     - Triggers `st.rerun()` to replace the streamed output with the blocked placeholder.
3. **Streamlit Exception Handling**:
   - To prevent `st.rerun()` or `st.stop()` from being caught by generic `except Exception`, the exception handler explicitly preserves Streamlit control-flow exceptions:
     ```python
     if type(e).__name__ in ("RerunException", "StopException"):
         raise e
     ```

---

## 3. Session State & Chat History Schema

Messages in `st.session_state.chat_history` follow this dictionary structure:

```python
{
    "role": "user" | "assistant",
    "content": str,                       # Display text
    "full_content": Optional[str],        # Full prompt with attachments for Azure
    "images_b64": Optional[List[str]],    # Base64 image list
    "text_files": Optional[List[dict]],   # [{"name": str, "content": str}]
    "airs_verdict": Optional[dict]        # Palo Alto AIRS JSON verdict
}
```

---

## 4. Environment Variables Reference

| Variable | Description |
|---|---|
| `AZURE_INFERENCE_SDK_ENDPOINT` | Azure AI Foundry Model Inference Endpoint URL |
| `AZURE_INFERENCE_SDK_KEY` | Azure AI Inference API Key |
| `AZURE_INFERENCE_DEPLOYED_MODELS` | Comma-separated list of deployed models (e.g. `gpt-5-mini`) |
| `AIRS_API_URL` | Palo Alto AIRS sync scan endpoint URL |
| `AIRS_API_KEY` | Palo Alto AIRS API authentication token (`x-pan-token`) |
| `AIRS_PROFILE_NAME` | Palo Alto AIRS security profile name configured in SCM |

---

## 5. Development & Testing Procedures

- **Dependencies**: Listed in `requirements.txt` (`requests`, `python-dotenv`, `streamlit`, `Pillow`, `azure-identity`, `azure-ai-inference`).
- **Syntax & Compilation Verification**:
  ```bash
  ./venv/bin/python -m py_compile app.py
  ```
- **Running the Application**:
  ```bash
  ./venv/bin/streamlit run app.py
  ```
