"""Algebra lineal: la rejilla que se mueve.

Pensada para la familia de cursos "Algebra lineal" (leccion 1.1 en
adelante), MUY visual: la materia se complica por abstracta, asi que aqui
cada idea se VE. La rejilla del plano se deforma de forma continua, los
vectores se estiran y giran, el paralelogramo del determinante se sombrea,
la nube de puntos se acuesta sobre su eje principal. Todo el calculo es
numpy puro y determinista — sin red, sin disco, sin azar (las nubes
"ruidosas" salen de `np.random.default_rng(semilla)` con semilla FIJA) —
condicion necesaria para `--disable_caching`: mismo script, mismo render.

La regla de color de la familia, que es tambien la de esta libreria: **el
color dice el papel**.

    i-sombrero  ambar    primera columna de la matriz y su imagen
    j-sombrero  cian     segunda columna; tambien las CIFRAS calculadas
    k-sombrero  violeta  tercera columna (3D)
    vector      rojo     el vector protagonista, la entrada, los datos
    imagen      verde    lo que sale de la cuenta: Mv, b, la suma
    propio      fucsia   direcciones propias, ejes principales
    area        naranja  el paralelogramo del determinante
    rejilla     gris     la rejilla FIJA de fondo (mobiliario)
    viva        azul     la rejilla que se MUEVE

Numeros (todo rotulo con cifra sale de aqui, nunca escrito a mano):
    fmt                    formato ASCII de un numero ("-0.0" normalizado)
    determinante           np.linalg.det redondeado a 10 decimales
    inversa                np.linalg.inv (ValueError si det = 0)
    rango                  np.linalg.matrix_rank
    nucleo                 base ortonormal del nucleo (SVD)
    imagen_base            base ortonormal de la imagen (SVD)
    proyeccion             (escalar, vector) de v sobre u
    angulo_entre           angulo en grados entre dos vectores
    autos                  (valores, vectores) reales ordenados de mayor a menor
    diagonalizar           P, D, P^-1  (ValueError si no es diagonalizable real)
    potencia               M^n por diagonalizacion o por producto repetido
    fibonacci_matriz       [[1,1],[1,0]]^n y F_n
    minimos_cuadrados      pendiente y ordenada de la recta que mejor ajusta
    nube                   nube de puntos determinista (semilla, n, media, cov)
    telemetria             serie con deriva + ruido (semilla) para ajustar
    ejes_principales       PCA: autovalores/autovectores de la covarianza
    rot2 / cizalla / escala / reflexion / proyeccion_matriz   matrices 2x2
    rot3                   matrices 3x3 de rotacion (x, y, z)
    resolver               x = A^-1 b

Piezas 2D (VGroup con localizadores que siguen move_to/shift, NO scale):
    plano                  rejilla fija (gris) + rejilla viva (azul) + ejes;
                           .p(x, y) coord -> pantalla; .rejilla_con(M);
                           .anim_matriz(M, *vectores); .aplicar(M)
    vector                 flecha desde el origen con etiqueta MathTex;
                           .coords, .punta(), .con_matriz(M), .con_coords(c)
    combinacion            a*u (ambar) + b*v (cian) cola-punta + resultante
    span_recta             la recta generada por u (tenue, larga)
    paralelogramo          la imagen del cuadrado unidad bajo M, sombreada; .area
    paralelogramo_de       el de dos vectores cualesquiera; .area (con signo)
    celdas                 varias celdas de la rejilla sombreadas bajo M
    matriz_columnas        Matrix por columnas coloreadas; .columna(j), .entrada(i, j)
    vector_columna         Matrix de una columna
    puntos_nube            los puntos de una nube sobre el plano
    recta                  una recta y = m x + b sobre el plano; .punto_de(x)
    grafica                una funcion f(x) en su caja de ejes; .punto_de(x)
    marca_angulo           arco de angulo entre dos vectores con su cifra

Piezas 3D minimas (proyeccion oblicua FIJA a 2D, sin ThreeDScene):
    espacio3               ejes x/y/z + rejilla del suelo; .p(x, y, z);
                           .rejilla_con(M); .anim_matriz(M, *vectores)
    vector3                flecha 3D proyectada; .con_matriz(M)
    caja3                  paralelepipedo (imagen del cubo unidad bajo M); .volumen
    plano_generado         parche del plano generado por dos vectores 3D
    satelite3              cubesat de alambre + paneles, con actitud R

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from algebra_lineal import plano, vector, matriz_columnas, cizalla

    pl = plano(unidad=0.8)
    v = vector(pl, (3, 2), color=C_VEC, nombre=r"\\vec v")
    self.add(pl, v)
    M = cizalla(1.0)
    self.play(*pl.anim_matriz(M, v), run_time=2)   # la rejilla y v se mueven
    v = v.con_matriz(M)   # (el clip lleva la cuenta: ver docstring de vector)
"""

import numpy as np

from manim import (Arc, Arrow, DashedLine, Dot, Line, MathTex, Matrix,
                   Polygon, Text, Transform, VGroup, DOWN, LEFT, ORIGIN,
                   RIGHT, UP)

from code_brand import CODE_MUTED, FUENTE_HUD, registrar_fuentes

# --- Paleta por ROL (la misma que el style_block de la familia) -------------
C_I = "#f59e0b"        # ambar: i-sombrero, primera columna
C_J = "#22d3ee"        # cian: j-sombrero, segunda columna, cifras
C_K = "#a78bfa"        # violeta: k-sombrero, tercera columna
C_VEC = "#f43f5e"      # rojo: el vector protagonista / los datos
C_IMG = "#34d399"      # verde: la imagen, el resultado
C_PROPIO = "#e879f9"   # fucsia: direcciones propias, ejes principales
C_AREA = "#fb923c"     # naranja: el paralelogramo del determinante
C_REJILLA = "#31414f"  # gris azulado: rejilla fija (mobiliario)
C_VIVA = "#3b82f6"     # azul: la rejilla que se mueve
C_EJE = CODE_MUTED     # ejes del plano

# Limites duros: pasarse levanta ValueError (VPS con 2 vCPU por render).
ALCANCE_MAX = 16       # semilado de la rejilla, en unidades
PUNTOS_MAX = 400       # puntos de una nube
MUESTRAS_MAX = 400     # muestras de una grafica


# =====================================================================
# Utilidades
# =====================================================================
def fmt(x, dec=1):
    """Numero en ASCII con `dec` decimales; "-0.0" se normaliza a "0.0"."""
    x = float(x)
    if abs(x) < 0.5 * 10 ** (-dec):
        x = 0.0
    return f"{x:.{dec}f}"


def _mat(m):
    m = np.asarray(m, dtype=float)
    if m.ndim != 2 or m.shape[0] != m.shape[1] or m.shape[0] not in (2, 3):
        raise ValueError("se esperaba una matriz cuadrada 2x2 o 3x3")
    return m


def _vec(v, n=None):
    v = np.asarray(v, dtype=float).reshape(-1)
    if n is not None and v.size != n:
        raise ValueError(f"se esperaba un vector de {n} componentes")
    return v


def _decimales(valores):
    """Decimales que hacen falta para no MENTIR: 0 si todo es entero, si no 1
    (o 2 cuando con 1 se perderia una cifra distinta de cero)."""
    valores = np.asarray(valores, dtype=float).reshape(-1)
    if np.allclose(valores, np.round(valores), atol=1e-9):
        return 0
    if np.allclose(valores, np.round(valores, 1), atol=1e-9):
        return 1
    return 2


def _texto_hud(texto, font_size=15, color=C_EJE):
    registrar_fuentes()
    return Text(texto, font=FUENTE_HUD, font_size=font_size, color=color)


# =====================================================================
# Los numeros
# =====================================================================
def determinante(m):
    """det(M) redondeado a 10 decimales (asi det(rot) = 1.0 exacto)."""
    return float(np.round(np.linalg.det(_mat(m)), 10))


def inversa(m):
    """M^-1. Levanta ValueError si det = 0 (mejor que un numero inventado)."""
    m = _mat(m)
    if abs(np.linalg.det(m)) < 1e-12:
        raise ValueError("la matriz no tiene inversa: det = 0")
    return np.linalg.inv(m)


def rango(m):
    return int(np.linalg.matrix_rank(np.asarray(m, dtype=float), tol=1e-9))


