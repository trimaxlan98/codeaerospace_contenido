# Ronda 1 — Auditoría del motor de contenido de Co.De Aerospace

Fecha: 2026-10-02 · Alcance: solo lectura (no se tocó ningún archivo del repo salvo este informe).
Qué se leyó: todo lo listado en el encargo, más lo que resultó ser vecino y relevante
(`studio/content/manim_extensions/{promo,lienzo,code_brand}.py`, `studio/tools/{sfx,musica,promo_verifica,render_promo}.py`,
`animaciones/fondos_a_medida.py`, `fondos_tematicos*.py`). `decks_espaciales.py` solo en estructura.
Qué se ejecutó: únicamente una medición de audio en memoria (sin escribir en `exports/`); **no se renderizó ningún video**.
Lo no verificado se marca como «estimado».

Aviso de proceso: mientras se auditaba, otro proceso editó `redes/carruseles/motor_carrusel.py` y creó
`animaciones/fondos_a_medida.py` (00:20). Los números de línea de `motor_carrusel.py` son del archivo ya editado.

---

## 1. Mapa de la arquitectura actual

### 1.1 Capas y piezas

```
marca/ (kit)                      paleta.json, SVG/PNG del logo, vectorizar_logo.py
   │  (paleta.json solo la lee la app de escritorio: studio/desktop/src/presentaciones.cjs:125)
   ▼
studio/content/manim_extensions/            ← módulos PLANOS en sys.path (≈50 archivos)
   marca_aerospace.py (+ .json)  logo por partes + animar_entrada/salida/sting + constantes de color
   estelas.py                    cometa y estela (sin Manim "TracedPath")
   rotulos_aerospace.py          tarjeta/tercio/capítulo/cortinilla/cierre HORIZONTAL (usa config.frame_*)
   marca_vertical.py             lo mismo en 9:16 (usa escena.camera.*) + fondo_reel (estrellas, 3 órbitas, satélite)
   reels_promo.py                Reloj, ventana(), leyenda(), cabecera(), chip() para loops periódicos
   code_brand.py                 registrar_fuentes() (Pango), marca CO.DE Academy (otra identidad: ámbar)
   promo.py / lienzo.py          ← SISTEMA PARALELO ya existente: Formato 9:16/16:9, zonas seguras, cabe()/encajar()
   │
studio/content/animations/experimentacion/
   30 logo (8 escenas) · 31 rótulos (1) · 32 vertical (8) · 33 reels en loop (3: OrbitEye, ATP, Modelo)
   │  render
marca/renderizar_{animaciones,reels,reels_promo}.sh   → exports/marca-codeaerospace/{,vertical,reels-promo}/*.mp4
   │  audio (paso MANUAL aparte)
studio/tools/sonido_marca.py   guiones de audio por escena, tiempos escritos a mano  → con_sonido/*.mp4
studio/tools/sonido_reels.py   importa sonido_marca; línea de tiempo circular (loop)  → reels-promo/con_sonido/
studio/tools/verificar_loop.py verificación de empalme (ffmpeg a 90×160 o PNG)  (paso MANUAL)
   │  (paralelo existente: sfx.py+musica.py, promo_verifica.py, render_promo.py, render_vertical.py)

redes/carruseles/motor_carrusel.py  JSON → PNG 1080×1350 con PIL; fondo panorámico vía fondo_a_medida
animaciones/fondos_espaciales.py (+ fondos_tematicos[_2], temas/*.py) fondos procedurales numpy; tamano() cambia el lienzo global
animaciones/temas_espaciales.py     registro de temas (Tema, derivar, plugins .json/.py)
animaciones/decks_espaciales.py     constructor .pptx (934 líneas, ver 1.3)
.claude/skills/animaciones-code/SKILL.md   manual de trabajo (solo cubre animaciones/, no la capa «marca»)
```

### 1.2 Cómo se conectan (flujo real hoy)

1. Escena Manim (30–33) → `bash marca/renderizar_*.sh` → mp4 mudo.
2. `python3 studio/tools/sonido_marca.py` / `sonido_reels.py` → lee la **duración** del mp4 (ffprobe), sintetiza un wav con eventos en segundos escritos a mano y lo pega con ffmpeg.
3. `verificar_loop.py` a mano (nadie lo invoca; ningún script falla si el loop está roto).
4. Carruseles: otra rama, sin Manim: JSON → PIL. Comparte con el resto solo el logo PNG y los colores copiados.

Los tres pasos 1→2→3 no están encadenados, no hay manifiesto de «qué pieza lleva qué audio, qué fps, qué periodo» y el vínculo escena↔audio es **el nombre de la clase** (diccionarios `ESCENAS`/`ESCENAS_V`/`REELS` en los scripts de audio).

### 1.3 `decks_espaciales.py` / temas (solo estructura)

- `decks_espaciales.py` (934 líneas) es un monolito con cinco responsabilidades: registro de decks y stickers (l. 56–180), utilidades de video con ffmpeg/LUT 3D (183–285), primitivas OOXML/python-pptx (287–480), medición de texto con fontconfig+PIL (397–478) y `class Diseno` (480–836, ≈360 líneas) más CLI (837–934). Los catálogos se cargan al importar (l. 60–62).
- `temas_espaciales.py` (232): `Tema` + `registrar/derivar/desde_json/cargar_plugins`. Los plugins `.py` se ejecutan con `exec_module` desde `animaciones/temas/` **y** desde `CODE_TEMAS_DIR` (código arbitrario por diseño: aceptable para un repo propio, no para un directorio compartido). Un tema roto se traga con `except Exception` y solo imprime a stderr (l. ~151), así que la app no se entera.
- `fondos_espaciales.py`: generadores `f(tipo, var, zona) → ndarray HxWx3`; `tamano()` (l. 40–59, nuevo) muta globales.

### 1.4 Dónde se duplica lógica (inventario)

