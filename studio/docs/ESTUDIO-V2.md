# ManimStudio v2 — de consola de render a estudio de video

Encargo del **2026-08-27** (corrida nocturna automática): mejorar la plataforma —
efectos de sonido, animaciones, transiciones, formas de uso— hasta convertirla en
un **estudio de video completo**, con todo lo nuevo consolidado en `main` y todo
documentado.

Este archivo es el tablero vivo. El diseño visual sigue en `DESIGN-SYSTEM.md` y el
rediseño de UI cerrado en `UX-REDISENO.md`.

---

## De qué se parte (auditoría del 2026-08-27)

ManimStudio ya sabe: renderizar escenas en un sandbox, agrupar clips en proyectos
con estilo compartido, narrarlos con TTS, sonorizar **promos**, verificarlos y
empaquetar un ZIP.

Lo que le falta para ser un estudio, en orden de cuánto duele:

1. **No monta la película.** Unir los clips de un curso en un solo archivo se hace
   *fuera*: descargar el ZIP, `unzip`, `ffmpeg -f concat`. La app produce piezas,
   no obras. Es el hueco más grande.
2. **No hay transiciones entre clips.** El único empalme posible es el corte seco
   del `concat -c copy`. `transiciones.py` (61 líneas) resuelve transiciones
   *dentro* de una escena, y nadie las conoce: no salen en ninguna pantalla.
3. **El sonido es solo de promos.** El manifiesto de cama sonora (`audio_json`)
   está cerrado con 409 a los proyectos `tipo='curso'`. Un curso solo puede tener
   voz. Y los 12 efectos de `sfx.py` no se pueden **oír** antes de usarlos: se
   eligen a ciegas en un desplegable.
4. **La marca sonora se pega a mano.** El intro/cierre de CO.DE Academy con su
   SFX vive en herramientas de línea de comandos y en la memoria del operador.
5. **Formas de uso.** Un solo atajo en toda la app (`Ctrl+Enter` para renderizar).
   Reordenar un clip son dos clics por posición. No hay forma de llegar a un curso
   por su nombre sin navegar.

---

## Tablero

