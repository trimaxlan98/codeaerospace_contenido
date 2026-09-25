# Curso 37 — Rendimiento de SQL Server (familia «Rendimiento SQL»)

## Cómo reanudar

- Worktree `~/Documentos/github/codeaerospace_contenido-sql`, rama `curso/optimiza-sql`.
- Tablero de estado: §12 de este archivo. Librería: `studio/content/manim_extensions/sqlperf.py`, sonda `studio/tools/sonda_sqlperf.py` (0 fallos).
- El dueño reanuda con: «continuamos con el curso de SQL».
- Fuente del temario: repo `~/Documentos/github/optimiza-sql` (material de un curso presencial del dueño). **Solo se usa el contenido técnico**; ver §4.

## 1. Encargo (2026-09-24)

«Revisa github/optimiza-sql para de ahí desarrollar un curso completo de CO.DE Academy en horizontal para subir a YouTube; elimina el tener que poner "Modulo XX" en cada momento del curso mientras sale la explicación [...]. Lo vas a hacer diseñando, evaluando y arquitectando tú, después mandas agentes Sonnet que vayan desarrollando el curso y repites el ciclo hasta que quede.»

Aclaraciones del dueño, mismo día:
- El «ruido visual» que hay que quitar ES la etiqueta «Modulo 0N» de la esquina superior izquierda. **No** se añade grano ni efecto de imagen.
- 21 lecciones / 84 clips.
- «En YouTube será para un público más general que no necesariamente tomó el curso que di: que todos entiendan, **nada de referencias específicas al curso**.»

## 2. Formato

- Familia horizontal 16:9, estilo **CONSOLA**, 7 módulos × 3 lecciones = **21 proyectos, 84 clips**.
- Nombre `Rendimiento SQL · N.M <Título>` (clave de `subir_curso.py`: no cambiar después de subir). Slug `rendimiento-sql-N-M-<tema>`.
- **Narrado sin subtítulos** (formato mudo, como los cursos 27–36). La voz se escribe después, con `guiones.py`.
- **SIN «Modulo 0N»**. `hud_modulo()` existe en el `style_block` solo para ABORTAR si alguien la llama. Lo único fijo en pantalla es la marca de agua y las escuadras de la marca.

Lo que puede haber en pantalla (el guardián `_vigilar()` aborta el render si un rótulo se vuelve frase):

| Elemento | Helper | Límite |
|---|---|---|
| Título del clip (arriba) | `titulo_curso()` | ≤ 6 palabras |
| Rótulo de mobiliario | `tag_junto()` | ≤ 4 palabras |
| Cifra calculada aquí (cian) | `cifra_pie()` / `tag_hud()` | ≤ 5 palabras |
| **Lectura medida en el motor (ámbar)** | `motor_pie()` / `tag_motor()` | ≤ 5 palabras |
| Dato público (gris) | `dato_pie()` | ≤ 5 palabras |
| Código T-SQL | `S.codigo([...])` | ≤ 5 líneas × 46 caracteres, ASCII |
| Fórmula | `formula_pie()` | una línea |
| Cierre del clip 4 | `cierre_leccion()` | 2 líneas |

## 3. Ángulo editorial

**Una consulta no se paga en segundos: se paga en páginas.** Todo el curso mide lo mismo —cuántas páginas de 8 KB lee el motor— y cada técnica se cuenta como una manera de leer menos. El arco va de «¿por qué esta consulta tarda?» (1.1) a «la tienda pasó de 53 s a 3.9 s» (7.3).

El ejemplo que atraviesa el curso es **una tienda en línea** con 200 mil clientes, 1.5 millones de pedidos y 3.75 millones de renglones de detalle, con sus problemas de fábrica: sin índices en las llaves foráneas, un mayorista con el 10 % de todos los pedidos, un correo guardado como VARCHAR y buscado como NVARCHAR, casi todos los pedidos «entregados».

## 4. Público y qué asume

Público general de YouTube: sabe qué es una tabla y ha escrito un `SELECT ... WHERE`. **No** asume que tomó ningún curso. Por eso:

- **Prohibido**: «sesión», «demo 03», «el script 00», «laboratorio», «la laptop del curso», «como vimos en clase», «TiendaPerf» en pantalla, horarios, nombres de alumnos. La base es «la tienda» o «pedidos», nada más.
- Cada término técnico (página, índice agrupado, lookup, histograma, sniffing) se **enseña con el dibujo antes de nombrarse**. El nombre aparece como `tag_junto` cuando el dibujo ya lo explicó.
- El código en pantalla es corto (≤ 5 líneas) y siempre de la tienda: `pedidos`, `clientes`, `detalle_pedido`.

