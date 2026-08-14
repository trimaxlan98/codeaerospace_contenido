"""Electromagnetismo: de la carga de Coulomb al bit que baja del satelite.

Pensado para la familia de cursos "Electromagnetismo" (leccion 1.1 en
adelante). Todo el calculo es numpy puro y determinista — sin red, sin disco,
sin azar — condicion necesaria para trabajar con `--disable_caching`: mismo
script, mismo render.

La regla de color del curso, que es tambien la de esta libreria: **el color
dice quien actua**.

    fuente    rojo     cargas, corrientes, el emisor
    campo E   ambar    el campo electrico
    campo B   verde    el campo magnetico
    onda      violeta  E y B casados y viajando; la señal radiada
    calculo   cian     umbrales, cifras, resultados de la cuenta

Ademas el gris azulado `COLOR_EJE` para el mobiliario (ejes, guias,
muescas). No mezclar roles: un mapa de campos debe poder leerse sin
narracion.

Funciones (los numeros que el clip rotula salen de aqui, nunca a mano):
    coulomb                 F = k q1 q2 / r^2
    campo_puntual           E = k q / r^2
    campo_dipolo_eje        E ~ 2 k p / r^3: cae con el CUBO
    b_hilo                  B = mu0 I / (2 pi r)
    b_solenoide             B = mu0 n I
    b_tierra                dipolo terrestre: 31.2 uT por (R_E/r)^3
    radio_larmor            r = m v / (q B)
    frecuencia_giro         f = q B / (2 pi m)
    par_torquer             tau = m_dip B
    tiempo_giro_torquer     barrer un angulo a par constante
    fem_espira              pico N B A omega del alternador
    c_de_constantes         1 / sqrt(mu0 eps0) — la sorpresa de Maxwell
    impedancia_vacio        eta0 = sqrt(mu0/eps0) = 376.73 ohm
    lambda_de / f_de        c = lambda f
    campo_de_flujo          E_pico = sqrt(2 eta0 S)
    z0_coaxial              (eta0 / 2 pi sqrt(er)) ln(D/d)
    gamma_de / swr_de       reflexion en una frontera de impedancias
    z_cuarto                el transformador de lambda/4
    fc_te10                 corte del modo TE10: c / (2 a)
    patron_dipolo_corto     sen(theta)
    patron_dipolo_medio     cos(pi/2 cos theta) / sen theta
    directividad            D de un patron con simetria acimutal (integrada)
    ganancia_apertura       ef (pi D / lambda)^2
    factor_array            |sin(N psi/2) / (N sin(psi/2))|
    angulo_apuntado         a donde mira el array con esa rampa de fase
    frecuencia_plasma       8.98 sqrt(Ne)
    retardo_iono            40.3 TEC / f^2, en metros de camino
    radio_geo               la orbita de Clarke, desde T sideral
    v_orbital / t_orbital   orbita circular a esa altitud
    fspl_db                 20 log10(4 pi d / lambda)
    flujo_isotropo          P / (4 pi d^2)
    pase_leo_geometria      elevacion, distancia y Doppler de un pase real
    atenuacion_lluvia       ITU-R P.838-3, k R^alpha con la tabla embebida
    ruido_dbw               10 log10(k T B)

Las piezas (una seccion por modulo, ver el indice al final del docstring)
exponen localizadores (`.punto_de`, `.foco`, `.a_tiempo`) que se recalculan
sobre la posicion ACTUAL del mobject: siguen siendo validos tras un `move_to`
o un `shift`. Lo que NO siguen es un `scale` — la escala se elige al
construir (`ancho`, `alto`) y no se toca despues; es la misma regla que en
`aerodinamica.py`, `enlace.py` y `espectro.py`. Y exponen los NUMEROS que
dibujan: el rotulo del clip debe salir de la misma fuente que el trazo.

Topes duros para no castigar el VPS (2 vCPU / 2 GB por render):
`MUESTRAS_MAX`, `LINEAS_MAX` y `CURVAS_MAX` levantan ValueError; pasarse
cambia lo que se ve y es mejor enterarse.

Piezas (modulo 1, campos quietos):
    carga                   punto con halo y signo
    lineas_campo            lineas de E integradas de verdad (RK4)
    equipotenciales         las curvas de nivel del potencial, integradas
    haz_curvas              n curvas en una caja de ejes, con etiquetas fuera
    hilo_corriente          hilo, circulos de B y brujulas tangentes
    solenoide_corte         corte con puntos/cruces y campo uniforme dentro
    tierra_iman             la Tierra y sus lineas de dipolo r = L sen^2
    cubesat_torquer         cubesat + bobina + B + el par
    giro_larmor             el circulo de la fuerza que no trabaja
    espejo_magnetico        la botella: espiral que rebota entre espejos
    mapa_orbitas            Tierra a escala, cinturones y orbitas LEO/MEO/GEO
    tubo_ondas              TWT: helice, haz y la onda que crece

Piezas (modulo 2, Maxwell y la onda):
    espira_iman             iman, bobina y galvanometro
    curvas_flujo_fem        Phi(t) arriba y -dPhi/dt abajo, alineadas
    alternador              la espira que gira y escribe la senoide
    transformador           dos devanados sobre un nucleo
    caja_gauss              flujo por una superficie cerrada (E o B)
    condensador_ampere      las placas, el lazo y el termino que faltaba
    onda_em                 E (ambar) y B (verde) perpendiculares viajando
    esfera_reparto          el frente esferico y el parche que recoge
    traza_polarizacion      lineal V/H o circular
    banda_espectro_em       el eje logaritmico de bandas HF..Ka

Piezas (modulo 3, guiar y soltar):
    cable_onda              un cable con la onda encima, a la lambda que sea
    linea_lc                la escalera LC del telegrafista
    corte_coaxial           seccion del coaxial con E radial y B circular
    corte_microstrip        seccion de microstrip con su campo
    onda_estacionaria       incidente + reflejada, envolvente y SWR
    frontera_z              dos medios y las flechas incidente/reflejada/transmitida
    linea_cuartos           tramos de linea con su Z0 rotulada
    guia_te10               la guia rectangular y su zigzag segun f/fc
    dipolo_radiante         el dipolo que suelta frentes
    patron_polar            el patron en polares de CUALQUIER funcion
    parabola_foco           rayos paralelos al foco
    array_fases             elementos + rampa de fase + frente inclinado

Piezas (modulo 4, el enlace por el espacio):
    capas_ionosfera         perfil Ne(h) dia/noche con D/E/F
    rebote_hf               la Tierra curva y los saltos ionosfericos
    ventana_iono            rayos que rebotan o cruzan segun la frecuencia
    barras_retardo          el peaje del GPS en L1/L2
    pase_leo                el pase: cupula del cielo, arco y elevacion
    margen_enlace           SNR contra umbral con la tormenta pasando
    cielo_ruido             la antena que mira al frio o al suelo
    arco_familia            el recap: carga -> campo -> onda -> ... -> bit

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from electromagnetismo import lineas_campo, carga

    mapa = lineas_campo([(1.0, -1.2, 0.0), (-1.0, 1.2, 0.0)])
    self.add(mapa)                       # y mapa.linea(3), mapa.cargas
"""

import numpy as np

from manim import (AnimationGroup, Annulus, Arc, Arrow, Circle, DashedLine,
                   DashedVMobject, Dot, Line, Polygon, Rectangle, Text,
                   Transform, VGroup, VMobject, DL, DOWN, DR, LEFT, ORIGIN,
                   RIGHT, UL, UP, UR)

from code_brand import (CODE_BG, CODE_MUTED, FUENTE_DISPLAY, FUENTE_HUD,
                        registrar_fuentes)

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
MUESTRAS_MAX = 400      # muestras de una curva parametrica
LINEAS_MAX = 24         # lineas de campo / equipotenciales de un mapa
CURVAS_MAX = 6          # curvas de un haz_curvas

# Paleta propia de la libreria (coincide con la del curso): el color dice
# QUIEN ACTUA. Ver la nota del docstring.
COLOR_CARGA = "#f43f5e"      # rojo: las fuentes (cargas, corrientes, emisor)
COLOR_E = "#f59e0b"          # ambar: campo electrico
COLOR_B = "#34d399"          # verde: campo magnetico
COLOR_ONDA = "#a78bfa"       # violeta: E y B viajando juntos; la señal
COLOR_CALCULO = "#22d3ee"    # cian: umbrales, cifras, resultados
COLOR_EJE = "#31414f"        # mobiliario: ejes, guias, muescas

# Alias cortos, para que el style_block de los clips escriba `color=C_ONDA`.
C_CARGA, C_E, C_B = COLOR_CARGA, COLOR_E, COLOR_B
C_ONDA, C_CALCULO, C_EJE = COLOR_ONDA, COLOR_CALCULO, COLOR_EJE

# Constantes fisicas (CODATA 2018; e, c y k son exactas desde el SI 2019).
Q_E = 1.602176634e-19        # carga elemental, C
M_ELECTRON = 9.1093837015e-31  # kg
EPS0 = 8.8541878128e-12      # permitividad del vacio, F/m
MU0 = 1.25663706212e-6       # permeabilidad del vacio, H/m
C_LUZ = 299792458.0          # m/s, exacta por definicion
K_COULOMB = 1.0 / (4.0 * np.pi * EPS0)   # 8.9875e9 N m^2 / C^2
K_BOLTZMANN = 1.380649e-23   # J/K, exacta
MU_TIERRA = 3.986004418e14   # GM de la Tierra, m^3/s^2
R_TIERRA = 6371.0e3          # radio medio, m (geometria de pases)
R_TIERRA_EQ = 6378.137e3     # radio ecuatorial, m (altitud de GEO)
T_SIDERAL = 86164.0905       # dia sideral, s (el periodo de GEO)
B_TIERRA_EC = 3.12e-5        # campo en el ecuador, T (dipolo centrado)

# Las bandas que usa la familia: (nombre, f_min Hz, f_max Hz, uso satelital).
# Fronteras IEEE para las de microondas; las tres primeras son las clasicas
# de radio. El "uso" es el ejemplo canonico que rotulan los clips.
BANDAS = (("HF", 3e6, 30e6, "onda corta: rebota en la ionosfera"),
          ("VHF", 30e6, 300e6, "FM, aviacion; ya cruza al espacio"),
          ("UHF", 300e6, 1e9, "TV, cubesats, IoT satelital"),
          ("L", 1e9, 2e9, "GPS, Iridium, Inmarsat"),
          ("S", 2e9, 4e9, "telemetria, radar meteo"),
          ("C", 4e9, 8e9, "satcom veterana: aguanta la lluvia"),
          ("X", 8e9, 12e9, "radar y satcom militar"),
          ("Ku", 12e9, 18e9, "TV directa al plato de balcon"),
          ("K", 18e9, 26.5e9, "la franja del vapor de agua"),
          ("Ka", 26.5e9, 40e9, "banda ancha: Starlink, Viasat"))

# ITU-R P.838-3, polarizacion horizontal: f GHz -> (kH, alphaH). La
# atenuacion especifica es gamma = k R^alpha en dB/km con R en mm/h. Entre
# puntos de la tabla se interpola en log-log (como recomienda el informe).
_P838 = ((10.0, 0.01217, 1.2571),
         (12.0, 0.02386, 1.1825),
         (15.0, 0.04481, 1.1233),
         (20.0, 0.09164, 1.0568),
         (25.0, 0.1571, 0.9991),
         (30.0, 0.2403, 0.9485),
         (35.0, 0.3374, 0.9047),
         (40.0, 0.4431, 0.8673))

_EPS = 1e-9


# --- utilidades internas ----------------------------------------------
def _texto_hud(texto, font_size=15, color=COLOR_EJE):
    """Etiqueta tecnica en la tipografia de telemetria de la marca.

    SOLO ASCII: Space Mono no trae superindices ni acentos fiables (un
    "10⁶" sale renderizado como "10'"). Lo que lleve acento o exponente va
    en `_texto_display` o en un MathTex del clip.
    """
    registrar_fuentes()
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=color)


def _texto_display(texto, font_size=18, color=COLOR_EJE):
    """Etiqueta con palabras de verdad (acentos incluidos), en Rajdhani."""
    registrar_fuentes()
    return Text(str(texto), font=FUENTE_DISPLAY, font_size=font_size,
                color=color)


def _curva(puntos, color, grosor=2.8, suave=True):
    """VMobject a partir de un array (n, 2) o (n, 3) de escena.

    `suave=False` traza la poligonal: es lo correcto a traves de una
    discontinuidad o un pico (un spline rebota e inventa).
    """
    pts = np.asarray(puntos, dtype=np.float64)
    if pts.shape[1] == 2:
        pts = np.column_stack([pts, np.zeros(len(pts))])
    curva = VMobject(color=color, stroke_width=grosor)
    if suave:
        curva.set_points_smoothly(pts)
    else:
        curva.set_points_as_corners(pts)
    return curva


def _validar_muestras(nombre, muestras):
    """Tope duro comun a todas las curvas parametricas de la libreria."""
    n = int(muestras)
    if n > MUESTRAS_MAX:
        raise ValueError(
            f"{nombre}: muestras={n} supera MUESTRAS_MAX={MUESTRAS_MAX}")
    return max(8, n)


class _Cartesiano(VGroup):
    """Base de las piezas con ejes: recuerda la caja de datos y traduce.

    Las subclases llaman a `_calibrar` DESPUES de haber añadido todos sus
    submobjects — ahi se congela el centro, y de la diferencia con el centro
    actual salen los localizadores validos tras un `move_to`.
    """

    def _calibrar(self, rango_x, rango_y, ancho, alto, origen):
        self._rx = (float(rango_x[0]), float(rango_x[1]))
        self._ry = (float(rango_y[0]), float(rango_y[1]))
        self._ancho = float(ancho)
        self._alto = float(alto)
        self._origen = np.asarray(origen, dtype=np.float64)
        self._centro_original = self.get_center()

    def _en(self, x, y):
        """Punto de escena del dato (x, y), recortado a la caja."""
        fx = float(np.clip((float(x) - self._rx[0])
                           / max(self._rx[1] - self._rx[0], _EPS), 0.0, 1.0))
        fy = float(np.clip((float(y) - self._ry[0])
                           / max(self._ry[1] - self._ry[0], _EPS), 0.0, 1.0))
        return (self._origen
                + np.array([fx * self._ancho, fy * self._alto, 0.0])
                + (self.get_center() - self._centro_original))


class _Anclada(VGroup):
    """Base de las piezas sin ejes: localizadores relativos a un ancla.

    El ancla es el centro congelado al construir; `_desde(dx, dy)` devuelve
    ese punto mas el desplazamiento acumulado del grupo. Vale tras un
    `move_to`/`shift`, no tras un `scale` (regla de la libreria).
    """

    def _anclar(self):
        self._centro_original = self.get_center()

    def _desde(self, dx, dy):
        return (self._centro_original + np.array([dx, dy, 0.0])
                + (self.get_center() - self._centro_original))


def _ejes_xy(ancho, alto, color=COLOR_EJE):
    """Par de ejes en L con origen en la esquina inferior izquierda,
    centrados en ORIGIN. Devuelve (VGroup, origen) con el origen ya en
    coordenadas de escena para que quien llama situe sus curvas."""
    x0, y0 = -ancho / 2, -alto / 2
    eje_x = Line((x0, y0, 0), (x0 + ancho, y0, 0), stroke_width=2.0,
                 color=color)
    eje_y = Line((x0, y0, 0), (x0, y0 + alto, 0), stroke_width=2.0,
                 color=color)
    return VGroup(eje_x, eje_y), np.array([x0, y0, 0.0])


# =====================================================================
# Los numeros — modulo 1: campos quietos
# =====================================================================
def coulomb(q1, q2, r):
    """|F| = k |q1 q2| / r^2 en N. La ley con la que empieza todo.

    Devuelve el MODULO; el signo (atrae o repele) lo decide el clip mirando
    los signos de las cargas, que es como se cuenta en pantalla.
    """
    d = float(r)
    if d <= 0:
        raise ValueError("coulomb: r debe ser positivo")
    return float(K_COULOMB * abs(float(q1) * float(q2)) / d ** 2)


def campo_puntual(q, r):
    """|E| = k |q| / r^2 en V/m."""
    d = float(r)
    if d <= 0:
        raise ValueError("campo_puntual: r debe ser positivo")
    return float(K_COULOMB * abs(float(q)) / d ** 2)


def campo_dipolo_eje(p, r):
    """Campo del dipolo sobre su eje, lejos: E = 2 k p / r^3, en V/m.

    La cuenta que separa al dipolo de la carga: cae con el CUBO. Es el
    motivo de que una antena no sea "una carga grande": el dipolo estatico
    casi no llega lejos, y para llegar hay que OSCILARLO (la radiacion cae
    con 1/r, pero esa es la historia del modulo 3).
    """
    d = float(r)
    if d <= 0:
        raise ValueError("campo_dipolo_eje: r debe ser positivo")
    return float(2.0 * K_COULOMB * abs(float(p)) / d ** 3)


def b_hilo(corriente, r):
    """B = mu0 I / (2 pi r) en T. Un amperio a un metro: 2e-7 T."""
    d = float(r)
    if d <= 0:
        raise ValueError("b_hilo: r debe ser positivo")
    return float(MU0 * float(corriente) / (2.0 * np.pi * d))


def b_solenoide(n_por_metro, corriente):
    """B = mu0 n I dentro de un solenoide largo, en T."""
    n = float(n_por_metro)
    if n <= 0:
        raise ValueError("b_solenoide: n_por_metro debe ser positivo")
    return float(MU0 * n * float(corriente))


def b_tierra(r_re):
    """Campo del dipolo terrestre en el plano ecuatorial, en T.

    B = B_ec (1/r)^3 con r en radios terrestres. En la superficie (r = 1)
    vale 31.2 uT; en GEO (r = 6.61) queda en 0.11 uT — trescientas veces
    menos, y por eso un magnetorquer en GEO es mala idea.
    """
    r = float(r_re)
    if r < 1.0:
        raise ValueError("b_tierra: r_re < 1 esta dentro del planeta")
    return float(B_TIERRA_EC / r ** 3)


def radio_larmor(q, m, v, b):
    """r = m v / (|q| B) en m. El radio del giro que no consume energia."""
    if float(b) <= 0 or float(q) == 0:
        raise ValueError("radio_larmor: hace falta B > 0 y q != 0")
    return float(float(m) * float(v) / (abs(float(q)) * float(b)))


def frecuencia_giro(q, m, b):
    """f = |q| B / (2 pi m) en Hz. No depende de la velocidad: por eso
    funciona el ciclotron (y por eso el TWT puede sincronizarse)."""
    if float(b) <= 0 or float(q) == 0:
        raise ValueError("frecuencia_giro: hace falta B > 0 y q != 0")
    return float(abs(float(q)) * float(b) / (2.0 * np.pi * float(m)))


def par_torquer(momento, b):
    """tau = m B en N m (el maximo, con m perpendicular a B)."""
    if float(b) <= 0:
        raise ValueError("par_torquer: B debe ser positivo")
    return float(float(momento) * float(b))


def tiempo_giro_torquer(momento, b, inercia, angulo_deg):
    """Segundos en barrer ese angulo partiendo del reposo, a par constante.

    theta = tau t^2 / (2 I) -> t = sqrt(2 theta I / tau). Es la cota
    optimista (sin frenar al final): con m = 0.2 A m^2 en los 30 uT de LEO
    y la inercia de un 1U (0.002 kg m^2), 90 grados salen en ~32 s. El
    clip lo cuenta como lo que es: lento, gratis e inagotable.
    """
    theta = np.radians(float(angulo_deg))
    if theta <= 0 or float(inercia) <= 0:
        raise ValueError("tiempo_giro_torquer: angulo e inercia positivos")
    tau = par_torquer(momento, b)
    return float(np.sqrt(2.0 * theta * float(inercia) / tau))


# =====================================================================
# Los numeros — modulo 2: Maxwell y la onda
# =====================================================================
def fem_espira(n_vueltas, b, area, omega):
    """Pico de la fem del alternador: N B A omega, en V.

    100 vueltas, 0.1 T, 100 cm^2 y 50 Hz dan 31.4 V — la senoide con la
    que nacio la red electrica.
    """
    if min(float(n_vueltas), float(b), float(area), float(omega)) <= 0:
        raise ValueError("fem_espira: todos los argumentos positivos")
    return float(n_vueltas) * float(b) * float(area) * float(omega)


def c_de_constantes():
    """1 / sqrt(mu0 eps0): la velocidad que Maxwell encontro escondida.

    mu0 y eps0 se midieron en mesas de laboratorio, con bobinas y
    condensadores, sin ver la luz por ningun lado. El resultado coincide
    con C_LUZ en mejor que 1 m/s — y esa coincidencia es el clip 2.2.4.
    """
    return float(1.0 / np.sqrt(MU0 * EPS0))


