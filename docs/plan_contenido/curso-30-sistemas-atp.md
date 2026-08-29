# Curso 30 — Sistemas ATP: apuntamiento y seguimiento de satelites

> **Numeracion**: archivo `curso-30`, correlativo a `docs/plan_contenido/`.
> Curso **30** de `PLAN.md` (el 29 es Emergencia vertical). Coinciden.

## 1. Como reanudar

- Rama **`curso/sistemas-atp`** sobre el checkout principal
  (`~/Documentos/github/codeaerospace_contenido`), que quedo libre en `main`.
- El tablero de estado es la **§12** de este archivo. Se actualiza tras cada
  hito, no al final.
- Frase de reanudacion del dueño: *"continuamos con el curso de Sistemas ATP"*.
- Libreria: `studio/content/manim_extensions/atp.py`. Cursos en
  `studio/content/cursos/sistemas-atp-N-M-<tema>/`.

### Nota sobre el acronimo (ATP vs APT)

El encargo dice **ATP**; el curso fuente de la Academy se titula *Sistemas
APT* y en su L1 define **APT** = *Acquisition, Pointing and Tracking*. Pero el
mismo texto llama **ATP-DT** al gemelo digital (L5, L7) y su L6 escribe
"*Acquisition, Tracking & Pointing*". Las dos formas circulan de verdad en el
campo: **ATP** es la estandar en comunicaciones opticas y **APT** la que usa
el texto de la Academy. **Se adopta ATP**, que es lo que pidio el dueño y lo
que da nombre al gemelo. Queda anotado para que lo confirme.

## 2. Formato

**Familia**: un proyecto = una **leccion de 4 clips**; un clip = una idea.
**3 modulos x 3 lecciones = 9 proyectos, 36 clips.** Horizontal 16:9.

- Nombre del proyecto: `Sistemas ATP · N.M <titulo>` — **es la clave de
  emparejamiento de `subir_curso.py`: no se cambia despues de subir.**
- Slug: `sistemas-atp-N-M-<tema>`.

### SIN SUBTITULOS (formato mudo)

El dueño no los pidio, asi que rige el defecto desde el curso 27. **La palabra
la pone la voz; la pantalla pone la cosa y su cifra.** `pie_curso` **no se
define** en el `style_block`, y los helpers pasan por `_vigilar()`, que
**ABORTA el render** si un rotulo se convierte en frase.

| Elemento | Helper | Limite |
|---|---|---|
| Titulo del clip (arriba) | `titulo_curso()` | <= 6 palabras |
| Etiqueta del modulo (UL) | `hud_modulo("Modulo 0N")` | fija |
| Rotulo de mobiliario | `tag_junto()` | <= 4 palabras |
| **Cifra medida** (carril inferior) | `cifra_pie()` | <= 5 palabras |
| Cifra flotante | `tag_hud()` | <= 5 palabras |
| Columna de cifras (UR) | `panel_cifras()` | <= 5 por linea |
| Formula | `formula_pie()` | una linea |
| Dato NO calculado aqui | `dato_pie()` | <= 5 palabras, **gris** |
| Cierre del clip 4 | `cierre_leccion()` | 2 lineas |

Consecuencia de ritmo: el tiempo que sostenia la lectura del pie lo sostiene
la **animacion**. Mas `Create`/`Transform`/updaters, menos `wait` vacio.
Duracion **28-45 s** por clip, tope duro por ambos lados.

## 3. Angulo editorial

**Una antena que persigue es una cadena de eslabones, y cada eslabon tiene su
cifra.** De dos lineas de texto a una prediccion, de la prediccion a una
trayectoria, de la trayectoria a un lazo, del lazo a una campaña que acota su
cola, y de ahi a un numero de decibelios que decide si el enlace cierra. El
curso recorre esa cadena midiendo cada eslabon.

El arco lo tensa una **paradoja**: *el mejor pase para el enlace es el peor
para la mecanica*. El pase cenital da el rango minimo y la mejor señal, y es
justo el que hace divergir la velocidad de acimut (keyhole). Empieza ahi y
termina resolviendo la pregunta que el curso arrastra desde el clip 1:
**por que 0.1 grados y no 0.5** — que resulta no ser un numero de mecanica
sino de radio.

## 4. Publico y que asume

