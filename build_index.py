import sqlite3

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config import DB_FILE, EMBEDDING_MODEL, INDEX_FILE, INDEX_IDS_FILE


def build_index():
    with sqlite3.connect(DB_FILE) as connection:
        rows = connection.execute("SELECT id, title, summary FROM news ORDER BY id").fetchall()
    if not rows:
        raise RuntimeError("資料庫沒有新聞")
    ids = np.asarray([row[0] for row in rows], dtype="int64")
    documents = [f"{row[1]}。{row[2]}" for row in rows]
    encoder = SentenceTransformer(EMBEDDING_MODEL, device="cuda" if __import__("torch").cuda.is_available() else "cpu")
    embeddings = encoder.encode(
        documents, batch_size=4, show_progress_bar=True,
        normalize_embeddings=True, convert_to_numpy=True,
    ).astype("float32")
    index = faiss.IndexIDMap(faiss.IndexFlatIP(embeddings.shape[1]))
    index.add_with_ids(embeddings, ids)
    faiss.write_index(index, str(INDEX_FILE))
    np.save(INDEX_IDS_FILE, ids)
    print(f"Indexed {index.ntotal} articles with {EMBEDDING_MODEL}: {INDEX_FILE}")


if __name__ == "__main__":
    build_index()

