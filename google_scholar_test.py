import logging
from tqdm import tqdm
from scholarly import scholarly, ProxyGenerator
import os
import csv

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Activate proxy because Google Scholar might otherwise block the IP address
logging.debug("Setting up proxy...")
pg = ProxyGenerator()
scholarly.use_proxy(pg, pg)

author_names = ['Albert Einstein']

keys = ['author', 'title', 'num_citations', 'number_of_co_authors', 'pub_year']
for year in range(2022, 2023):
    keys.append(f'{year}')

logging.debug("Opening output file...")
output_file = open('faculty_pubs.csv', 'a', newline='', encoding='utf-8', errors='replace')
dict_writer = csv.DictWriter(output_file, keys)

if os.path.getsize('faculty_pubs.csv') == 0:
    dict_writer.writeheader()
    output_file.flush()

dict_reader = csv.DictReader(open('faculty_pubs.csv', newline='', encoding='utf-8', errors='replace'), keys)
csv_reader = [row for row in dict_reader]

for name in author_names:
    logging.debug(f"Searching for author: {name}")
    try:
        author = next(scholarly.search_author(name))
        author = scholarly.fill((author), sections=['publications'])
    except StopIteration:
        logging.error(f"No author found for name: {name}")
        continue

    pubs = author['publications']
    logging.info(f"Found {len(pubs)} publications for {name}")

    progress_bar = tqdm(total=len(pubs), desc=f"Processing publications for {name}")
    author_pubs_in_file = [row for row in csv_reader if row['author'] == name]
    num_author_pubs_in_file = len(author_pubs_in_file)

    for i, pub in enumerate(pubs):
        if i < num_author_pubs_in_file:
            progress_bar.update(1)
            continue

        pub = scholarly.fill(pub)
        if any(x['title'] == pub['bib']['title'] for x in author_pubs_in_file):
            progress_bar.update(1)
            continue

        pub_res = {
            "author": name,
            "title": pub['bib']['title'],
            "num_citations": pub['num_citations'],
        }

        if 'author' in pub['bib']:
            pub_res["number_of_co_authors"] = len(pub['bib']['author'].split(' and ')) - 1
        else:
            pub_res["number_of_co_authors"] = ''

        if 'pub_year' in pub['bib']:
            pub_res['pub_year'] = pub['bib']['pub_year']
        else:
            pub_res['pub_year'] = ''

        for year in range(2022, 2023):
            pub_res[f'{year}'] = pub['cites_per_year'].get(year, '')

        dict_writer.writerow(pub_res)
        output_file.flush()
        progress_bar.update(1)

    progress_bar.close()

logging.info("Processing completed.")
