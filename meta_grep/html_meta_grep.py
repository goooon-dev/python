import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm  # tqdmをインポート

def fetch_meta_data(url):
    response = requests.get(url)
    time.sleep(2)
    # エンコーディングをresponseのエンコーディング属性から取得し、それをBeautifulSoupのパーサに設定
    encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(response.content, from_encoding=encoding, features="html.parser")

    meta_data = {}
    for meta in soup.find_all('meta'):
        name = meta.get('name') or meta.get('property')
        content = meta.get('content')
        if name and content:
            meta_data[name] = content
    
    # titleタグのテキストを抽出
    title_tag = soup.find('title')
    if title_tag:
        meta_data['title'] = title_tag.text
    
    # canonical URLの抽出
    canonical_tag = soup.find('link', rel='canonical')
    if canonical_tag:
        meta_data['canonical'] = canonical_tag.get('href')
    
    # nofollowが含まれるリンクのURLを抽出
    nofollow_links = [link.get('href') for link in soup.find_all('a', rel='nofollow')]
    meta_data['nofollow_links'] = ', '.join(nofollow_links)
    
    return meta_data

def load_urls(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def main():
    urls = load_urls('urls.txt')  # urls.txtファイルからURLを読み込み

    all_meta_data = []
    # tqdmをforループでラップしてプログレスバーを表示
    for url in tqdm(urls, desc="Scraping", unit="page"):
        meta_data = fetch_meta_data(url)
        meta_data['url'] = url
        all_meta_data.append(meta_data)

    df = pd.DataFrame(all_meta_data)
    df.to_csv('meta_data.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    main()
