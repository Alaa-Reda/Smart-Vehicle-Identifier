
# Frontend Components

## Overview

The `components` module contains reusable user interface components used by the Smart Vehicle Identifier frontend.

Each component is responsible for rendering a specific part of the application's user interface while keeping the frontend organized and maintainable.

Components should focus only on presentation and user interaction. Business logic and AI processing are handled by the backend.

---

# Folder Structure

```
components/
│
├── chatbot.py
├── comparison.py
├── ui.py
├── uploader.py
└── vehicle_card.py
```

---

# Component Specifications

## chatbot.py

### Purpose

Provides the chat interface that allows users to ask questions about an analyzed vehicle.

### Responsibilities

- Display chat messages.
- Accept user questions.
- Send questions to the frontend application.
- Display AI responses.

---

## comparison.py

### Purpose

Displays a side-by-side comparison between two vehicles.

### Responsibilities

- Present comparison results.
- Organize vehicle specifications.
- Highlight similarities and differences.

---

## ui.py

### Purpose

Contains shared UI utilities and reusable interface elements used across the application.

### Responsibilities

- Common buttons.
- Layout helpers.
- Styled containers.
- Shared interface elements.

---

## uploader.py

### Purpose

Provides the vehicle image upload interface.

### Responsibilities

- Select image files.
- Validate uploaded images.
- Preview selected images.
- Pass images to the frontend application.

---

## vehicle_card.py

### Purpose

Displays vehicle information returned from the backend.

### Responsibilities

- Show vehicle image.
- Display brand and model.
- Display vehicle specifications.
- Present confidence scores when available.

---

# Communication

```
User

↓

UI Component

↓

Frontend Application

↓

Backend API

↓

Frontend Application

↓

UI Component

↓

User
```

Components never communicate directly with the backend.

---

# Design Principles

Every component should:

- Have a single responsibility.
- Be reusable.
- Be independent.
- Focus only on the user interface.
- Receive data from the frontend application.

---

# Naming Convention

Files use **snake_case**.

Examples:

```
chatbot.py

comparison.py

ui.py

uploader.py

vehicle_card.py
```

---

# Development Rules

- One responsibility per component.
- No business logic.
- No AI inference.
- No database operations.
- No direct API implementation.
- Keep components lightweight and reusable.

---

# Future Improvements

Possible future components include:

- History Panel
- Settings Dialog
- Theme Switcher
- Notification Widget
- Loading Overlay
- Error Dialog
