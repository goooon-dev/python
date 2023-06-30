import requests
from bs4 import BeautifulSoup
import csv
# プログレスバーを表示させるライブラリ
from tqdm import tqdm

def check_url(url):
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        # 404の場合は専用ページがある場合があるので除外
        if response.status_code != 404:
            response.raise_for_status()
    except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as e:
        print(f"Broken link at {url}")
        return "Broken", "N/A", "N/A", url

    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.title.text if soup.title else ""
    # ステータスコードの取得
    status_code = response.status_code

    # リダイレクトがあった場合は、リダイレクト先のURLを取得
    final_url = response.url if url != response.url else "-"

    # 404のページであるか確認
    if "見つかりません" in title or "404" in title or "お探しのページ" in title:
        title_check = "有"
    else:
        title_check = "無"
    
    # リダイレクトされているか確認
    if response.history:
        redirect_check = "有"
    else:
        redirect_check = "無"

    if title:
        unnecessary_url = "-"
    else:
        unnecessary_url = "不要？なURL"
     
    return url, redirect_check, title_check, status_code, final_url, unnecessary_url

# ファイルからURLを読み込む
with open('urls.txt', 'r') as file:
    urls = file.read().splitlines()

# 結果を書き込むCSVファイルを開く
with open('results.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # ヘッダーを書き込む
    writer.writerow(["URL", "リダイレクト", "404ページ", "ステータスコード", "リダイレクト先URL", "不要？なURL"])
    
    # 各URLに対してチェックを行う
    for url in tqdm(urls):
        result = check_url(url)
        
        # 結果をCSVファイルに書き込む
        writer.writerow(result)
