# Ronda 2 — Visuales desde datos orbitales reales

Fecha: 2026-10-02. Autoría: ingeniería de astrodinámica y visualización. Solo lectura del repo; no se instaló nada.
Las afirmaciones sobre fuentes marcadas con (V) se leyeron en la página oficial el 2026-10-02; las marcadas con (M) vienen de memoria y hay que confirmarlas antes de apoyarse en ellas.

## 0. Resumen ejecutivo

- El repo NO tiene ningún dato orbital real ni propagador. Todo es geometría circular analítica o curvas didácticas. Ni `sgp4` ni `skyfield` están instalados (sí `numpy 2.5.3`, `scipy 1.18.1`, `requests 2.31`, `Pillow 12.3`, `pytz`, `zoneinfo`, `manim 0.21`; NO `astropy`, `matplotlib`, `pandas`, `cartopy`, `pyproj`).
- Hay una base excelente en la que enchufar datos reales: la vista polar, la curva S, la traza terrestre, las escenas de pases y el motor de carruseles ya existen y tienen el estilo de marca.
- Recomendación: un módulo `datos_orbitales` con dependencia mínima (`sgp4` de PyPI, licencia MIT/Apache-style; se instala con pip cuando el dueño lo apruebe; no se instaló en esta ronda) más `numpy`. Skyfield es opcional y pesado; no hace falta para los cinco productos propuestos.
- Dato nuevo e importante (V): CelesTrak informa que el espacio de 5 dígitos del catálogo NORAD se agotó el 2026-07-11 y el SATCAT ya pasa de 100 000. Los objetos nuevos no caben en TLE: hay que usar OMM/JSON como formato principal y TLE solo como compatibilidad.

## 1. Inventario del repo para órbitas

### 1.1 Qué hay y si es real o sintético

| Archivo | Qué contiene | Datos |
|---|---|---|
| `animaciones/seguidor_satelital.py` (1054 líneas) | `_beta(elmax, alt)`, `pase(elmax, az0, lado, alt, n, inv, ventana)` (pase de un LEO CIRCULAR sobre Tierra esférica, devuelve az, el, t, tca, dur), clase `Polar` (proyección acimutal equidistante: `pts(az, el)`, `fondo()`), `polilinea`, `tramo`, `punto_en`, `cifra_viva`, escenas `VistaPolarPase`, `CadenaTLEaAntena`, `AntenaSiguiendo`, `MontajeAzEl`, `LazoPID`, `Keyhole`, `DopplerEnS`, `GemeloDigitalATP`, `NochePases` | Sintéticos (parámetros elmax, az0, alt=550 km). `NochePases` dibuja seis pases inventados con máscara de 10° |
| `studio/content/manim_extensions/apuntado.py` (720) | `vista_polar`, `traza_pase(vista, el_max, az_culminacion)` (cuerda recta, "nada de propagar SGP4 en un clip", línea 261), `curva_s_doppler` (tanh invertida, forma didáctica), `tarjeta_tle` con `TLE_LINEA_1/2` de la ISS | TLE "didáctico" con época 26210 (julio 2026), declarado como valores didácticos: es un ejemplo de formato, no un dato vigente |
| `studio/content/manim_extensions/satelites.py` (1200) | Biblioteca de piezas de satélites y órbitas | Ilustrativo |
| `studio/content/manim_extensions/kepler.py` (73) | `OrbitaKepler`, `MoverKepler` | Kepler analítico |
| `studio/content/manim_extensions/sdr.py` (2122) | Cadena SDR completa. `ppm_a_hz`, `estimar_ppm`, `deriva_termica`; constantes `RTL`, `K_BOLTZMANN`. Emisoras "SINTÉTICAS" (línea 202) | Sintético y matemáticamente honesto |
| `studio/content/cursos/sdr-7-1-el-doppler-de-un-pase/` | Curso del Doppler. `style_block.py` calcula `DOP`, `DOP_MAX = 10.11 kHz` a 437 MHz, 550 km, 60° de elevación | Parámetros declarados, no efemérides |
| `studio/content/cursos/apuntar-a-un-satelite-el-arte-del-seguim/` (clips `02-dos-lineas-de-oro`, `03-del-tle-a-la-antena`) | Explica el TLE y su ruta a la antena | Didáctico |
| `studio/content/animations/experimentacion/03-orbita-kepler-real.py` | "Órbita kepleriana real" | Kepler analítico, no TLE |
| `studio/content/animations/dinamica-orbital/*` y `satelites/02-orbitas-y-tipos-de-satelite.py` | Kepler, elementos, perturbaciones | Analítico |
| `animaciones/espacio_orbitas.py` (`TrazaTerrestre`, `HuellaCobertura`), `animaciones/constelaciones.py` (WalkerDelta3D, PlanosOrbitales...) | Piezas publicables como stickers | Ilustrativos; el motor de carruseles ya avisa "cifras dentro de stickers: nunca las cites como dato" |
| `studio/tools/sonda_satelites.py` | Sonda de comprobaciones | Sin TLE |
| `redes/carruseles/motor_carrusel.py` + `ESQUEMA.md` | Motor 1080×1350. Lámina `dato`: `cifra*`, `titulo*`, `unidad`, `kicker`, `nota` (nota = de dónde sale la cifra). `sello`: ilustracion/simulacion/grabacion/beta/meta. Hay serie `divulgacion-orbital` con `doppler-curva-en-s`, `ventana-de-contacto`, `leo-meo-geo`... | Sin sello "dato real" ni "época" |
| Manim de marca: `marca_aerospace.py` (CIAN `#00D9FF`, AMBAR `#F59E0B`, FONDO `#080F15`, TENUE, Montserrat), `marca_vertical.py` (`marco(escena)`, `fondo_reel`, `bloque`, `tarjeta_vertical`, `cierre_vertical`, zona segura y ∈ [−7.4, +8.4]), `reels_promo.py` (`Reloj(escena, periodo)`, `ventana`, `ventana_texto`, `cabecera`, `chip`, `leyenda`, `linea_ciclica`, loop perfecto), `estelas.py` (`recorrer_con_estela`, `dibujar_con_cometa`) | Estilo | — |

