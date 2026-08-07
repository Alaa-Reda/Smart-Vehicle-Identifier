# Smart Vehicle Identifier

---

# 1. Project Overview

## Project Goal

Smart Vehicle Identifier is an AI-powered system that identifies vehicles from images or text and provides accurate, structured information using multiple AI components.

Instead of relying on a single model, the system combines:

- Vehicle Classification Model
- Qwen Vision-Language Model
- RAG System
- Web Scraping
- MongoDB Memory

to improve both accuracy and reliability.

---

# 2. Project Architecture

```text
                       User
                         │
                         ▼
                  Frontend (Streamlit)
                         │
                         ▼
                    Backend API
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
 Classification      Qwen Model      RAG System
      Model             (LLM)        + Memory
        │                │
        └──────────┬─────┘
                   ▼
         Confidence Decision
                   │
          High Confidence?
          │             │
         Yes            No
          │             ▼
          │      Web Scraping
          │             │
          ▼             ▼
      Final Answer  Extract Vehicle Data
              │
              ▼
         MongoDB Database
              │
              ▼
          Backend Response
              │
              ▼
            Frontend
```

---

# 3. Project Folder Structure

```text
Smart-Vehicle-Identifier/

│
├── backend/
├── frontend/
├── models/
├── web_scraping/
├── data/
├── notebooks/
├── tests/
│
├── requirements.txt
├── README.md
└── ...
```

---

# 4. Main Components

## Frontend

Responsible for

- User Interface
- Upload Image
- Chat
- Display Results

---

## Backend

Responsible for

- APIs
- Controllers
- Services
- RAG
- Memory
- Decision Making

---

## Models

Contains

- Vehicle Classification Model
- Qwen SDK
- AI Utilities

---

## Web Scraping

Fallback system.

Activated only when AI confidence is low.

Collects information from trusted automotive websites.

---

## Database

Stores

- Chat History
- Vehicle History
- Session Memory
- Comparison History
- Vector Embeddings

---

## Tests

Contains unit tests for every major module.

---

## Notebooks

Contains research notebooks used during experimentation and model evaluation.

---

# 5. Overall Request Flow

## Case 1

Vehicle Image

↓

Classification Model

↓

Confidence ≥ 80%

↓

Vehicle Name

↓

Qwen

↓

Final Answer

---

## Case 2

Vehicle Image

↓

Classification Model

↓

Confidence < 80%

↓

Qwen Vision

↓

Confident

↓

Final Answer

---

## Case 3

Vehicle Image

↓

Classification Model

↓

Confidence < 80%

↓

Qwen

↓

Not Confident

↓

Google Lens

↓

Google Search

↓

Web Scraping

↓

RAG

↓

Backend

↓

Frontend

---

# 6. Why Hybrid Architecture?

Using only one AI model is not sufficient because:

- Classification is accurate only for trained classes.
- LLMs may hallucinate.
- Vehicle specifications change over time.

Therefore the system combines

Classification
+

Qwen

Web Scraping

RAG

MongoDB

to maximize answer quality.

---

# 7. Module Dependency

```text
Frontend
    │
    ▼
Backend
    │
    ├────────► Models
    │
    ├────────► RAG
    │
    ├────────► Database
    │
    └────────► Web Scraping
```

---

# 8. Documentation Roadmap

This document explains the following modules in order:

1. scraper.py
2. search.py
3. google_lens.py
4. requests.py
5. playwright.py
6. parser.py
7. extractor.py
8. cleaner.py
9. json_builder.py

---

# scraper.py

> **File Location**

```text
web_scraping/scraper.py
```

---

# Purpose

`scraper.py` is the main orchestrator of the entire Web Scraping module.

It coordinates all scraping components, controls the workflow, decides how pages should be downloaded, merges data collected from multiple websites, and builds the final MongoDB-ready document.

Every backend component should interact with the Web Scraping module through this file instead of calling the helper modules directly.

---

# Main Class

```python
VehicleScraper
```

Import

```python
from web_scraping.scraper import VehicleScraper
```

Example

```python
scraper = VehicleScraper()
```

---

# Internal Dependencies

VehicleScraper internally imports the following modules:

```python
from .search import VehicleSearchClient
from .google_lens import GoogleLensClient
from .requests import HTTPClient
from .playwright import BrowserSession
from .parser import HTMLParser
from .extractor import VehicleExtractor
from .cleaner import DataCleaner
from .json_builder import VehicleDocumentBuilder
```

Workflow

```
VehicleScraper

│

├── VehicleSearchClient

├── GoogleLensClient

├── HTTPClient

├── BrowserSession

├── HTMLParser

├── VehicleExtractor

├── DataCleaner

└── VehicleDocumentBuilder
```

---

# Global Settings

## MAX_PAGES

```python
MAX_PAGES = 5
```

Purpose

Maximum number of websites that will be scraped for one request.

Increasing this value

Advantages

- More information
- Better accuracy

Disadvantages

- Slower response
- More HTTP requests

---

## BLOCKED_DOMAINS

```python
BLOCKED_DOMAINS = {
    ...
}
```

Purpose

Ignore websites that usually don't contain useful vehicle specifications.

Examples

- Facebook
- Instagram
- TikTok
- Reddit
- Pinterest
- Twitter

---

# Constructor

```python
VehicleScraper(
    use_selenium_for_all=False,
    headless=True,
    max_pages=5
)
```

Parameters

### use_selenium_for_all

Type

```python
bool
```

Default

```python
False
```

Purpose

Force Selenium for every page instead of Requests.

Normally

```
Requests

↓

If failed

↓

Selenium
```

When True

```
Every page

↓

Selenium
```

---

### headless

Type

```python
bool
```

Default

```python
True
```

Purpose

Run Selenium without opening a browser window.

---

### max_pages

Type

```python
int
```

Default

```python
5
```

