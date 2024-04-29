import requests
from bs4 import BeautifulSoup
import csv
import time  

def fetch_acm_search_results(query, num_pages=3):
    results_data = []
    
    for page in range(num_pages):
        # ACM uses pagination differently; check the exact number of results you want per page and calculate start accordingly
        start = page * 20  # Assuming 20 results per page; adjust if different
        url = "https://dl.acm.org/action/doSearch"
        params = {
            'AllField': query,
            'startPage': page,
            'pageSize': 20
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Safari/537.36'
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        html_content = response.text
        results_data += parse_results(html_content)

        time.sleep(5)  # Be respectful to the server
        
    return results_data

def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # ACM search results have different classes; find the correct class or tag used for results
    search_results = soup.find_all('div', class_='issue-item__content-right')  # Update this class based on actual observation
    
    results_data = []
    for result in search_results:
        title = result.find('h5', class_='issue-item__title').text.strip() if result.find('h5', class_='issue-item__title') else "Title not found"
        link = f"https://dl.acm.org{result.find('a')['href']}" if result.find('a') else "Link not found"
        snippet = result.find('div', class_='issue-item__abstract').text.strip() if result.find('div', class_='issue-item__abstract') else "Snippet not found"
        
        results_data.append({'Title': title, 'Link': link, 'Snippet': snippet})
    
    return results_data

def write_to_csv(results_data):
    with open('acm_search_results.csv', mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['Title', 'Link', 'Snippet']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results_data:
            writer.writerow(result)

def main():
    query = "high performance computing"
    num_pages = 3  # Adjust based on the number of results you expect
    results_data = fetch_acm_search_results(query, num_pages)
    write_to_csv(results_data)

if __name__ == "__main__":
    main()
