

# Web Scraping & Knowledge Extraction

## Overview

The `web_scraping` module is responsible for collecting, extracting, cleaning, validating, and structuring vehicle-related information from trusted online sources.

The processed data is transformed into structured JSON documents that are stored in MongoDB and used by the Smart Vehicle Identifier backend and AI services.

This module operates independently from the AI models and is responsible only for data acquisition and processing.

---

# Architecture Position

```
Online Sources

↓

Google Search API

↓

Google Lens API

↓

Web Scraper

↓

Parser

↓

Extractor

↓

Cleaner

↓

JSON Builder

↓

MongoDB
```

---

# Responsibilities

The Web Scraping module is responsible for:

- Searching for vehicle information.
- Collecting web content.
- Extracting useful vehicle information.
- Cleaning raw text.
- Parsing structured content.
- Building JSON datasets.
- Preparing structured documents for MongoDB.
- Updating existing vehicle records.
- Extracting pricing information.
- Recording source URLs.

The module is NOT responsible for:

- AI inference.
- Vehicle classification.
- Question answering.
- Database management.
- User interaction.
- Backend business logic.

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

Searches for vehicle information using Google Search API before scraping begins.

### Responsibilities

- Build search queries.
- Retrieve search results.
- Return candidate URLs.

---

## google_lens.py

### Purpose

Uses Google Lens API to identify visually similar vehicles and retrieve related information sources.

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
- Handle request headers.
- Manage request sessions.
- Return webpage content.

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
- Pass downloaded pages to the parser.
- Handle scraping workflow.

---

## parser.py

### Purpose

Parses raw HTML into structured information.

### Responsibilities

- Extract HTML elements.
- Remove unnecessary markup.
- Organize webpage content.

---

## extractor.py

### Purpose

Extracts meaningful vehicle information from parsed content.

### Responsibilities

- Extract vehicle specifications.
- Extract vehicle descriptions.
- Extract engine information.
- Extract horsepower.
- Extract transmission.
- Extract fuel economy.
- Extract dimensions.
- Extract features.
- Extract pricing information.
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
- Validate extracted values.

---

## json_builder.py

### Purpose

Converts cleaned data into structured JSON documents ready for MongoDB storage.

### Responsibilities

- Generate JSON objects.
- Validate data.
- Build standardized schema.
- Export structured knowledge.

---

# Workflow

```
Vehicle Image

↓

Google Lens API

↓

Vehicle Identification

↓

Google Search API

↓

Search Results

↓

Web Scraper

↓

Parser

↓

Extractor

↓

Cleaner

↓

JSON Builder

↓

MongoDB
```

---

# Communication

The Web Scraping module communicates with:

- FastAPI Backend
- MongoDB

It does not communicate directly with:

- Frontend
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
- Be reusable by other services.

---

# Future Improvements

Possible future enhancements include:

- Multi-source scraping.
- Automatic duplicate detection.
- Scheduled data collection.
- Incremental updates.
- Metadata enrichment.
- Parallel scraping.
- Price history tracking.
- Automatic cache refresh.
- Source credibility scoring.
- Multi-language scraping.