| # | Duplicación | Dónde | Consecuencia |
|---|---|---|---|
| D1 | **Sincronía audio↔video escrita dos veces**: tiempos de `animar_entrada` «medidos en el video» y copiados | `sonido_marca.py` l. 5–6 y 155–179 (2.25, 2.3, 2.5, 3.55, 4.93, 5.26, 5.42, 5.47, 5.95 …) vs `marca_aerospace.py` l. 240–317 (1.5·r, 1.9·r, 1.7·r, 0.35·r, 1.3·r, 1.1·r …) | Cambiar `ritmo`, la duración de una animación o el orden de un `play` desincroniza el sonido sin aviso. `ritmo≠1` ya no funciona con audio. |
| D2 | Tiempos de los reels en loop | `33-reels-promo.py` (T1/T2/T7 l. 21/137/294, `CONTROLADORES` l. 138–142, ventanas `3*i-1.5` l. 128, `4*i-2` l. 329/355, `desfase=4.0` l. 162, `theta` con `t<11` l. 190–193) vs `sonido_reels.py` (l. 95, 113, 125–132, 135–139: `(11.5, 2.2, 4.4, 6.6, 8.8)`, `3*i-1.5`, `4.0*i`, `("ReelATP", 12.0, 4.0)`) | Si se mueve una ventana del controlador, el «cambio de controlador» suena en otro momento. |
| D3 | Funciones físicas copiadas | `doppler_d`/`doppler_amp`: `33-reels-promo.py` l. 25–32 y `sonido_reels.py` l. 68–73 (con `T=12.0` por defecto repetido) | Dos fuentes de verdad de «la S del Doppler». |
| D4 | Datos de las ráfagas FSK «inventados dos veces» | `33` l. 48–54 (rng seed 5 tras ~600 k gaussianas) vs `sonido_reels.py` l. 87–94 (otro `default_rng(5)` sin esas llamadas) | Las semillas coinciden en el número pero no en el flujo: los bits que se ven en la cascada **no son** los tonos que suenan. Audio «inspirado en», no derivado de, la imagen. |
| D5 | Relojes | `reels_promo.Reloj` (l. 19–33) vs el `reloj=[0.0]` de `marca_vertical.fondo_reel` (l. 89–91) | En `ReelATP` el contenido corre en fase 4.0 s y el fondo en fase 0: sigue siendo periódico, pero hay dos relojes y dos desfases que deben coincidir a mano si algún día el fondo reacciona a la música. |
| D6 | Paleta | ver 1.5 | 7 hex en 10 archivos; `paleta.json` dice ser «fuente única» y **no la lee ni Manim ni PIL**. |
| D7 | Rótulos horizontales vs verticales | `rotulos_aerospace.py` (tarjeta/tercio/capítulo/cortinilla/cierre) y `marca_vertical.py` l. 175–265: mismas 5 piezas reescritas, con la nota «Mismos tiempos que `entrar_tarjeta`» | Un cambio de diseño hay que hacerlo dos veces; ya divergen (`regla_orbital` radio 0.055 vs 0.08, buffs, etc.). |
| D8 | Zonas seguras | `marca_vertical.py` l. 27–28 (+8.4/−7.4 «14 %/22 %») vs `promo.SEGURA["vertical"]` (arriba 10 %, abajo 20 %, der 14 %) y `lienzo.cabe()` | Tres definiciones de «zona segura de Instagram» con números distintos. |
| D9 | **Sistemas paralelos completos** | `promo.py`+`render_promo.py`+`promo_verifica.py` (formato, costura de bucle con piso de ruido, manifiesto `promo.json` con bloque `audio`) y `sfx.py`+`musica.py` (síntesis, 467+544 líneas) frente a `reels_promo.py`+`verificar_loop.py`+`sonido_*.py` | Cuatro generaciones de lo mismo. Las ideas buenas (manifiesto de audio medido contra la duración real; `lienzo.cabe` que falla si algo sale del cuadro; piso de ruido en la costura) ya existen y los reels nuevos **no las usan**. `pluck/whoosh/golpe/clic` de `sonido_marca.py` ≈ `blip/tick/barrido/aire` de `sfx.py`. |
| D10 | Scripts de render | `renderizar_reels.sh` y `renderizar_reels_promo.sh` son el mismo `una()` copiado (24 líneas c/u) | Un arreglo (p. ej. logs de error) hay que hacerlo 3 veces. |
| D11 | Cálculo de caché/fondos | `fondos_espaciales.fondo()` (caché 16:9, `_fondos`) vs `fondos_a_medida.fondo_a_medida()` (cualquier tamaño, **mismo directorio** `exports/estudio/_fondos`/`presentaciones/espaciales/_fondos` con convenciones de nombre distintas) | Se pisan por convención, no por diseño. |

### 1.5 Colores repetidos (medido con grep sobre `animaciones redes studio/content studio/tools studio/desktop marca`)

`#00D9FF`: 10 archivos · `#080F15`: 9 · `#0A0E27`: 6 · `#8E99A6`: 3 · `#93A4BD`: 2 · `#2A3742`: 2 · `#F59E0B`: 172 (academia, otra familia).
Casos concretos: `LINEA="#2A3742"` definido en `rotulos_aerospace.py:41` **y** en `33-reels-promo.py:16`; `paleta()` en `33` l. 59–62 reescribe `(8,15,21)`, `(0,217,255)`, `(242,243,244)` en RGB (= FONDO, CIAN, PLATA); `motor_carrusel.py:45` define `TENUE #93A4BD` (tema web Órbita) mientras Manim usa `TENUE #8E99A6` (marca): **dos «gris tenue» distintos** que además se llaman igual; `motor_carrusel.py:223` repite el cian como `(0, 217, 255, 0)`; `fondos_espaciales.py:434` (`ATMOSFERAS`) y los 18 temas llevan su propia copia. Parte de la divergencia es legítima (paleta del logo vs paleta web): el kit debe **nombrar ambas**, no fundirlas.

---

## 2. Riesgos y defectos concretos (archivo:línea)

Severidad: **A** = produce un resultado incorrecto hoy · **M** = se rompe con un cambio razonable · **B** = deuda/higiene.

### 2.1 Audio y loops

