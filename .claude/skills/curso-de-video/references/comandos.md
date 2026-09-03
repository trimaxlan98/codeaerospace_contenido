# Comandos del pipeline

Rutas relativas al checkout (o al worktree). Intérprete: siempre
`studio/backend/venv/bin/python` — el venv del checkout **principal** sirve
para los worktrees.

## 0. Entorno

| Cosa | Dónde |
|---|---|
| Imagen Docker de render | `codeaerospace_contenido-manim` (local) |
| VPS | `ssh root@187.124.55.225` (alias `triage-vps`), app en `/var/www/codeaerospace_contenido` |
| Env del backend en el VPS | `/etc/manimstudio/env` (fuera del repo; hay que cargarlo a mano) |
| ffmpeg | **solo local**; el VPS no lo tiene |
| Worktree para no estorbar al checkout principal | `git worktree add ../codeaerospace_contenido-<tema> -b curso/<tema> origin/main` |

## 1. Validar la librería ANTES de escribir clips

Sonda propia en el scratchpad que imprima las cifras y guarde PNGs con PIL,
ejecutada **en el contenedor** (el numpy del host ya rompió arrays una vez):

```bash
docker run --rm --user $(id -u):$(id -g) -v "$PWD":/workspace \
  -w /workspace codeaerospace_contenido-manim \
  python3 <scratchpad>/valida_<tema>.py
```

Si la sonda mide anchos de texto, tiene que **replicar la subclase `Text` con
sombra del style_block**, o los bbox salen inflados y da falsos positivos.

## 2. Render de validación (`ql`) y revisión de frames

```bash
studio/backend/venv/bin/python studio/tools/render_local.py \
  studio/content/cursos/<slug> --clip 3 --frames 8
studio/backend/venv/bin/python studio/tools/render_local.py \
  studio/content/cursos/<slug> --todos --frames 8
```

Salida en `render_jobs/validacion/<slug>/NN-<escena>/{scene.py,video.mp4,frames/}`.
Avisa si el clip se sale de 28–45 s. Aborta si falta cualquier clip declarado
en `curso.json` (por eso los stubs). Para el `final_state` hay que mirar el
**último frame real**, no el muestreo:

```bash
ffmpeg -y -sseof -0.4 -i video.mp4 -update 1 -frames:v 1 final.png
```

## 3. Subir el curso a la base

Local (`--dry-run` valida el manifiesto sin escribir):

```bash
studio/backend/venv/bin/python studio/tools/subir_curso.py \
  studio/content/cursos/<slug> --dry-run
```

En el VPS, como `manimstudio` y con el env cargado:

```bash
ssh triage-vps 'cd /var/www/codeaerospace_contenido && git pull'
ssh triage-vps "cd /var/www/codeaerospace_contenido && sudo -u manimstudio bash -c '
  set -a; . /etc/manimstudio/env; set +a
  studio/backend/venv/bin/python studio/tools/subir_curso.py \
    studio/content/cursos/<slug>'"
```

Idempotente; empareja el proyecto **por nombre exacto** y los clips por
posición. Nunca borra.

## 4. `qh` local y adopción en producción

`--calidad qh` escribe en el MISMO `render_jobs/validacion/<slug>/` y **pisa
los `ql`**: copiar a `render_jobs/qh/<slug>/` en cuanto termine.

```bash
# 3 procesos en paralelo, no más (8 cores, ~1 min/clip)
for s in <slug1> <slug2> <slug3>; do
  studio/backend/venv/bin/python studio/tools/render_local.py \
    studio/content/cursos/$s --todos --calidad qh &
done; wait
```

Subida y adopción (el uplink va a ~100 KB/s: correr el `scp` en background y
con margen, no con timeout de 10 min):

```bash
scp render_jobs/qh/<slug>/*/video.mp4 triage-vps:/root/staging-<slug>/Clip1.mp4  # …ClipN
ssh triage-vps 'python3 /root/adoptar_renders.py "<fragmento del nombre>" /root/staging-<slug>'
ssh triage-vps 'rm -rf /root/staging-<slug>'
```

`adoptar_renders.py` inserta jobs `done` con el `content_hash` correcto: por
eso el render local cuenta como vigente en prod. Verificación final por
consulta a la DB (sqlite3 CLI no está instalado: `python3 -c` tras cargar el
env).

## 4bis. Verificación previa (cursos VERTICALES)

Se corre **después de los `qh` y antes de mandar nada al VPS**. Cada cosa que
mira costó una vuelta entera en algún curso:

```bash
studio/backend/venv/bin/python studio/tools/verifica_vertical.py \
    studio/content/verticales/<slug>
```

- resolución y fps de cada pieza;
- que **`duracion_objetivo` coincida con el render real**. La voz se alinea
  contra el manifiesto, así que un manifiesto desfasado pone la voz sobre el
  plano equivocado — y el redondeo a frame de 60 fps no es el de 30, hay que
  re-comprobarlo después del `qh`, no sólo en `ql`;
- que las piezas de curso caigan en el rango de duración;
- que ninguna frase de voz pise a la anterior y que quede cola de silencio;
- que el `fade_out` quepa y que los eventos de SFX existan en la paleta;
- **las costuras**: último frame de cada pieza contra el primero de la
  siguiente. Si la cifra se repite EXACTA en todas las uniones, el culpable
  es siempre el mismo objeto de la capa fija — es la pista más útil.

Necesita PIL y numpy: el venv del backend no los trae, así que para las
costuras se corre con el `python3` del sistema o se mide aparte.

## 5. Narración (TTS)