def nucleo(m):
    """Base ortonormal del nucleo (columnas). Vacia si M es invertible."""
    m = np.asarray(m, dtype=float)
    _, s, vt = np.linalg.svd(m)
    tol = 1e-9
    r = int(np.sum(s > tol))
    base = vt[r:].T
    # Signo canonico: primera componente no nula positiva.
    for j in range(base.shape[1]):
        col = base[:, j]
        k = np.flatnonzero(np.abs(col) > 1e-12)
        if k.size and col[k[0]] < 0:
            base[:, j] = -col
    return base


def imagen_base(m):
    """Base ortonormal de la imagen (columnas de U que sobreviven)."""
    m = np.asarray(m, dtype=float)
    u, s, _ = np.linalg.svd(m)
    r = int(np.sum(s > 1e-9))
    base = u[:, :r]
    for j in range(base.shape[1]):
        col = base[:, j]
        k = np.flatnonzero(np.abs(col) > 1e-12)
        if k.size and col[k[0]] < 0:
            base[:, j] = -col
    return base


def proyeccion(v, u):
    """(escalar, vector): la sombra de v sobre u. escalar = v.u/|u|;
    vector = (v.u/u.u) u."""
    v, u = _vec(v), _vec(u)
    uu = float(u @ u)
    if uu < 1e-15:
        raise ValueError("no se puede proyectar sobre el vector cero")
    esc = float(v @ u) / np.sqrt(uu)
    return esc, (float(v @ u) / uu) * u


def angulo_entre(u, v):
    """Angulo en grados entre u y v (0..180)."""
    u, v = _vec(u), _vec(v)
    c = float(u @ v) / (np.linalg.norm(u) * np.linalg.norm(v))
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))


def autos(m):
    """(valores, vectores) REALES, ordenados de mayor a menor valor.
    Los vectores son columnas unitarias con primera componente no nula
    positiva. Levanta ValueError si algun autovalor es complejo (una
    rotacion, p. ej.): que el clip lo cuente, no que lo esconda."""
    m = _mat(m)
    val, vec = np.linalg.eig(m)
    if np.any(np.abs(val.imag) > 1e-9):
        raise ValueError("autovalores complejos: la matriz no tiene "
                         "direcciones propias reales")
    val = val.real
    vec = vec.real
    orden = np.argsort(-val)
    val, vec = val[orden], vec[:, orden]
    for j in range(vec.shape[1]):
        col = vec[:, j]
        k = np.flatnonzero(np.abs(col) > 1e-12)
        if k.size and col[k[0]] < 0:
            vec[:, j] = -col
    return val, vec


def diagonalizar(m):
    """P, D, P^-1 con M = P D P^-1 (autovalores reales y P invertible)."""
    val, vec = autos(m)
    if abs(np.linalg.det(vec)) < 1e-9:
        raise ValueError("no diagonalizable: los autovectores no forman base")
    return vec, np.diag(val), np.linalg.inv(vec)


def potencia(m, n):
    """M^n (entero n >= 0) por producto repetido: exacto y sin sorpresas."""
    m = _mat(m)
    if int(n) != n or n < 0:
        raise ValueError("n debe ser un entero no negativo")
    return np.linalg.matrix_power(m, int(n))


def fibonacci_matriz(n):
    """[[1,1],[1,0]]^n y F_n (F_0 = 0, F_1 = 1). Con n = 10, F_10 = 55."""
    q = np.array([[1, 1], [1, 0]], dtype=np.int64)
    qn = np.linalg.matrix_power(q, int(n))
    return qn.astype(float), int(qn[0, 1])


PHI = (1 + np.sqrt(5)) / 2   # 1.6180339887 — el autovalor dominante de Q


def minimos_cuadrados(xs, ys):
    """(pendiente, ordenada) de la recta que minimiza el error cuadratico:
    la proyeccion de y sobre el plano generado por [x, 1]."""
    xs, ys = _vec(xs), _vec(ys)
    a = np.column_stack([xs, np.ones_like(xs)])
    sol, *_ = np.linalg.lstsq(a, ys, rcond=None)
    return float(sol[0]), float(sol[1])


def nube(semilla=7, n=60, media=(0.0, 0.0), cov=((2.0, 1.2), (1.2, 1.0))):
    """Nube gaussiana determinista (n x 2). Semilla FIJA declarada en el
    style_block del clip: mismo numero, misma nube."""
    if n > PUNTOS_MAX:
        raise ValueError(f"maximo {PUNTOS_MAX} puntos")
    rng = np.random.default_rng(int(semilla))
    return rng.multivariate_normal(np.asarray(media, float),
                                   np.asarray(cov, float), size=int(n))


def telemetria(semilla=3, n=14, pendiente=0.35, ordenada=-1.2, ruido=0.35,
               x0=0.0, x1=6.5):
    """(xs, ys): una lectura con deriva lineal + ruido gaussiano (semilla
    fija). Sirve para AJUSTAR la recta y comparar con la verdadera."""
    if n > PUNTOS_MAX:
        raise ValueError(f"maximo {PUNTOS_MAX} puntos")
    rng = np.random.default_rng(int(semilla))
    xs = np.linspace(x0, x1, int(n))
    ys = pendiente * xs + ordenada + rng.normal(0.0, ruido, size=int(n))
    return xs, ys


def ejes_principales(puntos):
    """PCA: (valores, vectores, media) de la covarianza de una nube (n x 2
    o n x 3). vectores por columnas, de mayor a menor varianza."""
    p = np.asarray(puntos, dtype=float)
    media = p.mean(axis=0)
    cov = np.cov((p - media).T)
    val, vec = autos(cov)
    return val, vec, media


def rot2(grados):
    t = np.radians(grados)
    return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])


def cizalla(k, eje="x"):
    """Cizalla: [[1,k],[0,1]] (eje x: las filas se deslizan) o su traspuesta."""
    return (np.array([[1.0, k], [0.0, 1.0]]) if eje == "x"
            else np.array([[1.0, 0.0], [k, 1.0]]))


def escala(sx, sy=None):
    sy = sx if sy is None else sy
    return np.array([[sx, 0.0], [0.0, sy]])


def reflexion(eje="x"):
    """Reflexion respecto al eje x, al eje y o a la diagonal y = x."""
    return {"x": np.array([[1.0, 0.0], [0.0, -1.0]]),
            "y": np.array([[-1.0, 0.0], [0.0, 1.0]]),
            "diagonal": np.array([[0.0, 1.0], [1.0, 0.0]])}[eje]


def proyeccion_matriz(u):
    """La matriz que proyecta sobre la recta de u: u u^T / (u.u). Rango 1."""
    u = _vec(u)
    return np.outer(u, u) / float(u @ u)


def rot3(eje, grados):
    """Rotacion 3x3 alrededor de x, y o z (regla de la mano derecha)."""
    t = np.radians(grados)
    c, s = np.cos(t), np.sin(t)
    if eje == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=float)
    if eje == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=float)
    if eje == "z":
        return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)
    raise ValueError("eje debe ser x, y o z")


def resolver(a, b):
    """x = A^-1 b (ValueError si A es singular)."""
    return inversa(a) @ _vec(b)


# =====================================================================
# Base de piezas: el ancla
# =====================================================================
class _Anclada(VGroup):
    """Piezas cuyos localizadores leen la posicion ACTUAL a traves de un
    punto invisible `_ancla` (un Dot de radio 0 y opacidad 0 en el origen
    de construccion). Como el ancla es un submobject, sigue a move_to /
    shift; y como no depende del bounding box, una rejilla que se deforma
    (o una pieza asimetrica) no descoloca nada."""

    def _poner_ancla(self, punto):
        self._ancla = Dot(punto, radius=0.001, fill_opacity=0.0,
                          stroke_opacity=0.0)
        self.add(self._ancla)

    def _origen(self):
        return self._ancla.get_center()