| Sev | Dónde | Hallazgo |
|---|---|---|
| **A** | `sonido_reels.py:53` (`colchon`) | El «colchón de ciclo entero» **no lo es**: `f + det*0.5/m.T*(k+1)` añade `±0.5·(k+1)` ciclos por periodo. Para k=0 (±0.5 ciclo) hay quiebre de pendiente y para k=2 (±1.5 ciclos) un **salto** de valor (`sin(2π·(n±1.5)+2)` ≠ `sin(2)`). Medido en memoria: salto de costura = 115× la pendiente media con 3 notas (83× con 4 notas), y en el master de los 3 reels la costura vale 0.20–0.32 frente a un paso máximo normal de ≈0.10 (OrbitEye, Modelo): un clic. La docstring (l. 3–7) afirma lo contrario. |
| **A** | `sonido_reels.py:147` + `:169` | `master` rota el buffer `-desfase`: para `ReelATP` (desfase 4.0) la **costura del buffer circular queda a los 8 s del video**, no en el empalme. El loop del reel empalma bien, pero el clic suena a mitad. Además el único «control» impreso (`costura: abs(x[0]-x[-1]).max()`) no compara con ninguna referencia, así que no puede fallar. |
| **A** | `sonido_marca.py:11` (docstring «Determinista») y `:21,95,144`; `sonido_reels.py:21,61` | Un `RNG` global se consume en el orden de las llamadas y `main()` salta las escenas cuyo mp4 no existe (`if not mp4.exists(): continue`, `sonido_marca.py:367`, `sonido_reels.py:159`). Medido: el audio de `ReelATP` sale **distinto** (diferencia máx. 0.075) si solo existe ATP que si existen los tres. Rehacer un solo video cambia su sonido. |
| M | `sonido_marca.py:155–179, 225–256` | Todos los eventos son literales en segundos (ver D1). `ESCENAS` (l. 278–282) enlaza por nombre de clase: renombrar una escena silencia su audio (se salta sin error). |
| M | `sonido_marca.py:376` | `loudnorm` de una pasada sobre un wav ya normalizado en `master`: puede mover la dinámica de forma distinta por escena; `-shortest` + AAC añade ~21 ms de retardo (ya lo sabe `verificar_loop`). Sin pruebas de nivel/duración. |
| M | `sonido_reels.py:111` | Código muerto: `(np.where(t<10.6,1,0)+np.where(t>=10.6,1,0))` vale siempre 1. `sonido_marca.py:80` otra línea muerta (`if False`); `:68` variable `k` sin uso; `ruido_filtrado` deja sin procesar la cola < 2048 muestras. |
| **A** | `verificar_loop.py:42` vs `:50` | Criterios incompatibles: modo PNG pasa si `salto < 1.6 × percentil 90` de los pasos (permisivo), modo MP4 si `salto/mediana < 1.6`. Un mismo loop puede salir OK en uno y CORTE en el otro. |
| **A** | `verificar_loop.py:53` | `cost` (discontinuidad de audio) se calcula y **nunca se imprime ni se evalúa**: la comprobación de audio anunciada en la docstring no existe. Tampoco hay `sys.exit(≠0)` en ningún caso, ni `if __name__ == "__main__"` (todo corre al importar; `sys.argv[1:2]` sin argumentos termina en `ValueError` de numpy/ffmpeg). |
| M | `verificar_loop.py:23` | 90×160: invisible para una costura local (un texto de 24 px, el VFO, la traza del osciloscopio). Y compara último↔primero comprimidos (el propio archivo lo admite en su OJO). La prueba buena sería evaluar la **función** del reloj en `t` y `t+T` (ver mejora M2). |

### 2.2 Estado global y fragilidad en Manim

| Sev | Dónde | Hallazgo |
|---|---|---|
| M | `marca_vertical.py:34–39` | `_texto` muta `config.pixel_width` a 20000 y lo restaura en `finally`. Seguro hoy (un hilo), pero cualquier `Text` creado desde un updater, un hilo o un `Animation` perezoso dentro de esa ventana ve un lienzo de 20000 px; y si Manim cambia dónde lee `pixel_width`, falla en silencio (texto partido). Usar `with tempconfig({"pixel_width": 20000}):` (misma idea, pero API pública y reentrante) o, mejor, pasar el ancho al constructor de `Text` si la versión lo admite. Se repite el patrón de tocar `config.*` en `promo.py:151–155`, `presentacion.py:226–230`, `figura.py:292–298`. |
| **A** | `30-logo-co-de-aerospace.py:73` | `LogoCoDeCierre` crea `Text(..., font="Montserrat")` directo, **sin** `registrar_fuentes()` (que solo se llama desde `rotulos_aerospace._texto`, l. 52, y 30 no importa `rotulos_aerospace`). En una máquina/contenedor sin Montserrat instalado cae a la fuente por defecto y el cierre sale con otra tipografía sin ningún error. |
| M | `rotulos_aerospace.py:81,149,156,174,192,196,201` | Tamaños derivados de `config.frame_width/height`: en `-r 1080,1920` (que conserva ancho y estira la cámara, según `marca_vertical.py:8–10`) estas funciones dan medidas equivocadas. Por eso existe el duplicado D7. Cualquier pieza nueva que importe una función horizontal «por comodidad» sale mal en vertical. |
| M | `marca_aerospace.py:111,174–183` | El contorno de las órbitas **no es hijo del grupo** hasta `usar_contorno()`: `logo.shift/scale` antes de ese momento no lo mueven (se compensa con `_caja_orbitas`), pero `rotate`, `flip` o `copy()` del logo (las referencias `self.luna`, `self.satelite` de la copia siguen apuntando a los originales) lo dejan inconsistente. Funciona porque los usos actuales son shift/mover_a. |
| M | `marca_aerospace.py:279` | Constante mágica `0.0048` para escalar cometa/estela (`k = escala/0.0048`) sin relación a nada documentado. `animar_entrada` mezcla geometría, tiempos y estilo en una función de 80 líneas: no hay forma de leer «cuándo ocurre qué» sin ejecutar (la raíz de D1). |
| M | `marca_vertical.py:23,25,28` | Import duplicado de `config`; constantes de zona (`SEGURA_*`) y posiciones absolutas (`6.3` l. 180, `5.7` l. 222, `6.4` en `32` l. 163, `8.15`/`6.35` en `reels_promo.py` l. 62/67) válidas solo para 1080×1920 con cámara de 25.28 unidades. Sin tests, un cambio de formato (4:5, 1:1) rompe todo sin avisar. |
| B | `32-marca-vertical.py:149,221` | Importa funciones privadas (`_texto`, `_fijar_contorno`) desde escenas: la API pública incompleta empuja a saltarse el encapsulado. |
| B | `33-reels-promo.py:183` | Para extraer el satélite construye un `LogoCoDe(altura=8)` completo (6 arcos, letras, AEROSPACE) y lo descarta. Añadir `LogoCoDe.satelite_solo()`. |
| B | `33-reels-promo.py:241–264` | El osciloscopio evalúa `error_banda` 220 veces por fotograma en Python puro (≈80 k evaluaciones/s de video, vectorizable con numpy en una llamada). Lo mismo, a menor escala, `fondo_reel` (`marca_vertical.py:133–135`): con `entrada=False` hace `trazo.become(completa)` en **cada** fotograma para las 3 órbitas sin cambios. |
| B | `33` n.º de reel | Los nombres de sección «1», «2», «7» (l. 19, 135, 292) y `T7`: huecos de numeración que apuntan a escenas planeadas o borradas; ninguna lista las declara. |