def impedancia_vacio():
    """eta0 = sqrt(mu0/eps0) = 376.73 ohm: la razon E/H de la onda libre."""
    return float(np.sqrt(MU0 / EPS0))


def lambda_de(f):
    """c = lambda f -> lambda en m."""
    if float(f) <= 0:
        raise ValueError("lambda_de: f debe ser positiva")
    return float(C_LUZ / float(f))


def f_de(lam):
    """c = lambda f -> f en Hz."""
    if float(lam) <= 0:
        raise ValueError("f_de: lambda debe ser positiva")
    return float(C_LUZ / float(lam))


def campo_de_flujo(s):
    """Amplitud de E de una onda plana con ese flujo medio, en V/m.

    S = E^2 / (2 eta0) -> E = sqrt(2 eta0 S). La luz del Sol (1361 W/m^2)
    lleva un kilovoltio por metro de pico: el numero gancho del 2.3.2.
    """
    if float(s) < 0:
        raise ValueError("campo_de_flujo: S no puede ser negativo")
    return float(np.sqrt(2.0 * impedancia_vacio() * float(s)))


def banda_de(f):
    """Nombre de la banda a la que pertenece esa frecuencia ('Ku', ...)."""
    fh = float(f)
    for nombre, f0, f1, _ in BANDAS:
        if f0 <= fh < f1:
            return nombre
    raise ValueError(f"banda_de: {fh:g} Hz fuera de la tabla de bandas")


# =====================================================================
# Los numeros — modulo 3: guiar y soltar la onda
# =====================================================================
def z0_coaxial(d_sobre_d, er=2.25):
    """Z0 del coaxial: (eta0 / (2 pi sqrt(er))) ln(D/d), en ohm.

    Con polietileno (er = 2.25) y D/d = 6.52 salen los 75 ohm de la TV;
    con D/d = 3.49, los 50 ohm de la radiofrecuencia. La impedancia es
    GEOMETRIA: no hay ninguna resistencia escondida en el cable.
    """
    razon = float(d_sobre_d)
    if razon <= 1.0:
        raise ValueError("z0_coaxial: D/d debe ser > 1")
    if float(er) < 1.0:
        raise ValueError("z0_coaxial: er >= 1")
    return float(impedancia_vacio() / (2.0 * np.pi * np.sqrt(float(er)))
                 * np.log(razon))


def gamma_de(zl, z0):
    """Coeficiente de reflexion (ZL - Z0) / (ZL + Z0), con signo.

    Acepta ZL = inf (abierto, +1) y ZL = 0 (corto, -1): los dos extremos
    del clip 3.2.1.
    """
    z0f = float(z0)
    if z0f <= 0:
        raise ValueError("gamma_de: Z0 debe ser positiva")
    zlf = float(zl)
    if np.isinf(zlf):
        return 1.0
    if zlf < 0:
        raise ValueError("gamma_de: ZL no puede ser negativa")
    return float((zlf - z0f) / (zlf + z0f))


def swr_de(gamma):
    """SWR = (1 + |g|) / (1 - |g|). Con |g| = 1 devuelve inf, que es lo
    que un abierto o un corto hacen de verdad."""
    g = abs(float(gamma))
    if g > 1.0 + 1e-12:
        raise ValueError("swr_de: |gamma| > 1 no es pasivo")
    if g >= 1.0 - 1e-12:
        return float("inf")
    return float((1.0 + g) / (1.0 - g))


def z_cuarto(z1, z2):
    """El transformador de lambda/4: Z = sqrt(Z1 Z2), en ohm."""
    if float(z1) <= 0 or float(z2) <= 0:
        raise ValueError("z_cuarto: impedancias positivas")
    return float(np.sqrt(float(z1) * float(z2)))


def fc_te10(a_metros):
    """Frecuencia de corte del TE10: c / (2 a), en Hz.

    Para la WR-90 (a = 22.86 mm) salen 6.557 GHz: por debajo la guia
    simplemente NO transporta — no es que atenue, es que no cabe el modo.
    """
    a = float(a_metros)
    if a <= 0:
        raise ValueError("fc_te10: a debe ser positiva")
    return float(C_LUZ / (2.0 * a))


def patron_dipolo_corto(theta):
    """|sen(theta)| — el donut del dipolo elemental (theta desde el eje)."""
    return np.abs(np.sin(np.asarray(theta, dtype=np.float64)))


def patron_dipolo_medio(theta):
    """cos(pi/2 cos t) / sen t — el dipolo de media onda, normalizado.

    En el eje (t = 0) el limite es 0 y se devuelve 0 sin dividir por cero.
    """
    t = np.asarray(theta, dtype=np.float64)
    s = np.sin(t)
    with np.errstate(divide="ignore", invalid="ignore"):
        f = np.where(np.abs(s) < 1e-9, 0.0,
                     np.abs(np.cos(np.pi / 2.0 * np.cos(t))
                            / np.where(np.abs(s) < 1e-9, 1.0, s)))
    return f


def directividad(patron, muestras=2001):
    """D de un patron con simetria acimutal, integrando de verdad.

    D = 2 / integral( f(t)^2 sen t dt ), con f normalizada a max 1. Para
    sen(t) da 1.5 exacto (dipolo corto) y para el de media onda 1.641
    (2.15 dBi): las dos cifras canonicas salen de la MISMA integral que
    dibuja los patrones, no de una tabla.
    """
    n = int(muestras)
    if n < 101 or n > 20001:
        raise ValueError("directividad: muestras fuera de 101..20001")
    t = np.linspace(0.0, np.pi, n)
    f = np.asarray(patron(t), dtype=np.float64)
    fmax = float(np.max(np.abs(f)))
    if fmax <= 0:
        raise ValueError("directividad: el patron es nulo")
    f = f / fmax
    integral = float(np.trapezoid(f ** 2 * np.sin(t), t))
    return float(2.0 / integral)


def db_de(razon):
    """10 log10 de una razon de POTENCIAS."""
    r = float(razon)
    if r <= 0:
        raise ValueError("db_de: la razon debe ser positiva")
    return float(10.0 * np.log10(r))


def ganancia_apertura(diametro, f, eficiencia=0.6):
    """Ganancia de un plato: ef (pi D / lambda)^2, ADIMENSIONAL.

    El plato de balcon (60 cm, Ku 12 GHz, ef 0.6) da 3415 veces = 35.3
    dBi. Pasar a dB es cosa de `db_de`.
    """
    if float(diametro) <= 0 or float(f) <= 0:
        raise ValueError("ganancia_apertura: D y f positivos")
    ef = float(eficiencia)
    if not 0.0 < ef <= 1.0:
        raise ValueError("ganancia_apertura: eficiencia en (0, 1]")
    return float(ef * (np.pi * float(diametro) / lambda_de(f)) ** 2)


def factor_array(n, d_lambda, fase_deg, theta):
    """|AF| normalizado de un array lineal uniforme.

    psi = 2 pi d/lambda sen(theta) + fase; AF = sin(N psi/2)/(N sin(psi/2)).
    `theta` se mide desde la NORMAL del array (broadside), en radianes.
    """
    n_el = int(n)
    if not 2 <= n_el <= 512:
        raise ValueError("factor_array: n fuera de 2..512")
    if float(d_lambda) <= 0:
        raise ValueError("factor_array: d/lambda positivo")
    t = np.asarray(theta, dtype=np.float64)
    psi = (2.0 * np.pi * float(d_lambda) * np.sin(t)
           + np.radians(float(fase_deg)))
    medio = psi / 2.0
    s = np.sin(medio)
    with np.errstate(divide="ignore", invalid="ignore"):
        af = np.where(np.abs(s) < 1e-9, 1.0,
                      np.abs(np.sin(n_el * medio)
                             / (n_el * np.where(np.abs(s) < 1e-9, 1.0, s))))
    return af


def angulo_apuntado(d_lambda, fase_deg):
    """A donde mira el array con esa rampa de fase, en GRADOS desde la
    normal: sen(theta0) = -fase / (2 pi d/lambda)."""
    if float(d_lambda) <= 0:
        raise ValueError("angulo_apuntado: d/lambda positivo")
    seno = -np.radians(float(fase_deg)) / (2.0 * np.pi * float(d_lambda))
    if abs(seno) > 1.0:
        raise ValueError("angulo_apuntado: esa fase no apunta a ningun lado "
                         "(|sen| > 1); rampa demasiado empinada")
    return float(np.degrees(np.arcsin(seno)))


# =====================================================================
# Los numeros — modulo 4: el enlace por el espacio
# =====================================================================
def frecuencia_plasma(ne):
    """f_p = (1/2pi) sqrt(Ne e^2 / (eps0 m_e)) ~ 8.98 sqrt(Ne), en Hz.

    Con el pico diurno de la capa F (Ne ~ 1e12 m^-3) salen ~9 MHz: por
    debajo la ionosfera es un espejo, por encima una ventana. La formula
    se evalua con las constantes de verdad, no con el 8.98 redondeado.
    """
    n = float(ne)
    if n <= 0:
        raise ValueError("frecuencia_plasma: Ne debe ser positiva")
    return float(np.sqrt(n * Q_E ** 2 / (EPS0 * M_ELECTRON))
                 / (2.0 * np.pi))


def retardo_iono(tec, f):
    """Camino extra que la ionosfera le añade a esa portadora, en METROS.

    d = 40.3 TEC / f^2 (TEC en electrones/m^2). Con 50 TECU (5e17) el GPS
    L1 arrastra 8.1 m y L2 13.4 m — y de esa DIFERENCIA, medible, el
    receptor despeja el TEC y cancela el peaje. El 40.3 es
    e^2/(8 pi^2 eps0 m_e) evaluado, no una constante magica.
    """
    if float(tec) < 0:
        raise ValueError("retardo_iono: TEC no puede ser negativo")
    if float(f) <= 0:
        raise ValueError("retardo_iono: f debe ser positiva")
    k_iono = Q_E ** 2 / (8.0 * np.pi ** 2 * EPS0 * M_ELECTRON)
    return float(k_iono * float(tec) / float(f) ** 2)


def radio_geo():
    """Radio de la orbita de Clarke: (mu (T/2pi)^2)^(1/3) = 42 164 km.

    T es el dia SIDERAL (86164 s), no el solar: el satelite debe seguir a
    las estrellas fijas, no al Sol. La altitud sobre el ecuador es
    radio_geo() - R_TIERRA_EQ = 35 786 km.
    """
    return float((MU_TIERRA * (T_SIDERAL / (2.0 * np.pi)) ** 2) ** (1.0 / 3.0))


def v_orbital(h):
    """Velocidad de la orbita circular a esa altitud, en m/s."""
    r = R_TIERRA + float(h)
    if float(h) < 100e3:
        raise ValueError("v_orbital: por debajo de 100 km no hay orbita")
    return float(np.sqrt(MU_TIERRA / r))


def t_orbital(h):
    """Periodo de la orbita circular a esa altitud, en s."""
    r = R_TIERRA + float(h)
    if float(h) < 100e3:
        raise ValueError("t_orbital: por debajo de 100 km no hay orbita")
    return float(2.0 * np.pi * np.sqrt(r ** 3 / MU_TIERRA))


def fspl_db(d, f):
    """Perdida de espacio libre: 20 log10(4 pi d / lambda), en dB.

    GEO en Ku (35 786 km, 12 GHz) da 205.1 dB. No es absorcion: es la
    esfera repartiendose — la geometria del clip 4.2.2 en un numero.
    """
    if float(d) <= 0 or float(f) <= 0:
        raise ValueError("fspl_db: d y f positivos")
    return float(20.0 * np.log10(4.0 * np.pi * float(d) / lambda_de(f)))


def flujo_isotropo(p, d):
    """P / (4 pi d^2), en W/m^2: lo que toca a cada metro cuadrado de la
    esfera. 100 W a distancia GEO: 6.2e-15 W/m^2."""
    if float(p) <= 0 or float(d) <= 0:
        raise ValueError("flujo_isotropo: P y d positivos")
    return float(float(p) / (4.0 * np.pi * float(d) ** 2))


def pase_leo_geometria(h, el_max_deg=90.0, muestras=241):
    """La geometria completa de un pase LEO, de una sola fuente.

    Orbita circular a altitud `h`; el maximo de elevacion del pase es
    `el_max_deg` (90 = pasa por el cenit). Ignora la rotacion terrestre
    (en los ~10 min de un pase aporta < 5 % y ensuciaria la simetria de la
    curva S sin cambiar su lectura).

    Devuelve un dict de arrays alineados:
        t          segundos, 0 en el punto mas alto, solo el tramo visible
        elevacion  grados sobre el horizonte
        distancia  m, del observador al satelite
        v_radial   m/s, positiva alejandose (derivada numerica de la
                   distancia: consistente con ella por construccion)
    El Doppler de una portadora f es -f * v_radial / C_LUZ.
    """
    n = _validar_muestras("pase_leo_geometria", muestras)
    r = R_TIERRA + float(h)
    if float(h) < 100e3:
        raise ValueError("pase_leo_geometria: por debajo de 100 km no hay "
                         "orbita")
    el_max = np.radians(float(el_max_deg))
    if not 0.0 < el_max <= np.pi / 2:
        raise ValueError("pase_leo_geometria: el_max en (0, 90]")

    # Angulo central maximo visible (elevacion 0): cos(lam0) = R/r.
    lam0 = np.arccos(R_TIERRA / r)
    # Desplazamiento transversal del plano orbital que produce ese el_max:
    # en el punto mas alto, lam = beta y tan(el) = (cos b - R/r)/sin b.
    # Se invierte por biseccion (monotona en (0, lam0)).
    def _elev(lam):
        lam = np.maximum(np.asarray(lam, dtype=np.float64), 1e-12)
        return np.arctan2(np.cos(lam) - R_TIERRA / r, np.sin(lam))

    lo, hi = 1e-9, float(lam0) - 1e-9
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if _elev(mid) > el_max:
            lo = mid
        else:
            hi = mid
    beta = 0.5 * (lo + hi)

    # A lo largo del pase: cos(lam(t)) = cos(beta) cos(w t).
    omega = np.sqrt(MU_TIERRA / r ** 3)
    # Medio-arco orbital visible: cos(lam0) = cos(beta) cos(w t_max).
    coseno = np.clip(np.cos(lam0) / np.cos(beta), -1.0, 1.0)
    t_max = np.arccos(coseno) / omega
    t = np.linspace(-t_max, t_max, n)
    lam = np.arccos(np.clip(np.cos(beta) * np.cos(omega * t), -1.0, 1.0))
    elev = np.degrees(_elev(lam))
    dist = np.sqrt(R_TIERRA ** 2 + r ** 2
                   - 2.0 * R_TIERRA * r * np.cos(lam))
    v_rad = np.gradient(dist, t)
    return {"t": t, "elevacion": elev, "distancia": dist, "v_radial": v_rad}


def atenuacion_lluvia(f_ghz, r_mm_h):
    """Atenuacion especifica de la lluvia, en dB/km (ITU-R P.838-3, pol H).

    gamma = k R^alpha, con k y alpha de la tabla embebida (10-40 GHz) e
    interpolados en log-log entre puntos. A 25 mm/h (chaparron fuerte):
    1.1 dB/km en Ku bajo (12), 2.7 en el downlink Ka de 20 y 5.1 a 30 GHz
    — la razon fisica de que la C aguante tormentas que tumban a la Ka.
    """
    f = float(f_ghz)
    rr = float(r_mm_h)
    if rr < 0:
        raise ValueError("atenuacion_lluvia: R no puede ser negativa")
    if not _P838[0][0] <= f <= _P838[-1][0]:
        raise ValueError(f"atenuacion_lluvia: f={f} GHz fuera de "
                         f"{_P838[0][0]}-{_P838[-1][0]}")
    if rr == 0.0:
        return 0.0
    fs = np.array([fila[0] for fila in _P838])
    ks = np.array([fila[1] for fila in _P838])
    als = np.array([fila[2] for fila in _P838])
    k = float(np.exp(np.interp(np.log(f), np.log(fs), np.log(ks))))
    al = float(np.interp(np.log(f), np.log(fs), als))
    return float(k * rr ** al)


def ruido_dbw(t_kelvin, ancho_hz):
    """Potencia de ruido N = k T B, en dBW.

    150 K de sistema y un transpondedor de 36 MHz: -131.3 dBW. El suelo
    contra el que se mide todo enlace.
    """
    if float(t_kelvin) <= 0 or float(ancho_hz) <= 0:
        raise ValueError("ruido_dbw: T y B positivos")
    return db_de(K_BOLTZMANN * float(t_kelvin) * float(ancho_hz))


# =====================================================================
# Piezas — modulo 1: campos quietos
# =====================================================================
_PASOS_MAX = 2400        # tope interno de las integraciones de lineas


def _campo_electrico(cargas, p):
    """E 2D (sin unidades) de una lista de cargas (q, x, y) en el punto p."""
    e = np.zeros(2)
    for q, cx, cy in cargas:
        d = p - np.array([cx, cy])
        r2 = float(d @ d)
        if r2 < 1e-6:
            return np.zeros(2)
        e += q * d / r2 ** 1.5
    return e


def _integrar_linea(cargas, semilla, sentido, caja, paso=0.035,
                    radio_carga=0.16):
    """Linea de campo por RK4 desde `semilla`, hasta una carga o el borde.

    `sentido` +1 sigue a E (sale de una positiva), -1 lo remonta. Devuelve
    un array (n, 2); n <= _PASOS_MAX.
    """
    p = np.asarray(semilla, dtype=np.float64).copy()
    puntos = [p.copy()]
    for _ in range(_PASOS_MAX):
        def _dir(pp):
            e = _campo_electrico(cargas, pp) * sentido
            n = np.linalg.norm(e)
            return e / n if n > 1e-12 else np.zeros(2)

        k1 = _dir(p)
        if not k1.any():
            break
        k2 = _dir(p + 0.5 * paso * k1)
        k3 = _dir(p + 0.5 * paso * k2)
        k4 = _dir(p + paso * k3)
        p = p + paso / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        puntos.append(p.copy())
        if not (caja[0] <= p[0] <= caja[1] and caja[2] <= p[1] <= caja[3]):
            break
        if any(np.hypot(p[0] - cx, p[1] - cy) < radio_carga
               for _, cx, cy in cargas):
            break
    return np.array(puntos)


def _submuestrear(puntos, maximo=180):
    """Reduce una polilinea larga a `maximo` puntos conservando extremos."""
    if len(puntos) <= maximo:
        return puntos
    idx = np.linspace(0, len(puntos) - 1, maximo).round().astype(int)
    return puntos[idx]


class Carga(_Anclada):
    """Punto con halo y signo. El rojo de las FUENTES, salvo que el clip
    pida otro rol."""

    def __init__(self, nucleo, halo, signo, **kwargs):
        super().__init__(halo, nucleo, signo, **kwargs)
        self.nucleo = nucleo
        self.halo = halo
        self.signo = signo
        self._anclar()

    def punto(self):
        """Centro actual de la carga (el ancla de flechas y rotulos)."""
        return self.nucleo.get_center()


def carga(signo=+1, radio=0.16, color=COLOR_CARGA):
    """La carga puntual de la familia: nucleo, halo y su signo dibujado."""
    s = 1 if float(signo) >= 0 else -1
    nucleo = Dot(ORIGIN, radius=radio, color=color)
    halo = Circle(radius=radio * 2.1, stroke_width=0, fill_color=color,
                  fill_opacity=0.16)
    brazo = radio * 0.62
    trazos = VGroup(Line((-brazo, 0, 0), (brazo, 0, 0), stroke_width=2.6,
                         color=CODE_BG))
    if s > 0:
        trazos.add(Line((0, -brazo, 0), (0, brazo, 0), stroke_width=2.6,
                        color=CODE_BG))
    return Carga(nucleo, halo, trazos)


class LineasCampo(_Anclada):
    """Mapa de lineas de E integradas sobre el campo real de las cargas."""

    def __init__(self, lineas, cargas_mob, flechas, trazas, **kwargs):
        super().__init__(lineas, flechas, cargas_mob, **kwargs)
        self.lineas = lineas
        self.cargas = cargas_mob
        self.flechas = flechas
        self._trazas = trazas
        self._anclar()

    def linea(self, i):
        """La linea i (VMobject), para encenderlas una a una."""
        return self.lineas[i]

    def punto_en(self, i, fraccion):
        """Punto de escena a esa fraccion (0-1) de la linea i."""
        traza = self._trazas[i]
        k = int(np.clip(round(float(fraccion) * (len(traza) - 1)), 0,
                        len(traza) - 1))
        base = np.array([traza[k][0], traza[k][1], 0.0])
        return base + (self.get_center() - self._centro_original)


