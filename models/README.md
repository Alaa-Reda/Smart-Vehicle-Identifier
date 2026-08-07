# Models Module

---

# Overview

The **Models** module is the Artificial Intelligence core of the Smart Vehicle Identifier project.

It is responsible for identifying vehicles, analyzing vehicle images, answering user questions, and generating intelligent responses through a hybrid AI architecture.

Instead of relying on a single AI model, the system combines two specialized models, where each model performs the task it is designed for.

This architecture improves prediction accuracy, reduces inference cost, and increases system reliability.

---

# Objectives

The Models module is responsible for:

- Vehicle classification.
- Vehicle recognition.
- Image understanding.
- Vehicle analysis.
- Visual reasoning.
- Conversational AI.
- Confidence estimation.
- Structured response generation.

---

# AI Models

The project currently contains two independent AI models.

## 1. Local Vehicle Classification Model

Purpose

Identify the vehicle make, model, and production year from an uploaded image.

Technology

```
ConvNext Image Classification
```

Execution

```
Runs locally on the server.
```

Responsibilities

- Predict vehicle make.
- Predict vehicle model.
- Predict production year.
- Return Top-K predictions.
- Return confidence score.

Advantages

- Very fast inference.
- No Internet connection required.
- Specialized for vehicle recognition.
- Low operational cost.

Limitations

- Can recognize only vehicles included in the training dataset.
- Does not answer user questions.
- Does not provide detailed vehicle specifications.
- Does not perform reasoning.

---

## 2. Groq Vision Language Model

Purpose

Understand vehicle images and answer user questions using multimodal reasoning.

Technology

```
Groq API

Model:
Qwen/Qwen3.6-27B
```

Execution

```
Cloud Inference
```

Responsibilities

- Analyze uploaded images.
- Understand user questions.
- Explain vehicle specifications.
- Generate natural language responses.
- Perform multimodal reasoning.

Advantages

- Advanced reasoning.
- Image understanding.
- Natural language interaction.
- Flexible response generation.

Limitations

- Requires Internet connection.
- Higher inference cost.
- Slower than the local classification model.

---

# Hybrid AI Workflow

The Smart Vehicle Identifier system combines multiple AI components into a single intelligent pipeline.

```text
                User Uploads Vehicle Image
                          │
                          ▼
        Local Vehicle Classification Model
                          │
                          ▼
        Predict Vehicle Make / Model / Year
                          │
                          ▼
              Confidence Evaluation
                          │
              ┌───────────┴───────────┐
              │                       │
        High Confidence         Low Confidence
              │                       │
              │                       ▼
              │             Groq Vision Model
              │              (Image Analysis)
              │                       │
              └───────────────┬───────┘
                              │
                              ▼
             Vehicle Name / Visual Understanding
                              │
                              ▼
          Groq Searches Internal Knowledge
                              │
                     Vehicle Information Found?
                  ┌───────────┴───────────┐
                  │                       │
                YES                      NO
                  │                       │
                  │                       ▼
                  │              Google Lens Search
                  │                       │
                  │                       ▼
                  │                Web Scraping
                  │                       │
                  │                       ▼
                  │            Extract Vehicle Data
                  │                       │
                  └───────────────┬───────┘
                                  │
                                  ▼
                        RAG + Memory System
                                  │
                                  ▼
                      Prompt Construction
                                  │
                                  ▼
                        Groq Generates Answer
                                  │
                                  ▼
                           Backend Response
                                  │
                                  ▼
                               Frontend
```

---

# AI Pipeline Explanation

The Smart Vehicle Identifier system follows a hybrid AI architecture.

### Step 1 — Vehicle Classification

The uploaded image is processed by the local ConvNext classification model.

The model predicts:

- Vehicle Make
- Vehicle Model
- Production Year
- Confidence Score

The classification model is optimized only for vehicle recognition and does not contain detailed information about vehicle specifications.

---

### Step 2 — Vehicle Understanding

If the prediction confidence is high, the predicted vehicle name is passed to the Groq Vision Model.

If the confidence is low, the uploaded image is analyzed directly by the Groq Vision Model to improve identification accuracy.

---

### Step 3 — Internal Knowledge

The Groq Vision Model attempts to answer the user's question using its internal knowledge.

If enough information is available, response generation continues normally.

Otherwise, the external knowledge pipeline is activated.

---

### Step 4 — External Knowledge

The system performs:

- Google Lens search.
- Web Scraping from trusted automotive websites.

The collected information is cleaned, normalized, and converted into structured data.

---

### Step 5 — Retrieval-Augmented Generation (RAG)

The retrieved vehicle information is sent to the RAG module.

The RAG system is responsible for:

- Retrieving relevant information.
- Selecting useful context.
- Combining retrieved data with conversation memory.
- Building the final prompt.

---

### Step 6 — Final Response

The final prompt is sent to the Groq Vision Model.

The generated response combines:

- Vehicle classification result.
- Internal model knowledge.
- Web Scraping information.
- Google Lens results.
- RAG context.
- Conversation memory.

The final response is returned to the Backend and displayed in the Frontend.

---

# Folder Structure

```text
models/
│
├── demo.py
│
├── car_classification_model/
│   │
│   ├── car.py
│   ├── README.md
│   │
│   └── car_model/
│       ├── model.safetensors
│       ├── config.json
│       ├── preprocessor_config.json
│       ├── images/
│       └── reports/
│
└── qwen/
    ├── online_inference.py
    ├── config.py
    ├── prompts.py
    ├── conversation.py
    ├── ConversationManager.py
    ├── image_utils.py
    ├── logger.py
    ├── exceptions.py
    ├── schemas.py
    ├── __init__.py
    └── examples/
```

---

# Main Components

| Component                           | Responsibility                                                                                                                                                                       |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| demo.py                             | Streamlit demonstration application used to test the Groq Vision SDK. It is currently connected only to the Vision model and serves as a testing interface.                          |
| car_classification_model/           | Contains the complete local vehicle classification module.                                                                                                                           |
| car_classification_model/car.py     | Main interface for loading the ConvNext model and performing vehicle prediction. This is the file imported by the Backend.                                                           |
| car_classification_model/car_model/ | Stores the trained ConvNext model, including weights, configuration files, preprocessing configuration, architecture diagrams, and training reports.                                 |
| qwen/                               | Contains the complete Vision Language SDK responsible for communicating with the Groq API, processing images, managing conversations, handling prompts, and generating AI responses. |

