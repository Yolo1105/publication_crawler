import requests
from bs4 import BeautifulSoup
import csv
import time  

def fetch_google_search_results(query, num_pages=3):
    results_data = []
    
    for page in range(num_pages):
        start = page * 10
        url = "https://www.google.com/search"
        params = {'q': query, 'start': start}
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Safari/537.36'
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        html_content = response.text
        results_data += parse_results(html_content)

        time.sleep(5) 
        
    return results_data

def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    search_results = soup.find_all('div', class_='tF2Cxc')
    
    results_data = []
    for result in search_results:
        title = result.find('h3', class_='LC20lb').text.strip() if result.find('h3', class_='LC20lb') else "Title not found"
        link = result.a['href'] if result.a else "Link not found"
        snippet = result.find('div', class_='IsZvec').text.strip() if result.find('div', class_='IsZvec') else "Snippet not found"
        
        results_data.append({'Title': title, 'Link': link, 'Snippet': snippet})
    
    return results_data

def write_to_csv(results_data):
    with open('search_results.csv', mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['Title', 'Link', 'Snippet']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results_data:
            writer.writerow(result)

def main():
    query = "This work was supported in part through the NYU IT High Performance Computing resources, services, and staff expertise"
    num_pages = 500  
    results_data = fetch_google_search_results(query, num_pages)
    write_to_csv(results_data)

if __name__ == "__main__":
    main()