def lineas_campo(cargas, n_lineas=8, caja=(-3.4, 3.4, -2.4, 2.4),
                 color=COLOR_E, color_carga=COLOR_CARGA, radio_carga=0.16,
                 grosor=2.2, semilla_radio=0.24, con_flechas=True):
    """Lineas del campo E de esas cargas, integradas de verdad (RK4).

    `cargas` es una lista de (q, x, y) en coordenadas de escena. De cada
    carga positiva salen `n_lineas` equiespaciadas (si no hay positivas,
    se remontan desde las negativas). La simetria del dipolo o el punto de
    silla de dos cargas iguales SALEN de la integracion, no se dibujan.
    """
    if not 1 <= int(n_lineas) <= LINEAS_MAX:
        raise ValueError(f"lineas_campo: n_lineas fuera de 1..{LINEAS_MAX}")
    cargas = [(float(q), float(x), float(y)) for q, x, y in cargas]
    if not cargas:
        raise ValueError("lineas_campo: hace falta al menos una carga")

    positivas = [c for c in cargas if c[0] > 0]
    origenes = positivas if positivas else cargas
    sentido = 1 if positivas else -1

    lineas = VGroup()
    flechas = VGroup()
    trazas = []
    for _, cx, cy in origenes:
        for k in range(int(n_lineas)):
            ang = 2.0 * np.pi * k / int(n_lineas) + 0.001
            semilla = (cx + semilla_radio * np.cos(ang),
                       cy + semilla_radio * np.sin(ang))
            traza = _integrar_linea(cargas, semilla, sentido, caja,
                                    radio_carga=radio_carga)
            traza = _submuestrear(traza)
            if len(traza) < 4:
                continue
            trazas.append(traza)
            lineas.add(_curva(traza, color, grosor=grosor))
            if con_flechas:
                m = len(traza) // 2
                d = traza[min(m + 1, len(traza) - 1)] - traza[m]
                n = np.linalg.norm(d)
                if n > 1e-9:
                    d = d / n * 0.001
                    flechas.add(Arrow(
                        (traza[m][0] - d[0], traza[m][1] - d[1], 0),
                        (traza[m][0] + d[0], traza[m][1] + d[1], 0),
                        buff=0, color=color, stroke_width=2.2,
                        max_tip_length_to_length_ratio=200.0,
                        tip_length=0.13))

    cargas_mob = VGroup()
    for q, cx, cy in cargas:
        c = carga(signo=q, color=color_carga)
        c.move_to((cx, cy, 0))
        cargas_mob.add(c)
    return LineasCampo(lineas, cargas_mob, flechas, trazas)


class Equipotenciales(_Anclada):
    """Curvas de nivel del potencial, integradas perpendiculares a E."""

    def __init__(self, curvas, valores, **kwargs):
        super().__init__(curvas, **kwargs)
        self.curvas = curvas
        self.valores = valores
        self._anclar()

    def curva_nivel(self, i):
        return self.curvas[i]


def equipotenciales(cargas, radios=(0.45, 0.75, 1.1), color=COLOR_CALCULO,
                    caja=(-3.4, 3.4, -2.4, 2.4), grosor=1.6):
    """Equipotenciales alrededor de cada carga, una por radio de arranque.

    Cada curva arranca a ese radio de una carga y sigue la direccion
    PERPENDICULAR a E (una equipotencial es una linea de nivel: E no tiene
    componente a lo largo de ella). Se integra hasta cerrar la vuelta o
    salir de la caja; que alrededor de una carga aislada salgan circulos y
    en el dipolo ovalos que se deforman es resultado, no dibujo.
    """
    if len(radios) * len(cargas) > LINEAS_MAX:
        raise ValueError("equipotenciales: demasiadas curvas (tope "
                         f"{LINEAS_MAX})")
    cargas = [(float(q), float(x), float(y)) for q, x, y in cargas]
    curvas = VGroup()
    valores = []
    for q, cx, cy in cargas:
        for radio in radios:
            inicio = np.array([cx + float(radio), cy])
            p = inicio.copy()
            puntos = [p.copy()]
            paso = 0.03
            for n_paso in range(_PASOS_MAX):
                e = _campo_electrico(cargas, p)
                nrm = np.linalg.norm(e)
                if nrm < 1e-12:
                    break
                d = np.array([-e[1], e[0]]) / nrm
                # RK2 basta: la curva se cierra sola y el error es visual.
                pm = p + 0.5 * paso * d
                em = _campo_electrico(cargas, pm)
                nm = np.linalg.norm(em)
                if nm < 1e-12:
                    break
                p = p + paso * np.array([-em[1], em[0]]) / nm
                puntos.append(p.copy())
                if not (caja[0] <= p[0] <= caja[1]
                        and caja[2] <= p[1] <= caja[3]):
                    break
                if n_paso > 24 and np.linalg.norm(p - inicio) < paso:
                    puntos.append(inicio.copy())
                    break
            if len(puntos) > 8:
                traza = _submuestrear(np.array(puntos))
                curvas.add(_curva(traza, color, grosor=grosor))
                valores.append(abs(q) / float(radio))
    return Equipotenciales(curvas, valores)


class HazCurvas(_Cartesiano):
    """n curvas en una caja de ejes, con las cifras FUERA de la caja.

    La pieza multiuso de la familia: 1/r^2 contra 1/r^3, B(r), la
    atenuacion del cable, las curvas de lluvia... Las etiquetas van a la
    derecha de la caja, a la altura final de su curva y de su color — la
    leccion aprendida en Aerodinamica: dentro de un haz no hay hueco.
    """

    def __init__(self, ejes, curvas, etiquetas, funciones, log_x, log_y,
                 rango_x, rango_y, ancho, alto, origen, **kwargs):
        super().__init__(ejes, curvas, etiquetas, **kwargs)
        self.ejes = ejes
        self.curvas = curvas
        self.etiquetas = etiquetas
        self._funciones = funciones
        self._log_x = log_x
        self._log_y = log_y
        self._calibrar(rango_x, rango_y, ancho, alto, origen)

    def _tx(self, x):
        return float(np.log10(max(float(x), _EPS))) if self._log_x \
            else float(x)

    def _ty(self, y):
        return float(np.log10(max(float(y), _EPS))) if self._log_y \
            else float(y)

    def valor(self, i, x):
        """El numero que el clip rotula: misma fuente que el trazo."""
        return float(self._funciones[i](float(x)))

    def punto_de(self, i, x):
        """Punto de escena sobre la curva i en la abscisa x (de DATO)."""
        return self._en(self._tx(x), self._ty(self.valor(i, x)))

    def curva(self, i):
        return self.curvas[i]

    def vertical_en(self, x, color=COLOR_CALCULO):
        """Guia vertical de lado a lado de la caja, en la abscisa x."""
        arriba = self._en(self._tx(x), self._ry[1])
        abajo = self._en(self._tx(x), self._ry[0])
        return DashedLine(abajo, arriba, stroke_width=1.5, color=color,
                          dash_length=0.07)

    def horizontal_en(self, y, color=COLOR_CALCULO):
        """Guia horizontal de lado a lado, en la ordenada y (de DATO)."""
        izda = self._en(self._rx[0], self._ty(y))
        dcha = self._en(self._rx[1], self._ty(y))
        return DashedLine(izda, dcha, stroke_width=1.5, color=color,
                          dash_length=0.07)


def haz_curvas(funciones, rango_x, colores, nombres=None, ancho=5.8,
               alto=2.9, log_x=False, log_y=False, muestras=140,
               color_ejes=COLOR_EJE, font_size=14, etiqueta_x="",
               etiqueta_y="", grosor=2.8, suave=True):
    """La caja de ejes con un haz de hasta CURVAS_MAX funciones.

    `funciones` reciben la abscisa de DATO y devuelven la ordenada de
    DATO; si `log_x`/`log_y`, la CAJA es logaritmica pero las funciones
    siguen hablando en datos. El rango vertical se toma del propio haz.
    """
    if not 1 <= len(funciones) <= CURVAS_MAX:
        raise ValueError(f"haz_curvas: 1..{CURVAS_MAX} funciones")
    if len(colores) < len(funciones):
        raise ValueError("haz_curvas: falta un color por funcion")
    muestras = _validar_muestras("haz_curvas", muestras)
    x0, x1 = float(rango_x[0]), float(rango_x[1])
    if x1 <= x0:
        raise ValueError("haz_curvas: rango_x invertido")
    if log_x and x0 <= 0:
        raise ValueError("haz_curvas: log_x pide abscisas positivas")

    xs = (np.logspace(np.log10(x0), np.log10(x1), muestras) if log_x
          else np.linspace(x0, x1, muestras))
    tablas = []
    for funcion in funciones:
        ys = np.array([float(funcion(float(x))) for x in xs])
        tablas.append(ys)
    todos = np.concatenate(tablas)
    if log_y:
        if float(todos.min()) <= 0:
            raise ValueError("haz_curvas: log_y pide ordenadas positivas")
        ty0, ty1 = float(np.log10(todos.min())), float(np.log10(todos.max()))
    else:
        ty0, ty1 = float(todos.min()), float(todos.max())
        if ty0 > 0:
            ty0 = 0.0
    margen = 0.06 * max(ty1 - ty0, _EPS)
    ty1 += margen

    tx = np.log10(xs) if log_x else xs
    tx0, tx1 = float(tx[0]), float(tx[-1])

    ejes, origen = _ejes_xy(ancho, alto, color_ejes)
    curvas = VGroup()
    for ys, color in zip(tablas, colores):
        ty = np.log10(ys) if log_y else ys
        fx = (tx - tx0) / max(tx1 - tx0, _EPS)
        fy = np.clip((ty - ty0) / max(ty1 - ty0, _EPS), 0.0, 1.0)
        pts = origen + np.column_stack([fx * ancho, fy * alto,
                                        np.zeros(len(fx))])
        curvas.add(_curva(pts, color, grosor=grosor, suave=suave))

    etiquetas = VGroup()
    if nombres:
        for ys, color, nombre in zip(tablas, colores, nombres):
            ty_fin = float(np.log10(ys[-1]) if log_y else ys[-1])
            fy = float(np.clip((ty_fin - ty0) / max(ty1 - ty0, _EPS),
                               0.0, 1.0))
            tag = _texto_display(str(nombre), font_size=font_size + 2,
                                 color=color)
            tag.move_to(origen + np.array([ancho + 0.16, fy * alto, 0.0]))
            tag.align_to(origen + np.array([ancho + 0.16, 0, 0]), LEFT)
            etiquetas.add(tag)

    if etiqueta_x:
        tag_x = _texto_display(etiqueta_x, font_size=font_size + 1)
        tag_x.next_to(ejes[0], DOWN, buff=0.14)
        ejes.add(tag_x)
    if etiqueta_y:
        tag_y = _texto_display(etiqueta_y, font_size=font_size + 1)
        tag_y.next_to(ejes[1], UP, buff=0.10)
        ejes.add(tag_y)

    return HazCurvas(ejes, curvas, etiquetas, list(funciones), bool(log_x),
                     bool(log_y), (tx0, tx1), (ty0, ty1), ancho, alto,
                     origen)


class HiloCorriente(_Anclada):
    """El hilo de Oersted visto de frente: la corriente sale del papel."""

    def __init__(self, hilo, circulos, brujulas, radios, **kwargs):
        super().__init__(circulos, brujulas, hilo, **kwargs)
        self.hilo = hilo
        self.circulos = circulos
        self.brujulas = brujulas
        self._radios = radios
        self._anclar()

    def circulo(self, i):
        return self.circulos[i]

    def brujula(self, i):
        return self.brujulas[i]

    def b_relativo(self, i):
        """B del circulo i relativo al primero (cae como 1/r)."""
        return float(self._radios[0] / self._radios[i])


def hilo_corriente(n_circulos=4, radio_min=0.55, paso=0.55,
                   n_brujulas=6, color_hilo=COLOR_CARGA, color_b=COLOR_B,
                   color_brujula=COLOR_B):
    """El experimento de Oersted: hilo al centro (corriente hacia fuera,
    el punto), circulos de B y brujulas tangentes.

    El grosor de cada circulo cae como 1/r — el B = mu0 I / 2 pi r hecho
    trazo — y las brujulas se orientan tangentes, que es lo que dejo
    helado a Oersted: ninguna apunta al hilo.
    """
    if not 1 <= int(n_circulos) <= 8:
        raise ValueError("hilo_corriente: n_circulos fuera de 1..8")
    nucleo = Dot(ORIGIN, radius=0.13, color=color_hilo)
    punto = Dot(ORIGIN, radius=0.045, color=CODE_BG)
    hilo = VGroup(Circle(radius=0.2, color=color_hilo, stroke_width=2.2),
                  nucleo, punto)

    radios, circulos = [], VGroup()
    for i in range(int(n_circulos)):
        r = radio_min + paso * i
        radios.append(r)
        circulos.add(Circle(radius=r, color=color_b,
                            stroke_width=3.2 * radio_min / r,
                            stroke_opacity=0.9))

    brujulas = VGroup()
    r_brujula = radio_min + paso * min(1, int(n_circulos) - 1)
    for k in range(int(n_brujulas)):
        ang = 2.0 * np.pi * k / int(n_brujulas)
        centro = np.array([r_brujula * np.cos(ang),
                           r_brujula * np.sin(ang), 0.0])
        tangente = np.array([-np.sin(ang), np.cos(ang), 0.0]) * 0.19
        aguja = Arrow(centro - tangente, centro + tangente, buff=0,
                      color=color_brujula, stroke_width=3.0,
                      max_tip_length_to_length_ratio=0.5, tip_length=0.12)
        caja = Circle(radius=0.16, color=COLOR_EJE, stroke_width=1.4)
        caja.move_to(centro)
        brujulas.add(VGroup(caja, aguja))
    return HiloCorriente(hilo, circulos, brujulas, radios)


class SolenoideCorte(_Anclada):
    """El solenoide cortado a lo largo: espiras arriba y abajo, B dentro."""

    def __init__(self, espiras_arriba, espiras_abajo, flechas, tubo,
                 **kwargs):
        super().__init__(tubo, flechas, espiras_arriba, espiras_abajo,
                         **kwargs)
        self.espiras_arriba = espiras_arriba
        self.espiras_abajo = espiras_abajo
        self.flechas = flechas
        self.tubo = tubo
        self._anclar()

    def espira(self, i):
        """La pareja (arriba, abajo) de la espira i."""
        return VGroup(self.espiras_arriba[i], self.espiras_abajo[i])


def solenoide_corte(n_espiras=9, largo=4.6, alto=1.5,
                    color_espira=COLOR_CARGA, color_b=COLOR_B):
    """Corte longitudinal: cruces arriba (corriente entrando), puntos
    abajo (saliendo) y el campo uniforme en el interior.

    Que dentro sea denso y fuera no haya nada ES el mensaje del clip; por
    eso las flechas solo viven en el interior.
    """
    if not 3 <= int(n_espiras) <= 16:
        raise ValueError("solenoide_corte: n_espiras fuera de 3..16")
    xs = np.linspace(-largo / 2, largo / 2, int(n_espiras))
    arriba, abajo = VGroup(), VGroup()
    for x in xs:
        cruz_c = Circle(radius=0.13, color=color_espira, stroke_width=2.0)
        cruz_c.move_to((x, alto / 2, 0))
        brazo = 0.13 * 0.7071
        cruz = VGroup(cruz_c,
                      Line((x - brazo, alto / 2 - brazo, 0),
                           (x + brazo, alto / 2 + brazo, 0),
                           stroke_width=1.8, color=color_espira),
                      Line((x - brazo, alto / 2 + brazo, 0),
                           (x + brazo, alto / 2 - brazo, 0),
                           stroke_width=1.8, color=color_espira))
        arriba.add(cruz)
        pto = VGroup(Circle(radius=0.13, color=color_espira,
                            stroke_width=2.0),
                     Dot((0, 0, 0), radius=0.045, color=color_espira))
        pto.move_to((x, -alto / 2, 0))
        abajo.add(pto)

    flechas = VGroup()
    for y in (-alto * 0.22, alto * 0.22):
        for x0 in np.linspace(-largo / 2 + 0.35, largo / 2 - 1.05, 4):
            flechas.add(Arrow((x0, y, 0), (x0 + 0.7, y, 0), buff=0,
                              color=color_b, stroke_width=3.0,
                              max_tip_length_to_length_ratio=0.4,
                              tip_length=0.14))
    tubo = Rectangle(width=largo + 0.5, height=alto + 0.62,
                     stroke_width=1.2, color=COLOR_EJE)
    return SolenoideCorte(arriba, abajo, flechas, tubo)


class TierraIman(_Anclada):
    """La Tierra y sus lineas de dipolo r = L sen^2(theta)."""

    def __init__(self, tierra, lineas, trazas, radio_escena, **kwargs):
        super().__init__(lineas, tierra, **kwargs)
        self.tierra = tierra
        self.lineas = lineas
        self._trazas = trazas
        self._radio = radio_escena
        self._anclar()

    def linea(self, i):
        return self.lineas[i]

    def punto_en(self, i, fraccion):
        """Punto de escena a esa fraccion (0-1) de la linea i — el rail
        por el que los clips hacen viajar particulas atrapadas."""
        traza = self._trazas[i]
        k = int(np.clip(round(float(fraccion) * (len(traza) - 1)), 0,
                        len(traza) - 1))
        base = np.array([traza[k][0], traza[k][1], 0.0])
        return base + (self.get_center() - self._centro_original)

    def radio_escena(self):
        """El radio de la Tierra en unidades de escena (para escalar)."""
        return self._radio


def tierra_iman(radio=0.72, conchas=(1.7, 2.6, 3.6), color_b=COLOR_B,
                muestras=120):
    """El dipolo terrestre: cada linea es r = L sen^2(theta), la formula
    exacta de una linea de campo de dipolo. `conchas` son las L (donde la
    linea cruza el ecuador), en radios terrestres.

    La linea se recorre de un casquete al otro (donde r cae al radio de la
    Tierra) — el rail completo de una particula atrapada.
    """
    muestras = _validar_muestras("tierra_iman", muestras)
    if len(conchas) > LINEAS_MAX // 4:
        raise ValueError("tierra_iman: demasiadas conchas")
    tierra = VGroup(
        Circle(radius=radio, color=CODE_MUTED, stroke_width=2.0,
               fill_color="#0b1d33", fill_opacity=1.0),
        Arc(radius=radio * 0.62, start_angle=0.6, angle=1.1,
            color=CODE_MUTED, stroke_width=1.2),
        Arc(radius=radio * 0.55, start_angle=3.6, angle=0.9,
            color=CODE_MUTED, stroke_width=1.2))

    lineas, trazas = VGroup(), []
    for lado in (+1, -1):
        for l_re in conchas:
            # theta desde el polo; la linea toca la superficie donde
            # sen^2 = 1/L.
            t0 = np.arcsin(np.sqrt(1.0 / float(l_re)))
            ts = np.linspace(t0, np.pi - t0, muestras)
            rs = float(l_re) * np.sin(ts) ** 2 * radio
            xs = lado * rs * np.sin(ts)
            ys = rs * np.cos(ts)
            traza = np.column_stack([xs, ys])
            trazas.append(traza)
            lineas.add(_curva(traza, color_b, grosor=2.0))
    return TierraIman(tierra, lineas, trazas, radio)


class CubesatTorquer(_Anclada):
    """Un cubesat con su bobina, el campo de fondo y el par que resulta."""

    def __init__(self, cuerpo, bobina, flecha_b, flecha_m, arco_par,
                 momento, campo, inercia, **kwargs):
        super().__init__(flecha_b, cuerpo, bobina, flecha_m, arco_par,
                         **kwargs)
        self.cuerpo = cuerpo
        self.bobina = bobina
        self.flecha_b = flecha_b
        self.flecha_m = flecha_m
        self.arco_par = arco_par
        self._momento = momento
        self._campo = campo
        self._inercia = inercia
        self._anclar()

    def par(self):
        """El par maximo, N m — la misma cuenta que rotula el clip."""
        return par_torquer(self._momento, self._campo)

    def segundos_para(self, angulo_deg):
        return tiempo_giro_torquer(self._momento, self._campo,
                                   self._inercia, angulo_deg)

    def girable(self):
        """Lo que el clip debe rotar (cuerpo + bobina + momento), sin
        llevarse el campo de fondo ni el arco del par."""
        return VGroup(self.cuerpo, self.bobina, self.flecha_m)


