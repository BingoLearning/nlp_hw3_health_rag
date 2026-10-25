import sqlite3

import faiss
from sentence_transformers import SentenceTransformer

from config import DB_FILE, EMBEDDING_MODEL, INDEX_FILE
from local_llm import LocalLLM


class HealthRAG:
    def __init__(self):
        self.encoder = SentenceTransformer(EMBEDDING_MODEL, device="cuda")
        self.index = faiss.read_index(str(INDEX_FILE))
        self.llm = LocalLLM()
        self.history = []

    def retrieve(self, question, k=3):
        vector = self.encoder.encode([question], normalize_embeddings=True).astype("float32")
        scores, ids = self.index.search(vector, k)
        found = []
        with sqlite3.connect(DB_FILE) as connection:
            for news_id, score in zip(ids[0], scores[0]):
                if int(news_id) < 0:
                    continue
                row = connection.execute(
                    "SELECT id,title,link,content,summary,published_at,created_at FROM news WHERE id=?",
                    (int(news_id),),
                ).fetchone()
                if row:
                    found.append(dict(zip(
                        ["id", "title", "link", "content", "summary", "published_at", "created_at"], row
                    )) | {"score": float(score)})
        return found

    def ask(self, question, retrieve=True):
        sources = self.retrieve(question) if retrieve else []
        context = "\n\n".join(
            f"[新聞{i}] 標題：{row['title']}\n發布：{row['published_at']}\n摘要：{row['summary']}\n全文：{row['content'][:2200]}"
            for i, row in enumerate(sources, start=1)
        )
        messages = [{
            "role": "system",
            "content": (
                "你是健康新聞諮詢小幫手。只根據提供的新聞回答，資料不足就明說；"
                "不用新聞取代醫師診斷。使用台灣繁體中文。請直接回答問題，至少寫三個完整句子，"
                "不得只重複新聞標題。"
            ),
        }]
        messages.extend(self.history[-6:])
        prompt = question
        if retrieve:
            prompt = (
                "以下是檢索到的新聞資料：\n" + context
                + f"\n\n問題：{question}\n請綜合上面資料直接回答；不要只輸出標題。"
            )
        messages.append({"role": "user", "content": prompt})
        answer = self.llm.generate(messages, max_new_tokens=320)
        self.history.extend([
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ])
        return {"answer": answer, "sources": sources}

    def summarize_history(self):
        messages = [{"role": "system", "content": "把使用者剛才詢問的問題與回答整理成繁體中文重點條列。"}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": "請整理剛才詢問的問題與重要結論。"})
        return self.llm.generate(messages, max_new_tokens=300)

