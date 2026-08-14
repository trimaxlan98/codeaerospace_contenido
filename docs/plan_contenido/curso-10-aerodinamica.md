# Curso 10 — Aerodinámica (familia de lecciones)

- **Fuente**: documento maestro de curso autogestivo *Aerodinámica II —
  Flujo compresible y aerodinámica de alta velocidad* (4 semanas, 4
  módulos, 20 lecciones, 83 subtemas).
- **Título de la familia**: `Aerodinámica`, **sin el II**. Es una
  decisión explícita del cliente: el material se va a reciclar en otros
  programas donde la numeración del plan de estudios no aplica, y un
  título atado a "II" lo haría inservible fuera de esta licenciatura.
- **Público**: divulgación técnica; asume Aerodinámica I (flujo
  incompresible, perfiles, sustentación) y termodinámica básica.

## La decisión de granularidad

A diferencia de los cursos 1-13, **un proyecto de ManimStudio no es un
curso entero: es una lección**. Cada uno de los 4 clips de un proyecto
es un subtema del documento.

```
documento          ManimStudio
-----------------  ----------------------------------------
módulo   (4)   →   —  (agrupación editorial, no existe en la DB)
lección  (20)  →   proyecto  "Aerodinámica · N.M <título>"
subtema  (83)  →   clip      "MODULO 0K" en el HUD
```

El HUD ya rotulaba cada clip como `MODULO NN` en los trece cursos
anteriores, así que el vocabulario encaja: dentro de una lección, cada
clip es un módulo. Consecuencias:

- Una lección son **4 clips de 33-45 s** ≈ 2.5-3 min de video, contra
  los ~5 min de los cursos anteriores. Es lo correcto para material
  autogestivo: una unidad breve por sesión de estudio.
- Los 20 proyectos comparten **una sola librería** (`aerodinamica.py`) y
  **un solo `style_block`**: el molde. Entre dos lecciones, el
  `style_block` solo difiere en la cabecera y en su bloque
  `# --- Numeros de la leccion ---`. Cualquier otra diferencia es un
  error de copia.
- Los slugs son `aerodinamica-N-M-<tema>`, ordenables alfabéticamente.

## Mapa de las 20 lecciones

| Lección | Proyecto | Subtemas | Estado |
|---------|----------|----------|--------|
| 1.1 | El número de Mach y los regímenes de vuelo | 4 | **hecha** |
| 1.2 | Repaso de termodinámica aplicada | 4 | **hecha** |
| 1.3 | La velocidad del sonido | 4 | **hecha** |
| 1.4 | Ecuaciones de conservación para flujo compresible | 4 | **hecha** |
| 1.5 | Propiedades de estancamiento y relaciones isentrópicas | 4 | **hecha** |
| 2.1 | Naturaleza física de la onda de choque | 4 | **hecha** |
| 2.2 | Relaciones de la onda de choque normal | 4 | **hecha** |
| 2.3 | Medición de velocidad en flujo compresible | 4 | **hecha** |
| 2.4 | Flujo cuasi-unidimensional en conductos | 4 | **hecha** |
| 2.5 | Toberas convergentes y De Laval | 5 | **hecha** |
| 3.1 | Ondas de choque oblicuas | 4 | pendiente |
| 3.2 | La relación θ-β-M | 4 | pendiente |
| 3.3 | Reflexión e interacción de ondas | 4 | pendiente |
| 3.4 | Expansión de Prandtl-Meyer | 4 | pendiente |
| 3.5 | Teoría de choque-expansión aplicada a perfiles | 5 | pendiente |
| 4.1 | Ecuación del potencial de perturbación linealizada | 4 | pendiente |
| 4.2 | Correcciones de compresibilidad subsónica | 4 | pendiente |
| 4.3 | Número de Mach crítico y divergencia del arrastre | 4 | pendiente |
| 4.4 | El régimen transónico y sus soluciones de diseño | 4 | pendiente |
| 4.5 | Teoría supersónica linealizada y panorama hipersónico | 5 | pendiente |