## 5. Qué NO pisa

- Ningún curso previo de la colección trata bases de datos: no hay solape. No re-explica algoritmos de ordenamiento ni estructuras de datos en general: el árbol B se cuenta **solo** como «cuántas páginas hay que abrir».
- No enseña SQL desde cero (sintaxis, JOIN como concepto): asume que el espectador escribe consultas.
- No habla de hardware, SSD, RAID ni configuración del servidor más allá de MAXDOP/paralelismo en 1.3.

## 6. Principio visual no negociable

1. **La página es la moneda.** Toda lectura se VE como páginas que se encienden. Un scan enciende el muro entero; un seek, tres páginas de un árbol.
2. **El contador de lecturas en ámbar** (`S.contador_texto`) es el protagonista: sube mientras se leen páginas.
3. **El duelo**: toda mejora termina en dos barras de lecturas (log10) —antes en rojo, después en verde— con sus cifras ámbar.
4. **El plan se lee de derecha a izquierda** y el grosor de cada flecha es el número de filas (`S.flecha_plan`).
5. El código aparece en su panel (`S.codigo`) y **se ilumina la parte culpable** (un `YEAR(`, un `N'`, un `%`) con un rectángulo rojo; nunca con prosa.
6. Nada de «Modulo 0N». La pantalla es la cosa y su cifra.

## 7. Mapa de lecciones

| Lección | Proyecto | 4 clips |
|---|---|---|
| 1.1 | ✔ | ✔ | ✔ | #90 ✔ | — | ✔ | ✔ | ✔ |
| 1.2 | ✔ | ✔ | ✔ | #90 ✔ | — | ✔ | ✔ | ✔ |
| 1.3 | ✔ | ✔ | ✔ | #90 ✔ | — | ✔ | ✔ | ✔ |
| 2.1 | ✔ | ✔ | ✔ | #90 ✔ | — | ✔ | ✔ | ✔ |
| 2.2 | ✔ | ✔ | ✔ | #90 ✔ | — | ✔ | ✔ | ✔ |
| 2.3 | ✔ | ✔ | ✔ | #90 ✔ | — | ✔ | ✔ | ✔ |
| 3.1 | ✔ | ✔ | ✔ | #90 ✔ | — | ✔ | ✔ | ✔ |
| 3.2 | ✔ | ✔ | ✔ | #90 ✔ | — | ✔ | ✔ | ✔ |
| 3.3 | Columnas en vez de filas | filas contra columnas · rowgroups · lotes · 16,468 contra 6,512 |
| 4.1 | No envuelvas la columna | qué es sargable · YEAR() · CAST sí, CONVERT no · mover el cálculo |
| 4.2 | El tipo equivocado | VARCHAR y NVARCHAR · CONVERT_IMPLICIT · 960 contra 3 · el arreglo |
| 4.3 | LIKE, ISNULL y OR | prefijo y sufijo · ISNULL · la columna NOT NULL · dos seeks |
| 5.1 | Lo que el optimizador sabe | histograma · el paso del mayorista · densidad · cuándo se actualiza |
| 5.2 | Adivinar a ciegas | literal · variable: estima 8 · llegan 149,970 · el costo de errar |
| 5.3 | El motor que aprende | variable de tabla · compilación diferida · función escalar · inlining |
| 6.1 | El primero decide | un plan para todos · 501 primero · mayorista primero · el sesgo |
| 6.2 | Remedios | RECOMPILE · OPTIMIZE FOR · un índice para todos · PSP no llegó |
| 6.3 | Parámetros opcionales | la consulta comodín · plan genérico · OPPO · SQL dinámico |
| 7.1 | La caja negra | Query Store · la regresión · forzar el plan · abortar una consulta |
| 7.2 | Esperar a otro | el bloqueo · RCSI · escalamiento · optimized locking |
| 7.3 | La tienda está lenta | en qué se espera · 53 segundos · cuatro arreglos · 3.9 segundos |

## 8. Paleta por ROL

| Alias (style_block) | Color | Papel |
|---|---|---|
| `C_CALCULO` | `#22d3ee` cian | cifra **calculada aquí** (conteo sobre la reproducción de la tienda, o modelo) |
| `C_MOTOR` | `#f59e0b` ámbar | **medido en SQL Server 2025**: lecturas lógicas, páginas, segundos |
| `C_DATO` | `#94a0b0` gris | dato público (8 KB por página, 200 pasos, 1,048,576 filas por rowgroup) |
| `C_BUENO` | `#34d399` verde | el camino barato: seek, índice que sirve, plan bueno |
| `C_MALO` | `#f43f5e` rojo | el camino caro: scan de más, lookup masivo, plan malo |
| `C_INDICE` | `#3b82f6` azul | un índice (árbol, estructura), y las palabras clave del código |
| `C_CREE` | `#a78bfa` violeta | lo que el optimizador **cree** (estimación, histograma) |
| `C_TITULO` / `C_TENUE` | tinta / gris | texto y mobiliario |

