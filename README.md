# Web Scraper with Proxy Support

This sophisticated web scraper is designed to fetch search results from specified websites using a robust proxy rotation mechanism. Built using Python, it leverages powerful libraries such as `requests`, `BeautifulSoup`, `concurrent.futures`, and `fake_useragent` to perform efficient and stealthy web scraping.

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

You need to install the following Python packages to run the scraper. You can install them using the `requirements.txt` file or individually as listed below.

#### Using `requirements.txt`

Install all required packages with a single command:

```sh
pip install -r requirements.txt
```

**Contents of `requirements.txt`:**

```plaintext
requests
beautifulsoup4
fake_useragent
tqdm
```

#### Installing Packages Individually

If you prefer to install the packages individually, you can do so using the following commands:

```sh
pip install requests
pip install beautifulsoup4
pip install fake_useragent
pip install tqdm
```

### Installation

Clone the repository and install the required packages:

```sh
git clone https://github.com/yourusername/web-scraper-with-proxy-support.git
cd web-scraper-with-proxy-support
pip install -r requirements.txt
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

## Data Files

### `results.csv`

The `results.csv` file is used to store the search results crawled during a single run of the script. Each run of the scraper generates a new `results.csv` file with a date-based filename, such as `2024-05-23_results.csv`.

### `crawling_results.csv`

The `crawling_results.csv` file is used to accumulate all the data crawled so far. This file is continuously appended with new results from each run, providing a comprehensive record of all scraped data.

### Log File

A log file is generated for each run of the scraper, named with the current date (e.g., `2024-05-23.log`). This log file tracks real-time crawling results, including activities, errors, and proxy validation outcomes. It is useful for debugging and monitoring the scraping process.

## Ongoing Development

The current version of the web scraper is tailored for specific search engines for publications. The following modules are available for use:

- `google_crawler.py`
- `IEEE_Xplore.py`
- `microsoft_academic_crawler.py`
- `semantic_scholar.py`
- `google_scholar_crawler.py`

These modules can be used to crawl search results from the respective platforms. However, a more generalized crawler is still in development to support a wider range of websites and use cases.

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

### Main Function

- The `main()` function orchestrates the entire scraping process. It manages loading progress, getting user input, fetching search results, and writing results to CSV. It ensures that the script can resume from the last saved page or start a new search based on user input.
