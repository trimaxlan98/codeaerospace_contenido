# Curso 22 — Álgebra lineal (familia de lecciones)

- **Formato**: familia de lecciones, como Electromagnetismo (curso 16) y
  Metrología óptica (curso 20). Un proyecto de ManimStudio = una **lección**
  de 4 clips; cada clip = una idea. 4 módulos × 3 lecciones = **12
  proyectos, 48 clips**.
- **Título de la familia**: `Álgebra lineal`, sin numeración de plan de
  estudios (reciclable en cualquier programa).
- **Ángulo editorial**: la materia se complica porque es abstracta, así que
  aquí **cada idea se VE moverse**: la rejilla del plano se deforma, los
  vectores se estiran y giran, el paralelogramo se sombrea, la nube de
  puntos se aplasta. Estilo *Essence of linear algebra* pero guion,
  ejemplos y librería originales, en español. Ejemplos con sabor
  aeroespacial/telecom donde salen solos (actitud de un satélite, cambio de
  marco cuerpo/inercial, telemetría con deriva, imagen de un sensor), sin
  forzarlos.
- **Público**: divulgación técnica; asume aritmética y algo de trigonometría.
  Se muestran las fórmulas, pero lo que se explica es lo que DICEN.
- **No pisa** cursos publicados: «Redes neuronales» y «Embeddings» usan
  matrices como caja negra; aquí la matriz ES el movimiento.

```
familia            ManimStudio
-----------------  ----------------------------------------
módulo   (4)   →   —  (agrupación editorial, no existe en la DB)
lección  (12)  →   proyecto  "Álgebra lineal · N.M <título>"
idea     (48)  →   clip      "MODULO 0K" en el HUD (K = número de clip)
```

Slugs `algebra-lineal-N-M-<tema>`. Clips de 28–45 s (tope duro), pies ≥ 5 s
legibles, el pie cambia ANTES de la animación que ilustra. Un solo cierre a
pantalla limpia por lección (clip 4).

## Principio visual no negociable

1. En cada clip se ve **la rejilla** (plano o espacio) y, si hay una
   transformación, se ve **deformarse** de forma continua: rejilla de fondo
   fija en gris + rejilla viva en azul que se mueve. Las rectas siguen rectas,
   paralelas y equiespaciadas; el origen no se mueve — eso ES linealidad.
2. Los vectores **se ven mover** (Transform del arrow), no aparecen ya movidos.
3. **Cada número en pantalla se calcula con numpy** dentro de la librería o
   del `style_block` (`fmt()`); nada escrito a mano. La matriz que se
   muestra y la rejilla que se deforma salen del MISMO array.
4. La matriz se muestra **por columnas de colores**: columna 1 = a dónde va î
   (ámbar), columna 2 = a dónde va ĵ (cian), columna 3 = k̂ (violeta).
5. Un solo cierre a pantalla limpia por lección (dos líneas, la segunda en
   cian), como en Electromagnetismo.

## Mapa de las 12 lecciones

| Lección | Proyecto | Modelo | Clips |
|---------|----------|--------|-------|
| 1.1 | El vector: flecha, lista y movimiento | Fable (molde) | 4 |
| 1.2 | Combinaciones lineales y span | Sonnet | 4 |
| 1.3 | Dependencia lineal, base y dimensión | Sonnet | 4 |
| 2.1 | La matriz es un movimiento | Opus | 4 |
| 2.2 | Componer movimientos: el producto | Sonnet | 4 |
| 2.3 | El determinante: área y orientación | Opus | 4 |
| 3.1 | Sistemas Ax = b y la inversa | Sonnet | 4 |
| 3.2 | Rango, núcleo e imagen | Opus | 4 |
| 3.3 | Cambio de base: el mismo vector, otro idioma | Opus | 4 |
| 4.1 | Vectores propios: los que no giran | Opus | 4 |
| 4.2 | Diagonalizar y las potencias | Sonnet | 4 |
| 4.3 | Proyección, mínimos cuadrados y ejes principales | Opus | 4 |

Arco: el módulo 1 construye el espacio con vectores; el 2 lo pone a
moverse (la matriz); el 3 pregunta al revés (¿de dónde vino b?, ¿qué se
perdió?, ¿en qué idioma lo digo?); el 4 encuentra los ejes que la
transformación respeta y los usa para ver datos reales.

