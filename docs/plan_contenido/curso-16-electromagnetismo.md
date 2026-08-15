# Curso 16 — Electromagnetismo (familia de lecciones)

- **Formato**: familia de lecciones, como Aerodinámica (curso 10). Un
  proyecto de ManimStudio = una **lección** de 4 clips; cada clip = un
  subtema. 4 módulos × 3 lecciones = **12 proyectos, 48 clips**.
- **Título de la familia**: `Electromagnetismo`, sin numeración de plan
  de estudios, para poder reciclarlo en cualquier programa.
- **Ángulo editorial**: todos los ejemplos apuntan a
  **telecomunicaciones y satélites**. El arco completo de la familia es
  una sola frase: *de la carga de Coulomb al bit que baja del
  satélite*. Cada módulo termina con un gancho hacia el siguiente.
- **Público**: divulgación técnica; asume álgebra y trigonometría, no
  cálculo vectorial (las ecuaciones se muestran, pero lo que se explica
  es lo que dicen, no cómo se operan).
- **No pisa** los cursos ya publicados: «Cerrar el enlace» hace la
  contabilidad en decibelios (Friis como suma); aquí el enlace se cuenta
  como **geometría física** (la esfera que se reparte). «El espectro»
  habla de gestión/regulación; aquí el espectro aparece como propiedad
  física de la onda y mapa de bandas.

```
familia            ManimStudio
-----------------  ----------------------------------------
módulo   (4)   →   —  (agrupación editorial, no existe en la DB)
lección  (12)  →   proyecto  "Electromagnetismo · N.M <título>"
subtema  (48)  →   clip      "MODULO 0K" en el HUD
```

Slugs `electromagnetismo-N-M-<tema>`, ordenables. Clips de 28–45 s,
pies ≥ 5 s legibles, el pie cambia ANTES de la animación que ilustra.

## Mapa de las 12 lecciones

| Lección | Proyecto | Clips | Estado |
|---------|----------|-------|--------|
| 1.1 | La carga y el campo eléctrico | 4 | pendiente |
| 1.2 | La corriente y el campo magnético | 4 | pendiente |
| 1.3 | La fuerza de Lorentz | 4 | pendiente |
| 2.1 | La inducción de Faraday | 4 | pendiente |
| 2.2 | Las ecuaciones de Maxwell | 4 | pendiente |
| 2.3 | La onda electromagnética | 4 | pendiente |
| 3.1 | Las líneas de transmisión | 4 | pendiente |
| 3.2 | La reflexión y la onda estacionaria | 4 | pendiente |
| 3.3 | Las antenas | 4 | pendiente |
| 4.1 | La ionosfera | 4 | pendiente |
| 4.2 | El enlace con el satélite | 4 | pendiente |
| 4.3 | El clima, el ruido y el margen | 4 | pendiente |

Módulo 1 presenta los campos quietos, el 2 los casa y saca la onda, el
3 la guía hasta la antena y la suelta, el 4 la lleva al espacio y la
trae de vuelta convertida en bits.

## Paleta de la familia

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_CARGA` | `#f43f5e` rojo | las FUENTES: cargas, corrientes, el emisor |
| `C_E` | `#f59e0b` ámbar | campo eléctrico |
| `C_B` | `#34d399` verde | campo magnético |
| `C_ONDA` | `#a78bfa` violeta | la onda: E y B viajando juntos; la señal radiada |
| `C_CALCULO` | `#22d3ee` cian | lo que se CALCULA o se mide: umbrales, cifras, resultados |
| `C_EJE` | `#31414f` | mobiliario (ejes, guías, muescas) |

Regla de color, columna vertebral de la familia: **el color dice quién
actúa**. Rojo = la fuente que crea; ámbar = el campo eléctrico; verde =
el magnético; violeta = los dos casados y viajando; cian = el número
que sale de la cuenta. El espectador debe poder distinguir «qué campo
estoy viendo» sin oír la narración. No mezclar roles. El gris `C_EJE`
es mobiliario: el objeto del que habla el clip va en `C_TENUE` o en su
color de rol, nunca en `C_EJE` (desaparece sobre el fondo).

