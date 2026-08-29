#!/usr/bin/env bash
# Inventario reproducible de las entregas finales guardadas fuera de Git.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXPORTS="$REPO/exports"
DESTINO="$EXPORTS/inventario"

if [[ ! -L "$EXPORTS" ]]; then
  echo "ERROR: $EXPORTS debe ser un enlace al almacen persistente" >&2
  exit 1
fi

REAL="$(readlink -f "$EXPORTS")"
case "$REAL" in
  /home/alanrosasp/data/codeaerospace/exports) ;;
  *) echo "ERROR: destino inesperado de exports: $REAL" >&2; exit 1 ;;
esac

mkdir -p "$DESTINO"
TMP_MANIFEST="$(mktemp "$DESTINO/manifest.tsv.XXXXXX")"
TMP_SHA="$(mktemp "$DESTINO/sha256.txt.XXXXXX")"
trap 'rm -f "$TMP_MANIFEST" "$TMP_SHA"' EXIT

printf 'bytes\tarchivo\n' > "$TMP_MANIFEST"
find -L "$EXPORTS" -type f \
  \( -name curso_narrado.mp4 -o -name '*_vertical.mp4' -o \
     -path '*/promos/*/vertical.mp4' \) \
  -not -path "$DESTINO/*" -printf '%s\t%P\n' | sort -k2 >> "$TMP_MANIFEST"

while IFS=$'\t' read -r _ rel; do
  [[ "$rel" == "archivo" ]] && continue
  sha256sum "$EXPORTS/$rel" | sed "s#  $EXPORTS/\|  $REAL/#  #"
done < "$TMP_MANIFEST" > "$TMP_SHA"

mv "$TMP_MANIFEST" "$DESTINO/manifest.tsv"
mv "$TMP_SHA" "$DESTINO/sha256.txt"
trap - EXIT
echo "$(($(wc -l < "$DESTINO/manifest.tsv") - 1)) entregas inventariadas en $DESTINO"