Intermedio-avanzado. Asume: trigonometria, numeros complejos, nociones de
Laplace y de matrices. De la coleccion, da por vistos **Algebra lineal**
(curso 22: matrices, autovalores, espacio de estados) y **Calculo vectorial**
(23). Usa sin re-explicar el vocabulario de **Comunicaciones digitales** (24)
y de **Procesamiento de señales** (27, el lazo digital y el filtrado).

## 5. Que NO pisa

Esta es la seccion critica: hay **cuatro** cursos publicados que tocan el tema.

| Curso vecino | Que cubrio | Que hace ESTA familia |
|---|---|---|
| **9 · Apuntar a un satelite** (8 clips, `apuntado.py`) | La **divulgacion** del tema: que es Az/El, que hay Doppler, que hay un PID. Un aperitivo de 8 clips. | La **ingenieria** de lo mismo: presupuesto de error medido, keyhole cuantificado, LQR, Monte Carlo. Reutiliza su libreria entera como sustrato de dibujo. |
| **11 · Control** (`control.py`) | Teoria de control generica: polos, lugar de las raices, margenes, respuesta al escalon. | **Aplica** el control a ESTA planta. No re-explica que es un polo: lo usa. La entrada relevante aqui es una **rampa**, no un escalon. |
| **13 · Cerrar el enlace** (`enlace.py`) | El presupuesto de enlace completo: FSPL, PIRE, C/N0, G/T, Shannon, MODCOD. | La leccion 3.3 **no re-enseña el link budget**: lo usa para responder UNA pregunta, cuanto cuesta en dB desapuntarse. Solo el termino `L_point`. |
| **20 · Metrologia optica**, modulo 3 (`isl.py`) | ATP **optico** entre satelites (adquirir/apuntar/seguir un laser). | ATP de **radiofrecuencia desde tierra**, con una montura mecanica de media tonelada. Otro regimen entero. |

Tambien se **usa sin re-explicar**: mecanica orbital (curso 3), el espectro
(10) y la teoria de la informacion (21).

## 6. Principio visual no negociable

Lo que tiene que VERSE moverse en esta familia:

1. **El cielo de la estacion en vista polar**, con la traza del pase
   cruzandolo. Es el objeto central: aparece en 1.1, 1.3, 2.1 y 3.2.
2. **La montura dibujada y MOVIENDOSE**: el anillo de acimut gira y el brazo
   de elevacion sube. Cuando el keyhole aprieta, el eje de acimut se dispara
   y se ve **saturar**.
3. **Referencia y real como DOS trazas**: el error es la distancia visible
   entre ellas, nunca un numero abstracto.
4. **El umbral de 0.1 grados siempre presente como banda cian**: el
   presupuesto se VE, no se dice. Cuando el error se sale, se sale por
   encima de una linea que ya estaba dibujada.
5. **Las distribuciones se dibujan**: histograma con su p95 en ambar. Jamas
   una media suelta.
6. **El haz como cono** con su ancho a media potencia, y el satelite dentro
   o fuera. En banda S cabe holgado; en Ka casi no cabe.
7. **Las cadenas se dibujan como cadena** (TLE -> SGP4 -> ECI -> ECEF -> ENU
   -> Az/El): el eslabon activo se enciende.

## 7. Mapa de lecciones

| Leccion | Proyecto | Los 4 clips, en cuatro palabras |
|---|---|---|
| 1.1 | El cielo que se mueve | GEO quieto · LEO barre · pase de minutos · el objetivo |
| 1.2 | De dos lineas a dos angulos | el TLE · SGP4 propaga · cadena de marcos · el reloj manda |
| 1.3 | La ventana y el keyhole | la mascara · rango y elevacion · 1/cos diverge · cuatro salidas |
| 2.1 | La frecuencia que se mueve | la curva S · cuanta velocidad radial · banda por banda · corregir y precompensar |
| 2.2 | La montura es un robot | dos articulaciones · J y b · el reductor · el backlash |
| 2.3 | El lazo sobre una rampa | tres terminos · error de arrastre · D amortigua · windup |
| 3.1 | LQR: elegir el compromiso | espacio de estados · Q contra R · Riccati · margenes |
| 3.2 | La campana Monte Carlo | catalogo de perturbaciones · suma en cuadratura · el histograma · la semilla |
| 3.3 | Por que 0.1 grados | el ancho de haz · S contra Ka · la cuenta completa · gemelo y realidad |

