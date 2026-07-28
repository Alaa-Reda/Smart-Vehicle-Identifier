
# Frontend

# Smart Vehicle Identifier Frontend

## Overview

The Frontend module provides the graphical user interface (GUI) for the Smart Vehicle Identifier system.

It allows users to interact with the AI system through an intuitive interface without requiring technical knowledge.

The frontend communicates exclusively with the Backend REST API and is responsible only for presenting data and collecting user input.

It does not contain business logic or AI processing.

---

# Architecture Position

```
                User
                  │
                  ▼
          Streamlit Frontend
                  │
          HTTP REST API
                  │
                  ▼
         Smart Vehicle Backend
```

---

# Responsibilities

The Frontend is responsible for:

- Displaying the user interface.
- Uploading vehicle images.
- Sending user questions.
- Displaying vehicle information.
- Displaying AI-generated answers.
- Showing comparison reports.
- Managing user interaction.

The Frontend is NOT responsible for:

- AI inference.
- Vehicle recognition.
- Business logic.
- Prompt engineering.
- Database operations.
- Web scraping.

---

# Communication Flow

```
User

↓

Frontend

↓

HTTP Request

↓

Backend API

↓

JSON Response

↓

Frontend

↓

User
```

---

# Main Features

## Vehicle Image Analysis

Users can:

- Upload a vehicle image.
- Analyze the uploaded image.
- View recognized vehicle information.

---

## Intelligent Question Answering

Users can ask questions such as:

- What is the model of this car?
- What engine does it use?
- Is this car suitable for families?
- What are the specifications?

The frontend sends the question to the backend and displays the generated response.

---

## Vehicle Comparison

Users can compare two vehicles and receive a structured comparison including:

- Brand
- Model
- Engine
- Performance
- Features
- Advantages
- Disadvantages

---

## Session History

The frontend allows users to review previous conversations and vehicle analyses.

---

# Backend Integration

The frontend communicates with the following backend endpoints:

```
POST   /image/upload

POST   /image/analyze

POST   /chat

POST   /compare

GET    /history
```

All communication is performed using JSON over HTTP.

---

# User Workflow

```
Open Application

↓

Upload Vehicle Image

↓

Vehicle Analysis

↓

Ask Questions

↓

Receive AI Answer

↓

Compare Vehicles (Optional)

↓

Review History
```

---

# Design Principles

The frontend follows these principles:

- Simple User Experience (UX)
- Responsive Interface
- Minimal User Interaction
- Clear Information Presentation
- Fast Feedback
- Separation from Backend Logic

---

# Development Rules

The frontend must follow these rules:

- No AI logic.
- No database access.
- No prompt generation.
- No business logic.
- All processing must occur in the backend.
- Every user action should communicate through the REST API.

---

# Future Improvements

Possible future enhancements include:

- User authentication.
- Dashboard analytics.
- Dark/Light theme switching.
- Voice interaction.
- Multi-language support.
- Mobile-friendly interface.
- Vehicle recommendation dashboard.
