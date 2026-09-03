# Plan de contenido: de la Academia a los cursos de video

Fecha: 2026-08-06 (ultima actualizacion: 2026-08-29). Responsable de
arquitectura: Fable (guiones, diseño de curso); agentes sonnet/opus escriben
el codigo de los clips y librerias.

## Idea central

Hay TRES formatos vivos (desde 2026-08-27). El original (cursos 1-13) desmenuza la Academy en
cursos de 8 clips; el segundo (familia "Aerodinamica", desde 2026-08-14) parte
de un documento maestro de curso autogestivo y hace **un proyecto por
leccion**, con un clip por subtema. El tercero (curso 26 "Fractales", desde
2026-08-27) es **vertical (9:16)**: nace del formato de los promos de redes,
no lleva subtitulos —la imagen enseña y el audio remata— y se entrega como
un solo video de intro + clips + cierre unidos. Lo que NO cambia entre los dos: el tema
oficial `code_brand`, la libreria por familia, el rango de 28-45 s por clip y
la validacion visual de frames.

`code-academy-platform` tiene 14 cursos y ~124 lecciones de texto. **No** se
traduce un curso de la Academia a un curso de video: se **desmenuza** — cada
curso de video toma un hilo conceptual (3-6 lecciones, a veces cruzando
cursos) y lo cuenta en 8 clips animados de 25-45 s con el tema oficial
CO.DE Academy (`code_brand.py`).

## Cursos de video existentes (ya en produccion)

Los cuatro primeros son anteriores al plan (sus scripts solo viven en la DB
de produccion). Del 5 al 12 son la cola original del desmenuzado, cerrada el
2026-08-07: los 8 estan versionados en git, renderizados en `qh` en el VPS,
narrados con TTS y con su video final en `exports/<slug>/curso_narrado.mp4`.

