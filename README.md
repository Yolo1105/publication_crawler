# Publication Crawler with Proxy Support and Task Scheduler Automation

## Overview

This project automates the execution of a Python script at a specific time period using Windows Task Scheduler. The script scrapes publication data, checks for duplicates, updates a CSV file, and automatically commits and pushes the changes to a GitHub repository. If the computer is off at the scheduled time, the program will run when the computer is turned on. A window will pop up upon completion of the process, and a log will be created to confirm successful execution.

## Features

- **Scheduled Execution**: Automatically start the program at a specified time using Windows Task Scheduler.
- **Execution on Boot**: If the computer is off at the scheduled time, the program will run when the computer is turned on.
- **Data Scraping**: Scrape data from specified websites using a robust proxy rotation mechanism and save it to a CSV file.
- **Duplicate Check**: Ensure no duplicate entries are added to the CSV file.
- **GitHub Integration**: Automatically commit and push updates to a GitHub repository.
- **Completion Notification**: Display a pop-up window when the process is completed.
- **Logging**: Log the execution status and any errors encountered during the process.
- **Proxy Rotation**: Utilizes a frequently updated list of free proxies, testing each for functionality.
- **Random User-Agents**: Uses the `fake_useragent` library to generate diverse user-agent strings for each request.
- **Adaptive Request Timing**: Adjusts the timing between requests to mimic natural browsing speeds.
- **Multi-threading**: Enhances scraping efficiency with multi-threading.
- **Progress Tracking**: Supports resuming scraping tasks from the last saved checkpoint.
- **Detailed Logging**: Logs activities and errors, with logs saved in date-based filenames.

## Prerequisites

- Windows OS
- Python 3.x
- Git
- Required Python packages (listed in `requirements.txt`)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Install Python Packages

```bash
pip install -r requirements.txt
```

### 3. Configure Task Scheduler

#### Create a Task

1. **Open Task Scheduler:**

   ![Open Task Scheduler](C:\Users\mohan\OneDrive\Desktop\pictures\1.png)

2. **Click on "Create Basic Task":**

   ![Create Basic Task](C:\Users\mohan\OneDrive\Desktop\pictures\2.png)

3. **Name your task (e.g., "Run Publication Crawler"):**

   ![Name Task](C:\Users\mohan\OneDrive\Desktop\pictures\3.png)

4. **Set the trigger to your desired schedule (daily, weekly, etc.):**

   ![Set Trigger](C:\Users\mohan\OneDrive\Desktop\pictures\4.png)

5. **Set the action to "Start a program" and browse to your Python executable (e.g., `python.exe`):**

   ![Set Action](C:\Users\mohan\OneDrive\Desktop\pictures\5.png)

6. **Add arguments:**

   ```bash
   path\to\your\script.py
   ![Set Action](C:\Users\mohan\OneDrive\Desktop\pictures\6.png)

#### Configure Additional Settings

1. Go to the "Conditions" tab.
   - Check "Start the task only if the computer is on AC power".
   - Uncheck "Stop if the computer switches to battery power".
2. Go to the "Settings" tab.
   - Check "Allow task to be run on demand".
   - Check "Run task as soon as possible after a scheduled start is missed".
   - Check "If the task fails, restart every 1 minute".
   - Set "Attempt to restart up to" to 3 times.

### 4. Script Details

Ensure your script includes the following functionalities:

- **Scraping Data**: Logic to scrape data and save it to a CSV file.
- **Duplicate Check**: Implement a function to check for duplicates before adding new data to the CSV file.
- **GitHub Commit and Push**: Use `gitpython` or a subprocess call to commit and push changes to the repository.
- **Completion Notification**: Use a library like `tkinter` to display a pop-up window upon completion.
- **Logging**: Write logs to a file indicating the success or failure of the execution.

### 5. Logging

The script will create a `log.txt` file in the specified log directory, where it will log the execution time and status.

### 6. GitHub Repository

Ensure your GitHub repository is set up and you have configured your credentials to allow pushing from the script. Update the repository URL in the script if necessary.

### 7. Testing

Test the script manually before setting up the Task Scheduler to ensure everything works as expected.

## Publication Crawler Details

### Anti-Detection Strategies

The scraper employs several strategies to avoid detection and simulate human browsing behavior:

- **Proxy Rotation**: Utilizes a frequently updated list of free proxies, testing each for functionality.
- **Random User-Agents**: Uses the `fake_useragent` library to generate diverse user-agent strings for each request.
- **Adaptive Request Timing**: Adjusts the timing between requests to mimic natural browsing speeds.

### Data Crawling Process

1. **Scraping Proxies**: Retrieves proxies from `https://www.sslproxies.org/`, validating each one for functionality.
2. **Fetching and Parsing Results**: Constructs queries, fetches search results, and parses HTML content using BeautifulSoup to navigate complex page structures and extract data.

### Data Management

- **CSV Storage**: Systematically stores extracted data in CSV files, facilitating easy analysis.
- **Progress Tracking**: Saves the current state to a JSON file, allowing the scraper to resume operations after interruptions.