## 8. Paleta por ROL

El color dice el **papel**, no la estetica. Se hereda de `apuntado.py`
(curso 9) para que la familia se lea como su continuacion.

| Alias | Color | Papel |
|---|---|---|
| `C_CALCULO` | `#22d3ee` cian | **Toda cifra calculada aqui** y la ANTENA/montura, sujeto del curso. El carril de la cifra. |
| `C_SAT` | `#f59e0b` ambar | El satelite: su traza, su Doppler, la **referencia** que hay que seguir. Y el **p95** de una distribucion. |
| `C_CIELO` | `#a78bfa` violeta | El cielo, los marcos de referencia, lo **predicho** o nominal. |
| `C_PELIGRO` | `#f43f5e` rojo | Keyhole, saturacion, error **fuera** del presupuesto, sesgo. |
| `C_OK` | `#34d399` verde | Enganche, dentro del presupuesto, el enlace que **cierra**. |
| `C_EJE` | `#31414f` | Mobiliario: anillos, ejes, mascaras, rejillas. |
| `C_DATO` | `CODE_MUTED` gris | Dato publico **no** calculado aqui (para que el cian siga significando "medido"). |

## 9. Contrato de la libreria

`studio/content/manim_extensions/atp.py`. Deterministica
(`default_rng(semilla)`). **Reutiliza** de `apuntado.py` las piezas de dibujo
del curso 9 (`vista_polar`, `mascara_elevacion`, `traza_pase`, `cono_keyhole`,
`antena`, `tarjeta_tle`, `curva_s_doppler`, `curvas_seguimiento`,
`aguja_velocidad`), de `satelites.py` la mecanica orbital
(`velocidad_circular`, `periodo_orbital`, `fspl_db`) y de `control.py` el
mobiliario de lazo (`lazo_cerrado`, `plano_s`, `polo`).

### Funciones numericas (que devuelve MEDIDO)

**Geometria y cinematica del pase**
- `velocidad_angular_cenit(h_km)` → °/s de la linea de vista en el cenit.
- `rango_oblicuo(h_km, el_deg)` → km; vale `h` en el cenit.
- `tasa_acimut(h_km, el_deg)` → °/s exigidos al eje de acimut (el `1/cos el`).
- `perfil_pase(h_km, el_max_deg, mascara_deg, n)` → dict con `t, az, el, d,
  vr` muestreados: **la pieza central**, la referencia que siguen 2.3 y 3.2.
- `duracion_pase(h_km, el_max_deg, mascara_deg)` → s entre AOS y LOS.
- `radio_keyhole(h_km, el_max_deg, vel_max_deg_s)` → semiangulo del cono
  ciego, en grados, dado el tope del rotor.

**TLE y marcos**
- `altitud_de_movimiento_medio(n_rev_dia)` → km (424 con n=15.5).
- `enu_a_azel(e, n, u)` → `(az_deg, el_deg, d)`.
- `error_por_reloj(dt_s, h_km)` → grados de error por desincronia.

**Doppler**
- `velocidad_radial_max(h_km)` → km/s (≈7.0 a 550 km, **no** 7.59).
- `doppler_hz(vr_m_s, f0_hz)` → Hz.
- `tabla_doppler(h_km, bandas)` → por banda: `fd`, excursion.
- `tasa_doppler(h_km, f0_hz)` → Hz/s en la culminacion.

**Montura**
- `matrices_eje(J, b)` → `A, B` del espacio de estados.
- `par_necesario(J, b, alpha_deg_s2, w_deg_s)` → N·m en el eje de carga.
- `constante_mecanica(J, b)` → s.
- `par_viento(v_m_s, diametro_m, brazo_m)` → N·m.
- `traza_backlash(...)` → ciclo limite medido al invertir el giro.

**Lazo**
- `error_arrastre(v_deg_s, b, kp)` → °.
- `zeta_wn(kp, kd, J, b)` → `(zeta, wn)`.
- `sobreimpulso(zeta)` → fraccion; `t_establecimiento(zeta, wn)` → s.
- `simular_pase(perfil, kp, ki, kd, u_max, antiwindup, ...)` → `t, ref, real,
  error, u` + metricas `rms, max, frac_saturado`. **La otra pieza central.**

