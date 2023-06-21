## 概要
嫁に依頼されて作った
URLの一覧（urls.txt）からリンク切れ、リダイレクト有無、404ページ有無をCSVへ出力する

## ライブラリインストール
pip install -r requirements.txt

## 準備
- urls.txtを作成し調査したいurlを設定する（sample_urls.txt参考）

## 実行
- python CheckURLs.py
- 結果が同じディレクトリにresult.csvで出力される（sample_result.csv参考）