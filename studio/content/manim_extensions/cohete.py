"""Tsiolkovsky: la ecuacion del cohete, etapas y el canon de Newton.

Pensado para el curso "Tsiolkovsky: la tirania del cohete". Todo el
calculo es numpy puro y determinista (balistica RK4 con paso fijo; el
unico azar es la llama, con semilla): mismo script -> mismo render,
condicion necesaria para `--disable_caching`. Nada de red, nada de disco.

La regla de color del curso, que es tambien la de esta libreria: el
PROPELENTE (lo que se quema, la llama) es ambar, la CARGA UTIL (lo que
llega, lo medido) cian, la TIERRA (y la orbita conquistada) verde, la
masa MUERTA y lo imposible (el SSTO) rojo, la ESTRUCTURA violeta.
Mobiliario en `COLOR_EJE`.

Piezas:
    silueta_cohete   contorno + zonas apiladas por fraccion de masa
    patinador        hielo + patinador + bolas; momento conservado, `.en(t)`
    curva_tirania    m0/mf = e^(dv/ve); `.en(dv)`, `.con_ve` (Transform)
    canon_newton     Tierra + monte + `.trayectoria(v_frac)` RK4 real
    barras_carga     barras con NEGATIVOS bajo el eje (el SSTO imposible)
    llama_escape     particulas deterministas del empuje

Los NUMEROS que se rotulan salen de funciones (`razon_masas`,
`fraccion_propelente`, `carga_util` -- que puede ser NEGATIVA y eso es
la tesis --, `v_orbital`, `isp`, `retroceso`) o de constantes con cita
(`VE_*`, `COHETES_REALES`, `DV_LEO`), nunca a mano.

Topes duros para no castigar el VPS (2 vCPU / 2 GB por render):
`PASOS_MAX`, `MUESTRAS_MAX`, `BOLAS_MAX`, `BARRAS_MAX` y
`PARTICULAS_MAX` levantan ValueError.

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from cohete import curva_tirania, razon_masas, carga_util

    curva = curva_tirania()
    self.play(Create(curva.curva))
"""

import math

import numpy as np

from manim import (Circle, Dot, Line, Polygon, Rectangle, Text, VGroup,
                   VMobject, DOWN, LEFT, ORIGIN, RIGHT, TAU, UP)

from code_brand import FUENTE_HUD, registrar_fuentes

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
PASOS_MAX = 60_000          # pasos de una integracion RK4
MUESTRAS_MAX = 600          # muestras de una curva parametrica
BOLAS_MAX = 6
BARRAS_MAX = 8
PARTICULAS_MAX = 60

# Paleta propia de la libreria (coincide con la del curso).
COLOR_PROPELENTE = "#f59e0b"  # lo que se quema: propelente, la llama
COLOR_CARGA = "#22d3ee"       # lo que llega: la carga util, lo medido
COLOR_TIERRA = "#34d399"      # la Tierra, la orbita conquistada
COLOR_MUERTO = "#f43f5e"      # la masa muerta, lo imposible, el SSTO
COLOR_ESTRUCTURA = "#a78bfa"  # tanques, motores, la estructura
COLOR_EJE = "#31414f"         # mobiliario: ejes, cajas, el hielo

C_PROPELENTE, C_CARGA, C_TIERRA = COLOR_PROPELENTE, COLOR_CARGA, COLOR_TIERRA
C_MUERTO, C_ESTRUCTURA, C_EJE = COLOR_MUERTO, COLOR_ESTRUCTURA, COLOR_EJE

# --- Los numeros del mundo -------------------------------------------
# GM y radio terrestres; presupuesto delta-v a LEO = orbital (calculado)
# + perdidas por gravedad y arrastre (cita, ~1.6 km/s); velocidades de
# escape de motores (citas): queroseno/LOX, promedio quimico de trabajo,
# hidrogeno/LOX, ionico. Cohetes reales: (nombre, carga a LEO t, masa al
# despegue t), citas publicas.
GM_TIERRA = 3.986004418e14    # m^3/s^2
RADIO_TIERRA = 6.371e6        # m
G0 = 9.80665                  # m/s^2 (define el Isp)
PERDIDAS_LEO = 1600.0         # m/s (cita: gravedad + arrastre)
ALTURA_LEO = 200e3            # m
VE_RP1 = 3000.0               # m/s
VE_QUIMICO = 3500.0           # m/s (valor de trabajo del curso)
VE_HIDROLOX = 4400.0          # m/s
VE_ION = 30000.0              # m/s
EPS_ESTRUCTURA = 0.08         # fraccion estructural del modelo de etapas
COHETES_REALES = (("Saturn V", 140.0, 2970.0),
                  ("Falcon 9", 22.8, 549.0),
                  ("Soyuz", 7.08, 308.0))