**LQR y robustez**
- `lqr(A, B, Q, R)` → `K, P` (Riccati resuelta por iteracion, no a mano).
- `controlabilidad(A, B)` → `(rango, det)`.
- `margenes(A, B, K)` → `(margen_ganancia_db, margen_fase_deg)` medidos
  sobre la respuesta en frecuencia del lazo abierto.

**Monte Carlo**
- `campana_montecarlo(n, sigmas, semilla)` → array de RMS por corrida.
- `percentiles(muestras)` → `p50, p95, peor`.
- `presupuesto_cuadratura(terminos)` → RMS total.
- `incertidumbre_percentil(n, p)` → ± en corridas (el `sqrt(N p (1-p))`).

**Enlace**
- `ancho_haz(diametro_m, f_hz)` → θ3dB en grados.
- `perdida_apuntamiento(err_deg, th3_deg)` → dB.
- `ganancia_plato(diametro_m, f_hz, eta)` → dBi.
- `presupuesto_cn0(...)` → dB-Hz.

### Piezas de dibujo nuevas (con sus gemelas `con_*`)

- `Montura` / `montura(...)` — la montura de dos ejes de perfil.
  `.apuntar(az, el)` mueve **los dos** ejes; `.saturar(bool)` pone el eje de
  acimut en rojo. Gemelas por estado, no por reconstruccion.
- `TrazaError` / `traza_error(...)` — error contra tiempo con la **banda de
  ±0.1° ya dibujada**. Gemela `con_*` para el relevo de curva.
- `Histograma` / `histograma(...)` — barras + linea de p95 (ambar) + umbral
  (cian). Gemela con `filas_max` para que dos histogramas sean gemelos.
- `Presupuesto` / `presupuesto_barras(...)` — la suma en cuadratura, con el
  termino dominante destacado.
- `Haz` / `haz(...)` — cono de media potencia con el satelite dentro o fuera.
- `PlanoQR` / `plano_qr(...)` — el compromiso Q/R como curva.
- `Cadena` / `cadena(...)` — la cadena de marcos con el eslabon activo.

## 10. Lotes de produccion

**Un solo lote de 9 lecciones.** El curso es mediano (9, no 30) y el encargo
es de una noche: se maximiza el paralelismo. El molde (1.1) lo escribe el
orquestador; las 8 restantes van a un subagente cada una.

| Lote | Modulos | Lecciones | Que aporta a la libreria | Estado |
|---|---|---|---|---|
| 1 | 1, 2 y 3 | 1.1 – 3.3 | `atp.py` entera, validada antes de escribir un clip | ver §12 |

## 11. Receta de lote

1. Plan (este archivo).
2. `atp.py` + **sonda de validacion en el contenedor** (cifras impresas +
   PNGs con PIL) **antes de escribir un solo clip**.
3. Molde: leccion 1.1 entera escrita y validada por el orquestador.
4. Esqueletos: `curso.json` + stubs `class ClipN(Scene): self.wait(1)` de las
   9 lecciones (`render_local.py` aborta si falta cualquier clip declarado).
5. 8 subagentes, una leccion cada uno. **No tocan la libreria ni git.**
6. Revision de frames uno a uno + `cd studio/backend && venv/bin/pytest -q`.
7. PR a `main` con rutas explicitas, `gh pr merge`.
8. `git pull` + `subir_curso.py` por leccion en el VPS; **`qh` LOCAL** (3 en
   paralelo), scp al staging y `adoptar_renders.py`.
9. `guiones.py` en el VPS, **SERIAL**, detached.
10. Mux local con intro/cierre de marca, medir picos, re-muxear lo que pase
    de −0.5 dB, y actualizar §12, `PLAN.md` y la memoria.

## 12. Tablero de estado

Leyenda: `—` sin empezar · `~` en curso · `✔` hecho.