Contexto de producto: Orbit Eye y SAT-DT (según `ESQUEMA.md`) ya usan TLE reales; SAT-DT con telemetría simulada. Su código no está en este repo, así que conviene reutilizar su criterio, no su código.

### 1.2 Librerías disponibles

- Sí: `numpy`, `scipy`, `requests`, `Pillow`, `pycairo`, `pytz`, `zoneinfo` (Python 3.12.3), `manim 0.21.0`.
- No: `sgp4`, `skyfield`, `astropy`, `matplotlib`, `pandas`, `cartopy`, `pyproj`.
- Consecuencia: la traza terrestre necesita un mapa; sin cartopy hay que usar un contorno de costas propio (Natural Earth, dominio público, simplificado a ~110 m de escala; pesa pocos KB como JSON) y dibujarlo con `VMobject` de Manim, que además queda en estilo de marca. No hace falta cartopy.

## 2. Fuentes de datos, licencias y la regla de la época visible

### 2.1 Comparativa

| Fuente | Qué da | Condiciones (resumen) | ¿Redistribuir en una pieza? |
|---|---|---|---|
| CelesTrak GP (`celestrak.org/NORAD/elements/gp.php?GROUP=...&FORMAT=json|csv|tle|xml`) | Datos GP del 18 SDS (EE. UU.) en OMM (JSON/CSV/XML/KVN) y TLE. Se actualiza cada 2 h (V). | (V) Sin licencia explícita; se piden: caché local con sello de tiempo, descargar solo cuando se necesita, detenerse ante 403/404. Desde 2026-03-26: UNA descarga por actualización para grupos grandes (Active, Starlink); la segunda en la misma ventana recibe 403. Bloqueo por IP con 50+ errores 301/403/404 en 2 h o 250+ MB/día. Piden donaciones. | Sí en la práctica: son datos de un gobierno de EE. UU. de acceso abierto. Buena práctica: citar "CelesTrak / 18th SDS" y la época. No publicar volcados masivos del catálogo, solo las derivadas (pases, cifras, gráficas). |
| Space-Track (`space-track.org`) | Fuente primaria (18 SDS), histórico (`gp_history`), SATCAT, decaimientos. | (V) Cuenta personal obligatoria, no compartir credenciales. 30 solicitudes/min y 300/h; límites por tipo (p. ej. TLE 1/hora, SATCAT 1/día). Cesión de datos a terceros requiere aprobación, con una aprobación general para datos SSA "básicos" con citación apropiada. No usar los TLE para evaluación de conjunciones operativa (hay que ir al 18 SDS). | Derivadas con cita sí; redistribuir el archivo crudo no. Ideal para históricos (reel "así cambió la órbita") guardando solo derivadas. |
| SatNOGS DB (`db.satnogs.org/api/`: satellites, transmitters, tle) | Frecuencias de transmisores verificadas por la comunidad, modos y estado (alive/dead) y también TLE. | (M) Los datos del DB se publican con licencia abierta tipo CC BY-SA 4.0; la página de API no lo dice, hay que confirmarlo en la documentación del proyecto antes de publicar. Atribución a SatNOGS. | Sí, con atribución y revisando compartir-igual. Las frecuencias de transmisor no se inventan: salen de aquí. |
| TinyGS | Red de estaciones LoRa; datos de recepción. | (M) Sin API abierta documentada con licencia clara; uso sujeto a los términos del proyecto. | No depender de ello para piezas; solo como mención. |
| N2YO API | Posiciones, pases, "visual passes" | (M) Clave gratuita, límites por hora (del orden de miles por hora según endpoint), uso de la clave personal. Dato derivado de los TLE públicos. | Evitar: duplica lo que ya calculamos y añade dependencia y términos propios. |
| Heavens-Above | Pases visibles (magnitudes, ISS, Iridium) | (M) Sin API pública; sus términos no permiten extraerlo automáticamente. | Solo como VERIFICACIÓN manual de nuestras horas de pase (ver piezas), nunca como fuente. |
| JPL Horizons / NASA | Efemérides de la ISS (OEM/Horizons) y de cuerpos del sistema solar | (M) Públicas, de uso libre con crédito a NASA/JPL. | Útil para verificar el Sol/Luna y como comparación independiente de SGP4. |