_EPS = 1e-12


# --- nucleo: los numeros ----------------------------------------------
def v_orbital(altura=ALTURA_LEO):
    """v = sqrt(GM/(R+h)) de la orbita circular, en m/s (7788 a 200 km)."""
    return math.sqrt(GM_TIERRA / (RADIO_TIERRA + float(altura)))


def dv_leo():
    """El presupuesto del curso: orbital CALCULADA + perdidas (cita)."""
    return v_orbital() + PERDIDAS_LEO


DV_LEO = dv_leo()             # ~9388 m/s


def delta_v(ve, m0, mf):
    """Tsiolkovsky: dv = ve ln(m0/mf)."""
    m0, mf = float(m0), float(mf)
    if mf <= 0 or m0 < mf:
        raise ValueError(f"delta_v: masas invalidas m0={m0}, mf={mf}")
    return float(ve) * math.log(m0 / mf)


def razon_masas(dv=DV_LEO, ve=VE_QUIMICO):
    """m0/mf = e^(dv/ve): el multiplicador que cobra el logaritmo."""
    return math.exp(float(dv) / float(ve))


def fraccion_propelente(dv=DV_LEO, ve=VE_QUIMICO):
    """1 - e^(-dv/ve): que parte del cohete es combustible."""
    return 1.0 - 1.0 / razon_masas(dv, ve)


def carga_util(dv=DV_LEO, ve=VE_QUIMICO, eps=EPS_ESTRUCTURA, etapas=1):
    """Fraccion de carga util del modelo clasico de etapas iguales.

    Por etapa (dv/n cada una, estructura eps de la masa no-carga):
    lambda = (e^(-dv/(n ve)) - eps) / (1 - eps); total lambda^n.
    PUEDE SER NEGATIVA (SSTO quimico: -1.3 %): la ecuacion no cierra y
    esa es la tesis del clip 6. Se dibuja tal cual.
    """
    n = int(etapas)
    if n < 1 or n > 6:
        raise ValueError(f"carga_util: etapas={n} fuera de rango (1..6)")
    x = float(dv) / (n * float(ve))
    lam = (math.exp(-x) - float(eps)) / (1.0 - float(eps))
    if lam <= 0.0:
        # una etapa imposible arrastra el producto: se reporta la propia
        # lambda negativa (n=1 es el caso que se dibuja)
        return lam if n == 1 else lam * abs(lam) ** (n - 1)
    return lam ** n


def isp(ve=VE_QUIMICO):
    """Isp = ve/g0, en segundos (357 s para el promedio quimico)."""
    return float(ve) / G0


def retroceso(m_bola=5.0, u=10.0, m_total=70.0):
    """Retroceso del patinador al lanzar m_bola a u RELATIVOS: momento
    conservado, m_bola*u/(m_total - m_bola) = 0.769 m/s."""
    m_bola, m_total = float(m_bola), float(m_total)
    if m_bola >= m_total:
        raise ValueError("retroceso: la bola pesa mas que el patinador")
    return m_bola * float(u) / (m_total - m_bola)


# --- utilidades internas ----------------------------------------------
def _texto_hud(texto, font_size=15, color=COLOR_EJE):
    registrar_fuentes()
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=color)


def _poligonal(puntos, color, grosor=2.0):
    pts = np.asarray(puntos, dtype=np.float64)
    if pts.shape[1] == 2:
        pts = np.column_stack([pts, np.zeros(len(pts))])
    linea = VMobject(color=color, stroke_width=grosor)
    linea.set_points_as_corners(pts)
    return linea


