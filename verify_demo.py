import json
import sys

from config import RESULTS_DIR
from rag_engine import HealthRAG

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    engine = HealthRAG()
    questions = [
        "近期大腸癌新聞提到哪些容易被忽略的警訊？",
        "這些報導提到哪些檢查或治療方向？",
    ]
    results = []
    for question in questions:
        result = engine.ask(question, retrieve=True)
        results.append({"question": question, **result})
        print(f"問題：{question}\n回答：{result['answer']}")
        for source in result["sources"]:
            print(
                f"- {source['title']} | {source['link']} | "
                f"發布：{source['published_at']} | 新增：{source['created_at']}"
            )
    final_summary = engine.summarize_history()
    payload = {"turns": results, "final_summary": final_summary}
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "verification.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\n問題整理：" + final_summary)


if __name__ == "__main__":
    main()

