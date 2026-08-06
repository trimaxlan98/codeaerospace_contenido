# Curso 05 — Apuntar a un satelite: el arte del seguimiento

- **Proyecto**: name `Apuntar a un satélite: el arte del seguimiento`,
  quality `qh`.
- **Fuente**: Academy, curso Sistemas APT L1 (el problema del
  apuntamiento), L2 (TLE, SGP4, cadena de marcos, Az/El), L3 (geometria
  del pase, mascara de elevacion, keyhole), L4 (Doppler), L6 (PID
  aplicado — SOLO la intuicion: el detalle queda para el curso 07 de
  Control).
- **Slug**: `apuntar-a-un-satelite-el-arte-del-seguim`.
- **Publico**: divulgacion; conecta con los cursos publicados de
  Mecanica orbital y SDR.
- **Hilo narrativo**: el cielo se mueve → dos lineas que valen oro
  (TLE) → del TLE a la antena (cadena de marcos) → la vista polar del
  pase → el keyhole → la S del Doppler → el lazo que persigue →
  una noche de pases y cierre.

## Paleta del curso

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_SAT` | `#f59e0b` ambar | el satelite, su traza, su señal |
| `C_ANTENA` | `#22d3ee` cian | la antena/estacion y lo que la antena hace |
| `C_CIELO` | `#a78bfa` violeta | el cielo, la vista polar, el mapa, las referencias |
| `C_PELIGRO` | `#f43f5e` rojo | keyhole, error de apuntamiento, saturacion |
| `C_OK` | `#34d399` verde | enganche, ventana util, pase logrado |
| `C_EJE` | `#31414f` | mobiliario: anillos, ejes, mascara |

Regla de color: el SATELITE es ambar, la ANTENA cian, el CIELO violeta,
lo que FALLA rojo, lo LOGRADO verde. No mezclar roles.

## Contrato de la libreria `studio/content/manim_extensions/apuntado.py`

Determinista (numpy con semilla explicita cuando aplique), sin red, sin
archivos. Armoniza con code_brand/bloques. Se REUSA de `satelites.py`:
`imagen_mapa`, `puntos_en_mapa`, `traza_terrestre` (mapa raster: en los
clips SIEMPRE `Group`, no `VGroup`). Topes: `MUESTRAS_MAX = 400`.

```python
# --- la boveda del cielo ---------------------------------------------
vista_polar(radio=2.5, color="#31414f", font_size=15)
    # -> VistaPolar(VGroup): 3 anillos concentricos (el 0/30/60 grados;
    #    el horizonte es el anillo exterior, el cenit el centro) +
    #    cruces N/E/S/W (N arriba). Etiquetas HUD pequeñas "N","E","S",
    #    "W" y "30°","60°" sobre los anillos. Metodo
    #    .punto(az_deg, el_deg) -> np.array de escena (sigue al mobject
    #    si se mueve). Atributo .radio_u.
mascara_elevacion(vista, el_min=8.0, color="#31414f")
    # -> VMobject anillo sombreado entre el horizonte (el=0) y el_min:
    #    la zona donde la estacion NO declara visibilidad.
traza_pase(vista, el_max=45.0, az_culminacion=20.0, muestras=120,
           color="#f59e0b")
    # -> TrazaPase(VMobject): traza suave de un pase LEO sobre la vista
    #    polar (entra por el horizonte, culmina en el_max sobre el
    #    acimut az_culminacion, sale por el lado opuesto). Metodos
    #    .punto_en(t) con t en [0,1] (posicion sobre la traza) y
    #    .el_en(t) / .az_en(t) (grados). Geometria: pase de cuerda
    #    recta en proyeccion polar equidistante — suficiente y estable.
cono_keyhole(vista, radio_deg=8.0, color="#f43f5e")
    # -> VMobject circulo relleno translucido centrado en el cenit de
    #    la vista: la zona ciega de la montura Az/El.

# --- la montura -------------------------------------------------------
antena(escala=1.0, color="#22d3ee")
    # -> Antena(VGroup) icono 2D de montura Az/El: base + horquilla +
    #    plato (arco + alimentador). Metodo .orientar(deg) que rota el
    #    plato alrededor del pivote (0 = mirando al horizonte derecho,
    #    90 = cenit). Atributo .plato.
aguja_velocidad(maximo=10.0, valor=0.5, ancho=2.4, color="#22d3ee",
                color_peligro="#f43f5e")
    # -> AgujaVelocidad(VGroup) indicador semicircular "grados/s" con
    #    aguja; metodo .a_valor(v) -> np.array/angulo para animar con
    #    Rotate (devuelve el angulo objetivo de la aguja) y atributo
    #    .aguja. La zona sobre el 75% del maximo va sombreada en rojo.

# --- el TLE -----------------------------------------------------------
tarjeta_tle(font_size=15)
    # -> VGroup caja oscura con las 2 lineas TLE de la ISS (las de la
    #    leccion, valores didacticos) en FUENTE_HUD, mas la linea de
    #    nombre "ISS (ZARYA)". Atributo .campos: dict con VGroups de
    #    caracteres resaltables: "inclinacion", "raan", "excentricidad",
    #    "movimiento_medio", "epoca" (cada uno agrupa los glifos de ese
    #    campo para poder Indicate/colorear).

# --- el Doppler -------------------------------------------------------
curva_s_doppler(ancho=5.4, alto=2.6, color="#f59e0b",
                color_ejes="#31414f", font_size=15)
    # -> CurvaS(VGroup): ejes minimos (t ->, f ^) con linea punteada
    #    horizontal al centro etiquetada "f0" (HUD) y la curva S del
    #    Doppler (alta en AOS, cruza f0 en TCA, baja en LOS; tanh
    #    invertida). Metodo .punto_en(t_rel) -> np.array SOBRE la curva
    #    (t_rel en [0,1]) y atributos .ejes, .curva, .linea_f0.

# --- el lazo de seguimiento ------------------------------------------
curvas_seguimiento(ancho=5.6, alto=2.4, retraso=0.16, muestras=140,
                   color_ref="#f59e0b", color_ant="#22d3ee")
    # -> Seguimiento(VGroup): ejes minimos (t ->, angulo ^) con dos
    #    curvas: la referencia (rampa suave que acelera al centro, como
    #    el acimut de un pase) y la antena, identica pero desplazada
    #    `retraso` en t (rezago constante). Con retraso=0.0 ambas
    #    coinciden. Metodo .brecha_en(t_rel) -> (punto_ref, punto_ant)
    #    para dibujar la flecha del error. Atributos .ejes, .ref, .ant.
```