### 2.3 Rutas, entorno y caché

| Sev | Dónde | Hallazgo |
|---|---|---|
| M | `30:2`, `31:2`, `32:2`, `33:2` (+ docstrings `marca_aerospace.py:23`, `rotulos_aerospace.py:22`; y ≥ 20 módulos de `manim_extensions/` p. ej. `agentes.py:31`, `caos.py:41`) | `sys.path.insert(0, "/workspace/studio/content/manim_extensions")`. Localmente no existe y los scripts `.sh` suplen con `PYTHONPATH` (inofensivo). Pero `insert(0)` **gana** sobre `PYTHONPATH`: si `/workspace` existe (contenedor del estudio) con una copia vieja montada, esa versión se importa sin avisar. Reemplazar por una ruta calculada desde `__file__` o por un `conftest`/`manim.cfg`. |
| **A** | `motor_carrusel.py:37` (y `fondos_tematicos.py:25`) | Las fuentes oficiales (Rajdhani, DM Sans, Space Mono, Orbitron) se leen de `~/.local/share/fonts/codeaerospace` (fuera del repo, instaladas por otro script). En otra máquina o en CI: `OSError` en la primera `fuente()`; no hay validación previa ni mensaje claro. Montserrat sí va en el repo (`manim_extensions/fonts`). |
| M | `marca/renderizar_animaciones.sh:9,16–17`, `renderizar_reels*.sh:43,67` | (a) Los errores de Manim se descartan (`>/dev/null` y `>/dev/null 2>&1`): si una escena falla solo se ve un `cp` vacío o un `xargs` con código 123 sin mensaje. (b) `TMP=$(mktemp -d)` de `renderizar_animaciones.sh` no se borra nunca (sin `trap`) y acumula videos en `/tmp`. (c) `find ... -newer "$TMP"` depende de que el mtime del directorio no se actualice después del mp4: frágil. (d) Un `media_dir` por escena evita la corrupción en paralelo (bien, ya documentado en `SKILL.md:139`) **pero** tira la caché de textos y cada escena rehace Pango desde cero. (e) `renderizar_animaciones.sh` es secuencial (el resto usa `xargs -P`). (f) No hay «saltar si está fresco»: se re-renderiza todo. |
| M | `fondos_a_medida.py:29` | La «escritura atómica» usa `ruta.with_suffix(".tmp.jpg")`: nombre **fijo por clave**. Dos procesos que fabrican el mismo fondo a la vez (el caso que se quería evitar) escriben el mismo temporal y pueden corromperse entre sí. Añadir `os.getpid()` al nombre. |
| M | `fondos_a_medida.py:24–33` y `fondos_espaciales.py:40–59` | `tamano()` cambia `ANCHO/ALTO/XX/YY/PX` **globales**; los generadores los leen como globales de módulo. No es seguro con hilos ni con dos llamadas anidadas; `previo = FE.tamano(...)` está **fuera** del `try` (l. 24): si falla a mitad (p. ej. `MemoryError` en `_malla()`), el módulo queda con el tamaño nuevo y sin restaurar. Además parchea solo `fondos_tematicos` y `fondos_tematicos_2` por nombre (l. 53): un plugin de usuario que copie `XX/W/H` al importarse queda con la malla vieja. Funciona hoy porque `cargar_plugins()` importa esos módulos antes del cambio de tamaño (l. 22–24): dependencia de orden implícita. |
| M | `fondos_a_medida.py:17` | La clave de caché no incluye versión del generador ni del tema: tras editar `fondos_espaciales.py`/`temas/*.py` se siguen sirviendo JPG viejos hasta pasar `rehacer=True`. |
| M | `fondos_a_medida.py:22` | `TE.cargar_plugins()` se re-ejecuta en cada fallo de caché y vuelve a `exec_module` todos los plugins (efectos secundarios repetidos). |
| M | memoria (estimado, sin medir) | Una panorámica de 10 láminas es 10 800×1350: cada capa float32 RGB pesa ≈175 MB y un generador usa varias; orden de 2 GB. `validar` permite hasta 10 láminas (`motor_carrusel.py:~487`). |

### 2.4 `motor_carrusel.py`

| Sev | Línea | Hallazgo |
|---|---|---|
| **A** | 153–161 (`ajustar`) | Si el texto no cabe ni con `tam_min=18`, **devuelve 18 px igualmente** y el texto se desborda sin aviso. `validar` (l. 481+) solo cuenta caracteres (`titulo > 70`, `cuerpo > 330`), no mide con la fuente real. Resultado: un carrusel «válido» puede salir con texto fuera de caja; la única defensa es mirar la hoja de contacto. |
| M | 164–198 (`escribir`) | Cada llamada compone una capa RGBA del tamaño completo, difumina el alfa completo (`sombra`, l. 192) y repega la imagen entera. Una lámina hace 10–20 llamadas ⇒ decenas de desenfoques de 1080×1350. En `l_comparacion` (l. 405–414) y `l_texto` (l. 316) se hace además `img.copy()` y se vuelve a escribir «para medir». Lento y sin necesidad: medir con `ajustar()`/`partir()`, que ya existen. |
| M | 203–213 (`cargar_imagen`) | La rama final `Image.open(REPO / ref)` acepta **cualquier ruta** del JSON (incluido `../`). La barrera de privacidad (`PROHIBIDO_IMAGEN`, l. 61) es un `in` de subcadenas sobre `ref`: no cubre una copia renombrada de un sticker de tesis, ni mayúsculas, ni un archivo ajeno al repo. Para una regla «no negociable» (ESQUEMA.md) es una barrera débil. `spec["id"]`/`["serie"]` tampoco se sanean al armar la ruta de salida (l. 518+). |
| M | 555–570 (`main`) | `renderizar(spec)` no está en `try`: un sticker/fuente faltante aborta `--todos` y deja el resto sin renderizar; los errores de `validar` sí se saltan. |
| M | 234 (`marco`) | Abre y redimensiona `simbolo-plata.png` en cada lámina sin `lru_cache`. |
| B | 45, 223 | Colores y cian propios (ver 1.5). `pie_texto` sin validar longitud (límite de Instagram 2 200 caracteres, máx. 30 hashtags) ni texto alternativo. `CUIDADO.txt` usa un emoji (l. 542). |

