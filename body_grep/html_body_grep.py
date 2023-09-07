import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup, Comment
from dotenv import load_dotenv
from tqdm import tqdm
import re
import os


def extract_body_without_script(url, check_keywords):
    load_dotenv()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    webdriver_path = os.environ['CHROME_DRIVER_PATH']
    driver = webdriver.Chrome(service=webdriver.chrome.service.Service(webdriver_path), options=chrome_options)
    driver.get(url)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    
    for script in soup("script"):
        script.decompose()

    for comment in soup.findAll(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    for div in soup.find_all('div', style='display: none;'):
        div.decompose()

    for element in soup.find_all(True):
        if element.name is None:
            continue

        xpath = '//' + element.name
        for name, value in element.attrs.items():
            if name and value:
                xpath += f'[@{name}="{value}"]'
    
        try:
            selenium_element = driver.find_element(By.XPATH, xpath)
            if selenium_element.value_of_css_property("display") == "none":
                # element自体と、その子要素を全て削除する
                element.decompose()
        except:
            continue

    if soup.body:
        text = soup.body.get_text().replace("\n", " ")
    else:
        text = ""

    keyword_contexts = []

    for entry in check_keywords:
        keyword = entry["keyword"]
        correct_word = entry["correct_word"]
        for m in re.finditer(re.escape(keyword), text):
            start_idx = m.start()
            end_idx = m.end()
            
            # 前方10文字の境界を取得
            start_boundary = max(0, start_idx - 20)
            # 後方10文字の境界を取得
            end_boundary = min(len(text), end_idx + 20)
            
            # バウンダリが見つからない場合の対応
            if start_boundary == -1:
                start_boundary = 0
            if end_boundary == -1:
                end_boundary = len(text)
            
            context = text[start_boundary:end_boundary].strip()
            keyword_contexts.append((url, keyword, correct_word, context))

    driver.close()
    return keyword_contexts

def main():
    check_keywords = [
        {"keyword": "hoge", "correct_word": "huga"},
    ]
    results = []

    try:
        with open("urls.txt", "r") as file:
            urls = [line.strip() for line in file]

        for url in tqdm(urls, desc="Processing URLs"):
            keyword_contexts = extract_body_without_script(url, check_keywords)
            for url, keyword, correct_word, context in keyword_contexts:
                # すでに同じURL、キーワード、コンテキストの組み合わせがresultsに存在しないかチェック
                if (url, keyword, correct_word, context) not in results:
                    results.append((url, keyword, correct_word, context))

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # CSVに出力
        with open("results.csv", "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["url", "keyword", "correct_word", "context"])
            writer.writerows(results)

if __name__ == "__main__":
    main()
