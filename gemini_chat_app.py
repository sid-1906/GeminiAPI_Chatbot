import streamlit as st
import os
from google import genai
from google.genai import types
from google.genai.errors import APIError
from google.genai.types import Content, Part # Explicitly import Content and Part

# --- Configuration and Caching ---

def get_api_key():
    """Retrieves the GEMINI_API_KEY securely from Streamlit secrets."""
    try:
        # Streamlit securely loads secrets from .streamlit/secrets.toml
        key = st.secrets["GEMINI_API_KEY"]
        return key
    except KeyError:
        st.error("🔑 **GEMINI_API_KEY** not found. Please set your Gemini API key in Streamlit secrets.")
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
    st.success("Gemini chat session started. Ready to chat!")
    return chat

# --- Main Application Logic ---

def main():
    st.set_page_config(page_title="Free Gemini Chatbot", page_icon="⭐")
    st.title("⭐ Gemini Chatbot")
    st.caption("Powered by **Gemini 2.5 Flash** and Streamlit Community Cloud (Free Tier)")

    # 1. Initialize chat session
    try:
        chat = get_gemini_chat_session()
    except:
        # Execution halts in get_api_key if key is missing
        return

    # 2. Initialize Chat History in Session State
    if "messages" not in st.session_state:
        # Initial welcome message using the correct Content/Part types
        welcome_message = Part.from_text("Hello! I'm StreamlitChat. How can I help you today?")
        st.session_state.messages = [
            Content(role="model", parts=[welcome_message])
        ]

    # 3. Display Chat Messages
    for message in st.session_state.messages:
        # Streamlit chat message UI uses "user" and "assistant" roles
        role = "user" if message.role == "user" else "assistant"
        with st.chat_message(role):
            # Access the content of the message
            st.markdown(message.parts[0].text)

    # 4. Handle User Input
    if prompt := st.chat_input("Ask a question..."):
        # 4a. Add user message to history and display
        user_message = Content(role="user", parts=[Part.from_text(prompt)])
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
                    placeholder = st.empty()
                    for chunk in response_stream:
                        if chunk.text:
                            full_response += chunk.text
                            # Use markdown to display and the typing indicator
                            placeholder.markdown(full_response + "▌") 
                    placeholder.markdown(full_response) # Final complete response

                    # 4c. Store the final AI response (role 'model' is used by the Gemini SDK)
                    ai_response_content = Content(role="model", parts=[Part.from_text(full_response)])
                    st.session_state.messages.append(ai_response_content)

                except APIError as e:
                    error_message = f"An API Error occurred: {e}"
                    st.error(error_message)
                    st.session_state.messages.append(Content(role="model", parts=[Part.from_text("Sorry, I encountered an API error and couldn't generate a response.")]))

if __name__ == "__main__":
    main()
