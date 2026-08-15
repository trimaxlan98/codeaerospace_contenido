# Curso 20 — Metrología óptica (familia de lecciones)

> **Numeración**: archivo `curso-18`, curso **20** del PLAN. Formato de
> familia (como Aerodinámica y Electromagnetismo): un proyecto de
> ManimStudio = una **lección** de 4 clips; cada clip = un subtema.
> 3 módulos × 3 lecciones = **9 proyectos, 36 clips**.

- **Título de la familia**: `Metrología óptica`, sin numeración de plan
  de estudios (reciclable). Proyectos «Metrología óptica · N.M <título>»,
  slugs `metrologia-optica-N-M-<tema>`.
- **Ángulo editorial**: *la luz como regla*. El módulo 1 da la teoría
  básica (la onda, la fase, la interferencia, la difracción), el 2 las
  técnicas de medir con luz (tiempo de vuelo, franjas, frente de onda) y
  el 3 lleva todo eso al espacio: los **enlaces ópticos entre satélites
  (ISL)** — cómo se apunta un haz de microradianes a otro satélite, cómo
  se adquiere y se sigue, y cómo dos satélites se miden entre sí con
  nanómetros (GRACE-FO) y picómetros (LISA). Arco en una frase: *de la
  longitud de onda al satélite que se mide con el otro*.
- **Público**: divulgación técnica; álgebra y trigonometría, nada de
  cálculo. Las fórmulas se muestran; se explica lo que dicen.
- **No pisa** cursos publicados: «Cerrar el enlace» cuenta el enlace RF
  en dB; aquí el enlace es ÓPTICO y se cuenta en fotones por bit.
  Electromagnetismo 2.3 muestra la onda; aquí la onda es la REGLA.
  Relatividad-GPS toca relojes; aquí el tiempo de vuelo mide distancia.

```
familia            ManimStudio
-----------------  ----------------------------------------
módulo   (3)   →   —  (agrupación editorial)
lección  (9)   →   proyecto  "Metrología óptica · N.M <título>"
subtema  (36)  →   clip      "MODULO 0K" en el HUD (K = módulo)
```

Clips de 28–45 s, pies ≥ 5 s, el pie cambia ANTES de la animación.

## Mapa de las 9 lecciones

| Lección | Proyecto | Clips | Agente |
|---------|----------|-------|--------|
| 1.1 | La luz como regla | 4 | Sonnet |
| 1.2 | La interferencia: contar franjas | 4 | Opus |
| 1.3 | La difracción: el límite de la regla | 4 | Opus |
| 2.1 | Medir con el tiempo de vuelo | 4 | Sonnet |
| 2.2 | Medir la forma con franjas | 4 | Opus |
| 2.3 | Medir el frente de onda | 4 | Opus |
| 3.1 | El enlace óptico entre satélites | 4 | Sonnet |
| 3.2 | Apuntar, adquirir, seguir | 4 | Opus |
| 3.3 | Satélites que se miden entre sí | 4 | Opus |

## Paleta de la familia (regla por ROL)

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_HAZ` | `#f43f5e` rojo | la FUENTE de luz: el láser, el haz, el pulso que sale |
| `C_ONDA` | `#f59e0b` ámbar | la onda y su fase: senoides, frentes, la regla |
| `C_FRANJA` | `#a78bfa` violeta | lo que la luz DIBUJA: franjas, patrones, disco de Airy, manchas |
| `C_MEDIDA` | `#22d3ee` cian | lo que se MIDE o calcula: cifras, curvas de resultado, el detector |
| `C_OBJETO` | `#34d399` verde | el OBJETO medido o el otro extremo: espejo, pieza, el satélite receptor |
| `C_EJE` | `#31414f` | mobiliario |

Regla: el color dice quién actúa. Rojo emite, ámbar oscila, violeta es
el patrón que la luz pinta, cian es el número que sale, verde es lo que
se mide o a quien se apunta. El gris es mobiliario: nunca el objeto del
que habla el clip.

