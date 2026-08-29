# Presentaciones — animaciones sueltas para conferencias y tesis

Encargo del **2026-08-28**: además de cursos, promos y verticales, el estudio
tiene que producir **animaciones sueltas que se metan en un PowerPoint**. Se
usan en charlas de divulgación y en defensas de tesis, donde la animación no
se reproduce sola: la acompaña alguien que habla.

---

## Qué es una presentación, y por qué no es ninguna de las otras tres cosas

|  | curso | promo | **presentación** |
|---|---|---|---|
| dura | 28-45 s | 8-15 s | lo que haga falta |
| la narra | el TTS | nadie | **una persona, en vivo** |
| avanza | sola | en bucle | **cuando el ponente hace clic** |
| el fondo lo elige | la marca | la marca | **quien presenta** |
| se entrega como | mp4 / película | mp4 | **un .pptx** |

Las dos últimas filas son las que obligaron a código nuevo.

### Por qué no se llama «pieza»

Fue el primer nombre y se descartó: en este repo **«pieza» ya significa otras
dos cosas**. Es el SEGMENTO de una película montada (`pelicula.py`,
`ensamblar.py`, `audio_promo.py`, `alinear_voz.py`) y es también el nombre de
una plantilla de curso («Pieza de simulación»). Un tercer significado en la
misma app habría sido imposible de leer.

`presentacion` no colisiona con nada, y el artefacto que produce ya tiene su
propio nombre en la interfaz — «El PowerPoint» —, así que el proyecto y su
salida nunca se confunden.

### El fondo: la paleta de marca no sobrevive al blanco

Una plantilla de tesis suele ser blanca, y sobre blanco la paleta del canal
no se lee. Medido con WCAG 2.1:

| color | sobre `#05070a` (marca) | sobre blanco |
|---|---|---|
| `CODE_ACCENT` `#f59e0b` | 9.39:1 | **2.15:1** |
| `CODE_INK` `#e8edf3` | 17.13:1 | **1.18:1** |

El ámbar sobre blanco es ilegible y la tinta es invisible. Por eso
`presentacion.Lienzo` **voltea la paleta** según la luminancia del fondo, en vez de
limitarse a cambiar el color de atrás:

| rol | fondo oscuro | fondo claro | contraste en claro |
|---|---|---|---|
| tinta | `#e8edf3` | `#0f172a` | 17.85:1 |
| apoyo | `#94a0b0` | `#475569` | 7.58:1 |
| acento | `#f59e0b` | `#b45309` | 5.02:1 |

La marca de agua se retiñe con esa misma tinta, y las esquinas HUD (estética
de consola del canal) solo salen en fondo oscuro: sobre blanco se ven como
suciedad.

### El clic: un render, N fragmentos

Es la decisión de diseño de toda la feature.

Una animación de 40 s que corre sola deja al ponente hablando encima de ella.
Lo que sirve en una defensa es que **avance con el clic**. Se consigue así:

1. `presentacion.paso(self, "etiqueta")` deja la escena quieta 0.4 s y anota el
   instante del centro de esa pausa en `pasos.json`.
2. La escena se renderiza **una sola vez**.
3. `ffmpeg` corta ese mp4 en esos instantes.
4. Cada fragmento va en **su propio slide**, con su primer fotograma de póster.

Lo que compra ese orden:

- **Continuidad exacta.** El último fotograma de un fragmento y el primero
  del siguiente caen dentro de la misma pausa. Medido: diferencia media
  **0.22/255**, con **0.035 %** de píxeles por encima de 16 — ruido del
  códec, nada visible. Como el póster del slide siguiente es esa misma
  imagen, el salto de slide no se nota.
- **Un solo render.** Renderizar N veces la escena costaría N veces más en un
  VPS de 2 vCPU y ni así garantizaría el empalme.

La cola posterior al último `paso()` se descarta si dura menos de 0.5 s: es
el `wait` de cortesía con que termina casi toda escena, y un slide de dos
décimas sería un parpadeo en la sala.

---

## Los dos decks, y por qué el defecto es el GIF

`empaquetar_presentacion.py` sabe armar el .pptx de dos maneras. La diferencia es de
**fiabilidad**, no de gusto:

- **GIF (defecto).** PowerPoint arranca un GIF animado solo al entrar al
  slide, en todas las versiones y en las dos plataformas, sin XML de por
  medio. Los GIF se generan **sin repetición** (`-loop -1`): el fragmento se
  reproduce una vez y se queda congelado en su estado final, que es la imagen
  sobre la que el ponente sigue hablando.
- **mp4 (`--video`).** Pesa unas 2 veces menos y no se queda en 256 colores,
  pero que arranque solo depende del árbol `<p:timing>` del OOXML, que la
  herramienta escribe a mano porque `python-pptx` no lo expone. **El archivo
  está verificado; el comportamiento del autoplay hay que verlo una vez en el
  PowerPoint de quien presenta.** Si no arrancara solo, el video ocupa el
  slide entero, así que un clic en cualquier parte lo dispara.

### El difuminado del GIF: apagado a propósito