def _ancla(punto=ORIGIN):
    """Dot invisible que viaja con la pieza: localizador inmune a move_to."""
    p = np.asarray(punto, dtype=np.float64)
    if p.shape == (2,):
        p = np.append(p, 0.0)
    return Dot(p, radius=0.001, fill_opacity=0.0, stroke_opacity=0.0)


def _validar(nombre, valor, tope):
    valor = int(valor)
    if valor < 1 or valor > tope:
        raise ValueError(f"{nombre}: {valor} fuera de rango (1..{tope})")
    return valor


# =====================================================================
# La silueta del cohete
# =====================================================================
class SiluetaCohete(VGroup):
    """Contorno + zonas de masa apiladas; `.zona(nombre)` localiza."""

    def __init__(self, ancla, contorno, zonas, params, **kwargs):
        super().__init__(ancla, contorno, *zonas.values(), **kwargs)
        self._ancla = ancla            # centro de la base
        self.contorno = contorno
        self._zonas = zonas
        self.fracciones = params["fracciones"]
        self._params = params

    def zona(self, nombre):
        """El rectangulo de una zona: 'propelente'|'estructura'|'carga'."""
        return self._zonas[nombre]


def silueta_cohete(frac_propelente, frac_estructura, frac_carga,
                   alto=4.2, ancho=1.05):
    """Cohete de perfil con la masa apilada a escala VERTICAL.

    Las tres fracciones (de la masa total) se apilan de abajo arriba:
    propelente ambar, estructura violeta, carga cian. La altura de cada
    zona ES su fraccion de masa: la franja cian minuscula del clip 1 es
    el punto. Deben sumar ~1 (tolerancia 1e-6).
    """
    fracs = (float(frac_propelente), float(frac_estructura),
             float(frac_carga))
    if any(f < 0 for f in fracs) or abs(sum(fracs) - 1.0) > 1e-6:
        raise ValueError(f"silueta_cohete: fracciones invalidas {fracs}")
    alto, ancho = float(alto), float(ancho)
    base = np.array([0.0, -alto / 2.0, 0.0])
    # el cuerpo contiene TODA la pila de masa (la altura de cada zona es
    # su fraccion de `alto`); la nariz va encima, vacia, como remate
    h_cuerpo = alto
    h_nariz = alto * 0.14

    colores = {"propelente": COLOR_PROPELENTE,
               "estructura": COLOR_ESTRUCTURA, "carga": COLOR_CARGA}
    nombres = ("propelente", "estructura", "carga")
    zonas, y = {}, 0.0
    for nombre, f in zip(nombres, fracs):
        h = alto * f
        r = Rectangle(width=ancho * 0.92, height=max(h, 1e-4),
                      stroke_width=0.0, fill_color=colores[nombre],
                      fill_opacity=0.85)
        r.move_to(base + UP * (y + h / 2.0))
        zonas[nombre] = r
        y += h

    cuerpo = Rectangle(width=ancho, height=h_cuerpo, stroke_width=2.6,
                       color=COLOR_EJE)
    cuerpo.move_to(base + UP * h_cuerpo / 2.0)
    nariz = Polygon(base + UP * h_cuerpo + LEFT * ancho / 2.0,
                    base + UP * h_cuerpo + RIGHT * ancho / 2.0,
                    base + UP * (h_cuerpo + h_nariz),
                    stroke_width=2.6, color=COLOR_EJE)
    aleta_i = Polygon(base + LEFT * ancho / 2.0,
                      base + LEFT * (ancho * 0.95),
                      base + LEFT * ancho / 2.0 + UP * alto * 0.16,
                      stroke_width=2.2, color=COLOR_EJE)
    aleta_d = Polygon(base + RIGHT * ancho / 2.0,
                      base + RIGHT * (ancho * 0.95),
                      base + RIGHT * ancho / 2.0 + UP * alto * 0.16,
                      stroke_width=2.2, color=COLOR_EJE)
    contorno = VGroup(cuerpo, nariz, aleta_i, aleta_d)

    params = {"fracciones": dict(zip(nombres, fracs)), "alto": alto,
              "ancho": ancho}
    return SiluetaCohete(_ancla(base), contorno, zonas, params)