Decisión recomendada: fuente primaria CelesTrak (JSON/OMM por NORAD ID o por grupo) con respaldo en SatNOGS DB `tle`; Space-Track solo si se necesita historia. Frecuencias de transmisor desde SatNOGS DB.

### 2.2 Regla de «época visible» (no negociable)

1. Toda pieza derivada de elementos orbitales lleva, visible en pantalla, `Datos: CelesTrak/18 SDS · época AAAA-MM-DD HH:MM UTC` y la fecha de descarga si difiere.
2. Todo resultado de pase lleva además `Válido hasta ≈ época + N días` donde N depende de la órbita (ver §5.1): ISS y LEO bajos, 3 días para predecir minutos; 7 días como máximo para un reel "esta semana" con aviso.
3. Piezas que se publican con fecha: la hora del pase va en hora local con zona (`America/Mexico_City`) Y en UTC. México suspendió el horario de verano en 2022 (M: confirmar con `zoneinfo`; `ZoneInfo("America/Mexico_City")` lo resuelve con tzdata del sistema).
4. Sello de rigor propuesto, nuevo valor `"dato"` en el motor de carruseles (hoy hay ilustracion/simulacion/grabacion/beta/meta): `DATO REAL · época 2026-10-02`. Texto fijo de pie: `Predicción SGP4. Los elementos envejecen; verifica antes de salir.`
5. El sello cambia a `simulacion` automáticamente si la edad del TLE excede el límite de la pieza; el generador se niega a renderizar una pieza "en vivo" con TLE viejo (excepción `EpocaCaducada`).
6. Atribución fija en el cierre: `Datos orbitales: CelesTrak (18th Space Defense Squadron, US Space Force). Cálculo: SGP4. Co.De Aerospace`.

## 3. Diseño del módulo `datos_orbitales`

Ubicación propuesta: `studio/content/manim_extensions/datos_orbitales/` (en la ruta de `sys.path` que ya usan `marca_vertical` y `reels_promo`), con caché en `studio/content/datos_orbitales/cache/` (ignorada en git). Sin red durante el render: la escena solo lee de la caché o de un `.json` "congelado" que se guarda junto al clip (reproducibilidad).

