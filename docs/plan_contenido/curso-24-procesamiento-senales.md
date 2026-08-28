# Curso 27 — Procesamiento digital de señales (familia, 30 lecciones)

> **Archivo `curso-24`** por la numeración correlativa de `docs/plan_contenido/`;
> el **curso es el 27** de `PLAN.md` (26 = Fractales vertical).

## 0. Cómo reanudar

- Frase del dueño: **«continuamos con el curso de procesamiento de señales»**.
- Worktree `~/Documentos/github/codeaerospace_contenido-dsp`, rama
  `curso/procesamiento-senales` (creada desde `origin/main` a893fbf).
- **Todo el estado vive en este archivo** (§12 Tablero). La conversación no
  guarda nada.
- Encargo literal (2026-08-27): *«curso completo en horizontal, esta vez no
  incluyas subtítulos, todo lo demás igual, llévalo hasta el VPS. Procesamiento
  Digital de Señales, sumamente completo, el más completo hasta ahora.»*

## 1. Formato

Familia. **10 módulos × 3 lecciones = 30 proyectos**, 4 clips por lección =
**120 clips**. Es el curso más extenso de la colección (el anterior, Protocolos
de Internet, tiene 24 lecciones / 96 clips).

- Nombre de proyecto: `Procesamiento de señales · N.M <título>`
  (el nombre es la clave de emparejamiento de `subir_curso.py`: no se toca
  después de subir).
- Slug: `procesamiento-senales-N-M-<tema>`.
- Librería única: `studio/content/manim_extensions/dsp.py`.
- `style_block.py` idéntico en las 30 lecciones salvo su bloque
  `# --- Numeros de la leccion ---`.

## 2. LA REGLA NUEVA: formato mudo (sin subtítulos)

Este curso **elimina el pie narrativo** (`pie_curso`) que llevaban los 25
cursos horizontales anteriores. La palabra la pone la **voz**; la pantalla
solo pone la **cosa** y su **cifra**.

**Permitido en pantalla**

| Elemento | Límite | Color |
|---|---|---|
| Título del clip (arriba) | ≤ 6 palabras, sin verbo conjugado si se puede | tinta |
| Etiqueta HUD del módulo (UL) | `MODULO NN` | muted |
| Rótulo de mobiliario (ejes, `x[n]`, `h[n]`, `dB`, `Hz`) | ≤ 3 palabras | muted / color de su papel |
| **Cifra medida** con su etiqueta | ≤ 5 palabras **contando** la cifra | cian |
| Fórmula `MathTex` | una línea | cian |
| Dato NO calculado aquí | ≤ 5 palabras + marca `dato` | gris |
| Cierre del clip 4 | 2 líneas | blanca + cian |

**Prohibido**: cualquier renglón de prosa. Nada de «Si preguntamos lo bastante
seguido, la lista guarda TODA la curva». Esa frase es de la narración.

**Se hace cumplir con un guardián, no con disciplina**: `style_block.py`
define `_vigilar(texto, maximo)` y **aborta el render** si un rótulo se pasa de
palabras. `pie_curso` **no existe** en este style_block: un agente que lo copie
de otra familia rompe en el primer render.

**Consecuencia de ritmo** (importante para los 28–45 s): el tiempo que antes
sostenía la lectura del pie (≥ 5 s) ahora lo sostiene la **animación**. Los
clips llevan más `Create`/`Transform`/updaters y menos `wait` largo. La zona
inferior es el **carril de la cifra**: `cifra_pie()` y `formula_pie()`
comparten zona y nunca se suman.

## 3. Ángulo editorial

**Una señal es una lista de números; un filtro es la máquina que la reescribe.**
El curso baja una capa por debajo de *Comunicaciones digitales*: allí la
pregunta era «cómo cruzo el vacío con estos bits»; aquí es «qué le hago a los
números una vez que los tengo, y cuánto cuesta hacerlo en el aparato».

Arco: empieza en un **acelerómetro de un lanzador** (una tensión que hay que
convertir en lista) y termina en un **filtro aprendido** que hace el trabajo de
un banco de filtros, pasando por el plano Z, la aritmética de 16 bits de un DSP
de vuelo y el espectrograma de un sismómetro marciano.

## 4. Público y qué asume

Asume: números complejos y fasores (Electromagnetismo 2.3), base ortogonal y
cambio de base (Álgebra lineal 3.3 y 6.2), dB y ruido (Cerrar el enlace), y que
el alias **existe** (Comunicaciones digitales 1.1).

## 5. Qué NO pisa

| Curso vecino | Qué se queda allí | Qué hace este |
|---|---|---|
| 24 Comunicaciones digitales 1.1–1.3 | muestreo/cuantización **para transmitir**; pulsos, ISI, espectro de la modulación | el **espectro que se repite** (réplicas), el ruido de cuantizar como algo que se **da forma**, y la reconstrucción con su reloj |
| 24 Comunicaciones digitales 3.3 | sincronía de portadora y símbolo del receptor | 9.3 hace el **PLL digital como lazo** (NCO, ganancias, ruido de fase medido) |
| 8 SDR | qué es IQ y para qué sirve la cascada del waterfall | 3.1–3.3 explican la **maquinaria** de la DFT y 10.1 la señal analítica |
| 11 Control | realimentación, PID, estabilidad en el plano s | 4.1–4.2 usan el plano **Z** para filtros; 6.2 la estabilidad **numérica**, no la de lazo |
| 21 Teoría de la información | qué es un bit, entropía, capacidad | 1.2 usa bits como **niveles**, no como información |
| 10 El espectro | bandas, regulación, interferencia | 3.3 y 9.1 miden espectros; nunca reparten frecuencias |
| 22 Álgebra lineal 6.2 | funciones como vectores, base ortogonal | 3.1 **usa** el resultado: la DFT es un cambio de base |

## 6. Principio visual no negociable

1. **La secuencia se dibuja con tallos** (stem), nunca con una curva continua.
   La curva azul es el mundo; los tallos ámbar son los números. Si algo es
   discreto, se ve discreto.
2. **La convolución se ve deslizar**: `h` volteada avanzando muestra a muestra
   sobre `x`, con la ventana de productos encendida y la salida creciendo.
3. **El plano Z se ve como plano**: círculo unidad, ceros (o) y polos (×), y el
   punto que recorre el círculo mientras la respuesta se dibuja al lado. Es la
   imagen firma de esta familia.
4. **El espectro se repite**: las réplicas son piezas de pleno derecho, con su
   banda de guarda medida.
5. **La aritmética se ve romper**: el desbordamiento, el ciclo límite y el polo
   que se mueve al cuantizar el coeficiente son animaciones, no afirmaciones.
6. **Toda cifra en pantalla la calcula `dsp.py`** con `default_rng(semilla)` o
   `scipy.signal`, y se mide **sobre lo dibujado**.
7. Nada encimado. Nada de prosa (§2).

## 7. Mapa de las 30 lecciones