## Contrato de las librerías

Dos módulos en `studio/content/manim_extensions/`, deterministas, sin
red/disco/azar sin semilla, con topes duros `ValueError`, mismo estilo
que `distribuido.py`/`cripto.py` (núcleo puro → utilidades `_ancla`,
`_texto_hud`, `_validar` → piezas `VGroup` con localizadores sobre la
geometría ACTUAL). scipy está disponible (`scipy.special.j1`,
`numpy.unwrap`). Textos HUD en Space Mono, ASCII puro (µ se escribe
"u": "urad", "um"; exponentes con MathTex).

### `optica.py` (módulos 1 y 2)

Constantes: `C_LUZ = 299_792_458.0`, `LAMBDA_HENE = 632.8e-9`,
`LAMBDA_ISL = 1550e-9`, `LAMBDA_VERDE = 532e-9`.

Núcleo (números, VALIDADOS en el contenedor):
```python
frecuencia_de(lam)                 # c/lam: HeNe -> 473.8 THz
paso_franja(lam)                   # lam/2 por franja (Michelson): 316.4 nm
franjas_por_desplazamiento(d, lam) # 2 d / lam
longitud_coherencia(lam, dlam)     # lam^2/dlam: LED 20 nm@633 -> 20 um; HeNe 1 pm -> 0.40 m
intensidad_dos_haces(fase, V=1)    # (1 + V cos fase)/2 (normalizada)
visibilidad(imax, imin)            # (Imax-Imin)/(Imax+Imin)
franjas_indice(L, n_menos_1, lam)  # 2 L (n-1)/lam: 10 cm de aire (2.7e-4) -> 85.3 franjas
rendija_intensidad(theta, a, lam)  # sinc^2 (pi a sin/lam)
airy_intensidad(x)                 # (2 J1(x)/x)^2, x = pi D sin(theta)/lam
angulo_rayleigh(lam, D)            # 1.22 lam/D: Hubble 2.4 m @550 nm -> 0.28 urad; ojo 3 mm -> 224 urad
divergencia_gauss(lam, w0)         # lam/(pi w0): 1550 nm, w0 5 cm -> 9.87 urad
radio_haz(z, lam, w0)              # w0 sqrt(1+(z/zR)^2), zR = pi w0^2/lam
huella(theta, R)                   # 2 theta R: 9.87 urad a 5000 km -> 98.7 m
tiempo_vuelo(d)                    # 2 d / c: Luna 384 400 km -> 2.564 s; LAGEOS 5900 km -> 39.4 ms
distancia_por_tiempo(dt)           # 1 ps -> 0.15 mm; 6.67 ps -> 1 mm
ambiguedad_fase(f_mod)             # c/(2 f_mod): 10 MHz -> 15 m; 100 MHz -> 1.5 m
fotones_retorno(P, A_rx, D_tx_theta, R, ...)  # ley 1/R^4 del retrorreflector (opcional, cifra relativa)
fase_4_pasos(i1, i2, i3, i4)       # atan2(i4-i2, i1-i3), vectorizado
desenvolver(fase)                  # np.unwrap 1-D (y 2-D por filas+columnas simple)
altura_de_fase(fase, lam, theta)   # z = fase lam / (4 pi sin theta) para franjas proyectadas
zernike(n, m, rho, phi)            # polinomios (desenfoque 2,0; astig 2,±2; coma 3,±1; esferica 4,0)
strehl(sigma_ondas)                # exp(-(2 pi sigma)^2): lam/14 -> 0.80 (Marechal)
pendientes_locales(frente, paso)   # gradiente (Shack-Hartmann): desplazamiento de cada punto
```