### 3.1 Estructura

```
datos_orbitales/
  __init__.py
  fuentes.py      # descarga y caché con fecha (CelesTrak, SatNOGS)
  propagacion.py  # SGP4 -> TEME -> ECEF -> geodésicas
  observador.py   # topocéntrico, az/el/rango, pases
  doppler.py      # velocidad radial, curva Doppler
  traza.py        # traza terrestre y huella
  sello.py        # época, edad, sello de rigor, texto de atribución
  costas.json     # Natural Earth 110m simplificado
```

### 3.2 API propuesta (firmas)

```python
# fuentes.py
@dataclass(frozen=True)
class Elementos:
    norad: int; nombre: str; epoca: datetime      # tz UTC
    omm: dict                                      # registro OMM tal cual
    fuente: str                                    # "celestrak" | "satnogs" | "spacetrack"
    descargado: datetime
    @property
    def edad_dias(self) -> float: ...             # ahora UTC - epoca

def obtener(norad: int, *, fuente="celestrak", max_edad_h=6.0,
            cache_dir=CACHE, red=True) -> Elementos
    # 1) lee cache/<fuente>/<norad>.json; si la descarga tiene < max_edad_h, la usa
    # 2) si no, descarga UNA vez (cumple "una descarga por actualización", User-Agent
    #    "CoDeAerospace-contenido/1.0 (contacto)") y guarda con sello de tiempo
    # 3) ante 403/404 NO reintenta: usa cache aunque sea vieja y lo marca
def obtener_grupo(grupo: str, **kw) -> list[Elementos]   # "stations", "weather", "starlink"
def congelar(el: Elementos, ruta: Path) -> None          # para reproducir una pieza

# propagacion.py
def satrec(el: Elementos) -> "sgp4.api.Satrec"            # desde OMM (sgp4.omm) o TLE
def posicion_eci(el, t: datetime | np.ndarray) -> tuple[ndarray, ndarray]   # r, v (km, km/s) TEME
def posicion_geodetica(el, t) -> tuple[float, float, float]                  # lat°, lon°, h km (WGS84)
def error_estimado_km(el, t) -> float                     # heurística de §5.1

# observador.py
@dataclass(frozen=True)
class Observador:
    lat: float; lon: float; alt_m: float = 0.0
    nombre: str = "Observador"
    tz: str = "UTC"
    redondeo_deg: float | None = None     # privacidad, ver §5.3
def topocentrico(el, obs, t) -> tuple[float, float, float, float]   # az°, el°, rango km, rangedot km/s
@dataclass(frozen=True)
class Pase:
    aos: datetime; tca: datetime; los: datetime
    az_aos: float; az_tca: float; az_los: float
    el_max: float; rango_min_km: float
    visible: bool; magnitud: float | None   # visible = observador de noche, satélite al sol
def pases(el, obs, desde: datetime, dias: float = 7.0, *, el_min: float = 10.0,
          paso_s: float = 20.0, solo_visibles: bool = False) -> list[Pase]
    # barrido grueso a paso_s buscando cruces de el_min, refinado por bisección
    # (<0.5 s) para AOS/LOS y por sección áurea para TCA.
def trayectoria(el, obs, pase: Pase, n: int = 240) -> dict   # t, az, el, rango, rangedot (ndarray)

# doppler.py
C_KM_S = 299_792.458
def curva_doppler(el, obs, pase: Pase, f0_hz: float, n: int = 240) -> dict
    # f_rx(t) = f0 * (1 - rangedot/c) ;  df(t) = f_rx - f0   (rangedot>0 = se aleja)
    # devuelve t, f_rx, df, df_max, t_cruce (instante en que df = 0, ~TCA), pendiente_max_hz_s
def frecuencia_transmisor(norad: int) -> list[dict]          # SatNOGS DB: uplink/downlink/mode/status

# traza.py
def traza_terrestre(el, desde: datetime, minutos: float = 180, paso_s: float = 30
                    ) -> tuple[ndarray, ndarray, ndarray]    # t, lat, lon, con cortes en el antimeridiano
def huella_radio_km(h_km: float, el_min_deg: float = 0.0) -> float

# sello.py
def sello(el: Elementos, limite_dias: float = 3.0) -> dict
    # {"texto": "Datos: CelesTrak/18 SDS · época 2026-10-02 06:12 UTC",
    #  "edad_dias": 0.3, "caducado": False, "rigor": "dato"|"simulacion"}
def atribucion(fuentes: list[str]) -> str
```

