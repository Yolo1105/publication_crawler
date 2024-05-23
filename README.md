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
- Required Python packages (install using the requirements.txt file)

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

1. Run the script:

    ```sh
    python scraper.py
    ```

2. Follow the prompts to resume from the last saved page or start a new search.

## Working Process and Logic

### 1. Logging Setup

- The script starts by setting up logging to a file named with the current date (e.g., `2024-05-23.log`).
- If the log file does not exist, it creates a new one.

### 2. Generate a Random User Agent

- The script uses the `fake_useragent` library to generate a random user agent for each request to avoid detection.

### 3. Scrape Proxies

- The `scrape_proxies()` function scrapes a list of free proxies from a specified proxy listing website (`https://www.sslproxies.org/`).
- It extracts proxy IP and port from the table on the website and returns a list of proxies.

### 4. Validate Proxies

- The `validate_proxy(proxy)` function checks if a proxy is functional by making a request to Microsoft Academic.
- It returns `True` if the proxy is valid, otherwise logs errors and returns `False`.

### 5. Get Valid Proxies

- The `get_valid_proxies(proxies)` function validates a list of proxies concurrently using `ThreadPoolExecutor`.
- It returns a list of valid proxies.

### 6. Fetch Search Results

- The `fetch_search_results(base_url, query, query_param, total_pages, start_page, valid_proxies)` function manages fetching search results.
- It uses valid proxies to make requests and fetch search results for the specified query.
- If no valid proxies are available, it scrapes and validates new proxies.

### 7. Fetch Page Results

- The `fetch_page_results(base_url, query, query_param, page, valid_proxies)` function fetches search results from a single page.
- It selects a random proxy from the list of valid proxies and makes a request to fetch the HTML content.
- If the request fails, it retries up to 5 times with different proxies.

### 8. Parse Results

- The `parse_results(html)` function parses the HTML content to extract search results.
- It looks for specific HTML elements that contain the search results and extracts the title and link for each result.

### 9. Write Results to CSV

- The `write_to_csv(results_data)` function writes the extracted search results to a CSV file.
- The CSV file is named with the current date (e.g., `2024-05-23_results.csv`).

### 10. Save and Load Progress

- The `save_progress(base_url, query, query_param, total_pages, current_page, results_data)` function saves the current progress to a JSON file (`progress.json`).
- The `load_progress()` function loads the progress from the JSON file if it exists.

### 11. Get User Input

- The `get_user_input()` function prompts the user to resume from the last saved page or start a new search.
- The `get_page_input()` function prompts the user to enter the starting page and total number of pages to crawl.

### 12. Main Function

- The `main()` function orchestrates the entire scraping process.
- It manages loading progress, getting user input, fetching search results, and writing results to CSV.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