## Contrato de la librería `manim_extensions/electromagnetismo.py`

Determinista, sin red, sin archivos, sin azar. Mismo estilo que
`aerodinamica.py`: subclases de `VGroup` con localizadores que leen la
posición ACTUAL del mobject (siguen `move_to`/`shift`, **no** `scale`;
la escala se fija al construir con `ancho`/`alto`). Topes duros con
`ValueError`. Métodos nunca llamados como atributos de `Mobject`
(`color_de`, no `color`).

### Números (la fuente única de la verdad)

Todo rótulo con cifra sale de aquí o del `style_block`, nunca escrito a
mano en el clip. Validados contra valores publicados (CODATA, ITU-R
P.838-3, WR-90, órbita de Clarke):

```python
# módulo 1
coulomb(q1, q2, r)            # N; k = 8.9875e9
campo_puntual(q, r)           # V/m
campo_dipolo_eje(p, r)        # ~ 2kp/r^3: cae con el CUBO
b_hilo(I, r)                  # mu0 I / 2 pi r  (1 A a 1 m -> 2e-7 T)
b_solenoide(n, I)             # mu0 n I  (1000 esp/m, 10 A -> 12.6 mT)
b_tierra(r_re)                # dipolo: 31.2 uT * (1/r)^3 en el ecuador
radio_larmor(q, m, v, B)      # e- a 1e7 m/s en 50 uT -> 1.14 m
frecuencia_giro(q, m, B)      # e- en 50 uT -> 1.40 MHz
par_torquer(m_dip, B)         # tau = m B; 0.2 A m2 en 30 uT -> 6e-6 N m
tiempo_giro_torquer(m_dip, B, inercia, angulo)  # 1U, 90° -> ~32 s

# módulo 2
fem_espira(n, B, area, omega) # pico N B A w (100, 0.1 T, 100 cm2, 50 Hz -> 31.4 V)
c_de_constantes()             # 1/sqrt(mu0 eps0) = 299 792 458 m/s EXACTO
impedancia_vacio()            # sqrt(mu0/eps0) = 376.73 ohm
lambda_de(f), f_de(lam)       # c = lambda f
campo_de_flujo(S)             # E_pico = sqrt(2 eta0 S); sol 1361 W/m2 -> 1013 V/m
BANDAS                        # tabla (nombre, f_min, f_max, uso satelital)

# módulo 3
z0_coaxial(D_d, er)           # (59.96/sqrt(er)) ln(D/d); er 2.25, D/d 6.52 -> 75
z0_bifilar(...)               # opcional para el clip del telegrafista
gamma_de(ZL, Z0)              # (ZL-Z0)/(ZL+Z0); 75 en 50 -> 0.2
swr_de(gamma)                 # (1+|g|)/(1-|g|); 0.2 -> 1.5
z_cuarto(Z1, Z2)              # sqrt(Z1 Z2); 50-75 -> 61.2
fc_te10(a)                    # c/2a; WR-90 (22.86 mm) -> 6.557 GHz
patron_dipolo_corto(theta)    # sen(theta)
patron_dipolo_medio(theta)    # cos(pi/2 cos t)/sen t; D = 1.643 = 2.15 dBi
ganancia_apertura(D, f, ef)   # ef (pi D/lambda)^2; 60 cm, 12 GHz, 0.6 -> 35.3 dBi
factor_array(n, d_l, fase, theta)  # steering por rampa de fase

# módulo 4
frecuencia_plasma(ne)         # 8.98 sqrt(Ne) Hz; 1e12 m-3 -> 8.98 MHz
retardo_iono(tec, f)          # 40.3 TEC / f^2 / c; 50 TECU en L1 -> 8.1 m
radio_geo()                   # (mu T_sid^2/4pi^2)^(1/3) = 42 164 km -> h 35 786
fspl_db(d, f)                 # 20 log10(4 pi d/lambda); GEO Ku -> 205.1 dB
flujo_isotropo(P, d)          # P/4pi d^2; 100 W a GEO -> 6.2e-15 W/m2
v_orbital(h), t_orbital(h)    # 550 km -> 7.59 km/s, 95.6 min
doppler_pase(h, f, ...)       # curva S del pase, de la geometría real
atenuacion_lluvia(f, R)       # ITU-R P.838-3 k R^alpha (tabla kH/aH embebida)
ruido_dbw(T, B)               # 10 log10(k T B); 150 K, 36 MHz -> -131.3 dBW
```