Con `paletteuse=dither=bayer` una zona de fondo liso salía con **14 colores**
y solo el **25 %** de los píxeles en el blanco exacto. De cerca no se ve, pero
al reescalar —un proyector, una exportación a PDF— ese patrón se alía y
aparecen bandas horizontales sobre el fondo (se vieron en la primera
verificación). Con `dither=none` el **95 %** del fondo queda en un único color
y el GIF además pesa menos. Estas presentaciones son dibujo de línea sobre color
plano, que es justo el caso donde no hace falta difuminar.

---

## Valores medidos (`ventana-de-contacto`, 3 fragmentos, 9.9 s)

| calidad | render | fragmento mp4 | fragmento GIF | deck |
|---|---|---|---|---|
| `ql` | 852×480 @30 | 28-36 KB | 266-368 KB | 954 KB |
| `qh` | 1920×1080 @60 | 77-85 KB | 168-185 KB | **506 KB** |

**El deck de qh pesa la mitad que el de ql.** No es un error: un render limpio
se cuantiza mejor: la paleta de 256 colores mapea más píxeles al mismo valor
cuando la fuente no trae ruido de compresión. Conviene no "ahorrar" bajando la
calidad.

De punta a punta (render + corte + pósters + GIF + deck) en qh: **28 s**.

---

## En la app

Un proyecto de **tipo `presentacion`** con la plantilla «Presentación». Puede
llevar **varias escenas** —una charla suele tener cinco o seis animaciones— y
todas caen en el mismo deck, en el orden de los clips.

    Proyectos → Nuevo → «Presentación»
      · formato: 16:9 · 4:3 (auditorio, plantilla de tesis) · 1:1 (panel)
      · fondo:   marca · blanco · pizarra · o el #rrggbb exacto de tu plantilla
    Renderizar los clips como siempre
    Panel «El PowerPoint» → Armar → descargar el .pptx

El fondo se elige en el proyecto y **viaja con cada job**, igual que el
formato: un reintento produce el mismo archivo que el intento original, y no
un slide de otro color en medio del deck. Los dos quedan bloqueados en cuanto
hay renders vigentes, por la misma razón.

El trabajo está partido en dos a propósito:

- **El contenedor corta** (`cortar_presentacion.py`): es el único sitio con ffmpeg.
- **El backend arma el .pptx**: es el único con `python-pptx`. Meterlo en la
  imagen de manim obligaría a reconstruirla en el VPS.

El informe que cruza esa frontera habla en **rutas relativas al workspace**:
dentro del contenedor la raíz es `/workspace` y fuera es otra, así que una
ruta absoluta del contenedor no existe para quien la lee.

## Cómo se usa desde la consola

    studio/backend/venv/bin/python studio/tools/empaquetar_presentacion.py \
        studio/content/presentaciones/ventana-de-contacto \
        --fondo blanco --calidad qh

    ... --formato horizontal   horizontal 16:9 (defecto) | clasico 4:3 | cuadrado
    ... --fondo blanco         marca (defecto) | blanco | pizarra | #rrggbb
    ... --video                deck de mp4 en vez de GIF
    ... --bucle                los GIF se repiten (presentación de una sola parte)
    ... --escena Nombre        si el archivo tiene más de una

Acepta un directorio con la escena dentro **o un .py suelto**: las ~60
animaciones de `studio/content/animations/` se empaquetan tal cual, sin
tocarlas, eligiendo lienzo y fondo.

Deja en `exports/presentaciones/<slug>/<formato>-<fondo>/`: `completa.mp4`,
`fragmentos/NN.{mp4,gif}`, `posters/NN.png`, `pasos.json`, `scene.py`, el
`.pptx` y un `LEEME.md` con qué hacer en la sala (incluido qué hacer si algo
falla).

### Trampas ya cazadas

- **Rajdhani junta las palabras por debajo de 22 px** (defecto medido en un
  curso ya publicado: "por separado" salió "porseparado"). `presentacion.titulo()` y
  `presentacion.rotulo()` **lanzan un error** por debajo de ese tamaño en vez de
  avisar: proyectado a tres metros, en una defensa, eso lo lee el jurado. El
  guardián cazó un "Horizonte local" a 20 px en la propia escena de ejemplo.
  Para etiquetas chicas está `presentacion.dato()`, que usa Space Mono.
- **`pasos.json` va DENTRO de `media_dir`**, no en su padre: con el montaje de
  la herramienta el padre es `/`, de solo lectura.
- **El fondo se lee del render, no del argumento.** `presentacion.lienzo()` anota en
  `pasos.json` el lienzo que de verdad usó, y el slide se pinta de ese color.
  Importa cuando la escena elige su fondo en el código en vez de heredarlo.
- **`branding.ya_marcado()` reconoce `presentacion`.** Sin eso, el bloque de
  identidad del canal se anexaba a la presentación y le repintaba el fondo de negro.

---

## Estado