### 2.5 Pruebas

- **No existe ninguna prueba automática** para `manim_extensions/marca_*`, `rotulos`, `reels_promo`, `estelas`, `sonido_*`, `verificar_loop`, `motor_carrusel` ni `fondos_a_medida` (`find` sobre `studio/content`, `studio/tools`, `redes`: cero `test*`). Lo que hay: `animaciones/pruebas_presentaciones.py` (buen modelo: contraste WCAG, fuentes, .pptx), tests del backend (`studio/backend/tests`) y smoke del escritorio (`studio/desktop/test`). El motor de contenido no está cubierto.
- La verificación hoy es «renderizo y miro» (`sonda_marca.py` mide IoU del logo; `verificar_loop.py` a mano).
- Control de versiones: según `git status` al inicio, **`marca/`, `redes/`, `marca_*.py`, `reels_promo.py`, `rotulos_aerospace.py`, `estelas.py`, `30–33-*.py`, `sonido_*`, `verificar_loop` aparecen sin versionar (`??`)**. El motor completo no tiene historial: un `git clean` o un error de disco lo borra.

### 2.6 Documentación de trabajo (`SKILL.md`)

- `.claude/skills/animaciones-code/SKILL.md` cubre `animaciones/` (ponencia, tesis, decks) y la app PySide6. **No menciona** `marca/`, reels, loops, `sonido_*`, `verificar_loop`, carruseles ni `fondos_a_medida` (grep de «reel|carrusel|marca_aerospace|sonido|loop»: sin resultados relevantes). El conocimiento de estas piezas vive en docstrings largos y en la memoria de las conversaciones.
- El SKILL tiene afirmaciones que el código ya contradice: «`app/render_launcher.py` solo descubre escenas de la raíz, no de `animaciones/`» (l. 143) frente a «La pestaña Renders descubre las escenas de la raíz y de `animaciones/`» (l. 118). Una de las dos es falsa.
- `marca/paleta.json` dice: «La usan marca_aerospace.py (Manim), la app de escritorio y las presentaciones». Solo la lee la app (`presentaciones.cjs:125`; `app.js:1043`).

---

## 3. Backlog priorizado (impacto × esfuerzo)

Escala: impacto 1–5 (qué evita/da), esfuerzo S (≤ medio día) · M (1–2 días) · L (semana). Prioridad = impacto/esfuerzo.

| ID | Mejora | Impacto | Esfuerzo | Prioridad |
|---|---|---|---|---|
| **M1** | Arreglar clic de loop, RNG por reel y hacer que `verificar_loop` pueda fallar (§2.1) | 5 | S | **1** |
| **M2** | Módulo `ciclos` (puro numpy) compartido por video y audio + prueba exacta de periodicidad | 5 | M | **2** |
| **M3** | Cronología de eventos: `animar_entrada` registra marcas; el audio las consume (adiós D1) | 5 | M | **3** |
| **M4** | Kit de marca único (`marca/kit.json` + loaders Manim/PIL/PPTX) y fuentes/rutas sin `/workspace` ni `~/.local` | 4 | M | **4** |
| **M5** | CLI única `marca` + manifiesto `piezas.json` (render→audio→verificación, caché por hash, logs) | 4 | M | **5** |
| M6 | Suite de pruebas (`pytest`) del motor: fotogramas, validación de textos, carruseles, audio | 5 | M | (incluye M1/M2; se hace por capas) |
| M7 | `Formato` único para rótulos (adiós D7/D8) usando `promo.Formato`/`lienzo.cabe` | 3 | M | 6 |
| M8 | Carruseles: medir desborde con la fuente real, `escribir` sin capas completas, rutas seguras | 4 | M | 7 |
| M9 | Fondos: `tamano()` como context manager + clave de caché con versión + tmp por PID | 3 | S | 8 |
| M10 | Plantillas de reel parametrizables por JSON (`reels/<id>.json`) | 4 | L | 9 |
| M11 | Render distribuido / caché de fotogramas por hash | 3 | L | 10 |
| M12 | Versionar el motor (commit) y actualizar `SKILL.md` con una sección «marca» | 4 | S | **hacer ya, sin código** |
| M13 | Unificar con el sistema `promo.py`/`sfx.py`/`musica.py`: elegir uno y retirar el otro | 3 | L | 11 |

### Propuestas concretas

**M1 · Audio de loop sin clic + determinismo + verificador que falla** (S)
- `sonido_reels.colchon`: cambiar el detune a ciclos enteros: `f_k,det = ciclo_entero(f, T) + det * (k + 1) / T` (±1, ±2, ±3 ciclos por periodo) y quitar la fase `+ k` o dejarla (con ciclos enteros ya no importa). Test: `abs(x[0]-x[-1]) < 3 × mediana(|Δx|)` sobre el master **sin** rotar.
- En `master`, hacer la rotación por `desfase` **antes** de verificar y verificar tanto en el buffer rotado como en el original: la costura del buffer circular es físicamente un punto que debe ser continuo; si lo es, rotarlo no crea clic.
- RNG por reel: `rng = np.random.default_rng(zlib.crc32(nombre.encode()))` creado dentro de la función de cada reel y pasado a `pluck/clic/brillo/ruido_circular` (hoy usan `sm.RNG` y `RNG` globales). Test: generar `ATP` solo y con los otros dos ⇒ `np.array_equal`.
- `verificar_loop.py`: envolver en `main()`; unificar criterio (`salto / mediana(pasos) < 1.6` en ambos modos); imprimir y evaluar `cost` de audio (`< 3`); `sys.exit(1)` si algo falla; aceptar `--png` con ≥ 2 archivos.
- Borrar código muerto (`sonido_reels.py:111`, `sonido_marca.py:68,80`).