| Lección | Proyecto | Los 4 clips |
|---|---|---|
| 1.1 | Muestrear: el espectro se repite | la secuencia · réplicas · solape · guarda y antialias |
| 1.2 | Cuantizar: el ruido que fabricamos | la escalera · 6 dB por bit · dither · noise shaping |
| 1.3 | Volver al mundo | ZOH y droop · la sinc · sobremuestreo · jitter del reloj |
| 2.1 | LTI: el impulso lo dice todo | la caja y h[n] · linealidad · invarianza · suma de deltas |
| 2.2 | Convolución: deslizar y sumar | el deslizamiento · longitud y transitorio · BIBO · el coste |
| 2.3 | Correlación: hallar lo conocido | correlar vs convolucionar · filtro adaptado · resolución · el correlador GNSS |
| 3.1 | La DFT: proyectar sobre giros | el giro · la proyección · la matriz W · simetría y bins |
| 3.2 | La FFT: partir en dos | pares e impares · la mariposa · N log N medido · el orden bit-reverso |
| 3.3 | Fugas, ventanas, resolución | la fuga · ventanas · ENBW y scalloping · zero-padding no es resolución |
| 4.1 | La transformada Z | de la suma a z · polos y ceros · la ROC · estabilidad |
| 4.2 | Del plano a la respuesta | el punto en el círculo · vectores a polos y ceros · mover un polo · el filtro que se afila |
| 4.3 | Fase, retardo, mínima fase | fase lineal · retardo de grupo · fase mínima vs máxima · el eco que se puede deshacer |
| 5.1 | FIR por ventanas | truncar el ideal · Gibbs · la ventana que ablanda · el compromiso medido |
| 5.2 | Equirriple | el error que sobra · el intercambio de Remez · alternancia · orden vs rizado |
| 5.3 | Cuánto cuesta un FIR | orden y retardo · simetría: mitad de multiplicaciones · forma directa · el interpolador de media banda |
| 6.1 | IIR: traer el analógico | polos de Butterworth · la bilineal y su warping · Chebyshev y elíptico · IIR vs FIR medido |
| 6.2 | Biquads en cascada | forma directa que revienta · secciones de 2º orden · orden de las secciones · escalado |
| 6.3 | Peine, resonador, notch | el peine y sus dientes · el resonador · el notch de 400 Hz · Goertzel |
| 7.1 | Punto fijo Q15 | el formato · saturar vs envolver · escalado de la entrada · el margen medido |
| 7.2 | Coeficientes cuantizados | el polo que se mueve · la respuesta que se deforma · ciclo límite · la cura (cascada) |
| 7.3 | El presupuesto de tiempo real | MACs por segundo · bloques y latencia · convolución rápida por FFT · el cruce medido |
| 8.1 | Diezmar e interpolar | diezmar y su alias · el filtro antes · interpolar con ceros · las imágenes |
| 8.2 | Polifase y CIC | la mitad que se tira · las ramas polifase · CIC sin multiplicadores · el estatismo y su cura |
| 8.3 | Remuestreo racional | L/M · el reloj que no cuadra · Farrow fraccionario · el banco de filtros |
| 9.1 | Estimar el espectro | el periodograma no converge · promediar (Welch) · sesgo vs varianza · resolución vs varianza |
| 9.2 | LMS: el filtro que se ajusta | el error que manda · cancelar ruido · el paso mu · ecualizar un canal |
| 9.3 | Seguir: PLL y Kalman | el NCO · el detector de fase · el lazo de 2º orden · Kalman escalar |
| 10.1 | La señal analítica | la mitad negativa · Hilbert · envolvente y fase instantánea · IQ |
| 10.2 | Tiempo–frecuencia | la STFT · el espectrograma · el compromiso de Heisenberg · wavelets |
| 10.3 | El filtro aprendido | una red que filtra · lo que aprende · dónde gana · dónde no conviene |

## 8. Paleta por ROL

El color dice el papel, no la estética.

| Alias | Color | Papel |
|---|---|---|
| `C_SENAL` | `#3b82f6` azul | el mundo continuo y la señal de entrada |
| `C_MUESTRA` | `#f59e0b` ámbar | la **secuencia** x[n], los coeficientes, h[n] |
| `C_CALCULO` | `#22d3ee` cian | **toda cifra calculada aquí** |
| `C_RUIDO` | `#f43f5e` rojo | ruido, error, alias, desbordamiento |
| `C_SALIDA` | `#34d399` verde | la salida y[n], lo reconstruido, lo corregido |
| `C_IDEAL` | `#a78bfa` violeta | el ideal / el límite teórico (respuesta ideal, cota) |
| `C_APREND` | `#e879f9` fucsia | lo adaptado y lo aprendido (LMS, red) |
| `C_BANDA` | `#fb923c` naranja | el espectro, las réplicas, las bandas |
| `C_DATO` | `#94a0b0` gris | dato público, no medido aquí |
| `C_REJILLA` | `#31414f` | mobiliario |

## 9. Contrato de la librería `dsp.py`

Reutiliza sin duplicar: `algebra_lineal` (`_Anclada`, `fmt`, `grafica`,
`plano`), `comunicaciones` (`Onda`, `EspectroArea`, `muestrear`, `alias_de`,
`cuantizar`, `snr_cuantizacion`, `psd_db`, `awgn`), `bloques` (cajas y flechas),
`brillo`, `senal`, `transiciones`.

`scipy.signal` **sí** se usa (viene con manim en la imagen: `firwin`, `remez`,
`butter`, `cheby1`, `ellip`, `freqz`, `group_delay`, `lfilter`, `tf2zpk`,
`resample_poly`, `hilbert`, `stft`). Lo que se enseña como **mecanismo** se
implementa a mano (DFT como matriz, mariposas, convolución paso a paso, LMS,
PLL, CIC, polifase, Q15): si el espectador tiene que verlo funcionar, no puede
ser una llamada opaca.

### Piezas de dibujo (todas con su gemela `con_*` para `Transform`)

| Pieza | Qué dibuja |
|---|---|
| `Secuencia` / `secuencia(x)` | tallos + puntos de x[n]; `.tallo(n)`, `.marcar(n)`, `.ventana(a,b)`, `.con_valores(y)` |
| `PlanoZ` / `plano_z()` | círculo unidad, `.polos(ps)`, `.ceros(zs)`, `.punto_en(w)`, `.radios_a(w)`, `.con_pz(z,p)` |
| `RespuestaFrec` / `respuesta(w, mag_db)` | \|H\| en dB vs ω/π; `.marca_w(w)`, `.con_mag(m2)`, `.banda(a,b)` |
| `LineaRetardos` / `linea_retardos(n)` | cadena de `z^-1` + multiplicadores + sumador; `.encender(k)`, `.con_coefs(c)` |
| `Deslizador` / `deslizar(x, h)` | la convolución en marcha: h volteada + ventana de productos + salida creciendo |
| `Mariposa` / `mariposa(N)` | grafo radix-2 de la FFT; `.etapa(k)`, `.par(i,j)` |
| `Espectrograma` / `espectrograma(S)` | malla tiempo–frecuencia coloreada; `.marca_t(t)` |
| `Escalera` / `escalera(t, y, bits)` | señal + su versión cuantizada + el error debajo |
| `Barras` / `barras(vals)` | coeficientes/ganancias como barras con su cifra |

### Funciones numéricas (todas devuelven lo **medido**)

