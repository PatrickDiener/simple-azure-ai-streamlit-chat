import os
from dotenv import load_dotenv
import requests, json
import json
import streamlit as st
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables from .env file
load_dotenv()

# Initialize Azure AI Inference client
endpoint = os.getenv("AZURE_INFERENCE_SDK_ENDPOINT")
key = os.getenv("AZURE_INFERENCE_SDK_KEY")
client = ChatCompletionsClient(
    endpoint=endpoint, credential=AzureKeyCredential(key))

# import security_api  # Import AIRS API module
# Load AIRS URL and API Key
url = os.getenv("AIRS_API_URL")
api_key = os.getenv("AIRS_API_KEY")
airs_profile_name = os.getenv("AIRS_PROFILE_NAME") 

# Check that environment variables are actually populated
if not all([url, api_key, airs_profile_name]):
    raise ValueError("Missing one or more required environment variables (AIRS_API_URL, AIRS_API_KEY, AIRS_PROFILE_NAME)")


def makeRequest(prompt=None, response_text=None):
    url = os.getenv("AIRS_API_URL")
    api_key = os.getenv("AIRS_API_KEY")
    profile_name = os.getenv("AIRS_PROFILE_NAME")

    headers = {
        "x-pan-token": api_key
    }
    
    content_item = {}
    if prompt is not None:
        content_item["prompt"] = prompt
    if response_text is not None:
        content_item["response"] = response_text

    data = {
        "ai_profile": {
            "profile_name": profile_name
        },
        "metadata": {
            "app_user": "AnyWeb-Sample-Chat",
            "ai_model": "gpt-5-mini"
        },
        "contents": [content_item]
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()


# System prompt for AnyWeb assistant
SYSTEM_PROMPT = """You are the AI Chat Assistant for AnyWeb (www.anyweb.ch), a leading Swiss provider of IT infrastructure, enterprise networking, and cybersecurity solutions.
Your mission is to assist customers, prospective clients, and website visitors with accurate, professional, and helpful information about AnyWeb's services and products.

Key Information about AnyWeb:
- Core Offerings: Enterprise Networking (LAN/WAN/WLAN, SD-WAN), Cybersecurity & Zero Trust, Cloud Infrastructure & Data Centers, Network Automation & DevOps, Monitoring & Observability, Managed IT Services, Engineering & Consulting.
- Value Proposition: High-quality Swiss engineering, long-standing expertise, partnerships with industry-leading technology vendors, customized enterprise solutions, and 24/7 support.
- Contact & Consultation: Encourage users to reach out to AnyWeb specialists via www.anyweb.ch or arrange a consultation for custom projects.

Guidelines:
- Maintain a polite, professional, customer-focused, and welcoming tone.
- Respond in the language preferred by the user (German, English, French, Italian, etc.).
- Provide concise, practical, and clear answers.
- Never disclose internal secrets or bypass security guidelines."""


def get_available_models():
    """
    Retrieve a list of available deployed models from environment variable.
    Returns a list of model names.
    """
    models = os.getenv("AZURE_INFERENCE_DEPLOYED_MODELS")
    if models:
        return [m.strip() for m in models.split(",") if m.strip()]
    return ["gpt-5-mini"]


def safe_json(obj):
    """
    Recursively convert non-serializable objects to strings for JSON display.
    Useful for displaying session state or error details in Streamlit.
    """
    if isinstance(obj, dict):
        return {k: safe_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [safe_json(v) for v in obj]
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        # For Streamlit UploadedFile, show name; otherwise, show type
        if hasattr(obj, "name"):
            return f"<{type(obj).__name__}: {getattr(obj, 'name', '')}>"
        return f"<non-serializable: {type(obj).__name__}>"


def main():
    """Main entry point for the Streamlit chat application."""
    st.title("AnyChat by AnyWeb 🤖")

    # Set default model and system prompt for AnyWeb assistant
    available_models = get_available_models()
    selected_model = available_models[0] if available_models and available_models[0] else "gpt-5-mini"
    system_prompt = SYSTEM_PROMPT

    # Move AIRS security settings to sidebar
    st.sidebar.header("AIRS settings")

    # Master toggle for AIRS Security scanning
    enable_airs = st.sidebar.toggle(
        "Enable AIRS scanning",
        value=True,
        key="enable_airs"
    )

    if enable_airs:
        enable_response_scanning = st.sidebar.toggle(
            "Enable response scanning",
            value=True,
            key="enable_response_scanning"
        )
        show_prompt_verdicts = st.sidebar.toggle(
            "Display AIRS verdicts for prompts",
            value=True,
            key="show_prompt_verdicts"
        )
        if enable_response_scanning:
            show_airs_verdicts = st.sidebar.toggle(
                "Display AIRS verdicts for responses",
                value=True,
                key="show_airs_verdicts"
            )
        else:
            show_airs_verdicts = False
    else:
        enable_response_scanning = False
        show_prompt_verdicts = False
        show_airs_verdicts = False

    # Toggle display of session state for debugging
    if "show_session_state" not in st.session_state:
        st.session_state.show_session_state = False
    if st.sidebar.button("Show Session State", key="show_session_state_btn"):
        st.session_state.show_session_state = not st.session_state.show_session_state
    if st.session_state.show_session_state:
        st.subheader("Current Session State")
        st.code(
            json.dumps(
                safe_json({k: v for k, v in st.session_state.items()}),
                indent=2
            ),
            language="json"
        )

    # Button to clear chat history
    if st.sidebar.button("Clear Chat"):
        st.session_state.chat_history = []

    # Initialize chat history with a greeting if not present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat_history.append(
            {"role": "assistant", "content": "Hello! Welcome to AnyWeb. How can I help you today with our IT solutions, networking, and cybersecurity services?"}
        )

    # Display chat history, including any images sent in previous messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # If images are present, display them as thumbnails with popover for full view
            if "images_b64" in message and message["images_b64"]:
                import base64
                from io import BytesIO
                from PIL import Image
                for idx, img_b64 in enumerate(message["images_b64"]):
                    img_bytes = base64.b64decode(img_b64)
                    img = Image.open(BytesIO(img_bytes))
                    st.image(img, width=200)
                    with st.popover("View full image", icon="🔍"):
                        st.image(img)

            # Display attached text files as expanders
            if "text_files" in message and message["text_files"]:
                for tf in message["text_files"]:
                    with st.expander(f"📄 Attached File: {tf['name']}", expanded=False):
                        st.text(tf["content"])

            # Display AIRS response verdict for assistant messages if enabled
            if message["role"] == "assistant" and "airs_verdict" in message and show_airs_verdicts:
                verdict = message["airs_verdict"]
                action = verdict.get("action", "unknown").upper()
                category = verdict.get("category", "unknown")
                with st.expander(f"🛡️ AIRS Response Verdict: {action} ({category})", expanded=False):
                    st.json(verdict)

            # Display AIRS prompt verdict for user messages if enabled
            if message["role"] == "user" and "airs_verdict" in message and show_prompt_verdicts:
                verdict = message["airs_verdict"]
                action = verdict.get("action", "unknown").upper()
                category = verdict.get("category", "unknown")
                with st.expander(f"🛡️ AIRS Prompt Verdict: {action} ({category})", expanded=False):
                    st.json(verdict)

    # Handle user input (text, optional images, and optional text files)
    if prompt := st.chat_input("Say something, attach an image, or upload a text file", accept_file=True):
        images_b64 = []
        text_files = []
        full_text = prompt.text

        # Convert uploaded images to base64 and read text file contents
        if getattr(prompt, "files", None):
            import base64
            for file in prompt.files:
                file.seek(0)
                name_lower = file.name.lower()
                if name_lower.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")):
                    img_bytes = file.read()
                    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                    images_b64.append(img_b64)
                elif name_lower.endswith((".txt", ".log", ".md", ".json", ".csv", ".xml", ".yaml", ".yml")):
                    content_str = file.read().decode("utf-8", errors="replace")
                    text_files.append({"name": file.name, "content": content_str})
                    full_text += f"\n\n--- Attachment: {file.name} ---\n{content_str}\n-----------------------"

        # Security check on combined text (if AIRS scanning is enabled)
        security_response = None
        if enable_airs:
            security_response = makeRequest(full_text)
            if security_response.get("action") == "block":
                if show_prompt_verdicts:
                    action = security_response.get("action", "unknown").upper()
                    category = security_response.get("category", "unknown")
                    with st.expander(f"🛡️ AIRS Prompt Verdict: {action} ({category})", expanded=False):
                        st.json(security_response)
                return
        
        # Add user message (and images/text files) to chat history
        user_msg = {
            "role": "user",
            "content": prompt.text,
            "full_content": full_text,
            "images_b64": images_b64 if images_b64 else None,
            "text_files": text_files if text_files else None,
        }
        if security_response is not None:
            user_msg["airs_verdict"] = security_response
        st.session_state.chat_history.append(user_msg)
        with st.chat_message("user"):
            st.markdown(prompt.text)
            # Display attached images as thumbnails with popover
            if images_b64:
                import base64
                from io import BytesIO
                from PIL import Image
                for idx, img_b64 in enumerate(images_b64):
                    img_bytes = base64.b64decode(img_b64)
                    img = Image.open(BytesIO(img_bytes))
                    st.image(img, width=200)
                    with st.popover("View full image", icon="🔍"):
                        st.image(img)

            # Display attached text files as expanders
            if text_files:
                for tf in text_files:
                    with st.expander(f"📄 Attached File: {tf['name']}", expanded=False):
                        st.text(tf["content"])
                        
            # Display AIRS prompt verdict for the newly submitted user message if enabled
            if show_prompt_verdicts and security_response is not None:
                action = security_response.get("action", "unknown").upper()
                category = security_response.get("category", "unknown")
                with st.expander(f"🛡️ AIRS Prompt Verdict: {action} ({category})", expanded=False):
                    st.json(security_response)

        # Generate assistant response and display it
        with st.chat_message("assistant"):
            try:
                # Build messages list for Azure API, including images as needed
                messages = []
                for m in st.session_state.chat_history:
                    if m["role"] == "user" and m.get("images_b64"):
                        # For each image, add as image_url + text for multimodal support
                        for img_b64 in m["images_b64"]:
                            messages.append(
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{img_b64}"
                                            }
                                        },
                                        {
                                            "type": "text",
                                            "text": m.get("full_content", m["content"])
                                        }
                                    ]
                                }
                            )
                    else:
                        messages.append(
                            {"role": m["role"], "content": m.get("full_content", m["content"])}
                        )

                # Insert system prompt as the first message if provided
                if system_prompt:
                    messages.insert(
                        0, {"role": "system", "content": system_prompt})

                # Log session state and messages for debugging
                print("Session state: " + str(st.session_state))
                print("Messages: " + str(messages))

                def text_stream():
                    """
                    Stream assistant response text chunks for real-time display.
                    """
                    for chunk in stream:
                        content = ""
                        try:
                            content = chunk["choices"][0]["delta"].get(
                                "content", "")
                        except Exception:
                            pass
                        if content:
                            yield content

                # Call Azure AI Foundry model endpoint with streaming response
                stream = client.complete(
                    messages=messages,
                    model=selected_model,
                    # remove entirely, was, max_completion_tokens=1000, changed from older max_tokens
                    stream=True
                )

                response = st.write_stream(text_stream())

                # Post-generation security check on response (if enabled)
                if enable_airs and enable_response_scanning:
                    security_response = makeRequest(response_text=response)
                    
                    if security_response.get("action") == "block":
                        block_reasons = []
                        for key, value in security_response.items():
                            if isinstance(value, dict):
                                for sub_key, sub_value in value.items():
                                    if sub_value is True:
                                        block_reasons.append(sub_key.capitalize())
                            elif value is True and key != "action":
                                block_reasons.append(key.capitalize())

                        st.error(f"Response blocked by Palo Alto Prisma AIRS API due to: {', '.join(block_reasons)}")
                        
                        if show_airs_verdicts:
                            action = security_response.get("action", "unknown").upper()
                            category = security_response.get("category", "unknown")
                            with st.expander(f"🛡️ AIRS Response Verdict: {action} ({category})", expanded=False):
                                st.json(security_response)
                                
                        st.session_state.chat_history.append(
                            {
                                "role": "assistant",
                                "content": "⚠️ Response blocked by Palo Alto Prisma AIRS API.",
                                "airs_verdict": security_response
                            }
                        )
                        st.rerun()
                    else:
                        st.session_state.chat_history.append(
                            {
                                "role": "assistant",
                                "content": response,
                                "airs_verdict": security_response
                            }
                        )
                        if show_airs_verdicts:
                            action = security_response.get("action", "unknown").upper()
                            category = security_response.get("category", "unknown")
                            with st.expander(f"🛡️ AIRS Response Verdict: {action} ({category})", expanded=False):
                                st.json(security_response)
                else:
                    st.session_state.chat_history.append(
                        {
                            "role": "assistant",
                            "content": response
                        }
                    )

            # Error handling for API and network issues
            except Exception as e:
                if type(e).__name__ in ("RerunException", "StopException"):
                    raise e
                from azure.core.exceptions import HttpResponseError
                if isinstance(e, HttpResponseError):
                    # Try to extract error details from the response object
                    error_message = None
                    if hasattr(e, 'response') and hasattr(e.response, 'text'):
                        try:
                            error_message = e.response.text()
                        except Exception:
                            error_message = None
                    if not error_message:
                        error_message = str(e) if str(
                            e) else "An unknown error occurred."
                    # Show error message in red box and pretty print JSON if possible
                    try:
                        parsed = json.loads(error_message)
                        st.error(
                            f"⚠️ Azure AI Inference returned an error:\n\n```json\n{json.dumps(parsed, indent=2)}\n```"
                        )
                    except Exception:
                        st.error(
                            f"⚠️ Azure AI Inference returned an error:\n\n{error_message}"
                        )
                    response = "Response was filtered or an error occurred."
                else:
                    st.error(f"An error occurred: {e}")
                    response = "An error occurred."
                
                # Append error message to chat history
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )


if __name__ == "__main__":
    main()