**M2 · Módulo `ciclos.py` (video y audio leen lo mismo) + prueba exacta de loop** (M)
- Nuevo `studio/content/manim_extensions/ciclos.py`, **sin importar Manim** (solo numpy; así el audio lo importa sin arrastrar Pango):
  ```python
  @dataclass(frozen=True)
  class Ciclo:
      nombre: str; T: float; desfase: float = 0.0
      ventanas: dict[str, tuple[float, float]] = field(default_factory=dict)  # "PD": (11.5, 2.2) ...
  def doppler_d(tau, T): ...   # movidas aquí desde 33 y sonido_reels
  def doppler_amp(tau, T): ...
  def ventana(t, a, b, f, T): ...; def suave(u): ...   # movidas desde reels_promo
  CICLOS = {"ReelOrbitEye": Ciclo(...), "ReelATP": Ciclo(..., desfase=4.0, ventanas=CONTROLADORES), ...}
  ```
  `33-reels-promo.py` y `sonido_reels.py` importan `CICLOS[nombre]`; `Reloj(escena, ciclo)` toma `T` y `desfase` del objeto; `REELS` de audio se deriva de `CICLOS` (adiós D2, D3).
- Prueba exacta de periodicidad (sin compresión, en segundos): un `FotogramaPeriodico` que construye la escena una vez, fija `reloj.t = desfase` y captura `scene.renderer.camera.pixel_array`, luego `reloj.t = desfase + T` y vuelve a capturar; `np.abs(a-b).max() ≤ 2` (tolerancia por cuantización). Esto es **exacto** (misma función evaluada en `t` y `t+T`) y no depende del I-frame ni de la resolución. Coste: 2 fotogramas por reel a 270×480.

**M3 · Cronología de eventos compartida (video genera, audio consume)** (M)
- Añadir a `marca_aerospace.py` una pequeña clase `Marcas` y `marcar(escena, nombre)` que guarda `escena.renderer.time` en `escena._marcas`. `animar_entrada` llama `marcar` en cada hito: `orbita_0..5`, `luna_llega`, `satelite_llega`, `paneles`, `letras`, `punto_cae`, `aerospace`, `destello`. Al final de `construct` (o en `tear_down`) se escribe `<escena>.marcas.json` junto al mp4 (el `.sh` ya conoce la carpeta; `manim` deja el mp4 en `media_dir`, así que la ruta de las marcas se pasa por `MARCAS_DIR`).
- `sonido_marca.intro(m)` deja de tener `2.25`, `2.3`, `4.93`…: `t = marcas["luna_llega"]`. Si falta una marca, **falla** (en vez de sonar mal). `ritmo≠1` vuelve a funcionar y el audio sigue cualquier cambio de la animación.
- Para el fondo `fondo_reel` (órbitas a 0/0.5/1.0 s, 2 s) se publican también sus marcas, de modo que `orbitas_gigantes` (`sonido_marca.py:287–291`) las lea.
- Alternativa más ambiciosa (M10): que un único guion JSON declare la línea de tiempo y de él salgan tanto las `play(...)` como los eventos de audio; empezar por marcas es el 80 % del beneficio con el 20 % del riesgo.

**M4 · Kit de marca único** (M)
- Ampliar `marca/paleta.json` → `marca/kit.json` con tres bloques: `marca` (FONDO, MARINO, PLATA, PLATA_MEDIA, TINTA, PAPEL, CIAN, AMBAR, TENUE, LINEA), `web` (TINTA `#F1F5F9`, TENUE `#93A4BD`, TURQ, PANEL: la paleta del tema Órbita) y `tipografia` (rutas **relativas al repo**: copiar Rajdhani/DM Sans/Space Mono/Orbitron con su OFL a `marca/fuentes/` o `redes/fuentes_ttf/`), más `zona_segura` por formato.
- `marca_kit.py` (puro Python, sin Manim/PIL) con `kit()`, `hex(id)`, `rgb(id, alfa)`, `rgb255(id)`. Tres consumidores: `marca_aerospace.py` (constantes `FONDO…AMBAR` pasan a `= kit.hex(...)`), `motor_carrusel.py` (`TINTA…PANEL`, halo l. 223, rutas de fuente) y `decks_espaciales`/`temas/orbita` (para pptx). `33.paleta()` se genera con `rgb255`. La app ya lee el mismo JSON.
- Una prueba «lint de marca»: recorre `*.py`/`*.cjs` y falla si encuentra un hex de la marca fuera del kit (lista blanca explícita para los 18 temas). Detecta casos como `LINEA` duplicado.
- Rutas: un único `ruta_extensiones()` en `marca_kit.py` y quitar los `sys.path.insert("/workspace/...")` de 30–33 (y, por separado, de los ≥ 20 módulos que los traen). `motor_carrusel.FUENTES` pasa a la ruta del kit con un mensaje claro si falta.

**M5 · CLI única y manifiesto de piezas** (M)
- `marca/piezas.json`: una entrada por escena con `archivo, escena, formato(-r), fps, salida, ciclo|null, audio(fn), duracion_esperada`. Sustituye `ESCENAS`/`ESCENAS_V`/`REELS` y las listas dentro de los `.sh`.
- `python3 -m marca render [--solo X] [--calidad qh] [--jobs 4]` → mismo `una()` (media_dir propio, `--disable_caching`), pero: log completo en `exports/.../logs/<escena>.log` y cola de 20 líneas en pantalla al fallar; `trap` que limpia temporales; **saltar si fresco** comparando hash(escena.py + `manim_extensions/*.py` + calidad) guardado junto al mp4; escritura atómica (`.part` → `rename`). `... audio` y `... verificar` encadenados con `--todo`.
- Reutilizar `promo.formato()` y `promo_verifica.medir_bucle` en vez de crear una cuarta variante (ver M13).

**M6 · Pruebas automáticas del motor** (M, por capas; carpeta `studio/content/tests/`, `pytest`)
1. *Humo de render:* para cada escena de `piezas.json`, un fotograma a 270×480 (`-s`), comprobar: tamaño, no es monocolor, la fuente resuelta es Montserrat (`manimpango.list_fonts()` o el nombre en el SVG), sin excepciones. ~10 s/escena.
2. *Loop exacto:* M2.
3. *Textos:* validar cada rótulo con `lienzo.cabe()` (ya existe y lanza `FueraDelLienzo`) o con el bbox contra `zona_segura` del kit. Para carruseles: `ajustar()` devuelve además un booleano `cabe` y `validar()` lo propaga como error si `tam < tam_min` (corrige §2.4).
4. *Carruseles:* renderizar `specs/prueba` y comparar contra una hoja dorada con tolerancia (SSIM ≥ 0.98 por lámina) o, más barato, hash de las cajas de texto; cada tipo de lámina con texto extremo (título de 70 caracteres).
5. *Audio:* para cada pieza con `ciclo`: costura (M1), duración == `ciclo.T` ± 1 muestra, RMS dentro de ±1.5 dB de −17 LUFS aprox., sin recorte (`peak < 0.95`).
6. *Reproducibilidad:* el wav de una pieza no depende de qué otras existan (M1).
7. *Privacidad:* `cargar_imagen` rechaza rutas fuera de `STICKERS`/`marca` y cualquier `tesis_*` aunque venga renombrado (comparar hash contra una lista de stickers permitidos).
Con (1)–(3) se cubren los fallos de este informe que hoy solo se ven «mirando».