Demo obligatoria:
`studio/content/animations/experimentacion/17-apuntado.py` con
`DemoApuntado(Scene)` (~15 s): vista_polar + mascara + traza_pase con un
punto recorriendola y la antena orientandose, cono_keyhole, tarjeta_tle
con un campo resaltado, curva_s_doppler con punto, curvas_seguimiento
con y sin retraso, aguja_velocidad entrando en zona roja.

## Reglas duras para los clips

Identicas a los cursos 01-04: solo `class ClipN(Scene)`; Rotulos para
todo texto narrativo; un fenomeno por clip; 28-45 s; determinismo;
MathTex raw corto; solo paleta; `# --- momento ---` por beat; cada pie
visible >= 5 s. El mapa de satelites.py es raster: `Group`, no
`VGroup`.

## Storyboard clip a clip

### Clip 1 — `1 · El cielo que no se queda quieto` (escena `Clip1`, ~36 s)
Portada: `titulo_marca("Apuntar a un satélite", 42)` + subtitulo ambar
«el arte del seguimiento». HUD `Modulo 01`. Titulo «El cielo que no se
queda quieto». `imagen_mapa(alto_escena=4.6)` centrado (y≈-0.15, en
Group); sobre el, `traza_terrestre` de una orbita LEO inclinada
(sinusoide de ±51° generada en el clip con numpy, 2 periodos) ambar, y
un punto estacion cian fijo (usar `puntos_en_mapa`). Pie: «Una estación
fija. Un satélite a 27 000 km/h.» Un punto ambar recorre la traza
(MoveAlongPath). Pie: «Cruza tu cielo en diez minutos... si sabes hacia
dónde mirar.» Sobre la estacion crece un circulo verde translucido (su
huella de visibilidad) y el punto lo atraviesa: el tramo dentro pulsa
verde. Pie: «Todo el juego ocurre en esa pequeña ventana.» Pie gancho:
«Apuntar es resolver dónde, cuándo y a qué velocidad.»
**final_state**: mapa con traza ambar, estacion cian con su circulo
verde, punto satelite al final de la traza.