Purpose

Maximum number of pages to scrape.

---

# Private Functions

Private functions are helper functions used only inside VehicleScraper.

They should NOT be called directly from Backend.

---

## _fetch()

```python
_fetch(url)
```

Purpose

Download a webpage.

Workflow

```
Try HTTP Request

↓

Success

↓

Return HTML

↓

Failure

↓

Open Selenium

↓

Render JavaScript

↓

Return HTML
```

Returns

```python
str | None
```

Used By

```
_process_url()
```

---

## _process_url()

```python
_process_url(url)
```

Purpose

Process one webpage.

Workflow

```
Download HTML

↓

Parse HTML

↓

Extract Data

↓

Clean Data

↓

Return Dictionary
```

Returns

```python
dict
```

Uses

- HTTPClient
- BrowserSession
- HTMLParser
- VehicleExtractor
- DataCleaner

---

## _process_urls()

```python
_process_urls(urls)
```

Purpose

Process multiple webpages.

Workflow

```
URLs

↓

Filter blocked domains

↓

Process every page

↓

Merge all pages

↓

Return

Merged Data

+

Source URLs
```

Returns

```python
tuple(
    merged_data,
    source_urls
)
```

---

# Public Functions

These functions are intended to be used by the Backend.

---

## scrape_by_name()

```python
scrape_by_name(
    make,
    model,
    year
)
```

Purpose

Scrape vehicle specifications using

- Make
- Model
- Year

Example

```python
scraper = VehicleScraper()

vehicle = scraper.scrape_by_name(
    make="BMW",
    model="X5",
    year="2024"
)
```

Workflow

```
Vehicle Name

↓

Google Search

↓

Collect URLs

↓

Download Pages

↓

Parse

↓

Extract

↓

Clean

↓

Merge

↓

Build JSON

↓

Return Document
```

Returns

```python
dict
```

---

## scrape_by_image()

```python
scrape_by_image(image)
```

Purpose

Identify the vehicle using Google Lens before scraping.

Workflow

```
Image

↓

Google Lens

↓

Vehicle Title

↓

Extract

Make

Model

Year

↓

Google Search

↓

Collect URLs

↓

Scrape

↓

Build JSON
```

Example

```python
vehicle = scraper.scrape_by_image(
    "car.jpg"
)
```

Returns

```python
dict
```

---

## scrape_brand_overview()

```python
scrape_brand_overview(
    make,
    year
)
```

Purpose

Scrape general information about a vehicle brand.

Example

```
BMW

Audi

Toyota

Mercedes
```

instead of

```
BMW X5

Audi A6
```

Workflow

```
Brand

↓

Search

↓

Multiple Websites

↓

Extract

↓

Merge

↓

JSON
```

Returns

```python
dict
```

---

# Complete Internal Flow

```
Backend

↓

VehicleScraper

↓

Search URLs

↓

Download HTML

↓

Parse HTML

↓

Extract Vehicle Data

↓

Clean Data

↓

Merge Multiple Pages

↓

Build MongoDB Document

↓

Return Result
```

---

# Backend Usage

Typical usage inside Backend

```python
from web_scraping.scraper import VehicleScraper

scraper = VehicleScraper()

vehicle = scraper.scrape_by_name(
    make,
    model,
    year
)
```

or

```python
vehicle = scraper.scrape_by_image(image)
```

---

# Used By

This file is expected to be used by

- Backend Services
- AI Agent
- RAG Pipeline
- Chat Controller
- Comparison Service

Any future module that needs live vehicle information should communicate with the Web Scraping system through `VehicleScraper`.

---

# search.py

> **File Location**

```text
web_scraping/search.py
```

---

# Purpose

`search.py` is responsible for searching trusted automotive websites.

Instead of scraping random websites, this module builds an optimized search query, sends it to the search engine (Google/SerpAPI), filters the returned results, and returns only useful URLs for scraping.

This module is always executed before downloading any webpage.

---

# Main Class

```python
VehicleSearchClient
```

Import

```python
from web_scraping.search import VehicleSearchClient
```

Example

```python
client = VehicleSearchClient()
```

---

# Responsibilities

- Build optimized search queries.
- Search Google using SerpAPI.
- Filter trusted websites.
- Remove duplicated URLs.
- Ignore blocked domains.
- Return clean search results.

---

# Main Settings

## SERPAPI_KEY

```python
SERPAPI_KEY
```

Purpose

API Key used to communicate with SerpAPI.

Without this key, search requests cannot be executed.

---

## SEARCH_ENGINE

```python
google
```

Purpose

Defines which search engine is used.

---

## MAX_RESULTS

Example

```python
10
```

Purpose

Maximum number of search results returned for each request.

---

## PREFERRED_DOMAINS

Example

```text
caranddriver.com
edmunds.com
cars.com
motortrend.com
carwow.co.uk
autocar.co.uk
```

Purpose

Trusted automotive websites that have higher priority.

---

## BLOCKED_DOMAINS

Example

```text
facebook.com
instagram.com
reddit.com
tiktok.com
pinterest.com
youtube.com
```

Purpose

Websites that should never be scraped.

---

# Main Functions

---

## build_query()

```python
build_query(
    make,
    model,
    year
)
```

Purpose

Create an optimized Google search query.

Example

Input

```text
BMW
X5
2024
```

Output

```text
BMW X5 2024 specifications site:caranddriver.com OR site:edmunds.com
```

Returns

```python
str
```

---

## search()

```python
search(query)
```

Purpose

Send the search request to Google (SerpAPI).

Workflow

```
Query

↓

Google Search

↓

Search Results

↓

Return Raw Results
```

Returns

```python
list
```

---

## search_vehicle()

```python
search_vehicle(
    make,
    model,
    year
)
```

Purpose

Search for a specific vehicle.

Workflow

