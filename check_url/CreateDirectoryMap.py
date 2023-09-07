import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
from tqdm import tqdm


def get_links(driver, url):
    driver.get(url)
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.title.string if soup.title else "No Title"

    links = []
    for a in soup.find_all('a'):
        link_url = a.get('href')
        if link_url:
            full_url = urljoin(url, link_url)
            # Check if the URL is valid
            parsed = urlparse(full_url)
            if bool(parsed.netloc) and bool(parsed.scheme):
                links.append(full_url)

    return title, links

def build_directory_map(driver, url, node_id=1, max_depth=3, depth=0, visited=None):
    if visited is None:
        visited = set()

    if url in visited or depth > max_depth:
        return None
    
    visited.add(url)

    title, links = get_links(driver, url)
    directory_map = {'node': node_id, 'url': url, 'title': title, 'children': []}

    for link in tqdm(links, desc="Processing links"):
        time.sleep(2)
        link_parsed = urlparse(link)
        url_parsed = urlparse(url)
        if link_parsed.netloc == url_parsed.netloc:
            node_id += 1
            child = build_directory_map(driver, link, node_id, max_depth, depth + 1, visited)
            if child is not None:
                directory_map['children'].append(child)

    return directory_map

def flatten(directory_map, parent_node=None):
    url = directory_map['url']
    title = directory_map['title']
    node_id = directory_map['node']
    parent_id = parent_node['node'] if parent_node else None
    flattened = [{'node': node_id, 'parent_node': parent_id, 'url': url, 'title': title}]

    for child in directory_map['children']:
        flattened.extend(flatten(child, parent_node={'node': node_id}))

    return flattened

def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    url = 'http://www.nds.co.jp/index.html'
    directory_map = build_directory_map(driver, url)
    driver.quit()

    flattened_data = flatten(directory_map)
    df = pd.DataFrame(flattened_data)
    df.to_excel('directory_map.xlsx', index=False)

if __name__ == "__main__":
    main()
