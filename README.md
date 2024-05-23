# Web Scraper with Proxy Support

This web scraper is designed to fetch search results from specified websites using a robust proxy rotation mechanism. Built using Python, it leverages powerful libraries such as `requests`, `BeautifulSoup`, `concurrent.futures`, and `fake_useragent` to perform efficient and stealthy web scraping.

## Introduction

This project is used for crawling papers that acknowledged the use of NYU HPC Greene. Specifically, it aims to find publications that include the statement: "This work was supported in part through the NYU IT High Performance Computing resources, services, and staff expertise."

## Features

- Automatically scrapes and validates proxies from free proxy listing websites.
- Implements intelligent proxy rotation to minimize the risk of IP blocking.
- Employs multi-threading to enhance scraping efficiency.
- Detailed logging of activities and errors, with logs saved in date-based filenames.
- Supports resuming scraping tasks from the last saved checkpoint.
- Outputs scraped data into a well-structured CSV file.

## Setup

### Prerequisites

Ensure you have Python 3.6 or higher installed on your system.

### Required Packages
```sh
pip install requests
pip install beautifulsoup4
pip install fake_useragent
pip install tqdm
```

## Usage

### Running the Script

To start the scraper:

```sh
python scraper.py
```

Follow the on-screen prompts to resume from a previously saved page or initiate a new search.

### Anti-Detection Strategies

The scraper employs several strategies to avoid detection and simulate human browsing behavior:

- **Proxy Rotation:** Utilizes a frequently updated list of free proxies, testing each for functionality.
- **Random User-Agents:** Uses the `fake_useragent` library to generate diverse user-agent strings for each request.
- **Adaptive Request Timing:** Adjusts the timing between requests to mimic natural browsing speeds.

### Data Crawling Process

1. **Scraping Proxies:** Retrieves proxies from `https://www.sslproxies.org/`, validating each one for functionality.
2. **Fetching and Parsing Results:** Constructs queries, fetches search results, and parses HTML content using BeautifulSoup to navigate complex page structures and extract data.

### Introduction to BeautifulSoup

BeautifulSoup is a crucial Python library for parsing HTML and XML documents. It simplifies web scraping by providing tools to navigate and search the parse tree easily. Key features include handling multiple parsers like lxml and html5lib, searching by tags, attributes, and text, and processing poorly formatted HTML.

### Data Management

- **CSV Storage:** Systematically stores extracted data in CSV files, facilitating easy analysis.
- **Progress Tracking:** Saves the current state to a JSON file, allowing the scraper to resume operations after interruptions.

### Main Function

The `main()` function orchestrates the entire scraping operation, managing proxy updates, user interactions, data retrieval, and storage. It is designed to manage fetching search results for specific queries and ensures seamless operation even after interruptions.

### Logging and Error Management

Detailed logging is configured to capture all operational activities. The logs are stored with date-based filenames, helping in troubleshooting and ensuring transparency in the scraping process.

### Proxy and User Agent Management

- **Proxy Management:** The script dynamically manages proxies by scraping, validating, and rotating them to maintain uninterrupted access and avoid detection.
- **User Agent Rotation:** Random user agents are generated for each request to mimic diverse browsing patterns.

## Ongoing Development

The current version of the web scraper is tailored for specific search engines for publications. The following modules are available for use:

- `google_crawler.py`
- `IEEE_Xplore.py`
- `microsoft_academic_crawler.py`
- `semantic_scholar.py`
- `google_scholar_crawler.py`

These modules can be used to crawl search results from the respective platforms. However, a more generalized crawler is still in development to support a wider range of websites and use cases.

## Main Logic for Different Publication Search Engines

Each publication search engine requires a specific approach for crawling data. Here are the main components:

### Base URL

Each module is configured with a base URL specific to the search engine. This base URL is used to construct the search query URLs.

- **Google Scholar:** `https://scholar.google.com/scholar`
- **IEEE Xplore:** `https://ieeexplore.ieee.org/search/searchresult.jsp`
- **Microsoft Academic:** `https://academic.microsoft.com/search`
- **Semantic Scholar:** `https://www.semanticscholar.org/search`
- **Google:** `https://www.google.com/search`

