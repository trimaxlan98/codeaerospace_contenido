"""Calculo vectorial: el espacio que fluye.

Libreria de la familia de cursos "Calculo vectorial" (curso 23). Si
Algebra lineal fue *la rejilla que se mueve*, esto es *el espacio que
fluye*: el paisaje escalar con sus curvas de nivel, el gradiente que sube
la colina, el campo lleno de flechas, las particulas que siguen la
corriente, la ruedecita que gira donde hay rotacional, la cajita que se
vacia donde la divergencia es negativa, y los grandes teoremas
COMPROBADOS con numeros medidos (los dos lados de Green dan lo mismo).

Se apoya en `algebra_lineal` (mismo sys.path): el plano con rejilla, el
espacio3 en proyeccion oblicua, `vector`, `flecha_libre` y la paleta de
la marca. Todo el calculo es numpy puro y determinista — sin red, sin
disco, sin azar — condicion necesaria para `--disable_caching`.

Regla de color de la familia: **el color dice el papel**.

    gradiente  ambar   la direccion privilegiada: grad f, la normal n
    cifra      cian    cifras calculadas, tangentes
    campo      azul    las flechas del campo (la magnitud las gradua)
    vec        rojo    la particula / el camino protagonista
    res        verde   el resultado medido: trabajo, flujo, ambos lados
    flujo      fucsia  lineas de flujo / corriente
    region     naranja la region de integracion y su borde
    (frio->calido: color_calor(t) gradua alturas y magnitudes)

Numeros (todo rotulo con cifra sale de aqui, nunca escrito a mano):
    parcial / grad_num             derivadas centrales
    div_num / rot_num / rot3_num   divergencia y rotacional numericos
    integral_linea                 trabajo por Simpson sobre r(t)
    integral_linea_escalar         longitud/masa: f ds
    circulacion / flujo_curva      la cerrada: F.dr y F.n ds (2D)
    integral_doble                 malla de puntos medios
    flujo_caja3 / flujo_parche     flujo 3D por caras / parche parametrico
    potencial_comprobado           max |grad(phi) - F| en una malla (~0)
    velocidad_luz                  c calculada de mu0 y eps0

Catalogo cerrado de paisajes y campos (con cifras cabeza):
    paisaje_colinas / paisaje_silla / paisaje_valle
    campo_radial (div 2, rot 0)    campo_rotor (div 0, rot 2)
    campo_silla (0, 0)             campo_cizalla (0, -1)
    campo_viento / campo_remolino  (para retratos de flujo)
    campo_gravedad (conservativo; phi_gravedad)
    campo_fuente  (div 0 fuera del origen; flujo 2*pi si encierra)
    campo_dipolo  (div 0 exacto: sale de una funcion de corriente)
    campo_gradiente(f)             el campo grad f de un paisaje
    phi_demo / F_demo              x^2*y y su gradiente (trabajo A->B = 4)
    circulo / camino_recta / camino_arco / camino_escalera  r(t) de demo

Piezas 2D (sobre `plano` de algebra_lineal; crear DESPUES de colocarlo):
    campo_flechas    malla de flechas, color por |F|; .con_campo(G) gemelo
    curvas_nivel     marching squares; .curva(i), .niveles
    linea_flujo      streamline RK4; .puntos; sirve a Create y MoveAlongPath
    camino           curva parametrica; .punto(t), .tangente(t), .normal(t)
    rueda            ruedecita de paletas; girar .aspas sobre .centro()
    caja_conteo      cajita contable de la divergencia; .flujo, .flujos_lados
    region_rect      region sombreada + borde orientado; .curva es su r(t)
    normales_borde   flechitas n hacia fuera a lo largo de una cerrada
    mosaico_circulaciones   baldosas con circulacion (Green se cancela)
Piezas 3D (sobre `espacio3`):
    superficie3      malla de alambre z = f(x, y), color por altura
    plano_corte3 / curva_corte3   la rebanada y = cte (o x = cte)
    curva_nivel3     la curva de nivel f = nivel, dibujada a su altura
    flechas3         campo 3D disperso
    parche3          parche parametrico + normales ambar; .normal_en(u, v)
    cubo_flujo3      el cubo con sus 6 flujos medidos; .flujos, .total
    onda_em          E (ambar, en z) y B (cian, en y); .con_fase(t) gemelo

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from calculo_vectorial import *
    pl = plano(unidad=0.9); pl.move_to(DOWN * 0.15)
    campo = campo_flechas(pl, campo_rotor)
    self.add(pl.fijo, pl.ejes, campo)
"""

import numpy as np
from manim import (PI, Arrow, Circle, Dot, Line, ManimColor, Polygon,
                   Triangle, VGroup, VMobject, interpolate_color)

from algebra_lineal import (C_AREA, C_EJE, C_I, C_IMG, C_J, C_K, C_PROPIO,
                            C_REJILLA, C_VEC, C_VIVA, fmt, flecha_libre,
                            grafica, plano, espacio3, vector)

# --- roles de la familia ------------------------------------------------
C_GRAD = C_I          # ambar: gradiente, normal, direccion estrella
C_CIFRA = C_J         # cian: cifras y tangentes
C_CAMPO = C_VIVA      # azul: flechas del campo
C_RES = C_IMG         # verde: el resultado medido
C_FLUJO = C_PROPIO    # fucsia: lineas de flujo
C_REGION = C_AREA     # naranja: la region y su borde

_CALOR = [ManimColor(c) for c in
          ("#1d4ed8", "#3b82f6", "#22d3ee", "#34d399", "#f59e0b")]


def color_calor(t):
    """t en [0, 1] -> color frio->calido de la marca (azul -> ambar)."""
    t = float(np.clip(t, 0.0, 1.0)) * (len(_CALOR) - 1)
    i = min(int(t), len(_CALOR) - 2)
    return interpolate_color(_CALOR[i], _CALOR[i + 1], t - i)