---

# Overall Execution Flow

```text
Frontend

↓

Backend

↓

Vehicle Classification Model

↓

Groq Vision Model

↓

Google Lens (If Needed)

↓

Web Scraping (If Needed)

↓

RAG + Memory

↓

Groq Response Generation

↓

Backend Response

↓

Frontend
```

---

# Design Principles

The Models module follows a modular architecture.

Each AI model is isolated inside its own directory, allowing independent development, testing, maintenance, and future replacement without affecting the rest of the project.

The Backend controls the execution flow and decides when each model should be used.

---

# Notes

- The local vehicle classification model is always executed first.
- The Groq Vision model is responsible for reasoning and response generation.
- Web Scraping and Google Lens are executed only when additional information is required.
- The current `demo.py` is a testing interface for the Groq Vision SDK and is not yet connected to the local classification model.
- The production Backend will integrate both models into a single intelligent inference pipeline.



# demo.py

**Location**

```text
models/demo.py
```

## Purpose

A Streamlit demonstration application used for testing the Groq Vision SDK during development.

## Responsibilities

- Upload an image.
- Enter a prompt.
- Send requests to the Groq Vision SDK.
- Display the generated response.
- Show model configuration and usage statistics.
- Manage conversation history.

## Notes

- This file is intended only for development and testing.
- It is not part of the production Backend.
- It currently communicates only with the Groq Vision SDK.
- The local vehicle classification model is not integrated into this demo.



# car.py

**File Location**

```text
models/
└── car_classification_model/
    └── car.py
```

---

# Purpose

`car.py` is the main interface for the local vehicle classification model.

It loads the trained ConvNext model, preprocesses vehicle images, performs inference, and returns the predicted vehicle make, model, year, and confidence score.

This file is the only interface that the Backend should communicate with when using the local classification model.

---

# Role in the Project

The Backend never communicates directly with the ConvNext model files.

Instead, it imports the `CarClassifier` class from this file.

```
Backend

↓

CarClassifier

↓

ConvNext Model

↓

Prediction
```

---

# Responsibilities

- Load the trained ConvNext model.
- Load the image processor.
- Detect the available device (CPU/GPU).
- Prepare input images.
- Run inference.
- Calculate confidence scores.
- Return Top-K predictions.
- Convert predictions into dictionaries for APIs.

---

# Imports

## PyTorch

```python
import torch
```

Purpose

- Tensor operations.
- Device detection.
- Model inference.

---

## Transformers

```python
from transformers import (
    AutoImageProcessor,
    ConvNextForImageClassification,
)
```

Purpose

Loads:

- Image Processor
- ConvNext Classification Model

---

## PIL

```python
from PIL import Image
```

Purpose

Open and process images before inference.

---

## Path

```python
from pathlib import Path
```

Purpose

Manage the local model directory.

---

# Classes

This file contains two main classes.

```
CarPrediction

↓

CarClassifier
```

---

# CarPrediction

Purpose

Represents one prediction returned by the classification model.

Example

```
2010 Ford Mustang Coupe
```

Automatically extracts

```
Year

Make

Model
```

Stored Information

```
Rank

Label

Confidence

Year

Make

Model
```

---

## Methods

### confidence_pct

Returns

```
Confidence Percentage
```

Example

```
98.52%
```

---

### to_dict()

Converts prediction into JSON-friendly format.

Example Output

```json
{
    "rank": 1,
    "label": "2010 Ford Mustang Coupe",
    "score": 0.985214,
    "confidence": 98.52,
    "year": "2010",
    "make": "Ford",
    "model": "Mustang Coupe"
}
```

---

# CarClassifier

Purpose

Main interface used by the Backend to interact with the ConvNext classification model.

The Backend should instantiate this class once and reuse it for all predictions.

---

# Constructor

```python
CarClassifier(
    model_path=None,
    device=None,
    top_k=5,
)
```

Parameters

| Parameter  | Description                         |
| ---------- | ----------------------------------- |
| model_path | Path to the trained model directory |
| device     | CPU or CUDA                         |
| top_k      | Number of predictions returned      |

---

# Internal Variables

| Variable        | Purpose                       |
| --------------- | ----------------------------- |
| self.model_path | Location of the trained model |
| self.device     | Selected execution device     |
| self.top_k      | Default number of predictions |
| self._processor | HuggingFace Image Processor   |
| self._model     | Loaded ConvNext model         |

---

# Private Methods

## _load()

Purpose

Loads the complete AI model into memory.

Responsibilities

- Verify model folder exists.
- Load Image Processor.
- Load ConvNext weights.
- Move model to CPU/GPU.
- Set evaluation mode.

Called automatically during initialization.

---

## _prepare_image()

Purpose

Normalize any supported image input.

Accepted Inputs

```
Image Path

PIL Image
```

Returns

```
RGB PIL Image
```

This ensures every image has the correct format before inference.

---

# Public Methods

## predict()

```python
predict(image)
```

Purpose

Main inference function.

Input

```
Image Path

or

PIL Image
```

Output

```
List[CarPrediction]
```

Workflow

```
Image

↓

Preprocess

↓

ConvNext

↓

Softmax

↓

Top-K Predictions

↓

CarPrediction Objects
```

---

## predict_top1()

Returns

```
Only the highest confidence prediction.
```

Useful when only one vehicle prediction is required.

---

## predict_dict()

Purpose

Converts predictions into dictionaries.

Ideal for

- Backend APIs
- JSON Responses
- Database Storage

---

# Properties

## num_classes

Returns

```
Total number of vehicle classes.
```

---

## labels

Returns

```
List of all supported vehicle labels.
```

---

# Utility Methods

## get_info()

Returns

```python
{
    "model_path": "...",
    "num_classes": ...,
    "device": "...",
    "top_k": ...
}
```

