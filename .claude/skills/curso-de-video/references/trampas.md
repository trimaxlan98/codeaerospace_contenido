# Cosecha de trampas

Acumulada a lo largo de 27 cursos. **Todas siguen vigentes**: cada familia
nueva vuelve a tropezar con las mismas si no se leen antes de escribir clips.
La cosecha específica de cada familia está en la sección final de su
`docs/plan_contenido/curso-NN-*.md`; lee también la de la familia vecina más
parecida a la que vas a producir.

## Herramientas del pipeline

- `render_local.py` **aborta si falta CUALQUIER clip** declarado en
  `curso.json`: crear stubs `class ClipN(Scene): self.wait(1)` antes de
  paralelizar agentes.
- **`render_jobs/` y `exports/` son ENLACES SIMBÓLICOS al segundo disco**
  desde 2026-08-28. Dentro del contenedor el enlace queda colgando (el
  destino no está montado), así que nada puede leerse por
  `/workspace/render_jobs/...`. `render_local.py` apunta manim a
  `/media/scene.py`, que ya va montado; cualquier herramienta nueva que lea
  del repo dentro del contenedor tiene el mismo problema.
- `--frames 8` **muestrea**: puede caer justo en un relevo de pie y enseñar un
  frame casi vacío. No es un fallo; pero el `final_state` se saca del último
  frame real con ffmpeg.
- `--calidad qh` escribe en el mismo directorio que `ql` y lo pisa: copiar a
  `render_jobs/qh/<slug>/`.
- `guiones.py` escribe en `guiones/<slugify(NOMBRE)[:40]>/`, **no** en el slug
  del curso.
- El numpy del host ya corrompió arrays en silencio una vez (1.26.4 de sdist
  sobre Python 3.14): lo que sintetiza o mide números fuera del render corre
  **en el contenedor**, y `sfx.py` lleva un canario que aborta solo.
- **`render_vertical.py` borra `videos/` antes de componer, también con
  `--solo-componer`.** Si vas a comparar el `scene.py` del disco con el que
  compone hoy la herramienta, pon el mp4 a salvo ANTES de invocarla.
- **Un render que "no está" puede estar entero.** Si la herramienta murió
  entre el final de manim y la copia, el vídeo bueno sigue en
  `videos/scene/<resolucion>/<Escena>.mp4`. Comprueba que el `scene.py` del
  disco y el que compone hoy tienen el mismo md5, y reúsalo: son 10-15 min
  de render por pieza pesada.
- **Nada de `exports/` ni de `render_jobs/` está versionado**, y desde
  2026-08-28 viven en otro disco. Una migración se los puede llevar sin que
  Git diga una palabra: el 29 apareció un curso entero con solo su `voz/`.
  Lo único irreproducible en local es esa `voz/` (la sintetiza el VPS); todo
  lo demás se rehace desde el fuente, y rehacerlo dio cifras idénticas.

## Animación

- **`Transform` solo entre gemelas de estructura IDÉNTICA.** Distinta
  estructura = glifos rotos. Toda pieza que cambia necesita su gemela `con_*`.
  Casos que rompen la gemelidad sin que se note: una pieza que nace **sin
  valores** (textos de 0 glifos), un número de filas distinto (reservar con
  `filas_max` y rellenar con guiones), un resaltado que añade un `Rectangle`
  solo en una de las dos (reservarlo con un flag opt-in).
- **Los kwargs de `play()` PISAN los de cada animación.** Medido en el
  fuente de manim 0.20.1 (`Scene.compile_animations` termina con
  `for animation in animations: for k, v in kwargs.items(): setattr(...)`).
  Consecuencia, medida: `play(Transform(c, n, run_time=0.02), run_time=1.10)`
  deja el Transform en **1.10**, y el contador pasa todo ese rato con los
  dígitos a medio morfar. Un `Succession(Wait(0.55), Transform(..., 0.02))`
  **sí** sobrevive: al Succession se le pisa el total, pero sus hijos
  conservan sus tiempos, así que el morfeo sigue durando 0.02.
  Lo simple y seguro es `contador.become(nuevo.move_to(contador))` **fuera**
  de cualquier `play`. Ancho fijo (`03d`) en los contadores, siempre.
