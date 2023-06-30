from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv
import time

# Chromeのオプション設定
chrome_options = Options()
chrome_options.add_argument("--headless")  # GUIなしで実行する場合

# WebDriverのパスを設定(適宜変更してください)
webdriver_path = '/path/to/chromedriver'

# WebDriverのインスタンスを生成
driver = webdriver.Chrome(service=Service(webdriver_path), options=chrome_options)

# csvファイルの書き出し準備
with open('output.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["URL", "Redirect Check", "Title Check", "Status Code", "Final URL", "Unnecessary URL"])

    # テキストファイルからURLを読み込む
    with open('urls.txt', 'r') as url_file:
        urls = [line.strip() for line in url_file.readlines()]

        for url in urls:
            # URLを開く
            driver.get(url)

            # 最終的なURLとステータスコードを取得
            final_url = driver.current_url
            response_code = driver.execute_script("return document.readyState")

            # リダイレクトチェック
            if final_url != url:
                redirect_check = "○"
            else:
                redirect_check = "×"

            # タイトルチェック
            try:
                title = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'title'))).get_attribute('innerText')
                if "見つかりませんでした" in title or "404" in title:
                    title_check = "not found"
                else:
                    title_check = "found"
            except TimeoutException:
                title_check = "not found"

            # タイトルがないページは不要
            unnecessary_url = "○" if title is None else "×"

            # csvファイルに書き出す
            writer.writerow([url, redirect_check, title_check, response_code, final_url, unnecessary_url])

# WebDriverを閉じる
driver.quit()
