import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import logging
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(filename='search_log.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize UserAgent object
ua = UserAgent()

def fetch_google_search_results(query, num_pages=3):
    results_data = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_page = {
            executor.submit(fetch_page_results, query, page): page for page in range(num_pages)
        }
        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                results_data.extend(future.result())
            except Exception as e:
                logging.error(f"Fetching results for page {page} failed: {e}")
    
    return results_data

def fetch_page_results(query, page):
    start = page * 10
    url = "https://www.google.com/search"
    params = {'q': query, 'start': start}
    headers = {'User-Agent': ua.random}
    
    success = False
    retries = 3
    results_data = []
    
    while not success and retries > 0:
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            html_content = response.text
            logging.info(f"Fetched HTML content for page {page}")
            results_data = parse_results(html_content)
            
            # Randomize delay between requests
            time.sleep(random.uniform(5, 15))
            success = True
            
        except requests.RequestException as e:
            retries -= 1
            logging.error(f"Request failed (retries left: {retries}): {e}")
            time.sleep(random.uniform(5, 15))
    
    return results_data

def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    search_results = soup.find_all('div', class_='tF2Cxc')
    
    if not search_results:
        logging.warning("No search results found on the page.")
    
    results_data = []
    for result in search_results:
        title = result.find('h3', class_='LC20lb').text.strip() if result.find('h3', class_='LC20lb') else "Title not found"
        link = result.a['href'] if result.a else "Link not found"
        snippet = result.find('div', class_='IsZvec').text.strip() if result.find('div', class_='IsZvec') else "Snippet not found"
        
        results_data.append({'Title': title, 'Link': link, 'Snippet': snippet})
    
    return results_data

def write_to_csv(results_data):
    with open('results.csv', mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['Title', 'Link', 'Snippet']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results_data:
            writer.writerow(result)

def main():
    query = "This work was supported in part through the NYU IT High Performance Computing resources, services, and staff expertise"
    num_pages = 10  
    results_data = fetch_google_search_results(query, num_pages)
    if results_data:
        logging.info(f"Fetched {len(results_data)} results.")
    else:
        logging.warning("No results fetched.")
    write_to_csv(results_data)

if __name__ == "__main__":
    main()