`b_tierra`, `radio_geo` y compañía levantan `ValueError` fuera de su
dominio (r < 1 R_E, frecuencias no positivas…) en vez de devolver
números: un número inventado callando es peor que un error.

### Piezas (por lección)

```python
# 1.1
carga(signo, ...)                 # punto con halo y signo; .punto()
lineas_campo(cargas, ...)         # líneas E integradas de verdad; .linea(i)
curva_inverso(exponente, ...)     # F~1/r^2 o E_dipolo~1/r^3; .punto_de(r)
mapa_dipolo(...)                  # dipolo +/- con líneas y equipotenciales
                                  # .equipotencial(i), .linea(i), .cargas
# 1.2
hilo_corriente(...)               # hilo + círculos de B + brújulas; .circulo(i)
solenoide_corte(n_espiras, ...)   # corte con puntos/cruces y B uniforme
tierra_iman(...)                  # Tierra + líneas de dipolo; .linea(i),
                                  # .punto_en(linea, f) para partículas
cubesat_torquer(...)              # cubesat + bobina + B + par; .a_angulo(a)
# 1.3
giro_larmor(...)                  # trayectoria circular/espiral calculada
espejo_magnetico(...)             # botella: espiral que rebota (sobre tierra_iman)
mapa_cinturones(...)              # cortes de los cinturones + órbitas LEO/MEO/GEO
                                  # .orbita(nombre), .cinturon(i)
tubo_ondas(...)                   # TWT: hélice, haz, onda que crece; .a_fase(f)
# 2.1
espira_iman(...)                  # imán + bobina + galvanómetro; .a_posicion(x)
curva_flujo(...)                  # Phi(t) arriba y -dPhi/dt abajo, alineadas
alternador(...)                   # espira que gira + senoide que se escribe
transformador(n1, n2, ...)        # dos devanados; .relacion()
# 2.2
caja_gauss(...)                   # carga + superficie + flechas de flujo
condensador_ampere(...)           # placas + lazo de Ampère + corriente desplaz.
tarjetas_maxwell(...)             # las 4 ecuaciones; .tarjeta(i), .simetria()
calculo_c(...)                    # mu0 y eps0 multiplicándose hasta c
# 2.3
onda_em(...)                      # E (ámbar) y B (verde) perpendiculares
                                  # viajando; .a_fase(f), .vector_e(x)
esfera_flujo(...)                 # frente esférico + parche de antena; .a_radio(r)
traza_polarizacion(tipo, ...)     # lineal/circular; .a_fase(f)
banda_espectro_em(...)            # eje log de bandas L..Ka; .banda(nombre),
                                  # .punto_de(f)
# 3.1
cable_vs_lambda(...)              # cable con onda encima a varias f
linea_lc(n_celdas, ...)           # escalera LC + pulso saltando; .celda(i)
corte_coaxial(...) / corte_microstrip(...)  # secciones con E/B dentro
curva_atenuacion_cable(...)       # dB/100m vs f; .punto_de(f)
# 3.2
onda_estacionaria(gamma, ...)     # incidente+reflejada+envolvente; .a_fase(f)
                                  # .envolvente, .swr()
frontera_z(...)                   # dos medios + flechas incid/refl/trans
linea_cuartos(...)                # tramos con Z0 rotulada; .tramo(i)
guia_te10(...)                    # guía + patrón del modo + curva de corte
# 3.3
dipolo_radiante(...)              # cargas oscilando + frentes que se sueltan
patron_polar(funcion, ...)        # patrón en polares de CUALQUIER función
                                  # .punto_de(theta), .lobulo()
parabola_foco(...)                # rayos al foco; .rayo(i), .foco()
array_fases(n, ...)               # elementos + rampa de fase + haz; .a_fase(df)
# 4.1
capas_ionosfera(...)              # perfil Ne(h) día/noche + capas D/E/F
rebote_hf(...)                    # tierra curva + saltos ionosféricos; .salto(i)
ventana_iono(...)                 # rayos que rebotan o cruzan según f
retardo_gps(...)                  # dos portadoras, dos retardos; .barra(f)
# 4.2
diagrama_orbitas(...)             # Tierra a escala + LEO/MEO/GEO; .orbita(h),
                                  # .periodo(h)
esfera_reparto(...)               # la potencia sobre la esfera creciente
                                  # + el parche que recoge la antena
pase_leo(...)                     # horizonte + arco del pase + elevación
                                  # .a_tiempo(t), .elevacion(t), .distancia(t)
curva_doppler(...)                # la curva S del pase; .punto_de(t)
# 4.3
lluvia_atenuacion(...)            # curvas dB/km 12/20/30 GHz; .punto_de(f, R)
cielo_ruido(...)                  # antena al cielo (frío) vs al suelo (caliente)
margen_enlace(...)                # SNR vs tiempo con desvanecimiento y umbral
                                  # .a_tiempo(t), .umbral
arco_familia(...)                 # el recap: carga→campo→onda→antena→espacio→bit
```