### Clip 2 — `2 · Dos líneas que valen oro` (escena `Clip2`, ~36 s)
Titulo «Dos líneas que valen oro». `tarjeta_tle()` centrada (y≈+0.6).
Pie: «Todo lo que hace falta para encontrar un satélite cabe en dos
líneas de texto: el TLE.» Campos resaltados en relevo (Indicate +
color): `inclinacion` → pie «Cuánto se inclina su órbita...»;
`movimiento_medio` → pie «...y cuántas vueltas da al día: 15.5.» Acto
2: bajo la tarjeta (y≈-1.5) aparece la cuenta en relevo de formulas:
`formula_pie("T = 86400 / 15.5 = 92.9\\ \\text{min}")` → pie «Del
movimiento medio sale el periodo...» →
`formula_pie("h \\approx 424\\ \\text{km}")` con pie «...y con Kepler,
la altitud: 424 km. La ISS.» Acto 3: la `epoca` se resalta en rojo
suave; pie: «Pero caduca: cada día de propagación suma kilómetros de
error.» Pie cierre: «Refresca el TLE antes de cada pase.»
**final_state**: tarjeta TLE centrada con el campo de la epoca
resaltado.

### Clip 3 — `3 · Del TLE a la antena` (escena `Clip3`, ~36 s)
Titulo «Del TLE a la antena». Cadena de `bloque` en dos filas
(bloques.py): fila superior (y≈+1.1) «TLE» → «SGP4» → «ECI»; fila
inferior (y≈-0.5) «ECEF» → «ENU» → «AZ/EL» (conectar ECI→ECEF con un
codo o flecha diagonal). Colores: TLE/SGP4 violeta (mundo de los
datos), AZ/EL cian (lo que la antena entiende). `flujo` recorre la
cadena completa. Pie: «Del texto a los dos números que el rotor
entiende: seis marcos de referencia.» Acto 2: bloque ECI→ECEF pulsa;
pie: «El paso clave: la Tierra rota bajo la órbita.» Acto 3: junto a la
cadena (y≈-1.7) `etiqueta_hud("RELOJ +1 s → 0.8° DE ERROR")` aparece
con `destello` rojo sobre la cadena. Pie: «Un segundo de reloj
desincronizado: ocho veces el presupuesto de error. Sincroniza por
GPS.» Cierre: `formula_pie("Az = \\operatorname{atan2}(e, n)")` con pie
implicito... NO: pie cierre «Al final, pura trigonometría: acimut y
elevación.»
**final_state**: cadena completa de 6 bloques con la etiqueta HUD del
reloj abajo.

### Clip 4 — `4 · La vista polar del pase` (escena `Clip4`, ~37 s)
Titulo «No todos los pases valen lo mismo». `vista_polar(radio=2.35)`
centrada (x≈0, y≈-0.15). Pie: «El cielo de tu estación, visto desde
arriba: el borde es el horizonte, el centro el cénit.» Acto 2:
`mascara_elevacion(vista, el_min=8)` aparece; pie: «Bajo ocho grados no
hay pase: árboles, edificios y demasiada atmósfera.» Acto 3:
`traza_pase(el_max=12, az_culminacion=-60)` violeta tenue se dibuja;
tag_junto «rasante» cerca de su culminacion. Pie: «Un pase rasante:
lejos, corto y débil.» Acto 4: `traza_pase(el_max=80, az_culminacion=25)`
ambar se dibuja (la rasante baja opacidad); tag «casi cenital» (relevo
del tag anterior). Pie: «Uno alto: cuatro veces más cerca — doce
decibelios más de señal.» Un punto ambar recorre la traza alta. Pie
cierre: «La elevación máxima lo dice todo: caza los pases altos.»
**final_state**: vista polar con mascara, traza rasante tenue y traza
alta ambar con su tag.

### Clip 5 — `5 · Keyhole: el agujero del cénit` (escena `Clip5`, ~38 s)
Titulo «Keyhole: el agujero del cénit». `vista_polar(radio=2.2)` a la
izquierda (x≈-3.0, y≈-0.15) con `traza_pase(el_max=87, az_culminacion=5)`
ambar. A la derecha (x≈+3.2, y≈+0.6) `aguja_velocidad(maximo=10)`. Pie:
«El mejor pase para la señal es el peor para la mecánica.»
`formula_pie("\\dot{Az} = \\omega_t / \\cos(el)")`. Un punto recorre la
traza; la aguja sube con la elevacion (updater: valor segun .el_en(t)),
y al acercarse al cenit se dispara a la zona roja (9°/s). Pie: «Cerca
del cénit el acimut pide un giro imposible: la demanda se dispara.»
`cono_keyhole(radio_deg=8)` aparece pulsando en rojo sobre el centro.
Pie: «Ese cono ciego es el keyhole: ahí la montura no puede seguir.»
Acto final: la traza se re-dibuja esquivando... no — la aguja vuelve a
zona segura y el pie cierra: «Las salidas: aceptar el hueco, girar
antes, o cambiar de montura.»
**final_state**: vista polar con traza casi cenital, cono keyhole rojo
en el centro, aguja de velocidad en zona roja a la derecha.