```
Vehicle Name

↓

Build Query

↓

Google Search

↓

Filter Results

↓

Remove Duplicate URLs

↓

Return URLs
```

Example

```python
urls = client.search_vehicle(
    make="BMW",
    model="X5",
    year="2024"
)
```

Returns

```python
list[str]
```

---

## search_brand()

```python
search_brand(
    make
)
```

Purpose

Search general information about a vehicle manufacturer.

Example

```
BMW

Toyota

Mercedes

Hyundai
```

Returns

```python
list[str]
```

---

## filter_results()

```python
filter_results(results)
```

Purpose

Remove unwanted websites.

Rules

- Remove duplicated URLs.
- Remove blocked domains.
- Keep trusted websites.
- Ignore advertisements.

Returns

```python
list[str]
```

---

## rank_results()

```python
rank_results(results)
```

Purpose

Sort search results by quality.

Priority

```
Trusted Automotive Website

↓

Official Brand Website

↓

News Website

↓

Other Websites
```

Returns

```python
list[str]
```

---

# Complete Workflow

```
Vehicle Name

↓

build_query()

↓

Google Search

↓

Raw Results

↓

filter_results()

↓

rank_results()

↓

Clean URL List

↓

VehicleScraper
```

---

# Input

Example

```python
make = "BMW"

model = "X5"

year = "2024"
```

---

# Output

Example

```python
[
    "https://www.caranddriver.com/...",
    "https://www.edmunds.com/...",
    "https://www.cars.com/..."
]
```

---

# Used By

This module is mainly used by

- VehicleScraper
- Backend Services
- AI Agent
- Future Search Components

---

# Dependencies

Imports commonly used in this file may include

```python
requests
serpapi
urllib.parse
logging
re
json
```

---

# Related Files

```
scraper.py
        │
        ▼
search.py
        │
        ▼
requests.py
        │
        ▼
playwright.py
```

---

# Backend Usage

Typical usage

```python
from web_scraping.search import VehicleSearchClient

client = VehicleSearchClient()

urls = client.search_vehicle(
    make="BMW",
    model="X5",
    year="2024"
)

print(urls)
```

---

# Notes

- This module only searches and returns URLs.
- It does not download webpages.
- It does not parse HTML.
- It does not extract vehicle specifications.
- The returned URLs are passed to `scraper.py`, which continues the scraping pipeline.

---

# google_lens.py

> **File Location**

```text
web_scraping/google_lens.py
```

---

# Purpose

`google_lens.py` is responsible for identifying a vehicle from an image using Google Lens (SerpAPI).

Instead of relying only on the AI models, this module performs a reverse image search to identify the vehicle, then returns the detected make, model, and related search results.

The output of this module is later used by `search.py` to collect trusted automotive websites.

---

# Main Class

```python
GoogleLensClient
```

Import

```python
from web_scraping.google_lens import GoogleLensClient
```

Example

```python
lens = GoogleLensClient()
```

---

# Responsibilities

- Send an image to Google Lens.
- Perform reverse image search.
- Detect vehicle name.
- Return related search results.
- Extract the most likely make and model.
- Pass the detected information to the search module.

---

# Main Settings

## SERPAPI_KEY

```python
SERPAPI_KEY
```

Purpose

Authentication key used to access the Google Lens API through SerpAPI.

---

## GOOGLE_LENS_ENDPOINT

```python
Google Lens API Endpoint
```

Purpose

The endpoint responsible for processing reverse image search requests.

---

## MAX_RESULTS

Example

```python
10
```

Purpose

Maximum number of image search results returned by Google Lens.

---

# Main Functions

---

## identify_vehicle()

```python
identify_vehicle(image)
```

Purpose

Identify the vehicle from an uploaded image.

Workflow

```
Vehicle Image

↓

Upload Image

↓

Google Lens

↓

Vehicle Detection

↓

Return Results
```

Returns

```python
dict
```

Example

```python
vehicle = lens.identify_vehicle(
    "bmw_x5.jpg"
)
```

---

## search_image()

```python
search_image(image)
```

Purpose

Send the image to Google Lens and retrieve raw search results.

Returns

```python
list
```

---

## extract_vehicle_name()

```python
extract_vehicle_name(results)
```

Purpose

Extract the most probable vehicle name from Google Lens results.

Example

Input

```
BMW X5 SUV 2024
```

Output

```python
{
    "make": "BMW",
    "model": "X5"
}
```

Returns

```python
dict
```

---

## get_best_match()

```python
get_best_match(results)
```

Purpose

Select the highest-confidence search result returned by Google Lens.

Selection Criteria

- Highest confidence
- Automotive websites
- Official vehicle title
- Relevant image source

Returns

```python
dict
```

---

# Complete Workflow

```
Vehicle Image

↓

Google Lens API

↓

Search Results

↓

Best Match

↓

Vehicle Name

↓

scraper.py

↓

search.py

↓

Continue Scraping Pipeline
```

---

# Input

Example

```python
image = "vehicle.jpg"
```

---

# Output

Example

```python
{
    "make": "BMW",
    "model": "X5",
    "title": "2024 BMW X5",
    "confidence": 0.94
}
```

---

# Used By

This module is mainly used by

- VehicleScraper
- AI Agent
- Backend Services

---

# Dependencies

Common imports

```python
requests
serpapi
json
logging
Pillow
base64
io
```

---

# Related Files

```
scraper.py
      │
      ▼
google_lens.py
      │
      ▼
search.py
      │
      ▼
requests.py
```

---

# Backend Usage

Typical usage

```python
from web_scraping.google_lens import GoogleLensClient

lens = GoogleLensClient()

vehicle = lens.identify_vehicle("car.jpg")

print(vehicle)
```

---

# Notes

- This module is only responsible for identifying the vehicle from an image.
- It does not download webpages.
- It does not parse HTML.
- It does not extract vehicle specifications.
- The detected vehicle information is forwarded to `search.py`, which starts the web search process.
- It acts as the bridge between image-based input and text-based web scraping.