def _v(p, n=2):
    a = np.asarray(p, dtype=float).reshape(-1)
    if len(a) != n:
        raise ValueError(f"se esperaba un vector de {n} componentes")
    return a


# =====================================================================
# Numeros: derivadas
# =====================================================================
def parcial(f, p, i, h=1e-5):
    """Derivada parcial central de f (escalar) respecto de la coordenada i."""
    p = np.asarray(p, dtype=float)
    e = np.zeros_like(p)
    e[i] = h
    return float(f(p + e) - f(p - e)) / (2 * h)


def grad_num(f, p, h=1e-5):
    """Gradiente numerico de un campo escalar (2D o 3D)."""
    p = np.asarray(p, dtype=float)
    return np.array([parcial(f, p, i, h) for i in range(len(p))])


def div_num(F, p, h=1e-5):
    """Divergencia numerica de un campo vectorial (2D o 3D)."""
    p = np.asarray(p, dtype=float)
    total = 0.0
    for i in range(len(p)):
        e = np.zeros_like(p)
        e[i] = h
        total += (F(p + e)[i] - F(p - e)[i]) / (2 * h)
    return float(total)


def rot_num(F, p, h=1e-5):
    """Rotacional escalar 2D: dFy/dx - dFx/dy."""
    p = _v(p)
    ex, ey = np.array([h, 0.0]), np.array([0.0, h])
    dfy_dx = (F(p + ex)[1] - F(p - ex)[1]) / (2 * h)
    dfx_dy = (F(p + ey)[0] - F(p - ey)[0]) / (2 * h)
    return float(dfy_dx - dfx_dy)


def rot3_num(F, p, h=1e-5):
    """Rotacional 3D (vector) por diferencias centrales."""
    p = _v(p, 3)

    def d(comp, eje):
        e = np.zeros(3)
        e[eje] = h
        return (F(p + e)[comp] - F(p - e)[comp]) / (2 * h)

    return np.array([d(2, 1) - d(1, 2), d(0, 2) - d(2, 0), d(1, 0) - d(0, 1)])


# =====================================================================
# Numeros: integrales
# =====================================================================
def _r_prima(r, t, h=1e-6):
    return (np.asarray(r(t + h), float) - np.asarray(r(t - h), float)) / (2 * h)


def _simpson(g, a, b, n):
    n = int(n) + (int(n) % 2)          # par
    t = np.linspace(a, b, n + 1)
    y = np.array([g(ti) for ti in t])
    w = np.ones(n + 1)
    w[1:-1:2], w[2:-1:2] = 4.0, 2.0
    return float((b - a) / (3 * n) * (w * y.T).sum(axis=-1))


def integral_linea(F, r, a=0.0, b=1.0, n=2000):
    """Trabajo: integral de F(r(t)) . r'(t) dt por Simpson."""
    return _simpson(lambda t: float(np.dot(F(np.asarray(r(t), float)),
                                           _r_prima(r, t))), a, b, n)


def integral_linea_escalar(f, r, a=0.0, b=1.0, n=2000):
    """Integral de f ds (f escalar) a lo largo de r(t)."""
    return _simpson(lambda t: float(f(np.asarray(r(t), float)))
                    * float(np.linalg.norm(_r_prima(r, t))), a, b, n)


def circulacion(F, r, a=0.0, b=1.0, n=4000):
    """La integral de linea sobre una curva CERRADA (r(a) = r(b))."""
    return integral_linea(F, r, a, b, n)


def flujo_curva(F, r, a=0.0, b=1.0, n=4000):
    """Flujo 2D por una cerrada recorrida antihoraria: F . n ds, con
    n = (y', -x')/|r'| la normal EXTERIOR."""
    def g(t):
        rp = _r_prima(r, t)
        Ft = F(np.asarray(r(t), float))
        return float(Ft[0] * rp[1] - Ft[1] * rp[0])
    return _simpson(g, a, b, n)


def integral_doble(g, x0, x1, y0, y1, n=400):
    """Integral doble de g(p) sobre el rectangulo, por puntos medios."""
    xs = np.linspace(x0, x1, n + 1)
    ys = np.linspace(y0, y1, n + 1)
    cx = (xs[:-1] + xs[1:]) / 2
    cy = (ys[:-1] + ys[1:]) / 2
    dx, dy = (x1 - x0) / n, (y1 - y0) / n
    total = 0.0
    for y in cy:
        fila = np.array([g(np.array([x, y])) for x in cx])
        total += fila.sum()
    return float(total * dx * dy)


_CARAS3 = (("x", +1), ("x", -1), ("y", +1), ("y", -1), ("z", +1), ("z", -1))


def flujo_caja3(F, esquina=(0.0, 0.0, 0.0), lado=1.0, n=24):
    """Flujo de F por las 6 caras del cubo [esquina, esquina+lado]^3.
    Devuelve (total, [flujo por cara en el orden +x -x +y -y +z -z])."""
    e = _v(esquina, 3)
    ejes = {"x": 0, "y": 1, "z": 2}
    u = np.linspace(0, lado, n + 1)
    c = (u[:-1] + u[1:]) / 2
    dA = (lado / n) ** 2
    flujos = []
    for eje, signo in _CARAS3:
        k = ejes[eje]
        i, j = [d for d in range(3) if d != k]
        total = 0.0
        for a in c:
            for b in c:
                p = e.copy()
                p[k] += lado if signo > 0 else 0.0
                p[i] += a
                p[j] += b
                total += F(p)[k] * signo
        flujos.append(float(total * dA))
    return float(sum(flujos)), flujos


