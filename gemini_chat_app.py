import streamlit as st
import os
from google import genai
from google.genai import types
from google.genai.errors import APIError

# --- Configuration and Caching ---

def get_api_key():
    """Retrieves the GEMINI_API_KEY securely from Streamlit secrets."""
    try:
        # Streamlit securely loads secrets from .streamlit/secrets.toml
        key = st.secrets["GEMINI_API_KEY"]
        return key
    except KeyError:
        st.error("GEMINI_API_KEY not found. Please set your Gemini API key in Streamlit secrets.")
        st.stop()

@st.cache_resource
def get_gemini_chat_session():
    """Initializes and caches the Gemini client and chat session."""
    api_key = get_api_key()
    
    # 1. Configure the Gemini client
    client = genai.Client(api_key=api_key)

    # 2. Define System Instruction and Model
    # gemini-2.5-flash is used for its speed and suitability for chat on the free tier.
    config = types.GenerateContentConfig(
        system_instruction="You are a friendly, helpful AI assistant named StreamlitChat. Keep your answers concise but informative."
    )
    
    # 3. Start a persistent chat session to maintain memory
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=config,
    )
    st.success("Gemini chat session started.")
    return chat

# --- Main Application Logic ---

def main():
    st.set_page_config(page_title="Free Gemini Chatbot", page_icon="⭐")
    st.title("⭐ Gemini Chatbot")
    st.caption("Powered by Gemini 2.5 Flash and Streamlit Community Cloud (Free Tier)")

    # 1. Initialize chat session and client
    try:
        chat = get_gemini_chat_session()
    except:
        # Error message is handled within get_api_key
        return

    # 2. Initialize Chat History in Session State
    if "messages" not in st.session_state:
        st.session_state.messages = [
            types.Content(role="model", parts=[types.Part.from_text("Hello! I'm StreamlitChat. How can I help you today?")])
        ]

    # 3. Display Chat Messages
    for message in st.session_state.messages:
        # The Streamlit chat message UI uses "user" and "assistant" roles
        role = "user" if message.role == "user" else "assistant"
        with st.chat_message(role):
            # Access the content of the message
            st.markdown(message.parts[0].text)

    # 4. Handle User Input
    if prompt := st.chat_input("Ask a question..."):
        # 4a. Add user message to history and display
        user_message = types.Content(role="user", parts=[types.Part.from_text(prompt)])
        st.session_state.messages.append(user_message)
        
        with st.chat_message("user"):
            st.markdown(prompt)

        # 4b. Send message to Gemini and stream response
        with st.chat_message("assistant"):
            with st.spinner("Gemini is thinking..."):
                try:
                    # Stream the response from the chat session
                    response_stream = chat.send_message(prompt, stream=True)
                    
                    full_response = ""
                    # Display the response chunk by chunk (streaming)
                    placeholder = st.empty()
                    for chunk in response_stream:
                        if chunk.text:
                            full_response += chunk.text
                            placeholder.markdown(full_response + "▌") # Use '▌' for typing indicator
                    placeholder.markdown(full_response) # Final complete response

                    # 4c. Store the final AI response (role 'model' is used by the Gemini SDK)
                    ai_response_content = types.Content(role="model", parts=[types.Part.from_text(full_response)])
                    st.session_state.messages.append(ai_response_content)

                except APIError as e:
                    error_message = f"An API Error occurred: {e}"
                    st.error(error_message)
                    st.session_state.messages.append(types.Content(role="model", parts=[types.Part.from_text("Sorry, I encountered an API error.")]))

if __name__ == "__main__":
    main()
```eof

### 2. Dependencies File (`requirements.txt`)

```markdown:Required Python Libraries:requirements.txt
streamlit
google-genai
```eof

***

## Phase 2: Free Deployment Instructions

1.  **Get Your Key:** Obtain your free-tier **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  **GitHub Setup:** Create a **public GitHub repository** and upload both files: `gemini_chat_app.py` and `requirements.txt`.
3.  **Streamlit Secret:** Set your API key in the Streamlit Cloud secrets management:
    * Go to your Streamlit Community Cloud dashboard.
    * Click on **Settings** -> **Secrets**.
    * Input the following content into the **`.streamlit/secrets.toml`** editor:
    ```toml
    # .streamlit/secrets.toml
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
    ```
4.  **Deploy:** Link your GitHub repository to Streamlit Community Cloud, setting the **Main file path** to `gemini_chat_app.py`. Your chatbot will deploy for free and be accessible via the public URL.

You can find a tutorial for a similar deployment setup on YouTube.

[Building a LLM Chatbot using Google's Gemini Pro with Streamlit Python](https://www.youtube.com/watch?v=sf5MrM0AIiU) will walk you through deploying a Gemini-powered chatbot using Streamlit and Python.
http://googleusercontent.com/youtube_content/6