---

# Role in the Project

This module is activated when the user uploads an image instead of entering a vehicle name.

Pipeline

```
User Image

↓

Google Lens

↓

Vehicle Identification

↓

Vehicle Name

↓

Google Search

↓

Web Scraping

↓

Structured Vehicle Information
```

---

# requests.py

> **File Location**

```text
web_scraping/requests.py
```

---

# Purpose

`requests.py` is responsible for downloading static web pages using HTTP requests.

It provides a lightweight and fast way to retrieve HTML content from websites that do not require JavaScript rendering.

If the page cannot be fully loaded using HTTP requests, the scraping pipeline automatically switches to `playwright.py` for browser rendering.

---

# Main Class

```python
HTTPClient
```

Import

```python
from web_scraping.requests import HTTPClient
```

Example

```python
client = HTTPClient()
```

---

# Responsibilities

- Download HTML pages.
- Handle HTTP GET requests.
- Set request headers.
- Manage request timeout.
- Retry failed requests.
- Return HTML content.
- Detect failed responses.

---

# Main Settings

## REQUEST_TIMEOUT

```python
REQUEST_TIMEOUT = 30
```

Purpose

Maximum waiting time before cancelling the request.

---

## MAX_RETRIES

```python
MAX_RETRIES = 3
```

Purpose

Number of retry attempts if a request fails.

---

## USER_AGENT

```python
Mozilla/5.0 ...
```

Purpose

Simulates a real browser to reduce the chance of being blocked by websites.

---

## DEFAULT_HEADERS

Contains common HTTP headers such as

```text
User-Agent
Accept
Accept-Language
Connection
```

Purpose

Improve compatibility with target websites.

---

# Main Functions

---

## fetch()

```python
fetch(url)
```

Purpose

Download a webpage using an HTTP GET request.

Workflow

```
URL

↓

Send Request

↓

Receive Response

↓

Return HTML
```

Returns

```python
str
```

Example

```python
html = client.fetch(
    "https://www.caranddriver.com/"
)
```

---

## get()

```python
get(url)
```

Purpose

Wrapper around the HTTP request.

Responsibilities

- Send request
- Handle timeout
- Handle retries
- Return response object

Returns

```python
Response
```

---

## validate_response()

```python
validate_response(response)
```

Purpose

Verify that the HTTP response is valid before processing.

Checks

- Status Code
- Empty Content
- HTML Availability

Returns

```python
bool
```

---

## build_headers()

```python
build_headers()
```

Purpose

Generate HTTP request headers.

Returns

```python
dict
```

---

# Complete Workflow

```
URL

↓

Build Headers

↓

HTTP GET Request

↓

Response

↓

Validate Response

↓

Return HTML

or

Raise Exception
```

---

# Input

Example

```python
url = "https://www.edmunds.com/"
```

---

# Output

Example

```python
"<html> ... </html>"
```

---

# Error Handling

Possible exceptions

```python
TimeoutError

ConnectionError

HTTPError

RequestException
```

When an error occurs

```
Retry

↓

If Failed

↓

Return None

↓

VehicleScraper

↓

Use Playwright
```

---

# Used By

This module is mainly used by

- VehicleScraper

It is **not** called directly by the frontend or backend services.

---

# Dependencies

Common imports

```python
requests
logging
time
urllib
```

---

# Related Files

```
scraper.py
      │
      ▼
requests.py
      │
      ├────────► Success
      │
      ▼
Return HTML

OR

requests Failed

↓

playwright.py
```

---

# Backend Usage

Typical usage

```python
from web_scraping.requests import HTTPClient

client = HTTPClient()

html = client.fetch(url)

print(html)
```

---

# Notes

- Optimized for static websites.
- Faster than browser automation.
- Uses significantly less memory than Playwright.
- Returns raw HTML only.
- Does not parse HTML.
- Does not extract vehicle information.
- Acts as the first stage of webpage retrieval.

---

# Role in the Project

This module is the primary downloader for web pages.

Pipeline

```
Search URLs

↓

HTTPClient

↓

HTML Content

↓

HTML Parser

↓

Vehicle Extractor
```

If the webpage cannot be loaded correctly because it relies on JavaScript:

```
HTTPClient

↓

Failed

↓

BrowserSession (playwright.py)

↓

Rendered HTML

↓

Continue Pipeline
```

---

# playwright.py

> **File Location**

```text
web_scraping/playwright.py
```

---

# Purpose

`playwright.py` is responsible for rendering dynamic web pages using a real browser.

Many modern automotive websites load their content with JavaScript, making them inaccessible through normal HTTP requests.

This module launches a browser session, waits for the page to fully render, then returns the final HTML to continue the scraping pipeline.

It acts as the fallback solution whenever `requests.py` cannot retrieve the required content.

---

# Main Class

```python
BrowserSession
```

Import

```python
from web_scraping.playwright import BrowserSession
```

Example

```python
browser = BrowserSession()
```

---

# Responsibilities

- Launch a browser.
- Open web pages.
- Execute JavaScript.
- Wait for page rendering.
- Return fully rendered HTML.
- Close browser sessions safely.
- Handle browser errors.

---

# Main Settings

## HEADLESS

```python
HEADLESS = True
```

Purpose

Run the browser without displaying the graphical interface.

---

## PAGE_TIMEOUT

```python
PAGE_TIMEOUT = 30000
```

Purpose

Maximum time to wait for the page to finish loading.

---

## WAIT_UNTIL

```python
networkidle
```

Purpose

Defines when the page is considered fully loaded.

Common values

```text
load
domcontentloaded
networkidle
```

---

## USER_AGENT

Purpose

Use a realistic browser fingerprint to reduce blocking by websites.

---