def flujo_parche(F, S, u0=0.0, u1=1.0, v0=0.0, v1=1.0, n=120):
    """Flujo de F por el parche S(u, v): integral de F . (Su x Sv) du dv."""
    us = np.linspace(u0, u1, n + 1)
    vs = np.linspace(v0, v1, n + 1)
    cu = (us[:-1] + us[1:]) / 2
    cv = (vs[:-1] + vs[1:]) / 2
    du, dv = (u1 - u0) / n, (v1 - v0) / n
    h = 1e-6
    total = 0.0
    for uu in cu:
        for vv in cv:
            Su = (np.asarray(S(uu + h, vv), float)
                  - np.asarray(S(uu - h, vv), float)) / (2 * h)
            Sv = (np.asarray(S(uu, vv + h), float)
                  - np.asarray(S(uu, vv - h), float)) / (2 * h)
            total += float(np.dot(F(np.asarray(S(uu, vv), float)),
                                  np.cross(Su, Sv)))
    return float(total * du * dv)


def potencial_comprobado(F, phi, x0=-2.0, x1=2.0, y0=-2.0, y1=2.0, n=15):
    """max |grad(phi) - F| sobre una malla: ~0 si phi es potencial de F."""
    peor = 0.0
    for x in np.linspace(x0, x1, n):
        for y in np.linspace(y0, y1, n):
            p = np.array([x, y])
            peor = max(peor, float(np.linalg.norm(grad_num(phi, p) - F(p))))
    return peor


MU0 = 4e-7 * np.pi
EPS0 = 8.8541878128e-12


def velocidad_luz():
    """c calculada de mu0 y eps0 (m/s)."""
    return float(1.0 / np.sqrt(MU0 * EPS0))


# =====================================================================
# Catalogo: paisajes
# =====================================================================
def paisaje_colinas(p):
    """Dos colinas suaves (la del molde 1.1); alturas 0..~2.2."""
    x, y = _v(p)
    return (2.2 * np.exp(-((x - 1.2) ** 2 + (y - 0.8) ** 2) / 2.6)
            + 1.4 * np.exp(-((x + 1.8) ** 2 + (y + 1.2) ** 2) / 3.0))


def paisaje_silla(p):
    x, y = _v(p)
    return (x ** 2 - y ** 2) / 4.0


def paisaje_valle(p):
    x, y = _v(p)
    return (x ** 2 + y ** 2) / 6.0


# =====================================================================
# Catalogo: campos 2D
# =====================================================================
def campo_radial(p):
    return _v(p).copy()


def campo_rotor(p):
    x, y = _v(p)
    return np.array([-y, x])


def campo_silla(p):
    x, y = _v(p)
    return np.array([x, -y])


def campo_cizalla(p):
    x, y = _v(p)
    return np.array([y, 0.0])


def campo_viento(p):
    """Viento suave de izquierda a derecha con ondulacion (para retratos)."""
    x, y = _v(p)
    return np.array([1.0 + 0.35 * np.sin(0.9 * y), 0.45 * np.sin(0.8 * x)])


_A_REMOLINO = np.array([[-0.22, -1.0], [1.0, -0.22]])


def campo_remolino(p):
    """Remolino amortiguado (espiral hacia dentro): div < 0, rot > 0."""
    return _A_REMOLINO @ _v(p)


def campo_gravedad(p, eps=0.35):
    """Atraccion hacia el origen, suavizada: F = -p / (r^2+eps^2)^(3/2).
    Conservativo EXACTO: F = grad(phi_gravedad)."""
    p = _v(p)
    d = (p @ p + eps * eps) ** 1.5
    return -p / d


def phi_gravedad(p, eps=0.35):
    p = _v(p)
    return float(1.0 / np.sqrt(p @ p + eps * eps))


def campo_fuente(p, eps=1e-9):
    """La fuente puntual 2D: F = p/|p|^2. div = 0 fuera del origen; el
    flujo por cualquier cerrada que encierre el origen es 2*pi."""
    p = _v(p)
    return p / (p @ p + eps)


def campo_dipolo(p, c=0.4):
    """Dipolo 2D con lineas CERRADAS, div = 0 exacto (sale de la funcion
    de corriente psi = y / (x^2 + y^2 + c))."""
    x, y = _v(p)
    D = x * x + y * y + c
    return np.array([(x * x - y * y + c) / D ** 2, 2 * x * y / D ** 2])


def campo_gradiente(f, h=1e-5):
    """El campo grad f de un paisaje."""
    return lambda p: grad_num(f, p, h)


def phi_demo(p):
    """El potencial de demostracion: phi = x^2 y  (trabajo (0,0)->(2,1) = 4)."""
    x, y = _v(p)
    return x * x * y


def F_demo(p):
    """grad(phi_demo) = (2xy, x^2), analitico."""
    x, y = _v(p)
    return np.array([2 * x * y, x * x])


# --- campos 3D --------------------------------------------------------
def campo_radial3(p):
    return _v(p, 3).copy()


def campo_rotor3(p):
    x, y, z = _v(p, 3)
    return np.array([-y, x, 0.0])


# --- curvas r(t) de demostracion --------------------------------------
def circulo(centro=(0.0, 0.0), radio=1.5):
    """r(t), t en [0,1], antihorario."""
    c = _v(centro)
    return lambda t: c + radio * np.array([np.cos(2 * PI * t),
                                           np.sin(2 * PI * t)])


def camino_recta(A, B):
    A, B = _v(A), _v(B)
    return lambda t: A + t * (B - A)


def camino_arco(A, B, comba=1.0):
    """De A a B combando en perpendicular (comba > 0: a la izquierda)."""
    A, B = _v(A), _v(B)
    n = np.array([-(B - A)[1], (B - A)[0]])
    n = n / max(1e-12, np.linalg.norm(n))
    return lambda t: A + t * (B - A) + comba * np.sin(PI * t) * n