**Los módulos 1 y 2 están completos** (lecciones 1.1-2.5, 41 clips). El 1
fija el idioma; el 2 lo usa para romper el aire de frente. Quedan los
módulos 3 (ondas oblicuas) y 4 (transónico y linealizado).

## Paleta de la familia

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_SUB` | `#34d399` verde | subsónico: el aire se aparta a tiempo |
| `C_TRANS` | `#f59e0b` ámbar | transónico: conviven sub y supersónico |
| `C_SUPER` | `#f43f5e` rojo | supersónico: choques, arrastre de onda |
| `C_HIPER` | `#a78bfa` violeta | hipersónico: calor y química |
| `C_CALCULO` | `#22d3ee` cian | lo que se CALCULA: umbrales, resultados, energía térmica |
| `C_EJE` | `#31414f` | mobiliario (ejes, guías, muescas) |

Regla de color, la columna vertebral de la familia: **el color dice a
qué velocidad se vuela; cuanto más rápido, más caliente**. El espectador
debe poder leer una banda de regímenes o un diagrama de ondas sin oír la
narración. No mezclar roles.

Corolario práctico aprendido en las cuatro primeras lecciones: el gris
`C_EJE` es para mobiliario de fondo y **no** para el objeto del que habla
el clip. Un conducto o un tubo pintados con él desaparecen sobre el
fondo negro; van en `C_TENUE`.

## Contrato de la librería `manim_extensions/aerodinamica.py`

Determinista, sin red, sin archivos, sin azar (ni siquiera con semilla,
salvo las posiciones de las partículas del pistón, que se fijan una vez y
después solo se escalan). Mismo estilo que `enlace.py` / `espectro.py`:
subclases de `VGroup` con localizadores que leen la posición ACTUAL del
mobject. Topes duros que levantan `ValueError`: `MUESTRAS_MAX = 400`,
`ONDAS_MAX = 12`, `ZONAS_MAX = 6`.

**Limitación conocida y deliberada**: los localizadores siguen un
`move_to` o un `shift`, pero **no** un `scale`. La escala se elige al
construir (`ancho`, `alto`) y no se toca después. Es la misma regla que
en el resto de librerías del repo.

### Números (la fuente única de la verdad)

```python
velocidad_sonido(T)         # a = sqrt(gamma R T)
isa(h)                      # -> (T, p, rho, a), dos tramos hasta 20 km
razon_densidad(M)           # rho0/rho = (1 + 0.2 M^2)^2.5
error_incompresible(M)      # cuanto miente la densidad constante
mach_de_error(f)            # inversa en forma cerrada: f=0.05 -> M=0.314
razon_energias(M)           # (V^2/2)/e = 0.28 M^2
angulo_mach(M)              # mu = arcsen(1/M), en grados
razon_temperatura(M)        # T0/T = 1 + 0.2 M^2
fraccion_cinetica(M)        # 1 - T/T0
zona_de(M)                  # 'Subsónico' | 'Transónico' | ...
```

Todo rótulo con una cifra sale de aquí o del `style_block`. La curva
dibujada y el número escrito no pueden discrepar; ese es el motivo de que
`mach_de_error(0.05)` exista en vez de escribir `0.3` a mano (vale
**0.314**, y el 0.3 de los libros es ese número redondeado a la baja).

### Piezas

