import json
import sqlite3
import sys
from datetime import datetime

from config import DB_FILE, RAW_JSON
from local_llm import LocalLLM

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCHEMA = """
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    link TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    summary TEXT NOT NULL,
    published_at TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


def summarize(llm, title, content):
    messages = [
        {"role": "system", "content": "你是繁體中文健康新聞摘要助手。只依據文章內容，以一段約120字文字整理重點，不提供診斷。"},
        {"role": "user", "content": f"標題：{title}\n文章：{content[:6000]}"},
    ]
    return llm.generate(messages, max_new_tokens=220)


def build_database():
    rows = json.loads(RAW_JSON.read_text(encoding="utf-8"))
    llm = LocalLLM()
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_FILE) as connection:
        connection.execute(SCHEMA)
        for index, row in enumerate(rows, start=1):
            existing = connection.execute(
                "SELECT summary FROM news WHERE link = ?", (row["link"],)
            ).fetchone()
            summary = existing[0] if existing else summarize(llm, row["title"], row["content"])
            connection.execute(
                """INSERT INTO news(title, link, content, summary, published_at, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(link) DO UPDATE SET title=excluded.title, content=excluded.content,
                   summary=excluded.summary, published_at=excluded.published_at""",
                (row["title"], row["link"], row["content"], summary,
                 row["published_at"], datetime.now().isoformat(timespec="seconds")),
            )
            connection.commit()
            print(f"[{index}/{len(rows)}] {row['title']}\n摘要：{summary}\n")
    print(f"Database: {DB_FILE}")


if __name__ == "__main__":
    build_database()

