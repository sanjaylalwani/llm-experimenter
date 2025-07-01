import streamlit as st
import os
from dotenv import load_dotenv
from history_manager import HistoryManager
from datetime import datetime
from openai import OpenAI
from utils import SessionManager


# Initialize SessionManager
session_manager = SessionManager()

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = session_manager.generate_session_id()

# Initialize HistoryManager
history_manager = HistoryManager()

# Load environment variables
load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Streamlit Page Config
st.set_page_config(page_title="LLM Experimenter", layout="centered")
st.title("🤖 LLM Experimenter – OpenAI Chat")

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gpt-3.5-turbo"

# Sidebar Login
with st.sidebar:
    st.subheader("Login")
    user_input = st.text_input("Enter your email or name", value=st.session_state.get("user", ""))
    if st.button("Login"):
        if user_input:
            st.session_state.user = user_input
            st.success(f"Logged in as {user_input}")
        else:
            st.warning("Please enter a name or email.")

# App Body
if st.session_state.user:

    # Model selection
    st.selectbox("Select OpenAI model:",
                 options=["gpt-3.5-turbo", "gpt-4o"],
                 key="selected_model")

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
                response = client.chat.completions.create(
                    model=st.session_state.selected_model,
                    messages=st.session_state.chat_history,
                    temperature=0.7
                )
                answer = response.choices[0].message.content

            # Display assistant response
            st.chat_message("assistant").markdown(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

            # Save interaction to MongoDB
            history_manager.save_history(
                user=st.session_state.user,
                session_id = st.session_state.session_id,
                model=st.session_state.selected_model,
                prompt=prompt,
                response=answer
            )

        except Exception as e:
            st.error(f"Error: {e}")

    # Show past saved interactions
    with st.expander("📜 View Previous 5 Interactions"):
        saved_history = history_manager.get_history(st.session_state.user, limit=5)
        for item in saved_history:
            st.markdown(f"🕒 `{item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}` | **{item['model']}**")
            st.markdown(f"- **Prompt:** {item['prompt']}")
            st.markdown(f"- **Response:** {item['response']}")
            st.markdown("---")

else:
    st.info("Please login using the sidebar to start chatting.")