```python
# leccion 1.1
curva_compresibilidad(m_max, umbral, ...)  # .punto_de(M), .error(M),
                                           # .banda, .umbral, .etiquetas
balanza_energias(mach, ...)                # .a_mach(M), .razon(), .reparto()
banda_regimenes(...)                       # .punto_de(M, altura), .zona_de(M),
                                           # .color_de(M), .zona(i)
frentes_moviles(mach, n_ondas, paso, ...)  # .con_mach(M), .fuente(), .mu(),
                                           # .cono, .onda(k)

# leccion 1.2
piston_gas(fraccion, ...)                  # .a_fraccion(f), .presion_rel()
barras_calores(...)                        # .valor('cv'|'R'|'cp'|'gamma')
volumen_control(..., con_calor, con_trabajo)  # .punto_entrada(), .punto_salida()
diagrama_ts(...)                           # .punto_de(s,T), .estado(), .trayecto()

# leccion 1.3
pulso_conducto(avance, ...)                # .a_avance(f), .x_frente(), .rotulo
curva_sonido(t_rango, ...)                 # .punto_de(T), .a(T)
perfil_isa(h_max, ...)                     # .punto_de(h), .a(h), .temperatura(h)
curva_mu(m_rango, ...)                     # .punto_de(M), .mu(M)

# leccion 1.4
conducto(perfil, area_garganta, ...)       # .punto_de(x, y_rel), .area(x),
                                           # .garganta(), .paredes, .eje
barras_entalpia(mach, ...)                 # .a_mach(M), .fraccion()

# leccion 1.5
remanso(radio, n_lineas, ...)              # .punto(), .linea(i), .cuerpo
curvas_isentropicas(m_max, ...)            # .punto_de(i, M), .valor(i, M),
                                           # .color_de(i), .vertical_en(M)
tabla_isentropica(machs, ...)              # .fila(i), .celda(i,j),
                                           # .columna(j), .valor(i,j),
                                           # .resaltar(i)

# modulo 2 — numeros
choque_normal(M1)                          # -> M2, p2/p1, T2/T1,
                                           #    rho2/rho1, p02/p01
rayleigh_pitot(M1)                         # p02/p1 con choque desprendido
error_anemometro(M)                        # cuanto miente 1/2 rho V^2
mach_de_area(A/A*, rama)                   # invierte A/A* por biseccion

# modulo 2 — piezas
diagrama_xt(n_ondas, ...)                  # .caracteristica(i), .choque,
                                           # .coalescencia()
perfil_choque(salto, espesor_rel, ...)     # .curva, .escala
esquema_schlieren(n_rayos, desviados, ...) # .rayos, .onda, .cuchilla,
                                           # .pantalla, .banda
curvas_choque(grupo, m_max, ...)           # grupo 'saltos'|'perdidas';
                                           # .valor(i,M1), .color_de(i),
                                           # .vertical_en, .horizontal_en
curva_anemometro(m_max, umbral, ...)       # .punto_de(M), .error(M)
escalera_velocidades(tas, altitud, ...)    # .barra(i), .valor(i), .nombre(i)
curva_area_mach(m_max, ...)                # .rama_sub, .rama_super,
                                           # .mach_de(A,rama), .horizontal_en
perfil_tobera(area_garganta, regimenes,…)  # .tubo, .curva(k), .choque(k),
                                           # .mach(k,x), .presion(k,x),
                                           # .salida(k), .punto_de(k,x)
```

`choque_normal` levanta `ValueError` con M1 < 1 en vez de devolver
números: un choque de expansión viola la segunda ley y es justo el asunto
del clip 3 de la 2.1. Devolver algo ahí lo dejaría pasar callando.

`perfil_tobera` es la figura grande del módulo: resuelve la tobera régimen
a régimen invirtiendo A/A* en la rama que toca, y en el caso con choque
interno aplica el **A\* nuevo** que impone la pérdida de presión de
estancamiento (A\*₂ = A\*₁·p₀₁/p₀₂). De ahí sale sola la propiedad que el
clip cuenta: las tres curvas bloqueadas coinciden exactamente en el
convergente y solo se separan pasada la garganta.

Los cuatro grupos de números cuadran con NACA 1135 dentro del redondeo
publicado (desvío máximo 5·10⁻⁵).

La tabla **se genera, no se transcribe**: cada celda se evalúa con las
mismas funciones que dibujan las curvas, así que no puede traer una errata
de copia ni discrepar de la gráfica. Sus cinco filas coinciden con NACA
1135 dentro del redondeo a cuatro decimales que publica el informe (desvío
máximo 4.8·10⁻⁵).