## Paleta de la familia (por ROL)

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_I` | `#f59e0b` ámbar | î, primera columna de la matriz, primer eje propio |
| `C_J` | `#22d3ee` cian | ĵ, segunda columna; también las CIFRAS calculadas (tag_hud) |
| `C_K` | `#a78bfa` violeta | k̂, tercera columna (3D) |
| `C_VEC` | `#f43f5e` rojo | el vector protagonista / la entrada / los datos |
| `C_IMG` | `#34d399` verde | la imagen: el vector transformado, el resultado, b |
| `C_PROPIO` | `#e879f9` fucsia | direcciones propias, ejes principales |
| `C_AREA` | `#fb923c` naranja | el paralelogramo del determinante (fill 0.35) |
| `C_REJILLA` | `#31414f` | rejilla de fondo FIJA (mobiliario) |
| `C_VIVA` | `#3b82f6` azul | la rejilla que se MUEVE |
| `C_EJE` | `#94a0b0` muted | ejes x/y del plano |

Regla: **el color dice el papel**. Ámbar/cian son SIEMPRE las columnas (î,
ĵ) y sus imágenes; rojo el vector del que se habla; verde lo que sale de la
cuenta como vector; cian las cifras. La rejilla viva es azul y la fija gris:
en cualquier frame se sabe qué se movió y qué no.

## Librería `manim_extensions/algebra_lineal.py` (contrato)

Determinista, numpy puro, sin red/disco/azar (los datos "ruidosos" salen de
`np.random.default_rng(semilla)` con semilla FIJA declarada). Piezas
`VGroup` cuyos localizadores leen la posición ACTUAL (siguen `move_to`,
NO `scale`; la escala se fija con `unidad`).

```python
fmt(x, dec=1)                       # número formateado (ASCII, "-0.0" normalizado)
plano(unidad=1.0, x=(-4,4), y=(-3,3), fijo=True, vivo=True)
    # .fijo (rejilla gris) .vivo (rejilla azul) .ejes ; .p(x,y) coord->pantalla
    # .rejilla_con(M) : rejilla viva transformada por M (para Transform)
    # .anim_matriz(M, *vectores) : Transform de rejilla viva + flechas (linealidad continua)
    # .aplicar(M) : deja la rejilla en estado M (sin animar)
vector(plano, coords, color, nombre=None)  # Arrow desde el origen + etiqueta;
    # .con_matriz(M) gemelo transformado ; .coords ; .a_coords(c) mutación
matriz_columnas(M, colores=(C_I,C_J[,C_K]), dec=1)   # MathTex por columnas
vector_columna(v, color, dec=1)          # MathTex [x;y]
combinacion(plano, a, u, b, v)          # a*u en ámbar + b*v cian puestos cola-punta + resultante roja
span_recta(plano, u) / span_plano(...)  # la recta/plano generado (tenue)
paralelogramo(plano, M, color=C_AREA)   # área |det| sombreada; .area
determinante(M)                          # np.linalg.det redondeado
inversa(M), rango(M), nucleo(M)          # numpy; nucleo devuelve base ortonormal
proyeccion(v, u)                         # escalar y vector proyección
autos(M)                                 # (valores, vectores) ordenados, reales
diagonalizar(M)                          # P, D, P^-1
minimos_cuadrados(xs, ys)               # pendiente, ordenada
nube(semilla, n, cov)                    # nube de puntos determinista; .puntos
ejes_principales(nube)                  # PCA: autovectores de la covarianza
rot2(theta), cizalla(k), escala(sx,sy)  # matrices 2x2 clásicas
rot3(eje, theta)                         # matrices 3x3 de rotación
espacio3(...)                            # proyección oblicua FIJA de una caja 3D a 2D
    # .p(x,y,z) ; .rejilla_con(M) ; .vector(v) ; .anim_matriz(M)
```

Cifras cabeza (validadas en el contenedor con numpy antes de escribir clips):
det de cizalla = 1; det de rot = 1; det([[2,1],[1,2]]) = 3; autos de
[[2,1],[1,2]] = 1 y 3 con vectores (1,-1)/√2 y (1,1)/√2; Fibonacci por
potencias de [[1,1],[1,0]] con φ = 1.618; rot3 no conmutan (Rx(90)Ry(90) ≠
Ry(90)Rx(90)).

## Contrato para los subagentes (una lección por agente)

Rutas ABSOLUTAS dentro del worktree
`/home/alanrosasp/Documentos/github/codeaerospace_contenido-algebra`:

- Lección en `studio/content/cursos/algebra-lineal-N-M-<tema>/` con
  `curso.json`, `style_block.py` (copiar el de 1.1 y cambiar SOLO la cabecera
  y `# --- Numeros de la leccion ---`), `clips/0K-<tema>.py` con `class
  ClipK(Scene)`. Los stubs ya existen: sustituirlos.