La regla que no se rompe: **el ámbar es solo lo que midió el motor**. Una cifra que la librería calcula nunca va en ámbar, aunque coincida.

## 9. Contrato de la librería `sqlperf.py`

Numérica (sin manim; todo cacheado):
- `pedidos()` / `clientes()` — reproducción fila a fila del generador determinista (MD5 big-endian). ~3 s la primera vez.
- `filas_cliente(c)` — 1: **149,970** (= EQ_ROWS del motor), 501: **191**.
- `clientes_distintos()` **189,248**; `densidad()`; `estimado_variable()` **7.93**.
- `filas_rango(desde, hasta, estatus=None)` — 2025: **418,481**; cancelados 2025: **33,275**.
- `filas_estatus(e)` / `fraccion_estatus()` — entregado **91.55 %**, pendientes **2,791**.
- `filas_dia(f)`, `pedidos_por_dia()`, `filas_apellido('Garcia')` **10,165**, `telefonos_nulos()` **39,854**.
- `histograma()` — modelo de 181 pasos; el del cliente 1 tiene EQ_ROWS exacto.
- `umbral_estadisticas(n)` **38,729** (1.5 M); `umbral_estadisticas_viejo(n)` **300,500**.
- `filas_por_pagina(filas, paginas)` pedidos **67.6**; `bytes_por_fila()`; `profundidad()` **3**; `fanout_int()` **622**.
- `lecturas_seek_lookup(filas)` 501: **576** (motor 597); 1: **449,913** (motor 450,173).
- `punto_inflexion()` **7,454 filas = 0.497 %**.
- `rowgroups()` **4**; `detalle_total()` **3,750,000**.
- `MEDIDO[...]` — todas las lecturas y tiempos del motor (ámbar). `miles(x)` formatea `22,363`.

Dibujo:
- `pagina(ancho, alto, renglones, color, relleno)` — una página de 8 KB.
- `MuroPaginas(columnas, filas, lado, sep)` — la tabla entera; `.celda(i)`, `.encender(indices, color)`.
- `ArbolB(anchos=(1,4,12), ancho, alto, lado)` — `.niveles`, `.hojas`, `.ruta(hoja)`.
- `contador_texto(valor, color, font_size, digitos)` — contador ancho fijo (usar con `become` fuera de `play`).
- `barra_lecturas(valor, maximo, largo, alto, color, log=True)` — anclada a la izquierda en ORIGIN.
- `operador(nombre, color, ancho, alto)` y `flecha_plan(ini, fin, filas)` — cajas y flechas del plan.
- `codigo(lineas, font_size)` — panel T-SQL coloreado (≤ 5 × 46, ASCII). `.lineas[k]` es la línea k (para resaltarla).
- `marco_datos(ancho, alto)`.

## 10. Lotes

| Lote | Lecciones | Estado |
|---|---|---|
| 1 | 1.1–3.2 (8) | ✔ PR #90, qh, voz y mux |
| 2 | 3.3–5.3 (7) | ✔ qh, voz y mux; PR 2 |
| 3 | 6.1–7.3 (6) | ✔ qh, voz y mux; PR 2 |

## 11. Receta de lote

1. Sonda verde (`sonda_sqlperf.py`).
2. Molde (1.1, escrita por el orquestador).
3. Stubs de las 7 lecciones del lote (`curso.json` + `style_block.py` copiado del molde con su cabecera + 4 stubs).
4. Subagentes **Sonnet**, olas de 2–3, una lección cada uno, contrato en el scratchpad.
5. Revisión de frames del orquestador; correcciones (otra vuelta de agente si hace falta).
6. `pytest -q`, PR, merge.
7. Producción: `subir_curso.py`, `qh` local ×3, adopción, voz, mux.

## 12. Tablero de estado

Leyenda: — pendiente · ~ en curso · ✔ hecho.