# =====================================================================
# El plano
# =====================================================================
class Plano(_Anclada):
    """Ver `plano()`."""

    def __init__(self, unidad, alcance, x_rango, y_rango, fijo, vivo, ejes,
                 grosor, **kwargs):
        super().__init__(**kwargs)
        self.unidad = float(unidad)
        self.alcance = int(alcance)
        self.x_rango, self.y_rango = x_rango, y_rango
        self.grosor = grosor
        self._poner_ancla(ORIGIN)
        self.M = np.eye(2)
        self.fijo = self._rejilla_fija() if fijo else VGroup()
        self.ejes = self._ejes() if ejes else VGroup()
        self.vivo = self.rejilla_con(np.eye(2)) if vivo else VGroup()
        self.add(self.fijo, self.ejes, self.vivo)

    # -- coordenadas ------------------------------------------------------
    def p(self, x, y=None):
        """Coordenadas (x, y) -> punto de pantalla (sigue a move_to)."""
        if y is None:
            x, y = float(x[0]), float(x[1])
        return self._origen() + self.unidad * np.array([x, y, 0.0])

    def coords_de(self, punto):
        """Punto de pantalla -> coordenadas (x, y) del plano."""
        d = (np.asarray(punto) - self._origen()) / self.unidad
        return np.array([d[0], d[1]])

    # -- rejillas ---------------------------------------------------------
    def _lineas(self, transformar, color, grosor_menor, grosor_eje,
                op_menor, op_eje):
        a = self.alcance
        grupo = VGroup()
        # Verticales x = k, luego horizontales y = k; el orden es fijo para
        # que Transform empareje linea con linea entre dos rejillas.
        for k in range(-a, a + 1):
            for (p0, p1) in (((k, -a), (k, a)), ((-a, k), (a, k))):
                q0 = transformar(np.array(p0, float))
                q1 = transformar(np.array(p1, float))
                eje = (k == 0)
                grupo.add(Line(self.p(q0), self.p(q1), color=color,
                               stroke_width=grosor_eje if eje else grosor_menor,
                               stroke_opacity=op_eje if eje else op_menor))
        return grupo

    def _rejilla_fija(self):
        return self._lineas(lambda q: q, C_REJILLA, 1.2 * self.grosor,
                            1.6 * self.grosor, 0.55, 0.85)

    def _ejes(self):
        a = self.alcance
        ex = Line(self.p(-a, 0), self.p(a, 0), color=C_EJE, stroke_width=1.6,
                  stroke_opacity=0.9)
        ey = Line(self.p(0, -a), self.p(0, a), color=C_EJE, stroke_width=1.6,
                  stroke_opacity=0.9)
        return VGroup(ex, ey)

    def rejilla_con(self, m):
        """La rejilla viva transformada por M (2x2), construida desde la
        rejilla IDENTIDAD: M es la transformacion TOTAL, no la incremental.
        Se usa como destino de un Transform de `.vivo`."""
        m = _mat(m)
        return self._lineas(lambda q: m @ q, C_VIVA, 1.5 * self.grosor,
                            2.6 * self.grosor, 0.75, 1.0)

    def anim_matriz(self, m, *vectores, **kwargs):
        """Animaciones (lista) que llevan la rejilla viva y las flechas
        dadas al estado M: `self.play(*pl.anim_matriz(M, v, w), run_time=2)`.
        Manim interpola los extremos linealmente, asi que la rejilla
        intermedia es exactamente ((1-t) I + t M): linealidad continua.
        Tras el play, actualiza `pl.M`; los `Vector` deben re-crearse con
        `v = v.con_matriz(M)` (el objeto animado guarda coords viejas)."""
        m = _mat(m)
        anims = [Transform(self.vivo, self.rejilla_con(m), **kwargs)]
        for v in vectores:
            anims.append(Transform(v, v.con_matriz(m), **kwargs))
        self.M = m
        return anims

    def aplicar(self, m):
        """Deja la rejilla viva en el estado M sin animar."""
        m = _mat(m)
        self.vivo.become(self.rejilla_con(m))
        self.M = m
        return self

    def punto(self, coords, color=C_VEC, radio=0.07):
        return Dot(self.p(coords), radius=radio, color=color)


def plano(unidad=0.8, alcance=12, x_rango=None, y_rango=None, fijo=True,
          vivo=True, ejes=True, grosor=1.0):
    """El plano de la familia: rejilla fija gris + ejes + rejilla viva azul.

    `unidad` es el tamaño en pantalla de una unidad (0.8 deja 3.4 unidades
    por encima y por debajo del centro con titulo y pie fuera). `alcance`
    lineas a cada lado: 12 basta para que, tras estirar o encoger x3, la
    rejilla siga cubriendo el cuadro. Localizadores: `.p(x, y)`.
    Poner con `.move_to(...)` ANTES de crear vectores sobre el plano."""
    if alcance > ALCANCE_MAX:
        raise ValueError(f"alcance maximo {ALCANCE_MAX}")
    return Plano(unidad, alcance, x_rango, y_rango, fijo, vivo, ejes, grosor)


# =====================================================================
# Vectores
# =====================================================================
class Vector(VGroup):
    """Flecha desde el origen del plano hasta `coords`, con etiqueta.

    Atributos: .flecha, .etiqueta, .coords (np.array), .plano, .color.
    Localizadores: .punta(), .cola(). Gemelos: .con_matriz(M),
    .con_coords(c), .con_nombre(...). Un `Transform(v, v.con_matriz(M))`
    mueve la flecha; el objeto `v` conserva coords VIEJAS: el clip debe
    reasignar `v = v.con_matriz(M)` (o usar ReplacementTransform)."""

    def __init__(self, pl, coords, color, nombre, font_size, grosor,
                 etiqueta_dir, buff_etiqueta, punta_len, **kwargs):
        super().__init__(**kwargs)
        self.plano = pl
        self.coords = _vec(coords, 2)
        self.color_rol = color
        self.nombre = nombre
        self.font_size = font_size
        self.grosor = grosor
        self.etiqueta_dir = etiqueta_dir
        self.buff_etiqueta = buff_etiqueta
        self.punta_len = punta_len
        origen = pl.p(0, 0)
        destino = pl.p(self.coords)
        largo = float(np.linalg.norm(destino - origen))
        if largo < 1e-6:
            # El vector cero: un punto (una flecha sin largo revienta).
            self.flecha = Dot(origen, radius=0.06, color=color)
        else:
            self.flecha = Arrow(origen, destino, buff=0.0, color=color,
                                stroke_width=grosor,
                                tip_length=min(punta_len, 0.6 * largo),
                                max_tip_length_to_length_ratio=0.5,
                                max_stroke_width_to_length_ratio=25)
        self.add(self.flecha)
        self.etiqueta = None
        if nombre is not None:
            self.etiqueta = MathTex(nombre, font_size=font_size, color=color)
            self._colocar_etiqueta()
            self.add(self.etiqueta)

    def _colocar_etiqueta(self):
        d = self.etiqueta_dir
        if d is None:
            v = self.coords
            n = np.linalg.norm(v)
            if n < 1e-9:
                d = UP
            else:
                # Perpendicular a la flecha, hacia el lado "exterior"
                # (arriba-derecha por defecto), para no pisar la flecha.
                perp = np.array([-v[1], v[0], 0.0]) / n
                if perp[1] < 0 or (abs(perp[1]) < 1e-9 and perp[0] < 0):
                    perp = -perp
                d = perp
        self.etiqueta.move_to(self.punta() + self.buff_etiqueta * np.asarray(d)
                              + 0.5 * np.array([self.etiqueta.width * d[0],
                                                self.etiqueta.height * d[1],
                                                0.0]))

    def punta(self):
        return self.plano.p(self.coords)

    def cola(self):
        return self.plano.p(0, 0)

    def largo(self):
        return float(np.linalg.norm(self.coords))

    def _gemelo(self, coords=None, color=None, nombre="__mismo__"):
        return Vector(self.plano,
                      self.coords if coords is None else coords,
                      self.color_rol if color is None else color,
                      self.nombre if nombre == "__mismo__" else nombre,
                      self.font_size, self.grosor, self.etiqueta_dir,
                      self.buff_etiqueta, self.punta_len)

    def con_matriz(self, m, color=None, nombre="__mismo__"):
        """Gemelo con coords M @ coords (misma etiqueta salvo que se cambie)."""
        return self._gemelo(_mat(m) @ self.coords, color, nombre)

    def con_coords(self, coords, color=None, nombre="__mismo__"):
        return self._gemelo(_vec(coords, 2), color, nombre)

    def escalado(self, k, color=None, nombre="__mismo__"):
        return self._gemelo(float(k) * self.coords, color, nombre)