`lineas_campo` integra las líneas con RK4 sobre el campo real de las
cargas (no dibuja arcos a ojo): la simetría del dipolo y la
equidistancia en la carga aislada salen solas, no impuestas.
`patron_polar` recibe la FUNCIÓN, así el dipolo corto, el λ/2 y el
array pintan con la misma pieza y no pueden discrepar de los números.
`pase_leo` y `curva_doppler` comparten la misma geometría orbital: la
elevación, la distancia y el Doppler de un instante salen del mismo
cálculo.

## Módulo 1 — Los campos quietos

### Lección 1.1 — La carga y el campo eléctrico

Hilo: la carga y su ley 1/r² → el campo como mapa → el dipolo (la
semilla de toda antena) → el potencial como mapa de la energía.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | La carga y la ley de Coulomb | dos cargas, la fuerza medida, la curva 1/r² | curva 1/r² con dos puntos rotulados (r y 2r → F/4) |
| 2 | El campo: el mapa del empuje | líneas de la carga aislada; entra la segunda y el mapa se recombina | mapa de dos cargas iguales con su punto de silla |
| 3 | El dipolo: la semilla de la antena | +q y −q juntas; el mapa del dipolo; la curva 1/r³ contra 1/r² | mapa del dipolo + curva comparada; «toda antena es esto oscilando» |
| 4 | El potencial: el mapa de la energía | equipotenciales sobre el mapa; mover una carga cuesta | equipotenciales + cierre «El campo empuja. / El potencial cobra.» |

### Lección 1.2 — La corriente y el campo magnético

Hilo: Oersted → Ampère y el solenoide → la Tierra es un imán → el
magnetorquer (girar un satélite sin combustible).

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | La brújula que se tuerce | hilo con corriente, brújulas en círculo, B = μ₀I/2πr | hilo + círculos de B + la cifra 2·10⁻⁷ T a 1 m de 1 A |
| 2 | Ampère y el solenoide | espiras sumando; dentro uniforme, fuera casi nada | corte del solenoide con B = μ₀nI = 12.6 mT |
| 3 | La Tierra es un imán | dipolo terrestre, 31 µT en el ecuador, cae con el cubo | Tierra + líneas + curva B(r) con GEO marcada |
| 4 | Girar un satélite sin combustible | cubesat + bobina + τ = m×B; 90° en ~32 s | cubesat girado + cierre «La Tierra empuja gratis. / Solo hay que saber pedirle.» |

### Lección 1.3 — La fuerza de Lorentz