Detalle de cálculo (para implementar con `sgp4` + `numpy`; ya vienen en `numpy` los rotaciones):
- TEME → ECEF: rotación por GMST (fórmula IAU-82, `sgp4.api.jday` y `gstime` de sgp4), sin movimiento polar (error < 10 m, irrelevante para divulgación).
- Geodética WGS-84 por iteración de Bowring (3 iteraciones bastan).
- Topocéntrico: `r_ecef - r_obs` rotado a ENU; `az = atan2(E, N)`, `el = asin(U/|ρ|)`, `rangedot = (ρ · v_rel)/|ρ|` con `v_rel = v_ecef_sat` (el observador está fijo en ECEF).
- Visibilidad óptica: Sol con la aproximación de Meeus (suficiente a 0.01°) y condición `sol_el_obs < −6°` (crepúsculo civil) y satélite iluminado (sombra cilíndrica de la Tierra).

### 3.3 Ejemplo de cálculo del Doppler (comprobado con lo que ya hay)

Con `f_rx = f0·(1 − ṙ/c)` y ṙ en el horizonte ≈ `v·RT/(RT+h)`:
- LEO a 550 km (v = 7.59 km/s) y f0 = 437 MHz: ṙ ≈ 6.99 km/s, Δf ≈ 437e6·6.99/299 792 ≈ 10.2 kHz en el horizonte. El curso del repo (`DOP_MAX = 10.11 kHz`, con máscara) coincide en orden de magnitud: el código real debe reproducirlo dentro del 2 % cuando se le da una órbita circular a 550 km. Esto es una prueba de regresión gratis.
- ISS (≈ 7.66 km/s, 145.825 MHz del APRS, M): Δf máx ≈ 3.5 kHz. Satélite meteorológico NOAA/METOP a 137 MHz (APT) a 850 km: Δf máx ≈ ±3 kHz (M: confirmar en la pieza, calcular, no citar de memoria).
- Un número que sí vale la pena mostrar: la pendiente máxima de la S en el TCA, `df/dt|máx ≈ f0·v²/(c·ρ_min)` (valor típico decenas de Hz/s a 437 MHz para un pase cenital). Es lo que el receptor de lazo cerrado debe seguir.

### 3.4 Conexión con Manim (reel vertical en loop)

Principio: la escena nunca llama a la red ni a SGP4 en el bucle de cuadros. En `construct`, o antes, calcula arreglos con `datos_orbitales` y los congela en un `.json` junto al clip (reproducibilidad y verificación). Los updaters leen esos arreglos con `np.interp`.

```python
# reels_promo-compatible: periodo del loop = duración del pase comprimida (p. ej. 20 s)
class ReelPasesISS(Scene):
    def construct(self):
        el  = obtener(25544)                                    # ISS
        obs = Observador(19.43, -99.13, 2240, "CDMX", "America/Mexico_City", redondeo_deg=0.1)
        lista = pases(el, obs, ahora_utc(), dias=7, el_min=10, solo_visibles=True)
        T = 18.0; reloj = Reloj(self, T)                         # de reels_promo
        vp = vista_polar_real(lista)                             # nueva en apuntado: reutiliza Polar.pts(az, el)
        sello_dato(self, sello(el))                              # nueva en marca_vertical: pie con época
```