def vector(pl, coords, color=C_VEC, nombre=None, font_size=30, grosor=5.0,
           etiqueta_dir=None, buff_etiqueta=0.22, punta_len=0.22):
    """Flecha desde el origen de `pl` hasta `coords` (unidades del plano).
    `nombre` es TeX (r"\\vec v", r"\\hat{\\imath}", "3\\hat{\\imath}"...);
    `etiqueta_dir` fuerza el lado de la etiqueta (por defecto, perpendicular
    a la flecha, hacia arriba)."""
    return Vector(pl, coords, color, nombre, font_size, grosor, etiqueta_dir,
                  buff_etiqueta, punta_len)


def flecha_libre(pl, desde, hasta, color=C_IMG, grosor=5.0, punta_len=0.22,
                 opacidad=1.0):
    """Flecha entre dos coordenadas del plano (no anclada al origen): sirve
    para 'poner v en la punta de u' al sumar."""
    a, b = pl.p(desde), pl.p(hasta)
    largo = float(np.linalg.norm(b - a))
    if largo < 1e-6:
        return Dot(a, radius=0.06, color=color)
    fl = Arrow(a, b, buff=0.0, color=color, stroke_width=grosor,
               tip_length=min(punta_len, 0.6 * largo),
               max_tip_length_to_length_ratio=0.5,
               max_stroke_width_to_length_ratio=25)
    fl.set_opacity(opacidad)
    return fl


class Combinacion(VGroup):
    """a*u (ambar) desde el origen, b*v (cian) desde la punta de a*u, y la
    resultante (rojo por defecto). .au .bv .res .coords .a .b"""

    def __init__(self, pl, a, u, b, v, color_res, color_u, color_v, grosor,
                 mostrar_res, **kwargs):
        super().__init__(**kwargs)
        u, v = _vec(u, 2), _vec(v, 2)
        self.a, self.b = float(a), float(b)
        self.coords = self.a * u + self.b * v
        self.au = flecha_libre(pl, (0, 0), self.a * u, color=color_u,
                               grosor=grosor)
        self.bv = flecha_libre(pl, self.a * u, self.coords, color=color_v,
                               grosor=grosor)
        self.add(self.au, self.bv)
        self.res = None
        if mostrar_res:
            self.res = flecha_libre(pl, (0, 0), self.coords, color=color_res,
                                    grosor=grosor)
            self.add(self.res)


def combinacion(pl, a, u, b, v, color_res=C_VEC, color_u=C_I, color_v=C_J,
                grosor=4.5, mostrar_res=True):
    """La combinacion lineal a*u + b*v puesta cola-punta sobre el plano."""
    return Combinacion(pl, a, u, b, v, color_res, color_u, color_v, grosor,
                       mostrar_res)


def span_recta(pl, u, color=C_IMG, grosor=2.4, opacidad=0.6, largo=None):
    """La recta generada por u (pasa por el origen, larga)."""
    u = _vec(u, 2)
    n = np.linalg.norm(u)
    if n < 1e-9:
        raise ValueError("el vector cero no genera una recta")
    d = u / n
    L = (pl.alcance * 1.5) if largo is None else largo
    return Line(pl.p(-L * d), pl.p(L * d), color=color, stroke_width=grosor,
                stroke_opacity=opacidad)


def marca_angulo(pl, u, v, radio=0.6, color=C_J, cifra=True, font_size=16):
    """Arco entre u y v (desde u hacia v, el mas corto) con la cifra en
    grados en Space Mono. .arco .texto .grados"""
    u, v = _vec(u, 2), _vec(v, 2)
    a0 = np.degrees(np.arctan2(u[1], u[0]))
    a1 = np.degrees(np.arctan2(v[1], v[0]))
    dif = (a1 - a0 + 180.0) % 360.0 - 180.0
    arco = Arc(radius=radio, start_angle=np.radians(a0),
               angle=np.radians(dif), arc_center=pl.p(0, 0), color=color,
               stroke_width=2.4)
    grupo = VGroup(arco)
    grupo.arco = arco
    grupo.grados = abs(float(dif))
    grupo.texto = None
    if cifra:
        medio = np.radians(a0 + dif / 2)
        pos = pl.p(0, 0) + (radio + 0.32) * np.array([np.cos(medio),
                                                      np.sin(medio), 0.0])
        t = _texto_hud(f"{fmt(abs(dif), 0)} deg", font_size=font_size,
                       color=color)
        t.move_to(pos)
        grupo.texto = t
        grupo.add(t)
    return grupo


def proyeccion_dibujo(pl, v, u, color=C_IMG, color_guia=C_J):
    """La sombra de v sobre la recta de u: la flecha proyectada + la guia
    punteada perpendicular. .sombra .guia .escalar .coords"""
    esc, w = proyeccion(v, u)
    sombra = flecha_libre(pl, (0, 0), w, color=color, grosor=5.0)
    guia = DashedLine(pl.p(v), pl.p(w), color=color_guia, stroke_width=2.0,
                      dash_length=0.1)
    grupo = VGroup(sombra, guia)
    grupo.sombra, grupo.guia = sombra, guia
    grupo.escalar, grupo.coords = esc, w
    return grupo


# =====================================================================
# Areas
# =====================================================================
class Paralelogramo(VGroup):
    """.area (con signo = det), .poligono"""

    def __init__(self, pl, u, v, origen, color, opacidad, borde, **kwargs):
        super().__init__(**kwargs)
        u, v, o = _vec(u, 2), _vec(v, 2), _vec(origen, 2)
        self.area = float(u[0] * v[1] - u[1] * v[0])
        self.poligono = Polygon(pl.p(o), pl.p(o + u), pl.p(o + u + v),
                                pl.p(o + v), color=color, fill_color=color,
                                fill_opacity=opacidad, stroke_width=borde,
                                stroke_opacity=min(1.0, opacidad + 0.35))
        self.add(self.poligono)


def paralelogramo(pl, m, color=C_AREA, opacidad=0.35, borde=2.0):
    """La imagen del cuadrado unidad bajo M: el paralelogramo de sus
    columnas. .area = det(M) (con signo)."""
    m = _mat(m)
    return Paralelogramo(pl, m[:, 0], m[:, 1], (0, 0), color, opacidad,
                         borde)


def paralelogramo_de(pl, u, v, origen=(0, 0), color=C_AREA, opacidad=0.35,
                     borde=2.0):
    """El paralelogramo de dos vectores cualesquiera. .area con signo."""
    return Paralelogramo(pl, u, v, origen, color, opacidad, borde)


def celdas(pl, m, celdas_ij=((0, 0), (1, 0), (0, 1), (1, 1)), color=C_AREA,
           opacidad=0.28):
    """Varias celdas unidad de la rejilla, transformadas por M y
    sombreadas: sirve para 'toda area escala por det'. .area_celda"""
    m = _mat(m)
    grupo = VGroup()
    for (i, j) in celdas_ij:
        grupo.add(Paralelogramo(pl, m[:, 0], m[:, 1], m @ np.array([i, j]),
                                color, opacidad, 1.2))
    grupo.area_celda = determinante(m)
    return grupo


# =====================================================================
# Matrices en pantalla
# =====================================================================
class MatrizColumnas(VGroup):
    """Matrix de manim con columnas coloreadas. .matriz .columna(j)
    .entrada(i, j) .corchetes .valores"""

    def __init__(self, m, colores, dec, font_size, color_corchetes,
                 h_buff, v_buff, **kwargs):
        super().__init__(**kwargs)
        m = np.asarray(m, dtype=float)
        if m.ndim != 2:
            raise ValueError("matriz 2D")
        self.valores = m
        dec = _decimales(m) if dec is None else dec
        celdas_txt = [[fmt(x, dec) for x in fila] for fila in m]
        # h_buff es distancia centro a centro entre columnas: con entradas
        # anchas ("-0.33") 0.9 las pega. Se abre lo justo para dejar aire.
        mas_ancha = max((MathTex(t, font_size=font_size).width
                         for fila in celdas_txt for t in fila), default=0.0)
        h_buff = max(h_buff, mas_ancha + 0.32)
        self.matriz = Matrix(celdas_txt, h_buff=h_buff, v_buff=v_buff,
                             bracket_h_buff=0.18,
                             element_to_mobject_config={"font_size": font_size})
        self.corchetes = self.matriz.get_brackets()
        self.corchetes.set_color(color_corchetes)
        cols = self.matriz.get_columns()
        for j, col in enumerate(cols):
            col.set_color(colores[j % len(colores)])
        self.add(self.matriz)

    def columna(self, j):
        return self.matriz.get_columns()[j]

    def entrada(self, i, j):
        return self.matriz.get_rows()[i][j]

    def fila(self, i):
        return self.matriz.get_rows()[i]


