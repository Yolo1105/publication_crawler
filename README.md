# Web Scraper with Proxy Support

This project is a web scraper designed to fetch search results from a specified website using proxies. It is built using Python and leverages libraries such as `requests`, `BeautifulSoup`, `concurrent.futures`, and `fake_useragent` for efficient and anonymous web scraping.

## Features

- Scrapes proxies from a free proxy listing website.
- Validates proxies to ensure they are functional.
- Fetches search results using valid proxies to avoid IP blocking.
- Supports multi-threading for efficient scraping.
- Logs activities and errors to a file with a date-based filename.
- Allows resuming from the last saved page.
- Saves search results to a CSV file.

## Setup

### Prerequisites

- Python 3.6 or higher

### Required Packages

Install the necessary Python packages using the following command:

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

### Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/web-scraper-with-proxy-support.git
    cd web-scraper-with-proxy-support
    ```

2. Install the required Python packages:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Running the Script

1. Run the script:

    ```sh
    python scraper.py
    ```

2. Follow the prompts to either resume from the last saved page or start a new search.

### Introduction

This script is designed to scrape search results from Microsoft Academic using proxies to avoid getting banned. It scrapes a list of free proxies, validates them, and uses valid proxies to make requests. The search results are parsed from the HTML content and saved into a CSV file. The script also supports resuming from the last saved page in case of interruptions.

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

### 3. Data Storage in CSV

- **Writing Results to CSV:**
  - The `write_to_csv(results_data)` function writes the extracted search results to a CSV file. The CSV file is named with the current date (e.g., `2024-05-23_results.csv`). The function checks if the file already exists and appends new results to it. If the file does not exist, it creates a new one and writes the results.
  
- **Saving and Loading Progress:**
  - The `save_progress(base_url, query, query_param, total_pages, current_page, results_data)` function saves the current progress to a JSON file (`progress.json`). This allows the script to resume from where it left off in case of interruptions.
  - The `load_progress()` function loads the progress from the JSON file if it exists. This enables the script to continue fetching results from the last saved page.

### Main Function

- The `main()` function orchestrates the entire scraping process. It manages loading progress, getting user input, fetching search results, and writing results to CSV. It ensures that the script can resume from the last saved page or start a new search based on user input.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
```

This README now includes a brief introduction on how to run the code, lists all necessary packages in a `requirements.txt` format, and provides detailed sections on how the proxy and fake IP usage works, how the data is crawled, and how the data is stored in a CSV file.