Hilo: la fuerza que desvía sin trabajar → partículas atrapadas → los
cinturones y las órbitas → el TWT, el amplificador de a bordo.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | La fuerza que no empuja: desvía | q v×B, giro de Larmor; e⁻ a 10⁷ m/s en 50 µT gira en 1.14 m | círculo de Larmor + F siempre al centro + cifras |
| 2 | Atrapados en el campo | espiral a lo largo de una línea; el espejo magnético rebota | botella magnética con la partícula rebotando |
| 3 | Los cinturones y las órbitas | cortes de Van Allen; LEO por debajo, GPS dentro, GEO al borde | mapa cinturones + 3 órbitas rotuladas |
| 4 | El amplificador del satélite | TWT: el haz cede energía a la onda que viaja por la hélice | onda de salida crecida + cierre «Los campos quietos ya son tuyos. / Ahora vamos a moverlos.» |

## Módulo 2 — Maxwell: el matrimonio de los campos

### Lección 2.1 — La inducción de Faraday

Hilo: el flujo que cambia enciende corriente → Lenz pone el signo → el
alternador escribe la primera senoide → el transformador la transporta.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | El flujo que cambia | imán entra/sale de la bobina; Φ(t) y −dΦ/dt alineadas | las dos curvas alineadas: fem solo donde Φ cambia |
| 2 | Lenz: el signo que frena | la corriente inducida se opone; frenado magnético | espira frenando al imán + «el signo menos es conservación de la energía» |
| 3 | El alternador: nace la senoide | espira girando en B; la senoide se escribe sola; pico NBAω | senoide completa + 31.4 V de pico calculados |
| 4 | El transformador | dos devanados, relación N₁/N₂; subir para viajar, bajar para usar | transformador + cierre «Mover un imán hace corriente. / ¿Y si nada se moviera?» |

### Lección 2.2 — Las ecuaciones de Maxwell

Hilo: las dos de Gauss → el término que faltaba → los cuatro renglones
→ la sorpresa: una velocidad conocida.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Las dos de Gauss | flujo por una superficie cerrada; con carga sí, magnético jamás | las dos tarjetas de Gauss: ρ/ε₀ contra 0 |
| 2 | El término que faltaba | el condensador rompe a Ampère; la corriente de desplazamiento lo arregla | condensador + lazo + término de Maxwell en ámbar |
| 3 | Cuatro renglones | las 4 ecuaciones; la simetría ∂B/∂t ↔ ∂E/∂t resaltada | las cuatro tarjetas con la simetría en color |
| 4 | La sorpresa: una velocidad | μ₀ y ε₀ (dos números de mesa de laboratorio) → 1/√(μ₀ε₀) = 299 792 458 | la cuenta hecha + cierre «La luz no viaja por el campo. / La luz ES el campo.» |

### Lección 2.3 — La onda electromagnética

Hilo: la estructura de la onda → la energía que transporta → la
polarización → el mapa de bandas de las telecomunicaciones.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | El campo que viaja solo | E (ámbar) ⊥ B (verde) ⊥ marcha; λf = c | onda congelada con λ acotada y λf = c |
| 2 | La energía a bordo | Poynting; η₀ = 377 Ω; la luz del Sol lleva 1 kV/m | flujo + 376.73 Ω + el 1013 V/m del Sol |
| 3 | La polarización | lineal V/H, circular; dos señales en la misma frecuencia | trazas V/H/circular + «los satélites emiten las dos a la vez» |
| 4 | El mapa de las bandas | eje log de L a Ka; qué viaja por cada banda y por qué | banda espectral rotulada + cierre «Ya tienes la onda. / Ahora hay que llevarla a su antena.» |

## Módulo 3 — Guiar y soltar la onda

### Lección 3.1 — Las líneas de transmisión

Hilo: cuándo un cable deja de ser un cable → el telegrafista y Z₀ → la
geometría manda → las pérdidas mandan más.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Cuando el cable despierta | el mismo cable a 50 Hz y a 1 GHz; la regla ℓ > λ/10 | cable con la onda entera dentro + la regla |
| 2 | El telegrafista: Z₀ = √(L/C) | escalera LC, el pulso salta celda a celda | escalera + Z₀ = 50 Ω y 75 Ω como geometrías |
| 3 | Coaxial y microstrip | cortes con el campo dentro; Z₀ desde D/d y εr | los dos cortes + 75 Ω del coaxial calculado |
| 4 | Los decibelios que cobra el cable | atenuación vs f; por eso el LNB vive EN el foco | curva dB/100 m + cierre «Amplifica primero. / Cablea después.» |

