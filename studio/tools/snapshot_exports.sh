#!/usr/bin/env bash
# Protege el estado actual de exports contra eliminaciones accidentales.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXPORTS="$REPO/exports"
REAL="$(readlink -f "$EXPORTS")"
RAIZ="/home/alanrosasp/data/codeaerospace/snapshots"
NOMBRE="${1:-$(date +%Y-%m-%d_%H%M%S)}"
DESTINO="$RAIZ/$NOMBRE/exports"

if [[ ! -L "$EXPORTS" || "$REAL" != /home/alanrosasp/data/codeaerospace/exports ]]; then
  echo "ERROR: exports no apunta al almacen persistente esperado" >&2
  exit 1
fi
if [[ -e "$DESTINO" ]]; then
  echo "ERROR: la instantanea ya existe: $DESTINO" >&2
  exit 1
fi

mkdir -p "$(dirname "$DESTINO")"
cp -al "$REAL" "$DESTINO"
echo "instantanea protegida: $DESTINO"