- Reglas duras: 28–45 s por clip; pies ≥ 5 s; el pie cambia ANTES de la
  animación; HUD `hud_modulo("Modulo 0K")`; título con `titulo_curso`; un
  solo cierre a pantalla limpia (clip 4, dos líneas: blanca + cian); NADA
  encimado (revisar frames uno a uno); `tag_hud` solo ASCII (Space Mono no
  trae superíndices ni acentos); Rajdhani no trae λ ni ² (usar MathTex);
  cifras a la derecha con `to_corner(UR, buff=0.55).shift(DOWN*0.5)`; TODO
  número sale de la librería / style_block, nunca a mano; en cada clip la
  rejilla se ve y, si hay matriz, se ve deformarse (`plano.anim_matriz`).
- Validación (desde el worktree, con el venv del checkout principal):
  `/home/alanrosasp/Documentos/github/codeaerospace_contenido/studio/backend/venv/bin/python studio/tools/render_local.py studio/content/cursos/<slug> --clip N --frames 8`
  → revisar `render_jobs/validacion/<slug>/0N-ClipN/frames/*.png` uno a uno
  (Read). Criterio por frame: nada encimado, texto legible, cifras que
  coinciden con lo dibujado, rejilla visible, colores por rol, duración
  reportada en rango. Iterar hasta pasar los 4.
- No tocar la librería ni otras lecciones: si falta algo, hacerlo en el clip
  y REPORTARLO en el mensaje final (Fable lo sube a la librería).
- Al terminar: informar duración de cada clip y cualquier bug/rodeo.

## Tablero de estado

Columnas: storyboard · clips escritos · validada ql · en repo/PR · qh local
· adoptada en prod · narrada · muxeada.

| Lección | storyboard | clips | ql | repo/PR | qh | prod | narrada | mux |
|---------|-----------|-------|----|---------|----|------|---------|-----|
| 1.1 | ✔ | ✔ | ✔ 31.9/36.5/36.2/33.6 s | PR #35 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 1.2 | ✔ | ✔ | ✔ 29.8/32.5/30.9/30.9 s | PR #35 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 1.3 | ✔ | ✔ | ✔ 35.1/33.7/32.3/41.1 s | PR #35 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 2.1 | ✔ | ✔ | ✔ 40.8/36.3/38.0/36.9 s | PR #35 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 2.2 | ✔ | ✔ | ✔ 33.5/35.2/30.3/40.0 s | PR #35 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 2.3 | ✔ | ✔ | ✔ 34.6/36.3/38.3/41.8 s | PR #35 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 3.1 | ✔ | ✔ | ✔ 34.3/31.9/30.9/33.0 s | PR #35 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 3.2 | ✔ | ✔ | ✔ 42.1/41.7/36.0/41.3 s | PR #35 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 3.3 | ✔ | ✔ | ✔ 36.3/35.2/39.7/35.9 s | PR #35 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 4.1 | ✔ | ✔ | ✔ 38.5/35.4/39.2/39.7 s | PR #35 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 4.2 | ✔ | ✔ | ✔ 36.1/30.1/33.7/32.4 s | PR #35 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 4.3 | ✔ | ✔ | ✔ 38.0/40.3/37.0/39.0 s | PR #35 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |

Hitos globales (2026-08-19 15:30): **FAMILIA PUBLICADA DE PUNTA A PUNTA, 18 lecciones / 72 clips** — librería ✔ · PR #35 (módulos 1–4) y PR #36 (ampliación 5–6) mergeados · 18 proyectos en prod con 72 qh vigentes · narración Charon ×18 (serial) · 18 `exports/algebra-lineal-*/curso_narrado.mp4` (2:22–2:59, picos ≤ −0.5 dB, intro/cierre de marca) · PLAN.md/CATALOGO ✔ · memoria ✔. Las corridas nocturnas del cron murieron por cuota; el grueso se hizo en sesión interactiva con 17 subagentes.

## Módulo 1 — El espacio y sus vectores

### 1.1 El vector: flecha, lista y movimiento

Hilo: un vector es una flecha desde el origen Y una lista de números → sumar
es encadenar → escalar es estirar → todo vector es a·î + b·ĵ.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Una flecha y una lista | rejilla; la flecha roja (3,2) nace; sus coordenadas se leen en la rejilla; la columna [3;2] | vector (3,2) con proyecciones punteadas y la columna |
| 2 | Sumar es caminar | u y v; v se traslada a la punta de u; la resultante verde; las coordenadas se suman | u+v con paralelogramo tenue y la suma calculada |
| 3 | Escalar es estirar | 2u, 0.5u, −u sobre la misma recta; el escalar se lee en cifra | −1.5u con la recta del span insinuada |
| 4 | Todo vector es î y ĵ | î ámbar, ĵ cian; (3,2) = 3î + 2ĵ construido cola-punta; cierre | cierre «Una flecha es una lista. / Una lista es una flecha.» |