def camino_escalera(A, B, peldanos=4):
    """De A a B en escalones eje a eje (primero x, luego y, alternando)."""
    A, B = _v(A), _v(B)
    k = int(peldanos)

    def r(t):
        t = float(np.clip(t, 0.0, 1.0))
        s = t * k
        i = min(int(s), k - 1)
        u = s - i
        p0 = A + (B - A) * (i / k)
        p1 = A + (B - A) * ((i + 1) / k)
        if u < 0.5:
            return np.array([p0[0] + (p1[0] - p0[0]) * (u * 2), p0[1]])
        return np.array([p1[0], p0[1] + (p1[1] - p0[1]) * ((u - 0.5) * 2)])

    return r


# =====================================================================
# Piezas 2D
# =====================================================================
def _flecha(a, b, color, grosor=2.6, punta=0.11, opacidad=1.0):
    largo = float(np.linalg.norm(np.asarray(b) - np.asarray(a)))
    if largo < 1e-6:
        return Dot(a, radius=0.02, color=color, fill_opacity=opacidad)
    fl = Arrow(a, b, buff=0.0, color=color, stroke_width=grosor,
               tip_length=min(punta, 0.55 * largo),
               max_tip_length_to_length_ratio=0.5,
               max_stroke_width_to_length_ratio=40)
    fl.set_opacity(opacidad)
    return fl


class CampoFlechas(VGroup):
    """Malla de flechas del campo F sobre el plano. Color y tamano por
    magnitud (percentil 90 de la malla como referencia, o `magnitud_max`).
    `.en(x, y)` devuelve la flecha muestreada mas cercana; `.con_campo(G)`
    construye el gemelo con la MISMA malla (para Transform campo->campo)."""

    def __init__(self, pl, F, paso, escala, x0, x1, y0, y1, magnitud_max,
                 grosor, opacidad, **kwargs):
        super().__init__(**kwargs)
        self.plano_ref = pl
        self.F = F
        self.params = (paso, escala, x0, x1, y0, y1, magnitud_max, grosor,
                       opacidad)
        xs = np.arange(x0, x1 + 1e-9, paso)
        ys = np.arange(y0, y1 + 1e-9, paso)
        puntos = [np.array([x, y]) for y in ys for x in xs]
        mags = np.array([np.linalg.norm(F(p)) for p in puntos])
        ref = magnitud_max if magnitud_max else max(1e-9, np.percentile(mags, 90))
        self.magnitud_ref = float(ref)
        self.bases = puntos
        self.flechas = []
        for p, m in zip(puntos, mags):
            t = min(1.0, m / ref)
            largo = escala * (0.25 + 0.75 * t)
            d = F(p) / m if m > 1e-9 else np.array([1.0, 0.0])
            a = pl.p(p - d * largo / 2)
            b = pl.p(p + d * largo / 2)
            fl = _flecha(a, b, color_calor(0.15 + 0.85 * t), grosor=grosor,
                         punta=0.10, opacidad=opacidad if m > 1e-9 else 0.25)
            self.flechas.append(fl)
            self.add(fl)

    def en(self, x, y):
        p = np.array([float(x), float(y)])
        i = int(np.argmin([np.linalg.norm(b - p) for b in self.bases]))
        return self.flechas[i]

    def con_campo(self, G):
        return CampoFlechas(self.plano_ref, G, *self.params)


def campo_flechas(pl, F, paso=1.0, escala=0.5, x0=-4.0, x1=4.0, y0=-3.0,
                  y1=3.0, magnitud_max=None, grosor=2.6, opacidad=0.9):
    return CampoFlechas(pl, F, paso, escala, x0, x1, y0, y1, magnitud_max,
                        grosor, opacidad)


# --- curvas de nivel (marching squares) --------------------------------
def _cruce(pa, va, pb, vb, nivel):
    t = 0.5 if abs(vb - va) < 1e-12 else (nivel - va) / (vb - va)
    return pa + np.clip(t, 0.0, 1.0) * (pb - pa)


def _segmentos_nivel(f, nivel, x0, x1, y0, y1, n):
    xs = np.linspace(x0, x1, n + 1)
    ys = np.linspace(y0, y1, n + 1)
    V = np.array([[f(np.array([x, y])) for x in xs] for y in ys])
    segs = []
    for j in range(n):
        for i in range(n):
            a, b = V[j, i], V[j, i + 1]
            c, d = V[j + 1, i + 1], V[j + 1, i]
            A = np.array([xs[i], ys[j]])
            B = np.array([xs[i + 1], ys[j]])
            C = np.array([xs[i + 1], ys[j + 1]])
            D = np.array([xs[i], ys[j + 1]])
            idx = ((a >= nivel) | ((b >= nivel) << 1)
                   | ((c >= nivel) << 2) | ((d >= nivel) << 3))
            if idx in (0, 15):
                continue
            ab = _cruce(A, a, B, b, nivel)
            bc = _cruce(B, b, C, c, nivel)
            cd = _cruce(C, c, D, d, nivel)
            da = _cruce(D, d, A, a, nivel)
            tabla = {1: [(da, ab)], 2: [(ab, bc)], 3: [(da, bc)],
                     4: [(bc, cd)], 6: [(ab, cd)], 7: [(da, cd)],
                     8: [(cd, da)], 9: [(ab, cd)], 11: [(bc, cd)],
                     12: [(bc, da)], 13: [(ab, bc)], 14: [(da, ab)]}
            if idx in (5, 10):
                centro = (a + b + c + d) / 4 >= nivel
                if (idx == 5) == bool(centro):
                    segs += [(da, cd), (ab, bc)]
                else:
                    segs += [(da, ab), (bc, cd)]
            else:
                segs += tabla[idx]
    return segs


