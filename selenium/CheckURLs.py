import csv
import time
from tqdm import tqdm
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def get_status_code(url):
    try:
        return requests.get(url).status_code
    except Exception:
        return "500"


def get_title(driver):
    try:
        title = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'title'))).get_attribute('innerText')
        return title, "○" if "見つかりません" in title or "404" in title or "お探しのページ" in title else "×"
    except Exception:
        return None, ""

# リダイレクト後も含む最終的なURLを取得
def get_final_url(url, driver):
    driver.get(url)
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located)
    time.sleep(2) 
    return driver.current_url


def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    webdriver_path = './chromedriver'
    driver = webdriver.Chrome(service=webdriver.chrome.service.Service(webdriver_path), options=chrome_options)

    with open('output.csv', 'w', newline='', encoding='utf-8') as f, open('urls.txt', 'r') as url_file:
        writer = csv.writer(f)
        writer.writerow(["URL", "リダイレクト", "404", "リダイレクトURL", "リダイレクトタイトル", "ステータスコード", "PDF", "不要"])
        
        # プログレスバーの設定
        url_list = list(map(str.strip, url_file))
        progress_bar = tqdm(url_list, unit="URL", ncols=80)

        for url in progress_bar:
            try:
                final_url = get_final_url(url, driver)
                status_code = get_status_code(final_url)
                title, title_check = get_title(driver)
                PDF_check = "○" if "pdf" in final_url else ""
                unnecessary_url = "○" if title is None else ""
                redirect_check = "○" if final_url != url else ""
                redirect_title = title if final_url != url else ""
                writer.writerow([url, redirect_check, title_check, final_url if final_url != url else "", redirect_title, status_code, PDF_check, unnecessary_url])
            except Exception as e:
                print(f"Error occurred while processing URL: {url}. Error: {e}")
                writer.writerow([url, "", "", "", "", "500", "", ""])
    driver.quit()

if __name__ == '__main__':
    main()