Piezas nuevas mínimas a escribir (todas reutilizan lo existente):
- `apuntado.traza_pase_real(vista, tray)`: como `traza_pase` pero con az/el reales (usa `Polar.pts` de `seguidor_satelital.py`).
- `apuntado.curva_s_real(ancho, alto, df_hz, t)`: igual a `curva_s_doppler` pero con datos; el eje t en MM:SS, el eje f en kHz y la cifra viva con `cifra_viva`.
- `traza.mapa_mundi(vmob_costas, ancho)` + `recorrer_con_estela` (de `estelas.py`) para la traza terrestre con cometa.
- `marca_vertical.sello_dato(escena, sello)`: texto TENUE a y ≈ −7.0 (dentro de la zona segura inferior), con `bloque`.
- Loop perfecto: el reloj es módulo T; la marca del tiempo del pase da vueltas a `t % T`, y el texto de época es constante (no rota), así que el empalme es limpio.

### 3.5 Conexión con carruseles

Añadir al motor (cambios mínimos): (a) valor `sello: "dato"` con la etiqueta ámbar `DATO REAL`; (b) campo opcional `epoca` en la lámina `dato`, que se imprime junto a `nota`. Mientras eso no exista, se usa lo ya soportado:

```json
{"tipo": "dato", "cifra": "3.5", "unidad": "kHz", "kicker": "DOPPLER DE LA ISS",
 "titulo": "Eso se mueve la frecuencia en un solo pase",
 "nota": "Calculado con SGP4 · datos CelesTrak/18 SDS · época 2026-10-02 06:12 UTC · 145.825 MHz",
 "sello": "meta"}
```

Generador sugerido: `redes/carruseles/generar_desde_datos.py <plantilla> --norad 25544 --obs cdmx` que llena un spec desde `datos_orbitales` y escribe `fuentes` (con URL y fecha de consulta), `cuidado` (edad del TLE, zona horaria) y el `pie_texto` con la época. Respeta la regla 1 del ESQUEMA: «solo hechos con fuente»; aquí la fuente es la propia descarga, con fecha.

## 4. Cinco piezas de divulgación con datos reales

Todas: español latinoamericano, tuteo, sin superlativos. Todas con el sello `DATO REAL · época …` y verificación cruzada.

### 4.1 «Cuándo mirar la ISS esta semana en tu ciudad» (reel 9:16 loop, ~18 s)
- Guion: «La ISS pasa sobre CDMX [N] veces esta semana. Estas son las visibles. [Día/hora local] · sube por el SO, culmina a [el°], baja por el NE. Búscala 5 minutos antes.»
- Formato: reel vertical, vista polar con el cielo y los pases visibles apareciendo uno tras otro con `recorrer_con_estela`; barra de tiempo con hora local y UTC; loop cíclico.
- Datos: elementos de la ISS (CelesTrak, `CATNR=25544`); observador CDMX; `pases(..., solo_visibles=True)`.
- Verificación: contrastar a mano 3 pases con Heavens-Above (solo consulta manual) y con NASA Spot the Station (M: puede ser que ya no esté disponible; verificar). Tolerancia aceptable: AOS ±1 min con TLE de menos de 2 días. Prueba automática: la ISS culmina a una altitud entre 400 y 440 km y la inclinación 51.6° limita la latitud de la traza.
- Sello: `DATO REAL · época X · válido 3 días`.

### 4.2 «La S real del Doppler de un satélite meteorológico» (reel y lámina `dato`)
- Guion: «Un satélite meteo a 137 MHz no te habla en una frecuencia fija. Mira su curva real: empieza [+X kHz] arriba, cruza cero cuando está más cerca y termina [−X kHz] abajo.»
- Formato: reel 9:16; curva S dibujada con `curva_s_real` en CIAN, con la ISS/NOAA en AMBAR; cifra viva de Hz/s; cierre con `cierre_vertical`.
- Datos: NOAA 19 (NORAD 33591) o METEOR-M2 3/4 (sus números NORAD se confirman en CelesTrak grupo `weather`, M: algunos NOAA ya fueron retirados, verificar estado en SatNOGS `status`); frecuencia de SatNOGS DB `frecuencia_transmisor`.
- Verificación: (a) regresión contra la fórmula analítica con órbita circular; (b) comparar contra una grabación IQ real de SatNOGS si está disponible (se ve la misma S en el waterfall); (c) el cruce por cero debe caer dentro de ±2 s del TCA.
- Sello: `DATO REAL` para la forma de la curva; `SIMULACIÓN` si la frecuencia no viene de SatNOGS.

