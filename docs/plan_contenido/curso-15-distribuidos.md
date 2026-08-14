# Curso 18 · «Sistemas distribuidos: la nube por dentro» (archivo curso-15)

> **Numeración**: los archivos `curso-NN-*.md` van por orden de creación;
> la numeración REAL la lleva `PLAN.md`. Este es el **curso 18**.

## Tesis

«La nube» son miles de máquinas ordinarias fingiendo ser una sola
extraordinaria — y el truco no es hardware: son matemáticas. Con 1000
máquinas al 99.9 %, hay un **63 % de probabilidad de que alguna esté
caída AHORA**; la física pone pisos de latencia que ningún cable rompe
(113 ms ida y vuelta a Tokio); y en una red no existe el «ahora», así
que el orden, la mayoría y el reparto hay que **construirlos**: relojes
lógicos, quórums, líderes electos y anillos de hash. La nube no es un
lugar: es un pacto entre máquinas que desconfían unas de otras.

## Los números (todos calculados por la librería, jamás a mano)

| Cantidad | Valor | Fuente |
|---|---|---|
| P(alguna caída) con N=1000, p=99.9 % | **63.2 %** | 1 − p^N |
| N=10 / N=100 | 1.0 % / 9.5 % | 1 − p^N |
| 3 réplicas caídas a la vez | 1e-9 → disponibilidad **99.9999999 %** | (1−p)³ |
| v de la luz en fibra | 200 000 km/s (c/1.5, cita índice) | constante |
| CDMX–Nueva York | 3 359 km → RTT piso **34 ms** | haversine + 2d/v |
| CDMX–Madrid | 9 063 km → RTT piso **91 ms** | haversine |
| CDMX–Tokio | 11 307 km → RTT piso **113 ms** | haversine |
| Quórum N=5, W=3, R=3 | intersección garantizada ≥ **1** nodo | W+R−N |
| Anillo hash 4→5 nodos | se reubica **~20 %** de las claves (MEDIDO) | conteo sobre el anillo |
| Relojes de Lamport | contadores del diagrama, calculados | núcleo happened-before |
| Elección: mayoría de 5 | 3 votos; empate → nueva ronda (sembrado) | simulación determinista |

## Reglas de honestidad

- El 63.2 % es probabilidad de que AL MENOS UNA máquina esté caída, no
  de que el servicio falle — el clip lo dice y ahí entra la replicación.
- Los RTT son PISOS físicos (gran círculo × c/1.5): la latencia real es
  mayor (rutas, colas); se rotula «piso físico».
- La fracción del anillo se MIDE contando claves reasignadas en el
  dibujo, no se cita el 1/(n+1) teórico (se menciona que coincide).
- La elección de líder es «al estilo Raft», simplificada y sembrada
  (se rotula «simulación»); los términos y el empate resuelto por
  timeout aleatorio son los reales del algoritmo.
- CAP se cuenta como disyuntiva DURANTE una partición (la formulación
  moderna), no como «elige 2 de 3».
- Lamport: los relojes lógicos ordenan causas, no dan hora — el clip
  cierra con esa limitación (eventos concurrentes quedan sin orden).

## Paleta (regla semántica)

- `C_MENSAJE` ámbar `#f59e0b` — los mensajes, los datos viajando.
- `C_NODO` cian `#22d3ee` — los nodos, las réplicas, lo medido.
- `C_OK` verde `#34d399` — la mayoría, el quórum, lo disponible.
- `C_FALLO` rojo `#f43f5e` — las caídas, la partición, el split-brain.
- `C_TIEMPO` violeta `#a78bfa` — los relojes lógicos, el anillo de hash.
- `C_EJE` gris azulado `#31414f` — mobiliario.

## Los 8 clips (28–45 s duros; pies ≥5 s; pie cambia ANTES del transform)

### 1 · La máquina que no existe
«La nube» = una rejilla de nodos cian ordinarios. La cuenta cruel: la
curva 1 − p^N con p = 99.9 %: en N=10 casi nada (1 %), en N=100 ya 9.5 %,
en **N=1000 el 63.2 %**: siempre hay algo roto. Algunos nodos de la
rejilla se apagan en rojo mientras la curva sube. Cierre: el sistema
debe funcionar CON fallas, no sin ellas. Final: rejilla con caídos +
curva + 63.2 % rotulado.

### 2 · La velocidad de la luz no negocia
La física primero: la luz en fibra viaja a ~200 000 km/s (c/1.5). Línea
de ciudades a escala de distancia real (CDMX, NY, Madrid, Tokio) con
arcos de mensaje: **34, 91, 113 ms** de ida y vuelta, PISO físico, sin
colas ni rutas. Por eso existen réplicas cerca de ti (CDN). Final: línea
con los tres arcos y sus pisos rotulados.