class CurvasNivel(VGroup):
    """Curvas de nivel de f sobre el plano, frio->calido por altura.
    `.niveles` (valores) y `.curva(i)` (el VMobject del nivel i)."""

    def __init__(self, pl, f, niveles, x0, x1, y0, y1, n, grosor, opacidad,
                 **kwargs):
        super().__init__(**kwargs)
        if niveles is None:
            xs = np.linspace(x0, x1, 40)
            ys = np.linspace(y0, y1, 40)
            V = np.array([[f(np.array([x, y])) for x in xs] for y in ys])
            lo, hi = V.min(), V.max()
            niveles = list(lo + (hi - lo) * np.linspace(0.12, 0.92, 7))
        self.niveles = [float(v) for v in niveles]
        self.curvas = []
        vmin, vmax = min(self.niveles), max(self.niveles)
        for v in self.niveles:
            t = 0.5 if vmax - vmin < 1e-12 else (v - vmin) / (vmax - vmin)
            vm = VMobject(stroke_color=color_calor(t), stroke_width=grosor,
                          stroke_opacity=opacidad)
            for (p, q) in _segmentos_nivel(f, v, x0, x1, y0, y1, n):
                vm.start_new_path(pl.p(p))
                vm.add_line_to(pl.p(q))
            self.curvas.append(vm)
            self.add(vm)

    def curva(self, i):
        return self.curvas[i]


def curvas_nivel(pl, f, niveles=None, x0=-4.0, x1=4.0, y0=-3.0, y1=3.0,
                 n=110, grosor=2.4, opacidad=0.9):
    return CurvasNivel(pl, f, niveles, x0, x1, y0, y1, n, grosor, opacidad)


# --- lineas de flujo ---------------------------------------------------
def _rk4(F, p, dt):
    k1 = F(p)
    k2 = F(p + dt / 2 * k1)
    k3 = F(p + dt / 2 * k2)
    k4 = F(p + dt * k3)
    return p + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


class LineaFlujo(VMobject):
    """Streamline RK4 desde p0. `.puntos` son las coordenadas del plano
    (np.array Nx2). El VMobject sirve a Create y a MoveAlongPath."""

    def __init__(self, pl, F, p0, T, dt, color, grosor, limites, opacidad,
                 **kwargs):
        super().__init__(stroke_color=color, stroke_width=grosor,
                         stroke_opacity=opacidad, **kwargs)
        p = _v(p0)
        pts = [p.copy()]
        pasos = max(2, int(T / dt))
        for _ in range(pasos):
            p = _rk4(F, p, dt)
            if (abs(p[0]) > limites[0] or abs(p[1]) > limites[1]
                    or np.linalg.norm(F(p)) < 1e-4):
                pts.append(p.copy())
                break
            pts.append(p.copy())
        self.puntos = np.array(pts)
        self.set_points_as_corners([pl.p(q) for q in pts])


def linea_flujo(pl, F, p0, T=6.0, dt=0.02, color=C_FLUJO, grosor=2.6,
                limites=(4.6, 3.4), opacidad=0.9):
    return LineaFlujo(pl, F, p0, T, dt, color, grosor, limites, opacidad)


# --- caminos parametricos ---------------------------------------------
def _marca_direccion(pl, r, t, color, tam=0.11):
    h = 1e-4
    d = np.asarray(r(t + h), float) - np.asarray(r(t - h), float)
    ang = float(np.arctan2(d[1], d[0]))
    tri = Triangle(color=color, fill_color=color, fill_opacity=1.0,
                   stroke_width=0)
    tri.scale_to_fit_height(2 * tam)
    tri.rotate(ang - PI / 2)
    tri.move_to(pl.p(r(t)))
    return tri


class Camino(VGroup):
    """Curva parametrica r(t) sobre el plano. `.trazo` es el VMobject;
    `.marcas` los triangulitos de direccion. Localizadores en coordenadas:
    `.coords(t)`, `.tangente(t)` (unitaria), `.normal(t)` (exterior si la
    curva va antihoraria); `.punto(t)` ya en pantalla."""

    def __init__(self, pl, r, a, b, color, grosor, n, flechas, opacidad,
                 **kwargs):
        super().__init__(**kwargs)
        self.plano_ref, self.r, self.a, self.b = pl, r, float(a), float(b)
        ts = np.linspace(a, b, n)
        self.trazo = VMobject(stroke_color=color, stroke_width=grosor,
                              stroke_opacity=opacidad)
        self.trazo.set_points_as_corners([pl.p(r(t)) for t in ts])
        self.marcas = VGroup()
        if flechas:
            for t in np.linspace(a, b, flechas + 2)[1:-1]:
                self.marcas.add(_marca_direccion(pl, r, t, color))
        self.add(self.trazo, self.marcas)

    def coords(self, t):
        return np.asarray(self.r(t), float)

    def punto(self, t):
        return self.plano_ref.p(self.coords(t))

    def tangente(self, t, h=1e-5):
        d = self.coords(t + h) - self.coords(t - h)
        return d / max(1e-12, np.linalg.norm(d))

    def normal(self, t):
        tx, ty = self.tangente(t)
        return np.array([ty, -tx])


def camino(pl, r, a=0.0, b=1.0, color=C_VEC, grosor=3.5, n=220, flechas=0,
           opacidad=1.0):
    return Camino(pl, r, a, b, color, grosor, n, flechas, opacidad)