- `set_opacity` **enciende el fill** (no solo el trazo). `Indicate` va sobre
  la versión `_con_fondo`.
- `.animate` re-sube el VGroup al frente: cuidado con el orden z.
- `interpolate_color` exige `ManimColor`; las constantes `C_*` de las familias
  son `str`.
- Las etiquetas de `Grafica` son hijos internos: no aparecen si se animan
  `.ejes` / `.curva` por separado.
- **`Axes` cruza los ejes por el ORIGEN.** Un panel cuyo rango no incluye el
  cero (una fase de −190 a −85, una magnitud de −15 a 50 dB) deja una recta
  pegada al borde o en mitad del cuadro, con su etiqueta encima de la curva.
  Si el origen no cae en la esquina, se dibuja el marco a mano.
- Una pieza que entró **por sus hijos** (`Create(p.ejes)`, `FadeIn(p.barras)`)
  hay que consolidarla con `self.remove(*p.get_family()); self.add(p)` antes
  del primer `Transform` del grupo entero.
- Una **gemela** recién construida nace donde la fábrica la deja (casi siempre
  centrada en ORIGIN): si se transforma sin recolocarla antes, el `Transform`
  arrastra la pieza entera hacia el centro del cuadro.
- Un vector de módulo cero se dibuja como `Dot` invisible.
- `move_to` centra el **bounding box**: una figura asimétrica (un lóbulo de
  antena) hay que anclarla por su propio origen.
- Un localizador que cachea el centro perezosamente queda mudo si se le pide
  por primera vez después de mover el mobject.
- `MoveAlongPath` va reparametrizado: una ficha que termina su recorrido en un
  nodo se le monta encima — parar en ~0.55 del enlace y marcar la entrega
  encendiendo el nodo.
- Cálculos caros dentro de `updaters` (integrales con n=200) cuestan render:
  precalcular.
- `numpy 2.x`: `np.cross` ya no acepta vectores 2D.
- `\oiint` no compila en el LaTeX de la imagen.
- En `ql` la rejilla fija es casi invisible: no juzgar contraste por el `ql`.

## Composición y legibilidad

- **Nada encimado**: es la regla dura del proyecto y se verifica frame a
  frame, uno a uno.
- Las piezas densas (cabeceras, tablas, pilas) **se dimensionan midiendo**,
  no a ojo: una sonda en el contenedor que imprima ancho de caja / rótulo /
  valor campo a campo. La sonda tiene que replicar la subclase `Text` con
  sombra del style_block, o el glifo del espacio infla el bbox y da falsos
  positivos.
- **Escalar un VGroup encoge también la letra** (a 0.58 los rótulos ya no se
  leen): pasar `ancho`/`alto`/`fs` a la pieza en vez de escalar.
- Dos piezas densas lado a lado dejan los campos a ~6 px: apiladas a todo el
  ancho se leen.
- Rótulos de arista y de nodo tienen carriles propios; lo que viaje **por
  encima** del cable, no sobre él, y con `ocultar_etiquetas()` si hace falta.
- Un identificador largo (una MAC de 17 caracteres) se rotula por su cola, que
  es lo que distingue.
- `Rotulos.mostrar` cobra ~0.25 s extra de salida en cada relevo: contarlo al
  estimar duraciones.
- Un rótulo del carril inferior mostrado **antes** de dibujar una rejilla o una
  tabla queda debajo de ella.
- Los rótulos del momento anterior se apagan **antes** del relevo, o el frame
  muestreado enseña la cifra nueva con el rótulo viejo. (Con subtítulos, lo
  mismo con el pie.)