Useful for debugging and monitoring.

---

# Default Configuration

Default Model Path

```python
DEFAULT_MODEL_PATH
```

Points to

```
car_classification_model/

└── car_model/
```

The following files are loaded automatically

```
model.safetensors

config.json

preprocessor_config.json
```

---

# Backend Usage

Import

```python
from models.car_classification_model.car import CarClassifier
```

Initialize

```python
classifier = CarClassifier()
```

Prediction

```python
results = classifier.predict(image)
```

Best Prediction

```python
best = classifier.predict_top1(image)
```

API Output

```python
response = classifier.predict_dict(image)
```

---

# Interaction with Other Modules

```
Backend

↓

CarClassifier

↓

ConvNext Model

↓

Prediction

↓

Groq Vision Model

↓

Web Scraping (if needed)

↓

RAG

↓

Final Response
```

---

# Error Handling

The classifier automatically validates:

- Missing model directory.
- Unsupported image type.
- Invalid image format.
- Device selection.
- Model loading errors.

---

# Summary

`car.py` is the entry point of the local vehicle classification system.

It encapsulates the complete ConvNext inference pipeline and provides a clean API that allows the Backend to classify vehicle images without interacting directly with the model files or preprocessing logic.


# config.py

**File Location**

```text
models/
└── qwen/
    └── config.py
```

---

# Purpose

`config.py` is the central configuration file for the Groq Vision SDK.

It loads all runtime settings from environment variables and provides a single source of configuration for every module inside the SDK.

Instead of hardcoding values inside the code, every module imports its settings from this file.

---

# Responsibilities

- Load environment variables.
- Configure the Groq API.
- Configure the Vision model.
- Configure generation parameters.
- Configure network settings.
- Provide shared configuration across the SDK.

---

# Imported Libraries

## os

```python
import os
```

Purpose

Read environment variables.

---

## dotenv

```python
from dotenv import load_dotenv
```

Purpose

Load values from the `.env` file.

---

# Environment Loading

```python
load_dotenv()
```

Purpose

Load all environment variables before any configuration is used.

Without this line, the SDK cannot read the API key or model configuration.

---

# Configuration Sections

---

## Groq API

### GROQ_API_KEY

```python
GROQ_API_KEY
```

Purpose

Stores the API key used to authenticate requests with the Groq API.

Loaded from

```
.env
```

Example

```env
GROQ_API_KEY=xxxxxxxxxxxxxxxx
```

Used By

```
online_inference.py
```

---

## MODEL_NAME

```python
MODEL_NAME
```

Default

```text
qwen/qwen3.6-27b
```

Purpose

Specifies which Groq Vision model should be used.

Changing this value allows switching to another supported model without modifying the SDK.

Used By

```
online_inference.py
```

---

# Generation Configuration

These settings control how the model generates responses.

---

## MAX_TOKENS

```python
MAX_TOKENS
```

Purpose

Maximum number of tokens that the model may generate.

Higher values

- Longer responses
- More API usage
- Slightly slower inference

Default

```
1024
```

---

## TEMPERATURE

```python
TEMPERATURE
```

Purpose

Controls response randomness.

Typical Values

```
0.2 → More deterministic

0.7 → Balanced

1.0 → More creative
```

Default

```
0.7
```

---

## TOP_P

```python
TOP_P
```

Purpose

Controls nucleus sampling.

Lower values

More focused responses.

Higher values

More diverse responses.

Default

```
0.9
```

---

## STREAM

```python
STREAM
```

Purpose

Enable or disable streaming responses.

Values

```
True

False
```

Current Default

```
False
```

Used By

```
stream_chat()
```

inside

```
online_inference.py
```

---

# Network Configuration

---

## TIMEOUT

```python
TIMEOUT
```

Purpose

Maximum request timeout.

Unit

```
Seconds
```

Default

```
120
```

Used By

```
Groq Client
```

---

## RETRIES

```python
RETRIES
```

Purpose

Number of retry attempts when a request fails.

Default

```
3
```

Used By

```
chat()

chat_json()

stream_chat()
```

---

# Provider

```python
PROVIDER
```

Current Value

```
groq
```

Purpose

Defines the inference provider.

Unlike previous versions that supported Hugging Face, this SDK is permanently configured to use Groq.

---

# Configuration Flow

```
.env

↓

load_dotenv()

↓

config.py

↓

online_inference.py

↓

Groq Client

↓

Inference Request
```

---

# Files Depending on config.py

```
online_inference.py

↓

Groq Client

↓

chat()

↓

stream_chat()

↓

chat_json()
```

---

# Backend Usage

The Backend never edits configuration directly.

Instead, every module imports the required settings.

Example

```python
from models.qwen.config import (
    MODEL_NAME,
    MAX_TOKENS,
    TEMPERATURE,
)
```

This ensures that all SDK components use the same configuration.

---

# Available Settings

| Variable     | Description                |
| ------------ | -------------------------- |
| GROQ_API_KEY | Groq authentication key    |
| MODEL_NAME   | Vision model name          |
| MAX_TOKENS   | Maximum generated tokens   |
| TEMPERATURE  | Response creativity        |
| TOP_P        | Nucleus sampling value     |
| STREAM       | Enable streaming           |
| TIMEOUT      | Request timeout            |
| RETRIES      | Retry attempts             |
| PROVIDER     | Current inference provider |

---

# Summary

`config.py` is the global configuration manager for the Groq Vision SDK.

Every runtime parameter, API credential, generation option, and network setting is centralized in this file, allowing the rest of the SDK to remain modular and easy to maintain.


# online_inference.py

**File Location**

```text
models/
└── qwen/
    └── online_inference.py
```

---

# Purpose

`online_inference.py` is the core inference engine of the Groq Vision SDK.

It manages the complete communication between the Backend and the Groq API.

This file is responsible for:

- Creating the Groq client.
- Preparing prompts.
- Preparing images.
- Managing conversations.
- Sending requests.
- Receiving responses.
- Returning structured outputs.
- Handling retries and exceptions.

Every request sent to the Vision model passes through this file.

---

# Architecture