# Main Functions

---

## start_browser()

```python
start_browser()
```

Purpose

Initialize a new browser session.

Workflow

```
Start Browser

↓

Create Context

↓

Ready for Navigation
```

Returns

```python
Browser
```

---

## open_page()

```python
open_page(url)
```

Purpose

Navigate to a webpage.

Workflow

```
URL

↓

Open Browser

↓

Navigate

↓

Wait

↓

Return Page
```

Returns

```python
Page
```

---

## get_html()

```python
get_html(url)
```

Purpose

Retrieve the fully rendered HTML source.

Workflow

```
Open Page

↓

Render JavaScript

↓

Wait

↓

Return HTML
```

Returns

```python
str
```

Example

```python
html = browser.get_html(url)
```

---

## close_browser()

```python
close_browser()
```

Purpose

Close the browser and release all resources.

Returns

```python
None
```

---

# Complete Workflow

```
URL

↓

Launch Browser

↓

Navigate

↓

Execute JavaScript

↓

Wait Until Loaded

↓

Extract HTML

↓

Close Browser

↓

Return HTML
```

---

# Input

Example

```python
url = "https://www.caranddriver.com/"
```

---

# Output

Example

```python
"<html> ... rendered page ... </html>"
```

---

# Error Handling

Possible exceptions

```python
TimeoutError

NavigationError

BrowserClosedError

PlaywrightError
```

If an error occurs

```
Retry

↓

Log Error

↓

Return None
```

---

# Used By

This module is called only when:

- requests.py fails.
- The webpage depends on JavaScript.
- Dynamic content must be rendered.

Primary caller

```
VehicleScraper
```

---

# Dependencies

Common imports

```python
playwright
logging
asyncio
time
```

---

# Related Files

```
scraper.py

↓

requests.py

↓

Failed

↓

playwright.py

↓

Rendered HTML

↓

parser.py
```

---

# Backend Usage

Typical usage

```python
from web_scraping.playwright import BrowserSession

browser = BrowserSession()

html = browser.get_html(url)

print(html)
```

---

# Advantages

- Supports JavaScript-heavy websites.
- Produces fully rendered HTML.
- Handles lazy-loaded content.
- Suitable for modern automotive websites.

---

# Limitations

- Slower than HTTP requests.
- Higher CPU and memory usage.
- Requires a browser runtime.

---

# Notes

- This module does **not** extract vehicle information.
- It only returns rendered HTML.
- HTML is passed directly to `parser.py`.
- Browser sessions should always be closed after use.

---

# Role in the Project

This module is the fallback rendering engine of the Web Scraping pipeline.

Pipeline

```
Vehicle URL

↓

requests.py

↓

Success
        │
        ▼
HTML

OR

Failed

↓

playwright.py

↓

Rendered HTML

↓

parser.py

↓

extractor.py

↓

cleaner.py

↓

json_builder.py
```

---

# parser.py

> **File Location**

```text
web_scraping/parser.py
```

---

# Purpose

`parser.py` is responsible for parsing raw HTML documents into structured objects that can be easily navigated and analyzed.

Instead of working directly with HTML text, this module converts webpages into a tree structure using **BeautifulSoup**, allowing the extractor to locate vehicle specifications, titles, images, tables, and technical information.

This module does **not** extract vehicle data itself; it only prepares the HTML for the extraction stage.

---

# Main Class

```python
HTMLParser
```

Import

```python
from web_scraping.parser import HTMLParser
```

Example

```python
parser = HTMLParser()
```

---

# Responsibilities

- Parse HTML documents.
- Build BeautifulSoup objects.
- Locate important HTML elements.
- Search using CSS selectors.
- Search using HTML tags.
- Search using element attributes.
- Return structured HTML objects.
- Remove unnecessary HTML sections if needed.

---

# Main Settings

## PARSER_ENGINE

```python
html.parser
```

Purpose

Defines the HTML parsing engine used by BeautifulSoup.

Other supported parsers

```text
html.parser
lxml
html5lib
```

---

## REMOVE_SCRIPT_TAGS

```python
True
```

Purpose

Ignore JavaScript sections before extraction.

---

## REMOVE_STYLE_TAGS

```python
True
```

Purpose

Ignore CSS styles.

---

## REMOVE_COMMENTS

```python
True
```

Purpose

Ignore HTML comments.

---

# Main Functions

---

## parse()

```python
parse(html)
```

Purpose

Convert raw HTML into a BeautifulSoup object.

Workflow

```
Raw HTML

↓

BeautifulSoup

↓

Parsed HTML Object
```

Returns

```python
BeautifulSoup
```

Example

```python
soup = parser.parse(html)
```

---

## find()

```python
find(tag)
```

Purpose

Find the first matching HTML element.

Example

```python
parser.find("title")
```

Returns

```python
Tag
```

---

## find_all()

```python
find_all(tag)
```

Purpose

Retrieve all matching HTML elements.

Example

```python
parser.find_all("table")
```

Returns

```python
list[Tag]
```

---

## select()

```python
select(css_selector)
```

Purpose

Locate HTML elements using CSS selectors.

Example

```python
parser.select(".vehicle-specs")
```

Returns

```python
list[Tag]
```

---

## get_text()

```python
get_text(element)
```

Purpose

Extract clean text from an HTML element.

Example

```python
text = parser.get_text(title)
```

Returns

```python
str
```

---

## clean_html()

```python
clean_html()
```

Purpose

Remove unnecessary HTML elements before extraction.

Usually removes

```text
script

style

comments

hidden elements
```

Returns

```python
BeautifulSoup
```

---

# Complete Workflow

```
Raw HTML

↓

BeautifulSoup

↓

Clean HTML

↓

Search Elements

↓

Return Parsed Document
```

---

# Input

Example

```python
html = "<html>...</html>"
```

---

# Output

Example

