import os
import csv
import random
import logging
import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
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
        except (aiohttp.ClientError, aiohttp.http_exceptions.HttpProcessingError, asyncio.TimeoutError) as e:
            retries -= 1
            logging.error(f"Request failed (retries left: {retries}): {e}")
            await asyncio.sleep(random.uniform(5, 15))
    return None

def parse_mla_citation(html):
    soup = BeautifulSoup(html, 'html.parser')
    mla_citation_div = soup.find('div', class_='gs_citr')
    if mla_citation_div:
        return mla_citation_div.text.strip()
    return "MLA citation not found"

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
        
        mla_citation = parse_mla_citation(str(result))
        
        results_data.append({'Title': title, 'Link': link, 'MLA Citation': mla_citation})
    
    logging.info(f"Parsed results: {results_data}")
    return results_data

async def fetch_search_results(session, query, start_page, end_page, progress_bar):
    base_url = "https://scholar.google.com/scholar"
    query_param = 'q'
    headers = {'User-Agent': get_random_user_agent()}

    results_data = []

    tasks = []
    for page in range(start_page, end_page + 1):
        params = {query_param: query, 'start': (page - 1) * 10}
        tasks.append(fetch_page(session, base_url, params, headers))

    for task in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"Fetching pages {start_page} to {end_page}", leave=True):
        page_content = await task
        if page_content:
            page_results = parse_results(page_content)
            results_data.extend(page_results)
        progress_bar.update(1)

    return results_data

def load_existing_csv_data(csv_filename):
    existing_data = set()
    if os.path.exists(csv_filename):
        with open(csv_filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_data.add((row['Title'], row['Link'], row['MLA Citation']))
    return existing_data

def write_to_csv(results_data, csv_filename):
    if not results_data:
        logging.warning("No data to write to CSV.")
        return

    existing_data = load_existing_csv_data(csv_filename)
    
    new_data = [result for result in results_data if (result['Title'], result['Link'], result['MLA Citation']) not in existing_data]

    if not new_data:
        logging.info("No new data to write to CSV.")
        return
    
    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = ['Title', 'Link', 'MLA Citation']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        if not os.path.exists(csv_filename) or os.path.getsize(csv_filename) == 0:
            writer.writeheader()
        
        for result in new_data:
            writer.writerow({field: result[field] for field in fieldnames})

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
        start_page = input("Enter the starting page (1 for the first page): ").strip()
        total_pages = input("Enter the total number of pages to crawl: ").strip()
        if start_page.isdigit() and total_pages.isdigit():
            return int(start_page), int(total_pages)
        else:
            print("Invalid input. Please enter integer values for starting page and total pages.")

async def crawl_pages(query, start_page, end_page, results_data, progress_bar):
    async with aiohttp.ClientSession() as session:
        page_results = await fetch_search_results(session, query, start_page, end_page, progress_bar)
        results_data.extend(page_results)

def run_crawl_pages(query, start_page, end_page, results_data, progress_bar):
    asyncio.run(crawl_pages(query, start_page, end_page, results_data, progress_bar))

async def main():
    query = "This work was supported in part through the NYU IT High Performance Computing resources, services, and staff expertise"

    progress = load_progress()
    if progress and progress['query'] == query:
        print(f"Last saved page number: {progress['current_page']}")
        if get_user_input():
            start_page = progress['current_page']
            results_data = progress['results_data']
            total_pages = progress['total_pages']
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

    progress_bar = tqdm(total=total_pages, desc="Overall Progress", leave=True)

    middle_page = start_page + (total_pages // 2) - 1
    end_page = start_page + total_pages - 1

    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(run_crawl_pages, query, start_page, middle_page, results_data, progress_bar)
        executor.submit(run_crawl_pages, query, middle_page + 1, end_page, results_data, progress_bar)

    # Wait for all threads to complete
    executor.shutdown(wait=True)

    if results_data:
        logging.info(f"Fetched {len(results_data)} results.")
    else:
        logging.warning("No results fetched.")
    
    csv_date = datetime.now().strftime("%Y-%m-%d")
    write_to_csv(results_data, f'results/{csv_date}_results.csv')
    write_to_csv(results_data, 'results/google_scholar.csv')
    save_progress(query, total_pages, end_page, results_data)
    progress_bar.close()

if __name__ == "__main__":
    asyncio.run(main())