| Lección | plan | clips | ql ✔ frames | PR | subida | qh | voz | mux |
|---|---|---|---|---|---|---|---|---|
| 1.1 | ✔ | ✔ | ✔ | ~ | — | — | — | — |
| 1.2 | ✔ | ✔ | ✔ | ~ | — | — | — | — |
| 1.3 | ✔ | ✔ | ✔ | ~ | — | — | — | — |
| 2.1 | ✔ | ✔ | ✔ | ~ | — | — | — | — |
| 2.2 | ✔ | ✔ | ✔ | ~ | — | — | — | — |
| 2.3 | ✔ | ✔ | ✔ | ~ | — | — | — | — |
| 3.1 | ✔ | ✔ | ✔ | ~ | — | — | — | — |
| 3.2 | ✔ | ✔ | ✔ | ~ | — | — | — | — |
| 3.3 | ✔ | ✔ | ✔ | ~ | — | ✔ | ✔ | ✔ |
| 4.1 | ✔ | ✔ | ✔ | ~ | — | ✔ | ✔ | ✔ |
| 4.2 | ✔ | ✔ | ✔ | ~ | — | ✔ | ✔ | ✔ |
| 4.3 | ✔ | ✔ | ✔ | ~ | — | ✔ | ✔ | ✔ |
| 5.1 | ✔ | ✔ | ✔ | ~ | — | ✔ | ✔ | ✔ |
| 5.2 | ✔ | ✔ | ✔ | ~ | — | ✔ | ✔ | ✔ |
| 5.3 | ✔ | ✔ | ✔ | ~ | — | ✔ | ✔ | ✔ |
| 6.1 | ✔ | ✔ | ✔ | ~ | — | ✔ | ✔ | ✔ |
| 6.2 | ✔ | ✔ | ✔ | ~ | — | ✔ | ✔ | ✔ |
| 6.3 | ✔ | ✔ | ✔ | ~ | — | ✔ | ✔ | ✔ |
| 7.1 | ✔ | ✔ | ✔ | ~ | — | ✔ | ✔ | ✔ |
| 7.2 | ✔ | ✔ | ✔ | ~ | — | ✔ | ✔ | ✔ |
| 7.3 | ✔ | ✔ | ✔ | ~ | — | ✔ | ✔ | ✔ |

## 13. Storyboard

Convenciones: «ámbar» = `motor_pie`/`tag_motor` con `S.MEDIDO[...]`; «cian» = `cifra_pie`/`tag_hud` con una función de `S`. Los números citados aquí son los que devuelve hoy la librería: en el clip **se leen de la librería, nunca se escriben**. Duración 28–45 s. Cada clip 4 cierra a pantalla limpia con dos líneas (la segunda cian).

### Módulo 1 · Medir antes de tocar

#### 1.1 La página: lo que cuesta leer
Intención: el espectador sale sabiendo que el motor lee **páginas de 8 KB** y que el número que importa es cuántas lee.
1. **La tienda** — tres tablas como bloques (clientes, pedidos, detalle) con sus filas (cian: 200,000 · 1,500,000 · 3,750,000, de `MEDIDO`/`detalle_total`, las filas son conteos de la reproducción). Una consulta aparece (`SELECT ... WHERE id_cliente = 501`) y un cronómetro que da números distintos en cada intento: el tiempo no sirve para comparar.
2. **Un muro de páginas** — la tabla de pedidos se «parte» en un muro de páginas; una página se agranda: 8 KB (gris), ~67.6 filas por página (cian, `filas_por_pagina`). Contador ámbar: 22,183 páginas.
3. **Buscar por la llave** — `WHERE id_pedido = 750000`: tres páginas se encienden en verde, de arriba abajo (un árbol pequeño, sin nombrarlo aún). Ámbar: 3 lecturas.
4. **Buscar sin índice** — `WHERE id_cliente = 501`: el muro entero se enciende en rojo con barrido; contador ámbar hasta 22,363. Solo 191 filas útiles (cian) → 117 páginas por fila útil (cian). Cierre: «El motor no lee filas: lee paginas.» / «Optimizar es leer menos.»

#### 1.2 Lo que pasa al ejecutar
1. **De texto a plan** — tubería de cuatro cajas: analizar → vincular → optimizar → ejecutar; la consulta entra como texto y sale como plan (árbol de operadores).
2. **Muchos planes, un costo** — el optimizador genera 3–4 planes candidatos con barra de costo estimado (violeta: lo que CREE); elige el más barato. Rótulo: «costo estimado».
3. **El plan guardado** — caché de planes: la primera ejecución compila (barra larga), las siguientes reusan (cian: contador de ejecuciones). Mostrar que el plan se reusa para otro valor: semilla del capítulo 6.
4. **Estimado contra real** — dos flechas con filas estimadas (violeta) vs reales; `estatus = 'pendiente'`: 2,791 reales (cian) y la estimación cercana. Regla 10×: dibujada como franja. Cierre: «El plan se decide antes de leer.» / «Con lo que el motor cree.»