| Leccion | plan | libreria | clips | ql ✔ frames | PR | subida | qh | narrada | mux |
|---|---|---|---|---|---|---|---|---|---|
| 1.1 El cielo que se mueve | ✔ | — | — | — | — | — | — | — | — |
| 1.2 De dos lineas a dos angulos | ✔ | — | — | — | — | — | — | — | — |
| 1.3 La ventana y el keyhole | ✔ | — | — | — | — | — | — | — | — |
| 2.1 La frecuencia que se mueve | ✔ | — | — | — | — | — | — | — | — |
| 2.2 La montura es un robot | ✔ | — | — | — | — | — | — | — | — |
| 2.3 El lazo sobre una rampa | ✔ | — | — | — | — | — | — | — | — |
| 3.1 LQR: elegir el compromiso | ✔ | — | — | — | — | — | — | — | — |
| 3.2 La campana Monte Carlo | ✔ | — | — | — | — | — | — | — | — |
| 3.3 Por que 0.1 grados | ✔ | — | — | — | — | — | — | — | — |

## 13. Storyboard

> Toda cifra rotulada sale de `atp.py`. Las que aparecen abajo entre
> parentesis son las del texto fuente y **hay que re-medirlas**: si la
> libreria da otra, manda la libreria y se corrige el storyboard.

### Leccion 1.1 — El cielo que se mueve

*Intencion*: fundar la diferencia cinematica que justifica el curso entero.
Una antena de TV se instala y se olvida; una de LEO persigue. Y persigue
**rapido**.

1. **Dos cielos, dos antenas.** Vista polar. A la izquierda un GEO: un punto
   ambar clavado que no se mueve en 10 s de animacion. A la derecha un LEO
   que cruza la carta entera. Cifras: caja de control del GEO
   (`dato_pie`, gris, es dato publico) y el periodo sidereo.
   → `periodo_orbital`. Cifra: `GEO 35786 km`.
2. **Cuanto se mueve en tu cielo.** Se dibuja el triangulo estacion-satelite
   en el cenit y se mide `ω = v/h`. La aguja de velocidad sube hasta
   `0.79 °/s`. Comparacion visible: dos diametros lunares por segundo
   (dibujar los dos discos de 0.5°). Segundo caso a 400 km: `1.10 °/s`.
   → `velocidad_angular_cenit`. Cifras: `v = 7.59 km/s`, `0.79 grados/s`.
3. **Todo el tiempo que tienes.** La traza del pase cruza la carta con la
   mascara de 5° sombreada; un contador cuenta los segundos entre AOS y LOS
   y para en `~9.8 min`. Se apagan y encienden tres pases del dia.
   → `duracion_pase`. Cifra: `pase 9.8 min`.
4. **El objetivo.** El haz de la antena como cono sobre la traza; se estrecha
   de banda S a banda Ka y el satelite se sale. Aparece el numero que el
   curso perseguira: `0.1 grados`. **Cierre**: "Nueve lecciones para sostener
   una decima de grado" / "y para saber por que esa y no otra."

### Leccion 1.2 — De dos lineas a dos angulos

*Intencion*: el TLE no es magia ni es kepleriano; y el eslabon que mas
sorprende no es la matematica, es el reloj.

1. **Dos renglones de 69 caracteres.** `tarjeta_tle()`; se encienden uno a
   uno los campos (epoca, inclinacion, RAAN, excentricidad con el punto
   implicito, movimiento medio). → campos de `tarjeta_tle`.
   Cifra: `n = 15.5 rev/dia`.
2. **De n a la altitud.** Kepler: `T = 86400/n` y `a = (mu T^2/4pi^2)^(1/3)`.
   Se dibuja la orbita a escala junto a la Tierra y se rotula
   `h = 424 km`. Segundo caso n=15.0 → `574 km`: media revolucion menos son
   150 km mas. → `altitud_de_movimiento_medio`. `formula_pie` con Kepler.
3. **La cadena de marcos.** `cadena()`: TLE → SGP4 → ECI → ECEF → ENU →
   Az/El, encendiendo un eslabon por vez. En ECEF→ENU se dibuja la estacion
   sobre el globo y los tres ejes E, N, U. Se cierra con el ejemplo
   resuelto: e=400, n=300, u=500 → `Az 53.13`, `El 45.0`, `d 707 km`.
   → `enu_a_azel`. **Trampa a rotular**: el primer argumento de `atan2` es
   el ESTE.
4. **El reloj manda.** Un segundo de desfase desplaza la traza sobre la
   carta polar: el error resultante (`~0.8 grados`) se dibuja como arco
   junto a la banda de 0.1°, que cabe ocho veces dentro. → `error_por_reloj`.
   **Cierre**: "Un segundo de reloj cuesta ocho presupuestos" / "sincronizar
   no es consejo, es requisito."