# =====================================================================
# El patinador (momento conservado)
# =====================================================================
def _nucleo_patinador(n_bolas, m_pat, m_bola, u, dt_lanza):
    """(t_lanza, v_pat tras cada lanzamiento, v_bola en tierra de cada
    bola). Momento conservado con masa decreciente; el patinador parte
    del reposo en x=0 mirando a la izquierda (lanza hacia -x, retrocede
    hacia +x)."""
    ts, vs_pat, vs_bola = [], [0.0], []
    m = float(m_pat)
    v = 0.0
    for k in range(n_bolas):
        t = (k + 1) * float(dt_lanza)
        v_bola = v - float(u)                 # relativa u hacia -x
        m_despues = m - float(m_bola)
        v = (m * v - float(m_bola) * v_bola) / m_despues
        m = m_despues
        ts.append(t)
        vs_pat.append(v)
        vs_bola.append(v_bola)
    return np.array(ts), np.array(vs_pat), np.array(vs_bola)


class Patinador(VGroup):
    """Hielo + patinador + bolas, reproducible por `.en(t)`."""

    def __init__(self, ancla, hielo, cuerpo, bolas, nucleo, params,
                 **kwargs):
        super().__init__(ancla, hielo, cuerpo, bolas, **kwargs)
        self._ancla = ancla            # el origen (x=0 sobre el hielo)
        self.hielo = hielo
        self.cuerpo = cuerpo           # VGroup(cabeza, tronco, base)
        self.bolas = bolas
        self._nucleo = nucleo
        self._params = params

    def _escala_actual(self):
        return self.hielo.get_length() / max(self._params["largo"], _EPS)

    def retroceso(self):
        """El primer empujon, en m/s (0.769 con los valores por defecto)."""
        return float(self._nucleo[1][1])

    def velocidad_final(self):
        """v del patinador tras lanzar todo, en m/s."""
        return float(self._nucleo[1][-1])

    def en(self, t):
        """Coloca patinador y bolas al tiempo `t` (s) sobre la geometria
        ACTUAL; para UpdateFromAlphaFunc. Devuelve self."""
        ts, vs_pat, vs_bola = self._nucleo
        p = self._params
        esc = self._escala_actual() * p["metros_a_escena"]
        t = float(t)

        # posicion del patinador: integral por tramos de vs_pat
        x, t_prev = 0.0, 0.0
        for t_k, v_k in zip(ts, vs_pat[:-1]):
            if t <= t_k:
                x += v_k * (t - t_prev)
                break
            x += v_k * (t_k - t_prev)
            t_prev = t_k
        else:
            x += vs_pat[-1] * (t - t_prev)
        origen = self._ancla.get_center()
        self.cuerpo.move_to(origen + RIGHT * x * esc
                            + UP * p["alto_cuerpo"] * 0.5
                            * self._escala_actual())

        for k, bola in enumerate(self.bolas):
            if t < ts[k]:
                # aun en la mano: viaja con el patinador, escondida
                bola.move_to(self.cuerpo.get_center())
                bola.set_opacity(0.0)
            else:
                x_b = 0.0
                # el patinador estaba en x(t_k); la bola parte de ahi
                xx, t_prev2 = 0.0, 0.0
                for t_j, v_j in zip(ts, vs_pat[:-1]):
                    if ts[k] <= t_j:
                        xx += v_j * (ts[k] - t_prev2)
                        break
                    xx += v_j * (t_j - t_prev2)
                    t_prev2 = t_j
                x_b = xx + vs_bola[k] * (t - ts[k])
                bola.set_opacity(1.0)
                bola.move_to(origen + RIGHT * x_b * esc
                             + UP * 0.10 * self._escala_actual())
        return self