- **Un resalte que entra con `FadeIn` mientras el anterior sale con `FadeOut`
  deja DOS en pantalla medio segundo**, justo el que se usa para mirar:
  `Transform` sobre UN único mobject.
- **`Transform(pieza, gemela)` sobre una `_Anclada` cuyos submobjects entraron
  sueltos** (`FadeIn(pz.ejes)`, `Create(pz.circulo)`) mete la pieza ENTERA en
  escena y **por encima de todo**: hay que volver a poner los rótulos delante
  con `self.add(rotulo)` justo después.
- **`cierre_leccion` solo apaga lo que se le pasa**: si dibujaste `.curva` y
  `.area` de una pieza suelta, pasa TAMBIÉN `.ejes`, o la línea del eje
  sobrevive cruzando las dos frases del cierre.
- **Dos piezas solo son gemelas si comparten EJE.** Dos espectros de Welch con
  trozos distintos tienen 129 y 257 bins: no se puede `Transform` una en otra,
  se dibujan como dos piezas sobre el mismo rango.
- Una curva **sin techo natural** sale como un segmento horizontal pegado al
  borde si te fías del `np.clip` de la pieza (se lee como saturación, que es lo
  contrario de lo que hace): recorta los PUNTOS antes de dibujar.
- Un contador de cifras dentro de una animación larga deja dígitos a medio
  morfar. Dos formas que funcionan: `Succession(Wait(0.55), Transform(cont,
  nuevo, run_time=0.02))` (los hijos conservan su tiempo aunque el play pise
  el total), o `cont.become(nuevo.move_to(cont))` fuera del play. La que NO
  funciona es pasar el `Transform` corto DIRECTAMENTE al play — ver arriba.
  Y el contador se releva **después** del movimiento que lo justifica: antes,
  la cifra se adelanta a la pieza.
- Un clip que sale en 26–27 s se engorda con `wait`, no con más contenido.

## Tipografía

- Texto en pantalla **estrictamente sin acentos**; los acentos viven en
  `curso.json` (título y descripción), que no se renderiza.
- Rajdhani y Space Mono no traen superíndices, ni griegas, ni `⁻¹`, ni `≈`:
  `10^-3`, `λ`, `Σ`, `φ`, `σ` van en `MathTex`. Space Mono escribe `10⁶` como
  `10'`. `tag_hud` solo ASCII.
- **Rajdhani tiene DOS defectos de tamaño, los dos medidos en el contenedor y
  ninguno visible a ojo en un frame suelto:**
  1. **parte palabras a 16–17 px** — "retardada" sale "ret ardada";
  2. **junta las palabras por debajo de 22 px** — "por separado" salió
     **"porseparado"** en el `qh` de una lección ya publicada.
  Space Mono no tiene ninguno de los dos a ningún tamaño del curso. Por eso los
  helpers imponen **dos suelos**: 18 px para un rótulo de una palabra y **22 si
  tiene más**. Para etiquetas de varias palabras, mejor `tag_hud` directamente.
- El ancho de `Text` **no escala continuo** con `font_size`: 11 y 13 miden lo
  mismo. Bajar un punto no reduce nada; hay que acortar la cadena.
- Se caza con una sonda que renderice los rótulos REALES a varios tamaños y se
  mire el PNG (`texto2.py` del curso 27). Medir el bbox no basta: el problema
  está en los avances entre glifos, no en la caja.

## Honestidad con las cifras

Esta es la categoría que **no detecta el render**: solo se caza midiendo.

- **LA MALLA DECIDE, y por eso hay cifras que NO se rotulan.** La profundidad
  de un nulo, de un notch o de los ceros de un CIC depende de cuántos puntos
  tenga la rejilla: −119 dB con 4096 y −141 con 16384; −39.7 con 2048 y −240
  con 4096. Se rotula lo que **no se mueve** al cambiar la malla — la posición
  del nulo, el nivel de los lóbulos, el ancho del hueco. Por lo mismo, el
  "margen desperdiciado" de un diseño por ventanas no se mide de pico a nulo
  (91 dB, inflado) sino contra los lóbulos (27.2 dB).
