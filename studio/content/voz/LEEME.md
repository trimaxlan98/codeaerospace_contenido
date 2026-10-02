# Voz en off de los reels promocionales (prueba A/B: con voz vs sin voz)

Tres reels de 12 s en loop (`ReelOrbitEye`, `ReelATP`, `ReelModelo`) con voz sintética LOCAL, para medir en
Instagram si funcionan mejor con voz humana que sin ella. Cada reel tiene dos variantes con voz:

- **A «voz libre»** (`<Reel>_voz.mp4`): la voz queda entera entre 0.35 s y 11.4 s.
- **B «lazo de frase»** (`<Reel>_vozB.mp4`): la última frase queda incompleta y se completa con la primera al
  repetirse el loop (la voz cruza el empalme de las 12.000 s; hay 0.4 s de pausa justo en el corte).

Los videos son los de siempre (`-c:v copy`, sin recodificar); solo cambia el audio. Para la comparación, los reels
sin voz son `exports/marca-codeaerospace/reels-promo/con_sonido/<Reel>.mp4` (o sin audio, los `<Reel>.mp4`).

## Archivos

| Qué | Dónde |
|---|---|
| Guiones con tiempos (para grabar tu voz) | `studio/content/voz/guiones/<Reel>.md` |
| Voz sin mezclar (circular, 12 s, mono 48 kHz) | `studio/content/voz/wav/<Reel>_{A,B}_voz.wav` |
| Frases sueltas en caché (+ texto y `length_scale`) | `studio/content/voz/wav/frases/` |
| Mezcla final WAV y MP4 | `exports/marca-codeaerospace/reels-promo/con_voz/<Reel>_voz{,B}.{wav,mp4}` |
| Script | `studio/tools/voz_reels.py` (usa `sonido_reels.py` como librería) |

## Voz elegida y licencia (verificada 2026-10-02)

**Piper `es_MX-ald-medium`** (español de México, 1 locutor, 22 050 Hz, calidad media), de
<https://huggingface.co/rhasspy/piper-voices/tree/main/es/es_MX/ald/medium>.

- `MODEL_CARD` de la voz: «License: http://unlicense.org» (dominio público), datos de
  <https://huggingface.co/datasets/rmcpantoja/Ald_Mexican_Spanish_speech_dataset>. La ficha del dataset en
  Hugging Face (API) también dice `license: unlicense`.
- Está afinada a partir de la voz es_ES `davefx`, cuyo `MODEL_CARD` dice «License: CC0» (dataset
  OHF-Voice/voice-datasets). Unlicense y CC0 permiten uso comercial sin atribución.
- Alternativa que se probó y se descartó: `es_MX-claude-high` (Apache-2.0 según su ficha, pero el «dataset» que cita es
  un Space de Hugging Face, no un conjunto de datos con procedencia clara). `ald` tiene la cadena de licencias más limpia.
- El motor `piper-tts` 1.8.0 es GPL-3.0-or-later: eso rige al programa, no al audio que produce. No se redistribuye
  el programa ni el modelo (viven en `~/.local`, fuera del repo).
- Nota: es una voz sintética; en Instagram conviene activar la etiqueta de contenido generado/alterado si la
  plataforma lo pide para voz con IA.

Sin nube ni API: el texto no sale del equipo. La única descarga es la inicial (pip y el modelo).

## Instalar (una vez)

```bash
pip install --user --break-system-packages piper-tts            # se instala en ~/.local, sin sudo
mkdir -p ~/.local/share/piper && cd ~/.local/share/piper
B=https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/ald/medium
curl -L -O $B/es_MX-ald-medium.onnx && curl -L -O $B/es_MX-ald-medium.onnx.json
# (63 MB; sha256 019b3803293c93e34a206dd2e53a3889209a514e786fd7144f7b70196c579b63)
```

## Regenerar

```bash
python3 studio/tools/voz_reels.py                 # los 3 reels, A y B: mezcla, muxa y verifica
python3 studio/tools/voz_reels.py ReelATP         # solo uno
python3 studio/tools/voz_reels.py --resintetizar  # vuelve a sintetizar las voces
```

