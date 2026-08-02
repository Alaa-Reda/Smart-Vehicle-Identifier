from huggingface_hub import InferenceClient
import os

client = InferenceClient(
    api_key=os.getenv("HF_TOKEN")
)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-7B-Instruct",
    messages=[
        {
            "role": "user",
            "content": "Hello"
        }
    ],
)

print(response.choices[0].message.content)