```
Backend

↓

QwenOnlineInference

↓

Build Messages

↓

Prepare Image

↓

Groq Client

↓

Groq API

↓

Response

↓

Conversation Memory

↓

Backend
```

---

# Main Classes

This file contains two main classes.

```
_GroqClientSingleton

↓

QwenOnlineInference
```

---

# _GroqClientSingleton

Purpose

Creates a single Groq client shared across the application.

Using a Singleton prevents creating multiple API clients and reduces unnecessary overhead.

---

## Main Methods

### get_client()

Returns

```
Groq Client
```

Responsibilities

- Read API key.
- Validate authentication.
- Create Groq client.
- Configure timeout.
- Return existing client if already created.

---

### reset()

Purpose

Destroy the current client instance.

Useful during testing or reinitialization.

---

# QwenOnlineInference

Purpose

Main SDK class responsible for interacting with the Groq Vision model.

This class is imported directly by the Backend.

Example

```python
from models.qwen.online_inference import QwenOnlineInference

sdk = QwenOnlineInference()
```

---

# Constructor

```python
QwenOnlineInference(...)
```

Loads automatically

- Groq Client
- Model Configuration
- Generation Parameters
- Conversation Manager

Creates

```
self.client

self.conversation

self.last_response

self.last_usage
```

---

# Internal Variables

| Variable      | Purpose                 |
| ------------- | ----------------------- |
| client        | Groq client             |
| model_name    | Current AI model        |
| system_prompt | Default system prompt   |
| max_tokens    | Maximum response length |
| temperature   | Creativity level        |
| top_p         | Sampling parameter      |
| stream        | Enable streaming        |
| timeout       | API timeout             |
| retries       | Retry attempts          |
| conversation  | Conversation manager    |
| last_response | Last generated response |
| last_usage    | Token usage statistics  |

---

# Private Methods

## _build_messages()

Purpose

Creates the request payload sent to Groq.

Responsibilities

- Add System Prompt.
- Add conversation history.
- Add user prompt.
- Attach uploaded image.
- Return OpenAI-compatible messages.

Workflow

```
Prompt

+

Image

+

Conversation History

↓

OpenAI Message Format

↓

Groq API
```

---

# Public Methods

## chat()

```python
chat(
    prompt,
    image=None,
    history=None
)
```

Purpose

Main inference function.

Responsibilities

- Build request.
- Send request.
- Retry on failure.
- Save conversation.
- Save token usage.
- Return response.

Used By

```
Backend

Demo

Future RAG Pipeline
```

---

## chat_json()

Purpose

Generate structured JSON responses.

Useful when the Backend expects JSON instead of plain text.

Workflow

```
Prompt

↓

Append JSON Schema

↓

Groq

↓

Validate JSON

↓

Python Dictionary
```

---

## stream_chat()

Purpose

Receive streaming responses token by token.

Useful for real-time chat interfaces.

---

## health_check()

Purpose

Verify that the Groq API is available.

Returns

```
True

or

False
```

Useful for monitoring and diagnostics.

---

## save_history()

Purpose

Save the conversation history to a JSON file.

---

## load_history()

Purpose

Restore a previously saved conversation.

---

## get_model_info()

Returns

Current SDK configuration.

Example

```python
{
    "provider": "groq",
    "model": "...",
    "temperature": ...,
    "max_tokens": ...
}
```

---

## get_usage()

Returns

Current token usage.

Example

```python
{
    "prompt_tokens": ...,
    "completion_tokens": ...,
    "total_tokens": ...
}
```

---

## reset_usage()

Purpose

Clear token statistics.

---

## reset()

Purpose

Reset the current session.

Clears

- Conversation
- Last response
- Token usage

---

## export_config()

Returns

Current runtime configuration as a dictionary.

Useful for debugging.

---

## update_config()

Purpose

Modify SDK configuration during runtime.

Examples

```python
sdk.update_config(
    temperature=0.5,
    max_tokens=2048,
)
```

---

## close()

Purpose

Close the current session.

Clears memory and conversation history.

---

# Conversation Flow

```
User Prompt

↓

_build_messages()

↓

Groq API

↓

Response

↓

ConversationManager

↓

History Saved

↓

Return Response
```

---

# Image Processing

Image preparation is delegated to

```python
ImageProcessor.prepare_image()
```

Supported Inputs

- Local image path
- PIL Image
- Base64 image
- Image URL

---

# Dependencies

This file depends on

```
config.py

prompts.py

conversation.py

image_utils.py

exceptions.py

logger.py

schemas.py
```

---

# Backend Usage

Import

```python
from models.qwen.online_inference import QwenOnlineInference
```

Initialize

```python
sdk = QwenOnlineInference()
```

Text Request

```python
response = sdk.chat(
    prompt="Describe this vehicle."
)
```

Vision Request

```python
response = sdk.chat(
    prompt="Identify this car.",
    image=image,
)
```

JSON Response

```python
response = sdk.chat_json(
    prompt="Extract vehicle information.",
    schema=VehicleSchema,
)
```

---

# Interaction with Other Modules

```
Backend

↓

QwenOnlineInference

↓

ImageProcessor

↓

ConversationManager

↓

Groq API

↓

Response

↓

Backend
```

---

# Error Handling

This file handles

- Authentication errors
- API connection errors
- Timeout errors
- Invalid prompts
- Invalid images
- Invalid JSON responses
- Generation failures

---

# Summary

`online_inference.py` is the central execution engine of the Groq Vision SDK.

It manages the complete inference lifecycle, including client initialization, message construction, image preparation, conversation management, API communication, retry logic, response processing, and runtime configuration.

All Backend interactions with the Groq Vision model should be performed through this class.


# prompts.py

**File Location**

```text
models/
└── qwen/
    └── prompts.py
```

---

# Purpose

`prompts.py` defines the default **System Prompt** used by the Groq Vision SDK.

The System Prompt controls the AI behavior before any user message is processed.

Instead of embedding prompts inside the inference engine, all prompt definitions are centralized in this file to simplify maintenance, prompt engineering, and future AI improvements.

---

# Responsibilities