Necesita `ffmpeg`, `numpy`, `scipy` y que existan `exports/marca-codeaerospace/reels-promo/<Reel>.mp4`.
La mezcla es determinista; Piper no lo es bit a bit, así que las frases sintetizadas se guardan en
`wav/frases/` y solo se vuelven a sintetizar si cambia el texto o `--resintetizar`. Para cambiar un guion, edita el
diccionario `REELS` de `voz_reels.py` (tiempo `t` en segundos del video, texto `frase`, ortografía fonética `tts`
y `ls`, la velocidad: menor = más rápido). El script regenera los `guiones/*.md` y avisa si dos frases se pisan o la
voz se sale de 0.35–11.4 s.

Pronunciación (en `tts`): las siglas van en mayúsculas separadas («V F O», «S S T V») o fonéticas («i cú»), «Dóppler» con tilde, y
`0.1°` como «cero punto uno grados». No se pronuncia «Co.De»/«Strategy» en la voz: el TTS en español las lee mal (un reconocedor local oyó «con estrategia»); en la voz real, di «Code» como la marca lo diga.

## Cómo se mezcla

- Colchón y efectos = exactamente el audio de `sonido_reels.py` (mismo desfase). Bajan **9 dB** mientras hay voz
  (más 60 ms de margen y cierre de pausas < 0.4 s), con rampas Hann de ≈120 ms por lado, todo en tiempo circular.
- Voz: pasa-altas 80 Hz, nivel ≈ −16 dBFS RMS y compresión suave; fundidos de 8 ms por frase.
- Nivel final −16 LUFS (ffmpeg `ebur128`), pico real ≤ −2 dBTP (limitador suave); todo en un buffer circular de
  12.000 s exactos, así que el WAV empalma consigo mismo sin recorte ni clic.

## Verificaciones (el script las imprime)

Duración exacta de WAV y de video (12.000 s), costura (|primera − última muestra| frente al paso p99, como
`verificar_loop.py`), LUFS y pico real, y el margen voz/colchón en ventanas de 100 ms. Con `faster-whisper` (modelo `small`, local; no se instala por el script) se transcribió de vuelta cada mezcla repetida
dos veces: las frases se entienden también al cruzar el empalme (B). Los reconocedores fallan con siglas aisladas
(oyó «BFO», «CSTV», «Nico»/«y cu» por «IQ»): es límite del reconocedor y a la vez aviso de que esas siglas son lo más
frágil de la voz sintética. Lo que NO se puede verificar sin oír: naturalidad de la voz, pronunciación de las siglas (VFO, SSTV, IQ), y si el ducking se nota «bombeando».

## Regrabar con voz real

1. Abre `guiones/<Reel>.md`: cada fila es *tiempo → frase → qué se ve*. Los tiempos son del video; el video no cambia.
2. Pon el video en tu editor, graba cada frase a su tiempo inicial (o una sola toma siguiendo el video) con un
   micrófono cercano y sin reverberación. Mantén las frases dentro de 0.35–11.4 s (variante A).
3. Variante B: empieza la última frase en el tiempo indicado y deja que cruce el final; la primera frase del guion B
   (al inicio) completa esa oración. Verifica que el audio termine y empiece sin silencio de más en el empalme.
4. Mezcla bajando el colchón 6–9 dB mientras hablas: usa `<Reel>.wav` de `con_sonido/` como colchón o, mejor, solo
   el video sin audio, y deja la voz a −16 LUFS (pico ≤ −2 dBTP).
5. Muxa sin recodificar el video: `ffmpeg -i <Reel>.mp4 -i mezcla.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest salida.mp4`.

## Honestidad del contenido

Solo hechos de `redes/fuentes/` (plataformas y servicios, 2026-10-01) y advertencias de
`redes/carruseles/ESQUEMA.md`: Orbit Eye se dice «demo con grabación IQ» (sin receptor conectado, nada de «en vivo»);
ATP-DT es «en beta», 0.1° es un «presupuesto de diseño» y las curvas son «trazas ilustrativas»; el modelo repite la
cita de codeaerospace.com/services («cada proyecto digital… financia investigación aeroespacial real») y
«plataformas en línea, no maquetas». Sin cifras ni clientes. Si cambia un texto del reel, cambia el guion.