**M7 · `Formato` único para rótulos** (M)
- Una función `formato(escena)` que devuelve `(W, H, zona_segura, escala)` desde la **cámara**, nunca desde `config`; las piezas (`tarjeta_titulo`, `tercio`, `capitulo`, `cortinilla`, `cierre`) reciben ese objeto y se eliminan los duplicados de `marca_vertical.py` (≈90 líneas). Los parámetros distintos (emblema arriba, numeral enorme) pasan a ser variantes del `Formato`, no copias de código. Reusar `promo.Formato` (que ya garantiza 135 px/unidad en ambos formatos) en vez de inventar el cuarto.

**M8 · Carruseles** (M): ver M6.3 para el desborde; `escribir` sombra solo en la caja del texto (`capa.crop(bbox)`), medir con `ajustar` (sin `img.copy()`), `lru_cache` para `marco`, `try/except` por spec en `main` con resumen final y código de salida ≠ 0, `ruta = (REPO/ref).resolve()` + `is_relative_to(permitidos)`, saneo de `id`/`serie` con regex `^[a-z0-9-]+$`, validación de `pie_texto` (≤ 2 200 caracteres, ≤ 30 hashtags).

**M9 · Fondos** (S): `@contextmanager def lienzo(ancho, alto): previo = tamano(...); try: yield; finally: tamano(*previo)`; el `previo = tamano()` pasa dentro del `try`; tmp con `os.getpid()`; clave de caché con `hash(inspect.getsource(generador)) + tema.tinte`; cachear `cargar_plugins()` con una bandera.

**M10 · Plantillas de reel por JSON** (L): `reels/<id>.json` = `{"ciclo": {"T":12,"desfase":0}, "cabecera": {...}, "capas": [...], "leyendas": [{"grande","pequena","ventana":[a,b]}], "chip": {...}, "audio": {...}}`. Un `ReelPlantilla(Scene)` único construye cabecera, leyendas, chip y fondo a partir del JSON y deja un hueco `capa_central(self, reloj)` en Python (cascada, antena, anillo). Convierte «agregar un reel» en JSON + una función de dibujo, y permite revisarlos desde la app. Hacerlo **después** de M2/M3: sin ciclo declarativo no hay qué parametrizar.

**M11 · Render distribuido/caché** (L): con M5 en su sitio, el hash de entrada permite un directorio de caché compartido (disco de red o bucket) y que `-P N` use cola de trabajos en varias máquinas (`xargs -P` → lista de comandos por SSH, o el contenedor del estudio). Caché de fotogramas PNG por `hash(escena, t)` para iterar diseño sin volver a pasar por Pango. No empezar hasta que M5 y M6 existan: sin hash estable no hay caché confiable.

**M12 · Versionar y documentar** (S, sin código): commit de `marca/`, `redes/`, `marca_*.py`, `reels_promo.py`, `rotulos_aerospace.py`, `estelas.py`, `30–33`, `sonido_*`, `verificar_loop` (lo decide el dueño; el repo no tiene `user.name` según `SKILL.md:142`). Añadir al SKILL una sección «Marca y redes» (o una skill `marca-reels`) con: flujo render→audio→verificación, regla «todo es función periódica del reloj», trampa de `-r 1080,1920`, zona segura, y corregir la contradicción de `SKILL.md:118/143` y el texto de `paleta.json`.

**M13 · Un solo sistema promo/sonido** (L): decidir entre el camino `promo.py`+`sfx.py`+`musica.py`+`promo_verifica.py` (con manifiesto y herramientas ya probadas por el backend) y el nuevo `reels_promo`+`sonido_*`. Mi lectura: conservar `promo_verifica.medir_bucle` (piso de ruido) y el bloque `audio` del manifiesto, y migrar la síntesis `sonido_marca` (campana, whoosh) a `sfx.py` como eventos nombrados. No es urgente, pero cada mes que pasa se duplica más.

---

## 4. Las 5 mejoras de mayor retorno para hacer YA

Orden recomendado (cada una deja el repo mejor aunque no se haga la siguiente).

### 1) Arreglar el clic del loop y volver deterministas los audios (M1) — ~2 h
**Por qué ya:** hay un defecto audible hoy en los tres reels (y el verificador no puede detectarlo).
**Pasos**
1. `sonido_reels.py:53` → `x += np.sin(2*np.pi*(ciclo_entero(f, m.T) + det*(k+1)/m.T)*t + k)` (detune en ciclos enteros).
2. RNG por pieza: `def rng_de(nombre): return np.random.default_rng(zlib.crc32(nombre.encode()))`; pasar `rng` a `pluck/clic/brillo/whoosh/ruido_filtrado/ruido_circular` (parámetro opcional `rng=None` que cae a uno local seeded; eliminar `RNG` globales).
3. `verificar_loop.py`: `main()`, un solo criterio, evaluar `cost < 3`, `exit(1)`; eliminar el `if __name__` ausente.
4. `sonido_reels.main()` llama a la verificación de costura **sobre el buffer sin rotar** y aborta con código ≠ 0 si falla.
5. Prueba: `pytest studio/tools/test_audio_reels.py` con (a) costura < 3× paso, (b) ATP solo == ATP junto a los otros.
**Hecho cuando:** `python3 sonido_reels.py` imprime `costura OK` (razón < 3) en los 3 reels y el wav de ATP es idéntico se generen uno o tres.

