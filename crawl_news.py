import argparse
import json
import random
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import DEFAULT_CHANNEL, HEALTHNEWS_BASE, RAW_JSON

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NLP-course-homework/1.0"}


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_listing(html: str):
    soup = BeautifulSoup(html, "lxml")
    rows = []
    for item in soup.select("ul.list-unstyled > li.list-item"):
        anchor = item.select_one("div.list-title > a[href]")
        info = item.select_one("div.list-info")
        if not anchor:
            continue
        info_text = clean_text(info.get_text(" ", strip=True)) if info else ""
        date_match = re.search(r"(20\d{2}-\d{1,2}-\d{1,2})", info_text)
        rows.append({
            "link": urljoin(HEALTHNEWS_BASE, anchor["href"]),
            "published_at": date_match.group(1) if date_match else "",
        })
    return rows


def parse_article(html: str, metadata: dict):
    soup = BeautifulSoup(html, "lxml")
    title_node = soup.select_one("div#article-title a") or soup.select_one("h1")
    content_node = soup.select_one("div#article-content")
    if not title_node or not content_node:
        raise ValueError("找不到文章標題或全文")
    return {
        **metadata,
        "title": clean_text(title_node.get_text(" ", strip=True)),
        "content": clean_text(content_node.get_text(" ", strip=True)),
    }


def crawl(pages=2, max_articles=20, delay=1.0, channel=DEFAULT_CHANNEL):
    session = requests.Session()
    session.headers.update(HEADERS)
    listings = []
    for page in range(1, pages + 1):
        url = f"{HEALTHNEWS_BASE}/channel/{channel}/{page}"
        response = session.get(url, timeout=30)
        response.raise_for_status()
        listings.extend(parse_listing(response.text))
        time.sleep(delay)
    unique = list({row["link"]: row for row in listings}.values())[:max_articles]
    articles = []
    for index, row in enumerate(unique, start=1):
        response = session.get(row["link"], timeout=30)
        response.raise_for_status()
        articles.append(parse_article(response.text, row))
        print(f"[{index}/{len(unique)}] {articles[-1]['title']}")
        time.sleep(delay + random.uniform(0, 0.5))
    RAW_JSON.parent.mkdir(parents=True, exist_ok=True)
    RAW_JSON.write_text(json.dumps(articles, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(articles)} articles: {RAW_JSON}")
    return articles


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=2)
    parser.add_argument("--max-articles", type=int, default=20)
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()
    crawl(args.pages, args.max_articles, args.delay)