def cubesat_torquer(lado=1.15, momento=0.2, campo=30e-6, inercia=0.002,
                    color_b=COLOR_B, color_m=COLOR_CARGA):
    """El cubesat 1U con su magnetorquer: la bobina (fuente, rojo), el
    campo terrestre de fondo (verde) y el par tau = m x B.

    Los numeros por defecto son los de un 1U real: 0.2 A m^2 de bobina,
    30 uT en LEO y 0.002 kg m^2 de inercia -> 90 grados en ~32 s.
    """
    cuerpo = VGroup(
        Rectangle(width=lado, height=lado, stroke_width=2.2,
                  color=CODE_MUTED, fill_color="#101826", fill_opacity=1.0))
    for s in (-1, 1):
        panel = Rectangle(width=lado * 0.85, height=lado * 0.30,
                          stroke_width=1.6, color=CODE_MUTED,
                          fill_color="#0b2437", fill_opacity=1.0)
        panel.move_to((s * (lado / 2 + lado * 0.85 / 2 + 0.06), 0, 0))
        for k in range(2):
            raya = Line((-lado * 0.425 + (k + 1) * lado * 0.283, -lado * 0.15,
                         0),
                        (-lado * 0.425 + (k + 1) * lado * 0.283, lado * 0.15,
                         0), stroke_width=1.0, color=CODE_MUTED)
            raya.shift(panel.get_center())
            cuerpo.add(raya)
        cuerpo.add(panel)

    bobina = VGroup()
    for r in (0.30, 0.36, 0.42):
        bobina.add(Circle(radius=r * lado, color=color_m, stroke_width=1.8,
                          stroke_opacity=0.9))
    flecha_m = Arrow((0, 0, 0), (0, lado * 0.95, 0), buff=0, color=color_m,
                     stroke_width=3.4, tip_length=0.16)

    flechas = VGroup()
    for x in np.linspace(-2.8, 2.8, 5):
        flechas.add(Arrow((x, -1.85, 0), (x + 1.35, -1.35, 0), buff=0,
                          color=color_b, stroke_width=2.4,
                          stroke_opacity=0.65, tip_length=0.13))
    arco = Arc(radius=lado * 1.15, start_angle=np.pi / 2,
               angle=-np.pi / 3.2, color=COLOR_CALCULO, stroke_width=3.0)
    punta = Arrow(arco.get_end() - 0.001 * (arco.get_end()
                                            - arco.point_from_proportion(0.97)),
                  arco.get_end(), buff=0, color=COLOR_CALCULO,
                  stroke_width=3.0, tip_length=0.15)
    arco_par = VGroup(arco, punta)
    return CubesatTorquer(cuerpo, bobina, flechas, flecha_m, arco_par,
                          momento, campo, inercia)


class GiroLarmor(_Anclada):
    """El circulo de Larmor: la fuerza que no trabaja, solo tuerce."""

    def __init__(self, fondo, trayectoria, particula, radio_escena,
                 numeros, **kwargs):
        super().__init__(fondo, trayectoria, particula, **kwargs)
        self.fondo = fondo
        self.trayectoria = trayectoria
        self.particula = particula
        self._radio = radio_escena
        self.numeros = numeros
        self._anclar()

    def punto_de(self, angulo_deg):
        """Punto de escena sobre el circulo a ese angulo."""
        a = np.radians(float(angulo_deg))
        return self._desde(self._radio * np.cos(a),
                           self._radio * np.sin(a))

    def flecha_v(self, angulo_deg, largo=0.85, color=COLOR_CARGA):
        """La velocidad: tangente al circulo en ese punto."""
        a = np.radians(float(angulo_deg))
        p = self.punto_de(angulo_deg)
        d = np.array([-np.sin(a), np.cos(a), 0.0]) * largo
        return Arrow(p, p + d, buff=0, color=color, stroke_width=3.4,
                     tip_length=0.16)

    def flecha_f(self, angulo_deg, largo=0.7, color=COLOR_CALCULO):
        """La fuerza: siempre hacia el centro. Perpendicular a v SIEMPRE:
        por eso no puede darle ni quitarle energia a la particula."""
        a = np.radians(float(angulo_deg))
        p = self.punto_de(angulo_deg)
        d = -np.array([np.cos(a), np.sin(a), 0.0]) * largo
        return Arrow(p, p + d, buff=0, color=color, stroke_width=3.4,
                     tip_length=0.16)


def giro_larmor(radio=1.5, q=Q_E, m=M_ELECTRON, v=1.0e7, b=50e-6,
                color_b=COLOR_B, color_traza=COLOR_CARGA, n_marcas=24):
    """La particula girando en un campo que sale del papel (puntos verdes).

    Los numeros del clip (radio 1.14 m, giro a 1.4 MHz para un electron a
    1e7 m/s en los 50 uT terrestres) salen de `radio_larmor` y
    `frecuencia_giro` con estos mismos argumentos.
    """
    if not 4 <= int(n_marcas) <= 64:
        raise ValueError("giro_larmor: n_marcas fuera de 4..64")
    fondo = VGroup()
    lado = radio * 2.9
    for x in np.linspace(-lado / 2, lado / 2, 5):
        for y in np.linspace(-lado / 2, lado / 2, 4):
            fondo.add(VGroup(
                Circle(radius=0.085, color=color_b, stroke_width=1.4,
                       stroke_opacity=0.55),
                Dot((0, 0, 0), radius=0.03, color=color_b,
                    fill_opacity=0.55)).move_to((x, y, 0)))
    trayectoria = Circle(radius=radio, color=color_traza, stroke_width=2.6)
    particula = carga(signo=-1, radio=0.13, color=color_traza)
    particula.move_to((radio, 0, 0))
    numeros = {"radio_m": radio_larmor(q, m, v, b),
               "frecuencia_hz": frecuencia_giro(q, m, b)}
    return GiroLarmor(fondo, trayectoria, particula, radio, numeros)


class EspejoMagnetico(_Anclada):
    """La botella: la espiral que se aprieta y rebota donde B crece."""

    def __init__(self, lineas, bobinas, trayectoria, traza, **kwargs):
        super().__init__(lineas, bobinas, trayectoria, **kwargs)
        self.lineas = lineas
        self.bobinas = bobinas
        self.trayectoria = trayectoria
        self._traza = traza
        self._anclar()

    def punto_en(self, fraccion):
        """Punto de escena a esa fraccion (0-1) de la espiral."""
        traza = self._traza
        k = int(np.clip(round(float(fraccion) * (len(traza) - 1)), 0,
                        len(traza) - 1))
        base = np.array([traza[k][0], traza[k][1], 0.0])
        return base + (self.get_center() - self._centro_original)


def espejo_magnetico(largo=5.2, radio_max=1.05, apriete=0.42, vueltas=9.5,
                     rebotes=2, color_b=COLOR_B, color_traza=COLOR_CARGA,
                     muestras=360):
    """Las lineas que se aprietan en los extremos y la espiral atrapada.

    La espiral es la proyeccion 2D de una helice cuyo radio sigue al tubo
    de campo (donde las lineas se juntan, B crece y el radio de giro cae
    como 1/sqrt(B)) y cuyo avance se frena hasta REBOTAR en los espejos:
    la conservacion del momento magnetico hecha dibujo.
    """
    if muestras > MUESTRAS_MAX:
        raise ValueError("espejo_magnetico: muestras supera MUESTRAS_MAX")
    xs_l = np.linspace(-largo / 2, largo / 2, 90)
    # Tubo de campo: radio minimo en los extremos (apriete), maximo en el
    # centro. B ~ 1/area -> B_rel = (r_centro / r(x))^2.
    def _radio_tubo(x):
        u = 2.0 * np.asarray(x) / largo          # -1..1
        return radio_max * (1.0 - (1.0 - apriete) * u ** 2)

    lineas = VGroup()
    for s in (-1.0, -0.5, 0.5, 1.0):
        ys = s * _radio_tubo(xs_l)
        lineas.add(_curva(np.column_stack([xs_l, ys]), color_b, grosor=2.0))

    bobinas = VGroup()
    for lado in (-1, 1):
        x = lado * largo / 2
        r = float(_radio_tubo(x)) + 0.16
        bobinas.add(VGroup(
            Line((x, r, 0), (x, r + 0.34, 0), stroke_width=5.0,
                 color=COLOR_EJE),
            Line((x, -r, 0), (x, -r - 0.34, 0), stroke_width=5.0,
                 color=COLOR_EJE)))

    # La espiral: el centro-guia oscila (rebota) y el radio sigue al tubo.
    t = np.linspace(0.0, float(rebotes) * np.pi, muestras)
    xg = (largo / 2 * 0.92) * np.sin(t)          # el rebote: seno del avance
    rg = _radio_tubo(xg) * 0.72
    fase = 2.0 * np.pi * vueltas * t / t[-1]
    yg = rg * np.sin(fase)
    traza = np.column_stack([xg, yg])
    trayectoria = _curva(traza, color_traza, grosor=2.2, suave=False)
    return EspejoMagnetico(lineas, bobinas, trayectoria, traza)


class MapaOrbitas(_Anclada):
    """La Tierra a escala con sus cinturones y las orbitas de trabajo."""

    def __init__(self, tierra, cinturones, orbitas, nombres, escala,
                 alturas, **kwargs):
        super().__init__(cinturones, orbitas, tierra, **kwargs)
        self.tierra = tierra
        self.cinturones = cinturones
        self.orbitas = orbitas
        self._nombres = list(nombres)
        self._escala = escala
        self._alturas = alturas
        self._anclar()

    def orbita(self, nombre):
        return self.orbitas[self._nombres.index(nombre)]

    def punto_orbita(self, nombre, angulo_deg):
        r = ((R_TIERRA + self._alturas[self._nombres.index(nombre)])
             * self._escala)
        a = np.radians(float(angulo_deg))
        return self._desde(r * np.cos(a), r * np.sin(a))

    def periodo_horas(self, nombre):
        """El periodo de esa orbita, en horas — de `t_orbital`, no a mano."""
        h = self._alturas[self._nombres.index(nombre)]
        return t_orbital(h) / 3600.0

    def cinturon(self, i):
        return self.cinturones[i]


def mapa_orbitas(radio_tierra=0.34, con_cinturones=True,
                 orbitas=(("LEO", 550e3), ("GPS", 20200e3),
                          ("GEO", 35786e3)),
                 color_cinturon=COLOR_CARGA, color_orbita=COLOR_CALCULO):
    """El mapa a ESCALA: la Tierra, los dos cinturones de Van Allen y las
    orbitas que los esquivan (o no).

    Todo es lineal en distancia — LEO pegada a la superficie, GPS metida
    en el corazon del cinturon exterior y GEO en su borde de fuera: las
    tres lecturas del clip 1.3.3 son geometria de este dibujo.
    Cinturones: interior 1.2-2.0 R_E, exterior 3.0-7.0 R_E (protones y
    electrones atrapados; fronteras redondeadas de los modelos AP8/AE8).
    """
    if len(orbitas) > 5:
        raise ValueError("mapa_orbitas: demasiadas orbitas")
    escala = radio_tierra / R_TIERRA
    tierra = Circle(radius=radio_tierra, color=CODE_MUTED, stroke_width=1.8,
                    fill_color="#0b1d33", fill_opacity=1.0)

    cinturones = VGroup()
    if con_cinturones:
        for r0, r1, opacidad in ((1.2, 2.0, 0.20), (3.0, 7.0, 0.12)):
            cinturones.add(Annulus(inner_radius=r0 * radio_tierra,
                                   outer_radius=r1 * radio_tierra,
                                   stroke_width=0, fill_color=color_cinturon,
                                   fill_opacity=opacidad))

    orbitas_mob = VGroup()
    nombres, alturas = [], []
    for nombre, h in orbitas:
        r = (R_TIERRA + float(h)) * escala
        orbitas_mob.add(DashedVMobject(
            Circle(radius=r, color=color_orbita, stroke_width=1.8),
            num_dashes=48))
        nombres.append(nombre)
        alturas.append(float(h))
    return MapaOrbitas(tierra, cinturones, orbitas_mob, nombres, escala,
                       alturas)


class TuboOndas(_Anclada):
    """El TWT: la helice, el haz y la onda que sale mas alta que entro."""

    def __init__(self, tubo, helice, haz, onda_entrada, onda_salida, eje,
                 ganancia, **kwargs):
        super().__init__(tubo, helice, haz, onda_entrada, onda_salida,
                         **kwargs)
        self.tubo = tubo
        self.helice = helice
        self.haz = haz
        self.onda_entrada = onda_entrada
        self.onda_salida = onda_salida
        self.eje = eje
        self._ganancia = ganancia
        self._anclar()

    def ganancia_db(self):
        """La razon de amplitudes dibujada, pasada a dB de potencia."""
        return db_de(self._ganancia ** 2)


def tubo_ondas(largo=5.6, alto=1.15, ganancia_amplitud=4.0, n_vueltas=13,
               n_electrones=7, color_haz=COLOR_CARGA, color_onda=COLOR_ONDA):
    """El tubo de ondas progresivas de un transpondedor.

    La helice frena a la onda para que viaje al paso del haz de
    electrones; el haz le va cediendo energia y la senoide de salida se
    dibuja `ganancia_amplitud` veces mas alta que la de entrada (16 veces
    en potencia = 12 dB; los TWT reales encadenan etapas hasta 50-60 dB).
    """
    if not 1.5 <= float(ganancia_amplitud) <= 8.0:
        raise ValueError("tubo_ondas: ganancia_amplitud fuera de 1.5..8")
    tubo = Rectangle(width=largo, height=alto, stroke_width=2.0,
                     color=CODE_MUTED)
    xs = np.linspace(-largo / 2 + 0.3, largo / 2 - 0.3, int(n_vueltas) * 8)
    ys = 0.30 * alto * np.sin(2 * np.pi * n_vueltas
                              * (xs - xs[0]) / (xs[-1] - xs[0]))
    helice = _curva(np.column_stack([xs, ys]), CODE_MUTED, grosor=1.6)

    haz = VGroup()
    for x in np.linspace(-largo / 2 + 0.45, largo / 2 - 0.45,
                         int(n_electrones)):
        haz.add(Dot((x, 0, 0), radius=0.055, color=color_haz))

    def _senoide(x0, amplitud, color, ancho_s=1.6):
        xs_s = np.linspace(0, ancho_s, 60)
        ys_s = amplitud * np.sin(2 * np.pi * 2.2 * xs_s / ancho_s)
        pts = np.column_stack([xs_s + x0, ys_s])
        return _curva(pts, color, grosor=2.6)

    onda_entrada = _senoide(-largo / 2 - 1.9, 0.16, color_onda)
    onda_salida = _senoide(largo / 2 + 0.3, 0.16 * ganancia_amplitud,
                           color_onda)
    eje = Line((-largo / 2, 0, 0), (largo / 2, 0, 0), stroke_width=1.0,
               color=COLOR_EJE, stroke_opacity=0.0)
    return TuboOndas(tubo, helice, haz, onda_entrada, onda_salida, eje,
                     ganancia_amplitud)


# =====================================================================
# Piezas — modulo 2: Maxwell y la onda
# =====================================================================
def _flujo_iman(x):
    """Flujo (normalizado) de un iman en el eje de una espira, a distancia
    x del plano: (1 + x^2)^(-3/2). La forma exacta del dipolo en eje —
    la misma funcion alimenta a `espira_iman` y a `curvas_flujo_fem`,
    para que el dibujo del iman y la curva del flujo no puedan discrepar.
    """
    xx = np.asarray(x, dtype=np.float64)
    return (1.0 + xx ** 2) ** -1.5


class EspiraIman(_Anclada):
    """El experimento fundacional: iman, bobina y galvanometro."""

    def __init__(self, bobina, iman, galvanometro, aguja, **kwargs):
        super().__init__(bobina, iman, galvanometro, aguja, **kwargs)
        self.bobina = bobina
        self.iman = iman
        self.galvanometro = galvanometro
        self.aguja = aguja
        self._anclar()

    def flujo_en(self, x):
        """Flujo normalizado con el iman a x espiras de distancia."""
        return float(_flujo_iman(x))

    def aguja_a(self, deflexion):
        """La aguja girada a esa deflexion (-1..1). Para un
        ReplacementTransform del clip."""
        d = float(np.clip(deflexion, -1.0, 1.0))
        pivote = self.galvanometro[0].get_arc_center()
        nueva = Line(pivote, pivote + 0.52 * np.array(
            [np.sin(d * 1.05), np.cos(d * 1.05), 0.0]),
            stroke_width=3.0, color=COLOR_CALCULO)
        return nueva


def espira_iman(n_espiras=5, color_iman=COLOR_B, color_bobina=COLOR_CARGA):
    """El iman que entra en la bobina y la aguja que se entera.

    El iman es la FUENTE de campo (verde, rol de B); la corriente inducida
    vive en la bobina (rojo, rol de fuente electrica). El galvanometro es
    un arco con aguja: `aguja_a(d)` la gira, el clip decide cuando.
    """
    bobina = VGroup()
    for i in range(int(n_espiras)):
        x = -0.5 + i * 0.25
        bobina.add(Circle(radius=0.55, color=color_bobina,
                          stroke_width=2.6).stretch(0.34, 0).move_to(
                              (x, 0, 0)))
    iman = VGroup(
        Rectangle(width=1.15, height=0.42, stroke_width=1.8,
                  color=color_iman, fill_color="#0c2b22",
                  fill_opacity=1.0),
        Line((0, -0.21, 0), (0, 0.21, 0), stroke_width=1.4,
             color=color_iman))
    letra_n = _texto_hud("N", font_size=17, color=color_iman)
    letra_n.move_to((0.32, 0, 0))
    letra_s = _texto_hud("S", font_size=17, color=COLOR_EJE)
    letra_s.move_to((-0.32, 0, 0))
    iman.add(letra_n, letra_s)
    iman.move_to((-2.6, 0, 0))

    arco = Arc(radius=0.62, start_angle=np.pi * 0.25, angle=np.pi * 0.5,
               color=CODE_MUTED, stroke_width=2.0)
    arco.move_arc_center_to((2.4, -0.3, 0))
    marco = Circle(radius=0.75, color=COLOR_EJE, stroke_width=1.6)
    marco.move_to((2.4, 0, 0))
    galvanometro = VGroup(arco, marco)
    aguja = Line((2.4, -0.3, 0), (2.4, 0.22, 0), stroke_width=3.0,
                 color=COLOR_CALCULO)
    return EspiraIman(bobina, iman, galvanometro, aguja)


class CurvasFlujoFem(_Anclada):
    """Phi(t) arriba y -dPhi/dt abajo, alineadas en el tiempo."""

    def __init__(self, cajas, curva_flujo, curva_fem, ts, flujo, fem,
                 geometria, **kwargs):
        super().__init__(cajas, curva_flujo, curva_fem, **kwargs)
        self.cajas = cajas
        self.curva_flujo = curva_flujo
        self.curva_fem = curva_fem
        self._ts = ts
        self._flujo = flujo
        self._fem = fem
        self._geo = geometria
        self._anclar()

    def fem(self, t):
        """La fem en t — derivada numerica del MISMO flujo dibujado."""
        return float(np.interp(float(t), self._ts, self._fem))

    def _punto(self, caja, t, ys):
        x0, y0, ancho, alto, v0, v1 = self._geo[caja]
        fx = (float(t) - self._ts[0]) / (self._ts[-1] - self._ts[0])
        v = float(np.interp(float(t), self._ts, ys))
        fy = (v - v0) / max(v1 - v0, _EPS)
        return self._desde(x0 + fx * ancho, y0 + fy * alto)

    def punto_flujo(self, t):
        return self._punto(0, t, self._flujo)

    def punto_fem(self, t):
        return self._punto(1, t, self._fem)


def curvas_flujo_fem(velocidad=1.6, ancho=5.6, alto_caja=1.35, hueco=0.55,
                     color_flujo=COLOR_B, color_fem=COLOR_CALCULO,
                     muestras=180):
    """El iman pasa a velocidad constante; arriba el flujo, abajo la fem.

    La fem NO se dibuja de una formula aparte: es la derivada numerica
    (con signo menos) del flujo de arriba. Que el pico de fem caiga donde
    el flujo tiene la pendiente maxima —y que la fem sea CERO justo cuando
    el flujo es maximo— sale de derivar, que es el mensaje del clip.
    """
    muestras = _validar_muestras("curvas_flujo_fem", muestras)
    ts = np.linspace(-2.2, 2.2, muestras)
    flujo = _flujo_iman(velocidad * ts)
    fem = -np.gradient(flujo, ts)

    cajas = VGroup()
    geometria = []
    curvas = []
    for k, (ys, color) in enumerate(((flujo, color_flujo),
                                     (fem, color_fem))):
        y_base = hueco / 2 + alto_caja if k == 0 else -hueco / 2
        caja, origen = _ejes_xy(ancho, alto_caja, COLOR_EJE)
        caja.shift((0, y_base - alto_caja / 2, 0))
        origen = origen + np.array([0, y_base - alto_caja / 2, 0.0])
        v0, v1 = float(ys.min()), float(ys.max())
        margen = 0.08 * max(v1 - v0, _EPS)
        v0, v1 = v0 - margen, v1 + margen
        fx = (ts - ts[0]) / (ts[-1] - ts[0])
        fy = (ys - v0) / (v1 - v0)
        pts = origen + np.column_stack([fx * ancho, fy * alto_caja,
                                        np.zeros(len(ts))])
        curvas.append(_curva(pts, color, grosor=2.8))
        cajas.add(caja)
        geometria.append((float(origen[0]), float(origen[1]), ancho,
                          alto_caja, v0, v1))
    pieza = CurvasFlujoFem(cajas, curvas[0], curvas[1], ts, flujo, fem,
                           geometria)
    return pieza