- Define the default System Prompt.
- Configure the AI assistant personality.
- Define the response style.
- Control reasoning behavior.
- Improve response consistency.
- Reduce hallucinations.
- Provide a central location for Prompt Engineering.

---

# Main Variable

## SYSTEM_PROMPT

```python
SYSTEM_PROMPT
```

Purpose

Stores the default instruction sent to the Groq model before every conversation begins.

Every request automatically starts with this prompt.

---

# Current Responsibilities

The current System Prompt instructs the model to:

- Analyze uploaded vehicle images.
- Identify vehicles.
- Answer automotive-related questions.
- Explain answers clearly.
- Avoid unsupported assumptions.
- Produce professional responses.

---

# Execution Flow

```
SYSTEM_PROMPT

↓

QwenOnlineInference

↓

_build_messages()

↓

Groq API

↓

Generated Response
```

---

# Used By

```
online_inference.py
```

Example

```python
sdk = QwenOnlineInference(
    system_prompt=SYSTEM_PROMPT
)
```

Every request automatically includes this prompt as the first message.

---

# Current Prompt Structure

```
System Prompt

↓

Conversation History

↓

Current User Prompt

↓

Image (Optional)

↓

Groq Model
```

---

# Integration with the Ranking System

The current implementation uses a **single default System Prompt**.

For the production version of the project, this file will become the Prompt Repository used by the Ranking System.

Instead of sending one fixed prompt every time, the Ranking System will dynamically construct the final System Prompt according to the current situation.

---

# Planned Responsibilities for the Ranking System

The Ranking System should generate prompts dynamically using multiple factors.

---

## 1. Language Detection

The system should automatically detect the user's language before building the prompt.

Supported examples include:

- English
- Arabic
- Egyptian Arabic
- Mixed Arabic-English
- Other Arabic dialects
- Future multilingual support

The assistant should always answer using the same language used by the user unless another language is explicitly requested.

---

## 2. Tone Detection

The Ranking System should recognize the user's writing style.

Examples

- Professional
- Friendly
- Casual
- Technical
- Beginner
- Expert
- Offensive
- Aggressive

The generated prompt should adjust the response style while maintaining professionalism.

---

## 3. Moderation

If the user writes offensive or inappropriate messages, the prompt should instruct the model to:

- Stay respectful.
- Avoid offensive language.
- Continue helping whenever possible.
- Refuse only when required by the project rules.

The assistant should never respond with insults or aggressive language.

---

## 4. Confidence Verification

If the user says that the generated answer is incorrect, the Ranking System should verify the answer before changing it.

Suggested workflow

```
User

↓

"The answer is wrong."

↓

Check Conversation Memory

↓

Check Retrieved RAG Context

↓

Re-evaluate Model Knowledge

↓

Need More Evidence?

↓

YES

↓

Web Scraping

↓

Collect Trusted Sources

↓

Generate Updated Answer

↓

Return Verified Response
```

The system should not immediately assume that the model is wrong.

---

## 5. Evidence-Based Responses

When external verification is required, the Ranking System should instruct the model to include supporting evidence whenever available.

Examples

- Vehicle specifications
- Technical details
- Manufacturer information
- Trusted automotive websites
- Supporting images
- Reference links

This improves transparency and user confidence.

---

## 6. Prompt Categories

Instead of using one prompt, the project should maintain multiple prompt templates.

Examples

- Vehicle Identification
- Vehicle Analysis
- Vehicle Comparison
- Vehicle Specifications
- Image Analysis
- General Vehicle Questions
- Web Scraping
- RAG Generation
- JSON Extraction
- Safety & Moderation

The Ranking System should select the appropriate prompt according to the detected intent.

---

## 7. Context Awareness

Before generating the final prompt, the Ranking System should consider:

- User question
- Previous conversation
- Conversation Memory
- Vehicle Classification result
- Groq reasoning
- Google Lens result
- Web Scraping result
- Retrieved RAG documents
- Confidence score

The final prompt should be dynamically generated from all available information.

---

## 8. Dynamic Prompt Construction

Instead of sending

```
SYSTEM_PROMPT
```

The Ranking System should build

```
Language Prompt

+

Behavior Prompt

+

Moderation Prompt

+

Task Prompt

+

Retrieved Context

+

Conversation Memory

+

Current User Question

↓

Final System Prompt
```

This allows every request to receive a customized prompt based on the current situation.

---

# Future Prompt Repository

This file is expected to evolve into a repository containing multiple prompt templates.

Possible prompt templates include:

```text
SYSTEM_PROMPT

ARABIC_PROMPT

ENGLISH_PROMPT

VEHICLE_ANALYSIS_PROMPT

VEHICLE_COMPARISON_PROMPT

VEHICLE_SPECIFICATION_PROMPT

WEB_SCRAPING_PROMPT

RAG_PROMPT

JSON_PROMPT

MODERATION_PROMPT

VERIFY_RESPONSE_PROMPT

IMAGE_ANALYSIS_PROMPT
```

The Ranking System will dynamically combine these templates into a single final System Prompt.

---

# Backend Usage

The Backend does not interact directly with this file.

Instead, it initializes

```python
QwenOnlineInference
```

which automatically loads the current System Prompt.

In future versions, the Backend will receive the final prompt from the Ranking System instead of directly using `SYSTEM_PROMPT`.

---

# Summary

`prompts.py` is the Prompt Engineering layer of the Groq Vision SDK.

Currently, it stores the default System Prompt used by every request.

In the production architecture, this file will become a centralized Prompt Repository, while the Ranking System will dynamically generate the final System Prompt based on the user's language, writing style, conversation history, retrieved RAG context, classification results, external evidence, moderation requirements, and task type before sending the request to the Groq Vision model.


# conversation.py

**File Location**

```text
models/
└── qwen/
    └── conversation.py
```

---

# Purpose

`conversation.py` defines the conversation data model used throughout the Groq Vision SDK.

Instead of storing messages as raw dictionaries, every conversation message is represented as a structured object.

This provides a consistent message format across the entire SDK.

---

# Responsibilities

- Represent conversation messages.
- Store message metadata.
- Support serialization.
- Convert messages to API format.
- Simplify conversation management.