Muestreo y reconstrucción: `replicas(x, fs, k)` (espectro con réplicas),
`espectro(x, fs)` (\|DFT\| en dB), `solape_db(...)`, `reconstruir_sinc(tk,yk,t)`,
`zoh(tk,yk,t)`, `droop_db(f,fs)`, `snr_jitter(f, sigma_t, n)`.
Cuantización: `error_cuantizacion`, `sqnr_medida`, `recta_bits(bits)` (pendiente
dB/bit medida), `dither`, `noise_shaping`, `sqnr_en_banda`.
LTI: `impulso(n)`, `respuesta_impulso(b,a,n)`, `convolucion(x,h)`,
`pasos_convolucion(x,h)`, `suma_abs(h)` (BIBO), `correlacion(x,y)`,
`ganancia_proceso_db`, `chirp`, `codigo_ca`.
Frecuencia: `dft_matriz(N)`, `dft(x)`, `ops_dft(N)` / `ops_fft(N)` (conteos
reales), `mariposas(N)`, `bit_reverso(N)`, `ventana(nombre,N)`, `enbw(w)`,
`fuga_db(...)`, `scalloping_db(w)`.
Z y respuesta: `zpk(b,a)`, `respuesta_frec(b,a)`, `retardo_grupo(b,a)`,
`es_estable(a)`, `fase_minima(b)`, `reflejar_cero(b,k)`.
FIR/IIR: `fir_ventana(...)`, `fir_equirriple(...)`, `rizado_db(...)`,
`iir_butter/cheby/elip(...)`, `bilineal(...)`, `warp(...)`, `biquads(z,p,k)`,
`comparar_orden(...)`.
Aritmética: `q15(x)`, `satura(x)`, `envuelve(x)`, `cuantizar_coefs(b,a,bits)`
(devuelve el desplazamiento de polos medido), `ciclo_limite(...)`,
`macs_por_segundo(...)`, `overlap_add(x,h,L)`, `cruce_fft(...)`.
Multitasa: `diezmar`, `interpolar`, `polifase(h,M)`, `cic(x,R,N)`,
`respuesta_cic`, `farrow(x, mu)`, `banco_qmf(...)`.
Estimación/adaptación: `periodograma`, `welch_medido`, `varianza_estimador`,
`lms(x,d,mu,L)`, `nlms`, `curva_aprendizaje`, `pll(x, kp, ki)`,
`kalman_escalar(z, q, r)`.
Mundo real: `analitica(x)`, `envolvente(x)`, `fase_inst(x)`, `stft(x,...)`,
`wavelet_haar(x)`, `heisenberg(...)`, `entrenar_filtro(...)` (red pequeña en
numpy puro, semilla fija).

## 10. Lotes de producción

Cada lote recorre los 10 pasos ENTERO (plan → librería → molde → stubs →
agentes → revisión → PR → prod → narración → mux) antes de abrir el siguiente.

| Lote | Módulos | Lecciones | Qué aporta a la librería | Estado |
|---|---|---|---|---|
| 1 | 1–2 | 1.1–2.3 | `Secuencia`, `Escalera`, `Deslizador`, `Barras`, `EspectroDoble`, réplicas, cuantización, convolución, correlación | ~ producción |
| 2 | 3–4 | 3.1–4.3 | `Mariposa`, `PlanoZ`, `RespuestaFrec`, DFT/FFT, ventanas, Z, retardo de grupo | ~ producción |
| 3 | 5–6 | 5.1–6.3 | `LineaRetardos`, diseño FIR/IIR, biquads, Goertzel | ~ producción |
| 4 | 7–8 | 7.1–8.3 | Q15, ciclos límite, overlap-add, polifase, CIC, Farrow, bancos | ~ producción |
| 5 | 9–10 | 9.1–10.3 | `Espectrograma`, Welch, LMS, PLL, Kalman, Hilbert, STFT, filtro aprendido | ~ librería lista |

## 11. Receta de lote (los 10 pasos con las rutas de esta familia)

1. Storyboard del lote en §13 (se escribe al abrir el lote, no antes).
2. Ampliar `studio/content/manim_extensions/dsp.py` y **validarla en el
   contenedor** con una sonda del scratchpad que imprima cifras y guarde PNGs.
3. Molde: la primera lección del lote entera, mía, validada.
4. `curso.json` + stubs `class ClipN(Scene): self.wait(1)` de las 6 lecciones.
5. Un subagente por lección (Sonnet mecánicas / Opus delicadas), contrato en el
   scratchpad, con §2 (formato mudo) copiada íntegra.
6. Revisión mía de frames uno a uno + `pytest -q`.
7. PR a `main` y merge.
8. VPS: `git pull` + `subir_curso.py`; `qh` **local** (3 en paralelo) → staging →
   `adoptar_renders.py`.
9. `guiones.py` **SERIAL** en el VPS.
10. Mux local con la marca, medir picos, re-muxear > −0.5 dB, y **actualizar
    §12, `PLAN.md` y la memoria** antes de cerrar el lote.

## 12. Tablero de estado

Leyenda: `—` no empezado · `~` en curso · `✔` hecho.

| Lección | plan | libr. | clips | ql✔frames | PR | subida | qh | narrada | mux |
|---|---|---|---|---|---|---|---|---|---|
| 1.1 | ✔ | ✔ | ✔ | ✔ | ✔ #54 | ✔ | ✔ | ✔ | ✔ 2:27 |
| 1.2 | ✔ | ✔ | ✔ | ✔ | ✔ #54 | ✔ | ✔ | ✔ | ✔ 2:44 |
| 1.3 | ✔ | ✔ | ✔ | ✔ | ✔ #54 | ✔ | ✔ | ✔ | ✔ 2:22 |
| 2.1 | ✔ | ✔ | ✔ | ✔ | ✔ #54 | ✔ | ✔ | ✔ | ✔ 2:16 |
| 2.2 | ✔ | ✔ | ✔ | ✔ | ✔ #54 | ✔ | ✔ | ✔ | ✔ 2:43 |
| 2.3 | ✔ | ✔ | ✔ | ✔ | ✔ #54 | ✔ | ✔ | ✔ | ✔ 2:51 |
| 3.1 | ✔ | ✔ | ✔ | ✔ | ✔ #55 | ✔ | ✔ | ✔ | ✔ 2:17 |
| 3.2 | ✔ | ✔ | ✔ | ✔ | ✔ #55 | ✔ | ✔ | ✔ | ✔ 2:35 |
| 3.3 | ✔ | ✔ | ✔ | ✔ | ✔ #55 | ✔ | ✔ | ✔ | ✔ 2:35 |
| 4.1 | ✔ | ✔ | ✔ | ✔ | ✔ #55 | ✔ | ✔ | ✔ | ✔ 2:17 |
| 4.2 | ✔ | ✔ | ✔ | ✔ | ✔ #55 | ✔ | ✔ | ✔ | ✔ 2:36 |
| 4.3 | ✔ | ✔ | ✔ | ✔ | ✔ #55 | ✔ | ✔ | ✔ | ✔ 2:32 |
| 5.1 | ✔ | ✔ | ✔ | ✔ | ✔ #56 | ✔ | ✔ | ✔ | ✔ 2:15 |
| 5.2 | ✔ | ✔ | ✔ | ✔ | ✔ #56 | ✔ | ✔ | ✔ | ✔ 2:30 |
| 5.3 | ✔ | ✔ | ✔ | ✔ | ✔ #56 | ✔ | ✔ | ✔ | ✔ 2:21 |
| 6.1 | ✔ | ✔ | ✔ | ✔ | ✔ #56 | ✔ | ✔ | ✔ | ✔ 2:37 |
| 6.2 | ✔ | ✔ | ✔ | ✔ | ✔ #56 | ✔ | ✔ | ✔ | ✔ 2:36 |
| 6.3 | ✔ | ✔ | ✔ | ✔ | ✔ #56 | ✔ | ✔ | ✔ | ✔ 2:13 |
| 7.1 | ✔ | ✔ | ✔ | ✔ 29/29/29/29 s | — | — | — | — | — |
| 7.2 | ✔ | ✔ | ~ | — | — | — | — | — | — |
| 7.3 | ✔ | ✔ | ~ | — | — | — | — | — | — |
| 8.1 | ✔ | ✔ | ~ | — | — | — | — | — | — |
| 8.2 | ✔ | ✔ | ~ | — | — | — | — | — | — |
| 8.3 | ✔ | ✔ | ~ | — | — | — | — | — | — |
| 9.1–10.3 | ✔ mapa | — | — | — | — | — | — | — | — |