### 3 · No existe el «ahora»
Diagrama espacio-tiempo de 3 procesos con mensajes ámbar. Dos eventos
en máquinas distintas: ¿cuál fue primero? Sin reloj común, no se sabe.
Lamport 1978: cada proceso cuenta (contador violeta), cada mensaje
lleva el contador y el receptor toma max+1: la CAUSA siempre numera
menos que el efecto. Cierre honesto: eventos sin flechas entre sí
quedan **concurrentes** — el orden total no existe, se construye uno.
Final: diagrama con todos los relojes de Lamport rotulados.

### 4 · Partido en dos (CAP)
Dos centros de datos (cajas cian) con su enlace; un usuario escribe a
la izquierda, la réplica viaja. Se corta el enlace (rojo): PARTICIÓN.
Llega una lectura a la derecha: ¿respondes con lo que tienes (quizá
viejo) o esperas (no disponible)? Ésa es la disyuntiva real de CAP:
durante la partición eliges consistencia o disponibilidad. Final: las
dos cajas partidas con las dos salidas rotuladas (A / C).

### 5 · La mayoría manda
¿Cómo acordar sin jefe? Quórum: N=5 nodos; escribir exige W=3 (verde),
leer exige R=3; como **W+R > N**, todo conjunto de lectura pisa al
menos **1 nodo** con el dato nuevo (palomar: W+R−N = 1). Se ven los dos
conjuntos solapándose en el nodo compartido. Y por qué N impar: 5
tolera 2 caídas, 4 solo 1. Final: los 5 nodos con W y R marcados y la
intersección brillando.

### 6 · Elegir un líder
Nadie manda… hasta que se vota (al estilo Raft, simulación sembrada).
5 nodos; el de timeout más corto se candidatea (término 1), pide votos,
mayoría → líder (corona ámbar). Se cae el líder (rojo): silencio,
timeouts corren, DOS se candidatean a la vez → empate 2-2-1 → nadie
gana → nuevo término con timeouts re-sorteados → líder nuevo. Final:
término 3 con el nuevo líder coronado y el caído en rojo.

### 7 · El anillo que reparte
¿Qué nodo guarda qué clave? Anillo violeta: claves y nodos viven en el
mismo círculo (hash); cada clave pertenece al primer nodo a favor de
las manecillas. Entra un nodo nuevo: solo se mueven las claves de UN
arco — **29 % medido (7 de 24 claves contadas)**, del orden del 1/(n+1)
teórico (20 % en promedio); el resto ni se entera. Así crece la nube sin reordenar el mundo. Final:
anillo con 5 nodos, claves recoloreadas del arco movido y la cifra.

### 8 · La nube es un pacto
La recapitulación con la cuenta final: una máquina 99.9 %; tres
réplicas → **99.9999999 %** (nueve nueves): la fiabilidad no se compra,
se construye con matemáticas. Miniaturas (rejilla/curva, diagrama
Lamport, quórum, anillo). Cierre: «Ninguna máquina es fiable.» / «El
pacto entre ellas, sí.»

## Contrato de la librería `distribuido.py`

Núcleos numpy/python puros y deterministas (todo azar con semilla);
capa Manim con localizadores sobre geometría ACTUAL y anclas
invisibles; números por funciones; topes duros con ValueError.

Funciones: `prob_alguna_caida(p, n)`, `disponibilidad_replicas(p, k)`,
`distancia_km(ciudad_a, ciudad_b)` (haversine sobre `CIUDADES`),
`rtt_ms(a, b)` (2d/V_FIBRA), `relojes_lamport(eventos, mensajes)`,
`interseccion_quorum(n, w, r)`, `rondas_eleccion(semilla)` (lista de
rondas con timeouts, candidatos, votos y ganador), constantes
V_FIBRA_KMS, P_MAQUINA, CIUDADES.

Piezas: `rejilla_nodos` (grid de nodos; `.nodo(i)`, `.con_caidos(k,
semilla)` apaga en rojo), `curva_caidas` (1−p^N vs N, x log;
`.en(n)`), `linea_latencia` (ciudades a escala + `.arco(a, b)` con
`.rtt_ms` calculado), `diagrama_lamport` (3 procesos, eventos,
mensajes; relojes calculados por el núcleo; `.evento(p, i)`,
`.reloj(p, i)`), `par_centros` (dos cajas + enlace; `.con_corte()`),
`nodos_quorum` (N nodos en arco; `.marca_conjunto(indices, color)`,
`.interseccion(w_idx, r_idx)` MEDIDA), `anillo_hash` (círculo + nodos +
claves sembradas; `.con_nodo_extra()`, `.fraccion_movida()` MEDIDA
comparando asignaciones, `.clave(i)`, `.nodo(i)`), `corona(nodo)` para
el líder.

## Producción

Igual que cursos 16–17: validación en contenedor → stubs → 3 Opus
(clips 1-2, 4-5, 7-8) + Sonnet (demo 26-distribuido.py) + yo (clips 3 y
6, los de coreografía fina) → render_local ql + frames → tests → PR con
PLAN.md → qh local 3 procesos → adoptar en VPS → guiones.py → mux.
Proyecto: `studio/content/cursos/sistemas-distribuidos-la-nube-por-dentro/`, qh.
