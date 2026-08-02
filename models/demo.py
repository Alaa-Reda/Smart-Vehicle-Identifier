import streamlit as st
from PIL import Image
 
from pathlib import Path
import sys
 
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
 
from models.qwen.online_inference import QwenOnlineInference
from models.qwen.config import PROVIDER, MODEL_NAME
 
print("Provider:", PROVIDER)
print("Model:", MODEL_NAME)
 
st.set_page_config(
    page_title="Qwen3-VL SDK Demo",
    page_icon="🚗",
    layout="wide",
)
 
st.title("🚗 Qwen3-VL SDK Demo")
 
sdk = QwenOnlineInference()
 
# -----------------------------
# Sidebar
# -----------------------------
 
st.sidebar.header("Settings")
 
temperature = st.sidebar.slider(
    "Temperature",
    0.0,
    2.0,
    sdk.temperature,
)
 
max_tokens = st.sidebar.slider(
    "Max Tokens",
    128,
    4096,
    sdk.max_tokens,
)
 
sdk.update_config(
    temperature=temperature,
    max_tokens=max_tokens,
)
 
# -----------------------------
# Upload Image
# -----------------------------
 
uploaded_image = st.file_uploader(
    "Upload Image",
    type=["jpg", "jpeg", "png"],
)
 
image = None
 
if uploaded_image:
 
    image = Image.open(uploaded_image)
 
    st.image(
    image,
    width="stretch",
    )
# -----------------------------
# Prompt
# -----------------------------
 
prompt = st.text_area(
    "Prompt",
    value="Identify this vehicle.",
    height=120,
)
 
# -----------------------------
# Chat
# -----------------------------
 
col1, col2 = st.columns(2)
 
with col1:
 
    if st.button("Send"):
 
        if not prompt.strip():
 
            st.warning("Enter a prompt.")
 
        else:
 
            with st.spinner("Generating..."):
 
                response = sdk.chat(
                    prompt=prompt,
                    image=image,
                )
 
            st.success("Done")
 
            st.markdown(response)
 
with col2:
 
    if st.button("Reset Conversation"):
 
        sdk.reset()
 
        st.success("Conversation Reset")
 
# -----------------------------
# Model Info
# -----------------------------
 
with st.expander("Model Info"):
 
    st.json(
        sdk.get_model_info()
    )
 
# -----------------------------
# Usage
# -----------------------------
 
with st.expander("Usage"):
 
    st.json(
        sdk.get_usage()
    )
 
# -----------------------------
# History
# -----------------------------
 
with st.expander("Conversation"):
 
    st.json(
        sdk.conversation.get_messages()
    )
 
# streamlit run models/demo.py
 