### Proxy Validation

To avoid IP blocking, proxies are validated before use. The validation process involves:

1. **Scraping Proxies:** Proxies are scraped from free proxy listing websites like `https://www.sslproxies.org/`.
2. **Testing Proxies:** Each proxy is tested by making a request to the respective search engine. If the request is successful, the proxy is considered valid.
3. **Rotating Proxies:** Valid proxies are rotated for each request to distribute the load and minimize the risk of detection.

### Parsing Logic

The parsing logic varies for each search engine, as the HTML structure and elements differ. Here’s how the parsing is generally done:

- **Google Scholar:**
  - Results are contained in `div` elements with class `gs_r gs_or gs_scl`.
  - Title is extracted from `h3` elements with class `gs_rt`.
  - Links are found within `a` tags inside the `h3` elements.

- **IEEE Xplore:**
  - Results are within `div` elements with class `List-results-items`.
  - Title and links are extracted from `a` tags within these `div` elements.

- **Microsoft Academic:**
  - Results are in `li` elements with class `paper`.
  - Title and links are extracted from `h2` elements and their child `a` tags.

- **Semantic Scholar:**
  - Results are within `div` elements with class `search-result`.
  - Title and links are extracted from `a` tags within these `div` elements.

- **Google:**
  - Results are in `div` elements with class `g`.
  - Title and links are found within `h3` elements and their child `a` tags.

## How It Works

### 1. Proxy and Fake IP Usage

- **Scraping Proxies:** 
  - The `scrape_proxies()` function scrapes a list of free proxies from a proxy listing website (`https://www.sslproxies.org/`). It extracts proxy IP and port from the website and returns a list of proxies.
  
- **Validating Proxies:**
  - The `validate_proxy(proxy)` function checks if a proxy is functional by making a request to Microsoft Academic. If the request is successful (returns status code 200), the proxy is considered valid. This helps in ensuring that only functional proxies are used.
  
- **Generating Random User Agents:**
  - The script uses the `fake_useragent` library to generate random user agents for each request. This helps in avoiding detection by mimicking requests from different browsers and devices.
  
- **Using Valid Proxies:**
  - The `get_valid_proxies(proxies)` function validates a list of proxies concurrently using `ThreadPoolExecutor`. It returns a list of valid proxies that are used for making requests to avoid IP blocking.
  
- **Selecting a Random Proxy:**
  - The `get_random_proxy(valid_proxies)` function selects a random proxy from the list of valid proxies. This random selection helps in distributing the requests across different proxies, reducing the risk of getting banned.

### 2. Data Crawling Process

- **Fetching Search Results:**
  - The `fetch_search_results(base_url, query, query_param, total_pages, start_page, valid_proxies)` function manages fetching search results using the specified query. It leverages valid proxies to make requests and fetch search results for the given query. If no valid proxies are available, it scrapes and validates new proxies.
  
- **Fetching Page Results:**
  - The `fetch_page_results(base_url, query, query_param, page, valid_proxies)` function fetches search results from a single page. It constructs the URL with the query parameters, selects a random proxy, and makes a request to fetch the HTML content of the page. If the request fails, it retries up to 5 times with different proxies.

- **Parsing Results:**
  - The `parse_results(html)` function parses the HTML content to extract search results. It uses BeautifulSoup to find specific HTML elements containing the search results and extracts relevant information (title and link) for each result.

### Data Storage in CSV

- **Writing Results to CSV:**
  - The `write_to_csv(results_data)` function writes the extracted search results to a CSV file. The CSV file is named with the current date (e.g., `2024-05-23_results.csv`). The function checks if the file already exists and appends new results to it. If the file does not exist, it creates a new one and writes the results.
  
- **Saving and Loading Progress:**
  - The `save_progress(base_url, query, query_param, total_pages, current_page, results_data)` function saves the current progress to a JSON file (`progress.json`). This allows the script to resume from where it left off in case of interruptions.
  - The `load_progress()` function loads the progress from the JSON file if it exists. This enables the script to continue fetching results from the last saved page.