**Dónde está la sesión**: lotes 1 y 2 **cerrados** (12 vídeos narrados y
muxeados, marca sonora a −6.0 dB dentro de las salidas); lote 3 **cerrado**
tambien; lote 4 con 5 subagentes produciendo (los mato un corte de cuota y se
relanzaron); lote 5 con la librería ya escrita y validada en el scratchpad
(`dsp5.py`), pendiente de pegar a `dsp.py` cuando no haya agentes importandola.

**Salidas** en `exports/procesamiento-senales-*/curso_narrado.mp4` (no
versionadas): lote 1 de 2:16 a 2:51 (5 clips re-muxeados a −1.5 dB); lote 2 de
2:17 a 2:36 (ninguno hizo falta); lote 3 de 2:13 a 2:37 (7 re-muxeados,
uno de ellos a −2.5 dB porque tocaba 0.0).

## 13. Storyboard

### Lote 1 — Módulos 1 y 2

Hilo del lote: un **acelerómetro de un lanzador** (vibración longitudinal,
"pogo") es la señal viva de todo el módulo 1; el módulo 2 la pasa por sistemas.

#### 1.1 «Muestrear: el espectro se repite»
Intención: el alias ya se vio en Comunicaciones digitales *en el tiempo*. Aquí
se ve **en frecuencia**, que es donde se entiende: muestrear COPIA el espectro
cada fs, y el problema es que las copias se toquen.

- **c1 · La secuencia** — la vibración continua (azul) y el reloj de muestreo;
  los tallos ámbar aparecen sobre ella y luego la curva se apaga: quedan solo
  los números. Cifras: `fs = 800 Hz`, `N = 64`, `T = 1.25 ms`.
  Lib: `secuencia`, `muestrear`.
- **c2 · Las réplicas** — el espectro de la banda base (naranja) y las copias
  centradas en ±fs, ±2fs. Cifras: `banda 0-180 Hz`, `guarda 440 Hz` (medida
  como distancia entre el borde de una réplica y el de la vecina).
  Lib: `replicas`, `espectro`, `EspectroArea`.
- **c3 · Cuando se tocan** — fs baja a 300 Hz; las réplicas se solapan y el
  tono de 220 Hz reaparece en 80 Hz; los tallos coinciden con el impostor.
  Cifras: `220 Hz -> 80 Hz`, `error 0.98 rms` (medido sobre la ventana).
  Lib: `alias_de`, `solape_db`.
- **c4 · La guarda** — el filtro antialias recorta antes de muestrear; las
  réplicas se separan. Cifra: `atenuacion en fs/2 = XX dB` (medida).
  Cierre: «Muestrear no pierde nada.» / «Si el espectro cabe entre replicas.»

#### 1.2 «Cuantizar: el ruido que fabricamos»
Intención: cuantizar no es "redondear un poquito": **fabrica** una señal de
error, y esa señal tiene espectro, se puede medir y se puede mover.

- **c1 · La escalera** — 4 bits sobre la vibración; debajo, el error rojo.
  Cifras: `paso = 0.125`, `SQNR medida = XX dB`. Lib: `Escalera`, `sqnr_medida`.
- **c2 · Seis decibelios por bit** — barrido de 4 a 14 bits, puntos medidos y
  la recta ajustada encima. Cifra: `pendiente medida = 6.0X dB/bit`.
  Lib: `recta_bits`.
- **c3 · Cuando el error deja de ser ruido** — tono pequeño a 3 bits: el
  espectro del error muestra **armónicos** (no piso plano). Con dither, se
  aplanan. Cifras: `espurio -XX dB -> piso -XX dB`. Lib: `dither`.
- **c4 · Mover el ruido** — sobremuestreo ×8 + noise shaping de 1er orden: el
  ruido se va fuera de banda. Cifra: `SQNR en banda +XX dB`.
  Lib: `noise_shaping`, `sqnr_en_banda`.
  Cierre: «El ruido de cuantizar no se borra.» / «Se lleva donde no molesta.»

#### 1.3 «Volver al mundo»
Intención: el camino de vuelta tiene sus propias pérdidas, y una de ellas no
está en la señal sino en el **reloj**.

- **c1 · El DAC retiene** — la escalera del ZOH sobre la señal; al lado, su
  respuesta sinc. Cifra: `droop en fs/2 = -3.92 dB` (medido).
- **c2 · La sinc ideal** — cada muestra pone una sinc; se suman y reconstruyen
  la curva exacta. Cifra: `error rms = X.Xe-15`. Lib: `reconstruir_sinc`.
- **c3 · Sobremuestrear para reconstruir fácil** — ×4: las imágenes se alejan y
  el filtro analógico se vuelve trivial. Cifra: `imagen a XXX Hz, -XX dB`.
- **c4 · El reloj tiembla** — jitter σ_t en los instantes: la SNR cae con la
  frecuencia. Cifras: `sigma = 50 ps`, `SNR medida = XX dB @ 100 kHz`.
  Lib: `snr_jitter`. Cierre: «La secuencia no vale nada» / «sin el reloj que la
  sostiene.»

#### 2.1 «LTI: el impulso lo dice todo»
- **c1 · La caja** — sistema como bloque; entra un impulso, sale `h[n]`
  (tallos ámbar). Cifras: `h[0..4]` medidos. Lib: `bloques`, `respuesta_impulso`.
- **c2 · Linealidad** — dos entradas, sus salidas; la suma escalada da la suma
  escalada. Cifra: `error max = 0.0e+00` (medido).
- **c3 · Invarianza** — retardar la entrada 7 muestras retarda la salida 7.
  Cifra: `desplazamiento medido = 7`.
- **c4 · Suma de deltas** — la entrada se descompone en deltas pesadas; cada
  una arrastra su copia de `h`; se suman y aparece `y[n]`.
  Cierre: «Un sistema LTI no guarda secretos.» / «Se confiesa con un impulso.»

#### 2.2 «Convolución: deslizar y sumar»
- **c1 · El deslizamiento** — `h` volteada avanza sobre `x`; la ventana de
  productos se enciende; `y[n]` crece tallo a tallo. Lib: `Deslizador`.
- **c2 · Longitud y transitorio** — `N + M - 1` medido; los bordes marcados.
  Cifras: `N=24`, `M=9`, `salida=32`.
- **c3 · BIBO** — dos `h`: una sumable y otra no; la salida de la segunda se
  dispara. Cifras: `suma|h| = 2.31` vs `divergente`.
- **c4 · El coste** — contador de multiplicaciones: `N·M` MACs.
  Cifra: `216 MAC` medidos. Cierre: «Filtrar es deslizar y sumar.» / «Lo demas
  es hacerlo rapido.»

#### 2.3 «Correlación: hallar lo conocido»
- **c1 · Correlar no es convolucionar** — la misma pieza sin voltear;
  autocorrelación del ruido = un pico. Cifra: `pico/lateral = XX`.
- **c2 · El filtro adaptado** — chirp de radar enterrado a `SNR = -10 dB`; la
  correlación levanta el pico. Cifra: `ganancia de proceso = XX dB` (medida).