def matriz_columnas(m, colores=(C_I, C_J, C_K), dec=None, font_size=36,
                    color_corchetes=CODE_MUTED, h_buff=0.9, v_buff=0.75):
    """La matriz por columnas de colores: columna 1 = a donde va i-sombrero
    (ambar), columna 2 = j (cian), columna 3 = k (violeta). `dec=None`
    elige solo los decimales necesarios (0 si todo es entero)."""
    return MatrizColumnas(m, colores, dec, font_size, color_corchetes,
                          h_buff, v_buff)


def vector_columna(v, color=C_VEC, dec=None, font_size=36,
                   color_corchetes=CODE_MUTED):
    """[x; y] (o [x; y; z]) en el color del vector."""
    v = _vec(v)
    return MatrizColumnas(v.reshape(-1, 1), (color,), dec, font_size,
                          color_corchetes, 1.05, 0.75)


def matriz_tex(m, dec=None):
    """La matriz como cadena TeX (bmatrix) para incrustar en un MathTex."""
    m = np.asarray(m, dtype=float)
    dec = _decimales(m) if dec is None else dec
    filas = [" & ".join(fmt(x, dec) for x in fila) for fila in m]
    return r"\begin{bmatrix}" + r" \\ ".join(filas) + r"\end{bmatrix}"


# =====================================================================
# Datos sobre el plano
# =====================================================================
def puntos_nube(pl, puntos, color=C_VEC, radio=0.05, opacidad=0.85):
    """Los puntos (n x 2) de una nube como Dots sobre el plano. .puntos"""
    p = np.asarray(puntos, dtype=float)
    grupo = VGroup(*[Dot(pl.p(q), radius=radio, color=color,
                         fill_opacity=opacidad) for q in p])
    grupo.puntos = p
    return grupo


class Recta(VGroup):
    """y = m x + b sobre el plano; .punto_de(x)"""

    def __init__(self, pl, m, b, x0, x1, color, grosor, **kwargs):
        super().__init__(**kwargs)
        self.pl, self.m, self.b = pl, float(m), float(b)
        self.linea = Line(pl.p(x0, self.m * x0 + self.b),
                          pl.p(x1, self.m * x1 + self.b), color=color,
                          stroke_width=grosor)
        self.add(self.linea)

    def punto_de(self, x):
        return self.pl.p(x, self.m * x + self.b)


def recta(pl, m, b, x0=-6.0, x1=6.0, color=C_IMG, grosor=3.0):
    return Recta(pl, m, b, x0, x1, color, grosor)


class Grafica(_Anclada):
    """f(x) en una caja de ejes propia (no el plano). .ejes .curva
    .punto_de(x) .valor(x) .vertical_en(x) .horizontal_en(y)"""

    def __init__(self, f, rango_x, rango_y, ancho, alto, color, muestras,
                 etiqueta_x, etiqueta_y, **kwargs):
        super().__init__(**kwargs)
        if muestras > MUESTRAS_MAX:
            raise ValueError(f"maximo {MUESTRAS_MAX} muestras")
        self.f = f
        self.x0, self.x1 = float(rango_x[0]), float(rango_x[1])
        self.y0, self.y1 = float(rango_y[0]), float(rango_y[1])
        self.ancho, self.alto = float(ancho), float(alto)
        self._poner_ancla(ORIGIN)
        # Ejes en L cruzando en (x0 o 0, y0 o 0) segun donde caiga el 0.
        cx = 0.0 if self.x0 <= 0 <= self.x1 else self.x0
        cy = 0.0 if self.y0 <= 0 <= self.y1 else self.y0
        ex = Line(self._en(self.x0, cy), self._en(self.x1, cy), color=C_EJE,
                  stroke_width=1.8)
        ey = Line(self._en(cx, self.y0), self._en(cx, self.y1), color=C_EJE,
                  stroke_width=1.8)
        self.ejes = VGroup(ex, ey)
        xs = np.linspace(self.x0, self.x1, int(muestras))
        ys = np.array([float(f(x)) for x in xs])
        ys = np.clip(ys, self.y0, self.y1)
        self.curva = VGroup()
        pts = [self._en(x, y) for x, y in zip(xs, ys)]
        # Poligonal (no suave): las graficas de esta familia tienen picos.
        from manim import VMobject
        c = VMobject(color=color, stroke_width=3.0)
        c.set_points_as_corners(pts)
        self.curva = c
        self.add(self.ejes, self.curva)
        if etiqueta_x:
            t = _texto_hud(etiqueta_x, font_size=14)
            t.next_to(ex.get_end(), DOWN, buff=0.14)
            t.shift(LEFT * (t.width / 2 - 0.05))
            self.add(t)
        if etiqueta_y:
            t = _texto_hud(etiqueta_y, font_size=14)
            t.next_to(ey.get_end(), UP, buff=0.14)
            t.shift(RIGHT * max(0.0, t.width / 2 - 0.3))
            self.add(t)

    def _en(self, x, y):
        fx = (x - self.x0) / (self.x1 - self.x0)
        fy = (y - self.y0) / (self.y1 - self.y0)
        return (self._origen() + np.array([(fx - 0.5) * self.ancho,
                                           (fy - 0.5) * self.alto, 0.0]))

    def valor(self, x):
        return float(self.f(x))

    def punto_de(self, x):
        return self._en(x, float(np.clip(self.f(x), self.y0, self.y1)))

    def vertical_en(self, x, color=C_J):
        return DashedLine(self._en(x, self.y0), self._en(x, self.y1),
                          color=color, stroke_width=1.6, dash_length=0.08)

    def horizontal_en(self, y, color=C_J):
        return DashedLine(self._en(self.x0, y), self._en(self.x1, y),
                          color=color, stroke_width=1.6, dash_length=0.08)


def grafica(f, rango_x, rango_y, ancho=5.0, alto=2.8, color=C_J, muestras=161,
            etiqueta_x=None, etiqueta_y=None):
    """Una funcion en su caja de ejes (p. ej. det(A - lambda I) frente a
    lambda). Los ejes cruzan por el 0 si esta en rango."""
    return Grafica(f, rango_x, rango_y, ancho, alto, color, muestras,
                   etiqueta_x, etiqueta_y)


# =====================================================================
# 3D minimo: proyeccion oblicua fija
# =====================================================================
# Camara fija: acimut y elevacion elegidos para que los tres ejes se
# separen bien y el suelo se lea como suelo (validado a ojo en el
# contenedor). Ortografica: paralelas siguen paralelas.
_AZ = np.radians(-38.0)
_EL = np.radians(24.0)
_PROY = np.array([
    [np.cos(_AZ), -np.sin(_AZ), 0.0],
    [np.sin(_AZ) * np.sin(_EL), np.cos(_AZ) * np.sin(_EL), np.cos(_EL)],
])


def proyectar3(v):
    """(x, y, z) -> (X, Y) de pantalla (sin unidad ni origen)."""
    return _PROY @ _vec(v, 3)