#### 1.3 Leer un plan
1. **De derecha a izquierda** — plan de 3 operadores (Scan → Filter → Select) que se ilumina de derecha a izquierda; el grosor de flecha es el número de filas (1.5 M → 191).
2. **Scan, seek, lookup** — tres iconos/cajas con su dibujo de páginas mínimo: muro entero, ruta de 3 páginas, ruta que vuelve.
3. **Tres formas de unir** — Nested Loops (pocas filas afuera), Merge (dos listas ordenadas), Hash (tabla hash de un lado). Dibujo de las entradas; sin cifras inventadas.
4. **Ocho hilos** — el scan de pedidos repartido entre 8 hilos + coordinador (ámbar: «Scan count 9»); Gather Streams los junta. Cierre: «El plan es un mapa.» / «Las flechas gruesas son el costo.»

### Módulo 2 · El índice

#### 2.1 El árbol B
1. **Ordenar es encontrar** — el muro desordenado por cliente vs una lista ordenada con un índice arriba (como el de un libro).
2. **Bajar tres niveles** — `ArbolB((1,4,12))`: la ruta raíz→intermedia→hoja se enciende; ámbar 3 lecturas; cian: `profundidad()` = 3, fanout 622 entradas por página.
3. **El árbol crece lento** — gráfica: niveles contra filas (log): 1.5 M → 3; 1,000 M → 4 o 5 (cian, calcular con `profundidad` y los mismos filas/página y fanout). Mensaje: agregar mil veces más filas cuesta una o dos páginas más.
4. **Seek contra scan** — duelo: 3 contra 22,363 (ámbar). Cierre: «Un indice es un orden.» / «Tres paginas en vez de veintidos mil.» (sin cifras en el cierre: la segunda línea puede ser «Y el orden ahorra lecturas.»; decide el agente, sin números escritos a mano).

#### 2.2 El viaje de vuelta: lookup
1. **Un índice por cliente** — `CREATE INDEX ... (id_cliente)`; el índice solo guarda cliente + llave del pedido. Dibujo: índice delgado a la izquierda, tabla gruesa a la derecha.
2. **191 viajes** — por cada una de las 191 filas (cian) un viaje de 3 páginas al agrupado; contador ámbar sube a 597; cian modelo: 3 + 191 × 3 = 576.
3. **El mayorista** — cliente 1: 149,970 filas (cian) × 3 ≈ 449,913 (cian) contra el scan 22,363 (ámbar); el optimizador elige el scan (ámbar 22,363).
4. **Punto de inflexión** — gráfica lecturas vs filas: recta del lookup (3 por fila) contra la horizontal del scan; se cruzan en 7,454 filas = 0.50 % (cian). El 501 cae a la izquierda, el 1 a la derecha. Cierre: «Un lookup es barato.» / «Ciento cincuenta mil, no.»

#### 2.3 El índice que cubre
1. **INCLUDE** — el índice delgado engorda: fecha, estatus y total bajan a la hoja (código con `INCLUDE`).
2. **597 a 4** — la ruta de 3 niveles + 1 hoja; los viajes de vuelta desaparecen; duelo 597 → 4 (ámbar), 149× (cian, `razon`).
3. **El mayorista también** — 22,363 → 785 (ámbar); cian: filas por hoja ≈ 192 → 781 hojas.
4. **SELECT * lo rompe** — `comentarios` no está en el índice: vuelve el lookup, 597 (ámbar). Cierre: «Pide solo lo que usas.» / «El indice ya lo tiene.»

### Módulo 3 · Índices a la medida

#### 3.1 El orden de las llaves
1. **Dos órdenes** — dos listas ordenadas: (fecha, estatus) y (estatus, fecha), con filas coloreadas por estatus.
2. **Entregado casi no cambia** — 91.55 % entregados (cian): en ambos órdenes el rango es casi el mismo.
3. **Cancelado sí** — cancelados en 2025: el orden (fecha, estatus) recorre las 418,481 filas de 2025 (cian) → 1,978 lecturas (ámbar); (estatus, fecha) salta directo a las 33,275 (cian) → 161 (ámbar).
4. **Igualdad primero** — regla dibujada: columna de igualdad, luego la de rango. Cierre: «El orden de las llaves importa.» / «Igualdad primero, rango despues.»

#### 3.2 Índices que no se ven
1. **2,791 pendientes** — 0.19 % de la tabla (cian); un panel que los consulta todo el día.
2. **Índice filtrado** — `WHERE estatus = 'pendiente'` en el índice: 14 páginas, 13 lecturas (ámbar).
3. **La llave olvidada** — detalle_pedido sin índice en id_pedido: 17,606 páginas (ámbar) para el ticket de un pedido.
4. **El ticket** — 18,016 → 3 (ámbar), duelo. Cierre: «Toda llave foranea pide indice.» / «Y lo raro, un indice filtrado.»