- **c3 · Resolución** — chirp de banda B vs pulso; ancho del pico medido.
  Cifra: `ancho = 1/B = XX us`.
- **c4 · El correlador** — código pseudoaleatorio y el desplazamiento hallado.
  Cifra: `retardo hallado = 137 muestras` = el real.
  Cierre: «El ruido no se parece a nada.» / «Por eso la señal aparece.»

### Lote 2 — Módulos 3 y 4

Hilo del lote: se pasa del **tiempo** a la **frecuencia** y de ahí al **plano
Z**, que es donde un filtro deja de ser una lista de coeficientes y se vuelve
una figura. Señal de trabajo: la misma vibración del lanzador más un tono de
prueba, y como aplicación el análisis de un registro de telemetría.

Piezas nuevas de `dsp.py`: `Mariposa` (grafo radix-2), `PlanoZ` (círculo
unidad con polos y ceros y los radios al punto de trabajo), `RespuestaFrec`
(|H| en dB frente a ω/π, con su gemela y su marca de ω).

#### 3.1 «La DFT: proyectar sobre giros»
- **c1 · El giro** — e^{-j2πkn/N} como un punto girando en el plano complejo;
  la señal se multiplica por el giro y se **suma**. Lib: `dft_matriz`, `plano`.
- **c2 · La proyección** — un tono que coincide con un bin: la suma no se
  cancela. Otro que no: se cancela. Cifra: |X[k]| medido en los dos casos.
- **c3 · La matriz W** — la DFT como cambio de base ortogonal (se **usa** el
  resultado de Álgebra lineal 6.2, no se re-explica). Cifra: producto interno
  entre dos filas = 0 medido.
- **c4 · Simetría y bins** — X[N-k] = conj(X[k]) para señal real; qué frecuencia
  es cada bin (k·fs/N). Cierre: «La DFT no descompone en ondas.» / «Proyecta
  sobre giros.»

#### 3.2 «La FFT: partir en dos»
- **c1 · Pares e impares** — la suma de N se parte en dos de N/2 idénticas.
- **c2 · La mariposa** — el grafo con sus factores de giro; una etapa a la vez.
- **c3 · N log N medido** — contador real de multiplicaciones: `ops_dft(N)` vs
  `ops_fft(N)` para N = 1024. Cifra: la razón medida.
- **c4 · El orden bit-reverso** — por qué las entradas van barajadas. Cierre:
  «La FFT no es otra transformada.» / «Es la misma cuenta, sin repetirla.»

#### 3.3 «Fugas, ventanas y resolución»
- **c1 · La fuga** — un tono entre bins derrama energía por todo el espectro.
  Cifra: fuga medida en dB con ventana rectangular.
- **c2 · La ventana** — Hann, Hamming, Blackman: el lóbulo principal se
  ensancha y los laterales se hunden. Cifras medidas de los tres.
- **c3 · ENBW y scalloping** — lo que cuesta la ventana: ancho de ruido
  equivalente y la pérdida entre bins (medidas).
- **c4 · Zero-padding no es resolución** — interpola la curva, no separa dos
  tonos; para separarlos hay que medir **más tiempo**. Cierre: «Rellenar de
  ceros dibuja mejor.» / «Solo el tiempo resuelve.»

#### 4.1 «La transformada Z»
- **c1 · De la suma a z** — z⁻¹ es "una muestra de retraso": el operador que
  convierte la ecuación en diferencias en un polinomio.
- **c2 · Polos y ceros** — la fracción B(z)/A(z) y sus raíces en el plano.
  Lib: `zpk`, `PlanoZ`.
- **c3 · La ROC** — para qué valores converge la suma; causalidad.
- **c4 · Estabilidad** — todos los polos dentro del círculo unidad; se enseña
  moviendo uno hasta cruzarlo y viendo estallar h[n]. Cierre: «El círculo
  unidad no es un dibujo.» / «Es la frontera de lo estable.»

#### 4.2 «Del plano a la respuesta»
- **c1 · El punto que recorre el círculo** — ω avanza y el punto gira.
- **c2 · Los radios** — |H| es el producto de las distancias a los ceros
  dividido por el de las distancias a los polos: se dibujan los segmentos.
- **c3 · Mover un polo** — acercarlo al círculo afila el pico; medido.
- **c4 · Un filtro a mano** — colocar un cero donde estorba (el tono de red)
  y un polo donde interesa. Cierre: «Diseñar un filtro» / «es colocar puntos
  en un plano.»

#### 4.3 «Fase, retardo y mínima fase»
- **c1 · Fase lineal** — un FIR simétrico retrasa todo por igual; medido.
- **c2 · Retardo de grupo** — la derivada de la fase; qué le pasa a un pulso
  cuando no es plano (dispersión, medida).
- **c3 · Fase mínima** — el mismo |H| con los ceros dentro o fuera: distinta
  energía acumulada; medida.
- **c4 · El eco que se puede deshacer** — solo un sistema de fase mínima tiene
  inverso estable. Cierre: «El módulo no cuenta toda la historia.» / «La fase
  dice cuándo llega cada cosa.»

### Lote 3 — Módulos 5 y 6

Hilo del lote: **diseñar** un filtro. El módulo 4 enseñó a leer un filtro
puesto en el plano; aquí se elige dónde poner las cosas para cumplir un
pliego de condiciones, y se paga lo que cuesta. Pieza nueva: `LineaRetardos`
(la forma directa dibujada).

El pliego que se usa en las seis lecciones, para poder comparar: **paso hasta
0.20π, rechazo desde 0.32π, −45 dB**. Todo lo demás se mide contra él.

#### 5.1 «Truncar el ideal» (molde del lote)
- **c1 · La sinc que no cabe** — el filtro ideal es una sinc infinita; lo único
  posible es cortarla. `ideal_truncado`, `Secuencia`.
- **c2 · Gibbs** — la oreja que sale junto a la transición: +0.82 dB, y **no
  baja** al subir el orden (0.609 / 0.817 / 0.778 / 0.761 dB para órdenes
  20/40/80/160). Lo que sí mejora es lo estrecha que es la transición.
- **c3 · La ventana que ablanda** — al mismo orden 40: rect +0.817 dB de
  sobrepico y −27.5 dB de atenuación; hann +0.056 / −33.7; hamming +0.020 /
  −35.6; y **blackman +0.002 pero −24.1**, peor, porque su lóbulo principal se
  come la banda de transición. El matiz que hay que contar.
- **c4 · El precio** — para el pliego hacen falta **orden 72** por ventanas
  (37 multiplicaciones) frente a **orden 40** equirriple (21). Cierre: «El
  filtro ideal no existe.» / «Solo existe su recorte.»

#### 5.2 «Equirriple»
- **c1 · El margen que se tira** — el diseño por ventanas va de −28.1 a
  −119.3 dB en la banda de rechazo: donde sobra atenuación, sobra orden.
- **c2 · Repartir el error** — la idea del intercambio de Remez: mover los
  extremos hasta que todos midan lo mismo.
- **c3 · La alternancia** — 14 extremos medidos, todos entre −45.41 y
  −45.46 dB: **0.055 dB de diferencia**. Eso es lo óptimo.
- **c4 · Orden contra rizado** — 40 para −45 dB, 56 para −60 dB (medidos
  probando, no por fórmula). Cierre: «Lo óptimo no es lo más plano.» / «Es lo
  que reparte el error.»

