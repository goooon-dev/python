import os
import csv
import re
from dotenv import load_dotenv

def search_keywords_in_html_folder(folder_path, keywords):
    results = []
    
    # フォルダ内のファイルとサブフォルダを走査
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.html'):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    hit_keywords = []
                    for keyword in keywords:
                        pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
                        if pattern.search(content):
                            hit_keywords.append(keyword)
                    if hit_keywords:
                        results.append((file_path, filename, hit_keywords))
    
    return results

def write_results_to_csv(results):
    csv_path = 'Cedyna_html_grep結果.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['フォルダパス', 'ファイル名'] + keywords)  # ヘッダー行を書き込む
        for result in results:
            row = [result[0], result[1]]  # フォルダパスとファイル名を追加
            for keyword in keywords:
                if keyword in result[2]:
                    row.append('○')
                else:
                    row.append('')
            writer.writerow(row)

load_dotenv()
# ローカルフォルダのパスとキーワードを設定
folder_path = os.environ['FOLDER_PATH']
keywords = [
            'hoge'
            ]

# キーワード検索を実行
search_results = search_keywords_in_html_folder(folder_path, keywords)

# 結果をCSVファイルに出力
write_results_to_csv(search_results)