class Alternador(_Anclada):
    """La espira que gira en el campo y escribe la primera senoide."""

    def __init__(self, campo, espira, eje_giro, caja, n, b, area, omega,
                 ancho_caja, alto_caja, origen_caja, **kwargs):
        super().__init__(campo, eje_giro, espira, caja, **kwargs)
        self.campo = campo
        self.espira = espira
        self.eje_giro = eje_giro
        self.caja = caja
        self._n, self._b, self._area, self._omega = n, b, area, omega
        self._wc, self._hc = ancho_caja, alto_caja
        self._oc = origen_caja
        self._anclar()

    def fem_pico(self):
        """El pico N B A omega en voltios — el numero que rotula el clip."""
        return fem_espira(self._n, self._b, self._area, self._omega)

    def espira_a(self, angulo_deg):
        """La espira vista de canto, girada a ese angulo (para un
        ReplacementTransform del clip)."""
        a = np.radians(float(angulo_deg))
        centro = self.eje_giro.get_center()
        medio = 0.95 * np.array([np.cos(a), 0.35 * np.sin(a), 0.0])
        linea = Line(centro - medio, centro + medio, stroke_width=4.0,
                     color=COLOR_CARGA)
        extremo_a = Dot(centro - medio, radius=0.06, color=COLOR_CARGA)
        extremo_b = Dot(centro + medio, radius=0.06, color=COLOR_CARGA)
        return VGroup(linea, extremo_a, extremo_b)

    def senoide_hasta(self, angulo_deg, color=COLOR_CALCULO, muestras=140):
        """La senoide escrita desde 0 hasta ese angulo, dentro de la caja."""
        muestras = _validar_muestras("alternador.senoide_hasta", muestras)
        a1 = np.radians(float(angulo_deg))
        if a1 <= 0:
            raise ValueError("senoide_hasta: angulo positivo")
        angulos = np.linspace(0.0, a1, muestras)
        tope = np.radians(720.0)
        fx = angulos / tope
        fy = 0.5 + 0.42 * np.sin(angulos)
        base = self._oc + (self.get_center() - self._centro_original)
        pts = base + np.column_stack([fx * self._wc, fy * self._hc,
                                      np.zeros(muestras)])
        return _curva(pts, color, grosor=2.8)

    def punto_senoide(self, angulo_deg):
        a = np.radians(float(angulo_deg))
        base = self._oc + (self.get_center() - self._centro_original)
        return base + np.array([a / np.radians(720.0) * self._wc,
                                (0.5 + 0.42 * np.sin(a)) * self._hc, 0.0])


def alternador(n=100, b=0.1, area=0.01, hz=50.0, color_b=COLOR_B):
    """La espira de canto entre polos, y la caja donde se escribe la fem.

    Con los numeros por defecto (100 vueltas, 0.1 T, 100 cm^2, 50 Hz) el
    pico es 31.4 V. La senoide de la caja cubre dos vueltas completas.
    """
    omega = 2.0 * np.pi * float(hz)
    campo = VGroup()
    for y in np.linspace(-0.85, 0.85, 4):
        campo.add(Arrow((-1.55, y, 0), (1.55, y, 0), buff=0, color=color_b,
                        stroke_width=2.2, stroke_opacity=0.55,
                        tip_length=0.12))
    eje_giro = Dot(ORIGIN, radius=0.055, color=CODE_MUTED)
    espira = VGroup(Line((-0.95, 0, 0), (0.95, 0, 0), stroke_width=4.0,
                         color=COLOR_CARGA),
                    Dot((-0.95, 0, 0), radius=0.06, color=COLOR_CARGA),
                    Dot((0.95, 0, 0), radius=0.06, color=COLOR_CARGA))
    grupo_izq = VGroup(campo, espira, eje_giro)
    grupo_izq.shift(LEFT * 3.1)

    ancho_caja, alto_caja = 4.1, 2.1
    caja, origen = _ejes_xy(ancho_caja, alto_caja, COLOR_EJE)
    caja.shift(RIGHT * 1.9)
    origen = origen + np.array([1.9, 0.0, 0.0])
    return Alternador(campo, espira, eje_giro, caja, n, b, area, omega,
                      ancho_caja, alto_caja, origen)


class Transformador(_Anclada):
    """Dos devanados sobre el mismo nucleo: la palanca de la tension."""

    def __init__(self, nucleo, primario, secundario, n1, n2, **kwargs):
        super().__init__(nucleo, primario, secundario, **kwargs)
        self.nucleo = nucleo
        self.primario = primario
        self.secundario = secundario
        self._n1, self._n2 = int(n1), int(n2)
        self._anclar()

    def relacion(self):
        """V2/V1 = N2/N1 — la unica cuenta del transformador ideal."""
        return self._n2 / self._n1


def transformador(n1=4, n2=8, color_primario=COLOR_CARGA,
                  color_secundario=COLOR_CALCULO):
    """El nucleo en anillo y los dos devanados, con sus espiras CONTADAS:
    las que se dibujan son las que dividen (aqui 4:8 = subir al doble)."""
    if not 1 <= int(n1) <= 12 or not 1 <= int(n2) <= 12:
        raise ValueError("transformador: espiras fuera de 1..12")
    nucleo = VGroup(
        Rectangle(width=3.4, height=2.4, stroke_width=14.0,
                  color="#233240"),
        Rectangle(width=3.4, height=2.4, stroke_width=2.0,
                  color=CODE_MUTED))
    primario, secundario = VGroup(), VGroup()
    for lado, n_esp, color, destino in ((-1.7, n1, color_primario,
                                         primario),
                                        (1.7, n2, color_secundario,
                                         secundario)):
        ys = np.linspace(-0.75, 0.75, int(n_esp))
        for y in ys:
            espira = Circle(radius=0.19, color=color, stroke_width=2.6)
            espira.stretch(2.1, 0)
            espira.move_to((lado, y, 0))
            destino.add(espira)
    return Transformador(nucleo, primario, secundario, n1, n2)


class CajaGauss(_Anclada):
    """El flujo por una superficie cerrada: con carga sale neto; con un
    iman, todo lo que entra vuelve a salir."""

    def __init__(self, fuente, superficie, flechas, tipo, **kwargs):
        super().__init__(fuente, flechas, superficie, **kwargs)
        self.fuente = fuente
        self.superficie = superficie
        self.flechas = flechas
        self.tipo = tipo
        self._anclar()


def caja_gauss(tipo="electrica", radio_superficie=1.55,
               color_e=COLOR_E, color_b=COLOR_B):
    """La superficie cerrada (a trazos, cian tenue) y lo que la cruza.

    `tipo='electrica'`: una carga dentro y flechas radiales — todas
    SALEN: flujo neto. `tipo='magnetica'`: un iman dentro y sus lineas
    CERRADAS — cada linea que sale vuelve a entrar: flujo neto cero. El
    par de dibujos ES la pareja de leyes de Gauss.
    """
    superficie = DashedVMobject(
        Circle(radius=radio_superficie, color=COLOR_CALCULO,
               stroke_width=2.0), num_dashes=36)
    if tipo == "electrica":
        fuente = carga(signo=+1)
        flechas = VGroup()
        for k in range(10):
            ang = 2.0 * np.pi * k / 10 + 0.05
            d = np.array([np.cos(ang), np.sin(ang), 0.0])
            flechas.add(Arrow(0.45 * d, (radio_superficie + 0.55) * d,
                              buff=0, color=color_e, stroke_width=2.6,
                              tip_length=0.14))
        return CajaGauss(fuente, superficie, flechas, tipo)
    if tipo == "magnetica":
        iman = VGroup(
            Rectangle(width=0.9, height=0.34, stroke_width=1.6,
                      color=color_b, fill_color="#0c2b22",
                      fill_opacity=1.0),
            Line((0, -0.17, 0), (0, 0.17, 0), stroke_width=1.2,
                 color=color_b))
        lineas = VGroup()
        for l_re in (1.4, 2.2, 3.2):
            t0 = np.arcsin(np.sqrt(1.0 / l_re))
            ts = np.linspace(t0, np.pi - t0, 90)
            rs = l_re * np.sin(ts) ** 2 * 0.42
            for lado in (+1, -1):
                xs = lado * rs * np.sin(ts)
                ys = rs * np.cos(ts)
                lineas.add(_curva(np.column_stack([ys, xs]), color_b,
                                  grosor=1.8))
        return CajaGauss(iman, superficie, lineas, tipo)
    raise ValueError("caja_gauss: tipo 'electrica' o 'magnetica'")


class CondensadorAmpere(_Anclada):
    """El hueco que rompia a Ampere y el termino que lo arregla."""

    def __init__(self, cables, placas, lazo, flechas_i, flechas_e,
                 **kwargs):
        super().__init__(cables, placas, lazo, flechas_i, flechas_e,
                         **kwargs)
        self.cables = cables
        self.placas = placas
        self.lazo = lazo
        self.flechas_i = flechas_i
        self.flechas_e = flechas_e
        self._anclar()

    def e_a(self, fraccion, color=COLOR_E):
        """Las flechas de E entre placas a esa fraccion de carga (0-1),
        para un ReplacementTransform mientras el condensador se carga."""
        f = float(np.clip(fraccion, 0.05, 1.0))
        flechas = VGroup()
        for y in np.linspace(-0.62, 0.62, 4):
            flechas.add(Arrow((-0.34, y, 0), (0.34, y, 0), buff=0,
                              color=color, stroke_width=3.2 * f,
                              stroke_opacity=0.35 + 0.65 * f,
                              tip_length=0.13))
        flechas.move_to(self.placas.get_center())
        return flechas


def condensador_ampere(color_i=COLOR_CARGA, color_e=COLOR_E):
    """Cable - placa | placa - cable, el lazo de Ampere a caballo del
    hueco y la corriente que "sigue" por el como campo que crece."""
    cables = VGroup(
        Line((-3.3, 0, 0), (-0.55, 0, 0), stroke_width=3.4,
             color=CODE_MUTED),
        Line((0.55, 0, 0), (3.3, 0, 0), stroke_width=3.4,
             color=CODE_MUTED))
    placas = VGroup(
        Line((-0.45, -0.85, 0), (-0.45, 0.85, 0), stroke_width=5.0,
             color=CODE_MUTED),
        Line((0.45, -0.85, 0), (0.45, 0.85, 0), stroke_width=5.0,
             color=CODE_MUTED))
    lazo = DashedVMobject(Circle(radius=0.95, color=COLOR_B,
                                 stroke_width=2.2).stretch(1.35, 1),
                          num_dashes=30)
    lazo.move_to((0, 0, 0))
    flechas_i = VGroup(
        Arrow((-2.7, 0, 0), (-1.6, 0, 0), buff=0, color=color_i,
              stroke_width=3.4, tip_length=0.16),
        Arrow((1.6, 0, 0), (2.7, 0, 0), buff=0, color=color_i,
              stroke_width=3.4, tip_length=0.16))
    flechas_e = VGroup()
    for y in np.linspace(-0.62, 0.62, 4):
        flechas_e.add(Arrow((-0.34, y, 0), (0.34, y, 0), buff=0,
                            color=color_e, stroke_width=1.6,
                            stroke_opacity=0.5, tip_length=0.13))
    return CondensadorAmpere(cables, placas, lazo, flechas_i, flechas_e)


class OndaEm(_Anclada):
    """E (ambar) y B (verde) perpendiculares entre si y a la marcha."""

    def __init__(self, eje, flechas_e, flechas_b, env_e, env_b, flecha_k,
                 fase, largo, amplitud, n_ondas, dz, **kwargs):
        super().__init__(eje, env_e, env_b, flechas_e, flechas_b, flecha_k,
                         **kwargs)
        self.eje = eje
        self.flechas_e = flechas_e
        self.flechas_b = flechas_b
        self.env_e = env_e
        self.env_b = env_b
        self.flecha_k = flecha_k
        self._fase = float(fase)
        self._largo = largo
        self._amplitud = amplitud
        self._n_ondas = n_ondas
        self._dz = dz
        self._anclar()

    def lambda_escena(self):
        """La longitud de onda en unidades de escena (para acotarla)."""
        return self._largo / self._n_ondas

    def punto_cresta(self, k_cresta=0):
        """Punto de escena de la cresta k del campo E (para la llave de
        lambda: de cresta a cresta hay exactamente lambda_escena)."""
        x0 = (-self._largo / 2
              + (np.pi / 2 - self._fase + 2 * np.pi * k_cresta)
              / (2 * np.pi * self._n_ondas) * self._largo)
        return self._desde(x0, self._amplitud)

    def con_fase(self, fase):
        """Una onda igual con otra fase (ReplacementTransform y a andar).

        El desplazamiento entre fases es lo que anima la marcha: fase
        creciente = la onda avanza hacia la derecha.
        """
        nueva = onda_em(fase=fase, largo=self._largo,
                        amplitud=self._amplitud, n_ondas=self._n_ondas)
        nueva.move_to(self.get_center())
        return nueva


def onda_em(fase=0.0, largo=6.4, amplitud=1.15, n_ondas=2.5, n_flechas=15,
            color_e=COLOR_E, color_b=COLOR_B, color_k=COLOR_ONDA,
            muestras=160):
    """La onda plana en axonometrica de andar por casa.

    E oscila en vertical (ambar); B en el plano "que entra en el papel",
    dibujado como una diagonal corta (verde); la marcha es el eje x. Los
    tres son mutuamente perpendiculares y van EN FASE — en la onda plana
    E y B cruzan por cero juntos, error clasico de los dibujos malos.
    """
    muestras = _validar_muestras("onda_em", muestras)
    if not 2 <= int(n_flechas) <= 24:
        raise ValueError("onda_em: n_flechas fuera de 2..24")
    dz = np.array([-0.40, -0.27, 0.0])   # el "eje z" axonometrico
    k_onda = 2.0 * np.pi * n_ondas / largo

    eje = Line((-largo / 2 - 0.25, 0, 0), (largo / 2 + 0.25, 0, 0),
               stroke_width=1.6, color=COLOR_EJE)
    xs = np.linspace(-largo / 2, largo / 2, muestras)
    s = np.sin(k_onda * (xs + largo / 2) + float(fase))

    env_e = _curva(np.column_stack([xs, amplitud * s]), color_e,
                   grosor=2.6)
    pts_b = (np.column_stack([xs, np.zeros_like(xs)])
             + np.outer(amplitud * 0.85 * s, dz[:2]))
    env_b = _curva(pts_b, color_b, grosor=2.6)

    flechas_e, flechas_b = VGroup(), VGroup()
    for x in np.linspace(-largo / 2, largo / 2, int(n_flechas)):
        v = float(np.sin(k_onda * (x + largo / 2) + float(fase)))
        if abs(v) < 0.06:
            continue
        flechas_e.add(Arrow((x, 0, 0), (x, amplitud * v, 0), buff=0,
                            color=color_e, stroke_width=2.4,
                            tip_length=0.11))
        flechas_b.add(Arrow((x, 0, 0),
                            (x + dz[0] * amplitud * 0.85 * v,
                             dz[1] * amplitud * 0.85 * v, 0), buff=0,
                            color=color_b, stroke_width=2.4,
                            tip_length=0.11))
    flecha_k = Arrow((largo / 2 + 0.3, 0, 0), (largo / 2 + 1.35, 0, 0),
                     buff=0, color=color_k, stroke_width=4.0,
                     tip_length=0.2)
    return OndaEm(eje, flechas_e, flechas_b, env_e, env_b, flecha_k, fase,
                  largo, amplitud, n_ondas, dz)


class EsferaReparto(_Anclada):
    """La potencia del emisor repartiendose sobre frentes esfericos."""

    def __init__(self, emisor, frentes, radios, **kwargs):
        super().__init__(frentes, emisor, **kwargs)
        self.emisor = emisor
        self.frentes = frentes
        self._radios = radios
        self._anclar()

    def frente(self, i):
        return self.frentes[i]

    def flujo_relativo(self, i):
        """Flujo en el frente i relativo al primero: (r0/ri)^2."""
        return float((self._radios[0] / self._radios[i]) ** 2)

    def parche(self, i, angulo_deg=0.0, ancho_deg=None, color=COLOR_CALCULO):
        """Un parche de AREA FIJA sobre el frente i: mismo trozo de
        antena, cada vez menos angulo del total — el 1/r^2 hecho dibujo.
        Si no se da `ancho_deg`, se calcula para que el arco mida lo mismo
        que en el primer frente."""
        r = self._radios[i]
        if ancho_deg is None:
            ancho_deg = 26.0 * self._radios[0] / r
        a0 = np.radians(float(angulo_deg) - float(ancho_deg) / 2)
        arco = Arc(radius=r, start_angle=a0,
                   angle=np.radians(float(ancho_deg)), color=color,
                   stroke_width=5.0)
        arco.move_arc_center_to(self.emisor.get_center())
        return arco


def esfera_reparto(radios=(0.9, 1.7, 2.5, 3.3), color_frente=COLOR_ONDA,
                   color_emisor=COLOR_CARGA):
    """El emisor y sus frentes: misma potencia, esfera cada vez mayor.

    El grosor y la opacidad de cada frente caen como 1/r^2 DE VERDAD
    (relativos al primero): el dibujo ya es la ley que el clip enuncia.
    """
    if not 2 <= len(radios) <= 8:
        raise ValueError("esfera_reparto: 2..8 frentes")
    emisor = Dot(ORIGIN, radius=0.11, color=color_emisor)
    frentes = VGroup()
    for r in radios:
        rel = (radios[0] / r) ** 2
        frentes.add(Circle(radius=r, color=color_frente,
                           stroke_width=1.6 + 3.2 * rel,
                           stroke_opacity=0.30 + 0.70 * rel))
    return EsferaReparto(emisor, frentes, list(radios))


class TrazaPolarizacion(_Anclada):
    """El plano transversal: hacia donde apunta E mientras la onda llega."""

    def __init__(self, ejes, traza, vector, tipo, amplitud, fase,
                 **kwargs):
        super().__init__(ejes, traza, vector, **kwargs)
        self.ejes = ejes
        self.traza = traza
        self.vector = vector
        self.tipo = tipo
        self._amplitud = amplitud
        self._fase = float(fase)
        self._anclar()

    def _punta(self, fase):
        a = self._amplitud
        if self.tipo == "v":
            return np.array([0.0, a * np.sin(fase)])
        if self.tipo == "h":
            return np.array([a * np.sin(fase), 0.0])
        if self.tipo == "d":
            return np.array([a * 0.7071 * np.sin(fase),
                             a * 0.7071 * np.sin(fase)])
        return np.array([a * np.cos(fase), a * np.sin(fase)])

    def con_fase(self, fase):
        """La misma traza con el vector en otra fase, para animar la
        rotacion (circular) o el vaiven (lineal) por Transform."""
        nueva = traza_polarizacion(tipo=self.tipo, amplitud=self._amplitud,
                                   fase=fase)
        nueva.move_to(self.get_center())
        return nueva