Piezas (por lección):
```python
# 1.1
onda_regla(lam_px, ...)            # senoide con lambda acotada por una llave; .a_fase(f), .cresta(i)
reloj_luz(...)                     # la definicion del metro: pulso que recorre 1 m en 1/299792458 s; .a_t(t)
tren_coherencia(Lc, ...)           # tren de ondas de longitud finita; .con_longitud(L)
suma_ondas(fase, ...)              # dos senoides + su suma (constructiva/destructiva); .a_fase(f)
# 1.2
michelson(...)                     # fuente roja, divisor, dos espejos, detector; .espejo_movil, .a_desplazamiento(d)
patron_franjas(fase0, V, ...)      # franjas rectas (barra de intensidad); .a_fase(f), .con_visibilidad(V)
contador_franjas(...)              # curva I(d) + contador; .a_desplazamiento(d) (usa paso_franja)
celda_gas(...)                     # celda con n creciente en un brazo; .a_indice(n)
# 1.3
rendija_patron(a, lam, ...)        # rendija + curva sinc^2 rotable; .con_ancho(a)
disco_airy(...)                    # imagen 2-D del disco (celdas o ImageMobject sintetica) + perfil; .con_diametro(D)
dos_fuentes_rayleigh(sep, ...)     # dos discos que se acercan; .con_separacion(s), .resuelto()
haz_gaussiano(w0, lam, ...)        # cintura + hiperbolas de divergencia; .radio_en(z), .a_distancia(z)
# 2.1
pulso_ida_vuelta(d, ...)           # emisor, blanco, pulso que va y vuelve + cronometro; .a_t(t)
tierra_luna_laser(...)             # Tierra, Luna a escala de distancia (no de tamaño), retrorreflector; .pulso
satelite_slr(...)                  # estacion + LAGEOS + pulso; .a_t(t)
regla_ambiguedad(f_mod, ...)       # onda de modulacion como regla con vueltas; .con_frecuencia(f)
# 2.2
objeto_franjas(...)                # objeto (semiesfera) con franjas proyectadas deformadas; .con_fase0(f)
cuatro_pasos(...)                  # 4 imagenes de franjas desfasadas 90 grados + la fase calculada; .fase()
mapa_fase(...)                     # fase envuelta (dientes de sierra) y desenvuelta; .envuelta, .desenvuelta
perfil_superficie(...)             # perfil medido vs ideal con error en fraccion de lambda; .error_lambda()
# 2.3
frente_onda(zernike_coefs, ...)    # frente plano vs deformado (curvas de nivel o rejilla); .con_coeficientes(c)
shack_hartmann(...)                # rejilla de microlentes + manchas desplazadas; .con_frente(f), .mancha(i, j)
tarjetas_zernike(...)              # miniaturas: desenfoque, astig, coma, esferica; .tarjeta(nombre)
espejo_deformable(...)             # espejo con actuadores que corrigen; .a_correccion(k) + Strehl
```

### `isl.py` (módulo 3)

Constantes: `C_LUZ`, `LAMBDA_ISL = 1550e-9`, `H_PLANCK = 6.626e-34`,
`R_TIERRA_KM = 6371.0`, `V_LEO_KMS = 7.6`, `SEP_GRACE_KM = 220.0`,
`BRAZO_LISA_KM = 2.5e6`.

Núcleo:
```python
ganancia_apertura(D, lam)          # (pi D/lam)^2: 10 cm @1550 nm -> 4.1e10 = 106.1 dBi; 1 m @Ka 30 GHz -> 50 dBi
fspl_db(R, lam)                    # 20 log10(4 pi R/lam): 5000 km @1550 nm -> 272.2 dB
potencia_recibida_dbm(Pt_dbm, Gt, Gr, R, lam, perdidas_db=0)
energia_foton(lam)                 # h c/lam: 1550 nm -> 1.28e-19 J
fotones_por_segundo(P, lam)
fotones_por_bit(P, lam, tasa)      # 1 uW, 10 Gbps -> ~780 fotones/bit
divergencia_gauss, huella          # (re-exportadas o duplicadas de optica)
angulo_adelanto(v_perp)            # 2 v/c: 7.6 km/s -> 50.7 urad
doppler_optico(v, lam)             # v/lam: 7.6 km/s @1550 nm -> 4.9 GHz
desplazamiento_por_jitter(theta, R) # theta R: 1 urad a 5000 km -> 5 m
tiempo_luz(d)                      # d/c: 220 km -> 0.73 ms; brazo LISA 2.5e6 km -> 8.3 s
espiral_busqueda(paso, n_vueltas)  # puntos (x, y) de la espiral de adquisicion (deterministas)
error_cuadrante(x, y, w)           # señales normalizadas (A+B-C-D)/(suma) del detector de 4 cuadrantes
sensibilidad_relativa(dl, L)       # dl/L: 1 nm / 220 km -> 4.5e-15; 1 pm / 2.5e6 km -> 4e-22
```

