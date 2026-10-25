# 作業三：本機健康新聞 RAG 諮詢小幫手

爬取老師指定的「健康醫療網」新聞分類，使用本機模型產生摘要，以 `BAAI/bge-m3` 建立 FAISS cosine-similarity 向量索引，再由本機 Qwen 模型依檢索內容回答。網頁上的 checkbox 可決定該輪是否檢索。

新聞、摘要、回答與實驗結果均為 2026-10-25 在本機實際流程產生。

## 模型選擇

- 向量模型：老師 RAG 範例指定 `BAAI/bge-m3`，因此不替換。
- 生成與摘要模型：`Qwen/Qwen2.5-0.5B-Instruct`。老師的語言模型微調範例明確使用此模型，而且 0.5B FP16 可在 RTX 2060 6 GB 本機執行；同一份模型快取亦可避免再下載較大的模型。
- 全流程在 Windows 本機執行，不呼叫雲端生成 API。

## 資料表

SQLite `news` 至少包含流水號 `id`、新聞標題 `title`、新聞連結 `link`、文章全文 `content`、文章摘要 `summary`、新聞發布時間 `published_at`、文章新增時間 `created_at`。

## Windows 執行

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python crawl_news.py --pages 2 --max-articles 20 --delay 1
.\.venv\Scripts\python build_database.py
.\.venv\Scripts\python build_index.py
.\.venv\Scripts\python verify_demo.py
.\.venv\Scripts\python app.py
```

瀏覽器開啟 <http://127.0.0.1:5000>。每次回答後，頁面會條列顯示檢索的新聞標題、連結、新聞發布時間與資料入庫時間。「整理重點」會將前兩輪問題與回答整理成重點。

## 實際成果

從分類頁前兩頁實際取得 16 篇不重複文章；每篇均已由本機 Qwen 產生摘要並寫入 SQLite。`BAAI/bge-m3` 已為 16 篇文章建立 1,024 維正規化向量與 FAISS inner-product（cosine）索引。

兩輪實際 RAG 驗證已完成，包含每輪三筆來源的新聞標題、連結、發布時間與新增時間。第一題回答指出早期可能無症狀及瘜肉偵測的重要性；第二題實際列出大腸鏡、糞便潛血、TNT 治療等檢查或治療方向。模型原始回答與最後整理完整保留於 `results/verification.json`，未人工改寫。

實際爬取資料位於 `data/news_raw.json` 與 `data/news.db`，向量索引位於 `data/vector.index`，網頁可勾選是否使用檢索，並可在至少兩輪問答後整理問題重點。

## 驗證環境

Windows 11、AMD Ryzen 7 3700X（8C/16T）、15.93 GB RAM、NVIDIA RTX 2060 6 GB、驅動 572.60（CUDA 12.8）、Python 3.12.10、Git 2.55。新聞摘要、向量化、兩輪問答與問題整理均在本機完成，未呼叫雲端生成 API。

## 注意

這是新聞檢索與內容整理示範，不能取代醫師診斷；爬蟲設定固定延遲並限制頁數與筆數，避免對來源網站造成負擔。