#### 3.3 Columnas en vez de filas
1. **Filas contra columnas** — la misma tabla guardada por filas y por columnas; una suma solo toca 2 columnas.
2. **Rowgroups** — 3.75 M renglones en 4 rowgroups de hasta 1,048,576 (cian `rowgroups`, gris el tope); segmentos comprimidos.
3. **Lotes** — modo fila (una fila por vuelta) contra modo batch (~900 por lote, gris).
4. **16,468 contra 6,512** — ámbar; nota de que con 8 hilos las lecturas lob se cuentan distinto (~24,700): rotular «un hilo». Cierre: «Para sumar millones:» / «guarda columnas, no filas.»

### Módulo 4 · SARGabilidad

#### 4.1 No envuelvas la columna
1. **Qué es sargable** — un rango sobre la lista ordenada se ve como dos marcas; `WHERE fecha >= ... AND fecha < ...` = seek.
2. **YEAR()** — `YEAR(fecha_pedido) = 2025`: el motor tiene que calcular YEAR en cada una de 1.5 M filas → 7,182 (ámbar) contra el rango 1,975 (ámbar); 418,481 filas de 2025 (cian).
3. **CAST sí, CONVERT no** — `CAST(fecha AS DATE) = '2026-09-01'`: 17 lecturas (ámbar); `CONVERT(CHAR(10), ...)`: scan.
4. **Mover el cálculo** — `DATEADD(DAY, 30, fecha) > X` → `fecha > DATEADD(DAY, -30, X)`: 7,182 → 227 (ámbar). Cierre: «La columna va sola.» / «El calculo, del otro lado.»

#### 4.2 El tipo equivocado
1. **VARCHAR y NVARCHAR** — la columna email es VARCHAR; la aplicación manda N'...'. Precedencia de tipos: gana NVARCHAR, se convierte LA COLUMNA.
2. **CONVERT_IMPLICIT** — el plan muestra el aviso; el seek se vuelve scan del índice.
3. **960 contra 3** — duelo ámbar; 320× (cian).
4. **El arreglo** — el parámetro con el tipo de la columna. Cierre: «El tipo del parametro» / «es el tipo de la columna.»

#### 4.3 LIKE, ISNULL y OR
1. **Prefijo y sufijo** — `LIKE 'Gar%'` = rango en la lista ordenada (55, ámbar); `LIKE '%cia'` = revisar todo (1,012, ámbar). Mismo resultado: 10,165 Garcia (cian).
2. **ISNULL** — `ISNULL(telefono, '') = X` 535 contra `telefono = X` 3 (ámbar); 39,854 teléfonos nulos (cian).
3. **La columna NOT NULL** — sobre email el optimizador quita el ISNULL solo: 3 (ámbar).
4. **Dos seeks** — `OR` entre dos columnas indexadas: dos seeks y una unión, 14 lecturas (ámbar). Cierre: «El motor busca rangos.» / «Dale rangos que pueda ver.»

### Módulo 5 · Lo que el optimizador cree

#### 5.1 Lo que el optimizador sabe
1. **Histograma** — barras de pasos de `histograma()` (violeta), 181 pasos; RANGE_HI_KEY y EQ_ROWS como tags.
2. **El paso del mayorista** — el paso del cliente 1 es una torre: 149,970 (cian, coincide con el motor: rotular el ámbar al lado).
3. **Densidad** — 189,248 clientes distintos (cian): si no sabe el valor, supone 1.5 M / 189,248 = 7.93 filas.
4. **Cuándo se actualiza** — umbral RAIZ(1000 × n) = 38,729 contra el viejo 20 % = 300,500 (cian). Cierre: «El optimizador no lee la tabla:» / «lee su resumen.»

#### 5.2 Adivinar a ciegas
1. **Literal** — `id_cliente = 1`: usa el histograma, estima bien, elige scan: 22,363 (ámbar).
2. **Variable: estima 8** — `DECLARE @c INT = 1`: estima 7.93 (cian) → elige seek + lookup.
3. **Llegan 149,970** — flecha violeta delgada (8) contra la real gruesa; 450,173 lecturas (ámbar), 18,921× de error (cian).
4. **El costo de errar** — duelo 22,363 vs 450,173 (ámbar). Cierre: «Una mala estimacion» / «es un mal plan.»