| # | Curso | Origen | Libreria | Estado |
|---|-------|--------|----------|--------|
| 1 | Fractales: la belleza de los numeros complejos | original | — (solo en DB) | publicado |
| 2 | Satelites e IA: la red que aprende a gobernarse | original | — (solo en DB) | publicado |
| 3 | Mecanica orbital: el ballet de la gravedad | Academy: Mecanica Orbital L1-L9 | — (solo en DB) | publicado |
| 4 | Señales y espectro: de Fourier al enlace satelital | Academy: Señales y sistemas + SDR | — (solo en DB) | publicado |
| 5 | Redes neuronales: la maquina que aprende | IA L2-L6 (gradiente, regresion, logistica, redes, backprop, sobreajuste) | `aprendizaje.py` | publicado (PR #2) |
| 6 | De la palabra al vector: embeddings y atencion | IA L8-L9 (NLP, embeddings, transformers) | `atencion.py` | publicado (PR #2) |
| 7 | Agentes de IA: maquinas que operan el mundo | IA L10 + IA Agentica L1, L2, L5-L7 | `agentes.py` | publicado (PR #3) |
| 8 | SDR: la radio hecha software | SDR L3-L6 (IQ, FFT, waterfall, demodulacion) | `radio.py` | publicado (PR #4) |
| 9 | Apuntar a un satelite: el arte del seguimiento | APT L1-L4, L6 (Az/El, Doppler, PID) | `apuntado.py` (+ reusa `satelites.py`) | publicado (PR #5) |
| 10 | El espectro: la guerra invisible por las ondas | Espectro L1-L4, L6 (bandas, lluvia, UIT, NGSO-GSO) | `espectro.py` | publicado (PR #6) |
| 11 | Control: domar sistemas que se resisten | Señales y sistemas L10-L12, L16 + APT L6-L7 | `control.py` | publicado (PR #7) |
| 12 | Materiales que van al espacio | Materiales M1-M5 + Elasticidad M1 | `materia.py` | publicado (PR #8) |
| 13 | Cerrar el enlace: la cuenta en decibelios | Redes satelitales M2 (FSPL, PIRE, C/N0, G/T) + M7 (Shannon, MODCOD, ACM) | `enlace.py` | publicado (PR #9) |
| 14 | Matematicas en la naturaleza | original (divulgacion pura, heredero visual de Fractales) | `naturaleza.py` | publicado (PR #11) |
| 15 | Caos: el orden escondido | original (divulgacion pura, tercer titulo de la linea visual) | `caos.py` | publicado (PR #12) |
| 16 | Relatividad y el GPS | original (divulgacion pura, fisica aplicada a ingenieria) | `relatividad.py` | publicado (PR #13) |
| 17 | Tsiolkovsky: la tirania del cohete | original (divulgacion pura, astronautica) | `cohete.py` | publicado (PR #15) |
| 18 | Sistemas distribuidos: la nube por dentro | original (divulgacion, computo distribuido) | `distribuido.py` | publicado (PR #16) |
| 19 | Criptografia: el arte de guardar secretos | original (divulgacion, seguridad/telecom) | `cripto.py` | publicado (PR #19); primer curso con intro/cierre de marca en el mux |
| 20 | Metrologia optica (familia, 9 lecciones) | original (divulgacion, optica y enlaces opticos entre satelites) | `optica.py` + `isl.py` | publicado (PR #21): 9 lecciones narradas y muxeadas con intro/cierre |
| 21 | Teoria de la informacion: los bits de Shannon | original (divulgacion, telecom; puente con Criptografia y con Cerrar el enlace) | `informacion.py` | publicado (PR #20): qh en prod, narrado y muxeado con intro/cierre |
| 22 | Algebra lineal (familia, 18 lecciones) | original (divulgacion, muy visual: la rejilla que se deforma; ejemplos aeroespaciales donde salen solos) | `algebra_lineal.py` | publicado (PR #35 + #36): 18 lecciones, 72 qh en prod, narradas y muxeadas con intro/cierre (2026-08-19) |
| 23 | Calculo vectorial (familia, 12 lecciones) | original (divulgacion, muy visual: el espacio que fluye; secuela de Algebra lineal, cierra en Maxwell) | `calculo_vectorial.py` (sobre `algebra_lineal.py`) | publicado (PR #43): 12 lecciones, 48 qh en prod, narradas y muxeadas — PRIMER curso con el intro/cierre SONOROS (2026-08-20) |
| 24 | Comunicaciones digitales (familia, 18 lecciones) | original (divulgacion espacial/satelital: de la sonda muestreada al enlace cognitivo con IA) | `comunicaciones.py` | publicado (PR #45): 18 lecciones, 72 qh en prod, narradas y muxeadas con la marca sonora (2026-08-21) |
| 25 | Protocolos de Internet (familia, 24 lecciones) | original (divulgacion: la capa de paquetes; del cable de cobre a Marte, cierra en DTN/CCSDS) | `protocolos.py` | **en produccion por lotes** (plan completo en `curso-23-protocolos-internet.md`; 4 lotes de 6 lecciones) |
| 26 | Fractales: la forma del infinito (**VERTICAL**, 14 clips + intro y cierre) | original (releva al curso 1, que era horizontal y solo miraba el plano complejo) | `fractales.py` ampliada | **primer curso en 9:16**: sin subtitulos, voz escrita a mano y cama de SFX; plan en `curso-26-fractales-vertical.md` |
| 27 | Procesamiento digital de señales (familia, 30 lecciones) | original (la capa DEBAJO de Comunicaciones digitales: que se le hace a los numeros y cuanto cuesta hacerlo en el aparato) | `dsp.py` (2617 lineas, 11 piezas) | publicado (PRs #54, #55, #56, #57 y #58): **el curso mas extenso de la coleccion**, 30 lecciones y 120 clips en 5 lotes, con 120/120 qh en produccion. **Primer curso horizontal SIN SUBTITULOS** (formato mudo: la pantalla solo pone la cosa y su cifra medida, y un guardian en el style_block aborta el render si un rotulo se convierte en frase) |
| 28 | Satelites: la maquina que no se cae (**VERTICAL**, 14 clips + intro y cierre) | original (releva al curso 2 "Satelites e IA" y a la mitad divulgativa del 3, ambos horizontales y solo en la DB) | `satelites.py` ampliada | **TERMINADO** (2026-08-28): segundo curso en 9:16, 16 piezas, 7 min 30 s, narrado y muxeado; plan en `curso-28-satelites-vertical.md` |
| 29 | Emergencia: reglas simples, mundos enteros (**VERTICAL**, 14 clips + intro y cierre) | original (experimental: cada clip parte de 2-3 reglas que caben en una etiqueta y esas reglas producen un mundo entero; el FOTOGRAMA ENTERO es una simulacion numpy calculada en el render) | **`emergencia/`** (paquete nuevo: nucleo `Pelicula` + 13 simuladores) | **terminado 2026-08-28** (PR #63, sin mergear): 8 min 23 s, 16 piezas en 1080x1920@60, cada una sonorizada y subible por separado a Instagram. Plan en `curso-29-emergencia-vertical.md` |
| 30 | Sistemas ATP: apuntamiento y seguimiento de satelites (familia, 9 lecciones) | Academy: curso `sistemas-apt` (9 lecciones), desmenuzado a la capa de INGENIERIA | `atp.py` (sobre el sustrato de `apuntado.py` del curso 9) | **publicado (PR #67)**: 9 lecciones, 36 clips y 36/36 `qh` en produccion, 20.4 min. Horizontal SIN SUBTITULOS. Es la capa de ingenieria de lo que el curso 9 conto como divulgacion: presupuesto de error medido, keyhole cuantificado, LQR y Monte Carlo. Plan en `curso-30-sistemas-atp.md` |
| 31 | ESP32: el chip por dentro (**VERTICAL**, 14 clips + intro y cierre) | original (divulgacion de hardware embebido: del silicio a lo que el chip hace con el mundo) | `lienzo.py` (estilo nuevo) + `esp32.py` | **entregado 2026-09-02**: cuarto curso en 9:16 y **primero con el estilo LIENZO** — superficie lisa azul marino, una cosa y un dato por fotograma, cuatro carriles de un solo ocupante, sin subtitulos y sin HUD. 16 piezas, 8 min 27 s en 1080x1920@60, costuras 0.0000/255. **Falta la voz**: Vertex denegado por facturacion de GCP (403 dunning), no por el curso. Plan en `curso-31-esp32-vertical.md` |
| 32 | Transformadas: la que vuelve facil lo dificil (**VERTICAL**, 18 transformadas + intro y cierre) | original (una transformada por pieza, cada una contada por lo que VUELVE FACIL, no por su formula) | `transformadas.py` (sonda de **91 invariantes**) + `lienzo.py` ampliada | **entregado 2026-09-02**: quinto curso en 9:16, segundo con estilo LIENZO y **el primero MUDO por diseño** — se publica sin pista de audio para ponerle musica encima, asi que la animacion explica sola: portada con tesis de <=5 palabras, UN verbo visual y UNA cifra. 20 piezas, 11.05 min en 1080x1920@60, costuras 0.0000/255. Plan en `curso-32-transformadas-vertical.md` |
| 33 | Señales y sistemas (**VERTICAL**, 18 piezas + intro y cierre) | original (ocupa la capa de los SISTEMAS: que le hace un sistema a una señal; cita las transformadas del 32 sin volver a explicarlas) | `sistemas.py` (sonda de **51 invariantes**) | **en produccion**: plan y libreria cerrados, piezas por escribir. Plan en `curso-33-senales-y-sistemas.md` |

Los storyboards de los cursos 5-12 estan en `curso-01-*.md` .. `curso-08-*.md`
(la numeracion del archivo es la prioridad en la cola original, no el # de
esta tabla); del 13 en adelante, el numero de archivo ya es correlativo
(`curso-09-enlace.md` es el curso 13; `curso-11-matematicas-naturaleza.md`
es el curso 14, `curso-12-caos.md` el 15, `curso-13-relatividad-gps.md`
el 16, `curso-14-tsiolkovsky.md` el 17, `curso-15-distribuidos.md` el
18, `curso-17-criptografia.md` el 19 y `curso-19-teoria-informacion.md`
el 21 — el `curso-10` lo ocupa la
familia Aerodinamica y el `curso-16` la familia Electromagnetismo, que
tienen otro formato).

## Familia "Aerodinamica" (2026-08-14, formato nuevo)

Encargo distinto a todo lo anterior: la fuente no es la Academy sino un
**documento maestro de curso autogestivo** (Aerodinamica II, 4 modulos, 20
lecciones, 83 subtemas), y el cliente pide reciclarlo, asi que la familia se
titula **Aerodinamica** a secas, sin el "II".

Cambia la granularidad: **un proyecto de ManimStudio = una LECCION**, y cada
clip = un subtema. Son 4 clips de 33-45 s por proyecto (~2.5-3 min), no los 8
de los cursos 1-13. Los 20 proyectos comparten una sola libreria
(`aerodinamica.py`) y un solo `style_block` (el molde: entre dos lecciones
solo cambia su bloque `# --- Numeros de la leccion ---`).

Storyboard y contrato de la libreria: `curso-10-aerodinamica.md`.

| Leccion | Proyecto | Clips | Estado |
|---------|----------|-------|--------|
| 1.1 | El numero de Mach y los regimenes de vuelo | 4 | versionado, validado en local |
| 1.2 | Repaso de termodinamica aplicada | 4 | versionado, validado en local |
| 1.3 | La velocidad del sonido | 4 | versionado, validado en local |
| 1.4 | Ecuaciones de conservacion | 4 | versionado, validado en local |
| 1.5 | Propiedades de estancamiento e isentropicas | 4 | versionado, validado en local |
| 2.1 | Naturaleza fisica de la onda de choque | 4 | versionado, validado en local |
| 2.2 | Relaciones de la onda de choque normal | 4 | versionado, validado en local |
| 2.3 | Medicion de velocidad en flujo compresible | 4 | versionado, validado en local |
| 2.4 | Flujo cuasi-unidimensional en conductos | 4 | versionado, validado en local |
| 2.5 | Toberas convergentes y De Laval | 5 | versionado, validado en local |
| 3.1 | Ondas de choque oblicuas | 4 | versionado, validado en local |
| 3.2 | La relacion theta-beta-M | 4 | versionado, validado en local |
| 3.3 | Reflexion e interaccion de ondas | 4 | versionado, validado en local |
| 3.4 | Expansion de Prandtl-Meyer | 4 | versionado, validado en local |
| 3.5 | Teoria de choque-expansion | 5 | versionado, validado en local |
| 4.1 | Potencial de perturbacion linealizado | 4 | versionado, validado en local |
| 4.2 | Correcciones de compresibilidad subsonica | 4 | versionado, validado en local |
| 4.3 | Mach critico y divergencia del arrastre | 4 | versionado, validado en local |
| 4.4 | El regimen transonico | 4 | versionado, validado en local |
| 4.5 | Teoria linealizada y panorama hipersonico | 5 | versionado, validado en local |

**EL CURSO ESTA COMPLETO**: 20 lecciones y 83 clips, uno por subtema del
documento maestro. Pendiente: `subir_curso.py` contra produccion, renders
`qh`, narracion TTS y mux de los 20 proyectos.

## Familia "Electromagnetismo" (2026-08-14, mismo formato que Aerodinamica)

Segunda familia con el formato de lecciones: **un proyecto = una leccion de
4 clips**. Original (no viene de un documento maestro): 4 modulos x 3
lecciones = 12 proyectos, 48 clips, con TODOS los ejemplos apuntando a
telecomunicaciones y satelites. El arco: *de la carga de Coulomb al bit que
baja del satelite*. Una sola libreria (`electromagnetismo.py`, numeros
validados contra CODATA / ITU-R P.838-3 / WR-90 / orbita de Clarke) y un
solo style_block molde.

Storyboard y contrato de la libreria: `curso-16-electromagnetismo.md`.

| Leccion | Proyecto | Clips | Estado |
|---------|----------|-------|--------|
| 1.1 | La carga y el campo electrico | 4 | publicado: qh en prod, narrado y muxeado |
| 1.2 | La corriente y el campo magnetico | 4 | publicado: qh en prod, narrado y muxeado |
| 1.3 | La fuerza de Lorentz | 4 | publicado: qh en prod, narrado y muxeado |
| 2.1 | La induccion de Faraday | 4 | publicado: qh en prod, narrado y muxeado |
| 2.2 | Las ecuaciones de Maxwell | 4 | publicado: qh en prod, narrado y muxeado |
| 2.3 | La onda electromagnetica | 4 | publicado: qh en prod, narrado y muxeado |
| 3.1 | Las lineas de transmision | 4 | publicado: qh en prod, narrado y muxeado |
| 3.2 | La reflexion y la onda estacionaria | 4 | publicado: qh en prod, narrado y muxeado |
| 3.3 | Las antenas | 4 | publicado: qh en prod, narrado y muxeado |
| 4.1 | La ionosfera | 4 | publicado: qh en prod, narrado y muxeado |
| 4.2 | El enlace con el satelite | 4 | publicado: qh en prod, narrado y muxeado |
| 4.3 | El clima, el ruido y el margen | 4 | publicado: qh en prod, narrado y muxeado |

## Familia "Metrologia optica" (2026-08-15, formato de lecciones)

Tercera familia (curso 20 del plan): **un proyecto = una leccion de 4
clips**, 3 modulos x 3 lecciones = 9 proyectos, 36 clips. Original; el
angulo es *la luz como regla*: modulo 1 teoria basica (onda, fase,
interferencia, difraccion), modulo 2 tecnicas de medir con luz (tiempo de
vuelo, franjas, frente de onda), modulo 3 los **enlaces opticos entre
satelites (ISL)**: apuntar/adquirir/seguir y satelites que se miden entre
si (GRACE-FO, LISA). Dos librerias (`optica.py` modulos 1-2, `isl.py`
modulo 3) y un style_block molde. Storyboard: `curso-18-metrologia-optica.md`.

| Leccion | Proyecto | Clips | Estado |
|---------|----------|-------|--------|
| 1.1 | La luz como regla | 4 | publicado: qh en prod, narrado y muxeado (PR #21) |
| 1.2 | La interferencia: contar franjas | 4 | publicado: qh en prod, narrado y muxeado (PR #21) |
| 1.3 | La difraccion: el limite de la regla | 4 | publicado: qh en prod, narrado y muxeado (PR #21) |
| 2.1 | Medir con el tiempo de vuelo | 4 | publicado: qh en prod, narrado y muxeado (PR #21) |
| 2.2 | Medir la forma con franjas | 4 | publicado: qh en prod, narrado y muxeado (PR #21) |
| 2.3 | Medir el frente de onda | 4 | publicado: qh en prod, narrado y muxeado (PR #21) |
| 3.1 | El enlace optico entre satelites | 4 | publicado: qh en prod, narrado y muxeado (PR #21) |
| 3.2 | Apuntar, adquirir, seguir | 4 | publicado: qh en prod, narrado y muxeado (PR #21) |
| 3.3 | Satelites que se miden entre si | 4 | publicado: qh en prod, narrado y muxeado (PR #21) |

## Familia "Comunicaciones digitales" (2026-08-21, curso 24)

18 proyectos `Comunicaciones digitales · N.M <titulo>` (6 modulos x 3
lecciones, 72 clips): la capa de simbolos del enlace — muestreo,
constelaciones, canal espacial, codigos con memoria, sistemas
adaptativos y la IA en el enlace — con ejemplos de mayoria espacial
(cubesats, DSN, Voyager, DVB-S2, LEO, Marte) y la fibra como excepcion
terrestre declarada. Plan, storyboards, tablero e hitos:
`curso-22-comunicaciones-digitales.md`. Libreria `comunicaciones.py`
(validada 63/63 en contenedor; LDPC = Steiner S(2,3,9), IA en numpy puro
con semillas). Produccion con 17 subagentes + molde propio; toda cifra en
pantalla medida.

## Familia "Calculo vectorial" (2026-08-20, formato de lecciones)

Secuela natural de Algebra lineal: *el espacio que fluye*. 4 modulos x 3
lecciones = 12 proyectos / 48 clips. Los operadores se presentan primero
como movimiento (la ruedecita, la cajita contable, la particula que sigue
la corriente) y los teoremas se COMPRUEBAN midiendo los dos lados en
pantalla (Green 8.00 = 8.00, Stokes 4.0 = 4.0, divergencia 12.29 = 12.29,
Gauss 6.28/0.00, c = 299 792 458 m/s de mu0 y eps0). Libreria
`calculo_vectorial.py` sobre el sustrato de `algebra_lineal.py`.
Storyboard, contrato y tablero: `curso-21-calculo-vectorial.md`.
Es el PRIMER curso muxeado con el intro/cierre sonoros de la marca
(picos -6 dBFS medidos en el curso_narrado.mp4 final).

## Familia "Algebra lineal" (2026-08-19, formato de lecciones)

Cuarta familia (curso 22 del plan): **un proyecto = una leccion de 4
clips**, 6 modulos x 3 lecciones = 18 proyectos, 72 clips (la tarde del
2026-08-19 el dueno pidio ampliar: modulos 5 y 6). Original; el
angulo es *cada idea se VE moverse*: rejilla viva azul que se deforma sobre
la fija gris, la matriz por columnas de colores (a donde van i y j), el
paralelogramo del determinante, la nube que se endereza con sus ejes
principales. Ejemplos aeroespaciales donde salen solos (actitud del
satelite, marco cuerpo/inercial, telemetria con deriva). Libreria
`algebra_lineal.py` y style_block molde (leccion 1.1). Planeada por Fable,
producida por 11 subagentes Sonnet/Opus (una leccion por agente) y
validada frame a frame. Storyboard: `curso-20-algebra-lineal.md`.

| Leccion | Proyecto | Clips | Estado |
|---------|----------|-------|--------|
| 1.1 | El vector: flecha, lista y movimiento | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 1.2 | Combinaciones lineales y span | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 1.3 | Dependencia lineal, base y dimension | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 2.1 | La matriz es un movimiento | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 2.2 | Componer movimientos: el producto | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 2.3 | El determinante: area y orientacion | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 3.1 | Sistemas Ax = b y la inversa | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 3.2 | Rango, nucleo e imagen | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 3.3 | Cambio de base: el mismo vector, otro idioma | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 4.1 | Vectores propios: los que no giran | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 4.2 | Diagonalizar y las potencias | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 4.3 | Proyeccion, minimos cuadrados y ejes principales | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 5.1 | Ortogonalidad: bases que no se estorban | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 5.2 | La SVD: todo movimiento es girar, estirar, girar | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 5.3 | Cadenas de Markov: el equilibrio que la matriz esconde | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 6.1 | Rotaciones en 3D: toda rotacion tiene un eje | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 6.2 | Las funciones tambien son vectores | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |
| 6.3 | Sistemas dinamicos: la matriz que mueve el tiempo | 4 | publicado: qh en prod, narrado y muxeado (PR #35/#36) |

## Marca: intro y cierre para posproduccion (2026-08-14)

Proyecto especial **`marca-intro-y-cierre`** (no es una leccion): dos clips
de identidad que se unen en POSPRODUCCION al inicio y al final de cada
curso NUEVO. Los cursos ya publicados no se re-renderizan. Sin narracion;
ambos clips arrancan y terminan con >=0.5 s de fondo limpio `#05070a`
para que el empalme (`intro.mp4 + clips narrados + cierre.mp4`) sea un
concat invisible. El aviso de duracion 28-45 s de `render_local.py` NO
aplica a este proyecto. Diseño: `marca-intro-y-cierre.md`.

| Clip | Pieza | Duracion | Estado |
|------|-------|----------|--------|
| 1 | Intro "Encendido" | 10.5 s | publicado: qh en prod; `exports/marca-intro-y-cierre/intro.mp4` |
| 2 | Cierre "Despedida" | 9.0 s | publicado: qh en prod; `exports/marca-intro-y-cierre/cierre.mp4` |

## Cola de cursos nuevos (desmenuzado de la Academy)

La cola original esta agotada. Los proximos cursos se eligen tema a tema.

| Prio | Curso de video (8 clips) | Lecciones fuente (Academy) | Libreria nueva | Estado |
|------|--------------------------|----------------------------|----------------|--------|
| — | Criptografia (curso 19) | — | `cripto.py` | publicado (PR #19) |
| — | Teoria de la informacion: los bits de Shannon (curso 21) | original (divulgacion, telecom; puente natural con Criptografia y con "Cerrar el enlace") | `informacion.py` | publicado (PR #20; storyboard `curso-19-teoria-informacion.md`) |

Criterio de prioridad: (1) riqueza visual con primitivas existentes o
factibles, (2) tamaño de audiencia, (3) actualidad del tema, (4) no
canibalizar cursos de video ya publicados.

## Pipeline por curso

1. **Diseño (Fable)**: storyboard clip a clip + `style_block` + contrato de
   la libreria nueva → `docs/plan_contenido/curso-NN-*.md`.
2. **Codigo (agentes)**: libreria en `studio/content/manim_extensions/`
   (opus) y clips en `studio/content/cursos/<slug>/clips/` (sonnet), todo
   **versionado en git** — a diferencia de los 4 cursos previos, cuyos
   scripts solo viven en la DB de produccion.
3. **Validacion local**: `studio/tools/render_local.py <curso> --todos`
   compone el script igual que el runner (style_block + clip + identidad) y
   lo renderiza en `ql` en Docker, dejando video y frames PNG en
   `render_jobs/validacion/<slug>/`. Revision visual obligatoria de esos
   frames (regla dura: **nada encimado**; los textos se relevan con
   `Rotulos`) y dos revisores de vision por curso antes de dar por bueno.
4. **Subida**: `studio/tools/subir_curso.py` sincroniza el directorio del
   curso con la DB del backend (proyecto + clips) usando los modulos de
   `app/` — mismas validaciones que la API.
5. **Produccion (VPS)**: pull, subir_curso, renders `qh` por la cola del
   Studio, narracion TTS (`studio/tools/guiones.py`), export + mux.

### Restricciones operativas (aprendidas en los 8 cursos de la cola)

- **Duracion de clip: 28-45 s**, tope duro. `render_local.py` avisa cuando
  un clip se sale del rango.
- **Pies de al menos 5 s**, y el pie cambia **antes** del transform que
  ilustra — nunca despues.
- **El VPS no tiene `ffmpeg`**: el mux final (clips + voz →
  `exports/<slug>/curso_narrado.mp4`) se hace en local, con los renders `qh`
  bajados del VPS.
- Imagen Docker local: `codeaerospace_contenido-manim` (no
  `manimstudio-render`, que es otra cosa).
- Render `qh` ≈ frames/2.5 s (Cairo single-thread); el timeout del VPS es
  1200 s por job.

## Arrancar un curso nuevo

1. Elegir el hilo conceptual y las lecciones fuente; anotarlo en la cola de
   arriba con su libreria nueva.
2. Escribir el storyboard en `docs/plan_contenido/curso-NN-<tema>.md`
   siguiendo el formato de los ocho existentes (paleta con nombres `C_*`,
   clip a clip: intencion, visual, rotulos y pies literales, final_state).
3. Rama `curso/<tema>`, libreria en `manim_extensions/`, curso en
   `studio/content/cursos/<slug>/` (`curso.json` + `style_block.py` +
   `clips/NN-*.py`, una clase `ClipN(Scene)` por archivo).
4. `render_local.py --todos --frames 8` → revision visual → fixes.
5. `cd studio/backend && venv/bin/pytest -q` (los tests del Studio deben
   seguir en verde) → PR → merge → deploy y narracion en el VPS.

## Estructura versionada de un curso

```
studio/content/cursos/<slug>/
  curso.json        # name, description, quality, lista de clips (titulo,
                    # escena, archivo, final_state)
  style_block.py    # el bloque de estilo completo del proyecto
  clips/NN-slug.py  # un archivo por clip: SOLO la clase ClipN(Scene)
```

## Reglas anti-encimamiento (prioridad: el espectador)

- Todo texto narrativo pasa por `Rotulos` (zonas `arriba`/`abajo`): el
  rotulo nuevo desvanece al anterior de su zona; jamas coexisten dos.
- `pie_curso` y `formula_pie` comparten zona — nunca se suman.
- Titulos y pies se auto-encogen si exceden el ancho util del frame.
- Mobiliario de figura (tags de eje, llaves) se coloca respecto a los ejes
  con `buff` explicito y se retira antes de introducir el siguiente.
- Validacion visual obligatoria de frames antes de dar un clip por bueno.