# --- la ruedecita del rotacional --------------------------------------
class Rueda(VGroup):
    """Ruedecita de paletas: aro + aspas. Girarla:
    `Rotate(rueda.aspas, angle=..., about_point=rueda.centro())`.
    La velocidad fisica del giro es rot/2 (radianes por unidad de tiempo)."""

    def __init__(self, pl, p, radio, color, **kwargs):
        super().__init__(**kwargs)
        c = pl.p(_v(p))
        self._c = Dot(c, radius=0.001, fill_opacity=0.0, stroke_opacity=0.0)
        aro = Circle(radius=radio, color=color, stroke_width=2.4,
                     stroke_opacity=0.9).move_to(c)
        self.aspas = VGroup()
        for k in range(4):
            ang = k * PI / 4
            d = radio * np.array([np.cos(ang), np.sin(ang), 0.0])
            self.aspas.add(Line(c - d, c + d, color=color, stroke_width=3.0))
        eje = Dot(c, radius=0.05, color=color)
        self.add(self._c, aro, self.aspas, eje)

    def centro(self):
        return self._c.get_center()


def rueda(pl, p, radio=0.42, color=C_CIFRA):
    return Rueda(pl, p, radio, color)


# --- la cajita contable de la divergencia ------------------------------
class CajaConteo(VGroup):
    """Cajita centrada en p: borde naranja + una flecha por lado con la
    componente normal de F (verde si sale, rojo si entra). `.flujo` es el
    flujo medido por el contorno; `.div` el promedio flujo/area;
    `.flujos_lados` en el orden derecha, arriba, izquierda, abajo."""

    def __init__(self, pl, F, p, lado, escala, **kwargs):
        super().__init__(**kwargs)
        p = _v(p)
        m = lado / 2
        esquinas = [p + np.array(d) for d in
                    ((-m, -m), (m, -m), (m, m), (-m, m))]
        self.add(Polygon(*[pl.p(q) for q in esquinas], color=C_REGION,
                         stroke_width=2.6, fill_opacity=0.08,
                         fill_color=C_REGION))
        normales = [np.array([1.0, 0]), np.array([0, 1.0]),
                    np.array([-1.0, 0]), np.array([0, -1.0])]
        self.flechas = VGroup()
        for nrm in normales:
            q = p + nrm * m
            comp = float(np.dot(F(q), nrm))
            color = C_RES if comp >= 0 else C_VEC
            fin = q + nrm * escala * comp
            self.flechas.add(_flecha(pl.p(q), pl.p(fin), color, grosor=3.2,
                                     punta=0.12))
        self.add(self.flechas)

        def borde(t):
            t = (t % 1.0) * 4
            i = min(int(t), 3)
            u = t - i
            A, B = esquinas[i], esquinas[(i + 1) % 4]
            return A + u * (B - A)

        self.flujo = flujo_curva(F, borde, n=2000)
        self.div = self.flujo / (lado * lado)
        self.flujos_lados = []
        for nrm in normales:
            def cara(u, nrm=nrm):
                tang = np.array([-nrm[1], nrm[0]])
                return p + nrm * m + (u - 0.5) * lado * tang
            v = _simpson(lambda u, nrm=nrm, cara=cara:
                         float(np.dot(F(cara(u)), nrm)) * lado, 0, 1, 400)
            self.flujos_lados.append(v)


def caja_conteo(pl, F, p, lado=1.2, escala=0.35):
    return CajaConteo(pl, F, p, lado, escala)


# --- regiones y bordes -------------------------------------------------
class RegionRect(VGroup):
    """Rectangulo sombreado con borde orientado antihorario. `.curva` es
    su r(t) (t en [0,1]) para circulacion/flujo; `.borde` el contorno,
    `.marcas` las flechitas de direccion."""

    def __init__(self, pl, x0, x1, y0, y1, color, opacidad, flechas,
                 **kwargs):
        super().__init__(**kwargs)
        es = [np.array([x0, y0]), np.array([x1, y0]),
              np.array([x1, y1]), np.array([x0, y1])]
        self.esquinas = es
        self.relleno = Polygon(*[pl.p(q) for q in es], stroke_width=0,
                               fill_color=color, fill_opacity=opacidad)
        self.borde = Polygon(*[pl.p(q) for q in es], stroke_color=color,
                             stroke_width=3.0, fill_opacity=0)

        per = [np.linalg.norm(es[(i + 1) % 4] - es[i]) for i in range(4)]
        total = sum(per)

        def r(t):
            s = (t % 1.0) * total
            for i in range(4):
                if s <= per[i] or i == 3:
                    u = s / per[i]
                    return es[i] + np.clip(u, 0, 1) * (es[(i + 1) % 4] - es[i])
                s -= per[i]

        self.curva = r
        self.marcas = VGroup()
        if flechas:
            for t in np.linspace(0, 1, flechas + 1)[:-1]:
                self.marcas.add(_marca_direccion(pl, r, t + 0.03, color))
        self.add(self.relleno, self.borde, self.marcas)


def region_rect(pl, x0, x1, y0, y1, color=C_REGION, opacidad=0.16,
                flechas=6):
    return RegionRect(pl, x0, x1, y0, y1, color, opacidad, flechas)


def normales_borde(pl, r, a=0.0, b=1.0, n=12, largo=0.5, color=C_GRAD):
    """Flechitas n (exterior, curva antihoraria) a lo largo de r(t)."""
    grupo = VGroup()
    h = 1e-5
    for t in np.linspace(a, b, n + 1)[:-1]:
        d = np.asarray(r(t + h), float) - np.asarray(r(t - h), float)
        d = d / max(1e-12, np.linalg.norm(d))
        nrm = np.array([d[1], -d[0]])
        q = np.asarray(r(t), float)
        grupo.add(_flecha(pl.p(q), pl.p(q + nrm * largo), color, grosor=2.8,
                          punta=0.11))
    return grupo