def traza_polarizacion(tipo="v", amplitud=1.25, fase=0.9,
                       color_traza=COLOR_ONDA, color_vector=COLOR_E):
    """El vector E visto de frente y la figura que pinta en un periodo.

    `tipo`: 'v' y 'h' lineales, 'd' diagonal, 'circular'. Lineal pinta un
    segmento; circular, un circulo — las dos monedas con las que un
    satelite emite dos programas en la MISMA frecuencia.
    """
    if tipo not in ("v", "h", "d", "circular"):
        raise ValueError("traza_polarizacion: tipo v/h/d/circular")
    ejes = VGroup(Line((-1.6, 0, 0), (1.6, 0, 0), stroke_width=1.4,
                       color=COLOR_EJE),
                  Line((0, -1.6, 0), (0, 1.6, 0), stroke_width=1.4,
                       color=COLOR_EJE))
    if tipo == "circular":
        traza = Circle(radius=amplitud, color=color_traza, stroke_width=2.4)
    elif tipo == "v":
        traza = Line((0, -amplitud, 0), (0, amplitud, 0),
                     stroke_width=2.4, color=color_traza)
    elif tipo == "h":
        traza = Line((-amplitud, 0, 0), (amplitud, 0, 0),
                     stroke_width=2.4, color=color_traza)
    else:
        a = amplitud * 0.7071
        traza = Line((-a, -a, 0), (a, a, 0), stroke_width=2.4,
                     color=color_traza)
    pieza = TrazaPolarizacion(ejes, traza, VGroup(), tipo, amplitud, fase)
    punta = pieza._punta(float(fase))
    if np.hypot(*punta) > 0.05:
        vector = Arrow((0, 0, 0), (punta[0], punta[1], 0), buff=0,
                       color=color_vector, stroke_width=3.6,
                       tip_length=0.17)
        pieza.vector.add(vector)
        pieza.add(vector)
    return pieza


class BandaEspectroEm(_Anclada):
    """El eje logaritmico de las bandas, de la onda corta a la Ka."""

    def __init__(self, eje, zonas, nombres_mob, marcas, nombres, f0, f1,
                 ancho, alto, **kwargs):
        super().__init__(eje, zonas, nombres_mob, marcas, **kwargs)
        self.eje = eje
        self.zonas = zonas
        self.nombres = nombres_mob
        self.marcas = marcas
        self._nombres = nombres
        self._lf0, self._lf1 = np.log10(f0), np.log10(f1)
        self._ancho, self._alto = ancho, alto
        self._anclar()

    def punto_de(self, f, altura=0.0):
        """Punto de escena de esa frecuencia sobre la banda."""
        fx = (np.log10(float(f)) - self._lf0) / (self._lf1 - self._lf0)
        fx = float(np.clip(fx, 0.0, 1.0))
        return self._desde((fx - 0.5) * self._ancho, float(altura))

    def zona(self, nombre):
        return self.zonas[self._nombres.index(nombre)]

    def lambda_texto(self, f):
        """La longitud de onda de esa frecuencia, formateada (m/cm/mm)."""
        lam = lambda_de(f)
        if lam >= 1.0:
            return f"{lam:.0f} m" if lam >= 10 else f"{lam:.1f} m"
        if lam >= 0.1:
            return f"{lam * 100:.0f} cm"
        return f"{lam * 1000:.0f} mm"


def banda_espectro_em(f0=3e6, f1=40e9, ancho=11.4, alto=0.95,
                      color_zona=COLOR_ONDA, solo=None):
    """La regla logaritmica de bandas HF..Ka con sus fronteras reales.

    `solo` restringe a un subconjunto de nombres (p. ej. las satelitales
    L..Ka). Las zonas alternan opacidad para que las fronteras se lean;
    los nombres van dentro y las decadas (10 MHz, 1 GHz...) debajo.
    """
    usadas = [b for b in BANDAS
              if b[1] < f1 and b[2] > f0
              and (solo is None or b[0] in solo)]
    if not usadas:
        raise ValueError("banda_espectro_em: ninguna banda en ese rango")
    lf0, lf1 = np.log10(f0), np.log10(f1)

    eje = Line((-ancho / 2, -alto / 2 - 0.06, 0),
               (ancho / 2, -alto / 2 - 0.06, 0), stroke_width=2.0,
               color=COLOR_EJE)
    zonas, nombres_mob = VGroup(), VGroup()
    nombres = []
    for k, (nombre, b0, b1, _) in enumerate(usadas):
        x0 = (np.log10(max(b0, f0)) - lf0) / (lf1 - lf0) - 0.5
        x1 = (np.log10(min(b1, f1)) - lf0) / (lf1 - lf0) - 0.5
        zona = Rectangle(width=(x1 - x0) * ancho, height=alto,
                         stroke_width=1.0, color=color_zona,
                         fill_color=color_zona,
                         fill_opacity=0.10 + 0.08 * (k % 2))
        zona.move_to(((x0 + x1) / 2 * ancho, 0, 0))
        zonas.add(zona)
        tag = _texto_hud(nombre, font_size=14, color=CODE_MUTED)
        if tag.width > (x1 - x0) * ancho - 0.06:
            tag.scale_to_fit_width(max((x1 - x0) * ancho - 0.06, 0.12))
        tag.move_to(((x0 + x1) / 2 * ancho, 0, 0))
        nombres_mob.add(tag)
        nombres.append(nombre)

    marcas = VGroup()
    decada = 7
    while 10.0 ** decada <= f1:
        f = 10.0 ** decada
        if f >= f0:
            fx = (decada - lf0) / (lf1 - lf0) - 0.5
            texto = ("10 MHz" if decada == 7 else
                     "100 MHz" if decada == 8 else
                     "1 GHz" if decada == 9 else "10 GHz")
            raya = Line((fx * ancho, -alto / 2 - 0.06, 0),
                        (fx * ancho, -alto / 2 - 0.18, 0),
                        stroke_width=1.6, color=COLOR_EJE)
            tag = _texto_hud(texto, font_size=12, color=COLOR_EJE)
            tag.next_to(raya, DOWN, buff=0.07)
            marcas.add(VGroup(raya, tag))
        decada += 1
    return BandaEspectroEm(eje, zonas, nombres_mob, marcas, nombres, f0,
                           f1, ancho, alto)


# =====================================================================
# Piezas — modulo 3: guiar y soltar la onda
# =====================================================================
class CableOnda(_Anclada):
    """Un cable con la señal que lleva dentro, dibujada a su lambda."""

    def __init__(self, cable, extremos, onda, largo, lam, **kwargs):
        super().__init__(cable, extremos, onda, **kwargs)
        self.cable = cable
        self.extremos = extremos
        self.onda = onda
        self._largo = largo
        self._lam = lam
        self._anclar()

    def ondas_dentro(self):
        """Cuantas longitudes de onda caben en el cable dibujado."""
        return self._largo / self._lam

    def con_lambda(self, lam):
        """El mismo cable con otra señal (ReplacementTransform)."""
        nueva = cable_onda(largo=self._largo, lam=lam)
        nueva.move_to(self.get_center())
        return nueva


def cable_onda(largo=6.0, lam=12.0, amplitud=0.5, color_onda=COLOR_ONDA,
               muestras=200):
    """El cable del clip 3.1.1: a 50 Hz la 'onda' es una recta (lambda de
    6000 km); a 1 GHz caben varias enteras y el cable ya es un circuito
    distribuido. `ondas_dentro()` da el numero que decide la regla
    lambda/10."""
    muestras = _validar_muestras("cable_onda", muestras)
    if float(lam) <= 0:
        raise ValueError("cable_onda: lam positiva")
    cable = VGroup(
        Line((-largo / 2, 0.16, 0), (largo / 2, 0.16, 0),
             stroke_width=2.4, color=CODE_MUTED),
        Line((-largo / 2, -0.16, 0), (largo / 2, -0.16, 0),
             stroke_width=2.4, color=CODE_MUTED))
    extremos = VGroup(
        Rectangle(width=0.28, height=0.62, stroke_width=2.0,
                  color=CODE_MUTED).move_to((-largo / 2 - 0.14, 0, 0)),
        Rectangle(width=0.28, height=0.62, stroke_width=2.0,
                  color=CODE_MUTED).move_to((largo / 2 + 0.14, 0, 0)))
    xs = np.linspace(-largo / 2, largo / 2, muestras)
    ys = amplitud * np.sin(2.0 * np.pi * (xs + largo / 2) / float(lam))
    onda = _curva(np.column_stack([xs, ys]), color_onda, grosor=2.8)
    return CableOnda(cable, extremos, onda, largo, float(lam))


class LineaLC(_Anclada):
    """La escalera del telegrafista: L en serie, C a tierra, celda a celda."""

    def __init__(self, rail, celdas, tierra, largo, n, **kwargs):
        super().__init__(rail, celdas, tierra, **kwargs)
        self.rail = rail
        self.celdas = celdas
        self.tierra = tierra
        self._largo = largo
        self._n = n
        self._anclar()

    def celda(self, i):
        return self.celdas[i]

    def punto_celda(self, i):
        """El nudo superior de la celda i (donde el clip pone el pulso)."""
        x = -self._largo / 2 + (i + 0.5) * self._largo / self._n
        return self._desde(x, 0.55)


def linea_lc(n_celdas=6, largo=6.2, color_l=COLOR_B, color_c=COLOR_E):
    """Bobinas en el rail de arriba (verde: guardan corriente) y
    condensadores al de abajo (ambar: guardan tension). Z0 = sqrt(L/C)
    es el precio de avanzar una celda; el numero sale de `z0_coaxial` o
    se rotula desde el style_block."""
    if not 3 <= int(n_celdas) <= 10:
        raise ValueError("linea_lc: n_celdas fuera de 3..10")
    n = int(n_celdas)
    paso = largo / n
    rail = VGroup(Line((-largo / 2, -0.75, 0), (largo / 2, -0.75, 0),
                       stroke_width=2.4, color=CODE_MUTED))
    celdas = VGroup()
    for i in range(n):
        x0 = -largo / 2 + i * paso
        celda = VGroup()
        # la bobina: cuatro arcos sobre el rail superior
        for k in range(4):
            arco = Arc(radius=paso * 0.09, start_angle=np.pi, angle=-np.pi,
                       color=color_l, stroke_width=2.6)
            arco.move_arc_center_to((x0 + paso * (0.2 + 0.18 * k),
                                     0.55, 0))
            celda.add(arco)
        celda.add(Line((x0, 0.55, 0), (x0 + paso * 0.11, 0.55, 0),
                       stroke_width=2.4, color=CODE_MUTED))
        celda.add(Line((x0 + paso * 0.83, 0.55, 0), (x0 + paso, 0.55, 0),
                       stroke_width=2.4, color=CODE_MUTED))
        # el condensador: dos placas hacia el rail de abajo
        xc = x0 + paso * 0.92
        celda.add(Line((xc, 0.55, 0), (xc, 0.02, 0), stroke_width=2.2,
                       color=CODE_MUTED))
        celda.add(Line((xc - 0.16, 0.02, 0), (xc + 0.16, 0.02, 0),
                       stroke_width=3.0, color=color_c))
        celda.add(Line((xc - 0.16, -0.12, 0), (xc + 0.16, -0.12, 0),
                       stroke_width=3.0, color=color_c))
        celda.add(Line((xc, -0.12, 0), (xc, -0.75, 0), stroke_width=2.2,
                       color=CODE_MUTED))
        celdas.add(celda)
    tierra = VGroup()
    return LineaLC(rail, celdas, tierra, largo, n)


class CorteLinea(_Anclada):
    """Seccion transversal de una linea (coaxial o microstrip) con su
    campo dentro: E radial/vertical en ambar, B circular en verde."""

    def __init__(self, conductores, dielectrico, flechas_e, lineas_b, z0,
                 **kwargs):
        super().__init__(dielectrico, conductores, flechas_e, lineas_b,
                         **kwargs)
        self.conductores = conductores
        self.dielectrico = dielectrico
        self.flechas_e = flechas_e
        self.lineas_b = lineas_b
        self._z0 = z0
        self._anclar()

    def z0(self):
        """La impedancia de ESTA geometria (misma cuenta que el rotulo)."""
        return self._z0


def corte_coaxial(d_sobre_d=6.52, er=2.25, radio_ext=1.45,
                  color_e=COLOR_E, color_b=COLOR_B):
    """El coaxial cortado: vivo al centro, malla fuera, E radial y B en
    circulos. El D/d por defecto es el que da 75 ohm con polietileno —
    `z0()` lo confirma con la misma formula del clip."""
    r_int = radio_ext / float(d_sobre_d)
    conductores = VGroup(
        Circle(radius=radio_ext, color=CODE_MUTED, stroke_width=3.4),
        Dot(ORIGIN, radius=max(r_int, 0.07), color=COLOR_CARGA))
    dielectrico = Circle(radius=radio_ext, stroke_width=0,
                         fill_color="#101826", fill_opacity=1.0)
    flechas_e = VGroup()
    for k in range(8):
        ang = 2.0 * np.pi * k / 8 + 0.2
        d = np.array([np.cos(ang), np.sin(ang), 0.0])
        flechas_e.add(Arrow((max(r_int, 0.07) + 0.10) * d,
                            (radio_ext - 0.12) * d, buff=0, color=color_e,
                            stroke_width=2.2, tip_length=0.12))
    lineas_b = VGroup()
    for r in (0.5, 0.95):
        lineas_b.add(DashedVMobject(
            Circle(radius=r * radio_ext, color=color_b, stroke_width=1.8),
            num_dashes=24))
    return CorteLinea(conductores, dielectrico, flechas_e, lineas_b,
                      z0_coaxial(d_sobre_d, er))


def corte_microstrip(z0_ohm=50.0, color_e=COLOR_E, color_b=COLOR_B):
    """La microstrip del LNB: pista arriba, plano de masa abajo, el campo
    apretado en el sustrato (y un poco por el aire, que para el clip es
    el matiz de que er efectiva < er)."""
    sustrato = Rectangle(width=4.2, height=0.55, stroke_width=1.4,
                         color=CODE_MUTED, fill_color="#101826",
                         fill_opacity=1.0)
    sustrato.move_to((0, -0.275, 0))
    conductores = VGroup(
        Line((-2.1, -0.55, 0), (2.1, -0.55, 0), stroke_width=5.0,
             color=CODE_MUTED),
        Rectangle(width=0.85, height=0.10, stroke_width=1.2,
                  color=COLOR_CARGA, fill_color=COLOR_CARGA,
                  fill_opacity=0.9).move_to((0, 0.05, 0)))
    flechas_e = VGroup()
    for x in np.linspace(-0.30, 0.30, 3):
        flechas_e.add(Arrow((x, -0.02, 0), (x, -0.50, 0), buff=0,
                            color=color_e, stroke_width=2.2,
                            tip_length=0.11))
    for s in (-1, 1):
        arco = Arc(radius=0.42, start_angle=np.pi / 2,
                   angle=s * np.pi * 0.42, color=color_e,
                   stroke_width=1.8)
        arco.move_arc_center_to((s * 0.5, -0.05, 0))
        flechas_e.add(arco)
    lineas_b = VGroup(DashedVMobject(
        Circle(radius=0.55, color=color_b,
               stroke_width=1.8).stretch(0.6, 1).move_to((0, -0.1, 0)),
        num_dashes=20))
    return CorteLinea(conductores, sustrato, flechas_e, lineas_b,
                      float(z0_ohm))


class OndaEstacionaria(_Cartesiano):
    """Incidente + reflejada: la envolvente que no viaja y su SWR."""

    def __init__(self, ejes, onda, envolventes, gamma, fase, largo, alto,
                 origen, n_ondas, **kwargs):
        super().__init__(ejes, envolventes, onda, **kwargs)
        self.ejes = ejes
        self.onda = onda
        self.envolventes = envolventes
        self._gamma = float(gamma)
        self._fase = float(fase)
        self._n_ondas = n_ondas
        self._calibrar((0.0, 1.0), (-1.0, 1.0), largo, alto, origen)

    def swr(self):
        """El SWR de la envolvente dibujada, de `swr_de`."""
        return swr_de(self._gamma)

    def punto_maximo(self):
        """El primer maximo de la envolvente (desde la carga)."""
        return self._en(1.0 - 0.25 / self._n_ondas, 1.0)

    def punto_minimo(self):
        return self._en(1.0 - 0.5 / self._n_ondas,
                        (1.0 - abs(self._gamma)) / (1.0 + abs(self._gamma)))

    def con_fase(self, fase):
        """La onda total en otro instante, envolvente quieta
        (ReplacementTransform del clip: la onda 'hierve' dentro)."""
        nueva = onda_estacionaria(gamma=self._gamma, fase=fase,
                                  n_ondas=self._n_ondas,
                                  ancho=self._ancho, alto=self._alto)
        nueva.move_to(self.get_center())
        return nueva


def onda_estacionaria(gamma=0.2, fase=0.0, n_ondas=2.0, ancho=6.4,
                      alto=2.4, color_onda=COLOR_ONDA,
                      color_env=COLOR_CALCULO, muestras=220):
    """La linea con carga al final (x = derecha): incidente + reflejada.

    onda(x, t) = sen(kx - wt) + gamma sen(kx + wt); la envolvente es
    sqrt(1 + g^2 + 2 g cos(2kx)) — maximos y minimos donde deben, y su
    razon ES el SWR. Con gamma = 0 la envolvente es plana: nada rebota.
    """
    muestras = _validar_muestras("onda_estacionaria", muestras)
    g = float(gamma)
    if not -1.0 <= g <= 1.0:
        raise ValueError("onda_estacionaria: gamma en [-1, 1]")
    ejes, origen = _ejes_xy(ancho, alto, COLOR_EJE)
    # el "eje" util es la linea media; la caja da el marco
    xs = np.linspace(0.0, 1.0, muestras)
    k = 2.0 * np.pi * n_ondas
    amplitud_max = 1.0 + abs(g)

    def _y(x, t):
        return (np.sin(k * x - t) + g * np.sin(k * x + t)) / amplitud_max

    ys = _y(xs, float(fase))
    medio = origen + np.array([0, alto / 2, 0.0])
    pts = medio + np.column_stack([xs * ancho, ys * alto / 2,
                                   np.zeros(muestras)])
    onda = _curva(pts, color_onda, grosor=2.6)

    env = np.sqrt(1.0 + g * g + 2.0 * g * np.cos(2.0 * k * xs))
    env = env / amplitud_max
    envolventes = VGroup()
    for s in (+1, -1):
        pts_e = medio + np.column_stack([xs * ancho, s * env * alto / 2,
                                         np.zeros(muestras)])
        envolventes.add(_curva(pts_e, color_env, grosor=2.0))
    return OndaEstacionaria(ejes, onda, envolventes, g, fase, ancho, alto,
                            origen, n_ondas)


class FronteraZ(_Anclada):
    """Dos medios y el reparto: incidente, reflejada, transmitida."""

    def __init__(self, medios, frontera, flechas, gamma, **kwargs):
        super().__init__(medios, frontera, flechas, **kwargs)
        self.medios = medios
        self.frontera = frontera
        self.flechas = flechas
        self._gamma = gamma
        self._anclar()

    def reflejada(self):
        """|gamma|^2: fraccion de POTENCIA que rebota."""
        return float(self._gamma ** 2)


def frontera_z(z1=50.0, z2=75.0, color_onda=COLOR_ONDA):
    """La frontera entre dos impedancias y sus tres flechas, con el
    grosor proporcional a la POTENCIA de cada una (la de reflejada es
    gamma^2: con 50 -> 75, un 4 % — se ve fina porque ES fina)."""
    g = gamma_de(z2, z1)
    medios = VGroup(
        Rectangle(width=3.4, height=2.5, stroke_width=0,
                  fill_color="#101826", fill_opacity=1.0).move_to(
                      (-1.7, 0, 0)),
        Rectangle(width=3.4, height=2.5, stroke_width=0,
                  fill_color="#16202e", fill_opacity=1.0).move_to(
                      (1.7, 0, 0)))
    frontera = Line((0, -1.25, 0), (0, 1.25, 0), stroke_width=3.0,
                    color=CODE_MUTED)
    p_refl = g * g
    p_trans = 1.0 - p_refl
    flechas = VGroup(
        Arrow((-2.9, 0.55, 0), (-0.25, 0.55, 0), buff=0, color=color_onda,
              stroke_width=5.0, tip_length=0.18),
        Arrow((-0.25, -0.55, 0), (-2.9, -0.55, 0), buff=0,
              color=COLOR_CARGA,
              stroke_width=max(5.0 * p_refl, 1.2),
              tip_length=max(0.18 * np.sqrt(p_refl) * 2.2, 0.09)),
        Arrow((0.25, 0.55, 0), (2.9, 0.55, 0), buff=0, color=color_onda,
              stroke_width=5.0 * p_trans, tip_length=0.18 * p_trans + 0.04))
    return FronteraZ(medios, frontera, flechas, g)


class LineaCuartos(_Anclada):
    """Tramos de linea en serie, cada uno con su impedancia rotulada."""

    def __init__(self, tramos, etiquetas, llaves, zs, **kwargs):
        super().__init__(tramos, etiquetas, llaves, **kwargs)
        self.tramos = tramos
        self.etiquetas = etiquetas
        self.llaves = llaves
        self._zs = zs
        self._anclar()

    def tramo(self, i):
        return self.tramos[i]

    def z_adaptadora(self):
        """La del tramo central: sqrt(Z1 Z2), la misma que rotula."""
        return z_cuarto(self._zs[0], self._zs[-1])