Piezas:
```python
# 3.1
dos_satelites(sep_km, ...)         # dos satelites (verde) sobre arco de orbita; .a, .b, .enlace(); .a_separacion(km)
cono_haz(theta, R, ...)            # el cono del haz y su huella en el receptor; .con_divergencia(t)
barra_enlace(...)                  # presupuesto en cascada: Pt + Gt - FSPL + Gr = Pr (barras dB); .paso(i)
comparador_rf_optico(...)          # dos columnas: antena RF 1 m vs telescopio 10 cm con sus ganancias/anchos
# 3.2
punteria(...)                      # el satelite receptor y el haz; .con_error(urad) -> huella desplazada
adelanto_apuntado(v, ...)          # el receptor se mueve mientras la luz viaja: apuntar adonde ESTARA; .a_t(t)
espiral_adquisicion(...)           # espiral que barre la incertidumbre hasta ver el faro; .a_paso(k)
detector_cuadrantes(...)           # 4 cuadrantes + mancha; .con_mancha(x, y) -> señales; .señales()
# 3.3
grace_par(...)                     # dos satelites a 220 km, laser entre ellos, masa debajo que los separa; .a_t(t), .distancia()
interferometro_espacial(...)       # esquema LRI: laser, cavidad, señal de fase; .a_fase(f)
mapa_gravedad(...)                 # mapa (rejilla coloreada) de anomalias: la señal que se extrae; .region(nombre)
triangulo_lisa(...)                # tres naves a 2.5e6 km, brazos, onda gravitacional que estira; .a_estiramiento(h)
```

## Números que se rotulan (todos de las librerías)

| Cantidad | Valor | Función |
|---|---|---|
| f del HeNe (632.8 nm) | 473.8 THz | `frecuencia_de` |
| Una franja de Michelson | λ/2 = 316.4 nm | `paso_franja` |
| Longitud de coherencia LED (20 nm) / HeNe (1 pm) | 20 µm / 0.40 m | `longitud_coherencia` |
| Franjas al llenar 10 cm de aire | 85.3 | `franjas_indice` |
| Rayleigh Hubble 2.4 m @550 nm / ojo 3 mm | 0.28 µrad / 224 µrad | `angulo_rayleigh` |
| Divergencia gaussiana 1550 nm, w0=5 cm | 9.87 µrad → huella 98.7 m a 5000 km | `divergencia_gauss`, `huella` |
| Tiempo de vuelo Luna / LAGEOS | 2.564 s / 39.4 ms | `tiempo_vuelo` |
| 1 mm de distancia | 6.67 ps | `distancia_por_tiempo` |
| Ambigüedad 10 MHz / 100 MHz | 15 m / 1.5 m | `ambiguedad_fase` |
| Strehl con σ = λ/14 | 0.80 | `strehl` |
| Ganancia telescopio 10 cm @1550 / antena 1 m @30 GHz | 106.1 dBi / 50.0 dBi | `ganancia_apertura` |
| FSPL 5000 km @1550 nm | 272.2 dB | `fspl_db` |
| Pr con 1 W, 106+106 dBi, 5000 km | −30 dBm ≈ 1 µW | `potencia_recibida_dbm` |
| Fotones por bit a 10 Gbps | ~800 (801 con ganancias exactas) | `fotones_por_bit` |
| Ángulo de adelanto 7.6 km/s | 50.7 µrad (≈ 5 anchos de haz) | `angulo_adelanto` |
| Doppler óptico 7.6 km/s | 4.9 GHz | `doppler_optico` |
| Jitter 1 µrad a 5000 km | 5 m | `desplazamiento_por_jitter` |
| Luz entre GRACE (220 km) / brazo LISA | 0.73 ms / 8.3 s | `tiempo_luz` |
| 1 nm en 220 km / 1 pm en 2.5e6 km | 4.5e-15 / 4e-22 | `sensibilidad_relativa` |