class Espacio3(_Anclada):
    """Ver `espacio3()`."""

    def __init__(self, unidad, alcance, ejes, suelo, **kwargs):
        super().__init__(**kwargs)
        self.unidad = float(unidad)
        self.alcance = int(alcance)
        self._poner_ancla(ORIGIN)
        self.M = np.eye(3)
        self.suelo = self.rejilla_con(np.eye(3), fija=True) if suelo else VGroup()
        self.ejes = self._ejes() if ejes else VGroup()
        self.vivo = self.rejilla_con(np.eye(3)) if suelo else VGroup()
        self.add(self.suelo, self.ejes, self.vivo)

    def p(self, x, y=None, z=None):
        if y is None:
            x, y, z = (float(c) for c in x)
        q = _PROY @ np.array([x, y, z], float)
        return self._origen() + self.unidad * np.array([q[0], q[1], 0.0])

    def _ejes(self):
        a = self.alcance
        grupo = VGroup()
        for d, col, nom in ((np.array([1, 0, 0]), C_I, "x"),
                            (np.array([0, 1, 0]), C_J, "y"),
                            (np.array([0, 0, 1]), C_K, "z")):
            l = Line(self.p(-a * d), self.p(a * d), color=col, stroke_width=1.8,
                     stroke_opacity=0.55)
            t = MathTex(nom, font_size=26, color=col)
            t.move_to(self.p(a * d) + 0.28 * (self.p(a * d) - self.p(0, 0, 0))
                      / max(1e-9, np.linalg.norm(self.p(a * d) - self.p(0, 0, 0))))
            grupo.add(l, t)
        return grupo

    def rejilla_con(self, m, fija=False):
        """La rejilla del suelo (z = 0) transformada por M (3x3): las lineas
        x = k y y = k, en el mismo orden siempre (para Transform)."""
        m = _mat(m)
        a = self.alcance
        color = C_REJILLA if fija else C_VIVA
        op_menor, op_eje = (0.5, 0.8) if fija else (0.7, 1.0)
        grupo = VGroup()
        for k in range(-a, a + 1):
            for (p0, p1) in (((k, -a, 0), (k, a, 0)), ((-a, k, 0), (a, k, 0))):
                q0, q1 = m @ np.array(p0, float), m @ np.array(p1, float)
                eje = (k == 0)
                grupo.add(Line(self.p(q0), self.p(q1), color=color,
                               stroke_width=2.2 if eje else 1.3,
                               stroke_opacity=op_eje if eje else op_menor))
        return grupo

    def anim_matriz(self, m, *vectores, **kwargs):
        m = _mat(m)
        anims = [Transform(self.vivo, self.rejilla_con(m), **kwargs)]
        for v in vectores:
            anims.append(Transform(v, v.con_matriz(m), **kwargs))
        self.M = m
        return anims

    def aplicar(self, m):
        m = _mat(m)
        self.vivo.become(self.rejilla_con(m))
        self.M = m
        return self


def espacio3(unidad=0.9, alcance=3, ejes=True, suelo=True):
    """Ejes x/y/z (ambar/cian/violeta) y la rejilla del suelo, en proyeccion
    oblicua fija. `.p(x, y, z)` proyecta; `.anim_matriz(M3, *vectores)` como
    en el plano. Sin ThreeDScene: todo es 2D en pantalla."""
    if alcance > ALCANCE_MAX:
        raise ValueError(f"alcance maximo {ALCANCE_MAX}")
    return Espacio3(unidad, alcance, ejes, suelo)


class Vector3(VGroup):
    """Flecha 3D proyectada desde el origen. .coords .con_matriz(M)"""

    def __init__(self, esp, coords, color, nombre, font_size, grosor,
                 etiqueta_dir=None, **kwargs):
        super().__init__(**kwargs)
        self.espacio = esp
        self.coords = _vec(coords, 3)
        self.color_rol, self.nombre = color, nombre
        self.font_size, self.grosor = font_size, grosor
        self.etiqueta_dir = etiqueta_dir
        a, b = esp.p(0, 0, 0), esp.p(self.coords)
        largo = float(np.linalg.norm(b - a))
        if largo < 1e-6:
            self.flecha = Dot(a, radius=0.06, color=color)
        else:
            self.flecha = Arrow(a, b, buff=0.0, color=color, stroke_width=grosor,
                                tip_length=min(0.22, 0.6 * largo),
                                max_tip_length_to_length_ratio=0.5,
                                max_stroke_width_to_length_ratio=25)
        self.add(self.flecha)
        self.etiqueta = None
        if nombre is not None:
            self.etiqueta = MathTex(nombre, font_size=font_size, color=color)
            if etiqueta_dir is not None:
                # desplazamiento de PANTALLA desde la punta (como en 2D)
                self.etiqueta.move_to(b + np.asarray(etiqueta_dir, float))
            else:
                d = b - a
                n = np.linalg.norm(d)
                d = d / n if n > 1e-9 else UP
                self.etiqueta.move_to(b + 0.3 * d + 0.15 * UP)
            self.add(self.etiqueta)

    def punta(self):
        return self.espacio.p(self.coords)

    def con_matriz(self, m, color=None, nombre="__mismo__", etiqueta_dir=None):
        return Vector3(self.espacio, _mat(m) @ self.coords,
                       self.color_rol if color is None else color,
                       self.nombre if nombre == "__mismo__" else nombre,
                       self.font_size, self.grosor,
                       self.etiqueta_dir if etiqueta_dir is None else etiqueta_dir)

    def con_coords(self, coords, color=None, nombre="__mismo__", etiqueta_dir=None):
        return Vector3(self.espacio, coords,
                       self.color_rol if color is None else color,
                       self.nombre if nombre == "__mismo__" else nombre,
                       self.font_size, self.grosor,
                       self.etiqueta_dir if etiqueta_dir is None else etiqueta_dir)


def vector3(esp, coords, color=C_VEC, nombre=None, font_size=28, grosor=4.5,
            etiqueta_dir=None):
    """Flecha 3D proyectada. `etiqueta_dir`: desplazamiento de pantalla de la
    etiqueta respecto a la punta (p. ej. 0.34*DOWN), como en `vector` 2D."""
    return Vector3(esp, coords, color, nombre, font_size, grosor, etiqueta_dir)


def _aristas_caja(m, dims, origen):
    """Las 12 aristas del paralelepipedo M @ (caja de lados dims desde origen)."""
    m = _mat(m)
    o = _vec(origen, 3)
    dx, dy, dz = (float(d) for d in dims)
    esquinas = {}
    for i in (0, 1):
        for j in (0, 1):
            for k in (0, 1):
                esquinas[(i, j, k)] = m @ (o + np.array([i * dx, j * dy, k * dz]))
    aristas = []
    for (i, j, k), q in esquinas.items():
        for (di, dj, dk) in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            vecino = (i + di, j + dj, k + dk)
            if vecino in esquinas:
                aristas.append((q, esquinas[vecino]))
    return aristas


class Caja3(VGroup):
    """El paralelepipedo imagen de una caja bajo M. .volumen (con signo si
    la caja es el cubo unidad: det M). .aristas"""

    def __init__(self, esp, m, dims, origen, color, grosor, opacidad,
                 caras, **kwargs):
        super().__init__(**kwargs)
        m = _mat(m)
        self.volumen = float(np.linalg.det(m)) * float(np.prod(dims))
        self.aristas = VGroup(*[Line(esp.p(a), esp.p(b), color=color,
                                     stroke_width=grosor,
                                     stroke_opacity=opacidad)
                                for a, b in _aristas_caja(m, dims, origen)])
        self.add(self.aristas)
        self.caras = VGroup()
        if caras:
            o = _vec(origen, 3)
            dx, dy, dz = dims
            ex, ey, ez = (m @ np.array([dx, 0, 0.]), m @ np.array([0, dy, 0.]),
                          m @ np.array([0, 0, dz]))
            base = m @ o
            for (u, v, w) in ((ex, ey, ez), (ex, ez, ey), (ey, ez, ex)):
                for desplaz in (np.zeros(3), w):
                    a = base + desplaz
                    self.caras.add(Polygon(esp.p(a), esp.p(a + u),
                                           esp.p(a + u + v), esp.p(a + v),
                                           color=color, fill_color=color,
                                           fill_opacity=0.12,
                                           stroke_width=0))
            self.add(self.caras)


def caja3(esp, m=np.eye(3), dims=(1, 1, 1), origen=(0, 0, 0), color=C_AREA,
          grosor=2.6, opacidad=0.95, caras=True):
    """El cubo unidad (o una caja) transformado por M, con caras tenues.
    .volumen = det(M) * volumen de la caja."""
    return Caja3(esp, m, dims, origen, color, grosor, opacidad, caras)


def plano_generado(esp, u, v, extension=2.2, color=C_IMG, opacidad=0.22):
    """El parche del plano generado por u y v (3D), centrado en el origen."""
    u, v = _vec(u, 3), _vec(v, 3)
    s = float(extension)
    pol = Polygon(esp.p(-s * u - s * v), esp.p(s * u - s * v),
                  esp.p(s * u + s * v), esp.p(-s * u + s * v), color=color,
                  fill_color=color, fill_opacity=opacidad, stroke_width=1.6,
                  stroke_opacity=min(1.0, opacidad + 0.4))
    return pol