#### 5.3 «Cuánto cuesta un FIR»
- **c1 · El retardo** — un FIR de orden N retrasa N/2 muestras. Medido.
- **c2 · La simetría** — h[k] = h[N−k]: **21 multiplicaciones de 41**.
- **c3 · La forma directa** — `LineaRetardos`: la señal cayendo por las cajas
  z⁻¹ y las tomas sumándose.
- **c4 · El presupuesto** — MAC por segundo a 48 kHz. Cierre: «Un filtro no se
  mide en decibelios.» / «Se mide en multiplicaciones por segundo.»

#### 6.1 «IIR: traer el analógico»
- **c1 · El semicírculo** — los polos del Butterworth analógico, repartidos por
  igual (`polos_butter_analogico`): |p| = 1 y ±112.5°, ±157.5° para orden 4.
- **c2 · La bilineal** — el semiplano izquierdo ENTERO cabe dentro del círculo;
  y el warping: 0.9π pide Ω = 6.31, no 0.9. Medido ida y vuelta.
- **c3 · Las tres familias** — al mismo orden 8: butter −16.8 dB con 0.044 dB
  de rizado; cheby1 −62.5 dB con 0.5 dB; elíptico −45.0 dB con 0.5 dB en las
  dos bandas. Cada dB de atenuación se paga con rizado.
- **c4 · IIR contra FIR** — el mismo pliego: FIR equirriple orden 40 (21
  multiplicaciones) frente a IIR elíptico **orden 5** (11 coeficientes).
  Cierre: «El filtro analogico no se copia.» / «Se dobla sobre el circulo.»

#### 6.2 «Biquads en cascada»
- **c1 · La forma directa revienta** — un IIR de orden 10 guardado con 16 bits
  mueve sus polos **0.209** (¡y el filtro deja de ser el que era!).
- **c2 · Secciones de segundo orden** — el mismo filtro partido en 5 biquads.
- **c3 · La cifra** — a 16 bits: error 2.09e−01 en directa contra **1.78e−04**
  en cascada, **1173×** mejor. A 12 bits, 220×.
- **c4 · El orden de las secciones** — cuál va primero y por qué. Cierre: «Un
  filtro no es su ecuacion.» / «Es como se calcula.»

#### 6.3 «Peine, resonador, notch, Goertzel»
- **c1 · El peine** — y[n] = x[n] + g·x[n−M]: con M = 8, **3 dientes** medidos
  en 0.25π, 0.5π y 0.75π.
- **c2 · El resonador** — el mismo par de polos del módulo 4, ahora como
  herramienta.
- **c3 · El notch** — matar una frecuencia sin tocar el resto: −39.7 dB en
  0.4π con un cero en el círculo y un polo a 0.97.
- **c4 · Goertzel** — una sola frecuencia sin FFT: **128 multiplicaciones
  contra 448**, y el resultado **idéntico** al de la DFT (diferencia 0.0e+00).
  Cierre: «No siempre hace falta el espectro entero.» / «A veces basta una
  nota.»

### Lote 4 — Módulos 7 y 8

Hilo del lote: el filtro ya está diseñado; ahora hay que **meterlo en el
aparato**. Módulo 7: lo que le pasa cuando los números tienen 16 bits y el
tiempo se acaba. Módulo 8: cómo hacer lo mismo con muchas menos cuentas
cambiando la frecuencia de muestreo.

#### 7.1 «Punto fijo Q15» (molde del lote)
- **c1 · El formato** — 16 bits con signo para el rango [−1, 1): paso
  3.05e−05, y el **1.0 no existe** (el mayor es 0.99997).
- **c2 · Saturar o envolver** — el mismo pico de +1.3: saturando queda en
  0.99997; envolviendo sale **−0.7**. El fallo más feo del punto fijo.
- **c3 · El escalado** — bajar la señal 6 dB da margen (0.16 → 6.18 dB) y
  cuesta SNR (94.4 → 88.2 dB). Las dos cifras, medidas.
- **c4 · Lo que queda** — SNR de Q15 medida sobre la señal: 94.4 dB.
  Cierre: «El punto fijo no es coma flotante barata.» / «Es otro oficio.»

#### 7.2 «Coeficientes cuantizados y ciclos límite»
- **c1 · La banda muerta** — y[n] = Q(a·y[n−1]) con a = 0.9 y 8 bits: el
  filtro no llega a cero, se queda **atrapado en 0.03125** (la cota teórica
  es 0.0391).
- **c2 · El ciclo límite** — con a = −0.9 no se queda quieto: **oscila con
  periodo 2 para siempre**, sin entrada. Un fallo que en coma flotante no
  existe.
- **c3 · Cuántos bits** — 6 / 8 / 10 bits atrapan 0.125 / 0.03125 / 0.0078:
  escala exactamente con el paso. Es ruido de redondeo, no señal.
- **c4 · La cura** — más bits, o romper la realimentación exacta. Cierre:
  «Un filtro estable en el papel» / «puede no apagarse nunca.»

#### 7.3 «El presupuesto de tiempo real»
- **c1 · MAC por segundo** — 21 multiplicaciones por muestra a 48 kHz.
- **c2 · Bloques y latencia** — L = 64 son 1.33 ms; L = 256, 5.33 ms.
  Procesar por bloques es gratis en cuentas y caro en espera.
- **c3 · Overlap-add** — la convolución por bloques con FFT da **el mismo
  resultado**: error 3.3e−16 contra la directa.
- **c4 · El cruce** — la FFT gana a partir de **M = 24** (contando
  multiplicaciones REALES en los dos lados); con M = 41 sobre 10 000
  muestras, 410 000 contra 283 380. Cierre: «La FFT no siempre gana.» / «Hay
  que contar las multiplicaciones.»

#### 8.1 «Diezmar e interpolar»
- **c1 · Tirar muestras** — diezmar por 4 sin filtrar: el tono de 2600 Hz
  reaparece en **600 Hz**.
- **c2 · El filtro va ANTES** — con el antialias, |H(2600)| = **−67.5 dB**.
- **c3 · Meter ceros** — interpolar por L no cambia la señal, pero su
  espectro se llena de **imágenes**.
- **c4 · El filtro va DESPUÉS** — y las imágenes se van. Cierre: «Cambiar de
  ritmo no es tirar muestras.» / «Es filtrar y luego tirarlas.»

#### 8.2 «Polifase y CIC»
- **c1 · Lo que se tira** — filtrar 61 taps y quedarse con una de cada
  cuatro: tres cuartas partes del trabajo van a la basura.
- **c2 · Las ramas** — polifase reordena el mismo filtro en 4 ramas de 16,
  15, 15 y 15 taps: **61 → 15.25 multiplicaciones** por muestra de entrada.
- **c3 · CIC** — integradores y peines: diezma con **cero multiplicadores**.
- **c4 · Lo que cuesta el CIC** — su caída dentro de la banda: −0.42 dB si
  se usa una décima de la banda, −2.70 dB si se usa un cuarto, −11.61 dB si
  se usa entera. Cierre: «Lo barato no es gratis.» / «El CIC se paga en
  banda.»

#### 8.3 «Remuestreo racional y bancos»
- **c1 · L/M** — interpolar por L, filtrar, diezmar por M.
- **c2 · Farrow** — cuando los relojes no cuadran hace falta un retardo
  fraccionario: error 4.8e−05 con un tono a 0.037 fs, y **0.49** con uno
  cerca de Nyquist. El interpolador cúbico solo vale si sobra banda.
