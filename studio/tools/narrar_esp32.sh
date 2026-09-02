#!/bin/bash
# Narracion SERIAL de las piezas del curso 31 en el VPS.
#
# Serial y con pausa a proposito: la cuota de Vertex es por MINUTO y por
# modelo, y en paralelo el TTS devuelve 429. En el curso 28 un 429 se
# llevo una pieza entera; de ahi el `sleep 45` entre piezas.
#
# `ssh` dentro de un `while read` se come el stdin: por eso `ssh -n`.
set -u
VPS=triage-vps
REMOTO=/var/www/codeaerospace_contenido
BASE=/tmp/narrar-esp32
LOCAL=/home/alanrosasp/Documentos/github/codeaerospace_contenido
DESTINO=$LOCAL/exports/verticales/esp32/voz

mkdir -p "$DESTINO"

# Solo se narran las piezas que tienen frases; intro y cierre son mudas.
PIEZAS=$(cd "$LOCAL/studio/content/verticales/esp32/clips" && \
  for d in */; do
    n=${d%/}
    if python3 -c "
import json,sys
c=json.load(open('$LOCAL/studio/content/verticales/esp32/clips/$n/clip.json'))
sys.exit(0 if c.get('voz',{}).get('secciones') else 1)"; then echo "$n"; fi
  done)

echo "piezas a narrar:"; echo "$PIEZAS" | sed 's/^/  /'

for n in $PIEZAS; do
  if [ -s "$DESTINO/$n.wav" ]; then
    echo "== $n : ya existe, se salta"
    continue
  fi
  echo "== $n"
  ssh -n $VPS "mkdir -p $BASE/$n"
  scp -q "$LOCAL/studio/content/verticales/esp32/clips/$n/clip.json" \
      "$VPS:$BASE/$n/clip.json"
  ssh -n $VPS "cd $REMOTO && studio/backend/venv/bin/python \
      studio/tools/alinear_voz.py $BASE/$n $BASE/$n.wav" 2>&1 | sed 's/^/   /'
  scp -q "$VPS:$BASE/$n.wav" "$DESTINO/$n.wav" || echo "   SIN WAV"
  ls -la "$DESTINO/$n.wav" 2>/dev/null | awk '{print "   bajado:", $5, "bytes"}'
  sleep 45
done
echo "=== NARRACION TERMINADA ==="
ls -la "$DESTINO"
