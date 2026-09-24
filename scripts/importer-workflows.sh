#!/usr/bin/env bash
# Importe les workflows du dépôt dans n8n (installation neuve ou restauration).
# ⚠️ Un workflow qui existe déjà avec le même id est REMPLACÉ par la version du dépôt.
set -euo pipefail
cd "$(dirname "$0")/.."
CONTENEUR="${CONTENEUR:-n8n-atelier-ecriture}"

docker exec "$CONTENEUR" rm -rf /tmp/wf-import
docker cp workflows "$CONTENEUR:/tmp/wf-import"
docker exec "$CONTENEUR" n8n import:workflow --separate --input=/tmp/wf-import
docker exec "$CONTENEUR" n8n list:workflow