## Reglas de honestidad

- Las cifras de GRACE-FO (LRI ~nm en 220 km, K-band ~µm) y LISA (pm,
  brazos 2.5 millones de km, lanzamiento ~2035) se rotulan como
  «orden de magnitud» — son las publicadas, no medidas aquí.
- El presupuesto de enlace óptico es de JUGUETE (1 W, aperturas de 10
  cm, sin pérdidas de apuntado ni ópticas): se dice y se rotula
  «ideal». La comparación RF/óptico usa la MISMA fórmula de apertura.
- La espiral de adquisición y el detector de cuadrantes son
  simulaciones deterministas (rotular «simulación»).
- Rayleigh es un criterio, no una ley: se dice.
- «La luz define el metro»: c fija desde 1983 — el metro es la distancia
  que recorre la luz en 1/299 792 458 s.

## Módulo 1 — La luz como regla

### Lección 1.1 — La luz como regla (Sonnet)
Hilo: la onda y su λ → el metro se define con la luz → la coherencia
(hasta dónde sirve la regla) → dos ondas se suman: la fase se ve.

| Clip | Título | Visual | `final_state` |
|---|---|---|---|
| 1 | Una regla de 633 nanómetros | onda roja HeNe, λ acotada, f = c/λ = 473.8 THz; «cada cresta es una marca» | onda con λ = 632.8 nm y f rotuladas |
| 2 | El metro lo define la luz | pulso que recorre 1 m; c exacta desde 1983; el metro sale de c y del segundo | reloj_luz con «1 m = c · 1/299 792 458 s» |
| 3 | Hasta dónde sirve la regla | tren de ondas: LED (Lc 20 µm) vs HeNe (0.40 m); la coherencia | dos trenes con sus Lc rotuladas |
| 4 | Sumar dos ondas | dos senoides con fase variable y su suma; constructiva/destructiva | suma_ondas + cierre «La luz no se mide con la luz. / Se mide con su fase.» |

### Lección 1.2 — La interferencia: contar franjas (Opus)
Hilo: Michelson → cada franja es λ/2 → contar franjas = medir → medir el
aire con franjas (índice) y la visibilidad como salud de la medida.

| Clip | Título | Visual | `final_state` |
|---|---|---|---|
| 1 | El interferómetro de Michelson | fuente, divisor, dos espejos, detector; el patrón de franjas | michelson con franjas en el detector |
| 2 | Cada franja vale media longitud de onda | el espejo se mueve d; la intensidad I(d) oscila; N = 2d/λ | contador_franjas: 3 franjas ↔ 949 nm |
| 3 | Medir el aire | celda de 10 cm que se llena de aire: 85 franjas pasan; n−1 = 2.7e-4 | celda + contador en 85.3 |
| 4 | La visibilidad | franjas nítidas vs lavadas: V = (Imax−Imin)/(Imax+Imin); coherencia | patron_franjas con V=1 y V=0.3 + cierre «Contar franjas es medir. / Y se cuentan de una en una.» |

### Lección 1.3 — La difracción: el límite de la regla (Opus)
Hilo: la rendija ensancha → el disco de Airy → Rayleigh: dos puntos se
distinguen o no → el haz láser también se abre (divergencia): el reto
del satélite.