### Clip 6 — `6 · Doppler: la S del pase` (escena `Clip6`, ~36 s)
Titulo «La frecuencia que se mueve». `curva_s_doppler` centrada
(y≈-0.1) se dibuja: primero ejes y linea f0 punteada, luego la S. Pie:
«Apuntas perfecto... y no oyes nada: el satélite no transmite donde
crees.» `formula_pie("f_d = -\\,\\frac{v_r}{c}\\, f_0")`. Un punto
brillante recorre la S con pies en relevo: al inicio (arriba) «Se
acerca: la frecuencia llega comprimida, más alta.» → cruzando f0
(Flash en el cruce) «En la máxima aproximación, la nominal exacta...» →
al final (abajo) «...y al alejarse, cae. Una S perfecta.» Acto final:
`etiqueta_hud("VHF ±3.4 kHz · UHF ±10 kHz")` bajo la curva (sin tocar
pie). Pie cierre: «Cuanto más alta la banda, más grande la S: corrige
en vivo.»
**final_state**: curva S completa con linea f0, punto al final y
etiqueta HUD de bandas.

### Clip 7 — `7 · El lazo que persigue` (escena `Clip7`, ~36 s)
Titulo «El lazo que persigue». `curvas_seguimiento(retraso=0.16)`
centrada (y≈-0.1): primero se dibuja solo la referencia ambar. Pie: «El
propagador dicta dónde debería estar la antena en cada instante.»
Luego la curva cian de la antena. Pie: «La antena real siempre llega un
poco tarde.» Flecha roja vertical corta entre `.brecha_en(0.62)` con
tag rojo «error». Pie: «Esa brecha es el error de seguimiento: el
número que el lazo quiere matar.» Acto 2: ReplacementTransform a
`curvas_seguimiento(retraso=0.05)` (la flecha del error se encoge con
las curvas — recrearla); pie: «Un resorte proporcional acerca...»
Transform a `retraso=0.0` y la curva antena pasa a verde; pie: «...y la
memoria integral borra el rezago. Enganchado.» Cierre: pie «Domar ese
lazo a fondo es otro curso: aquí basta ver que persigue.»
**final_state**: dos curvas superpuestas (referencia ambar, antena
verde encima) sin flecha de error.

### Clip 8 — `8 · Una noche de pases` (escena `Clip8`, ~40 s)
Titulo «Una noche de pases». `vista_polar(radio=2.0)` a la izquierda
(x≈-3.1, y≈-0.2) con `traza_pase(el_max=55, az_culminacion=30)`;
`antena(escala=0.9)` a la derecha (x≈+3.0, y≈-0.6) mirando al
horizonte. Secuencia AOS→LOS: punto ambar entra por el horizonte, el
plato de la antena `.orientar` lo sigue (updater con el_en); al AOS
`etiqueta_hud("AOS 14:32")` junto a la vista (relevo con la de LOS
despues). Pies en relevo: «AOS: el satélite asoma; la antena ya está
esperando.» → «Cuatro minutos de persecución silenciosa...» → al
salir «LOS: se fue. La montura vuelve a su reposo.» (etiqueta
«LOS 14:41»). Acto final: todo se desvanece → tarjeta de cierre:
`titulo_marca("Apuntar a un satélite", 42)` + subtitulo ambar «el arte
del seguimiento» + subrayado `con_brillo`. `self.wait(2)`.
**final_state**: tarjeta de cierre del curso centrada, pantalla limpia
salvo esquinas HUD y marca de agua.

## Descripcion del proyecto (campo description)

Curso de divulgación en 8 clips sobre el apuntamiento y seguimiento de
satélites LEO: del cielo que se mueve al TLE y su caducidad, la cadena
de marcos de referencia hasta acimut y elevación, la vista polar del
pase y la máscara de elevación, el keyhole de las monturas Az/El, la
curva S del Doppler, el lazo de control que persigue la referencia y la
coreografía completa de un pase AOS→LOS. Estilo 3Blue1Brown en español.
