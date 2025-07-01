import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from history_manager import HistoryManager
from datetime import datetime

# Load environment variables
load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPENAI_API_KEY"),
)
# Initialize HistoryManager
history_manager = HistoryManager()

# Streamlit page config
st.set_page_config(page_title="LLM Experimenter", layout="centered")

# Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = None

st.title("🤖 LLM Experimenter – OpenAI Playground")

# --- Login Section ---
with st.sidebar:
    st.subheader("Login")
    user_input = st.text_input("Enter your email or name", value=st.session_state.get("user", ""))
    if st.button("Login"):
        if user_input:
            st.session_state.user = user_input
            st.success(f"Logged in as {user_input}")
        else:
            st.warning("Please enter a name or email.")

# Only proceed if logged in
if st.session_state.user:
    # --- Model Selection ---
    st.markdown("### 🔍 Choose OpenAI Model")
    model_options = ["gpt-3.5-turbo", "gpt-4o"]
    selected_model = st.selectbox("Select OpenAI model:", model_options)

    # --- Prompt Input ---
    prompt = st.text_area("Enter your prompt", height=150)
    if st.button("Run Model"):
        if not prompt.strip():
            st.warning("Prompt cannot be empty.")
        else:
            try:
                with st.spinner("Thinking..."):
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7
                    )
                    answer = response.choices[0].message["content"]
                    st.success("Response received:")
                    st.write(answer)

                    # Save to MongoDB history
                    history_manager.save_history(
                        user=st.session_state.user,
                        session_id=st.session_state.session_id,
                        model=selected_model,
                        prompt=prompt,
                        response=answer
                    )

            except Exception as e:
                st.error(f"Error: {e}")

    # --- Show History ---
    st.markdown("### 📜 Recent History")
    history = history_manager.get_history(st.session_state.user, limit=5)
    for item in history:
        with st.expander(f"🕒 {item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} | {item['model']}"):
            st.markdown(f"**Prompt:** {item['prompt']}")
            st.markdown(f"**Response:** {item['response']}")

else:
    st.info("Please login using the sidebar to start experimenting.")










# # main.py
# from history_manager import HistoryManager

# # Initialize manager
# history_mgr = HistoryManager()

# # Save a history record
# history_mgr.save_history(
#     user="sanjay",
#     session_id="abc123",
#     model="gpt-4",
#     prompt="What is LLM?",
#     response="A large language model..."
# )

# # Retrieve last 5 prompts
# recent_history = history_mgr.get_history("sanjay", limit=5)
# for record in recent_history:
#     print(record)

# # Close DB connection when done
# history_mgr.close_connection()

