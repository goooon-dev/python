import csv
import time
from tqdm import tqdm
import requests
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def is_error_page(driver):
    page_source = driver.page_source
    error_keywords = ["処理エラー", "見つかりません"]
    for keyword in error_keywords:
        if keyword in page_source:
            return True
    return False

def is_text_only_page(driver):
    # 画像が読み込まれるまで待つ
    images = driver.find_elements(By.TAG_NAME, "img")
    return len(images) == 0

def is_image_only_page(driver):
    # body要素が読み込まれるまで待つ
    body_text = driver.find_elements(By.TAG_NAME, "body")[0].text.strip()
    return len(body_text) == 0

def is_garbled_page(driver):
    # ページのソースを取得
    page_source = driver.page_source

    # 文字化けの典型的なパターン
    garbled_keywords = ["�", "ã‚", "ãƒ", "◆"]

    for keyword in garbled_keywords:
        if keyword in page_source:
            return True
    return False

def get_page_info(driver, url):
    driver.get(url)  # ページを開く

    if is_error_page(driver):
        return "エラーページです"
    elif is_garbled_page(driver):
        return "文字化けのページです"
    elif is_text_only_page(driver):
        return "文字のみのページです"
    elif is_image_only_page(driver):
        return "画像のみのページです"
    else:
        return "正常なページです"

def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    webdriver_path = './chromedriver'
    driver = webdriver.Chrome(service=webdriver.chrome.service.Service(webdriver_path), options=chrome_options)

    with open('output.csv', 'w', newline='', encoding='utf-8') as f, open('urls.txt', 'r') as url_file:
        writer = csv.writer(f)
        writer.writerow(["URL", "備考"])
        
        url_list = list(map(str.strip, url_file))
        progress_bar = tqdm(url_list, unit="URL", ncols=80)

        for url in progress_bar:
            try:
                description = get_page_info(driver, url)  # URLを関数に渡す
                writer.writerow([url, description])
            except Exception as e:
                tb = traceback.format_exception_only(type(e), e)
                first_line_of_error = tb[0].strip()
                print(f"Error occurred while processing URL: {url}. Error: {first_line_of_error}")
                writer.writerow([url, "予期せぬエラー: " + first_line_of_error])
    driver.quit()

if __name__ == '__main__':
    main()