### 4.3 «Starlink en un globo, con la fecha de los datos» (carrusel 7 láminas + reel)
- Guion: «Cada punto es un satélite Starlink en este instante. Los datos son del [fecha]. En una semana ya no coincidirán.»
- Formato: globo 3D simple (esfera Manim con puntos), corte por planos, lámina `dato` con el recuento de objetos del grupo, la inclinación dominante y la altitud mediana (se calculan, no se citan).
- Datos: grupo `starlink` de CelesTrak (descarga ÚNICA por actualización, ver límites: es el grupo más vigilado); OMM/JSON porque hay objetos con ID de 6 dígitos.
- Verificación: el recuento coincide con el del propio archivo; las altitudes caen en los rangos conocidos; guardar el JSON congelado con su hash en `fuentes/`.
- Sello: `DATO REAL · época X`, con un `cuidado` claro: la constelación cambia a diario, pieza con caducidad.

### 4.4 «Dónde mirar al cielo esta noche: la ISS y el Sol» (lámina o reel de 12 s)
- Guion: «Hoy a las [hora], mira hacia el [az] a [el°]. Se verá como una estrella que no parpadea y cruza en [mm:ss].»
- Formato: reel con vista polar, brújula y una línea de tiempo del pase; versión carrusel con `dato` («[el°] máxima») y `pasos`.
- Datos: `pases` + posición del Sol (Meeus) para saber si el satélite está iluminado y el observador a oscuras.
- Verificación: la hora local debe cuadrar con `zoneinfo` (sin sumas a mano), y comparar con la fecha del equinoccio/crepúsculo con una tabla astronómica.
- Sello: `DATO REAL`; aviso «nubes y hora local»: la predicción da geometría, no nubosidad.

### 4.5 «La traza de la ISS en 3 órbitas» y «por qué no pasa siempre sobre el mismo lugar» (reel loop)
- Guion: «Una vuelta dura ~92 minutos. La Tierra gira debajo y la traza se corre ~23° de longitud en cada vuelta.»
- Formato: planisferio con costas (JSON), traza dibujada con cometa, cifra viva del corrimiento en longitud; loop de tres órbitas.
- Datos: `traza_terrestre(el, desde, minutos=280)`. El corrimiento (periodo nodal ≈ 92.9 min, M) se calcula de la propia traza, no se pone a mano: 360°·T/86164 s ≈ 23.3° en cada vuelta.
- Verificación: periodo medido entre dos cruces del ecuador ascendente; la latitud máxima ≈ inclinación (51.6°, ver `i` en el OMM); la traza cruza el antimeridiano sin saltos (cortes explícitos).
- Sello: `DATO REAL`. Es la más robusta para publicar con datos de unos días de antigüedad.

Orden recomendado por valor y riesgo: 4.5 (la más robusta) → 4.2 (la más identitaria para la marca, SDR + Doppler) → 4.1 → 4.4 → 4.3.

## 5. Riesgos

### 5.1 Precisión de SGP4 y TLE viejos
- Error típico (M, literatura estándar): del orden de 1 km en la época, que crece unos 1–3 km por día en LEO bajo; para la ISS, que maniobra y tiene arrastre fuerte, 1 a 3 días es el límite razonable para predecir un pase al minuto. A 7 días el error de posición puede ser de decenas de km y el instante de AOS/TCA se corre de minutos a decenas de minutos.
- Reglas del módulo: `error_estimado_km(el, t) = 1.0 + k_dia * |t − época|` con `k_dia = 3` para h < 600 km y 1 para h > 1200 km; `sello()` pone `caducado=True` cuando `|t − época| > limite_dias` (3 para ISS y LEO bajo; 14 para MEO/GEO).
- Las maniobras de la ISS (reboost) y las de Starlink invalidan elementos posteriores a la maniobra: tratar la edad como cota, no como garantía.
- Dos limitaciones de SGP4 que hay que advertir en la pieza: no modela maniobras, y el Doppler calculado supone el valor nominal (no incluye el error del oscilador local del receptor, que es el tema de `sdr.estimar_ppm`).
- No usar estos cálculos para evaluación de conjunciones (restricción de Space-Track, V).
- Catálogo: usar OMM/JSON. Los TLE no pueden representar objetos con ID > 99 999 (V).

