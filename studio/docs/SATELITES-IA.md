# Satélites e IA: librería y curso (2026-08-05)

## Librería `studio/content/manim_extensions/satelites.py`

Constelaciones NTN y visuales de IA para Manim CE con la misma disciplina que
`fractales.py` (VPS con render capado a ~1.5 vCPU / 2 GB): numpy vectorizado,
resultados como `ImageMobject` o pocos VMobjects con datos precalculados, sin
matplotlib ni datos externos, determinista. Topes: `SATS_MAX=240`,
`FRAMES_MAX=260`, `RES_MAX_MAPA=1920`.

API principal (docstrings en el módulo):

- `ConstelacionWalker(planos, sats_por_plano, ...)` — Walker-delta real
  (RAAN repartido + fase inter-plano) propagada en lote y proyectada en
  ortográfica con inclinación de cámara; los satélites son `Dot`s que
  `AnimarWalker` mueve leyendo `trayectoria` (frames,N,3) precalculada, con
  oclusión tras el disco terrestre (opacidad baja). `enlaces_walker()` añade
  ISL con updaters que siguen a los Dots y se ocultan con ellos
  (`clear_updaters()` al terminar).
- `mapa_tierra()` / `imagen_mapa()` — mapa equirrectangular estilizado:
  continentes como polígonos lon/lat PROPIOS (en el módulo) rasterizados por
  ray-casting numpy. Es escenografía reconocible, no cartografía.
- `subsatelites_walker()` — (frames,N,2) de (lon,lat) con rotación terrestre
  opcional (`duracion_s`). `angulo_cobertura(h, elev_min)` — radio angular
  del casquete. `conteo_cobertura()` + `colorear_cobertura()` — capa de
  cobertura por conteo de satélites visibles (1=cian, 2+=dorado).
- `animar_cobertura(escena, trazas, ...)` — patrón morph_julia: lote de
  frames RGBA intercambiados mutando `pixel_array` (coste de vídeo
  constante). Acepta `imagen=` para reutilizar un mapa YA en escena
  (misma res) y evitar el "pop".
- `traza_terrestre()` — ground track partido en el antimeridiano;
  `puntos_en_mapa()` mapea lon/lat a coordenadas del mobject del mapa.
- `ventana_visibilidad(lat, lon, lonlat_sat, h)` — elevación vs tiempo
  desde una estación (verificada: cenital=90°, horizonte=0°).
- IA: `curva_aprendizaje(semilla, ...)` — recompensa RL sintética
  determinista (sigmoide + ruido suavizado con pad de borde + caídas de
  exploración); `heatmap_q(matriz)` — raster pixelado (NEAREST) para
  tablas Q/políticas.

Demo en Animaciones: `experimentacion/12-satelites-y-cobertura.py`.

### Truco del pase sobre una estación

Para que un ground track pase sobre una estación concreta no basta variar la
fase (solo desplaza la traza ~24° por rotación terrestre): hay que desplazar
la longitud del nodo ascendente. En la práctica: tomar el punto de la traza
con latitud más cercana a la estación y sumar `dlon = lon_est - lon_traza` a
toda la traza (equivale a elegir RAAN). El clip 4 lo hace inline (elevación
máxima 89°, pase útil de ~8 min).

## Curso "Satélites e IA: la red que aprende a gobernarse"

Proyecto en Proyectos (calidad `qm`), 8 clips, basado en la investigación
doctoral de Alan (gobernanza autónoma de redes programables 6G/NTN, IPN;
repo `trimaxlan98/tesis-doctorado-6g`). Regla editorial: el estado del arte
se afirma con su fuente; los aportes de la tesis aún sin validar a escala se
marcan con el chip `etiqueta_desarrollo()` ("EN DESARROLLO · tesis doctoral
IPN") — aplica a PADA, Margen Adaptativo, NTNEnv-v2 y los resultados demo de
QMIX (+5–13%, 3/3 semillas).

Recorrido: constelación-gancho → órbitas y latencias (GEO/MEO/LEO) → NTN
3GPP Rel-17→19 e IMT-2030 → topología dinámica (ground track, ventana de
~8 min, cobertura respirando) → RL monoagente (curva + política) → MARL
(Dec-POMDP, CTDE, QMIX monótono) → tolerancia bizantina (n≥3f+1, 5G-PBFT,
FL robusto) → PADA + falsabilidad (MA≥25%, medido 0.318) y cierre
"demostrado hoy vs en desarrollo".

El style_block del proyecto define paleta espacial (fondo `#05070f`, dorado
`#ffd27d`, cian `#4dd8e6`, violeta IA `#c77dff`), helpers `titulo_curso` /
`pie_curso` / `etiqueta_desarrollo` / `caja` / `estrellas`, e incluye el
parche del bug de `Text` con espacios de Manim 0.20.1 (ver FRACTALES.md).

## Presupuesto de render

Aplica la regla medida en FRACTALES.md: segundos de vídeo con imagen a
pantalla completa × 12 ≈ segundos de render (Cairo ~2.5 fps). El lote de
cobertura del clip 4 (110 frames a 640×320) pesa ~90 MB y tarda ~4 s de
numpy: el cuello sigue siendo Cairo, no el cómputo. Los clips de
constelación (VMobjects) rinden mucho más rápido.