| # | Sprint | Qué cierra | Estado |
|---|---|---|---|
| E0 | Consolidación de ramas | todo lo nuevo, en `main` | **hecho** (PR #61) |
| E1 | La película | monta el curso completo dentro de la app | **hecho** |
| E2 | Transiciones | empalmes reales entre clips + catálogo en escena | **hecho** |
| E3 | Sonido de cursos | cama de SFX en cursos + banco audible | **hecho** |
| E4 | Formas de uso | paleta de comandos, atajos, arrastrar clips | **hecho** |
| E5 | La regleta | ver la película montada dentro de la app | **hecho** |
| E6 | Medir la película | la unión puede salir mal sin fallar | **hecho** |

---

## E0 — Consolidación (hecho, PR #61)

Auditoría de las 40 ramas del repo. Tres cosas vivían fuera de `main`:

- La skill `curso-de-video` con el **formato mudo** del curso 27 y el guardián que
  aborta el render si aparece prosa en pantalla — **no estaba en ninguna rama**,
  solo como archivos sin commitear en el checkout principal.
- Los dos **cursos verticales** (26 Fractales, terminado; 28 Satélites, en
  producción) y las cuatro herramientas del formato 9:16.
- El **entorno de desarrollo local** (`studio/dev.sh`, runner parametrizable).

Nueve ramas resultaron obsoletas (su contenido ya estaba en `main` por otra vía):
`curso/agentes-de-ia`, `curso/apuntado`, `curso/control`, `curso/espectro`,
`curso/materiales`, `curso/redes-neuronales`, `curso/sdr`,
`curso/protocolos-internet` y `fix/mux-locale`. Se pueden borrar sin pérdida.

---

## E1 — La película (hecho)

**Lo que cierra**: ManimStudio deja de producir solo piezas. Un curso entero
—clips en orden, su narración pegada, la marca de CO.DE Academy al principio y
al final— sale como **un archivo**, montado dentro de la app.

Antes: `GET /api/projects/{pid}/archive` → zip → `unzip` → `sh mux.sh` en la
máquina del operador. Funcionaba, pero la app no sabía lo que había producido.

### Quién hace qué

```
Proyectos ─POST /api/projects/{pid}/pelicula──▶ PeliculaService
                                                  escribe exports/peliculas/<pid>/plan.json
                                                  ▼ runner.ensamblar(project_id)
                                              manim-runner  (cmd "ensamblar")
                                                  ▼ docker compose run  (mount rw solo de ese dir)
                                              studio/tools/ensamblar.py
                                                  ▼
                                              exports/peliculas/<pid>/pelicula.mp4 + pelicula.json
```

Del exterior al runner solo llega un **`project_id` validado con regex**, igual
que en `postproceso` y `verificar`. El plan (qué clips, en qué orden, con qué
voz y qué empalme) lo escribe el backend; sus rutas apuntan dentro de
`/workspace`, que el contenedor ve **read-only**. Lo único montado con
escritura es `exports/peliculas/<project_id>/`.

### El empalme: dos caminos con costes de otro orden

| Empalme | Cómo | Coste |
|---|---|---|
| `corte` (por defecto) | `concat -c copy` | **segundos** — el vídeo se copia, no se toca |
| `fundido`, `negro`, `blanco`, `deslizar`, `barrido`, `disolver` | `xfade` + `acrossfade` | **recodifica la película entera**; en el VPS (1,5 vCPU) un curso de media hora tarda decenas de minutos |

La interfaz lo dice antes de montar, no después de esperar. Por eso el defecto
es el corte, que es también lo que la colección viene usando.

**El offset de cada `xfade` se calcula sobre lo acumulado, no sobre la suma de
duraciones.** Cada empalme acorta el resultado en `d`; usando la suma cruda, los
cortes se desplazan cada vez más y el último cae fuera del vídeo — ffmpeg lo
pega **sin fundir y sin fallar**. Hay un test que fija los dos offsets de una
película de tres piezas.

### La voz: la misma lógica que `mux.sh`, portada línea a línea

Si la voz cabe, `apad` + `-shortest` (cada clip conserva su duración exacta y el
concat no se desincroniza). Si no cabe, `atempo` con el ratio justo y **tope
1.15** — más allá se nota. El vídeo se **copia siempre** en este paso (`-c:v
copy`): sonorizar un curso de 30 clips cuesta segundos.

Una pieza sin narración igual recibe **pista de silencio**: un `concat` que
mezcla clips con y sin audio sale mudo a partir del primero sin pista, y no
falla al hacerlo.

### La marca

El intro y el cierre son dos renders más del proyecto «Marca…» del catálogo, y
entran como piezas al principio y al final. Se valida que su **resolución medida
coincida** con la del curso: un intro vertical en un curso horizontal ni se pega
con `concat -c copy` ni sale bien por `xfade`.

### Cuándo caduca

`pelicula.json` guarda el hash del plan: nombre, resolución, fps, empalme y el
**mtime de cada archivo** (vídeo y voz). Un re-render deja la misma ruta con
otro contenido — por eso el mtime y no solo el nombre. Cambiar el empalme
también la caduca. Estados: `sin_clips`, `faltan_renders`, `sin_montar`,
`desactualizada`, `al_dia`, `montando`.

### API

| Método | Ruta | Notas |
|---|---|---|
| GET | `/api/projects/{pid}/pelicula` | estado, opciones, piezas, informe medido |
| POST | `/api/projects/{pid}/pelicula` | monta en segundo plano (202); 409 si no hay material o ya hay un montaje |
| POST | `/api/projects/{pid}/pelicula/cancel` | corta el montaje en curso |
| GET | `/api/projects/{pid}/pelicula/video` | el mp4, con soporte de Range |
| DELETE | `/api/projects/{pid}/pelicula` | borra la película (no el material) |

### Operación

`exports/` entra en `ReadWritePaths` de la unidad del backend (junto con
`guiones/`, que ya lo necesitaba y **no estaba en la copia del repo**: deriva
entre el unit desplegado y el versionado). `exports/peliculas/` debe ser del
usuario `manimstudio`: el contenedor de montaje corre con ese uid y `cap_drop:
ALL` le quita a root el `CAP_DAC_OVERRIDE` que le dejaría escribir en un
directorio ajeno — verificado en la imagen real, donde el montaje falla con
*Permission denied* si el uid no coincide.

### Verificación

- 19 tests nuevos (`tests/test_pelicula.py`), 209 en total, en verde.
- Montaje real **dentro de la imagen `codeaerospace_contenido-manim`**: dos
  piezas (una con voz) con `corte` → 5,54 s, y con `fundido` de 0,5 s → 5,17 s
  sobre 3,0 + 2,5. Tres piezas con `negro` de 0,5 s → 8,50 s exactos.

---

## E2 — Transiciones (hecho)

Dos capas distintas, y conviene no confundirlas:

- **Entre clips** (E1): las hace ffmpeg al montar la película. Son empalmes de
  archivos.
- **Dentro de una escena** (esto): las hace Manim entre dos bloques de
  contenido de un mismo clip. `transiciones.py` pasa de **3 funciones a 10**.

### Por qué importaba

Manim no trae transiciones entre bloques: lo único disponible es
`FadeOut(viejo)` + `FadeIn(nuevo)`. En un clip de 40 segundos eso parpadea diez
veces, siempre igual. Y las tres que ya existían **no salían en ninguna
pantalla**: había que leer el archivo para saber que estaban.

### Las diez

| Nombre | Qué hace | Cuándo |
|---|---|---|
| `deslizar` | el viejo sale, el nuevo entra por el lado opuesto | dos momentos del mismo tema |
| `empujar` | el nuevo empuja al viejo fuera del cuadro | igual, pero se nota |
| `zoom` | el viejo atraviesa la cámara, el nuevo emerge del fondo | entrar en un detalle |
| `barrido` | una **banda ámbar** cruza el cuadro | cambio de sección (es la marca) |
| `fundido_negro` | todo va a `CODE_BG` y vuelve | cambio de **tema** |
| `persiana` | franjas horizontales tapan y se retiran | textura |
| `rejilla` | celdas que se cierran en diagonal | textura, aire de pantalla de control |
| `difuminar` | el viejo se deshace, el nuevo se recompone | ruido, pérdida, olvido |
| `conmutar` | `Transform` de verdad | el mismo objeto en otro estado |
| `trazar` | `Uncreate` + `Create` | diagramas y ejes, donde el trazo cuenta |

`transicion(nombre, saliente, entrante, **kw)` despacha por nombre y levanta
`KeyError` **con el catálogo** si el nombre no existe: un typo no debe fallar a
mitad de render.

### La trampa que costó encontrar

`mobject.animate.shift(v)` **copia el mobject en el momento en que se construye
la animación**, no cuando se reproduce. En una `Succession` las tres partes se
construyen antes de que se reproduzca ninguna, así que dos `.animate.shift()`
seguidos calculan su destino desde la **misma** posición inicial: la banda del
barrido entraba al centro y se quedaba ahí, tapando la escena. La solución es
usar destinos **absolutos** (`move_to`, `scale_to_fit_height`, `set_opacity`),
que dan el mismo resultado sin importar cuándo se tomó la copia. Afecta a
`barrido` y a `rejilla`.

(`persiana` se quedó **byte a byte** como estaba: lleva 27 cursos en producción
y su segundo `stretch` relativo acaba en 1e-6 en vez de 1e-3 — invisible
igual. No se toca lo que ya salió al aire.)

### Cómo se ven

`animations/experimentacion/29-transiciones.py` las enseña **las diez seguidas**
sobre el mismo par de bloques, cada una con su nombre y su línea de
`DESCRIPCIONES`. Aparece sola en la pestaña Aprender. Renderizada y verificada
en la imagen real: 42 animaciones, 17,6 s, y ninguna transición deja nada
tapando la pantalla al terminar.

El asistente IA las tiene en `conocimiento.py` como regla, con el cuándo-usar-
cuál y el aviso de que `conmutar` deja convertido el objeto **saliente**.

### Verificación

Tres tests de deriva (`tests/test_transiciones.py`, por AST porque la librería
importa manim): cada entrada del catálogo apunta a una función que existe, cada
una tiene descripción, y el demo las enseña todas sin repetir ninguna.

---

## E3 — Sonido de cursos (hecho)

El sonido de ManimStudio estaba encerrado en los promos: los tres endpoints de
`audio` respondían **409** en cualquier proyecto `tipo='curso'`. Un curso solo
podía tener voz. Y los 18 efectos de `sfx.py` se elegían **a ciegas**, de un
desplegable de nombres, sin forma de oírlos antes.

### 1. La cama llega a los cursos, sin traerse la voz

Un clip de curso ahora puede llevar cama de sonido — un acento en el momento
que importa, un pad que sostiene una escena larga — con **una regla que manda
sobre todo lo demás: aquí no hay voz**. La narración de un curso la escribe
Gemini y la sintetiza «Generar narración»; la película la pega al montar.

Un manifiesto de curso con frases es un **error (422)**, no un aviso: aceptarlo
en silencio pegaría dos voces sobre el mismo clip, y después no se separan.

Lo que cambia por tipo:

| | promo | curso |
|---|---|---|
| voz en el manifiesto | sí | **no** (422) |
| pico por defecto de la cama | −3 dB | **−16 dB** (nace bajo la voz) |
| avisos | bucle, frases que se empujan, cola de silencio | cama que compite con la voz, sonidos fuera del clip |
| verificación | sí | **409** — mide la costura del bucle y 8-15 s, que en un curso no existen |

### 2. La película mezcla, no reemplaza

Dos cambios que solo se ven juntos:

- El plan usa **el mp4 que la app sirve** (`audio_path` si existe, el mudo si
  no). Montar con el mudo daría un curso que suena distinto a sus propios clips
  en la Biblioteca.
- `ensamblar.py` detecta si la pieza ya trae pista (`tiene_audio`) y, cuando
  además hay narración, las **mezcla** (`amix=inputs=2:normalize=0`). Mapear
  solo la voz tiraba la cama por la borda **sin que nada fallara**.

El nivel de la cama no se toca al mezclar: es el que se eligió en la interfaz.
Una ganancia escondida haría que lo que se oye no fuera lo que se puso.

Verificado midiendo: una pieza con cama a 440 Hz y voz a 880 Hz sale con
**ambas** bandas a ≈ −21 dB y una banda de control a 1500 Hz en −53,7 dB.

### 3. El banco de sonidos se puede oír

`sfx.py paleta` sintetiza los 18 efectos como wavs sueltos en `exports/sfx/`,
lanzado por el nuevo comando `paleta` del runner (el backend no tiene numpy).
La síntesis es determinista: se generan una vez y no caducan.

- `GET /api/sfx` — la paleta, cuáles están listos y si está completa.
- `POST /api/sfx` — sintetiza (409 si ya se está sintetizando).
- `GET /api/sfx/{nombre}` — el wav. El nombre va contra el **conjunto cerrado**
  de la paleta antes de construir ninguna ruta.

En el diálogo de audio, cada línea tiene un ▶ que reproduce su efecto, y un
solo `<audio>` para todo el diálogo: dos efectos a la vez no se distinguen.

**Hallazgo**: `exports/sfx/` sobrevive a los cambios de `PALETA`. Una corrida
vieja dejó `pad_intro.wav` y `pad_cierre.wav`, efectos que ya no existen.
Enumerar el directorio sin filtrar ofrecería en la interfaz sonidos que la
mezcla no sabe sintetizar — el listado los cruza con la paleta viva.

### Verificación

223 tests en verde (10 nuevos), el banco sintetizado de verdad en el contenedor
(18 efectos) y la mezcla medida banda a banda.

---

## E4 — Formas de uso (hecho)

La consola tenía **un** atajo en toda la app (`Ctrl+Enter` para renderizar) y no
estaba escrito en ninguna parte salvo el `title` de un botón. Y con ~80 cursos
en catálogo, llegar a «Álgebra lineal · 4.2 Diagonalizar» eran cuatro gestos:
Proyectos → desplegar la familia → buscar la lección → abrirla.

### Paleta de comandos (`Ctrl+K` / `⌘K`)

Escribir para ir a cualquier sitio. **No pide nada al servidor**: las fuentes
son el store compartido del catálogo (`catalogo.js`) y la tabla de vistas del
router, así que se abre instantánea.

Se **puntúa**, no se filtra: todas las palabras de la consulta tienen que
aparecer, en cualquier orden, y las que empiezan palabra puntúan mejor.
Escribir `alg 42` encuentra «Álgebra lineal · 4.2 Diagonalizar y las
potencias» — la comparación ignora tildes y, cuando una palabra no aparece tal
cual, se reintenta contra el texto **compactado** (sin puntuación), que es lo
que hace que `42` encuentre `4.2`. Nadie teclea el punto.

La familia va **delante** del título, no en la columna derecha: «1.1 El vector»
existe en Álgebra lineal y en Cálculo vectorial, y sin la familia las dos filas
son la misma. (Se vio en la primera captura de QA, no en el código.)

### Atajos

Una sola tabla (`ATAJOS` en `components/Atajos.jsx`) es a la vez la
implementación y la hoja de ayuda (`?`): no pueden separarse.

`Ctrl+K` la paleta · `g p/e/r/a/d/c` ir a cada sección (acorde de 1,2 s, como
GitHub) · `Ctrl+Enter` renderizar · `?` la hoja.

Dos reglas que evitan los errores clásicos de un atajo global:

- **Nada se dispara mientras se escribe** — input, textarea, `contenteditable`
  o el editor CodeMirror. Sin esto, teclear «gp» en el título de un clip te
  saca a Proyectos.
- **`Ctrl+K` sí funciona siempre**, incluso dentro del editor: es el atajo para
  *salir* de donde estás, y exigir soltar el foco primero lo haría inútil.

### Reordenar clips arrastrando

Mover un clip del final al principio eran seis clics de flecha. Ahora se
arrastra por el asa.

**Quien es `draggable` es el asa, no la tarjeta**: dentro de la tarjeta hay
inputs y un textarea, y un contenedor arrastrable se pelea con la selección de
texto. La tarjeta solo hace de destino, y se le pasa como imagen de arrastre
(`setDragImage`) para que lo que viaja se vea.

**Qué se arrastra vive en un `ref`, no en el estado.** El estado de React se
aplica en el siguiente render, y `dragstart` y `drop` pueden ocurrir sin que
haya habido uno en medio: entonces el `drop` leía `null` y el clip no se movía.
El estado se queda solo para atenuar la tarjeta que viaja, donde llegar un
render tarde no rompe nada. **Este bug lo encontró el QA, no la lectura.**

### Verificación

Arnés Playwright contra la app construida, con backend local y catálogo
sembrado (no se commitea; vive en el scratchpad). Ocho comprobaciones en verde:

- `Ctrl+K` abre la paleta; `alg 42` la resuelve a «4.2 Diagonalizar»; `↵` abre
  el curso (`#/proyectos/<id>`).
- `?` abre la hoja; `g r` va a Renders.
- Teclear «gp» **dentro del editor** no navega; `Ctrl+K` **sí** funciona ahí.
- Arrastrar el tercer clip sobre el primero deja `Tres, Uno, Dos`.

Nota del arnés: Playwright headless no arranca el *drag and drop nativo* de
Chromium; el reordenamiento se comprueba despachando los eventos de arrastre a
mano, que es lo que prueba los manejadores y su cableado.

---

## E5 — La regleta y el reproductor (hecho)

E1 dejó la película montada, pero para verla había que descargarla, y la lista
de clips no decía nada de cómo se reparte el tiempo. El panel «La película»
ahora enseña **la obra**, no solo su botón.

### La regleta

Un segmento por pieza, ancho proporcional a su duración. Ámbar la marca, tinta
las que llevan voz, apagado las mudas. Debajo, el total **descontando lo que se
comen los empalmes** (cada `xfade` recorta su duración del resultado).

Antes de montar se dibuja con las duraciones que la narración ya midió de cada
clip; después, con las **medidas del informe**, que son la verdad. Hacer clic en
un tramo salta a ese punto del reproductor.

### El reproductor

El curso montado se ve en el propio panel (`<video>` con soporte de Range del
backend), con la altura acotada: sin tope, un 1080p ocupaba la pantalla entera y
empujaba fuera el informe medido.

### Nota de formato

Por debajo del minuto la duración lleva un decimal: en una pieza de 8,7 s,
redondear a «9 s» borra justo lo que se está mirando.

### Verificación de punta a punta

Esta vez con el **runner real** (no solo el contenedor a mano): backend y
`manim_runner.py` locales contra el workspace del repo, tres clips sembrados de
3,0 / 4,0 / 2,5 s y `POST /api/projects/{pid}/pelicula` con `fundido` de 0,5 s.

- El runner registra `[pelicula] pid=… ok piezas=3 dur=8.667`.
- `exports/peliculas/<pid>/` queda con `plan.json`, `pelicula.mp4` y
  `pelicula.json`; el estado pasa a `al_dia`.
- `GET …/pelicula/video` sirve los 378 620 bytes y `ffprobe` mide **8,667 s**
  sobre los 8,5 previstos (la diferencia es el re-encode a los 15 fps del
  proyecto desde fuentes de 30).
- La interfaz enseña la regleta, el reproductor con la película dentro y el
  informe medido (duración, resolución, tamaño, empalme).

De paso quedó comprobado el arranque del runner en **modo desarrollo** (el que
entró en la consolidación E0): sin grupo `manimstudio` ni root para el `chown`,
deja el socket a 0600 y avisa, en vez de caerse.


---

## E6 — Medir la película (hecho)

La unión puede salir mal **sin fallar**: un offset de `xfade` que deja la última
pieza fuera produce un mp4 perfectamente formado y más corto; un `concat` que
mezcla clips con y sin pista de audio produce uno que enmudece a partir del
tercero. En los dos casos ffmpeg sale con 0 y el archivo se abre. Nadie lo ve
mirando el vídeo una vez.

`ensamblar.py` gana un segundo verbo — `ensamblar.py verificar <plan> <mp4>` —
que mide la película **contra el plan del que salió**. Tres comprobaciones,
todas objetivas:

| Qué | Cómo | Qué caza |
|---|---|---|
| **Duración** | medida vs. suma de piezas − empalmes, con **±0,5 s** de tolerancia | material perdido o duplicado |
| **Sonido, pieza a pieza** | `volumedetect` sobre cada tramo de la película montada | el `concat` que enmudece a mitad — un pico global sano convive con media película muda |
| **Resolución** | medida vs. la del proyecto | material de otro tamaño colado en el curso |

Tres decisiones que evitan que la medición se vuelva ruido:

- **Solo se acusa a las piezas que traían sonido.** Un curso sin narrar es mudo
  a propósito; marcarlo en rojo cada vez enseña a ignorar el aviso.
- **La tolerancia no es cero.** El re-encode cuadra a frames enteros y a los fps
  del proyecto: exigir la duración exacta marcaría como rota una película sana.
- **La decisión es una función pura** (`diagnostico`), aparte de la medición: lo
  que dice si una película está bien tiene que poder probarse sin montar nada.

**Se mide sola al terminar de montar** — recién montada es cuando el informe
anterior deja de valer — y el resultado vive dentro de `pelicula.json` con el
**mismo hash** que el montaje, así que caduca solo: volver a montar deja la
medición en «vieja» en vez de enseñar números de otra película.

`POST /api/projects/{pid}/pelicula/verificar` la repite a mano.

### Verificación (de la verificación)

De punta a punta con el runner real, montando tres clips con `corte`:

```
[pelicula] pid=… montar    ok=True  piezas=3 dur=9.529
[pelicula] pid=… verificar ok=False piezas=3
```

La medición automática saltó sola y **cazó algo de verdad**: «la película es
640x360 y el curso es 854x480» — los clips de prueba se habían sembrado a otra
resolución que la `ql` del proyecto. La duración (9,529 sobre 9,5 previstos)
entró en tolerancia y las tres piezas mudas **no** se acusaron, que es
exactamente lo que se buscaba.

Además, 12 tests nuevos sobre la función pura y sobre la caducidad del informe.

---

## Despliegue (hecho: 2026-08-28)

Desplegado y verificado en `https://coderesearch.space`. Estos son los pasos que
se ejecutaron; los dos últimos son **nuevos** respecto al despliegue de siempre.

```bash
ssh root@187.124.55.225
cd /var/www/codeaerospace_contenido && git pull --ff-only

# Frontend: el build ES el despliegue (nginx sirve dist/ del disco).
export PATH="$HOME/.nvm/versions/node/v24.15.0/bin:$PATH"   # node no está en el PATH de una sesión no interactiva
cd studio/frontend && node_modules/.bin/vite build

# NUEVO 1 — el directorio de las películas, del usuario que monta. El contenedor
# corre con el uid de `manimstudio` y `cap_drop: ALL` le quita a root el
# CAP_DAC_OVERRIDE: si el directorio es de otro, el montaje falla con
# "Permission denied" y nada más lo explica.
install -d -o manimstudio -g manimstudio exports/peliculas exports/sfx

# NUEVO 2 — ReadWritePaths con `exports`
cp studio/deploy/manimstudio-backend.service /etc/systemd/system/
systemctl daemon-reload

systemctl restart manimstudio-backend manimstudio-runner
```

Dos cosas que aparecieron al desplegar y conviene recordar:

- El `git pull` **abortó** por un `studio/tools/alinear_voz.py` sin commitear en
  el VPS (copiado a mano durante la producción de los cursos verticales). Era
  **byte a byte igual** al que entraba: se comprobó antes de borrarlo.
- La deriva del unit era **al revés de lo que parecía**: el desplegado ya tenía
  `guiones` y el del repo no. Ahora los dos tienen `guiones` y `exports`.

### Verificación en producción

- El runner arrancó por la ruta de siempre —`escuchando en
  /run/manimstudio/runner.sock (grupo manimstudio)`—, así que la
  parametrización del sprint E0 no cambió nada en el VPS.
- **Banco de sonidos**: `POST /api/sfx` sintetizó los **18 efectos en 3,4 s**.
- **Película de un curso real** («Procesamiento de señales · 9.1 Estimar el
  espectro», 4 clips narrados), montada con `corte` en **~8 s**:

  ```
  [pelicula] pid=9077c6e93ba94c52 montar    ok=True piezas=4 dur=115.244
  [pelicula] pid=9077c6e93ba94c52 verificar ok=True piezas=4
  ```

  1 min 55 s · 1920×1080 · 7,7 MB. Dos de las cuatro voces no cabían y se
  ajustaron con `atempo` **1.0497** — la lógica de `mux.sh`, funcionando.
- **La medición automática pasó**: +0,36 s sobre lo previsto (tolerancia ±0,5) y
  las cuatro piezas con su sonido, entre **−0,6 y −1,4 dBFS**. Ninguna lo perdió
  en la unión.
- **Entrega**: `GET …/pelicula/video` devuelve 200 con los 8 038 407 bytes en
  0,26 s, y **206 con 100 000 bytes exactos** ante un `Range` — se puede saltar
  dentro de una película de dos horas sin descargarla.
- **Interfaz**, con sesión firmada contra el sitio real: la paleta resuelve
  «senales 91» → «Procesamiento de señales · 9.1», y el panel enseña «al día»,
  la regleta, el reproductor con la película dentro y la línea de la medición.