---

# Main Class

```
Conversation
```

Purpose

Represents a single message exchanged during a conversation.

Each object stores one message only.

Example

```
System Message

or

User Message

or

Assistant Message
```

---

# Message Structure

A conversation object typically contains:

```
Role

Content

Timestamp

Additional Metadata
```

Each message is completely independent.

---

# Supported Roles

The conversation model supports multiple message types.

```
system

user

assistant
```

Future roles can be added if required.

---

# Object Lifecycle

```
User Prompt

↓

Conversation Object

↓

Conversation Manager

↓

Groq Request

↓

Assistant Response

↓

Conversation Object

↓

Conversation History
```

---

# Main Responsibilities

The Conversation object is responsible for:

- Representing one message.
- Storing message content.
- Identifying sender role.
- Preserving conversation order.
- Supporting history reconstruction.

---

# Serialization

The conversation object can be converted into a dictionary before sending requests.

Example

```python
{
    "role": "...",
    "content": "..."
}
```

This format is compatible with the Groq Chat Completion API.

---

# API Compatibility

The generated structure follows the standard chat format.

Example

```python
[
    {
        "role": "system",
        "content": "..."
    },
    {
        "role": "user",
        "content": "..."
    },
    {
        "role": "assistant",
        "content": "..."
    }
]
```

---

# Used By

This file is imported by:

```
ConversationManager.py

↓

online_inference.py
```

The Backend never creates Conversation objects directly.

Instead, the Conversation Manager creates and manages them automatically.

---

# Interaction Flow

```
User Prompt

↓

Conversation Object

↓

Conversation Manager

↓

Groq API

↓

Assistant Response

↓

Conversation Object

↓

Conversation History
```

---

# Future Integration

The Ranking System can enrich each conversation object with additional metadata.

Possible future fields include:

- User language.
- Detected intent.
- Confidence score.
- Retrieved RAG context.
- Web Scraping status.
- Classification result.
- Moderation result.

This metadata can help the Ranking System generate better prompts and improve context selection.

---

# Summary

`conversation.py` defines the basic conversation object used by the SDK.

It standardizes how messages are represented, stored, serialized, and passed between the Conversation Manager, the inference engine, and the Groq API.


# ConversationManager.py

**File Location**

```text
models/
└── qwen/
    └── ConversationManager.py
```

---

# Purpose

`ConversationManager.py` manages the complete conversation lifecycle inside the Groq Vision SDK.

Instead of storing raw chat messages inside the inference engine, all conversation operations are delegated to this manager.

It acts as the memory layer between the Backend and the Groq Vision model.

---

# Responsibilities

- Store conversation history.
- Add new messages.
- Retrieve previous messages.
- Clear conversation history.
- Build API-compatible chat history.
- Manage conversation memory.
- Support future RAG integration.

---

# Main Class

```
ConversationManager
```

Purpose

Maintains the complete conversation history exchanged between the user and the AI assistant.

Unlike `Conversation`, which represents a single message, this class manages the entire chat session.

---

# Managed Data

The manager stores:

```
System Messages

↓

User Messages

↓

Assistant Responses

↓

Conversation History
```

The conversation remains available until it is explicitly cleared or the session ends.

---

# Main Responsibilities

The Conversation Manager is responsible for:

- Creating conversation history.
- Appending new messages.
- Returning conversation history.
- Resetting conversations.
- Exporting conversation data.
- Preparing messages for the Groq API.

---

# Internal Workflow

```
User Prompt

↓

Conversation Object

↓

ConversationManager

↓

Conversation History

↓

Groq API

↓

Assistant Response

↓

ConversationManager

↓

Updated History
```

---

# Main Methods

## add_system_message()

Purpose

Adds the initial System Prompt to the conversation.

Usually called once at the beginning of a session.

---

## add_user_message()

Purpose

Stores the latest user message.

Used before sending a request to Groq.

---

## add_assistant_message()

Purpose

Stores the AI response after the request is completed.

This allows future requests to preserve conversation context.

---

## get_history()

Purpose

Returns the complete conversation history.

Output

```python
List[Conversation]
```

Used by

```
online_inference.py
```

before calling the Groq API.

---

## clear()

Purpose

Removes all stored messages.

Useful when starting a new chat session.

---

## export()

Purpose

Converts the conversation history into an API-compatible structure.

Example

```python
[
    {
        "role": "system",
        "content": "..."
    },
    {
        "role": "user",
        "content": "..."
    }
]
```

This structure is sent directly to the Groq Chat Completion API.

---

# Dependencies

This manager depends on

```
conversation.py
```

Each stored message is represented as a `Conversation` object.

---

# Used By

```
online_inference.py
```

Every request automatically retrieves conversation history from this manager before generating a response.

---

# Backend Interaction

Current Backend

```
Backend

↓

QwenOnlineInference

↓

ConversationManager

↓

Groq API
```

The Backend does not directly manipulate conversation history.

It communicates only with `QwenOnlineInference`, which internally uses the Conversation Manager.

---

# Future RAG Integration

In the production system, the Conversation Manager will become one of the primary context sources for the Ranking System.

Instead of sending only previous chat messages, the Ranking System can combine:

- Conversation History
- Session Memory
- Vehicle Memory
- Comparison Memory
- Retrieved RAG Documents
- Web Scraping Results
- Classification Results

to construct a richer prompt before calling the Groq model.

---

# Planned Improvements

The Conversation Manager can be extended to support:

- Conversation summarization.
- Automatic context trimming.
- Token-aware memory management.
- Long-term conversation memory.
- Persistent chat history.
- Session synchronization.
- Memory prioritization.
- Conversation search.

These features will reduce token usage while preserving important context.

---

# Execution Flow

```
User

↓

ConversationManager

↓

Conversation History

↓

Ranking System

↓

Prompt Builder

↓

Groq Vision Model

↓

Assistant Response

↓

ConversationManager

↓

Updated History
```

---

# Summary

`ConversationManager.py` is the conversation memory manager of the Groq Vision SDK.

It maintains the complete chat history, prepares messages for the Groq API, and serves as the bridge between the inference engine and future context-aware components such as the Ranking System and the RAG pipeline.


