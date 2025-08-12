import sys

# --- Top bar with New Session (left) and Configure (right) ---
import streamlit as st
from streamlit import columns
import os
from dotenv import load_dotenv
from datetime import datetime

# Append project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import SessionManager
from app.database.db_history_manager import HistoryManager
from app.database.db_llm_model import LLM_MODEL_Manager
from app.database.user_configuration_manager import get_user_config

from app.modelList.openai_class import CLS_OpenAI_Client
from app.modelList.anthropic_class import CLS_Anthropic_Client
from app.modelList.llama_class import CLS_Groq_Client
from app.modelList.gemini_class import CLS_Gemini_Client

from configurations.settings import Settings


# Initialize SessionManager
session_manager = SessionManager()

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = session_manager.generate_session_id()

# Initialize HistoryManager
history_manager = HistoryManager()

# Load environment variables
load_dotenv()

# Streamlit Page Config
st.set_page_config(page_title="LLM Experimenter", layout="centered")
st.title("LLM Experimenter")

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gpt-3.5-turbo"



top_left, top_spacer, top_right = st.columns([2,6,2])
with top_left:
    if st.button("New_Session", key="new_session_btn"
                 ):
        st.session_state.session_id = session_manager.generate_session_id()
        st.session_state.chat_history = []
        st.session_state['show_config'] = False  # Hide config on new session
        st.success("Started a new session.")
with top_right:
    if 'show_config' not in st.session_state:
        st.session_state['show_config'] = False
    if st.button("Configure", key="show_config_btn"):
        st.session_state['show_config'] = not st.session_state['show_config']

# Sidebar: Login and Session History
with st.sidebar:
    st.subheader("Login")
    user_input = st.text_input("Enter your email or name", value=st.session_state.get("user", ""))
    if st.button("Login"):
        if user_input:
            st.session_state.user = user_input
            st.success(f"Logged in as {user_input}")
        else:
            st.warning("Please enter a name or email.")

    # Show session history only if user is logged in
    if st.session_state.get("user"):
        st.markdown("---")
        st.subheader("📜 Session History")
        saved_history = history_manager.get_history(st.session_state.session_id, limit=10)
        for item in saved_history:
            st.markdown(f"🕒 `{item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}` | **{item['model']}**")
            st.markdown(f"- **Prompt:** {item['prompt']}")
            st.markdown(f"- **Response:** {item['response']}")


# --- Show configuration in main area if toggled ---
if st.session_state.get('show_config', False) and st.session_state.get("user"):
    settings = Settings()
    user_defaults = get_user_config(st.session_state.user, fallback=settings.defaults)
    st.markdown("---")
    st.subheader("⚙️ Advanced Parameters")
    temperature = st.slider("Temperature", 0.0, 1.0, user_defaults["temperature"], step=0.05, key="sidebar_temperature")
    max_tokens = st.number_input("Max Tokens", 10, 4096, user_defaults["max_tokens"], step=10, key="sidebar_max_tokens")
    top_p = st.slider("Top-p", 0.0, 1.0, user_defaults["top_p"], step=0.05, key="sidebar_top_p")
    presence_penalty = st.slider("Presence Penalty", -2.0, 2.0, user_defaults["presence_penalty"], step=0.1, key="sidebar_presence_penalty")
    frequency_penalty = st.slider("Frequency Penalty", -2.0, 2.0, user_defaults["frequency_penalty"], step=0.1, key="sidebar_frequency_penalty")

# App Body (show only if config is not shown)
if st.session_state.user and not st.session_state.get('show_config', False):
    # Use sidebar values for parameters
    temperature = st.session_state.get("sidebar_temperature", 0.7)
    max_tokens = st.session_state.get("sidebar_max_tokens", 512)
    top_p = st.session_state.get("sidebar_top_p", 1.0)
    presence_penalty = st.session_state.get("sidebar_presence_penalty", 0.0)
    frequency_penalty = st.session_state.get("sidebar_frequency_penalty", 0.0)

    flattened_options = []
    # Load model configurations
    llm_model_manager = LLM_MODEL_Manager()
    available_models = llm_model_manager.get_models()

    if available_models:
        for model in available_models:
            flattened_options.append(f"{model['company']}: {model['model']}")
    else:
        model_config = settings.model_config
        for provider, model_list in model_config.items():
            for model in model_list:
                flattened_options.append(f"{provider}: {model}")

    selected_flat = st.selectbox("Select Model:", flattened_options, key="flat")
    if selected_flat:
        provider_name = selected_flat.split(": ")[0]
        model_name = selected_flat.split(": ")[1]
        st.write(f"Provider: {provider_name}, Model: {model_name}")

    st.divider()

    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    # Prompt input
    prompt = st.chat_input("Ask something...")

    if prompt:
        # Display user message
        st.chat_message("user").markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Call OpenAI API
        try:
            with st.spinner("Thinking..."):
                print(f"Selected Model: {model_name}")
                print(f"Provider: {provider_name}")

                if provider_name == "openai":
                    openai_client = CLS_OpenAI_Client()
                    answer = openai_client.generate_text_response(
                        selected_model=model_name,
                        chat_history=st.session_state.chat_history,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        presence_penalty=presence_penalty,
                        frequency_penalty=frequency_penalty)
                    print(f"Response from OpenAI: {answer}")
                elif provider_name == "anthropic":
                    anthropic_client = CLS_Anthropic_Client()
                    answer = anthropic_client.generate_text_response(
                        selected_model=model_name,
                        chat_history=st.session_state.chat_history,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    print(f"Response from Anthropic: {answer}")
                elif provider_name == "llama":
                    llama_client = CLS_Groq_Client()
                    answer = llama_client.generate_text_response(
                        selected_model=model_name,
                        chat_history=st.session_state.chat_history,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        frequency_penalty=frequency_penalty
                    )
                    print(f"Response from Llama: {answer}")
                elif provider_name == "google":
                    google_client = CLS_Gemini_Client()
                    answer = google_client.generate_text_response(
                        selected_model=model_name,
                        chat_history=st.session_state.chat_history,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    print(f"Response from Llama: {answer}")

            # Display assistant response
            st.chat_message("assistant").markdown(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

            # Save interaction to MongoDB
            history_manager.save_history(
                user=st.session_state.user,
                session_id=st.session_state.session_id,
                model=model_name,
                prompt=prompt,
                response=answer
            )

        except Exception as e:
            st.error(f"Error: {e}")
elif not st.session_state.get('show_config', False):
    st.info("Please login using the sidebar to start chatting.")