**Desde 2026-09-03 la voz no necesita GCP** (`studio/docs/ESTUDIO-V3.md`,
R1). Proveedores: `edge` (edge-tts, gratis, red; defecto), `piper`
(offline, modelo en `MS_PIPER_VOICES_DIR`), `vertex` (Gemini, de pago) y la
grabación propia del dueño. Todas las herramientas aceptan `--proveedor`:

```bash
# horizontal, LOCAL (edge no necesita el VPS ni la key): usa el
# .secciones.json del clip; el guion lo escribes tú o Claude
studio/backend/venv/bin/python studio/tools/guiones.py "Familia · 1.1 Titulo" --proveedor edge
# vertical: frase a frase en sus t_inicio exactos (clip.json > voz.secciones)
studio/backend/venv/bin/python studio/tools/alinear_voz.py \
  studio/content/verticales/<slug>/clips/01-<pieza> salida.wav --proveedor edge
```

Desde la app: «Guion y voz» en cada clip (escribir el guion por secciones,
narrarlo con la voz elegida o **subir tu grabación** wav/mp3/m4a). API:
`PUT /api/projects/{pid}/narracion/{cid}/guion`, `POST …/narracion
{proveedor, voz, solo_audio}`, `PUT …/narracion/{cid}/audio?nombre=`.

Solo Vertex escribe el guion a partir del script; con `MS_TTS_GUIONISTA=ninguno`
(GCP en mora) la app pide el guion escrito. Con Vertex, en el VPS,
**SERIAL** — dos `guiones.py` a la vez dan 429 del TTS:

```bash
ssh triage-vps "cd /var/www/codeaerospace_contenido && sudo -u manimstudio bash -c '
  set -a; . /etc/manimstudio/env; set +a
  setsid nohup sh -c \"for n in \\\"Familia · 1.1 Titulo\\\" \\\"Familia · 1.2 Titulo\\\"; do
      studio/backend/venv/bin/python studio/tools/guiones.py \\\"\$n\\\"; done\" \
    < /dev/null > /tmp/narrar.log 2>&1 &'"
```

Idempotente (salta los wav ya hechos), así que una re-pasada arregla un wav
caído sin rehacer el lote. El guion se ajusta a la duración real del mp4, así
que **se narra después de adoptar los `qh`**.

Salida: `guiones/<slugify(NOMBRE)[:40]>/NN-<slug>.wav` — **no** es el slug del
curso; para bajarlos usa el glob `guiones/<familia>-N-M-*/`.

### Si el TTS falla

- **429** → es cuota: la de Vertex es **por minuto y por modelo**, y se agota
  narrando en serie si las frases son cortas. Reintenta con `sleep 45` entre
  piezas.
- **403 `PERMISSION_DENIED` con "Lightning dunning decision is deny"** → NO es
  cuota ni credenciales: *dunning* es cobro de morosidad, o sea que el
  proyecto de GCP tiene la facturación en mora y la API deniega todo. No hay
  reintento que valga; lo arregla el dueño en la consola de facturación. Se
  distingue en un minuto probando **una sola frase** contra el TTS en el VPS
  en vez de dejar el bucle entero fallando pieza a pieza. Pasó en el curso 31.

En los dos casos el curso se puede entregar **sin voz** (`unir_vertical.py
--sin-voz`) y añadirla después: narrar y re-muxear no obliga a re-renderizar
nada.

## 6. Mux local con la marca

Layout por lección en `exports/<slug>/`:

```
000-intro.mp4                 copiado tal cual de exports/marca-intro-y-cierre/intro.mp4
001-<clip>.mp4 + 001-<clip>.wav
002… 003… 004…
005-cierre.mp4                copiado tal cual de …/cierre.mp4
concat.txt                    una linea "file '000-intro.mp4'" por pieza, en orden
```

```bash
cd exports/<slug> && sh ../mux.sh      # deja curso_narrado.mp4
```

`mux.sh` acelera la voz con `atempo` (tope 1.15×), conserva el audio propio de
los clips sin narración (los SFX de la marca) y silencia los mudos, para que
el `concat -c copy` no se rompa. **Los SFX de la marca deben ser AAC 24 kHz
mono** (igual que el TTS) o el concat se rompe.

Medir picos SIEMPRE (vienen calientes de fábrica: en cursos recientes, entre
4 y 11 clips por lote):

```bash
ffmpeg -hide_banner -i con_audio/001-<clip>.mp4 -af volumedetect -f null - 2>&1 | grep max_volume
```

Pico > −0.5 dB → re-muxear ese clip con `volume=-1.5dB` (**−2.5 dB si toca
0.0**, que es recorte real) reaplicando el mismo `atempo`, y re-concatenar.
La marca sonora tiene que medir **−6.0 dB** dentro de la salida final.

## 7. Marca intro/cierre

`exports/marca-intro-y-cierre/{intro,cierre}.mp4` ya traen su pista de SFX
(respaldo `*_mudo.mp4`). Regenerarlas solo si se cambia el diseño sonoro:

```bash
docker run --rm --user $(id -u):$(id -g) -v "$PWD":/workspace \
  -w /workspace codeaerospace_contenido-manim python3 studio/tools/sfx.py marca
```

Es idempotente (parte de los `_mudo`). Criterio del dueño: espacial pero
tranquilo, nada estridente ni agudo; lo llamativo solo en el sting del cierre.

## 8. Tests y publicación

```bash
cd studio/backend && venv/bin/pytest -q          # tocaste backend o extensiones
git add <rutas explicitas> && git commit -m "feat(contenido): <familia> lote N"
gh pr create --base main && gh pr merge
```

Asuntos de commit **sin acentos**; nunca `git add -A`; los mp4 de `exports/`
no se versionan. Si `gh pr merge` falla, merge con git puro desde el worktree
(y si el clasificador bloquea el merge, pedírselo al usuario con `!`).