#### 5.3 El motor que aprende
1. **Variable de tabla** — antes: el optimizador supone 1 fila; dibujo de la tubería con 1.
2. **Compilación diferida** — ahora compila con las filas reales: 1.8 s → 0.67 s (ámbar).
3. **Función escalar** — 500 llamadas fila a fila (dibujo de bucle): 17.6 s (ámbar).
4. **Inlining** — la función se funde en la consulta: 0.85 s (ámbar), 20.7× (cian). Cierre: «Actualizar el motor» / «tambien es optimizar.»

### Módulo 6 · Parámetros

#### 6.1 El primero decide
1. **Un plan para todos** — procedimiento con `@id_cliente`; el primer valor compila y el plan se guarda.
2. **501 primero** — seek + lookup: 597 (ámbar) … y el mayorista con ese plan: 459,555 (ámbar).
3. **Mayorista primero** — scan: 22,363 para él y 22,363 para el 501 (ámbar).
4. **El sesgo** — 191 contra 149,970 filas (cian) en la misma columna: el problema es el dato, no el código. Cierre: «El primero que llega» / «decide por todos.»

#### 6.2 Remedios
1. **RECOMPILE** — un plan por ejecución: siempre bueno, cuesta CPU de compilar.
2. **OPTIMIZE FOR** — fijar el valor típico.
3. **Un índice para todos** — `(id_cliente, fecha_pedido DESC) INCLUDE (...)`: 6 y 1,974 (ámbar) con el MISMO plan.
4. **PSP no llegó** — la función automática que crea variantes: 0 variantes en esta tienda (ámbar). Cierre: «El mejor remedio» / «es un indice que sirva a todos.»

#### 6.3 Parámetros opcionales
1. **La consulta comodín** — `(@x IS NULL OR col = @x)` × 3.
2. **Plan genérico** — un solo plan para cualquier combinación: 20,010 (ámbar) para el cliente 501.
3. **OPPO** — SQL Server 2025 crea 2 variantes (ámbar): 6 lecturas (ámbar).
4. **SQL dinámico** — solo los filtros que llegan: 6 (ámbar). Cierre: «Un plan por forma de pregunta,» / «no uno para todas.»

### Módulo 7 · En producción

#### 7.1 La caja negra
1. **Query Store** — cada consulta con sus planes y métricas por intervalo (línea de tiempo).
2. **La regresión** — la misma consulta con dos planes; lecturas por intervalo que saltan.
3. **Forzar el plan** — `sp_query_store_force_plan`: se fija el bueno sin tocar código.
4. **Abortar una consulta** — hint ABORT_QUERY_EXECUTION: error 8778 (ámbar). Cierre: «Lo que no se registra» / «no se puede arreglar.»

#### 7.2 Esperar a otro
1. **El bloqueo** — sesión A actualiza sin confirmar; B quiere leer y espera (LCK_M_S).
2. **RCSI** — B lee la versión anterior y no espera.
3. **Escalamiento** — 10,000 bloqueos de fila > 5,000 (gris): se bloquea la tabla entera (OBJECT X).
4. **Optimized locking** — SQL Server 2025: un solo bloqueo de transacción; B pasa. Cierre: «Leer no deberia esperar» / «a escribir.»

#### 7.3 La tienda está lenta
1. **En qué se espera** — barras de estadísticas de espera (dibujo cualitativo, sin cifras inventadas).
2. **53 segundos** — 300 peticiones (ámbar) de cuatro tipos: login, mis pedidos, ticket, reporte; 53 s (ámbar).
3. **Cuatro arreglos** — el ticket (índice en la llave), mis pedidos (índice que cubre), login (tipo del parámetro), reporte (rango en vez de YEAR): cada uno enlazado a su lección, sin nombrar números de lección.
4. **3.9 segundos** — duelo 53 → 3.9 s (ámbar), 13.6× (cian). Cierre del curso: «Medir, leer el plan, leer menos.» / «Eso es optimizar.»

## 14. Cosecha heredada (riesgo alto en este curso)

- Rajdhani parte palabras a 16–17 px y las junta bajo 22 px: los helpers imponen 18/22.
- `Transform` solo entre gemelas; contadores con `become` fuera de `play`, ancho fijo.
- `Create` reañade el mobject a la escena (`introducer=True`).
- `Text` descarta espacios (sombra del style_block): el coloreado de `S.codigo` cuenta glifos sin espacios.
- Escalar un VGroup encoge la letra: pasar `font_size`/`ancho` a la pieza.

## 15. Cosecha de trampas del lote 1

