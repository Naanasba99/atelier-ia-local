#!/usr/bin/env python3
"""
verif_service.py — Mini-service de vérification pour le Fact-Checker.
Reçoit une affirmation, renvoie les 3 passages du corpus les plus proches.
Le jugement (confirmé/contredit/absent) est fait côté n8n par le LLM.

Usage : python verif_service.py   (laisser tourner pendant les exécutions)
Test  : curl http://localhost:5077/health
"""
import os
import requests
import chromadb
from flask import Flask, request, jsonify

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma")
OLLAMA_EMBED = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
COLLECTION = "faits_valides"
PORT = 5077
# 127.0.0.1 par défaut. Sur Linux, mettre FACTCHECK_HOST=172.17.0.1 (voir docs/INSTALLATION.md)
HOST = os.environ.get("FACTCHECK_HOST", "127.0.0.1")

app = Flask(__name__)
client = chromadb.PersistentClient(path=DB_DIR)
coll = client.get_or_create_collection(COLLECTION)


@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json(silent=True) or {}
    claim = (data.get("claim") or "").strip()
    if not claim:
        return jsonify({"error": "champ 'claim' manquant"}), 400

    try:
        r = requests.post(OLLAMA_EMBED, json={"model": EMBED_MODEL, "prompt": claim}, timeout=120)
        r.raise_for_status()
        emb = r.json()["embedding"]
    except Exception as e:
        return jsonify({"error": f"embedding impossible : {e}"}), 502

    n = min(3, max(coll.count(), 1))
    res = coll.query(query_embeddings=[emb], n_results=n)

    passages = []
    if res["documents"] and res["documents"][0]:
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
            passages.append({
                "texte": doc,
                "source": (meta or {}).get("source", "?"),
                "distance": round(dist, 3)
            })

    return jsonify({"claim": claim, "passages": passages, "corpus_total": coll.count()})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "documents_indexes": coll.count()})


if __name__ == "__main__":
    # 127.0.0.1 suffit sur Docker Desktop (Mac/Windows) : host.docker.internal y mène.
    print(f"Fact-check service sur http://localhost:{PORT} — corpus : {coll.count()} passages")
    app.run(host=HOST, port=PORT)