def linea_cuartos(z1=50.0, z2=75.0, largo_total=6.6, alto=0.62):
    """Fuente - tramo Z1 - tramo sqrt(Z1 Z2) - tramo Z2: el escalon
    partido en dos escalones que no reflejan (en la f de diseño)."""
    z_medio = z_cuarto(z1, z2)
    zs = (float(z1), z_medio, float(z2))
    anchos = (0.40, 0.20, 0.40)
    tramos, etiquetas = VGroup(), VGroup()
    x = -largo_total / 2
    for z, frac in zip(zs, anchos):
        w = largo_total * frac
        alto_tramo = alto * (0.65 + 0.7 * (z / max(zs)))
        tramo = Rectangle(width=w, height=alto_tramo, stroke_width=2.0,
                          color=CODE_MUTED, fill_color="#101826",
                          fill_opacity=1.0)
        tramo.move_to((x + w / 2, 0, 0))
        tramos.add(tramo)
        tag = _texto_hud(f"{z:.1f}" if z != round(z) else f"{z:.0f}",
                         font_size=15, color=COLOR_CALCULO)
        tag.next_to(tramo, UP, buff=0.14)
        etiquetas.add(tag)
        x += w
    return LineaCuartos(tramos, etiquetas, VGroup(), zs)


class GuiaTe10(_Anclada):
    """La guia rectangular y el rebote del modo: el zigzag segun f/fc."""

    def __init__(self, paredes, zigzag, patron, a_metros, f_hz, **kwargs):
        super().__init__(paredes, patron, zigzag, **kwargs)
        self.paredes = paredes
        self.zigzag = zigzag
        self.patron = patron
        self._a = a_metros
        self._f = f_hz
        self._anclar()

    def fc_hz(self):
        """El corte de ESTA guia — la misma cuenta que rotula el clip."""
        return fc_te10(self._a)

    def con_frecuencia(self, f_hz):
        """La misma guia con la onda a otra frecuencia: cerca del corte
        el zigzag es casi vertical (no avanza); lejos, casi recto."""
        nueva = guia_te10(a_metros=self._a, f_hz=f_hz)
        nueva.move_to(self.get_center())
        return nueva


def guia_te10(a_metros=0.02286, f_hz=10e9, largo=5.8, alto=1.5,
              color_onda=COLOR_ONDA, color_e=COLOR_E):
    """La WR-90 vista desde arriba, con el rayo rebotando al angulo REAL:
    cos(theta) = fc/f respecto de la pared. A 10 GHz con fc = 6.557 GHz
    el rebote avanza; bajar hacia fc lo empina hasta que a fc rebota en
    vertical y no avanza NADA — el corte hecho geometria.
    """
    fc = fc_te10(a_metros)
    f = float(f_hz)
    if f <= fc:
        raise ValueError(f"guia_te10: f={f:.3g} por debajo del corte "
                         f"{fc:.3g}; la guia no transporta")
    paredes = VGroup(
        Line((-largo / 2, alto / 2, 0), (largo / 2, alto / 2, 0),
             stroke_width=4.0, color=CODE_MUTED),
        Line((-largo / 2, -alto / 2, 0), (largo / 2, -alto / 2, 0),
             stroke_width=4.0, color=CODE_MUTED))
    # el angulo del rayo respecto del EJE: sen = fc/f
    seno = fc / f
    coseno = np.sqrt(1.0 - seno * seno)
    paso_x = alto * coseno / max(seno, 1e-6)
    puntos = [np.array([-largo / 2, -alto / 2])]
    y_arriba = True
    x = -largo / 2
    while x + paso_x <= largo / 2 + 1e-9:
        x += paso_x
        puntos.append(np.array([x, alto / 2 if y_arriba else -alto / 2]))
        y_arriba = not y_arriba
    if len(puntos) < 2:
        puntos.append(np.array([largo / 2,
                                alto / 2 if y_arriba else -alto / 2]))
    zigzag = _curva(np.array(puntos), color_onda, grosor=2.6, suave=False)

    # el patron del modo: E maximo al centro, nulo en las paredes
    patron = VGroup()
    for x0 in np.linspace(-largo / 2 + 0.5, largo / 2 - 0.5, 7):
        for frac, s in ((0.0, 1.0), (0.55, 0.62), (-0.55, 0.62)):
            y0 = frac * alto / 2
            largo_flecha = 0.30 * s
            patron.add(Arrow((x0, y0 - largo_flecha / 2, 0),
                             (x0, y0 + largo_flecha / 2, 0), buff=0,
                             color=color_e, stroke_width=1.8,
                             stroke_opacity=0.5, tip_length=0.08))
    return GuiaTe10(paredes, zigzag, patron, a_metros, f)


class DipoloRadiante(_Anclada):
    """El dipolo alimentado al centro y los frentes que se sueltan."""

    def __init__(self, brazos, alimentacion, frentes, cargas_mob, lam,
                 **kwargs):
        super().__init__(frentes, brazos, alimentacion, cargas_mob,
                         **kwargs)
        self.brazos = brazos
        self.alimentacion = alimentacion
        self.frentes = frentes
        self.cargas = cargas_mob
        self._lam = lam
        self._anclar()

    def frente(self, i):
        return self.frentes[i]

    def lambda_escena(self):
        """Separacion entre frentes = lambda en unidades de escena."""
        return self._lam


def dipolo_radiante(largo_brazo=1.1, n_frentes=4, lam=1.15,
                    color_antena=COLOR_CARGA, color_onda=COLOR_ONDA):
    """El dipolo de media onda: dos brazos, el generador al centro, las
    cargas oscilando (puntos en los brazos) y los frentes separados
    exactamente lambda. Los brazos miden lambda/4 cada uno si
    largo_brazo = lam/2 * 0.5 — el clip acota la resonancia con
    `lambda_escena`."""
    if not 1 <= int(n_frentes) <= 8:
        raise ValueError("dipolo_radiante: n_frentes fuera de 1..8")
    brazos = VGroup(
        Line((0, 0.14, 0), (0, 0.14 + largo_brazo, 0), stroke_width=5.0,
             color=color_antena),
        Line((0, -0.14, 0), (0, -0.14 - largo_brazo, 0), stroke_width=5.0,
             color=color_antena))
    alimentacion = VGroup(
        Circle(radius=0.13, color=CODE_MUTED, stroke_width=2.0),
        _texto_hud("~", font_size=16, color=CODE_MUTED))
    cargas_mob = VGroup()
    for y in (0.45, 0.95, -0.45, -0.95):
        cargas_mob.add(Dot((0, y, 0), radius=0.05, color=COLOR_E))
    frentes = VGroup()
    for i in range(int(n_frentes)):
        r = 0.45 + lam * i
        rel = 1.0 / (1.0 + 0.8 * i)
        frentes.add(Circle(radius=r, color=color_onda,
                           stroke_width=1.4 + 2.2 * rel,
                           stroke_opacity=0.25 + 0.65 * rel))
    return DipoloRadiante(brazos, alimentacion, frentes, cargas_mob, lam)


class PatronPolar(_Anclada):
    """El patron en polares de la funcion que le den: no puede discrepar
    de los numeros porque ES los numeros."""

    def __init__(self, rejilla, lobulos, funciones, radio, **kwargs):
        super().__init__(rejilla, lobulos, **kwargs)
        self.rejilla = rejilla
        self.lobulos = lobulos
        self._funciones = funciones
        self._radio = radio
        self._anclar()

    def lobulo(self, i):
        return self.lobulos[i]

    def valor(self, i, theta_deg):
        """|f| normalizado en esa direccion (theta desde el eje +x)."""
        return float(self._normalizadas[i](np.radians(float(theta_deg))))

    def punto_de(self, i, theta_deg):
        t = np.radians(float(theta_deg))
        r = self._radio * self.valor(i, theta_deg)
        return self._desde(r * np.cos(t), r * np.sin(t))

    def con_funciones(self, funciones, colores=None):
        """El mismo marco con otros lobulos (ReplacementTransform): asi
        gira el haz de un array al cambiar la rampa de fase."""
        nueva = patron_polar(funciones, radio=self._radio, colores=colores)
        nueva.move_to(self.get_center())
        return nueva


def patron_polar(funciones, radio=1.9, colores=None, muestras=240,
                 con_rejilla=True):
    """Patron(es) en polares. `funciones` reciben theta en RADIANES
    (medido desde el eje +x del dibujo) y devuelven amplitud; cada lobulo
    se normaliza a su maximo, que es como se comparan formas de patron.
    """
    muestras = _validar_muestras("patron_polar", muestras)
    if not 1 <= len(funciones) <= CURVAS_MAX:
        raise ValueError(f"patron_polar: 1..{CURVAS_MAX} funciones")
    if colores is None:
        colores = [COLOR_ONDA, COLOR_CALCULO, COLOR_E, COLOR_B][:len(
            funciones)]
    rejilla = VGroup()
    if con_rejilla:
        for frac in (1.0, 0.5):
            rejilla.add(DashedVMobject(
                Circle(radius=radio * frac, color=COLOR_EJE,
                       stroke_width=1.2), num_dashes=40))
        for ang in np.radians([0, 45, 90, 135]):
            d = np.array([np.cos(ang), np.sin(ang), 0.0]) * radio
            rejilla.add(Line(-d, d, stroke_width=1.0, color=COLOR_EJE,
                             stroke_opacity=0.7))
    ts = np.linspace(0.0, 2.0 * np.pi, muestras)
    lobulos = VGroup()
    normalizadas = []
    for funcion, color in zip(funciones, colores):
        vals = np.abs(np.asarray([float(funcion(float(t))) for t in ts]))
        vmax = float(vals.max())
        if vmax <= 0:
            raise ValueError("patron_polar: una funcion es nula")
        rs = vals / vmax * radio
        pts = np.column_stack([rs * np.cos(ts), rs * np.sin(ts)])
        lobulos.add(_curva(pts, color, grosor=2.8))
        normalizadas.append(
            (lambda fn, vm: (lambda t: abs(float(fn(float(t)))) / vm))(
                funcion, vmax))
    pieza = PatronPolar(rejilla, lobulos, list(funciones), radio)
    pieza._normalizadas = normalizadas
    return pieza


class ParabolaFoco(_Anclada):
    """El plato: rayos paralelos que la geometria manda TODOS al foco."""

    def __init__(self, plato, rayos, foco_mob, brazo, distancia_focal,
                 **kwargs):
        super().__init__(plato, rayos, brazo, foco_mob, **kwargs)
        self.plato = plato
        self.rayos = rayos
        self.foco_mob = foco_mob
        self.brazo = brazo
        self._f = distancia_focal
        self._anclar()

    def rayo(self, i):
        return self.rayos[i]

    def foco(self):
        """El punto de escena del foco (donde vive el LNB)."""
        return self.foco_mob.get_center()


def parabola_foco(apertura=3.4, distancia_focal=1.15, n_rayos=6,
                  color_rayo=COLOR_ONDA):
    """La parabola x = y^2/(4f) con rayos horizontales reflejados AL FOCO
    por la ley de reflexion de verdad (la propiedad focal no se impone:
    se calcula el rebote y sale)."""
    if not 2 <= int(n_rayos) <= 10:
        raise ValueError("parabola_foco: n_rayos fuera de 2..10")
    f = float(distancia_focal)
    ys = np.linspace(-apertura / 2, apertura / 2, 60)
    xs = ys ** 2 / (4.0 * f)
    x_borde = float(xs.max())
    plato = _curva(np.column_stack([xs - x_borde, ys]), CODE_MUTED,
                   grosor=4.0)
    foco_mob = Dot((f - x_borde, 0, 0), radius=0.09, color=COLOR_CARGA)
    brazo = Line((0.10 - x_borde, -apertura / 2 - 0.0, 0),
                 (f - x_borde, 0, 0), stroke_width=1.6, color=COLOR_EJE)

    rayos = VGroup()
    for y0 in np.linspace(-apertura / 2 * 0.85, apertura / 2 * 0.85,
                          int(n_rayos)):
        x_choque = y0 ** 2 / (4.0 * f)
        # reflexion real: entrante d=(-1,0); normal de la parabola
        # x - y^2/4f = 0 -> grad = (1, -y/2f) normalizado
        normal = np.array([1.0, -y0 / (2.0 * f)])
        normal = normal / np.linalg.norm(normal)
        d = np.array([-1.0, 0.0])
        r = d - 2.0 * float(d @ normal) * normal
        p_choque = np.array([x_choque - x_borde, y0, 0.0])
        p_final = p_choque + np.array([r[0], r[1], 0.0]) * (
            np.hypot(f - x_choque, y0))
        rayos.add(VGroup(
            Line((x_borde + 1.0 - x_borde + 1.4, y0, 0), p_choque,
                 stroke_width=2.2, color=color_rayo),
            Line(p_choque, p_final, stroke_width=2.2, color=color_rayo)))
    return ParabolaFoco(plato, rayos, foco_mob, brazo, f)


class ArrayFases(_Anclada):
    """La fila de elementos, su rampa de fase y el frente inclinado."""

    def __init__(self, elementos, barras, frente, flecha, n, d_lambda,
                 fase_deg, **kwargs):
        super().__init__(elementos, barras, frente, flecha, **kwargs)
        self.elementos = elementos
        self.barras = barras
        self.frente = frente
        self.flecha = flecha
        self._n = n
        self._d_lambda = d_lambda
        self._fase = fase_deg
        self._anclar()

    def apuntado_deg(self):
        """A donde mira: la misma cuenta que `angulo_apuntado`."""
        return angulo_apuntado(self._d_lambda, self._fase)

    def patron(self, theta):
        """El factor de array de ESTE array (para un patron_polar al
        lado, sin duplicar numeros). `theta` en radianes desde la
        normal."""
        return float(factor_array(self._n, self._d_lambda, self._fase,
                                  theta))

    def con_fase(self, fase_deg):
        """El mismo array con otra rampa (ReplacementTransform)."""
        nueva = array_fases(n=self._n, d_lambda=self._d_lambda,
                            fase_deg=fase_deg)
        nueva.move_to(self.get_center())
        return nueva


def array_fases(n=8, d_lambda=0.5, fase_deg=0.0, ancho=5.4,
                color_elemento=COLOR_CARGA, color_frente=COLOR_ONDA,
                color_fase=COLOR_CALCULO):
    """Los n elementos en fila, la rampa de fase como barras y el frente
    de onda PERPENDICULAR a donde `angulo_apuntado` dice que se mira.

    Con rampa cero el frente es horizontal (broadside); cada grado de
    rampa lo inclina — el haz se mueve sin que se mueva nada.
    """
    n_el = int(n)
    if not 2 <= n_el <= 16:
        raise ValueError("array_fases: n fuera de 2..16 (dibujables)")
    xs = np.linspace(-ancho / 2, ancho / 2, n_el)
    elementos, barras = VGroup(), VGroup()
    for i, x in enumerate(xs):
        elementos.add(VGroup(
            Line((x - 0.14, 0, 0), (x + 0.14, 0, 0), stroke_width=3.4,
                 color=color_elemento),
            Line((x, 0, 0), (x, -0.22, 0), stroke_width=2.0,
                 color=color_elemento)))
        fase_i = float(fase_deg) * i
        alto_barra = 0.014 * abs(fase_i)
        if alto_barra > 1e-6:
            barra = Rectangle(width=0.16, height=min(alto_barra, 1.35),
                              stroke_width=0, fill_color=color_fase,
                              fill_opacity=0.8)
            barra.move_to((x, -0.45 - min(alto_barra, 1.35) / 2, 0))
            barras.add(barra)
        else:
            barras.add(Line((x - 0.08, -0.45, 0), (x + 0.08, -0.45, 0),
                            stroke_width=2.2, color=color_fase))

    theta0 = np.radians(angulo_apuntado(d_lambda, fase_deg))
    direccion = np.array([np.sin(theta0), np.cos(theta0), 0.0])
    perpendicular = np.array([np.cos(theta0), -np.sin(theta0), 0.0])
    frente = VGroup()
    for k in range(3):
        centro = direccion * (1.1 + 0.75 * k) + np.array([0, 0.0, 0])
        medio = perpendicular * (ancho * 0.42)
        frente.add(Line(centro - medio, centro + medio,
                        stroke_width=2.6 - 0.5 * k, color=color_frente,
                        stroke_opacity=1.0 - 0.22 * k))
    flecha = Arrow((0, 0, 0), direccion * 3.1, buff=0, color=color_frente,
                   stroke_width=3.4, tip_length=0.18)
    return ArrayFases(elementos, barras, frente, flecha, n_el,
                      float(d_lambda), float(fase_deg))


# =====================================================================
# Piezas — modulo 4: el enlace por el espacio
# =====================================================================
def _ne_ionosfera(h_km, momento="dia"):
    """Densidad electronica del modelo de juguete de la familia, en m^-3.

    Suma de campanas para D (75 km), E (110) y F (300 de dia, 350 y mas
    tenue de noche). Los PICOS son los realistas — F diurna 1e12 m^-3,
    que da fp ~ 9 MHz con `frecuencia_plasma` — y esa es la unica
    pretension del modelo: las formas finas cambian con el sol y la hora.
    """
    h = np.asarray(h_km, dtype=np.float64)

    def campana(a, h0, s):
        return a * np.exp(-((h - h0) / s) ** 2)

    if momento == "dia":
        return (campana(2.5e9, 75.0, 14.0) + campana(1.5e11, 110.0, 20.0)
                + campana(1.0e12, 300.0, 85.0))
    if momento == "noche":
        return campana(5.0e9, 110.0, 22.0) + campana(2.0e11, 350.0, 95.0)
    raise ValueError("_ne_ionosfera: momento 'dia' o 'noche'")


class CapasIonosfera(_Cartesiano):
    """El perfil Ne(h) con sus capas: el techo electrico del planeta."""

    def __init__(self, ejes, curva_dia, curva_noche, franjas, etiquetas,
                 ne_max, h_max, ancho, alto, origen, **kwargs):
        super().__init__(ejes, franjas, curva_noche, curva_dia, etiquetas,
                         **kwargs)
        self.ejes = ejes
        self.curva_dia = curva_dia
        self.curva_noche = curva_noche
        self.franjas = franjas
        self.etiquetas = etiquetas
        self._ne_max = ne_max
        self._h_max = h_max
        self._calibrar((0.0, 1.0), (0.0, h_max), ancho, alto, origen)

    def ne(self, h_km, momento="dia"):
        """La densidad del perfil dibujado (para `frecuencia_plasma`)."""
        return float(_ne_ionosfera(h_km, momento))

    def punto_de(self, h_km, momento="dia"):
        """Punto de escena del perfil a esa altura."""
        return self._en(self.ne(h_km, momento) / self._ne_max,
                        float(h_km))


def capas_ionosfera(h_max=420.0, ancho=4.9, alto=3.1, color_dia=COLOR_E,
                    color_noche=COLOR_EJE, muestras=200):
    """Altura en vertical (como se dibuja una atmosfera), Ne en
    horizontal; el dia en ambar y la noche como fantasma gris — la capa D
    desaparece al ponerse el sol, y con ella la absorcion."""
    muestras = _validar_muestras("capas_ionosfera", muestras)
    hs = np.linspace(0.0, h_max, muestras)
    dia = _ne_ionosfera(hs, "dia")
    noche = _ne_ionosfera(hs, "noche")
    ne_max = float(dia.max()) * 1.06

    ejes, origen = _ejes_xy(ancho, alto, COLOR_EJE)
    curvas = []
    for ne, color in ((dia, color_dia), (noche, color_noche)):
        fx = ne / ne_max
        fy = hs / h_max
        pts = origen + np.column_stack([fx * ancho, fy * alto,
                                        np.zeros(muestras)])
        curvas.append(_curva(pts, color, grosor=2.8))

    franjas, etiquetas = VGroup(), VGroup()
    for nombre, h0, h1 in (("D", 60.0, 90.0), ("E", 95.0, 130.0),
                           ("F", 180.0, 400.0)):
        y0, y1 = h0 / h_max * alto, h1 / h_max * alto
        franja = Rectangle(width=ancho, height=y1 - y0, stroke_width=0,
                           fill_color=COLOR_ONDA, fill_opacity=0.07)
        franja.move_to(origen + np.array([ancho / 2, (y0 + y1) / 2, 0.0]))
        franjas.add(franja)
        tag = _texto_hud(nombre, font_size=16, color=CODE_MUTED)
        tag.move_to(origen + np.array([ancho + 0.28, (y0 + y1) / 2, 0.0]))
        etiquetas.add(tag)
    return CapasIonosfera(ejes, curvas[0], curvas[1], franjas, etiquetas,
                          ne_max, h_max, ancho, alto, origen)