def satelite3(esp, R=np.eye(3), tam=0.8, color=CODE_MUTED, color_panel=C_J,
              grosor=2.4):
    """Un cubesat de alambre (cuerpo tam x tam x 1.5 tam, dos paneles en
    +-y) con actitud R (3x3). .cuerpo .paneles .eje_z (flecha del eje
    longitudinal del cuerpo, ya girada) para leer la actitud."""
    R = _mat(R)
    t = float(tam)
    cuerpo = Caja3(esp, R, (t, t, 1.5 * t), (-t / 2, -t / 2, -0.75 * t),
                   color, grosor, 0.95, True)
    paneles = VGroup()
    for lado in (-1, 1):
        y0 = lado * (t / 2 + 0.08)
        y1 = lado * (t / 2 + 0.08 + 1.4 * t)
        esquinas = [np.array([-t * 0.35, y0, -0.45 * t]),
                    np.array([t * 0.35, y0, -0.45 * t]),
                    np.array([t * 0.35, y1, -0.45 * t]),
                    np.array([-t * 0.35, y1, -0.45 * t])]
        paneles.add(Polygon(*[esp.p(R @ e) for e in esquinas],
                            color=color_panel, fill_color=color_panel,
                            fill_opacity=0.25, stroke_width=1.8))
    eje = np.array([0.0, 0.0, 1.3 * t])
    eje_z = Arrow(esp.p(R @ np.zeros(3)), esp.p(R @ eje), buff=0.0,
                  color=C_VEC, stroke_width=3.5, tip_length=0.16,
                  max_tip_length_to_length_ratio=0.5)
    grupo = VGroup(cuerpo, paneles, eje_z)
    grupo.cuerpo, grupo.paneles, grupo.eje_z = cuerpo, paneles, eje_z
    grupo.R = R
    return grupo


# =====================================================================
# Modulos 5 y 6 (ampliacion 2026-08-19): ortogonalidad, SVD, Markov,
# rotaciones 3D con eje, funciones como vectores, sistemas dinamicos.
# Misma regla: numpy puro y determinista; las piezas son VGroup cuyos
# localizadores leen el plano (siguen move_to, no scale).
# =====================================================================
from manim import Rectangle, Square  # noqa: E402


# --- numeros ----------------------------------------------------------
def gram_schmidt(vectores):
    """Ortonormaliza una lista de vectores (columnas, en orden). Devuelve
    (Q, pasos): Q con los vectores ortonormales como columnas y `pasos`
    = lista de dicts {"v": original, "sombras": [proy sobre cada q previo],
    "resto": v - sum(sombras), "q": resto normalizado}. Lo que se DIBUJA
    (restar sombras) y lo que se calcula salen del mismo bucle."""
    vs = [_vec(v) for v in vectores]
    qs, pasos = [], []
    for v in vs:
        sombras = [float(v @ q) * q for q in qs]
        resto = v - (np.sum(sombras, axis=0) if sombras else 0.0)
        n = float(np.linalg.norm(resto))
        if n < 1e-12:
            raise ValueError("vectores dependientes: Gram-Schmidt se anula")
        q = resto / n
        qs.append(q)
        pasos.append({"v": v, "sombras": sombras, "resto": resto, "q": q})
    return np.column_stack(qs), pasos


def qr(m):
    """Q, R de numpy con la convencion diag(R) >= 0 (misma Q que
    gram_schmidt sobre las columnas de M)."""
    q, r = np.linalg.qr(_mat(m))
    s = np.sign(np.diag(r))
    s[s == 0] = 1.0
    return q * s, (r.T * s).T


def es_ortogonal(m, tol=1e-9):
    m = _mat(m)
    return bool(np.allclose(m.T @ m, np.eye(m.shape[0]), atol=tol))


def svd(m):
    """U, s, Vt (np.linalg.svd, full_matrices=False) con la convencion de
    que la primera componente no nula de cada columna de U es positiva.
    Acepta matrices de cualquier tamano (una imagen, p. ej.)."""
    u, s, vt = np.linalg.svd(np.asarray(m, dtype=float), full_matrices=False)
    for j in range(u.shape[1]):
        col = u[:, j]
        k = np.flatnonzero(np.abs(col) > 1e-12)
        if k.size and col[k[0]] < 0:
            u[:, j] = -col
            vt[j, :] = -vt[j, :]
    return u, s, vt


def aproximacion_rango(m, k):
    """La mejor aproximacion de rango k (SVD truncada) y el error relativo
    en norma de Frobenius: (M_k, error)."""
    u, s, vt = svd(m)
    k = int(k)
    mk = (u[:, :k] * s[:k]) @ vt[:k, :]
    m = np.asarray(m, dtype=float)
    err = float(np.linalg.norm(m - mk) / max(np.linalg.norm(m), 1e-12))
    return mk, err


def numero_condicion(m):
    s = np.linalg.svd(np.asarray(m, dtype=float), compute_uv=False)
    return float(s[0] / s[-1]) if s[-1] > 1e-15 else float("inf")


def elipse_de(m, n=96, radio=1.0):
    """Puntos (n x 2) de la imagen del circulo de radio `radio` bajo M."""
    t = np.linspace(0.0, 2.0 * np.pi, int(n), endpoint=False)
    c = np.column_stack([np.cos(t), np.sin(t)]) * float(radio)
    return c @ _mat(m).T


