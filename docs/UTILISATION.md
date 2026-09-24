# Utilisation — le guide du quotidien

## Avant chaque session

```bash
curl -s localhost:11434/api/tags | head -c 200     # Ollama répond ?
docker ps | grep n8n-atelier                        # n8n tourne ?
# sinon : docker compose -p atelier-ecriture -f docker-compose-n8n-atelier.yml up -d

# Atelier Express uniquement (laisser ce terminal ouvert) :
cd factcheck && venv/bin/python verif_service.py

# Longs traitements (autre terminal, Ctrl+C à la fin) :
caffeinate -i
```

Pour libérer de la mémoire : fermer les autres applications IA (Open WebUI, LM Studio…).

## La méthode, identique pour tous les workflows

1. Ouvrir **http://localhost:5679** et se connecter.
2. Cliquer sur le **workflow**.
3. **Double-cliquer sur le node de demande** (2ᵉ node en partant de la gauche).
4. Modifier **uniquement le texte** entre guillemets `"..."` ou entre backticks `` `...` ``. Fermer.
5. **Cmd+S** pour enregistrer.
6. **Execute workflow** (bouton en bas). Les nodes passent au vert un à un.
7. Résultat : **double-cliquer sur le dernier node de code** (RÉSULTAT FINAL / GATE), et/ou ouvrir le fichier dans `sorties/`.

⚠️ Ne jamais toucher à `const ... =`, aux backticks `` ` ``, au `;`, au `return`.
Ne jamais écrire de backtick `` ` `` ni `${` dans son texte.

> Sans modifier le node, « Execute » relance la **dernière demande enregistrée**.

## Quoi écrire dans chaque workflow

### 01 · Résumé de livre — node `PARAMÈTRES (écris ici)`

1. Déposer le livre dans `livres/` (`.pdf` avec du texte, `.txt`, `.md` ; un `.epub` se convertit en `.txt` avec Calibre).
2. Remplir :
   ```js
   fichier: "mon-livre.pdf",
   niveau: "detaille",          // "court" = 1 page ; "detaille" = fiche complète + annexes
   consigne: "",                // facultatif, ex. "insiste sur les idées de management"
   modele: "gemma4:e4b"
   ```
3. Résultat : `sorties/resume-<titre>-<date>.md`.

### 02 · Atelier Express — node `TA DEMANDE (écris ici)`

Entre les backticks de `demande`, écrire comme à une personne :
- **ce que tu veux** (type de texte, longueur) ;
- **les faits à utiliser**, en liste, suivis de « n'invente rien d'autre » ;
- **le ton** et **la structure**.

Facultatif : remplacer le texte de `echantillon_style` par 2-3 pages de ta propre prose pour que l'Éditeur imite ton style.

Résultat : `sorties/<type>-<sujet>-<date>.md` et, dans le node **RÉSULTAT FINAL** :
- `qualite` : décision, note moyenne, nombre de réécritures ;
- `factcheck.a_verifier_manuellement` : **ta liste de relecture**.

### 03 · Livre complet — node `Brief du livre`

Remplir `sujet`, `public`, `ton`, `nb_chapitres`, `transformation` (ce que le lecteur saura faire à la fin)
et, si possible, `echantillon_style`. Compter plusieurs heures. Résultat : `sorties/livre-...md`.

### 04 · Test 1 Chapitre — node `Données de test`

Pour essayer un modèle ou une consigne : thèse, ton, public, plan du chapitre. Résultat visible
dans le node GATE uniquement (pas de fichier).

## Avant de publier un texte

1. Lire `a_verifier_manuellement` et contrôler chaque point.
2. Vérifier chaque marqueur `[VERIF]` dans le texte, puis **retirer les marqueurs**.
3. Relire pour les raideurs de style (5 minutes).

Le fact-checker est une aide, pas une garantie : il laisse passer les inventions vagues
(« j'ai passé des semaines… »). Pour les résumés, se méfier sur les **livres célèbres** : le modèle
peut compléter avec ce qu'il sait déjà du livre au lieu de s'en tenir au texte.

## Ajouter des faits de référence (briefs)

1. Copier `briefs/_template.md` → `briefs/brief-<sujet>.md` et le remplir (une ligne = un fait).
2. Réindexer : `cd factcheck && venv/bin/python indexer_faits.py`
3. Relancer le service fact-check.

## Lancer un workflow sans navigateur (avancé)

```bash
docker exec -e N8N_RUNNERS_BROKER_PORT=5691 n8n-atelier-ecriture n8n execute --id=ResumeLivreLoc01
```

Identifiants : `ResumeLivreLoc01` (résumé), `88ccIy5TWBBJBYSQ` (Express),
`txEGIeW6qVQOjLdq` (Livre complet), `rzsnAfjmSxltwvDT` (Test 1).
Le `-e N8N_RUNNERS_BROKER_PORT=5691` est obligatoire : sans lui, erreur « port 5679 is already in use ».