### 2) Módulo `ciclos.py` + prueba exacta de periodicidad (M2) — ~1 día
**Por qué ya:** elimina D2, D3 y D5, y reemplaza la verificación por compresión por una exacta.
**Pasos**
1. Crear `ciclos.py` (sin importar Manim) con `Ciclo`, `suave`, `ventana`, `doppler_d/amp` y el registro `CICLOS` (nombre → `T`, `desfase`, `ventanas`).
2. `reels_promo.Reloj(escena, ciclo)`; `33-reels-promo.py` toma `T1/T2/T7`, `CONTROLADORES`, `desfase` de `CICLOS`; las `leyenda(..., 3*i-1.5, 3*i+1.5, ...)` pasan a `ciclo.ventanas[f"ley{i}"]`.
3. `sonido_reels.py` importa lo mismo; `REELS` se deriva de `CICLOS` (adiós `("ReelATP", 12.0, 4.0)`).
4. `tests/test_loop_exacto.py`: instancia la escena, fija `reloj.t` a `desfase` y a `desfase+T`, captura `pixel_array` a 270×480 y exige `max|a−b| ≤ 2`. Un fallo imprime las coordenadas del píxel (ubica el objeto no periódico).
**Hecho cuando:** cambiar una ventana en un solo sitio mueve imagen **y** sonido; el test de loop pasa en los 3 reels sin ffmpeg.

### 3) Marcas de tiempo: el video genera, el audio consume (M3) — ~1 día
**Por qué ya:** es la causa raíz de D1; hoy `ritmo≠1` o tocar un `play` rompe la banda sonora sin aviso, y hay 12 escenas con audio.
**Pasos**
1. `marca_aerospace.py`: `marcar(escena, nombre)` (guarda `escena.renderer.time`) y llamadas en `animar_entrada` (órbitas 0–5, luna, satélite, paneles, letras, punto, AEROSPACE, destello), `animar_salida`, `sting_logo`; `fondo_reel` marca `orbita_giga_0..2`.
2. Escribir `<Escena>.marcas.json` en `tear_down` (ruta por variable de entorno `MARCAS_DIR`, que fijan los `.sh`).
3. `sonido_marca.intro/ensamble/cierre/sting/orbitas_gigantes` leen las marcas (`M = cargar(nombre)`; `m.poner(M["luna_llega"], …)`). Si falta una marca: error explícito.
4. Prueba: renderizar `LogoCoDeIntro` a 270×480 y comparar marcas con una tabla dorada ±1 fotograma (documenta los tiempos reales, hoy solo «medidos»).
**Hecho cuando:** `animar_entrada(..., ritmo=0.7)` produce un audio que coincide sin tocar `sonido_marca.py`.

### 4) Kit de marca único y rutas sin `/workspace` ni `~/.local` (M4) — ~1 día
**Por qué ya:** dos grises «tenue», `LINEA` duplicado y el motor de carruseles que falla en cualquier máquina sin las fuentes instaladas a mano; el kit alimenta además PowerPoint.
**Pasos**
1. `marca/kit.json` (bloques `marca`, `web`, `tipografia`, `zona_segura`) + `marca_kit.py` (`hex`, `rgb`, `rgb255`, `fuente(clave)`, `ruta_extensiones()`).
2. Copiar al repo las TTF de Rajdhani/DM Sans/Space Mono/Orbitron (con sus licencias OFL) y que `motor_carrusel.F` y `fondos_tematicos._fuente` las resuelvan por el kit, con error claro («falta DMSans-400.ttf; ejecuta …»).
3. Sustituir constantes duplicadas (`marca_aerospace.py:51–58`, `rotulos_aerospace.py:40–41`, `33` l. 16 y 59–62, `motor_carrusel.py:45,223`) por lecturas del kit; quitar `sys.path.insert("/workspace/...")` de 30–33.
4. Prueba «lint de marca»: falla si aparece un hex de la marca fuera de `kit.json` (lista blanca para temas).
**Hecho cuando:** `grep -rn "#00D9FF"` solo da `kit.json` y los temas; `python3 motor_carrusel.py --validar specs/prueba/*.json` funciona en una máquina limpia.

### 5) CLI única con manifiesto, logs, caché por hash y versionado (M5 + M12) — ~1 día
**Por qué ya:** hoy un error de render es invisible (`>/dev/null`), `/tmp` se llena, todo se re-renderiza y el motor completo no está en git.
**Pasos**
1. **Primero, sin código:** commit de los archivos listados en M12 (el dueño decide) y sección «Marca y redes» en `SKILL.md` (corregir l. 118/143).
2. `marca/piezas.json` y `marca/cli.py` (`render`, `audio`, `verificar`, `todo`) que sustituyen a los tres `.sh`: `una()` único; log por escena y cola de 20 líneas al fallar; `trap`/`TemporaryDirectory`; salto si el hash (escena + `manim_extensions` + calidad) no cambió; salida con `.part` + `rename`; código de salida ≠ 0 si cualquier pieza falla.
3. Encadenar: `todo` = render → audio (marcas, M3) → verificar loop (M1/M2); imprime una tabla pieza/duración/costura/LUFS.
**Hecho cuando:** `python3 -m marca todo` re-renderiza solo lo cambiado, falla con mensaje legible si una escena rompe y deja una tabla de verificación.

### Lo que NO recomiendo hacer todavía
- Render distribuido (M11) y plantillas JSON de reel (M10): rentables solo cuando existan el ciclo declarativo (M2) y el hash estable (M5).
- Reescribir `decks_espaciales.py`: es grande pero tiene su propia batería (`pruebas_presentaciones.py`) y no es la fuente de los defectos hallados; partirlo en módulos puede esperar.
- Fusionar `promo.py`/`sfx.py` con lo nuevo (M13) antes de tener pruebas (M6): sin red de seguridad el riesgo supera el beneficio.

---

## Anexo: cómo se midió lo que no es lectura

Script en el scratchpad (no en el repo), importando `sonido_reels`/`sonido_marca` sin llamar a `main()` (no escribe wav ni mp4):
- Costura del `colchon` aislado (3 notas / 4 notas): |x[0]−x[−1]| / media(|Δx|) = 115 / 83.
- Master sin rotar de cada reel: costura 0.32 (OrbitEye), 0.25 (ATP; su paso máx. normal es 1.38 por la onda cuadrada del servo, así que ahí el clic queda enmascarado en amplitud pero sigue siendo una discontinuidad), 0.20 (Modelo); paso máximo normal ≈ 0.11 / 0.10.
- Determinismo: `ReelATP` generado tras `OrbitEye` frente a generado solo: `allclose = False`, diferencia máxima 0.0746.
- Metadatos de los mp4 existentes: reels de 12.000 s / 360 cuadros a 30 fps y audio AAC de 12.000 s (la duración coincide; no hay desfase de longitud).
