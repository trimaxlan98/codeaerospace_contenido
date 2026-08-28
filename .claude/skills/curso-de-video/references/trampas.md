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

## Animación

- **`Transform` solo entre gemelas de estructura IDÉNTICA.** Distinta
  estructura = glifos rotos. Toda pieza que cambia necesita su gemela `con_*`.
  Casos que rompen la gemelidad sin que se note: una pieza que nace **sin
  valores** (textos de 0 glifos), un número de filas distinto (reservar con
  `filas_max` y rellenar con guiones), un resaltado que añade un `Rectangle`
  solo en una de las dos (reservarlo con un flag opt-in).
- Un `Transform` de cifras dentro de una animación larga deja dígitos a medio
  morfar: `Succession(Transform corto, Wait)`, y ancho fijo (`03d`) en los
  contadores.
- `set_opacity` **enciende el fill** (no solo el trazo). `Indicate` va sobre
  la versión `_con_fondo`.
- `.animate` re-sube el VGroup al frente: cuidado con el orden z.
- `interpolate_color` exige `ManimColor`; las constantes `C_*` de las familias
  son `str`.
- Las etiquetas de `Grafica` son hijos internos: no aparecen si se animan
  `.ejes` / `.curva` por separado.
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
  morfar: `Succession(Wait(0.55), Transform(cont, nuevo, run_time=0.02))`, en
  ese orden y con el Transform corto.
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