### 5.2 Zonas horarias y tiempo
- Calcular todo en UTC, convertir solo al dibujar, con `zoneinfo.ZoneInfo`, nunca con offsets fijos. `datetime` siempre con tz.
- La fecha del pase puede cambiar de día al convertir (un pase a las 01:30 UTC del martes es el lunes por la noche en CDMX): el rótulo muestra la fecha local y la UTC.
- Las dos escalas: GMST usa UT1 ≈ UTC (error < 1 s, irrelevante); el campo de época del TLE es UTC y está en día fraccionario del año (2 dígitos de año; 2057 es el problema, no el actual).
- Reel "esta semana": la semana se fija al generar; el sello dice la fecha de generación.

### 5.3 Privacidad de la ubicación del observador
- Piezas públicas con ubicación de una persona o del equipo: nunca coordenadas exactas ni la dirección de una estación real. `Observador.redondeo_deg` redondea a 0.1° (≈ 11 km) y el rótulo dice solo la ciudad. El JSON congelado publicado (si se publica) lleva el valor redondeado, y el archivo con el valor exacto se queda fuera de git.
- Los pases se calculan con la ubicación redondeada para que el material que se publique sea reproducible con ella; la diferencia de ~10 km mueve el pase solo unos segundos.
- Cualquier pieza «para tu ciudad» usa un centro urbano público (CDMX, Bogotá...). Si alguna vez se pide ubicación al usuario en la app de escritorio, procesar localmente y no guardar.
- La estación de un cliente nunca se nombra (regla 3 del ESQUEMA).

### 5.4 Licencias y términos
- CelesTrak: abierta pero con política de descarga estricta (V): una descarga por ventana de actualización para grupos grandes; caché y sello de tiempo obligatorios en el módulo; respetar 403 deteniendo, no reintentando. Un render en lote con muchas escenas NO debe descargar: todas leen la misma caché.
- Space-Track: cuenta personal, límites 30/min y 300/h, TLE 1/hora (V); las credenciales fuera del repo (variables de entorno). No republicar el archivo.
- SatNOGS: comprobar la licencia exacta del DB y de las grabaciones (M: CC BY-SA); atribuir. Obras derivadas de Orbit Eye (GPL-3.0) ya están advertidas en el ESQUEMA.
- Costas de Natural Earth: dominio público, sin obligación; citarlo en créditos de todos modos.
- Fuentes tipográficas (Montserrat, OFL) ya resueltas en el repo.
- Piezas con cifras calculadas son obra propia de Co.De, pero la cifra no sustituye la cita de la fuente de datos.
- Pendiente de decisión del dueño: instalar `sgp4` (pip), y si se acepta una dependencia de red en el flujo de generación (hoy el estudio renderiza sin red).

## 6. Plan de implementación sugerido (orden)

1. `propagacion.py` + `observador.py` + `doppler.py` + pruebas (regresión: Doppler circular 550 km ≈ 10.1 kHz; ISS i = 51.6°; AOS/LOS por bisección). Con TLE congelado de ejemplo, sin red.
2. `fuentes.py` con caché y respeto a 403.
3. `sello.py` y valor `"dato"` en `motor_carrusel.py`.
4. `traza.py` + `costas.json`; piezas nuevas de Manim (`curva_s_real`, `traza_pase_real`, `sello_dato`).
5. Pieza piloto 4.5, luego 4.2 y 4.1. Revisión visual con la hoja de contacto, y el flujo habitual de la skill `animaciones-code`.

Archivos de referencia leídos: `animaciones/seguidor_satelital.py`, `studio/content/manim_extensions/{apuntado,sdr,satelites,kepler,marca_vertical,reels_promo,estelas,marca_aerospace}.py`, `studio/content/cursos/sdr-7-1-el-doppler-de-un-pase/`, `redes/carruseles/ESQUEMA.md`, `marca/paleta.json`. Fuentes web consultadas: celestrak.org/NORAD/documentation/gp-data-formats.php, space-track.org (acuerdo de usuario), db.satnogs.org/api (sin información de licencia en esa página).
