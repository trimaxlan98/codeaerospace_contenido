---
title: Voz — guion, proveedores y grabación propia
level: intro
summary: Cómo narrar un curso sin depender de Gemini: escribir el guion por secciones, elegir proveedor y voz (edge-tts, Piper, Vertex) o subir tu propia grabación, y qué hace la app con cada cosa.
tags: [voz, narracion, tts, guion, workflow]
minutes: 8
order: 4
---

## Las tres piezas de una narración

Una narración en ManimStudio son tres archivos por clip en
`guiones/<curso>/NN-<clip>.*`:

| Archivo | Qué es | Quién lo escribe |
|---|---|---|
| `.secciones.json` | el **guion cronometrado**: `[{t_inicio, t_fin, momento, texto}]` | Gemini (si hay Vertex), tú, o Claude |
| `.wav` | la **voz**, mono a 24 kHz, alineada a esos tiempos | el proveedor elegido, o tu grabación |
| `estado.json` | de dónde salió la voz y si sigue **al día** con el vídeo | la app |

Desde 2026-09 las tres piezas se manejan desde **Proyectos → clip → «Guion y
voz»**, y ninguna necesita GCP.

## 1. El guion por secciones

Cada sección es una frase o dos que se dicen **sobre un momento visual**. El
`t_inicio` es el instante del vídeo en el que empieza esa frase. Reglas que
la app comprueba al guardar:

- los `t_inicio` no retroceden,
- ninguna sección está vacía,
- caben unas 2,2 palabras por segundo de vídeo (la cabecera del diálogo te
  dice cuántas caben y cuántas llevas).

Consejos que vienen de 33 cursos:

- **No leas lo que ya está en pantalla**: complétalo. Si el clip rotula
  «−3 dB», la voz dice *por qué* son tres decibelios.
- Frases cortas, sin notación: «zeta al cuadrado más c», no «z^2+c».
- Deja **aire** entre secciones: el hueco es el momento en que se entiende lo
  que acaba de pasar. Un guion escrito a mano se alinea **exacto** a sus
  tiempos (los huecos de 4–7 s de un vertical se respetan).
- Si el audio no cabe en el vídeo, la app comprime los silencios; nunca corta
  la voz. Si aun así se pasa, el montaje de la película lo acelera hasta un
  15 % con `atempo`. Más que eso: acorta el guion.

Si Vertex está disponible, «Generar narración» le pide el guion a Gemini a
partir del script del clip. Si no (o si prefieres el tuyo), escribe el guion
y usa **«Narrar este guion»**: la voz habla lo que escribiste, sin reescribirlo.

## 2. Proveedores de voz

| Proveedor | Cuándo | Voz por defecto |
|---|---|---|
| **Edge** | el defecto: gratis, 45 voces en español, necesita red | Jorge (es-MX) |
| **Piper** | sin red o cuando Edge no responda; corre en el servidor | es_MX-claude-high |
| **Gemini** (Vertex) | cuando la facturación de GCP esté al día; es el único que escribe guiones | Charon |
| **Grabación propia** | cuando quieres tu voz (ver §3) | — |

El selector de la cabecera del proyecto elige proveedor y voz para «Generar
narración»; el del diálogo «Guion y voz», para ese clip. Cambiar la voz por
defecto **no** deja desactualizado lo ya narrado: cada clip recuerda con qué
voz se narró, y solo se rehace si cambia el script, la escena o la duración
del vídeo (o si lo pides con el botón de regenerar).

## 3. Tu propia grabación

Graba el clip con lo que tengas (móvil, Audacity, OBS) y súbelo desde «Guion
y voz → Subir grabación». Formatos: wav, mp3, flac, ogg, m4a, aac, webm,
opus; hasta 25 MB. La app:

1. lo convierte a **mono 24 kHz** (lo que esperan la cama de sonido y la
   película),
2. le **recorta el silencio** del principio y del final (conserva 0,12 s),
3. lo deja en la misma ruta que usaría el TTS, así **la película lo recoge
   sin ningún paso extra**.

Tres consejos de grabación:

- Graba con el vídeo delante y arranca a la vez: los tiempos importan más
  que la calidad del micrófono.
- Deja 1 s de silencio al inicio y al final; la app lo quita.
- Si el clip dura 40 s, que la voz no pase de 38: la cola de silencio es lo
  que hace limpio el corte con el clip siguiente.

## 4. Desde la terminal

Las mismas herramientas de siempre aceptan `--proveedor`:

```bash
# horizontal (usa el .secciones.json del clip)
studio/tools/guiones.py "Familia · 1.1 Titulo" --proveedor edge
# vertical (clip.json > voz.secciones, frase a frase en sus tiempos)
studio/tools/alinear_voz.py studio/content/verticales/<slug>/clips/01-<pieza> voz.wav --proveedor edge
```

Y la API, por si narras desde un script:

- `GET /api/narracion/proveedores` — qué hay disponible y por qué no.
- `PUT /api/projects/{pid}/narracion/{cid}/guion` — guardar el guion.
- `POST /api/projects/{pid}/narracion` — `{proveedor, voz, solo_audio, clips, force}`.
- `PUT /api/projects/{pid}/narracion/{cid}/audio?nombre=toma.m4a` — subir grabación (cuerpo crudo).

## Checklist antes de montar la película

- [ ] Todos los clips **al día** en la columna de narración.
- [ ] Ningún aviso «más larga que el vídeo».
- [ ] La voz **calla** antes del último fotograma (cola ≥ 0,8 s).
- [ ] La misma voz en todo el curso (o un cambio deliberado por módulo).