`conducto` acepta `'recto'`, `'convergente'`, `'divergente'` y
`'delaval'`; es la geometría sobre la que se escribirá todo el módulo 2,
por eso su `punto_de(x, y_rel)` devuelve la pared (`y_rel = ±1`) o el eje
(`0`) en cualquier estación.

**Decisión de diseño con trampa**: la `banda_regimenes` NO es lineal en
Mach. Cada régimen ocupa el mismo ancho en pantalla aunque el supersónico
abarque de 1.2 a 5 y el hipersónico de 5 a 30 — en un eje lineal, el
transónico (0.8-1.2), que es donde ocurre casi todo lo interesante, sería
una rendija. `punto_de` es continuo y monótono, así que el ORDEN de los
vehículos es verdad; la escala no. Las fronteras van rotuladas con su
número justamente para que se vea, y el clip 3 de la lección 1.1 lo dice
en voz alta en su último pie.

## Lección 1.1 — El número de Mach y los regímenes de vuelo

Hilo: el modelo incompresible caduca → qué mide realmente el número de
Mach → por qué M = 1 es una pared → quién vive en cada régimen.

| Clip | Subtema | Visual | `final_state` |
|------|---------|--------|---------------|
| 1 (44 s) | 1.1.1 | Curva del error de densidad; la banda verde y el 5 % la cortan en M = 0.314 | curva con banda, línea del 5 % y los puntos M 0.31 y M 0.80 (35 %) |
| 2 (42 s) | 1.1.2 | Balanza movimiento / térmica subiendo M 0.3 → 1 → 2 → 5 | balanza a M 5, ratio 7.00 |
| 3 (44 s) | 1.1.3 | Frentes de una fuente móvil 0 → 0.6 → 1 → 2, cono y μ; después la banda | banda de los cuatro regímenes con sus fronteras |
| 4 (40 s) | 1.1.4 | Cinco vehículos colgados de la banda por su Mach real | cierre: «Un solo número decide / qué ecuaciones puedes usar.» |

Pies clave (literales): *«Hasta Mach 0.31. Ese es el verdadero origen de
la regla del 0.3.»*, *«Por eso a Mach alto el aire no se aparta: se
calienta.»*, *«A Mach 1 el vehículo llega a la vez que su propio
aviso.»*, *«Ojo: los tramos no están a escala.»*

## Lección 1.2 — Repaso de termodinámica aplicada

Hilo: gas ideal y su R → dónde guarda el aire la energía → la primera ley
con el fluido pasando → la segunda ley como flecha.

| Clip | Subtema | Visual | `final_state` |
|------|---------|--------|---------------|
| 1 (39 s) | 1.2.1 | Émbolo: mismas partículas, medio volumen, doble presión | cilindro a 1/3, p ×3.1, y R = 8314/28.96 = 287 |
| 2 (42 s) | 1.2.2 | cv + R = cp como dos filas que miden lo mismo | las dos filas y γ = 1005/718 = 1.4 |
| 3 (38 s) | 1.2.3 | Volumen de control; caen Q y W y queda h0 constante | VC con 1 y 2, y h1+V1²/2 = h2+V2²/2 = h0 |
| 4 (43 s) | 1.2.4 | Plano T-s: camino isentrópico vertical contra el real, que deriva | cierre: «Casi todo este curso es isentrópico. / Salvo cuando aparece un choque.» |

## Lección 1.3 — La velocidad del sonido

Hilo: qué es un frente infinitesimal → de dónde sale la fórmula → cómo
cambia con la altitud → el cono.

| Clip | Subtema | Visual | `final_state` |
|------|---------|--------|---------------|
| 1 (39 s) | 1.3.1 | Escalón de presión recorriendo un tubo; delante nadie sabe nada | tubo casi teñido, frente junto al extremo |
| 2 (40 s) | 1.3.2 | a² = (∂p/∂ρ)s → a = √(γRT), y la curva a(T) | fórmula arriba y los puntos 340 / 295 m/s |
| 3 (33 s) | 1.3.3 | Perfil ISA; el mismo avión a 250 m/s a dos alturas | dos tarjetas: M 0.73 abajo, M 0.85 arriba |
| 4 (34 s) | 1.3.4 | Tres conos (M 1.2, 2, 5) y después μ(M) | cierre: «La velocidad del sonido no es un dato: / es el termómetro del aire.» |