### Main Function

The `main()` function orchestrates the entire scraping operation, managing proxy updates, user interactions, data retrieval, and storage. It is designed to manage fetching search results for specific queries and ensures seamless operation even after interruptions.

### Logging and Error Management

Detailed logging is configured to capture all operational activities. The logs are stored with date-based filenames, helping in troubleshooting and ensuring transparency in the scraping process.

### Proxy and User Agent Management

- **Proxy Management**: The script dynamically manages proxies by scraping, validating, and rotating them to maintain uninterrupted access and avoid detection.
- **User Agent Rotation**: Random user agents are generated for each request to mimic diverse browsing patterns.

### Ongoing Development

The current version of the web scraper is tailored for specific search engines for publications. The following modules are available for use:

- `google_crawler.py`
- `IEEE_Xplore.py`
- `microsoft_academic_crawler.py`
- `semantic_scholar.py`
- `google_scholar_crawler.py`

These modules can be used to crawl search results from the respective platforms. However, a more generalized crawler is still in development to support a wider range of websites and use cases.

### Main Logic for Different Publication Search Engines

Each publication search engine requires a specific approach for crawling data. Here are the main components:

### Base URL

Each module is configured with a base URL specific to the search engine. This base URL is used to construct the search query URLs.

- **Google Scholar**: `https://scholar.google.com/scholar`
- **IEEE Xplore**: `https://ieeexplore.ieee.org/search/searchresult.jsp`
- **Microsoft Academic**: `https://academic.microsoft.com/search`
- **Semantic Scholar**: `https://www.semanticscholar.org/search`
- **Google**: `https://www.google.com/search`

### Proxy Validation

To avoid IP blocking, proxies are validated before use. The validation process involves:

1. **Scraping Proxies**: Proxies are scraped from free proxy listing websites like `https://www.sslproxies.org/`.
2. **Testing Proxies**: Each proxy is tested by making a request to the respective search engine. If the request is successful, the proxy is considered valid.
3. **Rotating Proxies**: Valid proxies are rotated for each request to distribute the load and minimize the risk of detection.

### Parsing Logic

The parsing logic varies for each search engine, as the HTML structure and elements differ. Here’s how the parsing is generally done:

- **Google Scholar**:
  - Results are contained in `div` elements with class `gs_r gs_or gs_scl`.
  - Title is extracted from `h3` elements with class `gs_rt`.
  - Links are found within `a` tags inside the `h3` elements.

- **IEEE Xplore**:
  - Results are within `div` elements with class `List-results-items`.
  - Title and links are extracted from `a` tags within these `div` elements.

- **Microsoft Academic**:
  - Results are in `li` elements with class `paper`.
  - Title and links are extracted from `h2` elements and their child `a` tags.

- **Semantic Scholar**:
  - Results are within `div` elements with class `search-result`.
  - Title and links are extracted from `a` tags within these `div` elements.

- **Google**:
  - Results are in `div` elements with class `g`.
  - Title and links are found within `h3` elements and their child `a` tags.

## How It Works

### 1. Proxy and Fake IP Usage

- **Scraping Proxies**: 
  - The `scrape_proxies()` function scrapes a list of free proxies from a proxy listing website (`https://www.sslproxies.org/`). It extracts proxy IP and port from the website and returns a list of proxies.
  
- **Validating Proxies**:
  - The `validate_proxy(proxy)` function checks if a proxy is functional by making a request to Microsoft Academic. If the request is successful (returns status code 200), the proxy is considered valid. This helps in ensuring that only functional proxies are used.
  
- **Generating Random User Agents**:
  - The script uses the `fake_useragent` library to generate random user agents for each request. This helps in avoiding detection by

 mimicking requests from different browsers and devices.
  
- **Using Valid Proxies**:
  - The `get_valid_proxies(proxies)` function validates a list of proxies concurrently using `ThreadPoolExecutor`. It returns a list of valid proxies that are used for making requests to avoid IP blocking.
  
- **Selecting a Random Proxy**:
  - The `get_random_proxy(valid_proxies)` function selects a random proxy from the list of valid proxies. This random selection helps in distributing the requests across different proxies, reducing the risk of getting banned.

### 2. Data Crawling Process

- **Fetching Search Results**:
  - The `fetch_search_results(base_url, query, query_param, total_pages, start_page, valid_proxies)` function manages fetching search results using the specified query. It leverages valid proxies to make requests and fetch search results for the given query. If no valid proxies are available, it scrapes and validates new proxies.
  
- **Fetching Page Results**:
  - The `fetch_page_results(base_url, query, query_param, page, valid_proxies)` function fetches search results from a single page. It constructs the URL with the query parameters, selects a random proxy, and makes a request to fetch the HTML content of the page. If the request fails, it retries up to 5 times with different proxies.

- **Parsing Results**:
  - The `parse_results(html)` function parses the HTML content to extract search results. It uses BeautifulSoup to find specific HTML elements containing the search results and extracts relevant information (title and link) for each result.

### Data Storage in CSV