### 1.2 Combinaciones lineales y span

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Mezclar dos vectores | a·u + b·v con a, b variando; la punta recorre el plano | varias combinaciones y sus puntas |
| 2 | El span: todo lo que alcanzas | barrido: las puntas llenan el plano; sombra creciente | plano completo generado |
| 3 | Cuando se alinean | v colineal con u: el span se aplasta a una recta | recta del span con u y v encima |
| 4 | Span en tres dimensiones | espacio3: dos vectores generan un plano; el tercero sale o no | plano generado en 3D + cierre «Dos flechas: un plano. / Tres, si no se esconden: el espacio.» |

### 1.3 Dependencia lineal, base y dimensión

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | El vector que sobra | tres vectores en el plano: el tercero es combinación de los otros dos (se construye) | w = a·u + b·v cerrando el triángulo |
| 2 | Base: lo mínimo que lo genera todo | dos vectores no alineados; cualquier punto se alcanza; el ejemplo de la base canónica y otra | el mismo punto con dos parejas de coordenadas |
| 3 | Coordenadas: números que dependen de la base | la rejilla de otra base (oblicua) sobre la canónica; el mismo vector, otras cifras | rejilla oblicua + vector rojo con dos lecturas |
| 4 | Dimensión: cuántos hacen falta | recta 1, plano 2, espacio 3; ni uno más ni uno menos | tríptico + cierre «Base: los justos. / Dimensión: cuántos son.» |

## Módulo 2 — La transformación lineal

### 2.1 La matriz es un movimiento

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Mover el plano entero | rejilla viva se deforma bajo M; rectas siguen rectas, origen quieto | rejilla transformada, la fija detrás |
| 2 | Basta saber a dónde van î y ĵ | î y ĵ se mueven; sus destinos son las columnas; la matriz aparece por columnas | matriz por columnas + î', ĵ' |
| 3 | Un vector cualquiera sigue la receta | v = 3î+2ĵ → Mv = 3î'+2ĵ' construido; el producto matriz-vector | Mv verde con la cuenta |
| 4 | Un catálogo de movimientos | rotación, cizalla, escala, reflexión: la rejilla los ejecuta uno tras otro | cierre «La matriz no es una tabla. / Es a dónde van î y ĵ.» |

### 2.2 Componer movimientos: el producto

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Primero uno, luego otro | rotación y luego cizalla; el resultado es una sola matriz | rejilla tras BA + matriz producto |
| 2 | Multiplicar es componer | las columnas de BA = B aplicada a las columnas de A (se calcula) | producto por columnas coloreadas |
| 3 | El orden importa | AB vs BA sobre la misma rejilla, lado a lado | dos rejillas distintas + AB ≠ BA |
| 4 | Girar un satélite | rot3: alabeo luego cabeceo ≠ cabeceo luego alabeo (espacio3) | dos actitudes distintas + cierre «Componer es multiplicar. / Y el orden se nota.» |

### 2.3 El determinante: área y orientación

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | El cuadrado unidad se estira | el cuadrado î–ĵ se vuelve paralelogramo; su área medida = det | paralelogramo naranja + det = 3.0 |
| 2 | El factor de área | cualquier figura escala su área por det (rejilla entera) | rejilla + varias celdas sombreadas ×det |
| 3 | El signo: la orientación | reflexión: det negativo, î y ĵ intercambian lado | paralelogramo volteado + det = −1.0 |
| 4 | Cero: el plano se aplasta | matriz singular: rejilla a una recta; área 0; en 3D volumen (espacio3) | recta aplastada + cierre «El determinante es cuánto crece el área. / Cero: algo se perdió.» |

## Módulo 3 — Preguntar al revés

### 3.1 Sistemas Ax = b y la inversa

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | El sistema es una pregunta geométrica | Ax = b: ¿qué x aterriza en b? rejilla transformada, b verde, x rojo | x que aterriza en b |
| 2 | Deshacer el movimiento: la inversa | A^-1 devuelve la rejilla a su sitio; A^-1 A = I | rejilla vuelta + matriz inversa calculada |
| 3 | Resolver es aplicar la inversa | x = A^-1 b; la cuenta con números | x calculado y comprobado |
| 4 | Cuando no hay vuelta atrás | det 0: dos x van al mismo b, otros b no se alcanzan | recta aplastada + cierre «Si el área sobrevive, hay inversa. / Si se aplasta, no.» |