El remate del clip 3 es el mejor gancho de la lección: subir de altitud
lleva al avión de subsónico a transónico **sin tocar los mandos**.

## Lección 1.4 — Ecuaciones de conservación

Hilo: las tres cuentas → las tres hipótesis → la entalpía total → el
volumen de control sobre un conducto. Cierra el módulo 1.

| Clip | Subtema | Visual | `final_state` |
|------|---------|--------|---------------|
| 1 (33 s) | 1.4.1 | VC y las tres ecuaciones integrales alineadas por el igual | las tres, en verde / ámbar / cian |
| 2 (37 s) | 1.4.2 | Conducto De Laval y las tres hipótesis entrando una a una | sección en la garganta y las tres etiquetas |
| 3 (37 s) | 1.4.3 | Barra apilada de altura FIJA que se reparte al acelerar | M 2.5, 56 % cinética, T0 300 K → T 133 K, V 579 m/s |
| 4 (38 s) | 1.4.4 | Dos secciones sobre el conducto y la continuidad | cierre: «Ya sabes qué se conserva. / Falta saber convertirlo.» |

El cierre del **módulo** no está aquí sino en la 1.5: el idioma no está
completo hasta tener las relaciones isentrópicas y sus tablas.

## Lección 1.5 — Propiedades de estancamiento y relaciones isentrópicas

Hilo: dónde se para el aire → las tres razones como una sola con tres
exponentes → los números fijos de Mach 1 → la tabla. Cierra el módulo 1.

| Clip | Subtema | Visual | `final_state` |
|------|---------|--------|---------------|
| 1 (40 s) | 1.5.1 | Líneas de corriente contra un cuerpo romo; la central muere en el morro | punto de remanso rotulado, −56 °C fuera y +117 °C en el morro |
| 2 (42 s) | 1.5.2 | Las tres razones cayendo con el Mach, etiquetas en columna con guías | T/T0, RHO/RHO0 y p/p0 hasta Mach 3 |
| 3 (38 s) | 1.5.3 | Corte vertical en Mach 1 y los tres valores críticos | 0.8333, 0.6339 y 0.5283 fuera de la caja de ejes |
| 4 (38 s) | 1.5.4 | La tabla generada; se lee la fila de Mach 2 y se señala A/A* | cierre: «Ya tienes el idioma. / Ahora toca romper el aire.» |

El caso del clip 1 es el mismo de siempre (11 km, Mach 2): fuera hace 56
bajo cero y el morro va a 117 grados. Es el gancho de la lección y sale
entero de `isa()` y `razon_temperatura()`.

## Módulo 2 — las cinco lecciones

| Lección | Clips | Duraciones | Hilo |
|---------|-------|------------|------|
| 2.1 Naturaleza de la onda de choque | 4 | 38.5 / 37.4 / 40.1 / 43.5 s | coalescencia → espesor → irreversibilidad → Schlieren |
| 2.2 Relaciones del choque normal | 4 | 37.9 / 36.8 / 33.8 / 39.7 s | la caja a caballo → Rankine-Hugoniot → los saltos → lo que cuesta |
| 2.3 Medir la velocidad | 4 | 37.5 / 38.0 / 39.5 / 43.2 s | Pitot compresible → Rayleigh → error del anemómetro → IAS/CAS/EAS/TAS |
| 2.4 Flujo cuasi-unidimensional | 4 | 39.0 / 36.8 / 36.5 / 39.7 s | la hipótesis → dA/A=(M²−1)dV/V → los cuatro casos → A/A* con dos ramas |
| 2.5 Toberas convergentes y De Laval | 5 | 40.5 / 43.5 / 36.8 / 33.7 / 44.0 s | bloqueo → regímenes → sobre/subexpandida → campanas → túnel |

