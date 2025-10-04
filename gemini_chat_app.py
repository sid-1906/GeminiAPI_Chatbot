import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError
from google.genai.types import Content, Part

# --- Configuration and Caching ---

def get_api_key():
    """Retrieves the GEMINI_API_KEY securely from Streamlit secrets."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error("🔑 **GEMINI_API_KEY** not found. Please set your Gemini API key in Streamlit secrets.")
        st.stop()

@st.cache_resource
def get_gemini_chat_session():
    """Initializes and caches the Gemini client and chat session."""
    api_key = get_api_key()
    client = genai.Client(api_key=api_key)

    config = types.GenerateContentConfig(
        system_instruction=Content(
            role="system",
            parts=[Part(text="You are a friendly, helpful AI assistant named StreamlitChat. Keep your answers concise but informative.")]
        )
    )
    
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=config,
    )
    return chat

# --- Main Application Logic ---

def main():
    st.set_page_config(page_title="⭐ Gemini Chatbot", page_icon="🤖", layout="wide")

    # --- Sidebar ---
    with st.sidebar:
        st.title("⚙️ Settings")
        st.markdown("This chatbot is powered by **Gemini 2.5 Flash**.")
        if st.button("🗑️ Clear Chat History"):
            st.session_state.clear()
            st.success("Chat history cleared! Refresh to start again.")

        st.markdown("---")
        st.markdown("👨‍💻 *Built with Streamlit & Google GenAI*")

    # --- Title ---
    st.title("🤖 Gemini Chatbot")
    st.markdown("Ask me anything and I'll try my best to help! ✨")

    # Initialize chat session
    try:
        chat = get_gemini_chat_session()
    except Exception as e:
        st.error(f"❌ Failed to start chat session: {e}")
        return

    # Initialize session messages
    if "messages" not in st.session_state:
        welcome_message = Part(text="👋 Hello! I'm **StreamlitChat**. How can I help you today?")
        st.session_state.messages = [
            Content(role="model", parts=[welcome_message])
        ]

    # --- Display Chat Messages ---
    for message in st.session_state.messages:
        role = "user" if message.role == "user" else "assistant"
        with st.chat_message(role):
            if message.parts and message.parts[0].text:
                if role == "user":
                    st.markdown(f"🧑 {message.parts[0].text}")
                else:
                    st.markdown(f"🤖 {message.parts[0].text}")

    # --- Handle User Input ---
    if prompt := st.chat_input("Type your message here..."):
        user_message = Content(role="user", parts=[Part(text=prompt)])
        st.session_state.messages.append(user_message)

        with st.chat_message("user"):
            st.markdown(f"🧑 {prompt}")

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    response_stream = chat.send_message(prompt, stream=True)
                    full_response = ""
                    placeholder = st.empty()
                    for chunk in response_stream:
                        if chunk.text:
                            full_response += chunk.text
                            placeholder.markdown("🤖 " + full_response + "▌")
                    placeholder.markdown("🤖 " + full_response)

                    ai_response = Content(role="model", parts=[Part(text=full_response)])
                    st.session_state.messages.append(ai_response)

                except APIError as e:
                    st.error(f"⚠️ API Error: {e}")
                    st.session_state.messages.append(
                        Content(role="model", parts=[Part(text="⚠️ Sorry, I encountered an API error.")])
                    )
                except Exception as e:
                    st.error(f"⚠️ Unexpected error: {e}")
                    st.session_state.messages.append(
                        Content(role="model", parts=[Part(text="⚠️ Something went wrong while generating a response.")])
                    )

if __name__ == "__main__":
    main()