| Clip | Título | Visual | `final_state` |
|---|---|---|---|
| 1 | La rendija que ensancha | rendija a, patrón sinc²; a más angosta, más ancho | rendija_patron con dos anchos |
| 2 | El disco de Airy | apertura circular → disco + anillos; primer cero 1.22 λ/D | disco_airy con perfil y 1.22 λ/D |
| 3 | El criterio de Rayleigh | dos fuentes que se acercan hasta confundirse; Hubble 0.28 µrad, ojo 224 µrad | dos_fuentes justo resueltas + cifras |
| 4 | El haz que se abre | haz gaussiano w0 = 5 cm, 1550 nm: 9.87 µrad; a 5000 km, huella de 99 m | haz_gaussiano + huella + cierre «Ni el láser es una recta. / Todo haz se abre.» |

## Módulo 2 — Medir con luz

### Lección 2.1 — Medir con el tiempo de vuelo (Sonnet)
Hilo: pulso y cronómetro → la Luna a 2.5 s → satélites con láser (SLR)
→ la fase de modulación y la ambigüedad.

| Clip | Título | Visual | `final_state` |
|---|---|---|---|
| 1 | Un pulso y un cronómetro | pulso ida y vuelta, d = c·t/2; 1 mm son 6.7 ps | pulso_ida_vuelta con la cuenta |
| 2 | La Luna, milímetro a milímetro | retrorreflectores Apolo; 2.564 s; la Luna se aleja 3.8 cm/año (rotulado, cita) | tierra_luna_laser con 2.564 s |
| 3 | Satélites con láser | SLR a LAGEOS (5900 km, 39.4 ms); órbitas al mm; la ley 1/R⁴ del retorno | satelite_slr + 39.4 ms |
| 4 | La regla con vueltas | medir con la fase de una modulación: 10 MHz → 15 m de ambigüedad; combinar frecuencias | regla_ambiguedad + cierre «El tiempo mide lejos. / La fase mide fino.» |

### Lección 2.2 — Medir la forma con franjas (Opus)
Hilo: proyectar franjas → cuatro pasos dan la fase → desenvolver →
la superficie a λ/20.

| Clip | Título | Visual | `final_state` |
|---|---|---|---|
| 1 | Franjas sobre el objeto | franjas rectas se curvan sobre una semiesfera: la forma está en la fase | objeto_franjas |
| 2 | Cuatro pasos | 4 imágenes desfasadas 90°; φ = atan2(I4−I2, I1−I3) píxel a píxel | cuatro_pasos con la fase calculada |
| 3 | Desenvolver la fase | dientes de sierra → rampa continua (np.unwrap) | mapa_fase envuelta y desenvuelta |
| 4 | Un espejo a λ/20 | perfil medido vs ideal; error 30 nm en un espejo de telescopio | perfil_superficie + cierre «La forma no se toca. / Se lee en las franjas.» |

### Lección 2.3 — Medir el frente de onda (Opus)
Hilo: el frente plano y el torcido → Shack-Hartmann lo mide por
pendientes → Zernike lo nombra → el espejo deformable lo corrige.

| Clip | Título | Visual | `final_state` |
|---|---|---|---|
| 1 | El frente de onda | plano vs deformado (curvas de nivel); la aberración es un mapa de fase | frente_onda con desenfoque + coma |
| 2 | Shack-Hartmann | microlentes: cada mancha se desplaza según la pendiente local | shack_hartmann con manchas desplazadas |
| 3 | Los nombres de Zernike | desenfoque, astigmatismo, coma, esférica como tarjetas | tarjetas_zernike |
| 4 | Corregir el frente | espejo deformable: Strehl de 0.3 a 0.8 (σ = λ/14) | espejo_deformable + cierre «Medir el frente es el primer paso. / Corregirlo, el segundo.» |

## Módulo 3 — Luz entre satélites (ISL)

