
# Car Classification Model

## Overview

The Car Classification Model is the primary computer vision model used by the Smart Vehicle Identifier system.

Its responsibility is to analyze an input vehicle image and identify the most likely vehicle class. The classification result serves as the foundation for the remaining AI pipeline, enabling vehicle analysis, information retrieval, and intelligent question answering.

This model is integrated into the backend through the centralized model loader and operates as the first stage of the vehicle analysis workflow.

---

# Architecture Position

```
Vehicle Image

↓

Image Preprocessing

↓

Car Classification Model

↓

Vehicle Prediction

↓

Vehicle Service

↓

RAG Pipeline

↓

Final Response
```

---

# Responsibilities

The Car Classification Model is responsible for:

- Analyzing vehicle images.
- Identifying vehicle classes.
- Returning prediction confidence.
- Supporting downstream AI services.

The model is NOT responsible for:

- Vehicle comparison.
- Question answering.
- Prompt generation.
- Database operations.
- Business logic.

---

# Model Files

```
car_classification_model/
│
├── config.json
├── model.safetensors
├── preprocessor_config.json
│
├── images/
│   └── convnext_architecture.png
│
├── reports/
│   └── figures/
│       └── Training_Validation-Loss_Accuracy.png
│
└── README.md
```

---

# Model Components

## model.safetensors

Contains the trained model weights used during inference.

---

## config.json

Stores the model architecture configuration and inference settings.

---

## preprocessor_config.json

Defines the preprocessing pipeline required before inference, including image size, normalization parameters, and preprocessing configuration.

---

## images/

Contains documentation images related to the model architecture.

Example:

- ConvNeXt Architecture

---

## reports/

Contains training visualizations and evaluation figures that document the model's development process.

These files are provided for documentation purposes and are not required during inference.

---

# Input

The model receives:

- RGB vehicle image

Supported image formats include:

- JPG
- JPEG
- PNG

---

# Output

The model returns:

- Predicted Vehicle Class
- Prediction Confidence Score

The prediction is forwarded to the backend for additional processing.

---

# Integration

The model is loaded through the centralized model loader.

```
Backend

↓

loaders.py

↓

Car Classification Model

↓

Inference

↓

Prediction
```

---

# Dependencies

The model is used by:

- Vehicle Service
- Image Analysis Pipeline
- RAG System

Required libraries include:

- PyTorch
- Transformers
- Pillow

---

# Workflow

```
Upload Image

↓

Image Preprocessing

↓

Model Inference

↓

Vehicle Prediction

↓

Backend Processing

↓

Response Generation
```

---

# Development Rules

The model directory should contain only files required for inference and documentation.

Avoid storing:

- Temporary files
- Cache directories
- Training datasets
- Development scripts
- Experimental checkpoints

---

# Future Improvements

Possible future enhancements include:

- Improved vehicle recognition accuracy.
- Support for newer vehicle models.
- Faster inference.
- Quantized model versions.
- Expanded vehicle coverage.

---

# Notes

This directory contains the production-ready classification model used by the Smart Vehicle Identifier system.

Model loading, preprocessing, and inference are handled externally through the backend model loader, ensuring a clean separation between model assets and application logic.