### 3.2 Rango, núcleo e imagen

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | La imagen: a dónde puede llegar | rejilla → recta (rango 1) y → plano (rango 2) | las dos imágenes lado a lado |
| 2 | El rango es la dimensión de la imagen | matriz 2×2 rango 1 y 2; en espacio3 rango 2 = plano | rango rotulado por caso |
| 3 | El núcleo: lo que va a cero | los vectores que caen al origen forman una recta | recta del núcleo fucsia + flechas cayendo |
| 4 | Lo que se pierde y lo que queda | rango + nulidad = n (2 = 1 + 1; 3 = 2 + 1) | tríptico + cierre «Imagen: lo que queda. / Núcleo: lo que se pierde.» |

### 3.3 Cambio de base: el mismo vector, otro idioma

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Dos rejillas, un vector | la rejilla oblicua de otra base; el mismo v con dos coordenadas | dos lecturas del mismo vector |
| 2 | La matriz de cambio de base | P lleva de coordenadas nuevas a canónicas; P^-1 al revés | P y P^-1 calculadas |
| 3 | Traducir una transformación | P^-1 A P: el mismo movimiento contado en el otro idioma | las dos matrices y la misma rejilla |
| 4 | El marco del satélite | marco cuerpo vs marco inercial: el mismo vector Sol, dos listas | espacio3 + cierre «El vector no cambia. / Cambian sus números.» |

## Módulo 4 — Los ejes que la transformación respeta

### 4.1 Vectores propios: los que no giran

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Casi todo gira | la rejilla se deforma y los vectores cambian de dirección… menos dos | rejilla transformada con dos direcciones fucsia |
| 2 | Los que solo se estiran | Av = λv: se estira por 3 y por 1 en direcciones propias | autovectores con sus λ |
| 3 | Encontrarlos: det(A − λI) = 0 | la rejilla de A − λI se aplasta justo en λ = 1 y 3 | curva det(A−λI) con los ceros |
| 4 | Los que no los tienen | rotación: nadie se queda; cizalla: solo uno | dos casos + cierre «Los ejes propios / son los que la transformación respeta.» |

### 4.2 Diagonalizar y las potencias

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | En la base propia todo es estirar | la rejilla propia oblicua: A solo escala sus ejes | rejilla propia + D |
| 2 | A = P D P^-1 | traducir, estirar, destraducir | las tres matrices calculadas |
| 3 | Potencias sin sudar | A^n = P D^n P^-1; A^10 en un paso; Fibonacci y φ | A^10 calculada + φ = 1.618 |
| 4 | Iterar y converger | aplicar A muchas veces: todo vector se acuesta sobre el propio dominante | secuencia de vectores + cierre «Repite un movimiento mil veces / y verás su eje.» |

### 4.3 Proyección, mínimos cuadrados y ejes principales

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | El producto punto es una sombra | v·u = |v||u| cos θ: la proyección se ve; ortogonal = 0 | proyección + cifra |
| 2 | Proyectar sobre una recta | el punto más cercano; el error perpendicular | proyección con residuo |
| 3 | La recta que mejor ajusta | telemetría con deriva: la recta de mínimos cuadrados (calculada) | nube + recta + pendiente |
| 4 | Los ejes de una nube | PCA: autovectores de la covarianza; el eje mayor de una nube de datos; recap de familia | ejes principales + cierre «Encuentra los ejes / y el problema se endereza.» |


## Ampliación (2026-08-19, pedida por el dueño): módulos 5 y 6

Seis lecciones más (24 clips) con el mismo formato y molde. El módulo 5 encuentra
**los movimientos que respetan la geometría** (ortogonalidad, la SVD, el equilibrio de
Markov); el módulo 6 saca el álgebra lineal **del plano al mundo** (rotaciones 3D con
eje, funciones como vectores, sistemas dinámicos). Piezas nuevas de la librería
(sección "Modulos 5 y 6" de `algebra_lineal.py`): `gram_schmidt`, `qr`,
`es_ortogonal`, `svd`, `aproximacion_rango`, `numero_condicion`, `elipse_de`,
`imagen_sintetica`, `markov_estacionario`, `iterar`, `autos_complejos`,
`eje_rotacion`, `rot3_eje`, `muestrear`, `base_fourier`, `coeficientes`;
piezas `circulo_unidad` (→ elipse con `.con_matriz`, `.semiejes()`), `pixeles`
(matriz de grises, `.con_valores`), `barras` (`.con_valores`), `trayectoria`,
`triada3` (`.con_matriz`). Validadas en el contenedor (frame en
`render_jobs/validacion/_lib/`).