# image_utils.py

**File Location**

```text
models/
└── qwen/
    └── image_utils.py
```

---

# Purpose

`image_utils.py` is responsible for preparing images before they are sent to the Groq Vision model.

Instead of allowing every module to process images independently, all image preprocessing operations are centralized in this file.

This ensures that every image reaches the model in the correct format.

---

# Responsibilities

- Validate image input.
- Load images from different sources.
- Convert images into supported formats.
- Encode images for the Groq API.
- Resize or normalize images if required.
- Handle invalid image inputs.

---

# Supported Image Sources

The utility should support different image inputs such as:

```
Local Image Path

↓

PIL Image

↓

Image URL

↓

Base64 Image
```

Regardless of the source, the output format should always be compatible with the Groq Vision API.

---

# Main Class

```
ImageProcessor
```

Purpose

Provides all helper methods required to prepare images before inference.

The Backend never interacts with this class directly.

It is automatically used by

```
QwenOnlineInference
```

---

# Internal Workflow

```
Input Image

↓

Validation

↓

Image Loading

↓

Image Conversion

↓

Encoding

↓

Groq Vision API
```

---

# Main Methods

## prepare_image()

Purpose

Main preprocessing function.

Responsibilities

- Detect image type.
- Validate the image.
- Convert to supported format.
- Return processed image.

This is the primary method called by the inference engine.

---

## load_image()

Purpose

Load an image from disk.

Input

```
Image Path
```

Output

```
PIL Image
```

---

## validate_image()

Purpose

Verify that the provided image is valid before inference.

Checks may include:

- File existence.
- Supported format.
- Readability.
- Corrupted image detection.

---

## encode_image()

Purpose

Convert the processed image into the format required by the Groq Vision API.

Depending on the SDK implementation, this may produce:

- Base64 encoding.
- Binary payload.
- API-compatible image object.

---

## image_to_message()

Purpose

Create the image section of the OpenAI-compatible message format.

Example

```python
{
    "type": "image_url",
    "image_url": {
        ...
    }
}
```

This structure is later combined with the user's text prompt.

---

# Dependencies

This file depends on image-processing libraries such as:

```
Pillow (PIL)

↓

Base64

↓

IO Utilities
```

The exact implementation depends on the SDK version.

---

# Used By

```
online_inference.py
```

Whenever an image is passed to

```python
sdk.chat(...)
```

or

```python
sdk.chat_json(...)
```

the image is automatically processed through `image_utils.py`.

---

# Backend Interaction

The Backend never imports this file directly.

Instead, the workflow is:

```
Backend

↓

QwenOnlineInference

↓

ImageProcessor

↓

Groq Vision API
```

---

# Future Improvements

For the production system, this module can be extended with:

- Automatic image resizing.
- Image compression.
- Background removal.
- Image enhancement.
- Image orientation correction.
- Image quality validation.
- Duplicate image detection.
- Vehicle region cropping before inference.

These improvements can reduce API cost while improving recognition quality.

---

# Integration with the Ranking System

The Ranking System may use this module before sending requests to the Vision model.

Possible future workflow:

```
User Uploads Image

↓

Image Validation

↓

Image Quality Check

↓

Vehicle Detection

↓

Image Enhancement (Optional)

↓

Classification Model

↓

Groq Vision Model
```

This allows low-quality images to be improved before AI inference begins.

---

# Error Handling

This module should handle:

- Missing image files.
- Unsupported formats.
- Invalid image objects.
- Corrupted images.
- Encoding failures.
- Empty image input.

Errors are propagated back to the inference engine through the SDK exception system.

---

# Summary

`image_utils.py` centralizes all image preprocessing operations required by the Groq Vision SDK.

It guarantees that every uploaded image is validated, converted, encoded, and formatted correctly before being sent to the Vision model, providing a consistent and reliable image-processing pipeline across the project.


# schemas.py

**File Location**

```text
models/
└── qwen/
    └── schemas.py
```

---

# Purpose

`schemas.py` defines the data schemas used throughout the Groq Vision SDK.

Instead of passing raw dictionaries between modules, structured schema objects are used to standardize request and response data.

This improves consistency, readability, validation, and maintainability.

---

# Responsibilities

- Define SDK data models.
- Standardize request objects.
- Standardize response objects.
- Validate input data.
- Validate output data.
- Improve Backend integration.

---

# Why Schemas?

Without schemas

```
Dictionary

↓

Unknown Structure

↓

Possible Errors
```

With schemas

```
Schema Object

↓

Validated Data

↓

Consistent Structure

↓

Safe API Communication
```

Schemas ensure that every module works with the same data format.

---

# Used By

The schema definitions are shared across the SDK.

Main users include

```
online_inference.py

↓

ConversationManager.py

↓

Backend
```

Whenever structured data is required, these schemas should be used.

---

# Typical Data Flow

```
Backend Request

↓

Schema Validation

↓

Groq SDK

↓

Groq Response

↓

Schema Object

↓

Backend
```

---

# Expected Schema Types

Depending on the project requirements, this file may contain objects such as:

```
Chat Request

Chat Response

Image Request

Vehicle Information

Usage Statistics

Model Information

Conversation Message

Configuration Schema
```

These schemas provide a unified representation of SDK data.

---

# Backend Interaction

Instead of returning raw dictionaries, the SDK can return schema objects.

Example

```python
response = sdk.chat(...)

↓

ResponseSchema

↓

Backend
```

This makes Backend processing simpler and reduces parsing errors.

---

# Future Integration

The Ranking System may also use dedicated schemas.

Examples

```
Intent Schema

↓

Language Detection Schema

↓

Moderation Result

↓

Confidence Evaluation

↓

Ranking Decision

↓

Prompt Selection
```

These schema objects can be exchanged between the Ranking System and the Groq SDK.

---

# Advantages

Using schemas provides several benefits:

- Consistent data structure.
- Easier debugging.
- Input validation.
- Output validation.
- Better API documentation.
- Easier Backend integration.
- Simpler future maintenance.

---

# Interaction Flow