def mosaico_circulaciones(pl, x0, x1, y0, y1, nx=4, ny=2, color=C_REGION,
                          margen=0.12):
    """Baldosas con su circulacion antihoraria dibujada (3 triangulitos por
    baldosa): la imagen de Green antes de cancelar. Devuelve un VGroup de
    baldosas; `mosaico[j*nx+i]` es la baldosa (i, j)."""
    grupo = VGroup()
    dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
    for j in range(ny):
        for i in range(nx):
            bx0, by0 = x0 + i * dx + margen, y0 + j * dy + margen
            bx1, by1 = x0 + (i + 1) * dx - margen, y0 + (j + 1) * dy - margen
            baldosa = RegionRect(pl, bx0, bx1, by0, by1, color, 0.06, 3)
            grupo.add(baldosa)
    return grupo


# =====================================================================
# Piezas 3D (sobre espacio3)
# =====================================================================
class Superficie3(VGroup):
    """Malla de alambre z = f(x, y) sobre el espacio3, color por altura.
    `.z(x, y)` evalua f; `.lineas` son las polilineas."""

    def __init__(self, esp, f, x0, x1, y0, y1, n, grosor, opacidad,
                 **kwargs):
        super().__init__(**kwargs)
        self.f = f
        xs = np.linspace(x0, x1, n)
        ys = np.linspace(y0, y1, n)
        Z = np.array([[f(np.array([x, y])) for x in xs] for y in ys])
        zmin, zmax = float(Z.min()), float(Z.max())
        rango = max(1e-9, zmax - zmin)
        self.lineas = VGroup()
        for j, y in enumerate(ys):
            t = (float(Z[j].mean()) - zmin) / rango
            vm = VMobject(stroke_color=color_calor(t), stroke_width=grosor,
                          stroke_opacity=opacidad)
            vm.set_points_as_corners([esp.p(x, y, Z[j, i])
                                      for i, x in enumerate(xs)])
            self.lineas.add(vm)
        for i, x in enumerate(xs):
            t = (float(Z[:, i].mean()) - zmin) / rango
            vm = VMobject(stroke_color=color_calor(t), stroke_width=grosor,
                          stroke_opacity=opacidad)
            vm.set_points_as_corners([esp.p(x, y, Z[j, i])
                                      for j, y in enumerate(ys)])
            self.lineas.add(vm)
        self.add(self.lineas)

    def z(self, x, y):
        return float(self.f(np.array([float(x), float(y)])))


def superficie3(esp, f, x0=-2.6, x1=2.6, y0=-2.6, y1=2.6, n=15, grosor=1.8,
                opacidad=0.85):
    return Superficie3(esp, f, x0, x1, y0, y1, n, grosor, opacidad)


def plano_corte3(esp, eje="y", valor=0.0, x0=-2.6, x1=2.6, z0=0.0, z1=2.6,
                 color=C_CIFRA, opacidad=0.14):
    """La rebanada y = valor (o x = valor): un rectangulo translucido."""
    if eje == "y":
        es = [(x0, valor, z0), (x1, valor, z0), (x1, valor, z1),
              (x0, valor, z1)]
    else:
        es = [(valor, x0, z0), (valor, x1, z0), (valor, x1, z1),
              (valor, x0, z1)]
    return Polygon(*[esp.p(*q) for q in es], stroke_color=color,
                   stroke_width=1.6, stroke_opacity=0.7, fill_color=color,
                   fill_opacity=opacidad)


def curva_corte3(esp, f, eje="y", valor=0.0, a=-2.6, b=2.6, n=60,
                 color=C_VEC, grosor=3.2):
    """La curva del corte y = valor (o x = valor) sobre la superficie."""
    ts = np.linspace(a, b, n)
    vm = VMobject(stroke_color=color, stroke_width=grosor)
    if eje == "y":
        vm.set_points_as_corners([esp.p(t, valor,
                                        f(np.array([t, valor])))
                                  for t in ts])
    else:
        vm.set_points_as_corners([esp.p(valor, t,
                                        f(np.array([valor, t])))
                                  for t in ts])
    return vm


def curva_nivel3(esp, f, nivel, x0=-2.6, x1=2.6, y0=-2.6, y1=2.6, n=90,
                 color=C_VEC, grosor=3.0, en_altura=True):
    """La curva de nivel f = nivel dibujada EN el espacio3, a su altura
    (o proyectada al suelo con en_altura=False)."""
    z = float(nivel) if en_altura else 0.0
    vm = VMobject(stroke_color=color, stroke_width=grosor)
    for (a, b) in _segmentos_nivel(f, nivel, x0, x1, y0, y1, n):
        vm.start_new_path(esp.p(a[0], a[1], z))
        vm.add_line_to(esp.p(b[0], b[1], z))
    return vm


def flechas3(esp, F, paso=1.4, escala=0.4, rango=2.8, grosor=2.2,
             opacidad=0.8):
    """Campo 3D disperso: una flecha por punto de una malla ligera."""
    grupo = VGroup()
    malla = np.arange(-rango, rango + 1e-9, paso)
    puntos = [np.array([x, y, z]) for x in malla for y in malla
              for z in malla]
    mags = np.array([np.linalg.norm(F(p)) for p in puntos])
    ref = max(1e-9, np.percentile(mags, 90))
    for p, m in zip(puntos, mags):
        if m < 1e-9:
            continue
        t = min(1.0, m / ref)
        d = F(p) / m * escala * (0.3 + 0.7 * t)
        grupo.add(_flecha(esp.p(*(p - d / 2)), esp.p(*(p + d / 2)),
                          color_calor(0.15 + 0.85 * t), grosor=grosor,
                          punta=0.09, opacidad=opacidad))
    return grupo