| Lección | Proyecto | Modelo | Clips |
|---------|----------|--------|-------|
| 5.1 | Ortogonalidad: bases que no se estorban | Sonnet | 4 |
| 5.2 | La SVD: todo movimiento es girar, estirar, girar | Opus | 4 |
| 5.3 | Cadenas de Markov: el equilibrio que la matriz esconde | Sonnet | 4 |
| 6.1 | Rotaciones en 3D: toda rotación tiene un eje | Opus | 4 |
| 6.2 | Las funciones también son vectores | Opus | 4 |
| 6.3 | Sistemas dinámicos: la matriz que mueve el tiempo | Opus | 4 |

### 5.1 Ortogonalidad: bases que no se estorban

Hilo: dos vectores perpendiculares (producto punto 0) → en una base ortonormal las
coordenadas son simples sombras (productos punto) → Gram-Schmidt: restar sombras hasta
que nadie se estorbe → las matrices ortogonales (Q^T Q = I) son rotaciones y
reflexiones: mueven sin deformar (det ±1, longitudes intactas).

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Perpendicular es producto punto cero | u y v con `marca_angulo`; v gira hasta 90° y la cifra u·v baja a 0.0 | u ⟂ v con el ángulo recto marcado y u·v = 0.0 |
| 2 | Coordenadas sin resolver nada | base ortonormal q1, q2 (oblicua respecto a la canónica); el vector rojo; sus coordenadas = sombras sobre q1 y q2 (`proyeccion_dibujo`), cifras = v·q1, v·q2 | las dos sombras con sus cifras y el panel [v·q1; v·q2] |
| 3 | Gram-Schmidt: restar sombras | v1, v2, v3 en 3D? No: en 2D con dos vectores oblicuos: a v2 se le resta su sombra sobre q1 (flecha fantasma), queda el resto, se normaliza; `gram_schmidt` da los pasos | q1, q2 ortonormales sobre v1, v2 tenues; panel Q |
| 4 | Mover sin deformar | rejilla viva bajo una rotación y luego una reflexión: celdas siguen cuadradas; `es_ortogonal` ✓, det = 1.0 y −1.0; contra-ejemplo: cizalla deforma; cierre | cierre «Ortogonal: se mueve todo / y no se deforma nada.» |

### 5.2 La SVD: todo movimiento es girar, estirar, girar

Hilo: el círculo unidad bajo M es siempre una elipse → sus semiejes son σ1 u1, σ2 u2 →
M = U Σ V^T se ve: girar (V^T), estirar (Σ), girar (U) → los valores singulares miden
cuánto estira la matriz y su cociente (condición) cuánto amplifica errores → una imagen
es una matriz: quedarse con k valores singulares la comprime (`pixeles` +
`aproximacion_rango`).

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | El círculo se vuelve elipse | `circulo_unidad` + rejilla; `anim_matriz(M)` con Transform del círculo en elipse; los semiejes fucsia con σ1, σ2 calculados | elipse con semiejes y cifras σ1 = …, σ2 = … |
| 2 | Girar, estirar, girar | la misma rejilla hace V^T, luego Σ, luego U en tres pasos (anim_matriz con productos parciales); las tres matrices en panel | rejilla final = M, panel U Σ V^T |
| 3 | Cuánto estira: el número de condición | dos matrices: una bien condicionada (σ1/σ2 ≈ 1.3) y otra casi singular (≈ 25): el círculo se hace una aguja; un vector de error pequeño se amplifica | elipse aguja + cond = … |
| 4 | Una imagen es una matriz | `pixeles(imagen_sintetica(12))`; a su lado la aproximación rango 1, 2, 3, 5 con `Transform`; el error relativo baja (0.45 → 0.10); cierre | cierre «Toda matriz es girar, estirar, girar. / Quédate con lo que más estira.» |

### 5.3 Cadenas de Markov: el equilibrio que la matriz esconde