def patinador(n_bolas=3, m_pat=70.0, m_bola=5.0, u=10.0, dt_lanza=1.1,
              largo=9.0, metros_a_escena=0.55):
    """El patinador que lanza bolas: el cohete en miniatura.

    Nucleo con momento conservado y masa decreciente: cada bola sale a
    `u` m/s RELATIVOS (la 2a sale mas lenta en tierra porque el
    patinador ya retrocede). `pat.en(t)` reproduce t segundos;
    `.retroceso()` y `.velocidad_final()` son los numeros del clip 2.
    `metros_a_escena` comprime metros en unidades de escena.
    """
    n_bolas = _validar("patinador.n_bolas", n_bolas, BOLAS_MAX)
    largo = float(largo)
    nucleo = _nucleo_patinador(n_bolas, m_pat, m_bola, u, dt_lanza)

    hielo = Line(LEFT * largo / 2.0, RIGHT * largo / 2.0,
                 stroke_width=2.4, color=COLOR_EJE)
    alto_cuerpo = 0.95
    cabeza = Dot(UP * alto_cuerpo, radius=0.11, color=COLOR_CARGA)
    tronco = Line(ORIGIN, UP * (alto_cuerpo - 0.11), stroke_width=3.0,
                  color=COLOR_CARGA)
    patines = Line(LEFT * 0.16, RIGHT * 0.16, stroke_width=3.0,
                   color=COLOR_CARGA)
    cuerpo = VGroup(patines, tronco, cabeza)
    cuerpo.move_to(UP * alto_cuerpo * 0.5)

    bolas = VGroup(*[Dot(ORIGIN, radius=0.085, color=COLOR_PROPELENTE)
                     for _ in range(n_bolas)])
    for b in bolas:
        b.set_opacity(0.0)

    params = {"largo": largo, "metros_a_escena": float(metros_a_escena),
              "alto_cuerpo": alto_cuerpo}
    pieza = Patinador(_ancla(ORIGIN), hielo, cuerpo, bolas, nucleo, params)
    return pieza.en(0.0)


# =====================================================================
# La curva de la tirania
# =====================================================================
class CurvaTirania(VGroup):
    """m0/mf contra dv; `.en(dv)` localiza, `.con_ve` transforma."""

    def __init__(self, ancla, ejes, curva, params, **kwargs):
        super().__init__(ancla, ejes, curva, **kwargs)
        self._ancla = ancla            # origen de los ejes
        self.ejes = ejes
        self.curva = curva
        self._params = params
        self.ve = params["ve"]

    def _escala_actual(self):
        return self.ejes[0].get_length() / max(self._params["ancho"], _EPS)

    def en(self, dv):
        """Punto de escena sobre la curva para `dv` m/s (geometria
        ACTUAL)."""
        p = self._params
        esc = self._escala_actual()
        fx = float(dv) / p["dv_max"]
        fy = razon_masas(dv, self.ve) / p["y_max"]
        return (self._ancla.get_center() + RIGHT * fx * p["ancho"] * esc
                + UP * fy * p["alto"] * esc)

    def con_ve(self, ve):
        """La misma caja con otra ve (MISMO rango y): la curva se para o
        se tumba. Anclada por el origen (Transform)."""
        params = dict(self._params, ve=float(ve))
        otro = curva_tirania(**{k: params[k] for k in
                                ("ve", "dv_max", "ancho", "alto",
                                 "y_max", "color", "muestras")})
        otro.shift(self._ancla.get_center() - otro._ancla.get_center())
        return otro


def curva_tirania(ve=VE_QUIMICO, dv_max=11000.0, ancho=5.4, alto=3.0,
                  y_max=None, color=COLOR_PROPELENTE, muestras=220):
    """m0/mf = e^(dv/ve): suave al arranque, vertical al final.

    Ejes en la esquina inferior izquierda (ORIGIN - (a/2, a/2)). Si
    y_max es None se toma e^(dv_max/ve) de ESTA ve; al comparar motores
    con `con_ve` el rango y se conserva para que la comparacion sea
    honesta.
    """
    muestras = _validar("curva_tirania.muestras", muestras, MUESTRAS_MAX)
    ve, dv_max = float(ve), float(dv_max)
    ancho, alto = float(ancho), float(alto)
    if y_max is None:
        y_max = razon_masas(dv_max, ve)
    y_max = float(y_max)
    origen = np.array([-ancho / 2.0, -alto / 2.0, 0.0])

    ejes = VGroup(
        Line(origen, origen + RIGHT * ancho, stroke_width=2.0,
             color=COLOR_EJE),
        Line(origen, origen + UP * alto, stroke_width=2.0,
             color=COLOR_EJE))

    dvs = np.linspace(0.0, dv_max, muestras)
    ys = np.minimum(np.exp(dvs / ve), y_max)
    pts = [origen + RIGHT * (d / dv_max) * ancho + UP * (y / y_max) * alto
           for d, y in zip(dvs, ys)]
    curva = _poligonal(pts, color, 3.0)

    params = {"ve": ve, "dv_max": dv_max, "ancho": ancho, "alto": alto,
              "y_max": y_max, "color": color, "muestras": muestras}
    return CurvaTirania(_ancla(origen), ejes, curva, params)