- **c3 · Dos canales** — el banco de Haar reconstruye **exacto**: error
  4.4e−16.
- **c4 · Lo que cuesta separar bien** — un QMF de 32 taps separa mucho mejor
  y deja 0.0199 de error. Y la longitud **tiene que ser par**: con 31 taps
  el error es 0.967, cincuenta veces peor. Cierre: «Partir en bandas y
  volver a juntarlas» / «solo cuadra si los filtros encajan.»

### Lote 5 — Módulos 9 y 10

Hilo del lote: hasta aquí el filtro lo diseñábamos nosotros. Ahora la señal
trae algo que no sabemos de antemano, y el sistema tiene que **medirlo,
seguirlo o aprenderlo**. Cierra el curso volviendo al principio: una red que
aprende a filtrar redescubre, coeficiente a coeficiente, el filtro que
habríamos diseñado en el módulo 5.

Piezas nuevas: `Espectrograma` (la malla tiempo–frecuencia).

#### 9.1 «Estimar el espectro» (molde del lote)
- **c1 · El periodograma no converge** — con 4096 muestras sus bins tiemblan
  **5.61 dB**; con 16384, **5.54 dB**. Más datos NO lo arreglan.
- **c2 · Promediar** — Welch parte la señal en 31 trozos solapados y promedia:
  la dispersión cae a **0.75 dB**.
- **c3 · Lo que cuesta** — la resolución baja a fs/nseg = **3.91 Hz** con
  trozos de 256, frente a 0.24 Hz usando la señal entera.
- **c4 · Sesgo contra varianza** — trozos largos (mejor resolución, más
  temblor) contra trozos cortos. Cierre: «Un espectro medido una vez» / «no es
  el espectro.»

#### 9.2 «LMS: el filtro que se ajusta solo»
- **c1 · El escenario** — una voz, un ruido que se cuela por un camino
  desconocido, y un micrófono con SOLO el ruido.
- **c2 · El error manda** — w[n+1] = w[n] + μ·e[n]·x[n]; con μ = 0.005 el ruido
  cae **14.9 dB** y los coeficientes aprendidos se parecen al camino real
  ([0.7, −0.4, 0.25, 0.1, −0.05]) con un **4.9 %** de error. (Con μ = 0.02
  serían 15.2 dB y 9.6 %: más rápido y más basto.) Y restar la referencia a
  secas, sin aprender el camino, solo da **3.5 dB**.
- **c3 · El paso μ** — μ = 0.02 converge en **76 muestras** y se queda
  temblando en 0.0187; μ = 0.001 tarda **2894** y baja hasta 0.00094. Rápido y
  basto contra lento y fino, medido.
- **c4 · Cuando se rompe** — por encima de μ_max = 0.40 diverge. Cierre: «No
  hace falta conocer el ruido.» / «Basta con oírlo aparte.»

#### 9.3 «Seguir: PLL y Kalman»
- **c1 · El NCO** — un oscilador propio que hay que casar con la señal.
- **c2 · El lazo** — el detector de fase, el filtro y la realimentación:
  tras enganchar, el error de fase queda en **0.055 rad**.
- **c3 · La deriva** — con un tono cuya frecuencia se va (Doppler de un pase),
  el PLL la sigue: error final **1.3e−05** en frecuencia normalizada.
- **c4 · Kalman** — cuánto creerse cada medida: el rms baja de **0.608** a
  **0.190**. Cierre: «Seguir no es medir.» / «Es apostar y corregir.»

#### 10.1 «La señal analítica»
- **c1 · Media transformada** — poner a cero las frecuencias negativas
  convierte un seno en un fasor: |x| = **1.0000** medido.
- **c2 · La envolvente** — el módulo sigue la amplitud instantánea: error rms
  **0.0000** contra la envolvente real.
- **c3 · La frecuencia instantánea** — la derivada de la fase da **60.00 Hz**
  medidos sobre un tono de 60.
- **c4 · IQ** — por qué una radio guarda dos números por muestra. Cierre: «Una
  señal real esconde la mitad.» / «La analitica la enseña.»

#### 10.2 «Tiempo–frecuencia»
- **c1 · Lo que el espectro no ve** — un barrido con un golpe corto: en el
  espectro entero el golpe se diluye.
- **c2 · El espectrograma** — la STFT lo pone en su sitio.
- **c3 · Heisenberg, en cifras** — ventana de 64: Δt = 64 muestras, Δf =
  0.0156; de 256: Δt = 256, Δf = 0.0039. **El producto es 1.00 siempre.**
- **c4 · Wavelets** — la ventana que se encoge al subir de frecuencia. Cierre:
  «No hay ventana buena.» / «Hay ventana elegida.»

#### 10.3 «El filtro aprendido» (cierre del curso)
- **c1 · Aprender por ejemplos** — una red lineal ve pares entrada/salida y
  ajusta sus pesos.
- **c2 · Lo que aprende** — al terminar, sus coeficientes son **exactamente**
  el filtro del módulo 5: coseno **1.000000**, error relativo **1.9e−09**. No
  ha inventado nada: ha redescubierto lo que ya sabíamos diseñar.
- **c3 · Dónde no conviene** — y ha costado 3000 pasos de entrenamiento en vez
  de una línea de código.
- **c4 · Dónde sí** — con un amplificador saturado, que ningún filtro lineal
  puede deshacer, la red saca **5.2 dB** al mejor lineal posible. Cierre del
  curso: «Una señal es una lista de numeros.» / «Todo lo demas es que le
  haces.»



## 14. Cosecha heredada (lo que más riesgo tiene aquí)

- `Transform` solo entre gemelas idénticas: **toda** pieza que cambie necesita
  su `con_*`. En esta familia el peligro está en `PlanoZ` (un polo más = otra
  estructura) y en `Secuencia` (distinto número de tallos).
- `interpolate_color` exige `ManimColor`; los `C_*` son `str`.
- Space Mono no trae superíndices ni griegas: `z^-1`, `ω`, `Δ`, `π` en MathTex.
  `tag_hud` solo ASCII.
- Escalar un VGroup encoge la letra: pasar `ancho`/`alto`/`fs`.
- Un formateador que redondea puede escribir un rótulo **falso**
  (`fmt(0.5,0)` → "0"): en este curso hay muchas cifras < 1 (rizados,
  coeficientes) — decimales explícitos.
- Medir sobre la **ventana dibujada**: los SQNR, las ganancias de proceso y los
  rizados se calculan sobre exactamente los datos que se ven.
- `Rotulos.mostrar` cobra ~0.25 s de salida por relevo.
- En `ql` la rejilla fija casi no se ve: el contraste se juzga en `qh`.

## 15. Cosecha de trampas por lote

### Lote 1 — lo que cazó la sonda antes de escribir clips

Los cuatro se habrían colado en pantalla como cifras plausibles:

1. **El noise shaping empeoraba la SNR en banda** (38.7 dB frente a 40.9 dB
   del cuantizador plano). El error se **suma** en vez de restarse:
   `v = x + e[n-1]` da NTF = 1 + z⁻¹, que empuja el ruido **hacia DC**, justo
   donde molesta. Con el signo correcto: +29.9 dB de ganancia.
2. **La m-secuencia no era una m-secuencia**: el LFSR con índices de bit mal
   puestos degeneraba en un ciclo corto, y la autocorrelación daba una razón
   de 1.1 en vez de 127. Se cazó midiendo `R[0] / max|R[k≠0]|`, no mirando la
   secuencia. Ahora `pn_larga` se construye como `secuencia_pn` de
   Comunicaciones (lista de bits, polinomio primitivo) y da 127 / −1 exacto.