```python
BeautifulSoup Object
```

---

# Used By

This module is mainly used by

- VehicleExtractor
- VehicleScraper

---

# Dependencies

Common imports

```python
bs4

BeautifulSoup

re

logging
```

---

# Related Files

```
requests.py

↓

playwright.py

↓

parser.py

↓

extractor.py
```

---

# Backend Usage

Typical usage

```python
from web_scraping.parser import HTMLParser

parser = HTMLParser()

soup = parser.parse(html)

title = parser.find("title")
```

---

# Advantages

- Fast HTML parsing.
- Supports CSS selectors.
- Supports nested HTML traversal.
- Easy integration with BeautifulSoup.

---

# Limitations

- Requires valid HTML.
- Does not execute JavaScript.
- Does not extract business logic.
- Only prepares HTML for extraction.

---

# Notes

- This module is responsible only for parsing HTML.
- It never decides which data should be extracted.
- The parsed document is passed directly to `extractor.py`.
- BeautifulSoup objects returned here are used throughout the extraction pipeline.

---

# Role in the Project

This module converts downloaded HTML into a structured document that can be processed by the extraction engine.

Pipeline

```
requests.py

↓

playwright.py

↓

parser.py

↓

BeautifulSoup Object

↓

extractor.py

↓

Vehicle Information
```

---

# extractor.py

> **File Location**

```text
web_scraping/extractor.py
```

---

# Purpose

`extractor.py` is the core data extraction engine of the Web Scraping module.

After the HTML document has been parsed by `parser.py`, this module navigates through the page and extracts meaningful vehicle information such as specifications, performance, dimensions, safety features, pricing, and images.

The extracted data is returned as a structured Python dictionary, which is later cleaned and converted into the final JSON document.

---

# Main Class

```python
VehicleExtractor
```

Import

```python
from web_scraping.extractor import VehicleExtractor
```

Example

```python
extractor = VehicleExtractor()
```

---

# Responsibilities

- Extract vehicle specifications.
- Detect vehicle make and model.
- Extract technical specifications.
- Extract engine information.
- Extract performance values.
- Extract dimensions.
- Extract fuel information.
- Extract transmission details.
- Extract safety features.
- Extract pricing information.
- Extract images.
- Return structured data.

---

# Input

The extractor receives a parsed HTML document.

Example

```python
BeautifulSoup Object
```

Output from

```python
HTMLParser.parse()
```

---

# Output

The extractor returns a structured dictionary.

Example

```python
{
    "make": "...",
    "model": "...",
    "year": "...",
    "engine": "...",
    "horsepower": "...",
    "fuel_type": "...",
    "transmission": "...",
    "price": "...",
    "dimensions": {...},
    "performance": {...}
}
```

---

# Main Functions

---

## extract()

```python
extract(soup)
```

Purpose

Main entry point of the extraction engine.

This function coordinates all extraction functions and merges their outputs into one dictionary.

Workflow

```
BeautifulSoup

↓

Extract Title

↓

Extract Specifications

↓

Extract Features

↓

Extract Performance

↓

Merge

↓

Return Dictionary
```

Returns

```python
dict
```

---

## extract_title()

```python
extract_title(soup)
```

Purpose

Extract the vehicle title.

Example

```
2024 BMW X5 xDrive40i
```

Returns

```python
str
```

---

## extract_make()

```python
extract_make(soup)
```

Purpose

Extract the manufacturer.

Example

```
BMW

Toyota

Audi

Hyundai
```

Returns

```python
str
```

---

## extract_model()

```python
extract_model(soup)
```

Purpose

Extract the vehicle model.

Example

```
X5

Corolla

A6

Elantra
```

Returns

```python
str
```

---

## extract_year()

```python
extract_year(soup)
```

Purpose

Extract production year.

Returns

```python
int
```

---

## extract_engine()

```python
extract_engine(soup)
```

Purpose

Extract engine specifications.

Possible Data

```
Engine Type

Displacement

Turbo

Cylinders
```

Returns

```python
dict
```

---

## extract_performance()

```python
extract_performance(soup)
```

Purpose

Extract vehicle performance.

Possible Data

```
Horsepower

Torque

Top Speed

Acceleration

Fuel Economy
```

Returns

```python
dict
```

---

## extract_dimensions()

```python
extract_dimensions(soup)
```

Purpose

Extract physical dimensions.

Possible Data

```
Length

Width

Height

Wheelbase

Ground Clearance
```

Returns

```python
dict
```

---

## extract_transmission()

```python
extract_transmission(soup)
```

Purpose

Extract gearbox information.

Example

```
Automatic

Manual

CVT

Dual Clutch
```

Returns

```python
str
```

---

## extract_fuel()

```python
extract_fuel(soup)
```

Purpose

Extract fuel information.

Example

```
Gasoline

Diesel

Hybrid

Electric
```

Returns

```python
dict
```

---

## extract_price()

```python
extract_price(soup)
```

Purpose

Extract MSRP or market price.

Returns

```python
str
```

---

## extract_images()

```python
extract_images(soup)
```

Purpose

Collect vehicle images from the webpage.

Returns

```python
list[str]
```

---

## extract_features()

```python
extract_features(soup)
```

Purpose

Extract available vehicle features.

Possible Features

```
ABS

Lane Assist

Adaptive Cruise Control

Apple CarPlay

Android Auto

Blind Spot Monitor
```

Returns

```python
list
```

---

## extract_specifications()

```python
extract_specifications(soup)
```

Purpose

Extract all specification tables.

Returns

```python
dict
```

---

# Complete Workflow

```
BeautifulSoup

↓

Vehicle Title

↓

Specifications

↓

Engine

↓

Performance

↓

Dimensions

↓

Safety

↓

Features

↓

Images

↓

Merge

↓

Dictionary
```

---

# Used By

This module is used by

- VehicleScraper
- DataCleaner