```
Backend

↓

Schema Object

↓

Qwen SDK

↓

Groq API

↓

Schema Object

↓

Backend
```

---

# Summary

`schemas.py` defines the standardized data structures used throughout the Groq Vision SDK.

It provides a common contract between the SDK, Backend, and future Ranking System, ensuring that requests and responses follow a consistent, validated, and maintainable format.


# logger.py

**File Location**

```text
models/
└── qwen/
    └── logger.py
```

---

# Purpose

`logger.py` provides the centralized logging system for the Groq Vision SDK.

Instead of using Python's `print()` statements throughout the project, all modules use a shared logger instance.

This ensures consistent log formatting, easier debugging, and better monitoring of the SDK during development and production.

---

# Responsibilities

- Initialize the SDK logger.
- Standardize log formatting.
- Record runtime events.
- Record warnings.
- Record errors.
- Record debugging information.
- Support production monitoring.

---

# Main Component

```
logger
```

Purpose

Provides a shared logging instance that can be imported by any module inside the SDK.

Example

```python
from models.qwen.logger import logger
```

---

# Logging Levels

The logger supports different message levels.

## INFO

Used for normal application events.

Examples

- SDK initialization.
- Model loading.
- API request started.
- API request completed.

---

## WARNING

Used for recoverable problems.

Examples

- Missing optional parameter.
- Retry attempt.
- Slow response.
- Fallback execution.

---

## ERROR

Used for execution failures.

Examples

- API request failed.
- Invalid image.
- Authentication failure.
- Timeout.
- Invalid response.

---

## DEBUG

Used during development.

Examples

- Request payload.
- Generated messages.
- Internal variables.
- Response metadata.

---

# Used By

Almost every module imports the shared logger.

Examples

```
online_inference.py

config.py

image_utils.py

ConversationManager.py

exceptions.py
```

This provides a unified logging format across the SDK.

---

# Typical Workflow

```
Backend

↓

Qwen SDK

↓

logger.info()

↓

Execute Operation

↓

logger.error() (if needed)

↓

Return Result
```

---

# Example Usage

Initialization

```python
logger.info("Initializing Groq Vision SDK...")
```

Request

```python
logger.info("Sending request...")
```

Error

```python
logger.error("Request failed.")
```

---

# Future Improvements

The logging system can be extended with:

- Log files.
- Daily log rotation.
- Colored console output.
- Request identifiers.
- Performance timing.
- API latency monitoring.
- Token usage logging.
- Ranking System logging.
- Web Scraping logging.
- RAG execution logging.

---

# Integration with the Ranking System

The Ranking System can use this logger to record important decisions.

Examples

- Detected language.
- Detected user intent.
- Selected prompt.
- Retrieved RAG documents.
- Confidence evaluation.
- Web Scraping execution.
- Final routing decision.

This will make debugging AI decisions much easier.

---

# Summary

`logger.py` provides the centralized logging system for the Groq Vision SDK.

It allows every module to record runtime information, warnings, errors, and debugging messages using a single shared logger instance, making the SDK easier to monitor, debug, and maintain.


# exceptions.py

**File Location**

```text
models/
└── qwen/
    └── exceptions.py
```

---

# Purpose

`exceptions.py` defines all custom exception classes used by the Groq Vision SDK.

Instead of raising generic Python exceptions, the SDK uses specialized exceptions that clearly describe the type of failure.

This improves debugging, error handling, and Backend integration.

---

# Responsibilities

- Define custom exception classes.
- Standardize SDK error handling.
- Improve debugging.
- Simplify Backend exception handling.
- Provide meaningful error messages.

---

# Why Custom Exceptions?

Without custom exceptions

```
ValueError

↓

RuntimeError

↓

Exception
```

The Backend cannot easily determine the reason for the failure.

With custom exceptions

```
AuthenticationError

↓

ImageProcessingError

↓

GenerationError

↓

ValidationError
```

The Backend immediately knows what happened and can react accordingly.

---

# Exception Hierarchy

```
Exception

↓

QwenError

├── AuthenticationError

├── ConfigurationError

├── ImageProcessingError

├── ValidationError

├── GenerationError

└── APIError
```

*(The exact exception names depend on the implementation inside this file.)*

---

# Main Responsibilities

Each custom exception should represent one category of failures.

Examples include:

- Invalid configuration.
- Missing API key.
- Authentication failure.
- Image validation failure.
- Image processing failure.
- API communication failure.
- Response generation failure.
- Invalid request.
- Invalid response format.

---

# Used By

Almost every SDK module may raise one of these exceptions.

Examples

```
config.py

↓

online_inference.py

↓

image_utils.py

↓

ConversationManager.py
```

Instead of raising generic exceptions, they should raise SDK-specific exceptions.

---

# Backend Interaction

The Backend can catch only the exceptions it needs.

Example

```python
try:
    response = sdk.chat(...)
except GenerationError:
    ...
except ImageProcessingError:
    ...
except AuthenticationError:
    ...
```

This makes Backend error handling much cleaner.

---

# Execution Flow

```
Backend

↓

Qwen SDK

↓

Error Detected

↓

Raise Custom Exception

↓

Backend Handles Error

↓

Return User-Friendly Message
```

---

# Future Improvements

Additional exception classes can be introduced as the project grows.

Possible examples include:

- RankingError
- RAGError
- WebScrapingError
- GoogleLensError
- ClassificationError
- ConversationError
- MemoryError
- PromptGenerationError
- TokenLimitError
- RateLimitError

Using dedicated exception types will make the project easier to maintain and debug.

---

# Integration with the Ranking System

The Ranking System can also define its own custom exceptions while still following the same architecture.

Example

```
Ranking System

↓

IntentClassificationError

↓

PromptSelectionError

↓

ModerationError

↓

RoutingError

↓

FallbackError
```

This keeps error handling consistent across the entire AI pipeline.

---

# Summary

`exceptions.py` centralizes all custom exception classes used by the Groq Vision SDK.

It provides a consistent and maintainable error-handling mechanism, allowing both the SDK and the Backend to identify failures precisely, simplify debugging, and return appropriate user-facing error messages.