class Parche3(VGroup):
    """Parche parametrico S(u, v) en alambre + normales ambar.
    `.normal_en(u, v)` devuelve la normal unitaria (coordenadas 3D)."""

    def __init__(self, esp, S, u0, u1, v0, v1, nu, nv, normales, color,
                 grosor, **kwargs):
        super().__init__(**kwargs)
        self.S = S
        us = np.linspace(u0, u1, nu)
        vs = np.linspace(v0, v1, nv)
        self.malla = VGroup()
        for u in us:
            vm = VMobject(stroke_color=color, stroke_width=grosor,
                          stroke_opacity=0.8)
            vm.set_points_as_corners([esp.p(*S(u, v)) for v in vs])
            self.malla.add(vm)
        for v in vs:
            vm = VMobject(stroke_color=color, stroke_width=grosor,
                          stroke_opacity=0.8)
            vm.set_points_as_corners([esp.p(*S(u, v)) for u in us])
            self.malla.add(vm)
        self.add(self.malla)
        self.normales = VGroup()
        if normales:
            for u in np.linspace(u0, u1, normales + 2)[1:-1]:
                for v in np.linspace(v0, v1, normales + 2)[1:-1]:
                    n = self.normal_en(u, v)
                    q = np.asarray(S(u, v), float)
                    self.normales.add(_flecha(esp.p(*q),
                                              esp.p(*(q + 0.55 * n)),
                                              C_GRAD, grosor=2.6,
                                              punta=0.1))
            self.add(self.normales)

    def normal_en(self, u, v, h=1e-5):
        Su = (np.asarray(self.S(u + h, v), float)
              - np.asarray(self.S(u - h, v), float)) / (2 * h)
        Sv = (np.asarray(self.S(u, v + h), float)
              - np.asarray(self.S(u, v - h), float)) / (2 * h)
        n = np.cross(Su, Sv)
        return n / max(1e-12, np.linalg.norm(n))


def parche3(esp, S, u0=0.0, u1=1.0, v0=0.0, v1=1.0, nu=9, nv=9, normales=3,
            color=C_REGION, grosor=1.8):
    return Parche3(esp, S, u0, u1, v0, v1, nu, nv, normales, color, grosor)


class CuboFlujo3(VGroup):
    """El cubo [esquina, esquina+lado]^3 con una flecha de flujo por cara.
    `.flujos` (+x -x +y -y +z -z), `.total` (= integral de la divergencia)."""

    def __init__(self, esp, F, esquina, lado, escala, **kwargs):
        super().__init__(**kwargs)
        e = _v(esquina, 3)
        vs = [e + lado * np.array([i, j, k])
              for i in (0, 1) for j in (0, 1) for k in (0, 1)]
        aristas = [(0, 1), (0, 2), (0, 4), (3, 1), (3, 2), (3, 7), (5, 1),
                   (5, 4), (5, 7), (6, 2), (6, 4), (6, 7)]
        for (i, j) in aristas:
            self.add(Line(esp.p(*vs[i]), esp.p(*vs[j]), color=C_REGION,
                          stroke_width=2.2, stroke_opacity=0.9))
        self.total, self.flujos = flujo_caja3(F, e, lado)
        self.flechas = VGroup()
        ejes = {"x": 0, "y": 1, "z": 2}
        for (nombre, signo), fl in zip(_CARAS3, self.flujos):
            k = ejes[nombre]
            n = np.zeros(3)
            n[k] = signo
            c = e + lado / 2
            c[k] = e[k] + (lado if signo > 0 else 0.0)
            color = C_RES if fl >= 0 else C_VEC
            self.flechas.add(_flecha(esp.p(*c), esp.p(*(c + n * escala
                                                        * abs(fl))),
                                     color, grosor=3.0, punta=0.12))
        self.add(self.flechas)


def cubo_flujo3(esp, F, esquina=(0.0, 0.0, 0.0), lado=1.0, escala=0.6):
    return CuboFlujo3(esp, F, esquina, lado, escala)


class OndaEM(VGroup):
    """La onda plana: E en z (ambar) y B en y (cian), avanzando en x.
    `.con_fase(fase)` construye el gemelo desplazado (para Transform)."""

    def __init__(self, esp, x0, x1, n, k, E0, fase, **kwargs):
        super().__init__(**kwargs)
        self.params = (esp, x0, x1, n, k, E0)
        self.fase = fase
        xs = np.linspace(x0, x1, n)
        self.E = VGroup()
        self.B = VGroup()
        for x in xs:
            v = E0 * np.sin(k * x - fase)
            self.E.add(_flecha(esp.p(x, 0, 0), esp.p(x, 0, v), C_GRAD,
                               grosor=2.4, punta=0.09))
            self.B.add(_flecha(esp.p(x, 0, 0), esp.p(x, 0.62 * v, 0),
                               C_CIFRA, grosor=2.4, punta=0.09))
        env_E = VMobject(stroke_color=C_GRAD, stroke_width=1.6,
                         stroke_opacity=0.55)
        env_E.set_points_as_corners(
            [esp.p(x, 0, E0 * np.sin(k * x - fase)) for x in
             np.linspace(x0, x1, 5 * n)])
        env_B = VMobject(stroke_color=C_CIFRA, stroke_width=1.6,
                         stroke_opacity=0.55)
        env_B.set_points_as_corners(
            [esp.p(x, 0.62 * E0 * np.sin(k * x - fase), 0) for x in
             np.linspace(x0, x1, 5 * n)])
        self.add(self.E, self.B, env_E, env_B)

    def con_fase(self, fase):
        esp, x0, x1, n, k, E0 = self.params
        return OndaEM(esp, x0, x1, n, k, E0, fase)


def onda_em(esp, x0=-2.8, x1=2.8, n=25, k=2.2, E0=1.5, fase=0.0):
    return OndaEM(esp, x0, x1, n, k, E0, fase)
