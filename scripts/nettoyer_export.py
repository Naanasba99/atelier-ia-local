#!/usr/bin/env python3
"""
Nettoie les exports n8n avant de les mettre dans le dépôt.
  - garde uniquement ce qui sert à réimporter (id, nom, nodes, connexions, réglages)
  - retire l'e-mail du propriétaire, la mémoire interne (staticData), les versions
  - remplace l'échantillon de prose personnelle par un texte à compléter
  - ignore les workflows archivés (supprimés dans l'interface)
  - nomme les fichiers de façon lisible : 01-atelier-express.json, etc.
Usage : python3 nettoyer_export.py <dossier_export_brut> <dossier_workflows>
"""
import json, os, re, sys, glob

NOMS = {  # id n8n -> nom de fichier dans le dépôt
    "ResumeLivreLoc01": "01-atelier-lecture-resume-de-livre.json",
    "88ccIy5TWBBJBYSQ": "02-atelier-express-fact-checker.json",
    "txEGIeW6qVQOjLdq": "03-atelier-livre-complet.json",
    "rzsnAfjmSxltwvDT": "04-atelier-test-1-chapitre.json",
}
PLACEHOLDER = ("(aucun échantillon) COLLE ICI 2 À 3 PAGES DE TA PROPRE PROSE à la place de cette phrase. "
               "L'Éditeur imitera ce style. Tant que cette phrase est là, l'Éditeur se contente de fluidifier le texte.")

src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)

for f in sorted(glob.glob(os.path.join(src, "*.json"))):
    w = json.load(open(f, encoding="utf-8"))
    if w.get("isArchived"):
        continue
    for n in w["nodes"]:
        code = n.get("parameters", {}).get("jsCode")
        if code and "echantillon_style" in code:
            code = re.sub(r"(echantillon_style\s*[=:]\s*)`[\s\S]*?`",
                          lambda m: m.group(1) + "`" + PLACEHOLDER + "`", code)
            n["parameters"]["jsCode"] = code
    propre = {
        "id": w["id"],
        "name": w["name"],
        "nodes": w["nodes"],
        "connections": w["connections"],
        "settings": w.get("settings", {}),
        "pinData": {},
        "active": False,
    }
    nom = NOMS.get(w["id"], re.sub(r"[^a-z0-9]+", "-", w["name"].lower()).strip("-") + ".json")
    with open(os.path.join(dst, nom), "w", encoding="utf-8") as out:
        json.dump(propre, out, ensure_ascii=False, indent=2)
        out.write("\n")
    print("  ✓", nom, "—", w["name"])