# =====================================================================
# El canon de Newton (balistica real)
# =====================================================================
def _nucleo_canon(v_frac, r0, pasos, dt):
    """Trayectoria 2D en unidades R=1, GM=1: parte de (0, r0) con
    velocidad tangencial v_frac * v_circular(r0). Corta al impactar
    (|r| < 1) o al completar la vuelta. Devuelve (N, 2)."""
    v_circ = math.sqrt(1.0 / r0)
    pos = np.array([0.0, r0])
    vel = np.array([v_frac * v_circ, 0.0])

    def acc(p):
        r3 = max(np.linalg.norm(p) ** 3, _EPS)
        return -p / r3

    puntos = [pos.copy()]
    ang_acum = 0.0
    for _ in range(pasos):
        k1v = acc(pos)
        k1p = vel
        k2v = acc(pos + 0.5 * dt * k1p)
        k2p = vel + 0.5 * dt * k1v
        k3v = acc(pos + 0.5 * dt * k2p)
        k3p = vel + 0.5 * dt * k2v
        k4v = acc(pos + dt * k3p)
        k4p = vel + dt * k3v
        pos_nueva = pos + dt / 6.0 * (k1p + 2 * k2p + 2 * k3p + k4p)
        vel = vel + dt / 6.0 * (k1v + 2 * k2v + 2 * k3v + k4v)
        cruz_z = pos[0] * pos_nueva[1] - pos[1] * pos_nueva[0]
        ang = math.atan2(cruz_z, float(np.dot(pos, pos_nueva)))
        ang_acum += abs(ang)
        pos = pos_nueva
        puntos.append(pos.copy())
        if np.linalg.norm(pos) < 1.0:
            break
        if ang_acum >= TAU:
            break
    return np.array(puntos)


class CanonNewton(VGroup):
    """Tierra + monte; `.trayectoria(v_frac)` integra y dibuja."""

    def __init__(self, ancla, tierra, monte, params, **kwargs):
        super().__init__(ancla, tierra, monte, **kwargs)
        self._ancla = ancla            # centro de la Tierra
        self.tierra = tierra
        self.monte = monte
        self._params = params

    def trayectoria(self, v_frac, color=COLOR_PROPELENTE, grosor=2.4,
                    pasos=8000, dt=0.002):
        """La curva balistica REAL para v_frac de la velocidad circular
        del monte, sobre la geometria ACTUAL. Con v_frac=1.0 cierra la
        orbita; con menos, cae. Devuelve un VMobject."""
        pasos = _validar("canon_newton.pasos", pasos, PASOS_MAX)
        nucleo = _nucleo_canon(float(v_frac), self._params["r_monte"],
                               pasos, float(dt))
        esc = 0.5 * self.tierra.width   # radio actual = 1 en el nucleo
        centro = self._ancla.get_center()
        pts = [centro + esc * np.array([p[0], p[1], 0.0]) for p in nucleo]
        return _poligonal(pts, color, grosor)

    def cima(self):
        """El punto de disparo (la cima del monte), geometria ACTUAL."""
        esc = 0.5 * self.tierra.width
        return (self._ancla.get_center()
                + UP * esc * self._params["r_monte"])

    def v_orbital_kms(self):
        """La cifra real que se rotula: v circular a 200 km, en km/s."""
        return v_orbital() / 1000.0


def canon_newton(radio_escena=2.15, r_monte=1.16, color_tierra=COLOR_TIERRA):
    """El experimento mental de Newton con balistica de verdad.

    La Tierra a `radio_escena`; el monte a r_monte radios (exagerado
    para verse: se confiesa en el pie del clip). Las trayectorias se
    integran (RK4, campo 1/r^2) en `trayectoria(v_frac)`.
    """
    radio_escena, r_monte = float(radio_escena), float(r_monte)
    tierra = Circle(radius=radio_escena, color=color_tierra,
                    stroke_width=2.5, fill_color=color_tierra,
                    fill_opacity=0.22)
    base_i = radio_escena * 0.985
    monte = Polygon(UP * base_i + LEFT * radio_escena * 0.07,
                    UP * base_i + RIGHT * radio_escena * 0.07,
                    UP * radio_escena * r_monte,
                    stroke_width=2.2, color=color_tierra)
    params = {"radio_escena": radio_escena, "r_monte": r_monte}
    return CanonNewton(_ancla(ORIGIN), tierra, monte, params)


