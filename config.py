from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RAW_JSON = DATA_DIR / "news_raw.json"
DB_FILE = DATA_DIR / "news.db"
INDEX_FILE = DATA_DIR / "vector.index"
INDEX_IDS_FILE = DATA_DIR / "vector_ids.npy"
RESULTS_DIR = ROOT / "results"
HEALTHNEWS_BASE = "https://www.healthnews.com.tw"
DEFAULT_CHANNEL = "9b508eee-a171-75b6-0963-eec4e463fc46"
EMBEDDING_MODEL = "BAAI/bge-m3"
GENERATION_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

