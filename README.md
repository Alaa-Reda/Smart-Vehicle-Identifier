
# 🚗 Smart Vehicle Identifier

> **An AI-powered Vehicle Recognition & Visual Question Answering System**

**Computer Vision • Vision-Language Models • Retrieval-Augmented Generation (RAG) • FastAPI • Streamlit • FAISS • MongoDB**

---

## Overview

Smart Vehicle Identifier is an AI-powered system that analyzes vehicle images and provides intelligent, context-aware responses about the detected vehicle.

The project combines Computer Vision, Retrieval-Augmented Generation (RAG), and Vision-Language Models to build an end-to-end vehicle understanding platform capable of recognizing vehicles, retrieving relevant knowledge, and answering user questions naturally.

---

## Features

- Vehicle image analysis
- Vehicle classification
- Intelligent Visual Question Answering (VQA)
- Retrieval-Augmented Generation (RAG)
- Semantic search using vector embeddings
- Vehicle comparison
- Conversation history
- Modular AI architecture
- Extensible knowledge base

---

# System Architecture

```text
                    User
                      │
                      ▼
             Streamlit Frontend
                      │
                      ▼
                FastAPI Backend
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
 Image Processing              RAG Pipeline
        │                           │
        ▼                           ▼
 Car Classification         Semantic Retrieval
        │                           │
        ▼                           ▼
 Vehicle Information       FAISS + Embeddings
        │                           │
        └─────────────┬─────────────┘
                      ▼
          Qwen Vision-Language Model
                      │
                      ▼
              Intelligent Response
```

---

## Project Structure

```text
Smart-Vehicle-Identifier/
│
├── backend/
├── data/
├── frontend/
├── models/
├── notebooks/
├── tests/
├── web_scraping/
├── docs/
│
├── app.py
├── requirements.txt
└── README.md
```

---

## Module Overview

### Backend

Implements the application's business logic, REST API, RAG pipeline, memory management, and communication between all AI components.

---

### Frontend

Provides a user-friendly interface for uploading vehicle images, asking questions, and displaying AI-generated responses.

---

### Models

Contains all AI models used by the project, including:

- Vehicle Classification Model
- Embedding Model
- Qwen Vision-Language Model

---

### Data

Stores vector databases, MongoDB collections, and research datasets used throughout the project.

---

### Web Scraping

Collects, extracts, cleans, and structures vehicle information to build the project's knowledge base.

---

### Notebooks

Contains research notebooks documenting experimentation, model evaluation, and fine-tuning workflows conducted during the development process.

---

### Documentation

Contains the project's technical documentation, software design, architecture, and development documents.

---

## AI Pipeline

```text
Vehicle Image

↓

Vehicle Classification

↓

Vehicle Information

↓

Knowledge Retrieval

↓

Embedding Generation

↓

FAISS Search

↓

Relevant Context

↓

Qwen Vision-Language Model

↓

Generated Response
```

---

## Technologies

### Programming Language

- Python

### Backend

- FastAPI

### Frontend

- Streamlit

### Artificial Intelligence

- PyTorch
- Hugging Face Transformers
- Qwen3-VL
- Sentence Transformers

### Vector Database

- FAISS

### Database

- MongoDB

### Web Scraping

- Playwright
- Requests
- BeautifulSoup

---

## Development Workflow

The project was developed through multiple stages:

1. System architecture and planning.
2. Dataset preparation and experimentation.
3. AI model evaluation.
4. Knowledge base construction.
5. Backend implementation.
6. Frontend development.
7. System integration.
8. Testing and validation.

---

## Future Improvements

- Real-time vehicle detection
- OCR integration
- Vehicle damage assessment
- Multi-language support
- Voice interaction
- Additional Vision-Language Models
- Cloud deployment
- Mobile application

---

## License

This project was developed for educational and research purposes as a Graduation Project.