Números de referencia del módulo, todos calculados y no transcritos: el
choque de M1 = 2 (p2/p1 = 4.50, T2/T1 = 1.69, M2 = 0.5774, p02/p01 =
0.7209), el techo de compresión (γ+1)/(γ−1) = 6, la lectura de Rayleigh a
Mach 2 (5.640 frente a los 7.824 de un Pitot que ignorase el choque), la
presión crítica 0.5283 que bloquea una tobera, y la De Laval de garganta
0.42 (A_e/A_t = 2.38 → M de salida 2.39).

## Trampas encontradas (para las lecciones que faltan)

- **Piezas que se reconstruyen en una animación** (`piston_gas`,
  `pulso_conducto`) no pueden guardar coordenadas absolutas de
  construcción: tras un `move_to` del grupo, las piezas nuevas aparecen
  donde el grupo *estaba*. Se anclan a un submobject que nunca cambia (el
  cilindro, el tubo) y se aplica la diferencia. No sirve el centro del
  grupo: crece y encoge con las propias barras.
- **`Angle` elige el cuadrante por su cuenta** y en el cono de Mach se
  queda con el reflejo (330°), que se lee como una circunferencia
  alrededor del emisor. Un `Arc` explícito de `180-μ` a `180` es
  inequívoco.
- **`Transform` no actualiza los atributos del mobject**: tras
  transformar unos `frentes_moviles`, `fuente()` —que se lee del centro
  actual— apunta a un sitio que ya no es el emisor. Con
  `ReplacementTransform` y reasignando la variable, cada objeto siempre
  es coherente consigo mismo.
- **Etiquetas dentro de una barra rellena del mismo color no se leen.**
  Van fuera, sobre negro.
- **Una pieza sin nombre propio no llega a la escena** si el clip
  enciende sus partes una a una (`FadeIn(pulso.tubo)`, …). Por eso
  `pulso_conducto` expone `.rotulo`.
- **Un método no puede llamarse como un atributo de `Mobject`.** Una pieza
  con `def color(self, i)` lo tiene sombreado por el `color` del propio
  mobject, y el clip acaba llamando a un `ManimColor`: `TypeError`. De ahí
  que sea `color_de`, como en `banda_regimenes`.
- **En un haz de curvas que caen juntas no hay hueco limpio para las
  cifras.** Ni a izquierda ni a derecha del punto: la propia curva pasa por
  ahí. La salida es sacarlas FUERA de la caja de ejes a la altura exacta de
  su punto, y del mismo color — se leen sin guía, y una guía habría cruzado
  otras curvas.
- **`set_opacity` enciende el relleno.** Un `Polygon` de contorno al que se
  le llama `set_opacity(0.8)` sale macizo: los diamantes de Mach parecían
  gemas. Es `set_stroke(opacity=…)`.
- **Un spline a través de una discontinuidad rebota.** La curva de presión
  con choque interno, dibujada con `set_points_smoothly`, dejaba un pico
  hacia abajo justo antes del escalón — se leía como si la presión bajara
  antes de subir. Con 91 muestras, una poligonal se ve igual de suave donde
  la función lo es y no inventa nada donde no.
- **Localizar un trozo de fórmula por índices de glifo es frágil.**
  `SurroundingRectangle(formula[0][8:15])` acabó encerrando «−1) dV/V». Se
  parte el `MathTex` en argumentos y se recuadra `formula[2]`.
- **Una `DashedLine` degenerada no se arregla con `put_start_and_end_on`**:
  no tiene guiones que recolocar. La asíntota hay que construirla ya con
  sus extremos, y eso lo hace la pieza, que es quien tiene la caja.
- **Los pies necesitan ≥ 5 s legibles.** Con el relevo secuencial de
  `Rotulos` (0.25 s de salida + 0.5 s de entrada), eso es `wait(4.6)` como
  mínimo. Recortar tiempo se hace **quitando beats**, no acortando los que
  quedan.
