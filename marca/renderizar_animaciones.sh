#!/usr/bin/env bash
# Renderiza las animaciones del logo de Co.De Aerospace (demo 30 y rótulos 31) a exports/marca-codeaerospace/.
#   bash marca/renderizar_animaciones.sh            1080p60 horizontal + vertical 9:16
#   CALIDAD="-r 3840,2160 --fps 60" bash marca/renderizar_animaciones.sh   (4K)
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
SALIDA="$REPO/exports/marca-codeaerospace"
TMP="$(mktemp -d)"
CALIDAD="${CALIDAD:--r 1920,1080 --fps 60}"
DEMO=studio/content/animations/experimentacion/30-logo-co-de-aerospace.py
ROT=studio/content/animations/experimentacion/31-rotulos-aerospace.py
export PYTHONPATH="$REPO/studio/content/manim_extensions"
mkdir -p "$SALIDA"
render() {  # archivo escena nombre_salida [calidad]
  manim render $4 --disable_caching --media_dir "$TMP" "$1" "$2" >/dev/null
  cp "$(find "$TMP/videos" -name "$2.mp4" -newer "$TMP" | head -1)" "$SALIDA/$3.mp4"
  echo "  $3.mp4"
}
touch "$TMP"
for e in LogoCoDeIntro LogoCoDeIntroClaro LogoCoDeTrazo LogoCoDeEnsamble LogoCoDeSting LogoCoDeCierre LogoCoDeMarcaDeAgua; do
  render "$DEMO" "$e" "$e" "$CALIDAD"
done
render "$DEMO" LogoCoDeVertical LogoCoDeVertical "-r 1080,1920 --fps 60"
render "$ROT" DemoRotulosAerospace RotulosAerospace "$CALIDAD"
echo "listo → $SALIDA"
