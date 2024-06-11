import os
import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import logging
import json
import asyncio
import aiohttp
from fake_useragent import UserAgent
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Ensure the logs and results directories exist
os.makedirs('logs', exist_ok=True)
os.makedirs('results', exist_ok=True)

# Setup logging to file with date-based filename
log_date = datetime.now().strftime("%Y-%m-%d")
log_filename = f"logs/{log_date}.log"
if not os.path.exists(log_filename):
    open(log_filename, 'w').close()  # Create the file if it does not exist

logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Generate a random user agent
user_agent_cache = UserAgent()
def get_random_user_agent():
    return user_agent_cache.random

async def fetch_page(session, url, params, headers):
    retries = 5
    while retries > 0:
        try:
            async with session.get(url, params=params, headers=headers, timeout=10) as response:
                response.raise_for_status()
                html_content = await response.text()
                return html_content
        except (aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError) as e:
            retries -= 1
            logging.error(f"Request failed (retries left: {retries}): {e}")
            await asyncio.sleep(random.uniform(5, 15))
    return None

def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    search_results = soup.find_all('div', class_='gs_r gs_or gs_scl')
    
    if not search_results:
        logging.warning("No search results found on the page.")
    
    results_data = []
    for result in search_results:
        title_tag = result.find('h3', class_='gs_rt')
        title = title_tag.text.strip() if title_tag else "Title not found"
        link = title_tag.a['href'] if title_tag and title_tag.a else "Link not found"
        
        results_data.append({'Title': title, 'Link': link})
    
    logging.info(f"Parsed results: {results_data}")
    return results_data

async def fetch_search_results(session, query, start_page, end_page):
    base_url = "https://scholar.google.com/scholar"
    query_param = 'q'
    results_data = []
    headers = {'User-Agent': get_random_user_agent()}

    tasks = []
    for page in range(start_page, end_page):
        params = {query_param: query, 'start': page * 10}
        tasks.append(fetch_page(session, base_url, params, headers))
    
    for page_content in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"Fetching pages {start_page} to {end_page - 1}", leave=True):
        page_content = await page_content
        if page_content:
            page_results = parse_results(page_content)
            results_data.extend(page_results)

    return results_data

def write_to_csv(results_data):
    if not results_data:
        logging.warning("No data to write to CSV.")
        return

    csv_date = datetime.now().strftime("%Y-%m-%d")
    csv_filename = f"results/{csv_date}_results.csv"
    file_exists = os.path.isfile(csv_filename)
    
    print(f"Results Data: {results_data}")  # Debugging statement
    
    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = ['Title', 'Link']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for result in results_data:
            writer.writerow({field: result[field] for field in fieldnames})

    logging.info(f"Results written to CSV: {csv_filename}")
    print(f"Results written to CSV: {csv_filename}")

def save_progress(query, total_pages, current_page, results_data):
    progress = {
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

async def get_total_pages(query):
    base_url = "https://scholar.google.com/scholar"
    query_param = 'q'
    headers = {'User-Agent': get_random_user_agent()}
    params = {query_param: query, 'start': 0}

    async with aiohttp.ClientSession() as session:
        html_content = await fetch_page(session, base_url, params, headers)
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            result_stats = soup.find('div', id='gs_ab_md')
            if result_stats:
                text = result_stats.get_text()
                total_results = int(text.split()[1].replace(',', '').replace('.', ''))
                total_pages = (total_results // 10) + 1
                return total_pages
    return 0

async def main():
    query = "This work was supported in part through the NYU IT High Performance Computing resources, services, and staff expertise"

    loop = asyncio.get_event_loop()
    total_pages = await get_total_pages(query)
    print(f"Total number of pages to crawl: {total_pages}")

    progress = load_progress()
    if progress and progress['query'] == query:
        print(f"Last saved page number: {progress['current_page']}")
        if get_user_input():
            start_page = progress['current_page']
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

    num_threads = 5
    pages_per_thread = total_pages // num_threads
    tasks = []
    async with aiohttp.ClientSession() as session:
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for i in range(num_threads):
                start = start_page + i * pages_per_thread
                end = start + pages_per_thread
                if i == num_threads - 1:
                    end = start_page + total_pages  # Make sure the last thread covers any remaining pages
                tasks.append(loop.run_in_executor(executor, asyncio.ensure_future, fetch_search_results(session, query, start, end)))
            
            results = await asyncio.gather(*tasks)
            for result in results:
                results_data.extend(result)

    if results_data:
        logging.info(f"Fetched {len(results_data)} results.")
    else:
        logging.warning("No results fetched.")
    
    write_to_csv(results_data)
    save_progress(query, total_pages, start_page + total_pages, results_data)
    logging.info("Results written to CSV and progress saved")

if __name__ == "__main__":
    asyncio.run(main())