3. **El pico del filtro adaptado se buscaba con `abs`**: en un chirp con ruido
   el lóbulo negativo adyacente ganaba y el retardo salía 138 en vez de 137.
   El pico de un filtro adaptado es **positivo**: `argmax(r)`, no `argmax|r|`.
4. **La demo del correlador no era honesta con 80 muestras**: a −10 dB
   acertaba el retardo en 4 de 8 semillas (con una fallaba por 300 muestras).
   Se barrieron duración y SNR hasta un caso que acierta **8 de 8**: chirp de
   120 µs (240 muestras). Una demo que funciona con la semilla que elegiste no
   es una demo.

Además: `replicas()` necesitó un **eje de frecuencia fijo** (`f_max`) y un
selector de copias para que dos muestreos distintos sean gemelas de estructura
idéntica — sin eso no hay `Transform` entre "fs = 800" y "fs = 300", que es
justo la animación que cuenta la lección 1.1.

### Lote 1 — lo que cazó la revisión de frames

5. **El `Deslizador` de tres carriles no se leía**: los productos, dibujados
   sobre el carril de x, quedaban tapados por el rectángulo de resalte, y el
   eje Y de la pieza que se desliza cruzaba la figura entera. Rediseñado a
   **cuatro carriles** (x / h volteada / productos / y) con `eje_y=False` y
   carriles de productos y salida de longitud FIJA — así `Transform` entre
   pasos es seguro.
6. **La curva del mundo desaparecía bajo la escalera** en `Escalera`: se
   dibujaba antes que los escalones. Ahora va encima y más gruesa.
7. Una fila de cifras anclada con `next_to` a una muestra concreta se sale del
   frame por la izquierda: las filas se centran con `move_to`, no se cuelgan
   de un punto de la figura.
8. Un rótulo `error 0.162` junto a otro `error 0.004` **no dice cuál es cuál**:
   la etiqueta de una cifra tiene que llevar su condición dentro
   (`300 Hz: error 0.162`), que en formato mudo es lo único que la explica.


### Lotes 2 a 4 — lo que fue apareciendo

**De la librería (cazado midiendo, no mirando):**

9. `LineaRetardos` usaba `LEFT` sin que `dsp.py` lo importara: **cualquier**
   llamada reventaba con `NameError`. Mi prueba de humo de las piezas no lo
   cubrió porque no llegué a renderizar esa. Lección: la prueba de humo tiene
   que dibujar TODAS las piezas nuevas, no las que parecen más delicadas.
10. El "ciclo límite" que escribí primero era la oscilación natural de un
    filtro casi inestable: la amplitud salía **igual con 8, 10 y 12 bits**, que
    es justo la señal de que no era ruido de redondeo. Reescrito a primer
    orden, escala exacto con el paso (0.125 / 0.03125 / 0.0078).
11. El coste de la FFT comparaba multiplicaciones **complejas** con **reales**:
    inflaba la FFT por cuatro y daba un cruce falso en M = 16. Contadas todas
    reales, el cruce está en M = 24.
12. El interpolador de Farrow **adelantaba** en vez de retrasar, y se comparaba
    contra un retraso: el error salía 1700 veces mayor de lo que es.
13. El banco QMF usaba longitud **impar**, y con longitud impar la cancelación
    del alias no se cumple: error 0.967 en vez de 0.0199. El hallazgo acabó
    siendo el cierre de la lección 8.3.
14. `Escalera` normalizaba el carril de error por **su propio** paso, así que
    la gemela de 8 bits dibujaba el error igual de alto que la de 4 y el
    momento "el error se encoge" quedaba mudo.
15. `PlanoZ` dibuja las aspas de tamaño fijo: con `unidad` pequeña, un polo
    **estable** a 0.994 se dibujaba cruzando el círculo. Ahora hay
    `lado_marca`, pero el defecto no cambió (había 15 clips aprobados que
    dependían de él).

**De honestidad (lo que el render no detecta):**

16. **La malla decide**. La profundidad de un nulo, de un notch o de los ceros
    de un CIC depende de cuántos puntos tenga la rejilla (−119 dB con 4096,
    −141 con 16384; −39.7 dB con 2048, −240 con 4096). Esas cifras **no se
    rotulan nunca**. Lo que se rotula es lo que no se mueve al cambiar la
    malla: la posición del nulo, el nivel de los lóbulos, el ancho del agujero.
17. Por eso el "margen desperdiciado" de un diseño por ventanas no se mide de
    pico a nulo (91 dB, inflado) sino contra el nivel de los lóbulos: **27.2 dB**.
18. `h[79]` de un resonador vale **cero para los tres radios** (cae en un cruce
    por cero del seno): rotularlo junto a la palabra "inestable" habría
    enseñado un 0.0. Se usa el máximo de la cola.
19. La fase de un FIR simétrico solo es una recta **dentro de la banda de
    paso**; ajustarla entera da 1.7 rad de residuo y una conclusión falsa.
20. La caída de un CIC **no es un número**: −0.42, −2.70 o −11.61 dB según
    cuánta banda uses. Se rotulan las tres con su condición dentro.
21. Un agente reportó cuatro cifras descuadradas y **una no lo estaba**: al
    re-medirla, el valor original era el correcto. Los informes se verifican,
    en los dos sentidos.

**De tipografía (medido dos veces, la segunda con la sonda `texto2.py`):**

22. Rajdhani **parte palabras** a 16–17 px ("retardada" → "ret ardada") y
    **junta las palabras** por debajo de 22 px ("por separado" → "porseparado",
    comprobado en el frame `qh` real de la lección 2.1). Space Mono no hace ni
    lo uno ni lo otro a ningún tamaño del curso. Los helpers imponen ahora dos
    suelos: 18 px para un rótulo de una palabra y **22 px si tiene más de una**.

**De composición:**

23. Un resalte que entra con `FadeIn` mientras el anterior sale con `FadeOut`
    deja **dos** en pantalla medio segundo: `Transform` sobre un único mobject.
24. `Transform(pieza, gemela)` sobre una `_Anclada` cuyos submobjects entraron
    sueltos mete la pieza ENTERA en escena **y por encima de todo**.
25. `cierre_leccion` solo apaga lo que se le pasa: los `.ejes` de una pieza
    dibujada suelta sobreviven cruzando las dos frases del cierre.
26. `RespuestaFrec.en()` recorta con `np.clip`: una curva sin techo natural (la
    del warping, que llega a 31.8) sale como un segmento horizontal pegado al
    borde, que se lee como saturación — lo contrario de lo que hace.
27. Un contador de cifras dentro de una animación larga deja dígitos a medio
    morfar: `Succession(Wait(0.55), Transform(cont, nuevo, run_time=0.02))`.

## 16. Hitos globales
- 2026-08-27 — plan maestro escrito; rama y worktree creados.
- 2026-08-27 — `dsp.py` (lote 1, ~900 líneas) escrita y **validada en el
  contenedor**: cifras impresas + piezas renderizadas. Cuatro defectos
  cazados por la sonda ANTES de escribir un clip (ver §15).
- 2026-08-27 — molde 1.1 escrito, renderizado y aprobado frame a frame
  (32.3 / 32.8 / 30.0 / 33.3 s). Esqueletos + `style_block` con las cifras
  medidas de las 6 lecciones del lote 1; 5 subagentes en producción.
