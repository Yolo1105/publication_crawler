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

### Parameters

- **query**: The search query to fetch results for (default is "machine learning").
- **base_url**: The base URL of the website to fetch results from (default is "https://www.microsoft.com/en-us/research/project/academic/").
- **query_param**: The query parameter name used in the search URL (default is 'q').

### Logging

The script logs activities and errors to a file with a date-based filename (e.g., `2024-05-23.log`). The log file is created in the same directory as the script.

### CSV Output

The search results are saved to a CSV file with a date-based filename (e.g., `2024-05-23_results.csv`). The CSV file is created in the same directory as the script.

## Functions

### scrape_proxies()

Scrapes proxies from a free proxy listing website and returns a list of proxies.

### validate_proxy(proxy)

Validates a proxy by making a request to Microsoft Academic and returns `True` if the proxy is functional.

### get_valid_proxies(proxies)

Returns a list of valid proxies by checking each one concurrently.

### get_random_proxy(valid_proxies)

Selects a random proxy from the list of valid proxies.

### fetch_search_results(base_url, query, query_param, total_pages, start_page, valid_proxies)

Fetches search results from the specified website for a given query starting from a specific page.

### fetch_page_results(base_url, query, query_param, page, valid_proxies)

Fetches search results from a single page of the specified website.

### parse_results(html)

Parses HTML content to extract search results from Microsoft Academic.

### write_to_csv(results_data)

Writes search results to a CSV file.

### save_progress(base_url, query, query_param, total_pages, current_page, results_data)

Saves the current progress to a JSON file.

### load_progress()

Loads progress from a JSON file if it exists.

### get_user_input()

Gets user input for resuming or starting a new search.

### get_page_input()

Gets user input for starting page and total pages.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