| # | Sprint | Qué cierra | Estado |
|---|---|---|---|
| P1 | El lienzo | `presentacion.py`: formatos, fondo, paleta volteada, `paso()` | **hecho** |
| P2 | El paquete | `empaquetar_presentacion.py`: corte, pósters, GIF, .pptx, LEEME | **hecho** |
| P3 | La app | tipo `presentacion` en el estudio, con su pantalla | **hecho** |
| P4 | La biblioteca | "abrir como presentación" en las animaciones que ya existen | **hecho** |

### Lo que entró en P3

`projects.py` (tipo + 4:3 + fondos con validación) · `db.py` (columna `fondo`
en `projects` y en `jobs`) · `manim_runner.py` (`PRESENTACION_FONDO`, formato
`clasico`, comando `presentacion`) · `cortar_presentacion.py` · `presentaciones.py` +
`presentaciones_api.py` · `PresentacionPanel.jsx` · plantilla y selector de fondo en el
frontend. `python-pptx` está en `backend/requirements.txt`: **hay que
instalarlo en el VPS al desplegar**.

### P4 — reutilizar las ~60 animaciones que ya existen

En la Biblioteca, cualquier animación tiene un botón **«Como presentación»**:
crea el proyecto, mete el script y te lleva allí. No hay que rehacer nada.

Lo que había que resolver de verdad no era el trámite. Ninguna de esas
animaciones llama a `presentacion.lienzo()` —se escribieron para un curso—,
así que **el formato y el fondo elegidos se ignoraban en silencio**: se pedía
4:3 sobre blanco y salía 16:9 sobre negro, sin un aviso. Un flag que no hace
nada es peor que no ofrecerlo.

La solución es simétrica a la identidad de marca: el backend **garantiza el
lienzo** igual que garantiza la marca. `branding.aplicar(script, tipo)` anexa
`presentacion.adaptar_escenas(globals())` a cualquier script de un proyecto de
tipo presentación que no pida su propio lienzo. Los dos bloques son
excluyentes — el de presentación ya aplica identidad, con la paleta volteada.

Así el diálogo no tiene que recortarle la cabecera al script ni anteponerle un
bloque de estilo (`import sys` + `from manim import *` volverían a importar el
`Scene` real y se cargarían la sombra): el estilo compartido va **vacío** y el
script entra tal cual.

`adaptar_escenas` además **inyecta los nombres** `presentacion`, `paso` y
`PRES` en el script (con `setdefault`, sin pisar nunca los del autor). Sin
eso, el consejo que da el diálogo —«añade `presentacion.paso(self, "...")`
donde quieras cada parada»— fallaría con `NameError`, porque esa animación
nunca importó el módulo. Verificado: las dos formas producen dos slides.

**Lo que NO hace, y por eso el diálogo lo dice**: no repinta los colores. Pone
el lienzo, el fondo y la marca; los colores que la animación eligió a mano no
se pueden adivinar. Por eso el fondo por defecto al adaptar es el de **marca**
—aquel para el que se dibujó— y elegir uno claro sale con aviso: sobre blanco,
un diagrama de curso queda lavado (comprobado a ojo, no supuesto).

### Las tres trampas que solo aparecieron con la app entera montada

Ninguna se ve en las pruebas unitarias; las tres salieron de una corrida real
crear → renderizar → armar → descargar.

1. **`render_jobs/` y `exports/` son enlaces a otro disco** en esta máquina
   (`studio/docs/ARTEFACTOS-LOCALES.md`). Eso rompe dos cosas: `Path.resolve()`
   manda la ruta fuera del workspace y `relative_to` la rechaza, y dentro del
   contenedor el enlace apunta a un destino que no está montado. Por eso
   `PresentacionService._rel` compara **sin resolver** primero, y `handle_presentacion`
   monta `render_jobs` explícitamente de solo lectura.
2. **El informe del cortador viajaba en rutas absolutas del contenedor.** El
   backend las abría contra su propio sistema de archivos: `No such file or
   directory: /workspace/exports/...`. Ahora van relativas al workspace.
3. **Un armado que fallaba no decía por qué.** El error vivía en `_run`, que
   solo era visible mientras la tarea corría: al terminar, el panel volvía a
   «sin armar» sin explicación. Ahora una corrida que acabó en error sigue
   visible hasta el siguiente intento; una que salió bien sí desaparece.

### El mismo defecto estaba en la película, y en `unir_vertical.py`

**Montar una película estaba roto en este clon** desde la migración de
artefactos al segundo disco, por los dos primeros motivos de arriba:
`pelicula.py::_rel` resolvía el enlace y la ruta salía del workspace, y
`handle_ensamblar` no montaba `render_jobs` en el contenedor. `unir_vertical.py`
tenía el mismo fallo en su camino de respaldo (el que reintenta la mezcla
dentro del contenedor cuando el numpy del host no sirve).

Los tres arreglados. La regla vive ahora en un solo sitio,
`backend/app/rutas.py::relativa_al_workspace`, con el porqué escrito; el
montaje de los renders, en `manim_runner.py::montaje_render_jobs`. Dos pruebas
lo fijan: `test_pelicula.py` comprueba que un `render_jobs/` enlazado sigue
dentro del workspace y que **los dos** comandos que leen renders lo montan.