def imagen_sintetica(lado=12):
    """Matriz lado x lado de grises en [0, 1], determinista: un disco
    claro sobre fondo oscuro con una barra diagonal y una franja. Rango
    numerico alto (sirve para ver como la SVD truncada la reconstruye)."""
    n = int(lado)
    y, x = np.mgrid[0:n, 0:n]
    cx = cy = (n - 1) / 2.0
    img = 0.12 * np.ones((n, n))
    img[(x - cx) ** 2 + (y - cy) ** 2 <= (0.36 * n) ** 2] = 0.75
    img[np.abs(x - y) <= max(1, n // 12)] = 0.95
    img[(y >= int(0.72 * n)) & (y < int(0.72 * n) + max(1, n // 8))] = 0.45
    return img


def markov_estacionario(t):
    """Vector estacionario (suma 1) de una matriz de transicion T cuyas
    COLUMNAS suman 1 (T @ p lleva la distribucion de hoy a la de
    manana): el autovector de autovalor 1, normalizado."""
    t = _mat(t)
    if not np.allclose(t.sum(axis=0), 1.0, atol=1e-9):
        raise ValueError("las columnas de la matriz de transicion deben "
                         "sumar 1")
    val, vec = np.linalg.eig(t)
    k = int(np.argmin(np.abs(val - 1.0)))
    p = np.real(vec[:, k])
    p = p / p.sum()
    return p


def iterar(m, x0, n):
    """[x0, M x0, M^2 x0, ..., M^n x0] como array (n+1) x dim."""
    m, x = _mat(m), _vec(x0)
    out = [x]
    for _ in range(int(n)):
        x = m @ x
        out.append(x)
    return np.array(out)


def autos_complejos(m):
    """Autovalores (complejos, ordenados por modulo decreciente) y el
    modulo y angulo (grados) del primero: (valores, modulo, grados).
    Para clasificar un sistema x_{k+1} = A x_k: |lambda| < 1 encoge,
    > 1 estira, angulo != 0 gira."""
    val = np.linalg.eigvals(_mat(m))
    val = val[np.argsort(-np.abs(val))]
    return val, float(np.abs(val[0])), float(np.degrees(np.angle(val[0])))


def eje_rotacion(r):
    """Eje unitario y angulo (grados) de una rotacion 3D R: el autovector
    de autovalor 1 (teorema de Euler) y el angulo por la traza."""
    r = _mat(r)
    val, vec = np.linalg.eig(r)
    k = int(np.argmin(np.abs(val - 1.0)))
    eje = np.real(vec[:, k])
    eje = eje / np.linalg.norm(eje)
    kk = np.flatnonzero(np.abs(eje) > 1e-12)
    if kk.size and eje[kk[0]] < 0:
        eje = -eje
    ang = float(np.degrees(np.arccos(np.clip((np.trace(r) - 1.0) / 2.0,
                                             -1.0, 1.0))))
    return eje, ang


def rot3_eje(eje, grados):
    """Rotacion 3D de `grados` alrededor del eje unitario dado
    (Rodrigues)."""
    k = _vec(eje, 3)
    k = k / np.linalg.norm(k)
    th = np.radians(float(grados))
    kx = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * kx + (1 - np.cos(th)) * (kx @ kx)


def muestrear(f, n=12, a=0.0, b=1.0):
    """Una funcion como vector: sus n valores en puntos equiespaciados de
    [a, b). Devuelve (xs, valores)."""
    xs = a + (b - a) * (np.arange(int(n)) + 0.5) / int(n)
    return xs, np.array([float(f(x)) for x in xs])


def base_fourier(n=12, k_max=3):
    """Columnas: [1, cos(2pi x), sin(2pi x), cos(4pi x), ...] muestreadas
    en n puntos de [0,1) y NORMALIZADAS (ortonormales para n > 2 k_max).
    Devuelve (xs, B, etiquetas)."""
    xs = (np.arange(int(n)) + 0.5) / int(n)
    cols, tags = [np.ones(int(n))], ["1"]
    for k in range(1, int(k_max) + 1):
        cols.append(np.cos(2 * np.pi * k * xs))
        tags.append(f"cos {k}")
        cols.append(np.sin(2 * np.pi * k * xs))
        tags.append(f"sin {k}")
    b = np.column_stack(cols)
    b = b / np.linalg.norm(b, axis=0)
    return xs, b, tags


def coeficientes(v, base):
    """Coordenadas de v en una base ORTONORMAL (columnas): producto punto
    con cada columna. Devuelve (coefs, reconstruccion)."""
    b = np.asarray(base, dtype=float)
    c = b.T @ np.asarray(v, dtype=float)
    return c, b @ c


# --- piezas 2D ----------------------------------------------------------
class Elipse(VGroup):
    """La imagen del circulo unidad bajo M: un poligono cerrado. .m
    .con_matriz(M2) gemela; .semiejes() -> (s, U) de la SVD."""

    def __init__(self, pl, m, color, grosor, opacidad, radio, n, **kwargs):
        super().__init__(**kwargs)
        self.plano, self.m, self.radio = pl, _mat(m), float(radio)
        self.color_rol, self.grosor, self.opacidad, self.n = (color, grosor,
                                                              opacidad, n)
        pts = [pl.p(q) for q in elipse_de(self.m, n, radio)]
        self.curva = Polygon(*pts, color=color, stroke_width=grosor,
                             fill_color=color, fill_opacity=opacidad)
        self.add(self.curva)

    def con_matriz(self, m):
        return Elipse(self.plano, m, self.color_rol, self.grosor,
                      self.opacidad, self.radio, self.n)

    def semiejes(self):
        u, s, _ = svd(self.m)
        return s * self.radio, u


def circulo_unidad(pl, m=np.eye(2), color=C_VEC, grosor=3.0, opacidad=0.08,
                   radio=1.0, n=96):
    """El circulo unidad (o su imagen bajo M). `Transform(c, c.con_matriz(M))`
    lo convierte en la elipse de M; los semiejes son sigma_1 u_1, sigma_2 u_2."""
    return Elipse(pl, m, color, grosor, opacidad, radio, n)


class Pixeles(VGroup):
    """Una matriz de grises como cuadricula de cuadrados. .valores
    .con_valores(V) gemela del mismo tamano/posicion (para Transform)."""

    def __init__(self, valores, lado, color, **kwargs):
        super().__init__(**kwargs)
        v = np.clip(np.asarray(valores, dtype=float), 0.0, 1.0)
        self.valores, self.lado, self.color_rol = v, float(lado), color
        n, m = v.shape
        for i in range(n):
            for j in range(m):
                c = Square(side_length=self.lado, stroke_width=0.4,
                           stroke_color=C_REJILLA, fill_color=color,
                           fill_opacity=float(v[i, j]))
                c.move_to(np.array([(j - (m - 1) / 2) * self.lado,
                                    ((n - 1) / 2 - i) * self.lado, 0.0]))
                self.add(c)

    def con_valores(self, valores):
        g = Pixeles(valores, self.lado, self.color_rol)
        g.move_to(self.get_center())
        return g


def pixeles(valores, lado=0.22, color="#e8edf3"):
    """Imagen de grises (matriz en [0,1]) como cuadricula; la SVD truncada
    se ve con `Transform(img, img.con_valores(aproximacion_rango(M, k)[0]))`."""
    return Pixeles(valores, lado, color)


class Barras(VGroup):
    """Valores como barras verticales (una distribucion, unos coeficientes,
    una funcion muestreada). .valores .barras (lista) .con_valores(V)
    gemela (mismo ancho/escala/posicion, para Transform). Los negativos
    cuelgan hacia abajo de la linea base."""

    def __init__(self, valores, colores, ancho, alto, escala, etiquetas,
                 font_size, **kwargs):
        super().__init__(**kwargs)
        v = np.asarray(valores, dtype=float)
        self.valores, self.ancho, self.alto = v, float(ancho), float(alto)
        self.escala = (float(escala) if escala is not None
                       else (self.alto / max(float(np.max(np.abs(v))), 1e-9)))
        self.colores, self.etiquetas, self.font_size = (colores, etiquetas,
                                                        font_size)
        n = len(v)
        self.base = Line(np.array([-n * ancho / 2, 0, 0]),
                         np.array([n * ancho / 2, 0, 0]), color=C_EJE,
                         stroke_width=1.4)
        self.add(self.base)
        self.barras = []
        for i, x in enumerate(v):
            h = float(x) * self.escala
            col = colores[i % len(colores)] if isinstance(colores, (list, tuple)) else colores
            r = Rectangle(width=ancho * 0.72, height=max(abs(h), 0.01),
                          color=col, fill_color=col, fill_opacity=0.8,
                          stroke_width=0.8)
            cx = (i - (n - 1) / 2) * ancho
            r.move_to(np.array([cx, h / 2, 0.0]))
            self.barras.append(r)
            self.add(r)
        if etiquetas is not None:
            for i, t in enumerate(etiquetas):
                e = _texto_hud(str(t), font_size=font_size)
                e.next_to(self.base, DOWN, buff=0.1)
                e.set_x((i - (n - 1) / 2) * ancho)
                self.add(e)

    def con_valores(self, valores):
        g = Barras(valores, self.colores, self.ancho, self.alto, self.escala,
                   self.etiquetas, self.font_size)
        g.shift(self.base.get_center() - g.base.get_center())
        return g


def barras(valores, colores=C_J, ancho=0.32, alto=1.6, escala=None,
           etiquetas=None, font_size=14):
    """Barras de un vector de valores; `escala` fija unidades->pantalla
    (si no, la barra mayor mide `alto`). Gemelas con .con_valores(V)."""
    return Barras(valores, colores, ancho, alto, escala, etiquetas, font_size)


class Trayectoria(VGroup):
    """Una sucesion de estados (n x 2) sobre el plano: puntos unidos por
    segmentos a trazos, el primero marcado. .estados .puntos .segmentos"""

    def __init__(self, pl, estados, color, radio, grosor, **kwargs):
        super().__init__(**kwargs)
        e = np.asarray(estados, dtype=float)
        self.estados = e
        self.segmentos = VGroup(*[
            DashedLine(pl.p(e[i]), pl.p(e[i + 1]), color=color,
                       stroke_width=grosor, stroke_opacity=0.7,
                       dash_length=0.08)
            for i in range(len(e) - 1)])
        self.puntos = VGroup(*[Dot(pl.p(q), radius=radio, color=color)
                               for q in e])
        self.puntos[0].scale(1.5)
        self.add(self.segmentos, self.puntos)


def trayectoria(pl, estados, color=C_VEC, radio=0.05, grosor=2.0):
    """Los estados de `iterar(M, x0, n)` dibujados sobre el plano."""
    return Trayectoria(pl, estados, color, radio, grosor)


def triada3(esp, R=np.eye(3), largo=2.0, colores=(C_I, C_J, C_K), grosor=4.0):
    """Los tres ejes de un cuerpo con actitud R como `vector3`
    (ambar x, cian y, violeta z). .ejes (lista) ; .con_matriz(R2) gemela.
    Sirve para LEER una actitud (satelite3 solo trae .eje_z)."""
    R = _mat(R)
    ejes = [vector3(esp, R[:, k] * float(largo), color=colores[k],
                    grosor=grosor) for k in range(3)]
    g = VGroup(*ejes)
    g.ejes, g.R = ejes, R

    def con_matriz(R2, _esp=esp, _largo=largo, _col=colores, _gr=grosor):
        return triada3(_esp, R2, _largo, _col, _gr)
    g.con_matriz = con_matriz
    return g
