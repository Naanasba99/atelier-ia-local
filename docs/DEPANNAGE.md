# Dépannage — pannes rencontrées et solutions

Chaque entrée ci-dessous a réellement eu lieu. Symptôme → cause → solution.

## n8n ne trouve pas les fichiers / les dossiers sont vides

- **Symptôme** : `livres/`, `briefs/` ou `sorties/` vus comme vides par n8n ; fichiers produits introuvables.
- **Cause** (septembre 2026) : le dossier de l'atelier avait été déplacé, mais le conteneur avait été
  recréé en pointant vers l'ancien emplacement. Docker a alors créé des dossiers vides.
- **Solution** : toujours lancer le conteneur **depuis le dossier du dépôt** avec le compose :
  ```bash
  docker rm -f n8n-atelier-ecriture
  docker compose -p atelier-ecriture -f docker-compose-n8n-atelier.yml up -d
  docker inspect n8n-atelier-ecriture --format '{{range .Mounts}}{{.Source}} → {{.Destination}}{{println}}{{end}}'
  ```
  Les workflows ne sont pas perdus : ils vivent dans le volume `atelier-ecriture_n8n_atelier_data`.

## « Access to the file is not allowed » / écriture refusée

- **Cause** : n8n 2.x limite l'accès aux fichiers à son dossier interne.
- **Solution** : variable `N8N_RESTRICT_FILE_ACCESS_TO` dans le compose (déjà présente). Tout nouveau
  dossier monté doit y être ajouté, séparé par `;`.

## « Critique illisible : texte validé sans évaluation »

- **Cause** : le modèle critique (deepseek-r1) rendait un JSON valide mais mal rangé (notes hors de `scores`).
- **Solution appliquée à l'Express** : critique remplacé par `qwen2.5:7b` + schéma JSON imposé via le
  paramètre `format` d'Ollama ; le GATE récupère aussi les notes mal rangées.
- **Encore à faire** : Livre complet et Test 1 utilisent toujours deepseek-r1 → même correction à appliquer
  (copier le node « Préparer requête Critique » et le début du node GATE de l'Express).

## Le fact-checker ne vérifie rien (« aucun [VERIF] dans le texte »)

- **Cause** : le Rédacteur perdait ses marqueurs `[VERIF]` en réécrivant.
- **Solution appliquée** : le fact-checker repère désormais lui-même les affirmations factuelles
  (en plus des `[VERIF]`) ; la consigne du Rédacteur exige de garder les marqueurs.

## Tout sort « absent » au fact-check

- **Causes possibles** :
  1. le service fact-check n'est pas lancé → `curl localhost:5077/health` ;
  2. les briefs ne sont pas indexés → `cd factcheck && venv/bin/python indexer_faits.py` ;
  3. (historique) les scripts pointaient vers un ancien dossier : ils utilisent maintenant des chemins
     relatifs à leur propre emplacement.

## Le résumé d'un gros livre échoue en « timeout »

- **Cause** : sans boucle, n8n envoyait tous les morceaux à Ollama en même temps.
- **Solution appliquée** : le node « Boucle lecture » envoie un morceau à la fois.

## « Presque aucun texte extrait »

- **Cause** : PDF scanné (des images, pas de texte).
- **Solution** : faire un OCR d'abord (ex. `ocrmypdf entree.pdf sortie.pdf`), ou utiliser une version texte/EPUB convertie.

## « n8n Task Broker's port 5679 is already in use »

- **Cause** : lancement d'un workflow en ligne de commande (`n8n execute`) pendant que n8n tourne.
- **Solution** : ajouter `-e N8N_RUNNERS_BROKER_PORT=5691` à la commande `docker exec`.

## Ollama injoignable depuis n8n

```bash
docker exec n8n-atelier-ecriture wget -qO- http://host.docker.internal:11434/api/version
```
- Rien ne répond sur Mac : Ollama n'est pas lancé (ouvrir l'application).
- Sur Linux : voir [INSTALLATION.md](INSTALLATION.md), section Linux.

## Message « Failed to start Python task runner »

Sans conséquence : l'atelier n'utilise que des nodes de code JavaScript.

## Restaurer depuis une sauvegarde

Les workflows du dépôt suffisent : `./scripts/importer-workflows.sh`.
Pour restaurer la base complète (comptes, historique), il faut `database.sqlite` **et** le fichier
`config` (clé de chiffrement) du dossier `/home/node/.n8n` — c'est pourquoi les dossiers
`backup-n8n-*` ne doivent jamais être publiés.
