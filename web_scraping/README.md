
# Web Scraping & Knowledge Extraction

## Overview

The `web_scraping` module is responsible for collecting, extracting, cleaning, and structuring vehicle-related information from online sources.

The processed data is transformed into a structured knowledge base that supports the Retrieval-Augmented Generation (RAG) system used throughout the Smart Vehicle Identifier project.

This module operates during the data collection phase and is independent from the runtime inference pipeline.

---

# Architecture Position

```
Online Sources

↓

Search Engine

↓

Google Lens

↓

Web Scraper

↓

Content Extraction

↓

Content Cleaning

↓

JSON Builder

↓

Knowledge Base

↓

Embedding

↓

FAISS Database
```

---

# Responsibilities

The Web Scraping module is responsible for:

- Searching for vehicle information.
- Collecting web content.
- Extracting useful information.
- Cleaning raw text.
- Parsing structured content.
- Building JSON datasets.
- Preparing data for the embedding pipeline.

The module is NOT responsible for:

- AI inference.
- Vehicle classification.
- Question answering.
- Database operations.
- User interaction.

---

# Folder Structure

```
web_scraping/
│
├── cleaner.py
├── extractor.py
├── google_lens.py
├── json_builder.py
├── parser.py
├── playwright.py
├── requests.py
├── scraper.py
└── search.py
```

---

# File Specifications

## search.py

### Purpose

Searches for relevant vehicle information using search engines before scraping begins.

### Responsibilities

- Build search queries.
- Retrieve search results.
- Return candidate URLs.

---

## google_lens.py

### Purpose

Uses Google Lens to identify or locate visually similar vehicles and retrieve related information sources.

### Responsibilities

- Submit vehicle images.
- Retrieve matching search results.
- Provide candidate pages for scraping.

---

## requests.py

### Purpose

Handles HTTP requests for downloading webpage content.

### Responsibilities

- Send HTTP requests.
- Handle headers.
- Manage request sessions.
- Return page content.

---

## playwright.py

### Purpose

Handles websites that require JavaScript rendering.

### Responsibilities

- Launch browser sessions.
- Render dynamic pages.
- Retrieve fully loaded HTML.

---

## scraper.py

### Purpose

Coordinates the complete scraping workflow.

### Responsibilities

- Manage scraping tasks.
- Coordinate requests.
- Pass pages to the parser.
- Handle scraping flow.

---

## parser.py

### Purpose

Parses raw HTML into structured information.

### Responsibilities

- Extract HTML elements.
- Remove unnecessary markup.
- Organize page content.

---

## extractor.py

### Purpose

Extracts meaningful vehicle information from parsed content.

### Responsibilities

- Extract specifications.
- Extract descriptions.
- Extract technical information.
- Remove irrelevant content.

---

## cleaner.py

### Purpose

Cleans extracted information before storage.

### Responsibilities

- Remove duplicates.
- Normalize text.
- Clean formatting.
- Remove unnecessary whitespace.

---

## json_builder.py

### Purpose

Converts cleaned data into structured JSON documents ready for indexing.

### Responsibilities

- Generate JSON objects.
- Validate data.
- Export structured knowledge.

---

# Workflow

```
Vehicle Image

↓

Google Lens

↓

Search Results

↓

Scraper

↓

Parser

↓

Extractor

↓

Cleaner

↓

JSON Builder

↓

Knowledge Base
```

---

# Communication

The Web Scraping module communicates with:

- Knowledge Base Builder
- Embedding Pipeline

It does not communicate directly with:

- Frontend
- Database
- AI Models
- Controllers

---

# Development Rules

Every module should:

- Have one responsibility.
- Produce structured output.
- Handle errors gracefully.
- Avoid business logic.
- Remain independent from AI inference.
- Support future data sources.

---

# Future Improvements

Possible future enhancements include:

- Multi-source scraping.
- Automatic duplicate detection.
- Incremental updates.
- Scheduled data collection.
- Metadata enrichment.
- Parallel scraping.
