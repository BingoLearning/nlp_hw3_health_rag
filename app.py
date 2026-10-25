from flask import Flask, jsonify, render_template, request

from rag_engine import HealthRAG

app = Flask(__name__)
engine = None


def get_engine():
    global engine
    if engine is None:
        engine = HealthRAG()
    return engine


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/ask")
def ask():
    payload = request.get_json(force=True)
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"error": "問題不可為空"}), 400
    return jsonify(get_engine().ask(question, bool(payload.get("retrieve", True))))


@app.post("/api/summary")
def summary():
    return jsonify({"answer": get_engine().summarize_history(), "sources": []})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