- **Una cifra puede ser cero por casualidad.** `h[79]` de un resonador vale 0
  para radio 0.92, 1.00 y 1.05 (cae en un cruce por cero del seno): rotularlo
  junto a la palabra "inestable" habría enseñado un 0.0. Usa el máximo de la
  cola, no una muestra suelta.
- **Una magnitud puede ser recta solo en un tramo.** La fase de un FIR
  simétrico es una recta DENTRO de la banda de paso; ajustarla entera da 1.7
  rad de residuo y una conclusión falsa.
- **Una cifra sin su condición miente.** La caída de un CIC no es un número:
  −0.42, −2.70 o −11.61 dB según cuánta banda uses. Se rotulan las tres con la
  condición dentro del propio rótulo.
- **Comparar unidades distintas infla un lado.** El coste de una FFT en
  multiplicaciones complejas contra el de la convolución directa en reales
  multiplica la FFT por cuatro y da un cruce falso (M = 16 en vez de 24).
- **Una demo que solo funciona con tu semilla no es una demo**: barre semillas
  (y duración, y SNR) hasta un caso que acierte en todas, y si no lo hay, dilo.

- Si se dibuja una **ventana** de una simulación más larga, la estadística se
  mide sobre la ventana dibujada. Citar la corrida entera mientras se ve un
  trozo es mentir.
- Los datos que la librería no calcula (adopción de IPv6, número de AS de
  Internet) se declaran como medición pública **y en otro color**, para que el
  cian siga significando "calculado aquí".
- Comparar la **media** de dos trazas cortas puede invertir la conclusión
  (CUBIC parecía peor que Reno). Si la comparación honesta no cabe, se dice en
  el pie que compararlas así sería mentir.
- Un formateador que redondea puede escribir un rótulo **falso**
  (`fmt(0.5, 0)` → "0 Mb/s") y pasar el render tan campante.
- Una función que codifica una unidad (viajes, rondas) usada con el parámetro
  a 1 dibuja dos barras **iguales** junto al rótulo "5.6× mejor".
- Las leyes que se enseñan tienen que **cerrar** con los números dibujados (la
  ley de Little daba 24.5 % de error con magnitudes ingenuas y 1.0 % con las
  correctas).
- Los algoritmos con condición de parada devuelven a veces el máximo en vez de
  lo real (`conteo_al_infinito` daba 12 rondas cuando lo honesto era 7).
- Signos: el área de un paralelogramo y el volumen de una caja los llevan; una
  `svd()` puede dar reflexiones — para que "gire" hay que elegir la matriz con
  `det U = det V = +1`.
- Cuando el número depende de una semilla o de un hash real, **escanear en la
  validación** la semilla/el nombre que da la narrativa buena y fijarlo como
  constante del style_block.
- Al corregir un bug de la librería: los `final_state` de `curso.json`
  **también citan cifras**, y otros clips pueden llevar rodeos que compensaban
  el bug. Revisar ambos.

## Producción

- **Narración SERIAL**, siempre: dos `guiones.py` a la vez dan 429 del TTS.
- Los picos de audio vienen calientes de fábrica: medir SIEMPRE, re-muxear a
  −1.5 dB lo que pase de −0.5 dB, y a −2.5 dB lo que toque 0.0 (recorte real).
- El uplink al VPS va a ~100 KB/s: 100 MB de `qh` tardan ~25 min. `scp` en
  background, no con timeout de 10 min.
- Un corte de cuota mata a los subagentes a media faena. Se relanzan con el
  mismo contrato más "hay trabajo parcial en disco, re-valida todo": funciona.
- Las corridas **headless de madrugada comparten la cuota de sesión** del
  usuario: un encargo grande se hace en sesión interactiva con agentes, no por
  cron.