Hilo: un sistema con estados (un satélite: nominal / modo seguro / eclipse, o el clima)
y probabilidades de pasar de uno a otro → la matriz de transición (columnas suman 1)
lleva la distribución de hoy a la de mañana → iterar (`iterar`) converge al mismo
vector desde cualquier inicio → ese vector es el autovector de λ = 1
(`markov_estacionario`): el equilibrio estaba en la matriz (enlace con 4.2).

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Estados y probabilidades | 3 estados como nodos (`bloques`/círculos) con flechas rotuladas con probabilidades; la matriz T por columnas (columna = desde dónde) | diagrama + T con columnas coloreadas que suman 1 |
| 2 | La matriz mueve la distribución | `barras` de la distribución p0 = (1,0,0); T p0, T² p0… con Transform de barras; cifras | barras tras 1, 2, 5 pasos |
| 3 | Todo camino lleva al mismo sitio | dos inicios distintos (barras lado a lado) convergen a las mismas barras; en el plano 2D (dos estados) la trayectoria de p_k cae a un punto | barras iguales + trayectoria que converge |
| 4 | El equilibrio es un vector propio | T p* = p*: autovalor 1; `markov_estacionario` en panel; comparación con la iteración; cierre | cierre «El mañana es la matriz por el hoy. / El equilibrio, su vector propio.» |

### 6.1 Rotaciones en 3D: toda rotación tiene un eje

Hilo: en 3D una rotación es una matriz 3×3 ortogonal (det 1) → componer dos giros (alabeo,
cabeceo) da OTRO giro → Euler: todo giro tiene un eje que no se mueve = autovector de
λ = 1 (`eje_rotacion`) → ese eje y ese ángulo describen la actitud del satélite
(`satelite3` + `triada3`; `rot3_eje` para reconstruir).

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Girar en 3D es una matriz | `espacio3` + `triada3` bajo `rot3("z", 40)`: la tríada gira y el suelo también; matriz 3×3 por columnas | tríada girada + R por columnas |
| 2 | Dos giros hacen un giro | Rx luego Rz: tríada final; la matriz producto; sigue siendo ortogonal (det 1.0, longitudes 1) | tríada + R = Rz Rx |
| 3 | El eje que no se mueve | sobre la tríada girada, el eje fucsia (autovector λ = 1) quieto mientras un abanico de vectores gira alrededor; ángulo calculado | eje fucsia + «eje: (…), ángulo: … °» |
| 4 | La actitud del satélite | `satelite3` con `triada3` pasa de la actitud A a la B por UN giro alrededor del eje calculado (`rot3_eje` interpolado por ángulo); cierre | cierre «Toda rotación tiene un eje. / La actitud es un eje y un ángulo.» |

### 6.2 Las funciones también son vectores

Hilo: una función muestreada en n puntos es una lista = un vector (`muestrear` +
`barras`) → se suman y se escalan como vectores → producto punto de funciones = sumar
productos (área) → senos y cosenos son ORTOGONALES (`base_fourier`) → descomponer una
señal en esa base es proyectar: Fourier es un cambio de base (`coeficientes`).

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Una función es una lista | curva `grafica` → 12 barras (sus muestras) → el vector columna de 12 números (abreviado) | barras + «12 números = un vector de R^12» |
| 2 | Sumar y escalar funciones | dos curvas/barras se suman barra a barra; 0.5·f encoge cada barra | barras de f + g y de 0.5 f |
| 3 | Senos que no se estorban | barras de cos 1 y sin 1; su producto punto → 0.00; cos 1 consigo mismo → 1.00 (normalizado); panel con la base ortonormal | cifras ⟂ y panel |
| 4 | Fourier es un cambio de base | una señal (telemetría periódica) → sus coeficientes (barras por armónico) → reconstrucción con 1, 2, 3 armónicos (Transform); cierre | cierre «Una señal es un vector. / Fourier, una base que la entiende.» |

### 6.3 Sistemas dinámicos: la matriz que mueve el tiempo

Hilo: el estado de un sistema (posición, velocidad; o dos poblaciones; o temperatura de
dos módulos de un satélite) es un vector → un paso de tiempo es una matriz x_{k+1} = A x_k
(`iterar`, `trayectoria`) → los autovalores deciden el destino: |λ| < 1 encoge (estable),
> 1 estira (inestable), complejos giran (espiral) (`autos_complejos`) → recap de la
familia: el eje propio explica el tiempo.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | El estado es un vector | plano (posición, velocidad); un punto rojo; la matriz A lo mueve un paso; varios pasos: trayectoria | trayectoria de 8 pasos + A |
| 2 | Encoge, estira o gira | tres matrices en tres mini-planos: contractiva (espiral hacia dentro), expansiva (silla: una dirección estira), rotación pura (círculo); autovalores en cifra | los tres retratos con |λ| y ángulo |
| 3 | Las direcciones propias mandan | silla: rejilla viva bajo A con las dos direcciones fucsia; trayectorias que se acercan a una y huyen por la otra | retrato de fase con ejes propios |
| 4 | Repetir mil veces (recap de familia) | el sistema estable converge; fundido a la rejilla que se deforma, el paralelogramo, los ejes propios: la familia en 10 s; cierre | cierre «El tiempo es una matriz aplicada mil veces. / Sus ejes propios dicen el final.» |

