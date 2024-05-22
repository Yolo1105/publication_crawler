import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import logging
import json
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

logging.basicConfig(filename='search_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ua = UserAgent()

def scrape_proxies():
    url = 'https://www.sslproxies.org/'  
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    proxies = []
    
    rows = soup.select('table.table tbody tr')
    
    for row in rows:
        try:
            cells = row.find_all('td')
            if len(cells) >= 2:
                ip = cells[0].text.strip()
                port = cells[1].text.strip()
                proxy = f'{ip}:{port}'
                proxies.append(proxy)
            else:
                logging.warning("Row does not contain enough cells")
        except Exception as e:
            logging.error(f"Error parsing row: {e}")
    
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
    except Exception:
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
    return valid_proxies

def get_random_proxy(valid_proxies):
    return random.choice(valid_proxies) if valid_proxies else None

def fetch_google_scholar_results(query, num_pages=3, valid_proxies=None, start_page=0):
    results_data = []
    if valid_proxies is None:
        valid_proxies = get_valid_proxies(scrape_proxies())
    
    for page in tqdm(range(start_page, num_pages), desc="Fetching search results"):
        try:
            page_results = fetch_page_results(query, page, valid_proxies)
            results_data.extend(page_results)
            logging.info(f"Fetched results for page {page}: {page_results}")
            print(f"Fetched results for page {page}:")
            for result in page_results:
                print(result)
            
            save_progress(query, num_pages, page + 1, results_data)
            
            time.sleep(random.uniform(5, 15))
            
        except Exception as e:
            logging.error(f"Fetching results for page {page} failed: {e}")
    
    return results_data

def fetch_page_results(query, page, valid_proxies):
    start = page * 10
    url = "https://scholar.google.com/scholar" 
    params = {'q': query, 'start': start}
    headers = {'User-Agent': ua.random}
    
    success = False
    retries = 3
    results_data = []
    
    while not success and retries > 0:
        proxy = get_random_proxy(valid_proxies)
        proxies = {'http': f'http://{proxy}', 'https': f'https://{proxy}'} if proxy else None
        try:
            response = requests.get(url, params=params, headers=headers, proxies=proxies, timeout=10)
            response.raise_for_status()
            
            html_content = response.text
            logging.info(f"Fetched HTML content for page {page}")
            results_data = parse_results(html_content)
            
            success = True
            
        except requests.RequestException as e:
            retries -= 1
            logging.error(f"Request failed (retries left: {retries}): {e}")
            if proxy:
                valid_proxies.remove(proxy)
                logging.info(f"Removed invalid proxy: {proxy}")
            time.sleep(random.uniform(5, 15))
    
    return results_data

def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    search_results = soup.find_all('div', class_='gs_ri')  
    
    if not search_results:
        logging.warning("No search results found on the page.")
    
    results_data = []
    for result in search_results:
        title = result.find('h3', class_='gs_rt').text.strip() if result.find('h3', class_='gs_rt') else "Title not found"
        link = result.find('h3', class_='gs_rt').find('a')['href'] if result.find('h3', class_='gs_rt').find('a') else "Link not found"
        snippet = result.find('div', class_='gs_rs').text.strip() if result.find('div', class_='gs_rs') else "Snippet not found"
        
        results_data.append({'Title': title, 'Link': link, 'Snippet': snippet})
    
    return results_data

def write_to_csv(results_data):
    with open('results.csv', mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['Title', 'Link', 'Snippet']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results_data:
            writer.writerow(result)

def save_progress(query, num_pages, current_page, results_data):
    progress = {
        'query': query,
        'num_pages': num_pages,
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

def main():
    query = "This work was supported in part through the NYU IT High Performance Computing resources, services, and staff expertise"
    num_pages = 10 
    progress = load_progress()
    if progress and progress['query'] == query and progress['num_pages'] == num_pages:
        start_page = progress['current_page']
        results_data = progress['results_data']
        logging.info(f"Resuming fetching search results for query: {query} from page {start_page}")
    else:
        start_page = 0
        results_data = []
        logging.info(f"Starting to fetch search results for query: {query}")
    
    results_data.extend(fetch_google_scholar_results(query, num_pages, start_page=start_page))
    if results_data:
        logging.info(f"Fetched {len(results_data)} results.")
    else:
        logging.warning("No results fetched.")
    write_to_csv(results_data)
    logging.info("Results written to results.csv")

if __name__ == "__main__":
    main()