---

# Dependencies

Common imports

```python
BeautifulSoup

re

logging

json
```

---

# Related Files

```
parser.py

↓

extractor.py

↓

cleaner.py

↓

json_builder.py
```

---

# Backend Usage

Typical usage

```python
from web_scraping.extractor import VehicleExtractor

extractor = VehicleExtractor()

vehicle = extractor.extract(soup)
```

---

# Advantages

- Structured extraction.
- Supports multiple website layouts.
- Easy to extend.
- Independent extraction functions.
- Returns clean dictionaries.

---

# Limitations

- Depends on HTML structure.
- Different websites may require different selectors.
- Some values may be missing if the source website does not provide them.

---

# Notes

- This module does not download webpages.
- This module does not clean extracted data.
- This module focuses only on converting HTML into structured vehicle information.
- The output is passed directly to `cleaner.py` for normalization.

---

# Role in the Project

The extractor is the heart of the Web Scraping pipeline.

Pipeline

```
Search

↓

Requests / Playwright

↓

Parser

↓

Extractor

↓

Vehicle Information

↓

Cleaner

↓

JSON Builder

↓

MongoDB
```

---

# cleaner.py

> **File Location**

```text
web_scraping/cleaner.py
```

---

# Purpose

`cleaner.py` is responsible for cleaning, normalizing, and validating the extracted vehicle data before it is converted into the final JSON document.

After `extractor.py` collects raw information from multiple websites, the extracted values may contain duplicated fields, inconsistent formats, missing values, HTML artifacts, or different measurement units.

This module processes all extracted information and converts it into a consistent and reliable format for the Backend, MongoDB, and the RAG system.

---

# Main Class

```python
DataCleaner
```

Import

```python
from web_scraping.cleaner import DataCleaner
```

Example

```python
cleaner = DataCleaner()
```

---

# Responsibilities

- Remove duplicated values.
- Normalize text formatting.
- Handle missing values.
- Remove empty fields.
- Standardize units.
- Remove HTML artifacts.
- Validate extracted values.
- Prepare data for JSON serialization.

---

# Input

The cleaner receives a dictionary returned by `VehicleExtractor`.

Example

```python
vehicle_data = {
    "make": " BMW ",
    "model": "X5",
    "horsepower": "375 hp",
    "price": "",
    "engine": None
}
```

---

# Output

The cleaner returns a normalized dictionary.

Example

```python
{
    "make": "BMW",
    "model": "X5",
    "horsepower": 375,
    "price": None,
    "engine": None
}
```

---

# Main Functions

---

## clean()

```python
clean(vehicle_data)
```

Purpose

Main entry point of the cleaning module.

This function applies all cleaning operations before returning the final dictionary.

Workflow

```
Raw Dictionary

↓

Normalize Text

↓

Remove Empty Values

↓

Remove Duplicates

↓

Validate Fields

↓

Return Clean Dictionary
```

Returns

```python
dict
```

---

## normalize_text()

```python
normalize_text(value)
```

Purpose

Normalize text values.

Examples

Before

```
 BMW
```

After

```
BMW
```

Returns

```python
str
```

---

## remove_empty_values()

```python
remove_empty_values(data)
```

Purpose

Remove

- Empty strings
- Null values
- Unnecessary whitespace

Returns

```python
dict
```

---

## remove_duplicates()

```python
remove_duplicates(data)
```

Purpose

Remove duplicated information collected from multiple websites.

Example

Before

```
Engine
Engine
Engine
```

After

```
Engine
```

Returns

```python
dict
```

---

## normalize_units()

```python
normalize_units(data)
```

Purpose

Convert units into a unified format.

Examples

```
375 hp

↓

375
```

```
185 km/h

↓

185
```

```
4,970 mm

↓

4970
```

Returns

```python
dict
```

---

## validate_data()

```python
validate_data(data)
```

Purpose

Validate extracted values before saving.

Checks

- Missing fields
- Invalid numbers
- Invalid strings
- Incorrect data types

Returns

```python
dict
```

---

## merge_duplicate_fields()

```python
merge_duplicate_fields(data)
```

Purpose

Merge information collected from different websites into one consistent value.

Returns

```python
dict
```

---

# Complete Workflow

```
Raw Vehicle Data

↓

Normalize Text

↓

Remove Empty Values

↓

Remove Duplicate Values

↓

Normalize Units

↓

Validate Data

↓

Return Clean Dictionary
```

---

# Used By

This module is mainly used by

- VehicleScraper
- VehicleDocumentBuilder

---

# Dependencies

Common imports

```python
re

logging

copy

json
```

---

# Related Files

```
extractor.py

↓

cleaner.py

↓

json_builder.py
```

---

# Backend Usage

Typical usage

```python
from web_scraping.cleaner import DataCleaner

cleaner = DataCleaner()

clean_data = cleaner.clean(vehicle_data)
```

---

# Advantages

- Produces consistent data.
- Removes duplicated values.
- Improves data quality.
- Simplifies downstream processing.
- Ensures reliable MongoDB documents.

---

# Limitations

- Cannot recover missing information.
- Depends on the quality of extracted data.
- Only processes existing values.

---

# Notes

- This module never downloads webpages.
- This module never parses HTML.
- This module never extracts new information.
- It only improves the quality of already extracted data.
- The cleaned dictionary is passed directly to `json_builder.py`.

---

# Role in the Project

The cleaner guarantees that all vehicle information follows a unified format before being stored or sent to the AI system.

Pipeline

```
Requests / Playwright

↓

Parser

↓

Extractor

↓

Cleaner

↓

Normalized Vehicle Data

↓

JSON Builder

↓

MongoDB

↓

Backend
```

---

# json_builder.py

> **File Location**

```text
web_scraping/json_builder.py
```

---

# Purpose

`json_builder.py` is the final stage of the Web Scraping pipeline.