### Leccion 1.3 — La ventana y el keyhole

*Intencion*: la paradoja que tensa el curso. El mejor pase para el enlace es
el peor para la mecanica.

1. **La mascara no es adorno.** Vista polar con la mascara a 5°; se sube a
   10° y la traza util se acorta visiblemente. Se mide el recorte del tiempo
   de contacto. → `duracion_pase` con dos mascaras.
2. **Elevacion y distancia.** El rango oblicuo dibujado como segmento que se
   estira: en el cenit vale `550 km`, a 5° vale `2205 km`. La atenuacion
   extra `12.1 dB` se pone como barra. → `rango_oblicuo`, `fspl_db`.
3. **El 1/cos que diverge.** DOS pases sobre la misma carta: `el_max = 30°`
   y `el_max = 85°`. La aguja de velocidad de acimut marca `0.51 °/s` y
   `9.04 °/s`. Aparece el cono de keyhole y la traza se pone roja donde la
   montura ya no puede. → `tasa_acimut`, `radio_keyhole`. Cifra:
   `18x mas exigente`.
4. **Cuatro salidas.** Cuatro miniaturas: aceptar el hueco, flip de acimut,
   desapuntar a proposito, montura X-Y (la singularidad se va al horizonte).
   La X-Y se dibuja y se ve que el cenit queda limpio.
   **Cierre**: "El mejor pase del enlace" / "es el peor de la mecanica."

### Leccion 2.1 — La frecuencia que se mueve

*Intencion*: apuntar bien no basta si escuchas donde el satelite no esta. El
gemelo geometrico en el dominio de la frecuencia.

1. **La curva S.** `curva_s_doppler()` construyendose mientras el satelite
   recorre la traza polar al lado: alta en AOS, cruza `f0` en la
   culminacion, baja en LOS. Los dos graficos comparten el tiempo.
2. **Cuanta velocidad radial.** El error comun: no es la velocidad orbital
   entera. Se descompone el vector velocidad sobre la linea de vista y se
   mide el maximo: `7.0 km/s`, no 7.59. → `velocidad_radial_max`.
3. **Banda por banda.** Barras: VHF `±3.4 kHz`, UHF `±10.2 kHz`, S
   `±51 kHz`, X `±200 kHz`. Se superpone el ancho de un modem de 9600 bd y
   se ve que la portadora se sale. → `tabla_doppler`. Y la tasa en la
   culminacion: `153 Hz/s` a 437 MHz. → `tasa_doppler`.
4. **Corregir y precompensar.** Dos flechas de signo opuesto: bajada se
   corrige en recepcion (`f0 - fd`), subida se **precompensa**
   (`f0 + fd`). La señal deslizante se convierte en linea recta centrada en
   el filtro. **Cierre**: "La geometria y la frecuencia" / "beben del mismo
   reloj."

### Leccion 2.2 — La montura es un robot

*Intencion*: abrir la caja. La antena no obedece: tiene inercia, fricción,
holgura y un motor con limite.

1. **Dos articulaciones.** `montura()` de perfil: el eje vertical gira, el
   brazo de elevacion sube. Se marcan los 2 GDL y se apunta a un Az/El
   concreto siguiendo la traza.
2. **J y b.** El modelo se reduce a `J θ'' + b θ' = τ` y se dibuja el
   diagrama de polos: uno en el origen (integrador) y otro en `-b/J`. La
   constante mecanica `J/b = 4 s`: se empuja la montura y tarda una
   eternidad en parar. → `constante_mecanica`, `plano_s`, `polo`.
3. **El reductor: par barato, velocidad cara.** El par en el eje de carga
   `0.184 N·m` frente a `0.26 mN·m` en el motor con N=1000, η=0.7. Pero la
   velocidad se divide por N — y el keyhole pedia 9 °/s. Se enfrentan las
   dos cifras. → `par_necesario`.
4. **El backlash.** Se anima la inversion de giro: el eje de entrada se
   mueve y el de salida no, durante `0.3°`. Junto a la banda de 0.1° se ve
   que se come el presupuesto **entero** antes de que el control actue.
   Aparece el ciclo limite. → `traza_backlash`. **Cierre**: "La holgura se
   come el presupuesto" / "antes de que el control opine."