class ReboteHF(_Anclada):
    """La onda corta dando la vuelta al planeta a saltos."""

    def __init__(self, tierra, iono, saltos, alcances, **kwargs):
        super().__init__(tierra, iono, saltos, **kwargs)
        self.tierra = tierra
        self.iono = iono
        self.saltos = saltos
        self._alcances = alcances
        self._anclar()

    def salto(self, i):
        return self.saltos[i]

    def alcance_km(self, i):
        """Distancia sobre el suelo acumulada tras el salto i (misma
        geometria circular que el dibujo)."""
        return float(self._alcances[i])


def rebote_hf(n_saltos=3, salto_deg=22.0, radio=6.5, h_iono_rel=0.115,
              color_onda=COLOR_ONDA):
    """La Tierra como arco grande, la capa F encima, y el rayo que
    rebota techo-suelo-techo. `salto_deg` es el angulo central de CADA
    salto; con el radio real eso son ~2400 km por salto — tres saltos
    cruzan un oceano, que es la cuenta de `alcance_km`."""
    if not 1 <= int(n_saltos) <= 5:
        raise ValueError("rebote_hf: n_saltos fuera de 1..5")
    centro = np.array([0.0, -radio + 0.9, 0.0])
    barrido = np.radians(salto_deg * (int(n_saltos) + 0.6))
    a0 = np.pi / 2 + barrido / 2

    tierra = Arc(radius=radio, start_angle=a0, angle=-barrido,
                 color=CODE_MUTED, stroke_width=3.0, arc_center=centro)
    r_iono = radio * (1.0 + h_iono_rel)
    iono = DashedVMobject(
        Arc(radius=r_iono, start_angle=a0, angle=-barrido,
            color=COLOR_E, stroke_width=2.0, arc_center=centro),
        num_dashes=40)

    saltos = VGroup()
    alcances = []
    ang = a0 - np.radians(salto_deg) * 0.3
    acumulado = 0.0
    for i in range(int(n_saltos)):
        medio = ang - np.radians(salto_deg) / 2
        fin = ang - np.radians(salto_deg)
        p0 = centro + radio * np.array([np.cos(ang), np.sin(ang), 0.0])
        p1 = centro + r_iono * np.array([np.cos(medio), np.sin(medio),
                                         0.0])
        p2 = centro + radio * np.array([np.cos(fin), np.sin(fin), 0.0])
        saltos.add(VGroup(
            Line(p0, p1, stroke_width=2.6, color=color_onda),
            Line(p1, p2, stroke_width=2.6, color=color_onda)))
        acumulado += np.radians(salto_deg) * R_TIERRA / 1000.0
        alcances.append(acumulado)
        ang = fin
    return ReboteHF(tierra, iono, saltos, alcances)


class VentanaIono(_Anclada):
    """Rayos hacia la ionosfera: los lentos rebotan, los rapidos cruzan."""

    def __init__(self, suelo, capa, rayos, comportamientos, fp, **kwargs):
        super().__init__(suelo, capa, rayos, **kwargs)
        self.suelo = suelo
        self.capa = capa
        self.rayos = rayos
        self.comportamientos = comportamientos
        self._fp = fp
        self._anclar()

    def rayo(self, i):
        return self.rayos[i]

    def fp_hz(self):
        """La frecuencia de plasma que decide quien cruza."""
        return self._fp


def ventana_iono(frecuencias=(5e6, 15e6, 300e6), ne_pico=1.0e12,
                 color_onda=COLOR_ONDA):
    """El suelo, la capa (a la altura del pico F) y un rayo por
    frecuencia, todos con el mismo angulo de salida.

    Quien rebota y quien cruza lo decide `frecuencia_plasma(ne_pico)` —
    unos 9 MHz — comparada con cada portadora: f < fp rebota SIEMPRE
    (aun en vertical); por encima, la capa es una ventana. El matiz
    oblicuo (la MUF, fp por la secante) es narrativa del clip.
    """
    if not 2 <= len(frecuencias) <= CURVAS_MAX:
        raise ValueError(f"ventana_iono: 2..{CURVAS_MAX} frecuencias")
    fp = frecuencia_plasma(ne_pico)
    suelo = Line((-5.4, -1.7, 0), (5.4, -1.7, 0), stroke_width=2.6,
                 color=CODE_MUTED)
    capa = Rectangle(width=10.8, height=0.75, stroke_width=0,
                     fill_color=COLOR_E, fill_opacity=0.14)
    capa.move_to((0, 1.35, 0))

    origen = np.array([-4.1, -1.7, 0.0])
    rayos = VGroup()
    comportamientos = []
    for k, f in enumerate(frecuencias):
        d = np.array([np.cos(np.radians(52.0)), np.sin(np.radians(52.0)),
                      0.0])
        p_capa = origen + d * ((1.05 - origen[1]) / d[1])
        desplaza = np.array([1.15 * k, 0.0, 0.0])
        if f < fp:
            # rebota: sube, toca la capa y baja simetrico
            bajada = np.array([d[0], -d[1], 0.0])
            p_suelo = p_capa + bajada * ((p_capa[1] + 1.7) / d[1])
            rayo = VGroup(
                Line(origen + desplaza, p_capa + desplaza,
                     stroke_width=2.6, color=color_onda),
                Line(p_capa + desplaza, p_suelo + desplaza,
                     stroke_width=2.6, color=color_onda))
            comportamientos.append("rebota")
        else:
            # cruza: un quiebro pequeño dentro de la capa y sigue
            d2 = np.array([np.cos(np.radians(46.0)),
                           np.sin(np.radians(46.0)), 0.0])
            p_fuera = p_capa + d2 * 1.9
            rayo = VGroup(
                Line(origen + desplaza, p_capa + desplaza,
                     stroke_width=2.6, color=color_onda),
                Line(p_capa + desplaza, p_fuera + desplaza,
                     stroke_width=2.6, color=color_onda))
            comportamientos.append("cruza")
        rayos.add(rayo)
    return VentanaIono(suelo, capa, rayos, comportamientos, fp)


class BarrasRetardo(_Anclada):
    """El peaje ionosferico por portadora: la barra ES el retardo."""

    def __init__(self, suelo, barras, etiquetas, fs, tec, escala,
                 **kwargs):
        super().__init__(suelo, barras, etiquetas, **kwargs)
        self.suelo = suelo
        self.barras = barras
        self.etiquetas = etiquetas
        self._fs = fs
        self._tec = tec
        self._escala = escala
        self._anclar()

    def retardo_m(self, i):
        """Los metros de mas de la portadora i — de `retardo_iono`."""
        return retardo_iono(self._tec, self._fs[i])

    def barra(self, i):
        return self.barras[i]


def barras_retardo(frecuencias=(1.57542e9, 1.22760e9), nombres=("L1", "L2"),
                   tec=5.0e17, escala=0.28, color=COLOR_CALCULO):
    """Una barra por portadora, altura = metros de retardo a ese TEC
    (50 TECU por defecto: L1 8.1 m, L2 13.4 m). La DIFERENCIA entre
    barras es lo que el receptor mide y le permite despejar el TEC."""
    if len(frecuencias) != len(nombres):
        raise ValueError("barras_retardo: un nombre por frecuencia")
    suelo = Line((-1.9, 0, 0), (1.9, 0, 0), stroke_width=2.0,
                 color=COLOR_EJE)
    barras, etiquetas = VGroup(), VGroup()
    xs = np.linspace(-0.9, 0.9, len(frecuencias))
    for x, f, nombre in zip(xs, frecuencias, nombres):
        alto = retardo_iono(tec, f) * escala
        barra = Rectangle(width=0.62, height=alto, stroke_width=0,
                          fill_color=color, fill_opacity=0.85)
        barra.move_to((x, alto / 2, 0))
        barras.add(barra)
        tag = _texto_hud(nombre, font_size=15, color=CODE_MUTED)
        tag.move_to((x, -0.28, 0))
        etiquetas.add(tag)
    pieza = BarrasRetardo(suelo, barras, etiquetas, list(frecuencias),
                          tec, escala)
    return pieza


class PaseLeo(_Anclada):
    """El pase de un LEO sobre la cupula del cielo del observador."""

    def __init__(self, cupula, horizonte, observador, trayecto, geo,
                 radio, **kwargs):
        super().__init__(cupula, horizonte, observador, trayecto,
                         **kwargs)
        self.cupula = cupula
        self.horizonte = horizonte
        self.observador = observador
        self.trayecto = trayecto
        self._geo = geo
        self._radio = radio
        self._anclar()

    def t_max(self):
        """Medio pase, en segundos: el pase completo dura 2 t_max."""
        return float(self._geo["t"][-1])

    def elevacion(self, t):
        return float(np.interp(float(t), self._geo["t"],
                               self._geo["elevacion"]))

    def distancia_km(self, t):
        return float(np.interp(float(t), self._geo["t"],
                               self._geo["distancia"]) / 1000.0)

    def doppler_khz(self, t, f_hz):
        """El corrimiento de esa portadora en ese instante, en kHz."""
        v = float(np.interp(float(t), self._geo["t"],
                            self._geo["v_radial"]))
        return float(-float(f_hz) * v / C_LUZ / 1000.0)

    def a_tiempo(self, t):
        """Punto de escena del satelite en ese instante del pase."""
        tt = float(np.clip(t, self._geo["t"][0], self._geo["t"][-1]))
        frac = tt / max(self._geo["t"][-1], _EPS)
        el = np.radians(self.elevacion(tt))
        x = frac * self._radio * 0.94
        y = np.sin(el) * self._radio
        return self._desde(x, max(y, 0.0))


def pase_leo(h=550e3, el_max_deg=80.0, radio=2.9, color_sat=COLOR_CARGA,
             color_trayecto=COLOR_CALCULO):
    """La cupula del cielo (semicirculo), el horizonte y el arco del
    pase, con la GEOMETRIA REAL de `pase_leo_geometria` detras: la
    elevacion, la distancia y el Doppler de cada instante salen del
    mismo calculo que dibuja el arco."""
    geo = pase_leo_geometria(h, el_max_deg)
    cupula = DashedVMobject(
        Arc(radius=radio, start_angle=0.0, angle=np.pi, color=COLOR_EJE,
            stroke_width=1.8), num_dashes=40)
    horizonte = Line((-radio - 0.4, 0, 0), (radio + 0.4, 0, 0),
                     stroke_width=2.2, color=CODE_MUTED)
    observador = VGroup(
        Polygon((-0.16, 0, 0), (0.16, 0, 0), (0.0, 0.30, 0),
                stroke_width=2.0, color=CODE_MUTED,
                fill_color="#101826", fill_opacity=1.0))

    ts = geo["t"]
    puntos = []
    for tt in np.linspace(ts[0], ts[-1], 90):
        el = np.radians(float(np.interp(tt, ts, geo["elevacion"])))
        frac = tt / max(ts[-1], _EPS)
        puntos.append([frac * radio * 0.94,
                       max(np.sin(el) * radio, 0.0)])
    trayecto = _curva(np.array(puntos), color_trayecto, grosor=2.2)
    return PaseLeo(cupula, horizonte, observador, trayecto, geo, radio)


class MargenEnlace(_Cartesiano):
    """El SNR del enlace contra su umbral mientras pasa la tormenta."""

    def __init__(self, ejes, curva, umbral, corte, ts, snrs, umbral_db,
                 rango_t, rango_snr, ancho, alto, origen, **kwargs):
        super().__init__(ejes, corte, umbral, curva, **kwargs)
        self.ejes = ejes
        self.curva = curva
        self.umbral = umbral
        self.corte = corte
        self._ts = ts
        self._snrs = snrs
        self._umbral_db = umbral_db
        self._calibrar(rango_t, rango_snr, ancho, alto, origen)

    def snr(self, t):
        """El SNR dibujado en ese instante, en dB."""
        return float(np.interp(float(t), self._ts, self._snrs))

    def punto_de(self, t):
        return self._en(float(t), self.snr(t))

    def minimo(self):
        """(t, snr) del fondo del desvanecimiento."""
        i = int(np.argmin(self._snrs))
        return float(self._ts[i]), float(self._snrs[i])

    def margen_db(self):
        """El margen en cielo claro: snr inicial menos umbral."""
        return float(self._snrs[0] - self._umbral_db)


def margen_enlace(snr_claro=12.0, umbral_db=6.0, atenuacion_max=10.0,
                  duracion_min=40.0, ancho=6.0, alto=2.8,
                  color_snr=COLOR_CALCULO, color_umbral=COLOR_CARGA,
                  muestras=200):
    """SNR(t) = claro - tormenta(t), umbral debajo y la zona en que el
    enlace SE CAE sombreada — sale sombreada solo si la tormenta se come
    el margen, que es exactamente lo que el clip quiere enseñar."""
    muestras = _validar_muestras("margen_enlace", muestras)
    ts = np.linspace(0.0, float(duracion_min), muestras)
    centro_t = duracion_min * 0.55
    tormenta = float(atenuacion_max) * np.exp(
        -((ts - centro_t) / (duracion_min * 0.13)) ** 2)
    snrs = float(snr_claro) - tormenta

    y0 = min(float(snrs.min()), umbral_db) - 1.5
    y1 = float(snr_claro) + 1.5
    ejes, origen = _ejes_xy(ancho, alto, COLOR_EJE)
    fx = ts / duracion_min
    fy = (snrs - y0) / (y1 - y0)
    pts = origen + np.column_stack([fx * ancho, fy * alto,
                                    np.zeros(muestras)])
    curva = _curva(pts, color_snr, grosor=2.8)

    fy_u = (umbral_db - y0) / (y1 - y0)
    umbral = DashedLine(origen + np.array([0, fy_u * alto, 0.0]),
                        origen + np.array([ancho, fy_u * alto, 0.0]),
                        stroke_width=1.8, color=color_umbral,
                        dash_length=0.08)

    corte = VGroup()
    debajo = snrs < umbral_db
    if debajo.any():
        t0 = float(ts[np.argmax(debajo)])
        t1 = float(ts[len(ts) - 1 - np.argmax(debajo[::-1])])
        zona = Rectangle(width=(t1 - t0) / duracion_min * ancho,
                         height=alto, stroke_width=0,
                         fill_color=color_umbral, fill_opacity=0.13)
        zona.move_to(origen + np.array(
            [((t0 + t1) / 2) / duracion_min * ancho, alto / 2, 0.0]))
        corte.add(zona)
    return MargenEnlace(ejes, curva, umbral, corte, ts, snrs, umbral_db,
                        (0.0, duracion_min), (y0, y1), ancho, alto,
                        origen)


class CieloRuido(_Anclada):
    """La antena que escucha: el cielo esta frio, el suelo caliente."""

    def __init__(self, plato, cono, termometro, apuntado, t_kelvin,
                 **kwargs):
        super().__init__(cono, plato, termometro, **kwargs)
        self.plato = plato
        self.cono = cono
        self.termometro = termometro
        self.apuntado = apuntado
        self._t = t_kelvin
        self._anclar()

    def t_antena(self):
        """La temperatura que 've' la antena, K."""
        return float(self._t)

    def ruido_dbw(self, ancho_hz):
        """El suelo de ruido de esa T con ese ancho — de `ruido_dbw`."""
        return ruido_dbw(self._t, ancho_hz)


def cielo_ruido(apuntado="cielo", t_cielo=20.0, t_suelo=290.0,
                color_cono=COLOR_ONDA):
    """El plato apuntando al cielo (20 K de fondo frio) o hacia el
    horizonte-suelo (290 K de planeta tibio), con su cono de escucha y
    el termometro al lado. Dos instancias = la comparacion del clip."""
    if apuntado not in ("cielo", "suelo"):
        raise ValueError("cielo_ruido: apuntado 'cielo' o 'suelo'")
    t_kelvin = float(t_cielo if apuntado == "cielo" else t_suelo)
    ang = np.radians(64.0 if apuntado == "cielo" else 8.0)
    d = np.array([np.cos(ang), np.sin(ang), 0.0])

    ys = np.linspace(-0.42, 0.42, 40)
    xs = ys ** 2 / 1.4
    plato_arc = _curva(np.column_stack([xs, ys]), CODE_MUTED, grosor=3.6)
    pie = Line((0.12, -0.42, 0), (0.12, -0.85, 0), stroke_width=2.4,
               color=CODE_MUTED)
    plato = VGroup(plato_arc, pie)
    # la parabola nace abriendose hacia +x; se gira hacia donde apunta
    plato_arc.rotate(ang, about_point=(0, 0, 0))

    cono = VGroup()
    for s in (-1, 1):
        borde = np.radians(11.0) * s
        d_borde = np.array([np.cos(ang + borde), np.sin(ang + borde),
                            0.0])
        cono.add(DashedLine((0, 0, 0), tuple(d_borde * 3.4),
                            stroke_width=1.6, color=color_cono,
                            dash_length=0.09))

    alto_term = 0.35 + 1.85 * (t_kelvin / 290.0)
    termometro = VGroup(
        Rectangle(width=0.30, height=2.3, stroke_width=1.6,
                  color=COLOR_EJE),
        Rectangle(width=0.30, height=alto_term, stroke_width=0,
                  fill_color=(COLOR_CALCULO if apuntado == "cielo"
                              else COLOR_CARGA), fill_opacity=0.85))
    termometro[0].move_to((2.9, 0.3, 0))
    termometro[1].move_to((2.9, 0.3 - (2.3 - alto_term) / 2, 0))
    return CieloRuido(plato, cono, termometro, apuntado, t_kelvin)


class ArcoFamilia(_Anclada):
    """El recap de la familia: cada etapa del viaje, en su color."""

    def __init__(self, etapas, flechas, nombres, **kwargs):
        super().__init__(flechas, etapas, **kwargs)
        self.etapas = etapas
        self.flechas = flechas
        self._nombres = nombres
        self._anclar()

    def etapa(self, i):
        return self.etapas[i]

    def flecha(self, i):
        return self.flechas[i]

    def nombre(self, i):
        return self._nombres[i]


def arco_familia(paso=1.72):
    """Los siete hitos del curso en fila: carga (rojo), campo (ambar),
    onda (violeta), linea, antena, satelite y el bit (cian). Los iconos
    reutilizan las formas de la familia en miniatura."""
    etapas = VGroup()
    nombres = ["carga", "campo", "onda", "linea", "antena", "satelite",
               "bit"]

    icono_carga = carga(signo=+1, radio=0.12)

    lineas_mini = VGroup()
    for s in (-0.5, 0.0, 0.5):
        arco_l = Arc(radius=0.4, start_angle=s - 0.45, angle=0.9,
                     color=COLOR_E, stroke_width=2.2)
        lineas_mini.add(arco_l)

    xs = np.linspace(-0.42, 0.42, 40)
    onda_mini = _curva(np.column_stack(
        [xs, 0.22 * np.sin(2 * np.pi * 2 * (xs + 0.42) / 0.84)]),
        COLOR_ONDA, grosor=2.4)

    linea_mini = VGroup(
        Line((-0.4, 0.10, 0), (0.4, 0.10, 0), stroke_width=2.2,
             color=CODE_MUTED),
        Line((-0.4, -0.10, 0), (0.4, -0.10, 0), stroke_width=2.2,
             color=CODE_MUTED))

    antena_mini = VGroup(
        Line((0, -0.30, 0), (0, 0.10, 0), stroke_width=2.4,
             color=COLOR_CARGA),
        Line((0, 0.10, 0), (-0.24, 0.38, 0), stroke_width=2.4,
             color=COLOR_CARGA),
        Line((0, 0.10, 0), (0.24, 0.38, 0), stroke_width=2.4,
             color=COLOR_CARGA))

    sat_mini = VGroup(
        Rectangle(width=0.34, height=0.34, stroke_width=2.0,
                  color=CODE_MUTED, fill_color="#101826",
                  fill_opacity=1.0),
        Rectangle(width=0.30, height=0.16, stroke_width=1.4,
                  color=CODE_MUTED).move_to((-0.36, 0, 0)),
        Rectangle(width=0.30, height=0.16, stroke_width=1.4,
                  color=CODE_MUTED).move_to((0.36, 0, 0)))

    bit_mini = _texto_hud("1 0 1 1", font_size=17, color=COLOR_CALCULO)

    iconos = [icono_carga, lineas_mini, onda_mini, linea_mini,
              antena_mini, sat_mini, bit_mini]
    x0 = -paso * (len(iconos) - 1) / 2
    for i, icono in enumerate(iconos):
        icono.move_to((x0 + i * paso, 0, 0))
        etapas.add(icono)

    flechas = VGroup()
    for i in range(len(iconos) - 1):
        flechas.add(Arrow((x0 + i * paso + 0.52, 0, 0),
                          (x0 + (i + 1) * paso - 0.52, 0, 0), buff=0,
                          color=COLOR_EJE, stroke_width=2.2,
                          tip_length=0.12))
    return ArcoFamilia(etapas, flechas, nombres)