Its responsibility is to convert the cleaned vehicle information into a unified JSON structure that can be stored in MongoDB, indexed for the RAG system, or returned directly to the Backend API.

This module ensures that every scraped vehicle follows the same schema regardless of the source website.

---

# Main Class

```python
VehicleDocumentBuilder
```

Import

```python
from web_scraping.json_builder import VehicleDocumentBuilder
```

Example

```python
builder = VehicleDocumentBuilder()
```

---

# Responsibilities

- Build standardized JSON documents.
- Merge all cleaned vehicle information.
- Organize vehicle specifications.
- Attach metadata.
- Store source URLs.
- Prepare MongoDB documents.
- Prepare RAG-ready documents.

---

# Input

The builder receives cleaned data from `DataCleaner`.

Example

```python
clean_vehicle_data = {
    "make": "BMW",
    "model": "X5",
    "year": 2024,
    "horsepower": 375,
    "fuel_type": "Gasoline"
}
```

---

# Output

Example

```python
{
    "vehicle": {
        ...
    },

    "specifications": {
        ...
    },

    "performance": {
        ...
    },

    "metadata": {
        ...
    }
}
```

---

# Main Functions

---

## build()

```python
build(vehicle_data)
```

Purpose

Main function responsible for building the final vehicle document.

Workflow

```
Clean Vehicle Data

↓

Organize Sections

↓

Add Metadata

↓

Generate JSON

↓

Return Final Document
```

Returns

```python
dict
```

---

## build_vehicle()

```python
build_vehicle(data)
```

Purpose

Create the main vehicle section.

Example

```json
{
    "make": "BMW",
    "model": "X5",
    "year": 2024
}
```

Returns

```python
dict
```

---

## build_specifications()

```python
build_specifications(data)
```

Purpose

Build the specifications section.

Example

```json
{
    "engine": "...",
    "transmission": "...",
    "fuel_type": "..."
}
```

Returns

```python
dict
```

---

## build_performance()

```python
build_performance(data)
```

Purpose

Create the vehicle performance section.

Example

```json
{
    "horsepower": 375,
    "torque": "...",
    "top_speed": "..."
}
```

Returns

```python
dict
```

---

## build_dimensions()

```python
build_dimensions(data)
```

Purpose

Store vehicle dimensions.

Example

```json
{
    "length": "...",
    "width": "...",
    "height": "..."
}
```

Returns

```python
dict
```

---

## build_features()

```python
build_features(data)
```

Purpose

Store vehicle features.

Example

```json
[
    "ABS",
    "Apple CarPlay",
    "Blind Spot Monitor"
]
```

Returns

```python
list
```

---

## build_metadata()

```python
build_metadata(data)
```

Purpose

Generate metadata about the scraping process.

Metadata may include

- Source websites
- Scraping date
- Number of pages processed
- Data quality score
- Confidence score

Returns

```python
dict
```

---

## build_sources()

```python
build_sources(urls)
```

Purpose

Store all source URLs used to build the final document.

Example

```json
[
    "https://www.caranddriver.com/...",
    "https://www.edmunds.com/..."
]
```

Returns

```python
list
```

---

# Final Document Structure

```
Vehicle

│

├── Basic Information

├── Specifications

├── Performance

├── Dimensions

├── Features

├── Images

├── Sources

└── Metadata
```

---

# Complete Workflow

```
Clean Vehicle Data

↓

Vehicle Section

↓

Specifications

↓

Performance

↓

Dimensions

↓

Features

↓

Metadata

↓

Source URLs

↓

Final JSON Document
```

---

# Used By

This module is mainly used by

- VehicleScraper
- Backend
- MongoDB
- RAG Pipeline
- AI Agent

---

# Dependencies

Common imports

```python
json

datetime

uuid

logging
```

---

# Related Files

```
extractor.py

↓

cleaner.py

↓

json_builder.py

↓

Backend

↓

MongoDB

↓

RAG
```

---

# Backend Usage

Typical usage

```python
from web_scraping.json_builder import VehicleDocumentBuilder

builder = VehicleDocumentBuilder()

document = builder.build(clean_data)
```

---

# Advantages

- Standardized JSON format.
- Easy MongoDB integration.
- RAG-ready structure.
- Consistent schema across all websites.
- Simplifies Backend processing.

---

# Limitations

- Depends on cleaned data.
- Does not perform extraction.
- Does not modify values.
- Only organizes and structures information.

---

# Notes

- This module is the final stage of the Web Scraping pipeline.
- It does not scrape websites.
- It does not parse HTML.
- It does not clean data.
- It only converts structured information into a unified document.
- The generated JSON can be stored directly in MongoDB or indexed by the RAG system.

---

# Role in the Project

This module acts as the bridge between Web Scraping and the rest of the project.

Pipeline

```
Search

↓

Requests / Playwright

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

↓

RAG

↓

Backend

↓

Frontend
```

---

# Complete Web Scraping Pipeline

```
User Request

↓

scraper.py

↓

search.py

↓

google_lens.py (optional)

↓

requests.py

↓

playwright.py (fallback)

↓

parser.py

↓

extractor.py

↓

cleaner.py

↓

json_builder.py

↓

MongoDB

↓

RAG

↓

Backend Response

↓

Frontend
```

---

# Summary

| File            | Responsibility                            |
| --------------- | ----------------------------------------- |
| scraper.py      | Main coordinator of the scraping pipeline |
| search.py       | Search trusted automotive websites        |
| google_lens.py  | Identify vehicles from images             |
| requests.py     | Download static HTML pages                |
| playwright.py   | Render JavaScript pages                   |
| parser.py       | Parse HTML into structured objects        |
| extractor.py    | Extract vehicle specifications            |
| cleaner.py      | Normalize and validate extracted data     |
| json_builder.py | Build the final JSON document             |