- **La librería creaba `Text` de manim sin filtrar los glifos de espacio**: recuadros de resaltado gigantes, coloreado de SQL corrido un carácter, contador que se salía por la izquierda. Toda pieza de `sqlperf` crea su texto con `S.texto()`.
- **Los agentes Sonnet dibujan pequeño y arriba**: la primera ola entregó muros de 0.17, árboles de 3 unidades y media pantalla vacía. La regla «llena el cuadro» con la zona útil numérica (y ∈ [−2.7, 2.6], x ∈ [−6.3, 6.3]) y la letra mínima 18/22 px **en todo texto** (no solo en los helpers) resolvieron la segunda.
- **Barras log sin aviso**: un público general lee 3 contra 22,363 en log como «un décimo». Toda barra log lleva «escala logaritmica».
- **Colores de papel como decoración**: arcoíris de hilos y cubetas en rojo/verde/ámbar. Tonos de un solo matiz (`paleta_categorica`).
- **Honestidad que cazó la revisión, no el agente**: flecha de salida de un scan filtrado rotulada con las filas LEÍDAS (1.5 M) en vez de las devueltas (191); páginas de la tabla (17,606) rotuladas como «lecturas»; renglones de un pedido concreto sacados de `lineas_detalle`, que solo está validada en el total.
- `Indicate(color=X)` hace ida y vuelta de color y deshace un `set_color` en el mismo `play`.
- A 480p (`ql`) Rajdhani junta «cl» y «cliente» parece «diente»; la `@` de Space Mono parece «ä». A 1080p se leen bien: no se corrige en `ql`.

## 15bis. Cosecha de trampas de los lotes 2 y 3

- **`rot.limpiar()` sin zona borra también el título**: dos agentes lo usaron a mitad de clip y el título desaparecía; la hoja de interiores lo cazó (pieza a pieza no se notaba). A mitad de clip, `rot.limpiar("abajo")`.
- **`S.operador` encoge el nombre si no cabe**, y bajo 22 px Rajdhani se come el espacio («Variantecliente»). Nombres de dos palabras con `ancho=` suficiente.
- **El ámbar se cuela como resaltado**: bordes de operadores, tachas y hasta un rótulo «sobre 200,000 clientes» salieron en ámbar. Solo cifras medidas.
- **`dato_pie` no es para frases ni para nombres del motor**: «el orden ya no sirve · dato» y «LCK_M_IX · dato». Frases fuera; nombres del motor como `tag_hud` gris junto a lo que nombran.
- **Un detalle técnico falso en el código de pantalla**: `VARCHAR(50)` para una columna que es `VARCHAR(120)`. Los agentes no leen el esquema: el orquestador lo revisa.
- **Precisión falsa**: `~4,167 lotes` sobre un `~900` aproximado → `~4,200`.
- **Paneles de código que tapan el título** (`move_to(UP * 2.15)` con 4–5 líneas) y **operadores en el carril de la cifra**: los dos defectos de maquetación más repetidos después de «deja media pantalla vacía».
- Dos agentes redondearon con buen criterio lo que el storyboard no fijaba (la escala lineal con torre recortada en el histograma, no repetir la razón de 5.2 en 5.1): el storyboard puede dejar elecciones abiertas si el contrato dice qué no se negocia.

## 16. Hitos

- 2026-09-24: plan, librería `sqlperf.py` y sonda (0 fallos).
- 2026-09-24: molde 1.1 escrito y revisado; 20 lecciones por agentes Sonnet (olas de 3), cada una revisada por el orquestador fotograma a fotograma y devuelta con correcciones cuando hizo falta (1.2, 1.3, 2.1, 2.3, 3.1, 4.1, 4.3, 6.3, 7.2 volvieron al agente; otras las corrigió el orquestador).
- 2026-09-24: PR #90 fusionado (lote 1, 1.1–3.2).
- 2026-09-25: **las 21 lecciones producidas**: 84 clips en `qh` 1080p60 (`render_jobs/qh/rendimiento-sql-*`), voz edge es-MX-JorgeNeural sintetizada EN LOCAL desde `curso-37-guion-de-voz.md` (84 wavs, ninguno acelerado por el mux), y **21 montajes con intro y cierre en `exports/rendimiento-sql-*/curso_narrado.mp4`: 48.1 min**, de 2:13 a 2:23 cada uno, picos de los clips entre −1.1 y −3.0 dB, marca sonora −6.0 dB. Hojas de interiores de las 84 piezas revisadas (cazaron un título borrado por `rot.limpiar()` y cajas tapadas por un `Indicate`).
- Pendiente (a decisión del dueño): subir las 21 lecciones a la base de producción de ManimStudio (`subir_curso.py` + adopción de los `qh`) y la voz en el VPS.
