# from huggingface_hub import snapshot_download

# snapshot_download(
#     repo_id="todorristov/car_classification_model",
#     local_dir=r"D:\Visual-Question-Answering\models\car_classification_model",
#     local_dir_use_symlinks=False
# )

# print("Download Complete ✅")


# import streamlit as st
# import torch
# from PIL import Image

# from transformers import (
#     AutoImageProcessor,
#     ConvNextForImageClassification,
# )

# # ===========================
# # Configuration
# # ===========================

# MODEL_PATH = r"D:\Visual-Question-Answering\models\car_classification_model"

# st.set_page_config(
#     page_title="Car Classification",
#     page_icon="🚗",
#     layout="centered"
# )

# # ===========================
# # Load Model
# # ===========================

# @st.cache_resource
# def load_model():

#     processor = AutoImageProcessor.from_pretrained(MODEL_PATH)

#     model = ConvNextForImageClassification.from_pretrained(MODEL_PATH)

#     model.eval()

#     return processor, model


# processor, model = load_model()

# # ===========================
# # UI
# # ===========================

# st.title("🚗 Car Classification")

# uploaded_file = st.file_uploader(
#     "Upload a car image",
#     type=["jpg", "jpeg", "png"]
# )

# if uploaded_file:

#     image = Image.open(uploaded_file).convert("RGB")

#     st.image(image, use_container_width=True)

#     inputs = processor(images=image, return_tensors="pt")

#     with torch.no_grad():
#         outputs = model(**inputs)

#     probs = torch.softmax(outputs.logits, dim=-1)

#     top5_probs, top5_ids = torch.topk(probs, k=5)

#     st.subheader("Top Predictions")

#     for score, idx in zip(top5_probs[0], top5_ids[0]):

#         label = model.config.id2label[idx.item()]

#         st.write(
#             f"**{label}**  —  {score.item()*100:.2f}%"
#         )

from datasets import load_dataset

dataset = load_dataset(
    "Paulescu/stanford_cars",
    cache_dir=r"D:\Visual-Question-Answering\datasets"
)


from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="todorristov/car_classification_model",
    local_dir=r"D:\Visual-Question-Answering\models\car_classification_model",
    local_dir_use_symlinks=False
)

print("Download Complete ✅")