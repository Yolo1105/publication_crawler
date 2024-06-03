import os
import csv
import time
import random
import logging
import json
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
from time import sleep

# Setup logging to file with date-based filename
log_date = datetime.now().strftime("%Y-%m-%d")
log_filename = f"{log_date}.log"
if not os.path.exists(log_filename):
    open(log_filename, 'w').close()  # Create the file if it does not exist

logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Generate a random user agent
user_agent_cache = UserAgent()
def get_random_user_agent():
    return user_agent_cache.random

def scrape_proxies():
    # Scrapes proxies from multiple free proxy listing websites
    proxy_sites = [
        'https://www.sslproxies.org/',
        'https://free-proxy-list.net/',
        'https://www.us-proxy.org/',
        'https://www.proxy-list.download/HTTP'
    ]
    proxies = []
    for url in proxy_sites:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.select('table.table tbody tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    ip = cells[0].text.strip()
                    port = cells[1].text.strip()
                    proxy = f'{ip}:{port}'
                    proxies.append(proxy)
                else:
                    logging.warning("Row does not contain enough cells")
        except requests.RequestException as e:
            logging.error(f"Failed to fetch proxies from {url}: {e}")
    return proxies

def validate_proxy(proxy):
    # Validates a proxy by making a request to Google Scholar
    url = 'http://scholar.google.com'
    proxies = {
        'http': f'http://{proxy}',
        'https': f'https://{proxy}'
    }
    try:
        response = requests.get(url, proxies=proxies, timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        logging.error(f"Connection refused for proxy {proxy}")
    except requests.exceptions.SSLError as e:
        logging.error(f"SSL error for proxy {proxy}: {e}")
    except requests.exceptions.ProxyError as e:
        logging.error(f"Proxy error for proxy {proxy}: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"General error for proxy {proxy}: {e}")
    return False

def get_valid_proxies(proxies):
    # Returns a list of valid proxies by checking each one
    valid_proxies = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {executor.submit(validate_proxy, proxy): proxy for proxy in proxies}
        for future in tqdm(as_completed(future_to_proxy), total=len(future_to_proxy), desc="Validating proxies", leave=True):
            proxy = future_to_proxy[future]
            try:
                if future.result():
                    valid_proxies.append(proxy)
            except Exception as e:
                logging.error(f"Proxy validation failed: {e}")
    if not valid_proxies:
        logging.error("No valid proxies found.")
    return valid_proxies

def get_random_proxy(valid_proxies):
    # Selects a random proxy from the list of valid proxies
    return random.choice(valid_proxies) if valid_proxies else None

def fetch_search_results(base_url, query, total_pages=10, start_page=0, valid_proxies=None):
    # Fetches search results from a specified website for a given query starting from a specific page
    results_data = []
    if valid_proxies is None:
        valid_proxies = get_valid_proxies(scrape_proxies())
    
    if not valid_proxies:
        logging.error("No valid proxies available. Exiting.")
        return results_data

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for page in range(start_page, start_page + total_pages):
            futures.append(executor.submit(fetch_page_results, base_url, query, page, valid_proxies))

        for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching search results", leave=True):
            try:
                page_results = future.result()
                results_data.extend(page_results)
                logging.info(f"Fetched results: {page_results}")
            except Exception as e:
                logging.error(f"Fetching results failed: {e}")

    return results_data

def fetch_page_results(base_url, query, page, valid_proxies):
    # Fetches search results from a single page of the specified website
    start = page * 10
    headers = {'User-Agent': get_random_user_agent()}
    
    success = False
    retries = 5
    backoff = 1
    results_data = []
    
    while not success and retries > 0:
        proxy = get_random_proxy(valid_proxies)
        proxies = {'http': f'http://{proxy}', 'https': f'https://{proxy}'} if proxy else None
        try:
            options = webdriver.ChromeOptions()
            options.add_argument(f'user-agent={get_random_user_agent()}')
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver.get(base_url)
            
            # Wait for the search bar to be present
            for _ in range(10):  # Retry up to 10 times (about 10 seconds)
                try:
                    search_bar = driver.find_element(By.NAME, 'q')
                    break
                except:
                    sleep(1)
            else:
                raise Exception("Search bar not found")

            # Perform search
            search_bar.send_keys(query)
            search_bar.send_keys(Keys.RETURN)
            
            sleep(random.uniform(2, 5))  # Wait for the results to load
            
            html_content = driver.page_source
            driver.quit()
            
            logging.info(f"Fetched HTML content for page {page}")
            results_data = parse_results(html_content)
            
            success = True
            
        except requests.exceptions.ConnectionError:
            logging.error(f"Connection refused for proxy {proxy}")
            retries -= 1
            if proxy in valid_proxies:
                valid_proxies.remove(proxy)
                logging.info(f"Removed invalid proxy: {proxy}")
            sleep(backoff)
            backoff *= 2
        except Exception as e:
            retries -= 1
            logging.error(f"Request failed (retries left: {retries}): {e}")
            if proxy in valid_proxies:
                valid_proxies.remove(proxy)
                logging.info(f"Removed invalid proxy: {proxy}")
            sleep(backoff)
            backoff *= 2
    
    return results_data

def parse_results(html):
    # Parses HTML content to extract search results
    soup = BeautifulSoup(html, 'html.parser')
    search_results = soup.find_all('div', class_='tF2Cxc')
    
    if not search_results:
        logging.warning("No search results found on the page.")
    
    results_data = []
    for result in search_results:
        title = result.find('h3', class_='LC20lb').text.strip() if result.find('h3', class_='LC20lb') else "Title not found"
        link = result.find('a')['href'] if result.find('a') else "Link not found"
        
        results_data.append({'Title': title, 'Link': link})
    
    return results_data

def write_to_csv(results_data, filename):
    # Writes search results to a CSV file
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = ['Title', 'Link']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for result in results_data:
            writer.writerow({field: result[field] for field in fieldnames})

def save_progress(progress):
    # Saves the current progress to a JSON file
    with open('progress.json', 'w') as f:
        json.dump(progress, f)

def load_progress():
    # Loads progress from a JSON file if it exists
    try:
        with open('progress.json', 'r') as f:
            progress = json.load(f)
            return progress
    except FileNotFoundError:
        return None

def get_user_input():
    # Gets user input for resuming or starting a new search
    while True:
        resume = input("Do you want to resume from the last saved page? (y/n): ").strip().lower()
        if resume in ['yes', 'y']:
            return True
        elif resume in ['no', 'n']:
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

def get_page_input():
    # Gets user input for starting page and total pages
    while True:
        start_page = input("Enter the starting page (0 for the first page): ").strip()
        total_pages = input("Enter the total number of pages to crawl: ").strip()
        if start_page.isdigit() and total_pages.isdigit():
            return int(start_page), int(total_pages)
        else:
            print("Invalid input. Please enter integer values for starting page and total pages.")

def main():
    # Main function to manage fetching search results
    query = "This work was supported in part through the NYU IT High Performance Computing resources, services, and staff expertise"
    websites = [
        "https://scholar.google.com"
    ]
    
    progress = load_progress()
    results_data = []
    
    if progress and progress['query'] == query:
        print(f"Last saved progress found.")
        if get_user_input():
            start_page = progress['current_page']
            total_pages = int(input("Enter the total number of pages to crawl: ").strip())
            results_data = progress['results_data']
            logging.info(f"Resuming fetching search results for query: {query} from page {start_page}")
        else:
            start_page, total_pages = get_page_input()
            results_data = []
            logging.info(f"Starting to fetch search results for query: {query} from page {start_page}")
    else:
        print("No last saved progress found. Please enter the starting page and total number of pages.")
        start_page, total_pages = get_page_input()
        results_data = []
        logging.info(f"Starting to fetch search results for query: {query} from page {start_page}")

    with ThreadPoolExecutor(max_workers=len(websites)) as executor:
        futures = []
        for website in websites:
            futures.append(executor.submit(fetch_search_results, website, query, total_pages, start_page=start_page))

        for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching search results", leave=True):
            try:
                site_results = future.result()
                results_data.extend(site_results)
                logging.info(f"Fetched results: {site_results}")
            except Exception as e:
                logging.error(f"Fetching results failed: {e}")
    
    if results_data:
        logging.info(f"Fetched {len(results_data)} results.")
    else:
        logging.warning("No results fetched.")
    
    csv_filename = f"{datetime.now().strftime('%Y-%m-%d')}_results.csv"
    write_to_csv(results_data, csv_filename)
    logging.info(f"Results written to CSV: {csv_filename}")

if __name__ == "__main__":
    main()
