# pages/1_Admin.py
import streamlit as st
import yaml
from pathlib import Path
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configurations.settings import settings

st.set_page_config(page_title="Admin Settings")
st.title("🛠️ Admin Configuration")

config_path = Path("configurations/models.yml")

# Show existing default settings
st.markdown("### Current Default Settings")
st.json(settings.defaults)

# Editable admin section
st.markdown("### ✏️ Update Default Parameters")

new_temperature = st.slider("Temperature", 0.0, 1.0, settings.defaults["temperature"], 0.05)
new_max_tokens = st.number_input("Max Tokens", 10, 4096, settings.defaults["max_tokens"], 10)
new_top_p = st.slider("Top-p", 0.0, 1.0, settings.defaults["top_p"], 0.05)
new_presence_penalty = st.slider("Presence Penalty", -2.0, 2.0, settings.defaults["presence_penalty"], 0.1)
new_frequency_penalty = st.slider("Frequency Penalty", -2.0, 2.0, settings.defaults["frequency_penalty"], 0.1)

if st.button("💾 Save Configuration"):
    try:
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        # Update default settings
        config_data["defaults"] = {
            "temperature": float(new_temperature),
            "max_tokens": int(new_max_tokens),
            "top_p": float(new_top_p),
            "presence_penalty": float(new_presence_penalty),
            "frequency_penalty": float(new_frequency_penalty)
        }

        with open(config_path, "w") as f:
            yaml.safe_dump(config_data, f)

        st.success("Configuration updated! Reload app to reflect changes.")
    except Exception as e:
        st.error(f"Failed to update: {e}")
