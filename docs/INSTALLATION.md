# Installation — déployer l'atelier sur une nouvelle machine

Procédure testée le 24/09/2026 sur une installation n8n neuve (import des 4 workflows + résumé
de livre exécuté de bout en bout).

## Ce qu'il faut

| Élément | Minimum | Recommandé |
|---|---|---|
| Mémoire (RAM) | 16 Go | 24-32 Go (moins d'attente entre les modèles) |
| Disque libre | 30 Go (modèles ≈ 25 Go) | 50 Go |
| Processeur | Apple Silicon (M1+) ou carte graphique NVIDIA | — |
| Logiciels | Docker (Desktop sur Mac/Windows), Ollama, Python 3.10+, git | — |

Sur une machine **sans** Apple Silicon ni carte graphique, tout fonctionne mais 5 à 20 fois plus lentement.

---

## Étape 1 — Installer les logiciels (Mac)

```bash
# Homebrew doit être installé (https://brew.sh)
brew install --cask docker     # puis ouvrir Docker Desktop une fois
brew install --cask ollama     # puis ouvrir Ollama une fois
brew install python git gh
```

## Étape 2 — Télécharger les modèles d'IA

```bash
ollama pull gemma4:e4b          # rédacteur, éditeur, lecteur (≈ 10 Go)
ollama pull qwen2.5:7b          # critique et fact-check (≈ 5 Go)
ollama pull deepseek-r1:7b      # critique du Livre complet et du Test 1 (≈ 5 Go)
ollama pull mistral:7b          # mémoire du Livre complet (≈ 4 Go)
ollama pull nomic-embed-text    # recherche dans les briefs (≈ 0,3 Go)

ollama list                     # vérifier
```

Seul le résumé de livre ? `gemma4:e4b` suffit.

## Étape 3 — Récupérer le dépôt

```bash
gh auth login                   # le dépôt est privé : se connecter à GitHub
gh repo clone Naanasba99/atelier-ia-local
cd atelier-ia-local
```

## Étape 4 — Préparer les dossiers

```bash
mkdir -p briefs livres sorties
cp exemples/briefs/*.md briefs/      # puis remplacer par tes propres briefs
```

## Étape 5 — Lancer n8n

> **Nouvelle installation** : ouvre `docker-compose-n8n-local.yml` et, dans la section `volumes`,
> commente la ligne `n8n_sangour3i_data` (le volume de la machine d'origine) et décommente
> `n8n_local_data` (base vierge). Ainsi tu pars d'une instance propre, sans les credentials d'origine.

```bash
docker compose -p n8n-local -f docker-compose-n8n-local.yml up -d
docker ps | grep n8n-local           # doit afficher « Up »
```

Ouvrir **http://localhost:5680** et créer le compte propriétaire (e-mail + mot de passe,
reste local à la machine).

> Le fuseau horaire est réglé sur `America/Mexico_City` dans le compose : l'adapter à ta zone si besoin.

## Étape 6 — Importer les workflows

```bash
./scripts/importer-workflows.sh
```

Les 4 workflows apparaissent dans n8n. Aucun identifiant (clé d'API, mot de passe) n'est nécessaire.

## Étape 7 — Service fact-check (pour l'Atelier Express)

```bash
cd factcheck
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python indexer_faits.py     # indexe les briefs → affiche « Terminé : N passages »
venv/bin/python verif_service.py     # laisse tourner ; test : curl localhost:5077/health
```

## Étape 8 — Premier test (résumé d'un livre libre de droits)

```bash
curl -L -o livres/candide.txt https://www.gutenberg.org/cache/epub/4650/pg4650.txt
```

Dans n8n : **Atelier Lecture — Résumé de livre** → node **PARAMÈTRES** → `fichier: "candide.txt"`
→ Cmd+S → **Execute workflow**. Après ~11 min, le fichier `sorties/resume-candide-...md` apparaît.

---

## Variante Linux (serveur, VPS, PC)

Sur Linux, `host.docker.internal` n'existe pas d'office et les services qui écoutent sur `127.0.0.1`
ne sont pas joignables depuis Docker. Trois réglages :

1. **Le compose** contient déjà `extra_hosts: host.docker.internal:host-gateway` → rien à faire.
2. **Ollama** doit écouter sur l'interface Docker :
   ```bash
   sudo systemctl edit ollama
   # ajouter :
   # [Service]
   # Environment="OLLAMA_HOST=0.0.0.0"
   sudo systemctl restart ollama
   ```
   ⚠️ Ollama devient alors joignable depuis le réseau : **bloquer le port 11434** de l'extérieur
   (ex. `sudo ufw deny 11434` puis `sudo ufw allow from 172.16.0.0/12 to any port 11434`).
3. **Le fact-check** : lancer `FACTCHECK_HOST=172.17.0.1 venv/bin/python verif_service.py`
   (172.17.0.1 = adresse du Mac/serveur vue depuis Docker ; vérifier avec `ip addr show docker0`).

## Variante serveur distant (VPS)

- Ne **jamais** ouvrir le port 5679 sur Internet. Accéder à n8n par tunnel :
  `ssh -L 5679:localhost:5679 utilisateur@serveur` puis ouvrir http://localhost:5679 sur son poste,
  ou via Tailscale.
- Sans carte graphique, prévoir des temps très longs : préférer un modèle plus petit
  (ex. `qwen2.5:3b`) en changeant la ligne `model:` des nodes concernés.

---

## Mettre à jour / sauvegarder

```bash
# Après une modification dans n8n : enregistrer les workflows dans le dépôt
./scripts/exporter-workflows.sh
git add workflows && git commit -m "Mise à jour des workflows" && git push

# Mettre à jour n8n
docker compose -p atelier-ecriture -f docker-compose-n8n-atelier.yml pull
docker compose -p atelier-ecriture -f docker-compose-n8n-atelier.yml up -d
```

Les données de n8n (comptes, historique) vivent dans le volume Docker `atelier-ecriture_n8n_atelier_data`.
Les workflows, eux, sont dans le dépôt : même si le volume est perdu, une réinstallation + l'étape 6 suffit.
