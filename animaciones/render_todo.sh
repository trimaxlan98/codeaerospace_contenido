#!/usr/bin/env bash
# Renderiza todas las piezas a 1080p30 en ../exports/<tema>/<oscuro|claro>/
# Uso: ./render_todo.sh [oscuro|claro|ambos] [archivo.py ...]
#   ./render_todo.sh                       -> todo, fondo oscuro
#   ./render_todo.sh ambos                 -> todo, oscuro y claro
#   ./render_todo.sh claro constelaciones.py
# SOLO="ClaseA ClaseB" limita a esas piezas.
# TEMA_VISUAL=orbita dibuja con la fuente y colores de ese tema (temas_espaciales.py) a <tema>/t_<id>[_en]/; pásalo con un solo tema oscuro|claro (el del tema).
# IDIOMA=en renderiza con los textos en inglés (traducciones_en.py, estricto) a <tema>_en/ (oscuro_en, claro_en); por defecto es.
# Variables: JOBS (procesos en paralelo, def. 4), CALIDAD (def. "-r 1920,1080 --fps 30")
set -uo pipefail
cd "$(dirname "$0")"
TEMAS=${1:-oscuro}; shift || true
[ "$TEMAS" = ambos ] && TEMAS="oscuro claro"
ARCHIVOS=${*:-$(ls -1 *.py | grep -v -E '^(code_lib|_)')}
JOBS=${JOBS:-4}
CALIDAD=${CALIDAD:--r 1920,1080 --fps 30}
IDIOMA=${IDIOMA:-es}
SUFIJO=""; [ "$IDIOMA" = en ] && SUFIJO="_en"
TEMA_VISUAL=${TEMA_VISUAL:-}
SALIDA=../exports
mkdir -p "$SALIDA"

tareas=()
for t in $TEMAS; do
  for f in $ARCHIVOS; do
    for c in $(grep -oE '^class\s+\w+\(Pieza\w*\)' "$f" | sed -E 's/class\s+(\w+).*/\1/' | grep -v '^Pieza'); do
      [ -n "${SOLO:-}" ] && [[ " $SOLO " != *" $c "* ]] && continue
      tareas+=("$t $f $c")
    done
  done
done
echo "${#tareas[@]} piezas, $JOBS en paralelo"

render_uno() {
  t=$1; f=$2; c=$3; tema=${f%.py}
  carp="$t"; [ -n "$TEMA_VISUAL" ] && carp="t_$TEMA_VISUAL"
  dest="$SALIDA/$tema/$carp$SUFIJO"; mkdir -p "$dest"
  [ -f "$dest/$c.mp4" ] && [ -z "${FORZAR:-}" ] && { echo "= $t/$tema/$c (ya existe)"; return; }
  tmp=$(mktemp -d)
  if CODE_TEMA_VISUAL=$TEMA_VISUAL CODE_IDIOMA=$IDIOMA CODE_TEMA=$t manim render $CALIDAD --media_dir "$tmp" -o "$c" "$f" "$c" >"$tmp/log" 2>&1; then
    mv "$(find "$tmp/videos" -name "$c.mp4" | head -1)" "$dest/$c.mp4"; echo "+ $t/$tema/$c"
  else
    mkdir -p "$SALIDA/_errores"; cp "$tmp/log" "$SALIDA/_errores/$t$SUFIJO-$c.log"; echo "! $t/$tema/$c FALLÓ"
  fi
  rm -rf "$tmp"
}
export -f render_uno; export SALIDA CALIDAD FORZAR IDIOMA SUFIJO TEMA_VISUAL
printf '%s\n' "${tareas[@]}" | xargs -P "$JOBS" -L1 bash -c 'render_uno "$@"' _
