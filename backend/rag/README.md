
# Backend RAG Module

# ⚠️ Core Module

The **RAG (Retrieval-Augmented Generation)** module is the **heart of the Smart Vehicle Identifier system**.

This module is responsible for orchestrating the complete intelligence workflow of the application.

Every intelligent operation inside the system eventually passes through this module.

Without the RAG module, the system becomes only:

- An image classifier
- A search engine
- A database

The RAG module combines all of these components together into one intelligent pipeline capable of answering user questions with accurate and contextual responses.

---

# Module Overview

The RAG module coordinates communication between:

- AI Models
- Web Scraping
- Memory Layer
- Database
- Retrieval Engine
- Prompt Builder
- Large Language Model (Qwen)

Its responsibility is not only retrieval.

Its responsibility is making intelligent decisions.

---

# Architecture Position

```
                    User Question
                          │
                          ▼
                    Chat Controller
                          │
                          ▼
                    Chat Service
                          │
                          ▼
                   RAG Pipeline
        	  ┌──────────┼──────────┐
      		  │          │          │
       		  ▼          ▼          ▼
 		Image Analysis  Retrieval  Memory
    		  │          │          │
      		  └──────────┼──────────┘
               	         ▼
         	   		Prompt Builder
                   		│
                   		▼
             	 Qwen3-VL Model
                	   │
                   	   ▼
            	Generated Answer
```

---

# Responsibilities

The RAG module is responsible for:

- Orchestrating the complete AI workflow.
- Retrieving relevant information.
- Building conversation context.
- Creating prompts.
- Calling the LLM.
- Returning the final answer.

The RAG module is NOT responsible for:

- HTTP Requests.
- Database CRUD.
- Vehicle Detection.
- Web Scraping.
- UI Rendering.

---

# Folder Structure

```
rag/
│
├── pipeline.py
├── retriever.py
├── context_builder.py
├── prompt_builder.py
├── response_generator.py
└── rag_manager.py
```

---

# File Specifications

---

# pipeline.py

## Purpose

The main execution pipeline of the entire system.

This file controls the complete AI workflow from user question until final response.

This is considered the main execution engine.

---

## Main Class

```python
class RAGPipeline
```

---

## Responsibilities

- Start workflow.
- Call Retriever.
- Call Context Builder.
- Call Prompt Builder.
- Call Response Generator.
- Return final response.

---

## Public Methods

### run()

Execute complete pipeline.

---

### initialize_pipeline()

Prepare required resources.

---

### execute_step()

Execute one pipeline stage.

---

### finalize()

Return final output.

---

## Workflow

```
Question

↓

Retrieve Context

↓

Build Context

↓

Generate Prompt

↓

Qwen

↓

Final Answer
```

---

# retriever.py

## Purpose

Retrieve the most relevant information required to answer the user's question.

---

## Main Class

```python
class Retriever
```

---

## Responsibilities

- Search FAISS.
- Retrieve MongoDB metadata.
- Rank documents.
- Remove duplicates.
- Return Top-K context.

---

## Public Methods

### retrieve()

Main retrieval function.

---

### search_vectors()

Search FAISS.

---

### rank_documents()

Rank retrieved documents.

---

### filter_documents()

Remove irrelevant results.

---

## Dependencies

Uses

- FAISS
- MongoDB

---

# context_builder.py

## Purpose

Build the final context that will be sent to the language model.

---

## Main Class

```python
class ContextBuilder
```

---

## Responsibilities

- Merge retrieved documents.
- Merge vehicle information.
- Merge chat history.
- Remove duplicated information.
- Optimize context length.

---

## Public Methods

### build_context()

Create final context.

---

### merge_documents()

Merge retrieval results.

---

### optimize_context()

Reduce unnecessary information.

---

## Dependencies

Uses

- Retriever
- Memory Layer

---

# prompt_builder.py

## Purpose

Generate the final prompt for Qwen.

Prompt quality directly affects answer quality.

---

## Main Class

```python
class PromptBuilder
```

---

## Responsibilities

- Create System Prompt.
- Create User Prompt.
- Inject Context.
- Apply Prompt Template.

---

## Public Methods

### build_prompt()

Generate complete prompt.

---

### build_system_prompt()

Generate system instructions.

---

### build_user_prompt()

Generate user request.

---

## Dependencies

Uses

- Context Builder

---

# response_generator.py

## Purpose

Generate the final answer using Qwen.

---

## Main Class

```python
class ResponseGenerator
```

---

## Responsibilities

- Send prompt to Qwen.
- Receive generated response.
- Validate output.
- Format response.

---

## Public Methods

### generate()

Generate answer.

---

### validate_output()

Check response quality.

---

### format_response()

Return clean response.

---

## Dependencies

Uses

- Qwen Model

---

# rag_manager.py

## Purpose

Coordinate communication between every RAG component.

Acts as the central manager of the RAG module.

---

## Main Class

```python
class RAGManager
```

---

## Responsibilities

- Initialize components.
- Manage workflow.
- Handle errors.
- Monitor execution.
- Coordinate pipeline.

---

## Public Methods

### initialize()

Initialize all modules.

---

### execute()

Execute complete workflow.

---

### shutdown()

Release resources.

---

# Complete Workflow

```
User

↓

Frontend

↓

Chat Controller

↓

Chat Service

↓

RAG Manager

↓

Pipeline

↓

Retriever

↓

Context Builder

↓

Prompt Builder

↓

Qwen

↓

Generated Answer

↓

Frontend
```

---

# Dependencies

The RAG module communicates with:

- Memory Module
- Database Layer
- Web Scraping Module
- AI Models
- Chat Service

It never communicates directly with the Frontend.

---

# Development Rules

Every RAG component must follow these rules.

✅ Single Responsibility Principle.

✅ One class per file.

✅ Modular design.

✅ Independent components.

✅ Reusable methods.

✅ Clear interfaces.

❌ No HTTP requests.

❌ No UI logic.

❌ No database CRUD.

❌ No frontend communication.

---

# Naming Convention

Files

```
pipeline.py

retriever.py

context_builder.py

prompt_builder.py

response_generator.py

rag_manager.py
```

Classes

```
RAGPipeline

Retriever

ContextBuilder

PromptBuilder

ResponseGenerator

RAGManager
```

---

# Future Extensions

Future improvements may include:

- Hybrid Retrieval
- Query Rewriting
- Multi-Agent Reasoning
- Multi-Modal Retrieval
- Knowledge Graph Integration
- Self-Reflection Pipeline
- Citation Generation
- Response Verification
