#!/usr/bin/env python3
"""
indexer_faits.py — Indexe les briefs dans ChromaDB pour le Fact-Checker.
À relancer après chaque modification des briefs (ou après chaque commit).
Usage : python indexer_faits.py
"""
import os, glob, hashlib, requests, chromadb

BRIEFS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "briefs")
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma")
OLLAMA_EMBED = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
COLLECTION = "faits_valides"

def embed(text: str):
    r = requests.post(OLLAMA_EMBED, json={"model": EMBED_MODEL, "prompt": text}, timeout=120)
    r.raise_for_status()
    return r.json()["embedding"]

def chunks_from_markdown(text: str):
    """Découpe en paragraphes + lignes de faits (les tirets des sections Faits validés)."""
    out = []
    for bloc in text.split("\n\n"):
        bloc = bloc.strip()
        if len(bloc) < 30:
            continue
        # Les listes de faits : une ligne = un fait = un chunk (précision maximale)
        lignes_faits = [l.strip("- ").strip() for l in bloc.split("\n") if l.strip().startswith("-")]
        if lignes_faits:
            out.extend([l for l in lignes_faits if len(l) > 20])
        else:
            out.append(bloc)
    return out

def main():
    client = chromadb.PersistentClient(path=DB_DIR)
    # Réindexation complète idempotente : on repart de zéro à chaque run
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    coll = client.get_or_create_collection(COLLECTION)

    fichiers = [p for p in glob.glob(os.path.join(BRIEFS_DIR, "*.md"))
                if os.path.basename(p) not in ("style-reference.md", "_template.md")]
    if not fichiers:
        print("Aucun brief trouvé dans", BRIEFS_DIR)
        return

    total = 0
    for path in fichiers:
        nom = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            texte = f.read()
        for i, chunk in enumerate(chunks_from_markdown(texte)):
            uid = hashlib.md5(f"{nom}:{i}:{chunk}".encode()).hexdigest()
            coll.add(ids=[uid], documents=[chunk],
                     metadatas=[{"source": nom}], embeddings=[embed(chunk)])
            total += 1
        print(f"  {nom} : indexé")

    print(f"\nTerminé : {total} passages dans la collection '{COLLECTION}'.")
    print(f"Base : {DB_DIR}")

if __name__ == "__main__":
    main()
