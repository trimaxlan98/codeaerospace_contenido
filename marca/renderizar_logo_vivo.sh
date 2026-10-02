#!/usr/bin/env bash
# Renderiza los el «logo vivo» en loop sobre entornos (9:16, 1080×1920, 30 fps, 8 s) a exports/estudio/logo_vivo/.
#   bash marca/renderizar_logo_vivo.sh            todos (en paralelo, JOBS=4)
#   bash marca/renderizar_logo_vivo.sh ReelIntro  solo esos
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
SALIDA="$REPO/exports/estudio/logo_vivo"
FUENTE=studio/content/animations/experimentacion/35-logo-vivo.py
CALIDAD="${CALIDAD:--r 1080,1920 --fps 30}"
export PYTHONPATH="$REPO/studio/content/manim_extensions:$REPO/animaciones"
mkdir -p "$SALIDA"
ESCENAS=("$@")
[ ${#ESCENAS[@]} -eq 0 ] && ESCENAS=(LogoVivoOrbita LogoVivoNebulosa LogoVivoMarte LogoVivoLunar LogoVivoFisica LogoVivoEspectro)
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
