#!/usr/bin/env bash
# Exporte les workflows de n8n vers workflows/ (à lancer après chaque modification dans n8n,
# puis : git add workflows && git commit -m "..." && git push).
# Les exports sont nettoyés : ni e-mail du compte, ni données internes, ni prose personnelle.
set -euo pipefail
cd "$(dirname "$0")/.."
CONTENEUR="${CONTENEUR:-n8n-atelier-ecriture}"

docker exec "$CONTENEUR" sh -c 'rm -rf /tmp/wf-export && n8n export:workflow --all --separate --pretty --output=/tmp/wf-export' >/dev/null
rm -rf /tmp/wf-export-atelier && docker cp "$CONTENEUR:/tmp/wf-export" /tmp/wf-export-atelier
python3 scripts/nettoyer_export.py /tmp/wf-export-atelier workflows
rm -rf /tmp/wf-export-atelier
echo "Export terminé → workflows/"
git status --short workflows || true
