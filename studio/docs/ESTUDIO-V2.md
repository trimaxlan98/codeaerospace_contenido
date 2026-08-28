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
| E3 | Sonido de cursos | cama de SFX en cursos + banco audible | pendiente |
| E4 | Formas de uso | paleta de comandos, atajos, arrastrar clips | pendiente |
| E5 | Movimiento | transiciones de vista y micro-animaciones en la consola | pendiente |

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