- **Writing Results to CSV**:
  - The `write_to_csv(results_data)` function writes the extracted search results to a CSV file. The CSV file is named with the current date (e.g., `2024-05-23_results.csv`). The function checks if the file already exists and appends new results to it. If the file does not exist, it creates a new one and writes the results.
  
- **Saving and Loading Progress**:
  - The `save_progress(base_url, query, query_param, total_pages, current_page, results_data)` function saves the current progress to a JSON file (`progress.json`). This allows the script to resume from where it left off in case of interruptions.
  - The `load_progress()` function loads the progress from the JSON file if it exists. This enables the script to continue fetching results from the last saved page.

## Auto Scheduler for Publication Crawler

## Overview

This repository contains a script for automatically crawling publication data, checking and removing duplicates, updating an existing list, committing changes, and pushing updates to GitHub. The entire process is automated to run monthly using Windows Task Scheduler, ensuring that your publication data is always up to date without any manual intervention.

## Prerequisites

- Python 3.x
- Git
- Tkinter (for message boxes)
- Windows Task Scheduler

## Installation

1. **Clone the Repository:**

   Clone this repository to your local machine using VSCode or any other Git client.

   ```bash
   git clone git@github.com:Yolo1105/task_auto_scheduler.git
   ```

2. **Install Dependencies:**

   Ensure you have the necessary Python packages installed. You can use `pip` to install any missing packages.

   ```bash
   pip install gitpython
   ```

3. **Configure Paths:**

   Update the paths in `auto_scheduler.py` to match your local setup.

   ```python
   repo_path = r"C:\Users\mohan\OneDrive\Desktop\GitHub_Repo\publication_crawler"
   script_path = os.path.join(repo_path, 'test_script.py')
   ```

## Setting Up Windows Task Scheduler

1. **Open Task Scheduler:**

   Open Windows Task Scheduler from the Start menu.

   ![Open Task Scheduler](file-rUHP1TZ1PjgOQ7Z5YAORZhQX)

2. **Create a New Task:**

   - Click on "Create Basic Task".
   - Name your task (e.g., "Publication Crawler Auto Scheduler").

   ![Create Basic Task](file-5kmoJzNgHwnLEvzyeNitgSot)

3. **Configure Triggers:**

   - Go to the "Triggers" tab.
   - Click "New" and set it to run monthly.

   ![Task Trigger](file-yj94t8gPCtWywczitZBtNMJT)

4. **Set Monthly Trigger:**

   - Select "Monthly".
   - Set the desired start date and time.
   - Choose the months and days to run.

   ![Monthly Trigger](file-PTQHOfO1MExVeJRsIFVnfHGu)

5. **Configure Actions:**

   - Go to the "Actions" tab.
   - Click "New" and set the action to start the Python executable.
   - In the "Program/script" field, specify the path to the `auto_scheduler.py` script. **Ensure you select `auto_scheduler.py`, not `crawler.py`, as `auto_scheduler.py` handles the execution of the crawling script internally.**

   ![Specify Script](file-wBoXhyIr0HtAuxnPsULZMd3c)

6. **Configure Conditions and Settings:**

   Adjust any additional settings or conditions as needed.

   ![Configure Settings](file-bjC5GHlNHM4Lsn9cfEZyvvvY)

## Automated Workflow

The `auto_scheduler.py` script will handle the following tasks:

1. **Logging:**

   Logs messages and the last run time to a log file located on your desktop.

2. **Script Execution:**

   Executes the `test_script.py` to crawl and update publication data.

3. **Git Operations:**

   Commits and pushes changes to the GitHub repository with a timestamp.

4. **Notifications:**

   Displays popup messages to indicate the start and end of the script execution. When the script starts running, a popup window will notify the user. Another popup window will notify the user when the script finishes running.

### Detailed Functionality

#### Execution Logic

- **Script Start:**

   ```python
   log_message("Script started.")
   show_message("Script Start", "The script is starting to run.")
   log_message("Script start running.")
   ```

   Logs the start of the script and shows a popup message.

- **Run the Script:**

   ```python
   run_script()
   ```

   Executes the publication crawling script.

- **Commit and Push Changes:**

   ```python
   commit_and_push_changes()
   ```

   Commits any changes and pushes them to GitHub.

- **Log Last Run Time:**

   ```python
   log_last_run_time()
   ```

   Logs the last run time of the script.

- **Script End:**

   ```python
   show_message("Script End", "The script has finished running.")
   log_message("Script finished running.")
   ```

   Logs the end of the script and shows a popup message.

#### Scheduling Logic

- **Run Schedule:**

   The script is designed to run monthly. If the scheduled time is missed (e.g., the laptop was off), it will execute the next time the laptop is turned on.

- **Automation:**

   Once configured, no manual intervention is needed. The Windows Task Scheduler will automatically run the script at the specified intervals.

## Notifications

The script provides visual feedback through popup windows to notify the user:

- **Start Notification:**

  When the script starts running, a popup window will appear with the message "The script is starting to run."

- **End Notification:**

  Upon completion, another popup window will notify the user that "The script has finished running."