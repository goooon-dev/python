import os
import csv
from dotenv import load_dotenv

def grep_image_files(folder_path):
    image_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpeg', '.jpg', '.gif')):
                image_paths.append(os.path.join(root, file))
    return image_paths

def write_to_csv(image_paths):
    csv_path = '画像ファイルパス一覧.csv'
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ファイルパス', 'ファイル名'])
        for path in image_paths:
            writer.writerow([os.path.dirname(path), os.path.basename(path)])

load_dotenv()
# フォルダのパスを指定して実行
folder_path = os.environ['FOLDER_PATH']
image_paths = grep_image_files(folder_path)
write_to_csv(image_paths)