### Leccion 2.3 — El lazo sobre una rampa

*Intencion*: un pase **no es un escalon**. Es una rampa, y la rampa revela lo
que el escalon esconde.

1. **Tres terminos, tres analogos.** `lazo_cerrado()` y, sobre la montura, un
   resorte (kp), un amortiguador (kd) y una memoria que acumula (ki). Cada
   uno se enciende por separado.
2. **El error de arrastre.** La referencia sube en rampa y la antena queda
   sistematicamente por detras: `e = v b / kp`. A 1 °/s son `0.05°`
   (dentro); a 5 °/s son `0.25°`, **dos veces y media** por encima del
   presupuesto. La banda de 0.1° ya esta dibujada y se ve rebasarla.
   → `error_arrastre`.
3. **D amortigua, I limpia.** Con kp=10, J=2: `ωn = 2.24 rad/s`,
   `ζ = 0.056`, sobreimpulso `84 %`, `t_est = 32 s`. Con
   `kd = 5.76` → `ζ = 0.7`, sobreimpulso `4.6 %`, `t_est = 2.6 s`. Y el
   detalle que importa: **D no cambio el arrastre**. → `zeta_wn`,
   `sobreimpulso`, `t_establecimiento`.
4. **Windup.** El par satura; el integrador sigue cargando; al salir, el
   sobreimpulso llega tarde y grande. Se activa el clamping y la misma
   traza se endereza. Se miden los dos RMS sobre el pase entero.
   → `simular_pase` con y sin antiwindup. **Cierre**: "El pase es una
   rampa" / "y solo la integral borra el rezago."

### Leccion 3.1 — LQR: elegir el compromiso

*Intencion*: dejar de tocar ganancias a tientas y declarar prioridades.

1. **El estado.** `x = [θ, ω]`. Se reescribe la planta como `A, B` con los
   numeros del curso y se comprueba la controlabilidad: `det C = -0.25`,
   rango 2. → `matrices_eje`, `controlabilidad`.
2. **Q contra R.** El coste como dos platillos de balanza: Q castiga el
   error, R castiga el par. Se mueve la relacion `q/r` y el lazo cambia de
   velocidad en vivo. → `plano_qr`.
3. **Riccati, y el regalo.** Con q=100, r=1: `k1 = 10`, `k2 = 4.47`,
   `ωn = 3.16 rad/s`, `t_est = 1.8 s`. Con r=100: `ωn = 1 rad/s`,
   `3.16x` mas lento — exactamente la raiz cuarta de 100. Y `ζ = 0.707`
   **para cualquier q y r**: lo que en el PID se buscaba a tientas, aqui
   viene garantizado. → `lqr`.
4. **Margenes.** Se miden margen de ganancia y de fase del lazo. Se marca el
   objetivo (`>= 6 dB`, `>= 45°`) y se enseña como una latencia extra se
   los come. Nota honesta: LQG **no** hereda las garantias del LQR (Doyle,
   1978) — va en `dato_pie` gris. → `margenes`.
   **Cierre**: "Q y R no son ganancias" / "son una declaracion de
   prioridades."

### Leccion 3.2 — La campana Monte Carlo

*Intencion*: una simulacion es UNA muestra. Lo que se acepta es una cola.

1. **Catalogo de perturbaciones.** El viento como el gigante: `78 N·m`
   frente a los `0.175 N·m` de acelerar la inercia — **450 veces**. Se
   dibujan las dos barras a escala real y la de inercia casi no se ve.
   Luego deriva termica, sesgo de encoder, latencia, cuantizacion
   (`0.0055°` con 16 bits). → `par_viento`.
2. **Suma en cuadratura.** Las cuatro contribuciones como catetos que se
   componen: `0.073°`, con 27 % de margen bajo el objetivo. Y la leccion
   del metodo: bajar el termino GRANDE mueve el total; bajar el pequeño no.
   Se demuestra moviendo cada uno. → `presupuesto_cuadratura`.
3. **El histograma.** 500 corridas. Barras creciendo mientras corre la
   campaña; al final `p50 = 0.041°`, `p95 = 0.094°` (ambar), peor
   `0.137°`. El umbral de 0.1° en cian: el p95 pasa **por 6 %**, y el peor
   caso NO pasa. → `campana_montecarlo`, `percentiles`.
