import csv
import requests
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
from dotenv import load_dotenv

def get_status_code(url):
    try:
        response = requests.get(url, timeout=10)  # タイムアウトを設定
        return response.status_code
    except requests.RequestException as e:
        return 500

def get_title(driver):
    try:
        title_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, 'title'))
        )
        title = title_element.get_attribute('innerText')
        return title, "○" if "見つかりません" in title or "404" in title or "お探しのページ" in title else "×"
    except Exception as e:
        return "Unknown", "×"

def get_final_url(driver):
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))  # Bodyタグが存在するまで待機
        return driver.current_url
    except Exception as e:
        return driver.current_url

def main():
    load_dotenv()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    webdriver_path = os.getenv('CHROME_DRIVER_PATH')
    if not webdriver_path:
        print("Error: The environment variable CHROME_DRIVER_PATH is not set.")
        return

    driver = webdriver.Chrome(service=Service(webdriver_path), options=chrome_options)

    try:
        with open('output.csv', 'w', newline='', encoding='utf-8') as f, open('urls.txt', 'r') as url_file:
            writer = csv.writer(f)
            writer.writerow(["URL", "リダイレクト", "404", "リダイレクトURL", "リダイレクトタイトル", "ステータスコード", "PDF", "不要"])

            # プログレスバーの設定
            url_list = list(map(str.strip, url_file))
            progress_bar = tqdm(url_list, unit="URL", ncols=80)

            for url in progress_bar:
                driver.get(url)  # ここでURLを開く
                original_title, _ = get_title(driver)  # リダイレクト前のタイトルを取得
                final_url = get_final_url(driver)
                PDF_check = "○" if ".pdf" in final_url.lower() else ""
                title, title_check = get_title(driver)
                redirect_check = "○" if final_url != url else ""
                redirect_title = title if final_url != url else ""
                status_code = get_status_code(final_url)
                writer.writerow([url, original_title, redirect_check, title_check, final_url if final_url != url else "", redirect_title, status_code, PDF_check])
    except Exception as e:
        print(f"An error occurred during the main process: {e}")
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
