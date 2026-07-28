
# Qwen Vision-Language Model

## Overview

The Qwen Vision-Language Model is responsible for visual understanding and intelligent reasoning within the Smart Vehicle Identifier system.

It receives the detected vehicle information together with user questions and generates detailed, context-aware responses.

---

# Deployment Strategy

During the early development phase, the project team evaluated running the model locally.

However, due to hardware limitations and the computational requirements of large Vision-Language Models, local deployment was not practical for the development environment.

To ensure stable performance and faster development, the production system uses the online hosted version of the model through the Hugging Face Inference API.

For users with sufficient hardware resources, the project also provides optional scripts for running the model locally.

---

# Folder Structure

```
qwen/
│
├── README.md
├── install_qwen_model.py
├── local_inference.py
└── online_inference.py
```

---

# Files

## install_qwen_model.py

Downloads the required Qwen model files for local deployment.

This script is optional and is only needed when running the model locally.

---

## local_inference.py

Loads the locally downloaded Qwen model and performs inference without requiring an internet connection.

Recommended only for systems with sufficient GPU memory.

---

## online_inference.py

Connects to the hosted Qwen model through the Hugging Face Inference API.

This is the default inference method used by the Smart Vehicle Identifier system.

---

# Current Configuration

Default Mode:

```
Online Inference
```

Optional Mode:

```
Local Inference
```

---

# Development Notes

The online deployment was selected to:

- Reduce hardware requirements.
- Improve development flexibility.
- Simplify project setup.
- Provide a consistent execution environment.

Developers may switch to local inference by downloading the model and replacing the inference implementation.

---

# Future Improvements

- Automatic mode selection.
- GPU capability detection.
- Local model caching.
- Multi-provider support.
