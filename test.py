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

# Setup logging to file with date-based filename
log_date = datetime.now().strftime("%Y-%m-%d")
log_filename = f"{log_date}.log"
if not os.path.exists(log_filename):
    open(log_filename, 'w').close()

logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Generate a random user agent
user_agent_cache = UserAgent()
def get_random_user_agent():
    return user_agent_cache.random

def scrape_proxies():
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
                    proxies.append(f'{ip}:{port}')
                else:
                    logging.warning("Row does not contain enough cells")
        except requests.RequestException as e:
            logging.error(f"Failed to fetch proxies from {url}: {e}")
    return proxies

def validate_proxy(proxy):
    url = 'http://scholar.google.com'
    proxies = {
        'http': f'http://{proxy}',
        'https': f'https://{proxy}'
    }
    try:
        response = requests.get(url, proxies=proxies, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        logging.error(f"Proxy validation error for {proxy}: {e}")
    return False

def get_valid_proxies(proxies):
    valid_proxies = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {executor.submit(validate_proxy, proxy): proxy for proxy in proxies}
        for future in tqdm(as_completed(future_to_proxy), total=len(future_to_proxy), desc="Validating proxies"):
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
    return random.choice(valid_proxies) if valid_proxies else None

def fetch_search_results(config, query, total_pages=10, start_page=0, valid_proxies=None):
    results_data = []
    if valid_proxies is None:
        valid_proxies = get_valid_proxies(scrape_proxies())

    if not valid_proxies:
        logging.error("No valid proxies available. Exiting.")
        return results_data

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for page in range(start_page, start_page + total_pages):
            futures.append(executor.submit(fetch_page_results, config, query, page, valid_proxies))

        for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching search results"):
            try:
                page_results = future.result()
                results_data.extend(page_results)
                logging.info(f"Fetched results: {page_results}")
            except Exception as e:
                logging.error(f"Fetching results failed: {e}")

    return results_data

def fetch_page_results(config, query, page, valid_proxies):
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
            driver.get(config['base_url'])

            for _ in range(10):
                try:
                    search_bar = driver.find_element(By.NAME, 'q')
                    break
                except:
                    time.sleep(1)
            else:
                raise Exception("Search bar not found")

            search_bar.send_keys(query)
            search_bar.send_keys(Keys.RETURN)
            time.sleep(random.uniform(2, 5))

            html_content = driver.page_source
            driver.quit()

            logging.info(f"Fetched HTML content for page {page}")
            results_data = parse_results(html_content, config['parsing_rules'])
            success = True

        except Exception as e:
            retries -= 1
            logging.error(f"Request failed (retries left: {retries}): {e}")
            if proxy in valid_proxies:
                valid_proxies.remove(proxy)
                logging.info(f"Removed invalid proxy: {proxy}")
            time.sleep(backoff)
            backoff *= 2

    return results_data

def parse_results(html, parsing_rules):
    soup = BeautifulSoup(html, 'html.parser')
    search_results = soup.select(parsing_rules['result_selector'])

    if not search_results:
        logging.warning("No search results found on the page.")

    results_data = []
    for result in search_results:
        title = result.select_one(parsing_rules['title_selector']).text.strip() if result.select_one(parsing_rules['title_selector']) else "Title not found"
        link = result.select_one(parsing_rules['link_selector'])['href'] if result.select_one(parsing_rules['link_selector']) else "Link not found"
        if parsing_rules.get('link_prefix'):
            link = parsing_rules['link_prefix'] + link

        results_data.append({'Title': title, 'Link': link})

    return results_data

def write_to_csv(results_data):
    csv_date = datetime.now().strftime("%Y-%m-%d")
    csv_filename = f"{csv_date}_results.csv"
    file_exists = os.path.isfile(csv_filename)

    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = ['Title', 'Link']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for result in results_data:
            writer.writerow({field: result[field] for field in fieldnames})

def save_progress(config, query, total_pages, current_page, results_data):
    progress = {
        'config': config,
        'query': query,
        'total_pages': total_pages,
        'current_page': current_page,
        'results_data': results_data
    }
    with open('progress.json', 'w') as f:
        json.dump(progress, f)

def load_progress():
    try:
        with open('progress.json', 'r') as f:
            progress = json.load(f)
            return progress
    except FileNotFoundError:
        return None

def get_user_input():
    while True:
        resume = input("Do you want to resume from the last saved page? (y/n): ").strip().lower()
        if resume in ['yes', 'y']:
            return True
        elif resume in ['no', 'n']:
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

def get_page_input():
    while True:
        start_page = input("Enter the starting page (0 for the first page): ").strip()
        total_pages = input("Enter the total number of pages to crawl: ").strip()
        if start_page.isdigit() and total_pages.isdigit():
            return int(start_page), int(total_pages)
        else:
            print("Invalid input. Please enter integer values for starting page and total pages.")

def load_config():
    return {
        'base_url': 'https://scholar.google.com',
        'query_param': 'q',
        'parsing_rules': {
            'result_selector': 'div.gs_r.gs_or.gs_scl',
            'title_selector': 'h3.gs_rt',
            'link_selector': 'h3.gs_rt > a',
            'link_prefix': None
        }
    }

def main():
    config = load_config()
    query = input("Enter the search query: ").strip()

    progress = load_progress()
    if progress and progress['query'] == query and progress['config']['base_url'] == config['base_url']:
        print(f"Last saved page number: {progress['current_page']}")
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
        print("No last saved page found. Please enter the starting page and total number of pages.")
        start_page, total_pages = get_page_input()
        results_data = []
        logging.info(f"Starting to fetch search results for query: {query} from page {start_page}")

    results_data.extend(fetch_search_results(config, query, total_pages, start_page=start_page))

    if results_data:
        logging.info(f"Fetched {len(results_data)} results.")
    else:
        logging.warning("No results fetched.")

    write_to_csv(results_data)
    logging.info("Results written to CSV")
    save_progress(config, query, total_pages, start_page + total_pages, results_data)

if __name__ == "__main__":
    main()
