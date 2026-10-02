#!/usr/bin/env bash
# Renderiza los reels verticales 9:16 de la marca (1080×1920, 30 fps) a exports/marca-codeaerospace/vertical/.
#   bash marca/renderizar_reels.sh            todos (en paralelo, JOBS=4)
#   bash marca/renderizar_reels.sh ReelIntro  solo esos
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
SALIDA="$REPO/exports/marca-codeaerospace/vertical"
FUENTE=studio/content/animations/experimentacion/32-marca-vertical.py
CALIDAD="${CALIDAD:--r 1080,1920 --fps 30}"
export PYTHONPATH="$REPO/studio/content/manim_extensions"
mkdir -p "$SALIDA"
ESCENAS=("$@")
[ ${#ESCENAS[@]} -eq 0 ] && ESCENAS=(ReelIntro ReelIntroClaro ReelTrazo ReelEnsamble ReelSting ReelCierre ReelMarcaDeAgua ReelRotulos)
una() {  # un media_dir propio por escena: en paralelo comparten caché de texto y se corrompen
  local tmp; tmp="$(mktemp -d)"
  manim render $CALIDAD --disable_caching --media_dir "$tmp" "$FUENTE" "$1" >/dev/null 2>&1
  cp "$(find "$tmp/videos" -name "$1.mp4" | head -1)" "$SALIDA/$1.mp4"
  rm -rf "${tmp:?}"
  echo "  $1.mp4"
}
export -f una; export CALIDAD FUENTE SALIDA
printf '%s\n' "${ESCENAS[@]}" | xargs -P "${JOBS:-4}" -I{} bash -c 'una {}'
echo "listo → $SALIDA"
