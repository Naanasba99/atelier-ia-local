# Atelier Écriture & Lecture — IA 100 % locale

Un atelier qui **écrit** et **résume** des textes avec des modèles d'IA qui tournent **sur ta propre machine**.
Aucune donnée ne part dans le cloud, aucun abonnement, aucune clé d'API.

Il est construit avec trois briques gratuites :

| Brique | Rôle | En une phrase |
|---|---|---|
| **Ollama** | le « cerveau » | Fait tourner les modèles d'IA (gemma4, qwen2.5…) sur le Mac |
| **n8n** (dans Docker) | le « chef d'orchestre » | Enchaîne les étapes : qui parle à quel modèle, dans quel ordre, avec quels contrôles |
| **Service fact-check** (Python + ChromaDB) | la « mémoire des faits » | Retrouve dans tes briefs les passages qui confirment ou contredisent une phrase |

---

## Les 4 workflows

| # | Workflow | Ce qu'il fait | Durée typique |
|---|---|---|---|
| 01 | **Atelier Lecture — Résumé de livre** | Lit un livre (PDF, TXT, MD) et produit une fiche de résumé avec citations vérifiées | ~1 min par 20 000 caractères (≈ 30-40 min pour 300 pages) |
| 02 | **Atelier Express** | Écrit un texte court (post, article, email) à partir d'une demande, le fait critiquer, vérifie les faits, puis le polit | 8-15 min |
| 03 | **Atelier Livre complet** | Écrit un livre entier à partir d'un brief : plan, chapitres, critique, édition | plusieurs heures |
| 04 | **Test 1 Chapitre** | Banc d'essai : un seul chapitre, pour tester des prompts ou des modèles | ~3 min |

**L'idée centrale à retenir** — et à expliquer :

> Un seul modèle d'IA qui écrit « d'un coup » invente, oublie des points et dérive.
> L'atelier découpe le travail en **rôles spécialisés** (rédacteur, critique, vérificateur, éditeur),
> chacun avec des consignes strictes, et place entre eux des **contrôles écrits en code** (le GATE)
> qui ne se laissent pas convaincre par un texte bien tourné.
> Les notes des IA mesurent la **forme** ; seuls le code et la relecture humaine garantissent les **faits**.

---

## Démarrage rapide (machine déjà installée)

```bash
# 1. Ollama tourne ? (doit lister des modèles)
curl -s localhost:11434/api/tags | head -c 200

# 2. n8n tourne ? Sinon le lancer :
docker ps | grep n8n-atelier || docker compose -p atelier-ecriture -f docker-compose-n8n-atelier.yml up -d

# 3. Pour l'Atelier Express uniquement : le service fact-check (laisser ce terminal ouvert)
cd factcheck && venv/bin/python verif_service.py

# 4. Empêcher la veille pendant les longs traitements (Ctrl+C à la fin)
caffeinate -i
```

Puis : ouvrir **http://localhost:5679** → choisir un workflow → **double-cliquer sur le node de demande**
(2ᵉ node en partant de la gauche) → écrire ta demande → **Cmd+S** → **Execute workflow**.
Le résultat arrive dans le dossier `sorties/`.

➡️ Guide complet : [docs/UTILISATION.md](docs/UTILISATION.md)

---

## Documentation

| Document | Pour qui / pour quoi |
|---|---|
| [docs/UTILISATION.md](docs/UTILISATION.md) | **Utiliser** l'atelier au quotidien : quoi écrire dans quel node |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | **Comprendre et expliquer** comment c'est monté, étape par étape, avec schémas |
| [docs/INSTALLATION.md](docs/INSTALLATION.md) | **Déployer** sur une nouvelle machine (Mac, Linux, serveur) |
| [docs/DEPANNAGE.md](docs/DEPANNAGE.md) | **Réparer** : les pannes déjà rencontrées et leur solution |

---

## Contenu du dépôt

```
atelier-ecriture/
├── README.md                          ← tu es ici
├── docker-compose-n8n-atelier.yml     ← définition du conteneur n8n
├── workflows/                         ← les 4 workflows n8n (à importer)
│   ├── 01-atelier-lecture-resume-de-livre.json
│   ├── 02-atelier-express-fact-checker.json
│   ├── 03-atelier-livre-complet.json
│   └── 04-atelier-test-1-chapitre.json
├── factcheck/                         ← service de vérification des faits
│   ├── verif_service.py               ← petit serveur web (port 5077)
│   ├── indexer_faits.py               ← range les briefs dans la base ChromaDB
│   └── requirements.txt
├── scripts/
│   ├── importer-workflows.sh          ← dépôt → n8n
│   ├── exporter-workflows.sh          ← n8n → dépôt (après chaque modification)
│   └── nettoyer_export.py             ← retire les données personnelles des exports
├── exemples/briefs/                   ← modèle de brief + un exemple complet
├── docs/                              ← documentation
├── briefs/    (non versionné)         ← TES briefs : les faits de référence
├── livres/    (non versionné)         ← livres à résumer
└── sorties/   (non versionné)         ← textes produits
```

**Ce qui n'est volontairement pas dans le dépôt** : tes briefs et ta prose (dépôt séparé
`atelier-briefs` sur le Gitea local), les textes produits, les livres (droits d'auteur),
les sauvegardes n8n (elles contiennent la clé de chiffrement), l'environnement Python et la base ChromaDB
(ils se reconstruisent en une commande).

---

## Matériel et limites honnêtes

- **Matériel testé** : Mac M4, 16 Go de RAM. Un seul gros modèle tient en mémoire à la fois ;
  le passage d'un modèle à l'autre coûte 20 à 30 s.
- **Qualité** : bonne structure, fidèle au plan, mais plume inférieure aux grands modèles du cloud.
  Les résumés sont justes sur le fond et peuvent se tromper sur des détails (lieux, qui fait quoi).
  Sur un livre **célèbre**, le modèle peut compléter avec ce qu'il sait déjà du livre au lieu de s'en
  tenir au texte fourni.
- **Fact-checker** : il attrape des inventions (surtout celles avec un nom propre ou un chiffre),
  mais pas toutes. **La relecture humaine reste obligatoire avant toute publication.**
- **Livre complet** : jamais exécuté en entier à ce jour ; son critique (deepseek-r1) n'a pas reçu
  la correction appliquée à l'Express (voir [DEPANNAGE](docs/DEPANNAGE.md)).

---

*Historique : conçu en juillet 2026 (workflows Express, Livre complet, Test 1). Remis en service et
complété le 24/09/2026 : workflow de résumé de livre, critique et fact-checker de l'Express corrigés,
conteneur recâblé sur les bons dossiers, documentation et dépôt.*