- Los mejores hallazgos vienen de agentes que **miden en vez de fiarse** de lo
  que el orquestador les dio: en una sola familia encontraron doce defectos
  reales de la librería.

## Estilo LIENZO (curso 31; todas medidas, ninguna supuesta)

- **La cifra grande no cabe.** Space Mono BOLD a cuerpo 128 gasta **1.061
  unidades por carácter** y la zona segura vertical son 5.76: **5 caracteres**.
  "7 200 000 000" mide 14.10 y el guardián aborta. La escala cerrada baja de
  peldaño sola (128/112/96/80/72/64/56 = 5/6/7/8/9/10/12 caracteres), pero la
  lección editorial es otra: **el número de un reel se escribe corto** — 7 200
  con la etiqueta "millones", no 7 200 000 000.
- **El espacio de una monoespaciada es un abismo**: "7 200" se leía como dos
  números. Los grupos de miles van en `Text` sueltos separados a mano.
- **Las unidades no sobreviven a las versalitas.** La etiqueta va en
  mayúsculas y "MHz" sale "MHZ", "ms" sale "MS", "mV" sale "MV" (que es otra
  unidad). Se escriben con todas sus letras: "megahercios", "milisegundos".
- **Centrar el dibujo en su franja está mal.** Cualquier dibujo más bajo que
  la franja queda a dos unidades de su cifra y la composición se parte en dos
  mitades sin relación. Se apoya en el SUELO de la franja; el vacío se
  acumula arriba, que es donde sí es aire.
- **El acento traslúcido sobre el fondo no existe.** Medido: ámbar `#F5A31B`
  sobre `#0B1B33` al 26–45 % da (72,62,45), verde oliva sucio; al 14 % da
  (44,46,48), un gris que ya no es ámbar. No hay ventana buena: las piezas de
  área van con **trazo** y el fondo del lienzo dentro, opaco.
- **Barras que se tocan son una losa.** Doce tareas pegadas no se pueden
  contar. El hueco se le quita al ANCHO de cada barra, no a su sitio, para que
  la escala de tiempo no mienta.
- **La 'y' de una palabra con descendente descuelga el wordmark**: alinear dos
  tokens por el borde inferior sube media equis el que lleva descendente. Se
  alinean por el superior si los dos tienen ascendente.
- **`rstrip("0")` sobre un entero se come la cifra**: el formateador devolvía
  "4" para 40.0 y "37" para 369.75. Sin punto decimal nada detiene el strip, y
  ningún render lo marca como error.
- **`Create` va con `rate_func=smooth` y un contador va lineal.** Si una
  animación y una cifra cuentan el MISMO dato, van con el mismo ritmo: medido,
  la barra iba por el 16 % del recorrido cuando el número decía 33 %.
- **La cifra que no corresponde a lo que se enseña** es el fallo más repetido:
  relevar el dibujo y después la cifra deja uno o dos segundos con el número
  viejo debajo del dibujo nuevo. Se cambian los dos en el mismo movimiento
  (`L.relevo`); un hueco sin cifra es un estado válido, una cifra falsa no.
- **Un guardián que nunca ha abortado no está demostrado que funcione.** El de
  legibilidad estuvo muerto medio curso (filtraba con `Text.has_points()`, y
  un `Text` de manim no tiene puntos propios: 14 rótulos en la familia, 0
  pasaban). Al arreglarlo empezó a medir GLIFO a glifo y abortaba el molde,
  porque el guion de "WI-FI" mide 0.018 a cuerpo completo. **Pruébalo con un
  caso que TIENE que fallar** antes de creerte que protege algo.
- **Gris significa "dado", no "del fabricante".** La hoja de datos, la
  literatura y los PARÁMETROS elegidos de una simulación (el periodo de un
  bucle, la constante dieléctrica del sustrato) van los tres en gris. El
  acento es sólo lo que sale de medir o calcular en ese render.