### Lección 3.2 — La reflexión y la onda estacionaria

Hilo: la frontera devuelve la onda → la onda que no viaja → adaptar
con λ/4 → la guía de onda como pasillo.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Γ: lo que devuelve la frontera | abierto, corto y adaptado; Γ = (Z_L−Z₀)/(Z_L+Z₀) | tres casos con su Γ (−1, +1, 0) |
| 2 | La onda que no viaja | incidente + reflejada = estacionaria; SWR | envolvente + SWR 1.5 del caso 75→50 |
| 3 | El transformador de λ/4 | un tramo de √(Z₁Z₂) = 61.2 Ω lo adapta | línea adaptada, reflejo apagado |
| 4 | La guía de onda | el pasillo con paredes; TE₁₀ y su frecuencia de corte | guía WR-90 + fc = 6.557 GHz + cierre «Guiar ya sabes. / Falta soltar.» |

### Lección 3.3 — Las antenas

Hilo: la carga que oscila radia → el patrón y la ganancia → la
parabólica → el array en fase.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | La carga que oscila radia | el dipolo λ/2: frentes que se sueltan; resonancia | dipolo radiando + λ/2 acotado |
| 2 | El patrón: concentrar, no crear | el donut del dipolo en polares; 2.15 dBi | patrón polar + «la ganancia se roba de otras direcciones» |
| 3 | La parabólica | rayos al foco; G = η(πD/λ)²; 60 cm → 35.3 dBi | parábola + la cifra del plato de balcón |
| 4 | El array en fase | rampa de fase → el haz gira sin moverse nada | array apuntando + cierre «Miles de antenas quietas / apuntando a un satélite que corre.» |

## Módulo 4 — El enlace por el espacio

### Lección 4.1 — La ionosfera

Hilo: el techo eléctrico → el espejo de la onda corta → la ventana al
espacio → el peaje que paga el GPS.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | El techo eléctrico | el Sol enciende capas D/E/F; perfil Ne(h) día/noche | perfil con las capas rotuladas |
| 2 | El espejo de la onda corta | f < fp rebota; saltos múltiples dan la vuelta al mundo | rebote multi-salto sobre la Tierra curva |
| 3 | La ventana al espacio | subir la frecuencia hasta cruzar; por eso satcom vive arriba | rayos: HF rebota, VHF/SHF cruzan |
| 4 | El peaje del GPS | retardo ∝ TEC/f²; 8 m en L1; dos frecuencias lo cancelan | barras de retardo L1/L2 + cierre «La ionosfera cobra peaje. / El GPS paga con dos monedas.» |

### Lección 4.2 — El enlace con el satélite

Hilo: la órbita que no se mueve del cielo → la esfera que se reparte →
GEO contra LEO → el pase de un LEO.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | La órbita quieta | T = 24 h fija el radio: 42 164 km; el arco de Clarke | Tierra + GEO a escala + la cuenta del radio |
| 2 | La esfera que se reparte | 100 W repartidos en una esfera de 36 000 km: 6·10⁻¹⁵ W/m² | esfera + parche de antena + la cifra monstruosa |
| 3 | GEO contra LEO | 65× la distancia = 36 dB; 240 ms contra 4 ms | comparación a escala con las dos cifras |
| 4 | El pase: siete minutos | horizonte a horizonte; elevación, distancia y la S del Doppler | pase completo + curva S + cierre «GEO espera quieto. / LEO hay que cazarlo.» |

### Lección 4.3 — El clima, el ruido y el margen

Hilo: la lluvia que apaga la Ka → escuchar el frío del cielo → el
margen del enlace → el cierre de la familia.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | La lluvia que apaga la Ka | gotas del tamaño de la onda; dB/km a 12/20/30 GHz | curvas de lluvia con las tres bandas |
| 2 | Escuchar el frío del cielo | la antena al cielo ve 20 K; al suelo, 290 K; kTB | termómetros + N = kTB en dBW |
| 3 | El margen | SNR contra umbral; entra la tormenta y se lo come | curva de SNR cruzando el umbral y volviendo |
| 4 | De la carga al bit | el recap de la familia entera, pieza a pieza | cadena carga→campo→onda→línea→antena→espacio→bit + cierre de familia |