### Tablero de la ampliación

| Lección | storyboard | clips | ql | repo/PR | qh | prod | narrada | mux |
|---------|-----------|-------|----|---------|----|------|---------|-----|
| 5.1 | ✔ | ✔ | ✔ 33.5/33.8/40.3/35.4 s | PR #36 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 5.2 | ✔ | ✔ | ✔ 37.9/37.7/43.5/41.1 s | PR #36 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 5.3 | ✔ | ✔ | ✔ 30.3/31.2/31.7/30.9 s | PR #36 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 6.1 | ✔ | ✔ | ✔ 37.3/36.6/40.2/42.5 s | PR #36 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 6.2 | ✔ | ✔ | ✔ 33.3/33.4/33.0/40.3 s | PR #36 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 6.3 | ✔ | ✔ | ✔ 33.7/38.5/38.1/40.5 s | PR #36 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |

## Cosecha de trampas (se llena durante la producción)

- `Transform` entre dos VGroup de distinta estructura (panel de 1 columna → 2 columnas, matriz → columnas, dos `tag_hud`) morphea glifos rotos durante la transición: usar FadeOut + FadeIn(shift) o el relevo secuencial de `Rotulos` (1.3, 4.3).
- Dos `Vector` que convergen al mismo punto bajo `anim_matriz` (singular, núcleo) necesitan `etiqueta_dir` distinto desde su creación y `bring_to_front` para el z-order; la librería no lo hace (3.1, 2.3).
- `Paralelogramo.area` y `Caja3.volumen` llevan SIGNO (son el det): si el pie habla de tamaño, pintar `abs()` (2.3).
- Rajdhani no tiene ⁻¹, φ ni λ; Space Mono no tiene superíndices: en `Text` escribir `P^-1` y dejar los símbolos a MathTex (4.2).
- Un `Vector` que va a cero se vuelve un Dot invisible: marcar el cero a mano (fantasma + punto + Flash) (4.1).
- Abanicos equiespaciados frente a giros de simetría alta (90°): el paso no debe dividir al ángulo o la imagen coincide con el original (4.1).
- `C_TENUE` == `C_EJE` (#94a0b0): una recta auxiliar gris se lee como un eje; usar trazos rojos/fantasma para "carriles" (4.1).
- La rejilla fija de `plano()`/`espacio3()` a 0.5–0.55 de opacidad es casi invisible en ql: donde la comparación viva/fija es el mensaje, subirla a ~0.95 desde el clip (3.3).
- `anim_matriz` toma el estado TOTAL desde la identidad: para encadenar movimientos se pasa el producto (D @ R), no el incremento (4.3).
- `satelite3()` solo trae `.eje_z`: para leer una actitud hace falta una tríada de `vector3` (3.3). Sugerencias de librería pendientes: `segmento(pl,a,b)` transformable, `opacidad_fija` en Plano, `.ejes` en satelite3, `span_recta(trazos=True)`.
- Ampliación (módulos 5–6): `svd()` devuelve reflexiones (det U = −1) la mitad de las veces y entonces el "girar" de `anim_matriz` pasa por un aplaste: elegir M con det U = det V = +1 (5.2 usa [[2,-0.5],[-1,1.5]]); `eje_rotacion` ya elige el signo del eje para que `rot3_eje` reproduzca R (corregido en la librería tras 6.1); la proyección oblicua de `espacio3` decide qué ángulos se leen: medir las direcciones proyectadas antes de escribir (6.1); una silla mal arrancada se lee como contracción: dar peso a la componente que crece y pasos suficientes (6.3); `Barras` se coloca por `.base`, no por `move_to`, y sus etiquetas chocan con barras negativas (6.2, 5.3); `Grafica` no expone su origen (alinear por `_ancla`) (6.2); el pie mostrado antes del plano queda DEBAJO de la rejilla: `bring_to_front(pie, titulo, hud)` tras `FadeIn(pl)` (6.2); `cierre_leccion(pie=None)` deja el pie anterior pegado (5.3); `Create` sobre un VGroup de rectas las escalona: dos `Create` en el mismo play (6.3).
- El muestreo equiespaciado de `--frames 8` cae fácil en relevos de pies o en el hueco del cierre: antes de declarar un hueco, extraer el frame exacto con ffmpeg (2.1, 3.2).