# =====================================================================
# Barras (con negativos: el SSTO imposible)
# =====================================================================
class BarrasCarga(VGroup):
    """Barras sobre un eje cero; los valores negativos cuelgan en rojo."""

    def __init__(self, ancla, eje, barras, params, **kwargs):
        super().__init__(ancla, eje, barras, **kwargs)
        self._ancla = ancla            # extremo izquierdo del eje cero
        self.eje = eje
        self.barras = barras
        self._params = params
        self.valores = params["valores"]

    def barra(self, i):
        return self.barras[int(i)]

    def tope(self, i):
        """El extremo (arriba si positiva, abajo si negativa) de la
        barra i, geometria ACTUAL: donde va la cifra."""
        b = self.barras[int(i)]
        if self.valores[int(i)] >= 0:
            return b.get_top()
        return b.get_bottom()

    def base(self, i):
        """El pie de la barra i sobre el eje cero (geometria ACTUAL):
        donde va el nombre."""
        b = self.barras[int(i)]
        if self.valores[int(i)] >= 0:
            return b.get_bottom()
        return b.get_top()


def barras_carga(valores, ancho=5.2, alto=2.9, v_max=None,
                 color_pos=COLOR_CARGA, color_neg=COLOR_MUERTO,
                 ancho_barra=0.62):
    """Barras de carga util (en %); las NEGATIVAS cuelgan del eje en
    rojo — el SSTO que no cierra se ve, no se maquilla.

    `valores` es una tupla de numeros (%). El eje cero es horizontal;
    v_max fija la escala (por defecto, el mayor |valor|).
    """
    n = _validar("barras_carga.n", len(valores), BARRAS_MAX)
    valores = tuple(float(v) for v in valores)
    ancho, alto = float(ancho), float(alto)
    if v_max is None:
        v_max = max(abs(v) for v in valores)
    v_max = max(float(v_max), _EPS)

    izquierda = np.array([-ancho / 2.0, 0.0, 0.0])
    eje = Line(izquierda, izquierda + RIGHT * ancho, stroke_width=2.2,
               color=COLOR_EJE)

    paso = ancho / (n + 1)
    barras = VGroup()
    for i, v in enumerate(valores):
        h = alto * 0.5 * abs(v) / v_max
        color = color_pos if v >= 0 else color_neg
        r = Rectangle(width=ancho_barra, height=max(h, 0.02),
                      stroke_width=2.0, color=color,
                      fill_color=color, fill_opacity=0.35)
        x = izquierda[0] + (i + 1) * paso
        if v >= 0:
            r.move_to(np.array([x, h / 2.0, 0.0]))
        else:
            r.move_to(np.array([x, -h / 2.0, 0.0]))
        barras.add(r)

    params = {"valores": valores, "ancho": ancho, "alto": alto,
              "v_max": v_max}
    return BarrasCarga(_ancla(izquierda), eje, barras, params)


# =====================================================================
# La llama del escape
# =====================================================================
def llama_escape(n=18, ancho=0.55, largo=1.1, color=COLOR_PROPELENTE,
                 semilla=3):
    """Abanico determinista de particulas de escape apuntando hacia
    ABAJO desde ORIGIN (el clip lo rota/coloca). Dots con tamanos y
    posiciones sembrados: mismo script, misma llama."""
    n = _validar("llama_escape.n", n, PARTICULAS_MAX)
    rng = np.random.default_rng(int(semilla))
    llama = VGroup()
    for _ in range(n):
        f = rng.random()
        x = (rng.random() - 0.5) * float(ancho) * (0.4 + 0.6 * f)
        y = -f * float(largo)
        d = Dot(np.array([x, y, 0.0]),
                radius=0.028 + 0.05 * rng.random() * (1.0 - 0.6 * f),
                color=color)
        d.set_opacity(0.9 - 0.55 * f)
        llama.add(d)
    return llama