### Lección 3.1 — El enlace óptico entre satélites (Sonnet)
Hilo: por qué láser (ganancia de apertura) → el cono de microradianes →
el presupuesto en fotones por bit → RF vs óptico.

| Clip | Título | Visual | `final_state` |
|---|---|---|---|
| 1 | Por qué láser | telescopio de 10 cm @1550 nm: 106 dBi; antena de 1 m @30 GHz: 50 dBi | comparador_rf_optico con las dos cifras |
| 2 | Un cono de microradianes | dos satélites a 5000 km; haz de 9.87 µrad → huella de 99 m | cono_haz + huella |
| 3 | Fotones por bit | cascada Pt 30 dBm + 106 − 272 + 106 = −30 dBm ≈ 1 µW → ~800 fotones/bit a 10 Gbps | barra_enlace + fotones/bit |
| 4 | Radio o luz | tabla: ancho de haz, ganancia, tasa, espectro sin licencia; el costo: apuntar | comparador + cierre «El láser regala ganancia. / La cobra en puntería.» |

### Lección 3.2 — Apuntar, adquirir, seguir (Opus)
Hilo: 1 µrad son 5 m → el receptor se movió mientras la luz viajaba
(adelanto 2v/c) → la espiral y el faro → el detector de cuadrantes y el
jitter.

| Clip | Título | Visual | `final_state` |
|---|---|---|---|
| 1 | Un microradián son cinco metros | punteria: error de 1 µrad → huella 5 m fuera; 10 µrad la pierde | punteria con dos errores |
| 2 | Apuntar adonde estará | el receptor se mueve 7.6 km/s: 2v/c = 50.7 µrad de adelanto (5 anchos de haz) | adelanto_apuntado |
| 3 | La espiral y el faro | espiral de búsqueda hasta ver el faro; luego el otro responde | espiral_adquisicion (simulación) |
| 4 | Seguir sin temblar | detector de 4 cuadrantes: la mancha corrige; jitter y Doppler 4.9 GHz | detector_cuadrantes + cierre «Adquirir es encontrarse. / Seguir es no soltarse.» |

### Lección 3.3 — Satélites que se miden entre sí (Opus)
Hilo: GRACE-FO: la gravedad los separa → el LRI mide nanómetros en 220
km → el mapa del agua y el hielo → LISA: picómetros en millones de km.

| Clip | Título | Visual | `final_state` |
|---|---|---|---|
| 1 | Dos satélites y una balanza | GRACE-FO: masa debajo tira del primero, la distancia cambia | grace_par con distancia variando |
| 2 | Nanómetros en 220 kilómetros | LRI: láser entre ellos, franja = λ/2; 1 nm/220 km = 4.5e-15 | interferometro_espacial + cifra |
| 3 | El mapa del agua | mapa de anomalías: acuíferos, hielo, la señal que sale de una distancia | mapa_gravedad |
| 4 | Picómetros entre tres naves | LISA: triángulo 2.5e6 km, 8.3 s de luz, la onda gravitacional estira un brazo | triangulo_lisa + cierre «La luz fue la regla del taller. / Ahora es la regla del universo.» |

## Producción

1. Yo: este storyboard, molde de `style_block` (uno por familia, copiado
   en cada proyecto con su cabecera), contratos.
2. Dos Opus en paralelo: `optica.py` y `isl.py` (validación numérica y
   visual en el contenedor; scipy disponible).
3. Valido el molde con stubs en la lección 1.1.
4. Nueve agentes en paralelo, uno por LECCIÓN (curso.json + copia del
   style_block + 4 clips), Opus/Sonnet según la tabla, contrato por
   lección; cada uno itera `render_local --clip N --frames 12` y revisa
   sus frames.
5. Yo reviso frames de las 9 lecciones, `--todos` por proyecto, pytest,
   PR único `curso/metrologia-optica` con PLAN.md.
6. Tras el merge: qh local (3 lecciones en paralelo), adoptar, guiones,
   mux con intro/cierre de marca.