## Trampas propias (cosecha de las 12 lecciones)

- **Un localizador debe anclar en coordenadas de CONSTRUCCIÓN, no en el
  centro del bounding box.** `_Anclada._desde` sumaba el centro del grupo:
  correcto solo si la pieza nace centrada en ORIGIN. Una pieza asimétrica
  (la media cúpula de `pase_leo`, la flecha de marcha de `onda_em`)
  desplazaba TODOS sus localizadores. Corregido en la librería; los
  `punto_en` de `lineas_campo`/`tierra_iman` ya usaban la forma buena.
- **La envolvente de `onda_estacionaria` llevaba el signo del término
  cruzado invertido** (+2γcos2kx en vez de −2γcos2kx): quedaba corrida
  λ/4 de su propia onda y la suma se le salía por arriba. La detectó el
  clip 3.2.2 al ver que los localizadores de máximo/mínimo (correctos)
  caían fuera de la envolvente pintada.
- Un punto rotulado en el EXTREMO IZQUIERDO de un `haz_curvas` choca con
  la etiqueta del eje Y (que vive sobre el origen): anclar el tag en
  `DR`/`DOWN`, no en `UR`/`UP`.
- `tag_junto` (Rajdhani fs 18) come los espacios en frases multi-palabra
  («lazodeAmpère»): las etiquetas técnicas multi-palabra van en `tag_hud`
  (Space Mono, ASCII).
- Rajdhani no trae λ ni ²: un pie con «(D/λ)²» sale con glifos de
  fallback. Reescribir con palabras o pasar a MathTex.
- `to_corner(UR)` para cifras choca con el título y el corchete del HUD:
  la convención de la familia es `to_corner(UR, buff=0.55).shift(DOWN*0.5)`.
- Piezas con partes que se añaden a escena por separado no se apagan con
  un `FadeOut` del padre (quedan en `scene.mobjects` a opacidad 0): se
  apagan por partes.
- `arcsin(-0.0)` con formato `:+.1f` imprime «-0.0 deg»: normalizar con
  `+ 0.0` antes de formatear.
- Asperezas documentadas y rodeadas SIN tocar la librería (candidatas a
  limpieza futura): las líneas de `caja_gauss("magnetica")` no escalan
  con `radio_superficie`; `condensador_ampere` trae unas `flechas_e`
  estáticas que compiten con `e_a()`; las cargas de `dipolo_radiante` no
  escalan con `largo_brazo` y van en ámbar sobre brazos rojos; el
  termómetro de `cielo_ruido("suelo")` cruza el cono; `margen_enlace` no
  acepta etiquetas de eje; el trayecto de `pase_leo` es elevación-vs-
  tiempo (un pase cenital dibuja un pico, no una cúpula — fiel a la
  física); las barras de `array_fases` saturan en 1.35 e invaden la
  franja del pie con rampas grandes.

## Trampas heredadas (de Aerodinámica, aplican tal cual)

- Piezas que se reconstruyen en animación se anclan a un submobject
  fijo, nunca a coordenadas de construcción ni al centro del grupo.
- `Arc` explícito, no `Angle` (elige cuadrante solo).
- `ReplacementTransform` + reasignar la variable, nunca `Transform` si
  después se usan localizadores.
- Etiquetas fuera de las barras rellenas; cifras de haces de curvas
  FUERA de la caja de ejes, a la altura del punto y de su color.
- `set_stroke(opacity=…)`, jamás `set_opacity` sobre contornos.
- Poligonal densa a través de discontinuidades, no
  `set_points_smoothly`.
- `MathTex` partido en argumentos para recuadrar, no índices de glifo.
- Espera de pie ≥ 4.6 s; recortar quitando beats, no acortándolos.
- Space Mono no tiene superíndices unicode: `10⁶` se escribe con
  `MathTex` o como `10^6` en Space Mono plano.