4. **Cuanto confias en ese p95.** `sqrt(N p (1-p)) = 4.9` corridas, ±1
   punto percentil. Con N=2000 baja a ±0.5: cuadruplicar solo duplica la
   confianza. Y la semilla: misma semilla, histograma identico — se dibujan
   los dos superpuestos y coinciden. → `incertidumbre_percentil`.
   **Cierre**: "La mediana no acepta un sistema" / "lo acepta la cola."

### Leccion 3.3 — Por que 0.1 grados

*Intencion*: cerrar el circulo. El requisito que el curso arrastra desde el
clip 1 no es de mecanica: es de radio.

1. **El ancho de haz.** `θ3dB ≈ 70 λ/D`. El haz se dibuja sobre el plato de
   3 m y se estrecha al subir la frecuencia. Comprobacion de coherencia: a
   media anchura la perdida da exactamente `3 dB`. → `ancho_haz`.
2. **S contra Ka.** El MISMO error de `0.1°` sobre la MISMA montura:
   banda S `θ3dB = 3.18°` → `0.012 dB`; banda Ka `θ3dB = 0.233°` →
   `2.2 dB`. **180 veces**. Se ve al satelite holgado dentro del haz de S y
   asomando fuera del de Ka. → `perdida_apuntamiento`.
3. **La cuenta completa.** Cascada de dB: EIRP `9 dBW`, FSPL `164.5 dB` a
   10° (y `154.1` en el cenit: `10.4 dB` solo por geometria), G/T
   `12.8 dB/K`, y el termino de desapuntamiento. Total
   `C/N0 = 82.9 dB-Hz`; a 1 Mbps deja `Eb/N0 = 22.9 dB`. El enlace cierra.
   → `presupuesto_cn0`, `ganancia_plato`, `fspl_db`.
4. **Gemelo y realidad.** La cadena entera del curso se redibuja de un
   tiron, eslabon a eslabon, y se cierra el lazo: el gemelo predice, la
   estacion mide, la diferencia reajusta el gemelo.
   **Cierre**: "Cero coma un grado no describe una antena" / "describe una
   banda."

## 14. Cosecha heredada (lo que mas riesgo tiene aqui)

De `references/trampas.md` y de las familias vecinas, lo que esta familia va
a repetir si nadie avisa:

- **`Transform` solo entre gemelas de estructura IDENTICA.** Aqui hay muchos
  relevos de cifra (la aguja de velocidad, el histograma que crece, el error
  que cambia): cada pieza que cambia necesita su gemela `con_*`, y los
  contadores, ancho fijo.
- **La malla decide.** Un percentil de 500 corridas y una `t_est` leida de
  una simulacion **dependen del muestreo**. Se rotula lo que no se mueve al
  refinar la malla; el p95 se rotula CON su N al lado.
- **Una cifra sin su condicion miente.** La velocidad radial maxima es 7.0
  km/s **en el horizonte de un pase a 550 km**, no en general. El error de
  arrastre es 0.25° **a 5 °/s**. La condicion va DENTRO del rotulo.
- **Comparar unidades distintas infla un lado.** El par de viento (78 N·m)
  contra el par de aceleracion (0.175 N·m) son ambos en el eje de carga: no
  mezclar con el par del motor (0.26 mN·m), que esta al otro lado del
  reductor. **Es la trampa numero uno de 2.2 y 3.2.**
- **Rajdhani parte palabras a 16-17 px y las junta por debajo de 22.** Los
  suelos (18 / 22) van en el `style_block` y no se bajan.
- **Sin acentos en pantalla.** Griegas, superindices y `≈` solo en `MathTex`.
- **`move_to` centra el bounding box**: la montura y el haz son asimetricos y
  hay que anclarlos por su pivote propio (ya mordio en el curso 9).
- **`cierre_leccion` solo apaga lo que se le pasa**: si se dibujo `.ejes` de
  una pieza suelta, hay que pasarlo tambien.
- Los `final_state` de `curso.json` **tambien citan cifras**: si se corrige
  la libreria, se revisan.

## 15. Cosecha de trampas del lote (se escribe DURANTE la produccion)

_(pendiente)_

## 16. Hitos globales

_(pendiente)_
