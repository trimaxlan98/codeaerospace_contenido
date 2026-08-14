"""El presupuesto de enlace: decibelios, PIRE, FSPL, ruido, Shannon y margen.

Pensado para el curso "Cerrar el enlace: la cuenta en decibelios". Todo el
calculo es numpy puro y determinista (`np.random.default_rng(semilla)` donde
hace falta azar: hoy solo el piso de ruido y la nube de simbolos): mismo
script -> mismo render, condicion necesaria para trabajar con
`--disable_caching`. Nada de red, nada de disco.

La regla de color del curso, que es tambien la de esta libreria: lo que SUMA
es verde, lo que RESTA es rojo, la SEÑAL es ambar, el RUIDO violeta y el
RESULTADO (saldo, margen, techo del canal) cian. Ejes y mobiliario en el gris
azulado `COLOR_EJE`. No mezclar roles: la cascada de un presupuesto de enlace
se tiene que poder leer sin narracion.

Piezas:
    regla_db          multiplicar arriba = sumar abajo (el idioma del curso)
    patron_ganancia   de isotropica a lobulo estrecho a area visual constante
    frente_esferico   la misma energia repartida en una esfera que crece
    curva_fspl        perdida de espacio libre vs distancia, una curva por banda
    piso_ruido        una señal asomando sobre el ruido; el piso puede subir
    termometro_ruido  la temperatura de ruido del sistema, barra + rotulo
    cascada_db        EL diagrama del curso: waterfall de ganancias y perdidas
    curva_shannon     el techo del canal y su region prohibida
    nube_simbolos     constelaciones QPSK/8PSK/16APSK/32APSK con dispersion
    escalera_modcod   los peldaños de eficiencia por los que sube y baja ACM
    barra_margen      lo que sobra, y lo que se come la lluvia

Las piezas exponen localizadores (`.punto_de`, `.nivel`, `.centro_de`,
`.cima`, `.punta`) calculados sobre la geometria ACTUAL del mobject: siguen
siendo validos despues de mover o escalar, asi que los clips cuelgan flechas,
llaves y tags sin adivinar coordenadas. Y exponen los NUMEROS que dibujan
(`.db`, `.acumulado`, `.eficiencia`, `.valor`): en un curso que trata de una
cuenta, el rotulo del clip debe salir de la misma fuente que la barra, nunca
escribirse a mano.

Topes duros para no castigar el VPS (2 vCPU / 2 GB por render):
`TERMINOS_MAX`, `PELDANOS_MAX`, `SIMBOLOS_MAX` y `MUESTRAS_MAX` levantan
ValueError; pasarse cambia lo que se ve y es mejor enterarse.

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from enlace import cascada_db, curva_fspl, barra_margen

    casc = cascada_db([("PIRE", 58.0), ("FSPL", -205.2), ("G/T", 13.2)])
    for i in range(3):
        self.play(casc.aparecer(i))
    self.add(Text(f"{casc.acumulado(-1):.1f} dBHz"))

    fspl = curva_fspl()
    self.add(Dot(fspl.punto_de(36000, 12.0)))   # y fspl.db(36000, 12.0)
"""

import numpy as np

from manim import (AnimationGroup, Circle, DashedLine, DashedVMobject, Dot,
                   FadeIn, Line, Polygon, Rectangle, Text, Transform, VGroup,
                   VMobject, DOWN, LEFT, ORIGIN, RIGHT, UP)

from code_brand import CODE_MUTED, FUENTE_HUD, registrar_fuentes

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
TERMINOS_MAX = 8        # barras de una cascada de presupuesto
PELDANOS_MAX = 6        # MODCODs de la escalera
SIMBOLOS_MAX = 256      # simbolos de una constelacion
MUESTRAS_MAX = 400      # muestras maximas de una curva parametrica

# Paleta propia de la libreria (coincide con la del curso).
COLOR_SENAL = "#f59e0b"     # LA SEÑAL: potencia util, PIRE, portadora
COLOR_GANANCIA = "#34d399"  # lo que SUMA: ganancia de antena, G/T, -k
COLOR_PERDIDA = "#f43f5e"   # lo que RESTA: FSPL, atmosfera, lluvia
COLOR_RUIDO = "#a78bfa"     # el ruido: N0, kTB, la temperatura
COLOR_MARGEN = "#22d3ee"    # el resultado: saldo, margen, techo del canal
COLOR_EJE = "#31414f"       # mobiliario: ejes, guias, reglas, muescas

# Alias cortos con los nombres de la tabla de paleta del curso, para que el
# style_block de los clips pueda escribir `color=C_SENAL` tal cual.
C_SENAL, C_GANANCIA, C_PERDIDA = COLOR_SENAL, COLOR_GANANCIA, COLOR_PERDIDA
C_RUIDO, C_MARGEN, C_EJE = COLOR_RUIDO, COLOR_MARGEN, COLOR_EJE

# Constantes fisicas del presupuesto de enlace.
FSPL_K = 92.45          # termino constante de FSPL con d en km y f en GHz
BOLTZMANN_DBW = -228.6  # 10*log10(k) en dBW/K/Hz

# Escalones de la regla de decibelios: (factor lineal, etiqueta lineal).
# El salto x2 -> +3 dB y x10 -> +10 dB es el que hace de gancho en el clip 2.
# Las etiquetas evitan superindices: Space Mono no trae el glifo (un "10⁶"
# sale renderizado como "10'"), asi que el millon se escribe "1M".
_ESCALONES = ((1.0, "1"), (2.0, "2"), (10.0, "10"), (100.0, "100"),
              (1e3, "1000"), (1e6, "1M"))

_EPS = 1e-9


# --- utilidades internas ----------------------------------------------
def _texto_hud(texto, font_size=15, color=COLOR_EJE):
    """Etiqueta tecnica corta en la tipografia de telemetria de la marca."""
    registrar_fuentes()
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=color)


def _curva(puntos, color, grosor=3.0):
    """VMobject suave a partir de un array (n, 2) o (n, 3) de escena."""
    pts = np.asarray(puntos, dtype=np.float64)
    if pts.shape[1] == 2:
        pts = np.column_stack([pts, np.zeros(len(pts))])
    curva = VMobject(color=color, stroke_width=grosor)
    curva.set_points_smoothly(pts)
    return curva


def _poligonal(puntos, color, grosor=2.0):
    """Como `_curva` pero SIN suavizar: para el ruido erizado, donde suavizar
    redondearia justo lo que se quiere mostrar."""
    pts = np.asarray(puntos, dtype=np.float64)
    if pts.shape[1] == 2:
        pts = np.column_stack([pts, np.zeros(len(pts))])
    linea = VMobject(color=color, stroke_width=grosor)
    linea.set_points_as_corners(pts)
    return linea


def _validar_muestras(nombre, muestras):
    """Tope duro comun a todas las curvas parametricas de la libreria."""
    n = int(muestras)
    if n > MUESTRAS_MAX:
        raise ValueError(
            f"{nombre}: muestras={n} supera MUESTRAS_MAX={MUESTRAS_MAX}")
    return max(8, n)


def _punto(objeto):
    """Coordenada de escena de un punto o del centro de un mobject."""
    if hasattr(objeto, "get_center"):
        return np.asarray(objeto.get_center(), dtype=np.float64)
    pt = np.asarray(objeto, dtype=np.float64).flatten()
    if pt.size == 2:
        pt = np.array([pt[0], pt[1], 0.0])
    return pt[:3].astype(np.float64)


def _ejes_xy(ancho, alto, color=COLOR_EJE):
    """Par de ejes en L con origen en la esquina inferior izquierda, centrados
    en ORIGIN. Devuelve (VGroup, origen) con el origen ya en coordenadas de
    escena para que quien llama sitúe sus curvas."""
    x0, y0 = -ancho / 2, -alto / 2
    eje_x = Line((x0, y0, 0), (x0 + ancho, y0, 0), stroke_width=2.0,
                 color=color)
    eje_y = Line((x0, y0, 0), (x0, y0 + alto, 0), stroke_width=2.0,
                 color=color)
    return VGroup(eje_x, eje_y), np.array([x0, y0, 0.0])


def _fmt_db(v, decimales=1):
    """Valor en dB con signo explicito: en una cascada el signo ES la lectura."""
    return f"{v:+.{decimales}f}".rstrip("0").rstrip(".") if decimales else \
        f"{v:+.0f}"


def fspl_db(d_km, f_ghz):
    """Perdida de espacio libre en dB. La formula del curso, en un solo sitio:
    20log10(d km) + 20log10(f GHz) + 92.45.

    Acepta escalares o arrays en cualquiera de los dos argumentos: `curva_fspl`
    la evalua sobre todo el eje de distancias de una vez.
    """
    d = np.maximum(np.asarray(d_km, dtype=np.float64), _EPS)
    f = np.maximum(np.asarray(f_ghz, dtype=np.float64), _EPS)
    return 20 * np.log10(d) + 20 * np.log10(f) + FSPL_K


# --- el idioma: decibelios --------------------------------------------
class ReglaDB(VGroup):
    """Dos escalas sobre el mismo eje: factores arriba, decibelios abajo."""

    def __init__(self, eje, lineales, decibelios, marcas, **kwargs):
        super().__init__(eje, lineales, decibelios, **kwargs)
        self.eje = eje
        self.lineales = lineales
        self.decibelios = decibelios
        self._marcas = marcas

    def _marca(self, i):
        n = len(self._marcas)
        if not -n <= i < n:
            raise IndexError(f"regla_db: escalon {i} fuera de rango ({n})")
        return self._marcas[i % n]

    def marca_lineal(self, i):
        """Punto de la muesca i en la escala de factores (arriba)."""
        return _punto(self.lineales[i % len(self.lineales)])

    def marca_db(self, i):
        """Punto de la muesca i en la escala de decibelios (abajo)."""
        return _punto(self.decibelios[i % len(self.decibelios)])

    def par(self, i):
        """VGroup(etiqueta_lineal, etiqueta_db) del escalon i, para Indicate:
        resaltar el par es exactamente el mensaje 'esto es aquello'."""
        j = i % len(self.lineales)
        return VGroup(self.lineales[j], self.decibelios[j])

    def db_de(self, i):
        """Los decibelios del escalon i (10log10 del factor)."""
        return 10 * np.log10(self._marca(i))


def regla_db(ancho=6.4, alto=0.9, font_size=15, color=COLOR_SENAL,
             color_db=COLOR_MARGEN, color_eje=COLOR_EJE):
    """Regla de conversion: factores lineales arriba, decibelios abajo.

    Los escalones NO se colocan a escala logaritmica real (x1 y x10⁶ caerian
    a distancias absurdas): se reparten equiespaciados y es la propia
    correspondencia columna a columna la que cuenta la historia — multiplicar
    arriba es sumar abajo. Las dos etiquetas de un escalon comparten la x
    exacta, asi que la lectura vertical nunca miente.
    """
    registrar_fuentes()
    n = len(_ESCALONES)
    x0 = -ancho / 2
    paso = ancho / (n - 1)

    eje = Line((x0, 0, 0), (x0 + ancho, 0, 0), stroke_width=2.0,
               color=color_eje)
    muescas = VGroup()
    lineales = VGroup()
    decibelios = VGroup()
    factores = []

    for i, (factor, etiqueta) in enumerate(_ESCALONES):
        x = x0 + i * paso
        muescas.add(Line((x, -0.09, 0), (x, 0.09, 0), stroke_width=1.6,
                         color=color_eje))
        arriba = _texto_hud(f"×{etiqueta}", font_size=font_size, color=color)
        arriba.move_to((x, alto / 2 + 0.12, 0))
        abajo = _texto_hud(f"+{10 * np.log10(factor):.0f} dB",
                           font_size=font_size, color=color_db)
        abajo.move_to((x, -alto / 2 - 0.12, 0))
        lineales.add(arriba)
        decibelios.add(abajo)
        factores.append(factor)

    return ReglaDB(VGroup(eje, muescas), lineales, decibelios, factores)


# --- la potencia que apunta -------------------------------------------
class PatronGanancia(VMobject):
    """Patron polar cuyo estrechamiento cuenta la ganancia de la antena."""

    def __init__(self, ganancia_db, escala, color, muestras, **kwargs):
        super().__init__(color=color, stroke_width=3.0, **kwargs)
        self.ganancia_db = float(ganancia_db)
        self.escala = float(escala)
        self._color = color
        self._muestras = muestras
        self.set_points_smoothly(self._puntos())
        self.set_fill(color, opacity=0.12)
        # Vector del centro del bounding box al ORIGEN POLAR (la antena).
        # Se guarda porque el lobulo es asimetrico: su centro geometrico no
        # es donde esta la antena, y sin esto un `move_to` deja al emisor
        # flotando en mitad del lobulo en vez de en su vertice.
        self._al_origen = -self.get_center()

    def _exponente(self):
        """Exponente del coseno que da el lobulo.

        La directividad de un patron cos^n va como ~2(n+1), asi que
        n = 10^(G/10)/2 - 1 reproduce la ganancia pedida. Se satura a 60 para
        que 45 dB no degenere en una aguja de un pixel.
        """
        lineal = 10 ** (self.ganancia_db / 10)
        return float(np.clip(lineal / 2 - 1, 0.0, 60.0))

    def _puntos(self):
        n = self._exponente()
        theta = np.linspace(0, 2 * np.pi, self._muestras)
        # cos^n del ANGULO MITAD: es una funcion suave y sin nodos en 2pi, que
        # da un lobulo unico hacia +x (un cos^n crudo se parte en dos lobulos
        # y ademas se anula bruscamente en +-90 deg).
        r = np.cos(theta / 2) ** (2 * n) if n > 0 else np.ones_like(theta)
        # Area visual ~constante: la potencia no se crea, se reparte. El area
        # de un lobulo r(theta) va como la integral de r^2, asi que se
        # normaliza por su raiz.
        area = np.trapezoid(r ** 2, theta) if hasattr(np, "trapezoid") else \
            np.trapz(r ** 2, theta)
        r = r / np.sqrt(max(area / (2 * np.pi), _EPS))
        r = r * self.escala
        return np.column_stack([r * np.cos(theta), r * np.sin(theta),
                                np.zeros_like(theta)])

    def origen_polar(self):
        """Donde esta la antena: el punto del que sale la radiacion."""
        return self.get_center() + self._al_origen

    def anclar_en(self, punto):
        """Coloca el patron con su ORIGEN POLAR en `punto` (no su centro).
        Devuelve self para encadenar."""
        self.shift(np.asarray(_punto(punto)) - self.origen_polar())
        return self

    def con_ganancia(self, g_db):
        """Mismo patron con otra ganancia, anclado en la MISMA antena: el
        argumento natural de un Transform.

        Se ancla por origen polar y no por centro a proposito — al estrecharse
        el lobulo, centro y vertice se separan, y anclar por centro haria que
        la antena se deslizara sola durante la animacion.
        """
        otro = PatronGanancia(g_db, self.escala, self._color, self._muestras)
        return otro.anclar_en(self.origen_polar())

    def punta(self):
        """Extremo del lobulo (el punto mas lejano en la direccion de tiro)."""
        return np.array([self.get_right()[0], self.origen_polar()[1], 0.0])


def patron_ganancia(ganancia_db=0.0, escala=1.6, color=COLOR_SENAL,
                    muestras=180):
    """Patron de radiacion apuntando a la DERECHA, de isotropico (0 dB) a
    lobulo estrecho, a area visual aproximadamente constante."""
    muestras = _validar_muestras("patron_ganancia", muestras)
    return PatronGanancia(ganancia_db, escala, color, muestras)


# --- la caida del espacio libre ---------------------------------------
class FrenteEsferico(VGroup):
    """Anillos concentricos cuya densidad de marca cae como 1/r^2."""

    def __init__(self, anillos, origen, radios, **kwargs):
        super().__init__(*anillos, **kwargs)
        self.anillos = VGroup(*anillos)
        self._origen = np.asarray(origen, dtype=np.float64)
        self._radios = list(radios)

    def anillo(self, i):
        return self.anillos[i % len(self.anillos)]

    def en(self, i, deg):
        """Punto del anillo i en ese angulo (0 = derecha, antihorario).

        Se recalcula sobre la posicion ACTUAL del grupo, no sobre la de
        construccion: mover el frente no invalida los receptores colgados.
        """
        r = self._radios[i % len(self._radios)]
        a = np.deg2rad(float(deg))
        centro = self.origen()
        return centro + np.array([r * np.cos(a), r * np.sin(a), 0.0])

    def origen(self):
        """Centro actual de la familia de anillos."""
        return self.anillos[0].get_center()


def frente_esferico(radios=(0.6, 1.2, 1.8, 2.4), origen=ORIGIN,
                    color=COLOR_SENAL, puntos=42, semilla=7):
    """Anillos punteados desde `origen`, con la opacidad de las marcas cayendo
    como 1/r^2: la misma energia repartida en una esfera que crece.

    El primer anillo marca la referencia de opacidad; los demas se atenuan
    por (r0/r)^2, que es exactamente la ley que el clip narra.
    """
    rng = np.random.default_rng(int(semilla))
    radios = [float(r) for r in radios]
    if not radios:
        raise ValueError("frente_esferico: hace falta al menos un radio")
    n = _validar_muestras("frente_esferico", puntos)
    base = np.asarray(_punto(origen), dtype=np.float64)
    r0 = radios[0]

    anillos = []
    for r in radios:
        # Fase inicial propia por anillo (determinista): sin ella los puntos
        # quedan alineados en radios perfectos y se lee como una rueda.
        fase = rng.uniform(0, 2 * np.pi)
        angulos = np.linspace(0, 2 * np.pi, n, endpoint=False) + fase
        opacidad = float(np.clip((r0 / max(r, _EPS)) ** 2, 0.08, 1.0))
        marcas = VGroup(*[
            Dot(base + np.array([r * np.cos(a), r * np.sin(a), 0.0]),
                radius=0.026, color=color).set_opacity(opacidad)
            for a in angulos])
        aro = DashedVMobject(Circle(radius=r, color=color, stroke_width=1.4)
                             .move_to(base), num_dashes=48)
        aro.set_opacity(opacidad * 0.5)
        anillos.append(VGroup(aro, marcas))
    return FrenteEsferico(anillos, base, radios)


class CurvaFspl(VGroup):
    """FSPL vs distancia, una curva por frecuencia, con los numeros a mano."""

    def __init__(self, ejes, curvas, etiquetas, frecuencias, d_km, rango_db,
                 ancho, alto, origen, **kwargs):
        super().__init__(ejes, curvas, etiquetas, **kwargs)
        self.ejes = ejes
        self.curvas = curvas
        self.etiquetas = etiquetas
        self._frecuencias = list(frecuencias)
        self._d = (float(d_km[0]), float(d_km[1]))
        self._db = rango_db
        self._ancho = float(ancho)
        self._alto = float(alto)
        self._origen = np.asarray(origen, dtype=np.float64)
        # Centro al construir: `punto_de` le suma el desplazamiento acumulado
        # y por eso sigue valiendo tras un move_to. Se guarda AQUI y no la
        # primera vez que se pide, o el primer uso tras mover fijaria el
        # centro ya desplazado y el localizador quedaria mudo.
        self._centro_original = self.get_center()

    def db(self, d_km, f_ghz):
        """El valor que el clip rotula. Misma fuente que la curva dibujada."""
        return float(fspl_db(d_km, f_ghz))

    def _rel(self, d_km, f_ghz):
        lo, hi = np.log10(self._d[0]), np.log10(self._d[1])
        x = (np.log10(np.clip(d_km, self._d[0], self._d[1])) - lo) / (hi - lo)
        y = (self.db(d_km, f_ghz) - self._db[0]) / (self._db[1] - self._db[0])
        return float(x), float(np.clip(y, 0.0, 1.0))

    def punto_de(self, d_km, f_ghz):
        """Punto de escena sobre la curva de esa frecuencia."""
        x, y = self._rel(d_km, f_ghz)
        desplazamiento = self.get_center() - self._centro_original
        return (self._origen + np.array([x * self._ancho, y * self._alto, 0.0])
                + desplazamiento)



def curva_fspl(f_ghz=(2.0, 12.0, 30.0), d_km=(300.0, 40000.0), ancho=5.8,
               alto=2.6, color_ejes=COLOR_EJE, font_size=14, muestras=160,
               colores=None):
    """Ejes (distancia km en log ->, FSPL dB ^) con una curva por frecuencia.

    Las etiquetas se cuelgan al final de cada curva, que es donde mas
    separadas quedan entre si (la distancia entre curvas es constante en dB,
    pero al final no compiten con el trazo de ninguna otra).
    """
    muestras = _validar_muestras("curva_fspl", muestras)
    frecuencias = [float(f) for f in f_ghz]
    if not frecuencias:
        raise ValueError("curva_fspl: hace falta al menos una frecuencia")
    paleta = list(colores) if colores else [COLOR_PERDIDA, COLOR_SENAL,
                                            COLOR_RUIDO]

    d0, d1 = float(d_km[0]), float(d_km[1])
    ds = np.logspace(np.log10(d0), np.log10(d1), muestras)
    todos = [fspl_db(ds, f) for f in frecuencias]
    lo = float(min(v.min() for v in todos)) - 4.0
    hi = float(max(v.max() for v in todos)) + 4.0

    ejes, origen = _ejes_xy(ancho, alto, color_ejes)
    curvas = VGroup()
    etiquetas = VGroup()
    for i, (f, vals) in enumerate(zip(frecuencias, todos)):
        x = (np.log10(ds) - np.log10(d0)) / (np.log10(d1) - np.log10(d0))
        y = (vals - lo) / (hi - lo)
        pts = origen + np.column_stack([x * ancho, y * alto,
                                        np.zeros_like(x)])
        color = paleta[i % len(paleta)]
        curva = _curva(pts, color, grosor=2.6)
        etiqueta = _texto_hud(f"{f:g} GHz", font_size=font_size, color=color)
        etiqueta.next_to(pts[-1], RIGHT, buff=0.12)
        curvas.add(curva)
        etiquetas.add(etiqueta)

    tag_x = _texto_hud("DISTANCIA", font_size=font_size - 1)
    tag_x.next_to(ejes[0], DOWN, buff=0.16)
    tag_y = _texto_hud("FSPL dB", font_size=font_size - 1)
    tag_y.next_to(ejes[1], UP, buff=0.14)
    ejes.add(tag_x, tag_y)

    return CurvaFspl(ejes, curvas, etiquetas, frecuencias, (d0, d1),
                     (lo, hi), ancho, alto, origen)


# --- el ruido ----------------------------------------------------------
class PisoRuido(VGroup):
    """Una señal asomando sobre el piso de ruido; el piso puede subir."""

    def __init__(self, ejes, ruido, senal, nivel, cima_rel, params, **kwargs):
        super().__init__(ejes, ruido, senal, **kwargs)
        self.ejes = ejes
        self.ruido = ruido
        self.senal = senal
        self.nivel = float(nivel)
        self.cima_rel = float(cima_rel)
        self._params = params

    def cima(self):
        """Punta del LOBULO de señal (para colgar una flecha o un tag).

        Se lee del punto central de la curva, no de `get_top()`: cuando el
        piso sube y el lobulo se hunde, el maximo global de la traza pasa a
        ser una cresta cualquiera del ruido, y una flecha colgada ahi
        apuntaria a ruido en vez de a la señal.
        """
        pts = self.senal.points
        return np.array(pts[len(pts) // 2], dtype=np.float64)

    def margen_rel(self):
        """Cuanto asoma la señal sobre el piso, en fraccion de la caja. Es la
        lectura del clip: sube el ruido y esto se encoge."""
        return self.cima_rel - self.nivel

    def _variante(self, nivel, cima_rel):
        otro = piso_ruido(nivel=nivel, cima_rel=cima_rel, **self._params)
        otro.move_to(self.get_center())
        return otro

    def con_nivel(self, nivel):
        """Mismo grafico con el piso de ruido mas alto (o mas bajo).

        La CIMA de la señal no se mueve — solo sube el suelo. Es el punto
        narrativo del clip 5 ("la señal no empeoro: subio el suelo") y por eso
        `cima_rel` es una altura absoluta de la caja y no un delta sobre el
        piso: con un delta, subir el ruido arrastraria el pico hacia arriba y
        se leeria justo al reves.
        """
        return self._variante(nivel, self.cima_rel)

    def con_senal(self, cima_rel):
        """Mismo grafico con la punta de la señal a otra altura."""
        return self._variante(self.nivel, cima_rel)


def piso_ruido(ancho=5.6, alto=2.2, nivel=0.28, cima_rel=0.85, semilla=11,
               color=COLOR_RUIDO, color_senal=COLOR_SENAL, muestras=300,
               color_ejes=COLOR_EJE):
    """Piso de ruido erizado con un lobulo de señal centrado encima.

    `nivel` y `cima_rel` son alturas ABSOLUTAS relativas a la caja (0-1): la
    del suelo y la de la punta de la señal. El clip sube `nivel` hasta casi
    tapar la señal sin que la señal se mueva (ver `PisoRuido.con_nivel`).
    """
    muestras = _validar_muestras("piso_ruido", muestras)
    rng = np.random.default_rng(int(semilla))
    ejes, origen = _ejes_xy(ancho, alto, color_ejes)

    x = np.linspace(0, 1, muestras)
    # Ruido: gaussiano centrado en `nivel`, con la amplitud tipica de un piso
    # bien medido (no se suaviza: el erizado ES la lectura).
    ruido_y = np.clip(nivel + rng.normal(0, 0.035, muestras), 0.02, 0.98)
    # Señal: lobulo gaussiano estrecho que sale del piso y llega a `cima_rel`.
    # Si el ruido ya la supera, la señal queda sepultada — y se ve.
    lobulo = np.exp(-((x - 0.5) ** 2) / (2 * 0.045 ** 2))
    senal_y = np.clip(ruido_y + (cima_rel - nivel) * lobulo, 0.02, 0.99)

    # La traza de señal se recorta a la ventana del lobulo: si se dibujara de
    # lado a lado quedaria pintada ENCIMA del piso en todo el ancho y taparia
    # justo lo que el clip quiere comparar.
    ventana = np.abs(x - 0.5) <= 0.16

    pts_ruido = origen + np.column_stack([x * ancho, ruido_y * alto,
                                          np.zeros_like(x)])
    pts_senal = origen + np.column_stack([x[ventana] * ancho,
                                          senal_y[ventana] * alto,
                                          np.zeros(int(ventana.sum()))])
    ruido = _poligonal(pts_ruido, color, grosor=1.6)
    ruido.set_opacity(0.85)
    senal = _poligonal(pts_senal, color_senal, grosor=2.4)

    tag = _texto_hud("POTENCIA", font_size=13)
    tag.next_to(ejes[1], UP, buff=0.14)
    ejes.add(tag)

    params = {"ancho": ancho, "alto": alto, "semilla": semilla,
              "color": color, "color_senal": color_senal,
              "muestras": muestras, "color_ejes": color_ejes}
    return PisoRuido(ejes, ruido, senal, nivel, cima_rel, params)


class TermometroRuido(VGroup):
    """Temperatura de ruido del sistema: barra y numero, siempre en sincronia."""

    def __init__(self, marco, columna, rotulo, t_kelvin, t_max, alto, ancho,
                 font_size, color, **kwargs):
        super().__init__(marco, columna, rotulo, **kwargs)
        self.marco = marco
        self.columna = columna
        self.rotulo = rotulo
        self.t_kelvin = float(t_kelvin)
        self._t_max = float(t_max)
        self._alto = float(alto)
        self._ancho = float(ancho)
        self._font_size = font_size
        self._color = color

    def _columna_para(self, t):
        frac = float(np.clip(t / self._t_max, 0.0, 1.0))
        barra = Rectangle(width=self._ancho, height=max(self._alto * frac,
                                                        0.02),
                          stroke_width=0, fill_color=self._color,
                          fill_opacity=0.85)
        barra.move_to(self.marco.get_bottom() + UP * (barra.height / 2))
        return barra

    def a_temperatura(self, t):
        """Animacion unica que reescala la barra Y reescribe el rotulo.

        Van juntas a proposito: en dos animaciones separadas el numero y la
        barra se desincronizan durante medio segundo, y un termometro que
        miente medio segundo es peor que no ponerlo.
        """
        nueva = self._columna_para(t)
        nuevo_rotulo = _texto_hud(f"T = {t:.0f} K", font_size=self._font_size,
                                  color=self._color)
        nuevo_rotulo.move_to(self.rotulo.get_center())
        self.t_kelvin = float(t)
        return AnimationGroup(Transform(self.columna, nueva),
                              Transform(self.rotulo, nuevo_rotulo))


def termometro_ruido(t_kelvin=150.0, t_max=600.0, alto=2.2, ancho=0.42,
                     color=COLOR_RUIDO, font_size=15, color_eje=COLOR_EJE):
    """Barra vertical con la temperatura de ruido del sistema y su rotulo."""
    marco = Rectangle(width=ancho, height=alto, stroke_width=1.8,
                      color=color_eje)
    frac = float(np.clip(t_kelvin / t_max, 0.0, 1.0))
    columna = Rectangle(width=ancho, height=max(alto * frac, 0.02),
                        stroke_width=0, fill_color=color, fill_opacity=0.85)
    columna.move_to(marco.get_bottom() + UP * (columna.height / 2))
    rotulo = _texto_hud(f"T = {t_kelvin:.0f} K", font_size=font_size,
                        color=color)
    rotulo.next_to(marco, DOWN, buff=0.18)
    return TermometroRuido(marco, columna, rotulo, t_kelvin, t_max, alto,
                           ancho, font_size, color)


# --- la cascada: el corazon del curso ---------------------------------
class CascadaDB(VGroup):
    """Waterfall del presupuesto: cada barra arranca donde acabo la anterior."""

    def __init__(self, barras, guias, saldo, valores, acumulados, niveles,
                 **kwargs):
        super().__init__(**kwargs)
        self._barras = list(barras)
        self._guias = list(guias)
        self.saldo = saldo
        self._valores = list(valores)
        self._acumulados = list(acumulados)
        self._niveles = list(niveles)
        # Se añaden todos al grupo (invisibles) para que move_to/scale del
        # conjunto los arrastre: `aparecer` solo los enciende.
        for barra in self._barras:
            self.add(barra)
        for guia in self._guias:
            self.add(guia)
        self.add(saldo)
        for mob in [*self._barras, *self._guias, saldo]:
            mob.set_opacity(0)
        # Ver la nota de CurvaFspl: el centro se congela al construir para que
        # `nivel(i)` siga apuntando bien despues de mover la cascada.
        self._centro_original = self.get_center()

    def __len__(self):
        return len(self._barras)

    def barra(self, i):
        return self._barras[i]

    def valor(self, i):
        """Los dB del termino i, con su signo."""
        return self._valores[i]

    def acumulado(self, i):
        """dB acumulados TRAS aplicar el termino i (acepta indices negativos:
        `.acumulado(-1)` es el saldo final que el clip rotula)."""
        return self._acumulados[i]

    def nivel(self, i):
        """Punto del extremo de la barra i, para colgar llaves o flechas."""
        base = self._niveles[i]
        return base + (self.get_center() - self._centro_original)


    def aparecer(self, i, run_time=0.7):
        """Animacion de la barra i con su guia (para LaggedStart o beat a
        beat). La guia entra con la barra: nunca hay una linea suelta."""
        barra = self._barras[i]
        partes = [barra]
        if i < len(self._guias):
            partes.append(self._guias[i])
        return AnimationGroup(*[FadeIn(p.set_opacity(1), shift=0.12 * UP)
                                for p in partes], run_time=run_time)

    def aparecer_saldo(self, run_time=0.9):
        """La barra cian del acumulado final, que se dibuja desde cero."""
        return FadeIn(self.saldo.set_opacity(1), shift=0.14 * UP,
                      run_time=run_time)


def cascada_db(terminos, ancho=7.0, alto=3.0, font_size=15,
               color_ganancia=COLOR_GANANCIA, color_perdida=COLOR_PERDIDA,
               color_saldo=COLOR_MARGEN, etiqueta_saldo="C/N₀",
               color_eje=COLOR_EJE):
    """Diagrama de cascada del presupuesto de enlace.

    `terminos` es una lista de (etiqueta, valor_db): positivo sube en verde,
    negativo baja en rojo. La barra final, en cian, es el acumulado medido
    desde cero — el saldo del enlace.

    La escala vertical se calcula sobre el RECORRIDO real del acumulado (no
    sobre el termino mayor): en un presupuesto de enlace la FSPL vale -205 dB
    y aplastaria todo lo demas a un pixel si mandara ella.
    """
    items = [(str(e), float(v)) for e, v in terminos]
    if not items:
        raise ValueError("cascada_db: hace falta al menos un termino")
    if len(items) > TERMINOS_MAX:
        raise ValueError(f"cascada_db: {len(items)} terminos supera "
                         f"TERMINOS_MAX={TERMINOS_MAX}")

    acumulados = []
    total = 0.0
    for _, v in items:
        total += v
        acumulados.append(total)

    # La escala abarca el recorrido del acumulado y el cero (la linea base
    # tiene que salir siempre: sin ella una cascada no se lee).
    niveles_db = [0.0, *acumulados]
    lo, hi = min(niveles_db), max(niveles_db)
    span = max(hi - lo, 1.0)
    escala = alto / span

    n = len(items)
    ancho_barra = min(0.72, ancho / (n + 1) * 0.78)
    paso = ancho / n
    x0 = -ancho / 2 + paso / 2
    y_cero = -alto / 2 - lo * escala

    barras, guias, niveles = [], [], []
    previo = 0.0
    for i, (etiqueta, valor) in enumerate(items):
        x = x0 + i * paso
        y_ini = y_cero + previo * escala
        y_fin = y_cero + acumulados[i] * escala
        color = color_ganancia if valor >= 0 else color_perdida
        cuerpo = Rectangle(width=ancho_barra,
                           height=max(abs(y_fin - y_ini), 0.04),
                           stroke_width=0, fill_color=color, fill_opacity=0.85)
        cuerpo.move_to(((x), (y_ini + y_fin) / 2, 0))

        tag = _texto_hud(etiqueta, font_size=font_size - 1, color=color)
        # Dos alturas alternadas bajo la barra: las etiquetas de un
        # presupuesto ("PIRE", "FSPL", "G/T") no caben en una sola fila.
        tag.move_to((x, -alto / 2 - (0.30 if i % 2 == 0 else 0.62), 0))

        num = _texto_hud(_fmt_db(valor), font_size=font_size, color=color)
        # El numero va al extremo exterior de la barra, salvo que ahi invada
        # la banda de etiquetas: una barra corta y negativa (la atmosfera,
        # -1.5 dB de 205) acaba justo encima de la fila de tags y su cifra se
        # encimaba con ella. En ese caso el numero se pasa al otro extremo.
        banda_tags = -alto / 2 - 0.06
        if valor >= 0 or (min(y_ini, y_fin) - 0.10) > banda_tags:
            num.next_to(cuerpo, UP if valor >= 0 else DOWN, buff=0.10)
        else:
            num.next_to(cuerpo, UP, buff=0.10)

        barras.append(VGroup(cuerpo, tag, num))
        niveles.append(np.array([x, y_fin, 0.0]))
        if i < n - 1:
            guia = DashedLine((x + ancho_barra / 2, y_fin, 0),
                              (x + paso - ancho_barra / 2, y_fin, 0),
                              stroke_width=1.3, color=color_eje,
                              dash_length=0.06)
            guias.append(guia)
        previo = acumulados[i]

    # La barra del saldo: desde el cero, en cian, un poco separada.
    x_saldo = x0 + (n - 0.02) * paso
    y_fin = y_cero + acumulados[-1] * escala
    cuerpo = Rectangle(width=ancho_barra,
                       height=max(abs(y_fin - y_cero), 0.04),
                       stroke_width=0, fill_color=color_saldo,
                       fill_opacity=0.9)
    cuerpo.move_to((x_saldo, (y_cero + y_fin) / 2, 0))
    tag = _texto_hud(etiqueta_saldo, font_size=font_size, color=color_saldo)
    tag.move_to((x_saldo, -alto / 2 - 0.30, 0))
    num = _texto_hud(f"{acumulados[-1]:.1f}", font_size=font_size,
                     color=color_saldo)
    num.next_to(cuerpo, UP, buff=0.10)
    saldo = VGroup(cuerpo, tag, num)

    base = Line((-ancho / 2 - 0.2, y_cero, 0), (ancho / 2 + 0.35, y_cero, 0),
                stroke_width=1.6, color=color_eje)
    casc = CascadaDB(barras, guias, saldo, [v for _, v in items], acumulados,
                     niveles)
    casc.add_to_back(base)
    return casc


# --- el techo del canal ------------------------------------------------
class CurvaShannon(VGroup):
    """Eficiencia espectral maxima y la region que nadie alcanza."""

    # Opacidad a la que se revela la region prohibida. Es un sombreado de
    # apoyo, no una mancha: a opacidad plena tapa la curva que enmarca.
    OPACIDAD_PROHIBIDA = 0.16

    def __init__(self, ejes, curva, prohibida, rango_snr, rango_ef, ancho,
                 alto, origen, **kwargs):
        super().__init__(ejes, prohibida, curva, **kwargs)
        self.ejes = ejes
        self.curva = curva
        self.prohibida = prohibida
        self._snr = rango_snr
        self._ef = rango_ef
        self._ancho = float(ancho)
        self._alto = float(alto)
        self._origen = np.asarray(origen, dtype=np.float64)
        # Ver la nota de CurvaFspl.
        self._centro_original = self.get_center()

    def revelar_prohibida(self):
        """Animacion que enciende la region imposible a su opacidad correcta.

        Existe para que el clip no tenga que acordarse del numero: un
        `set_opacity(1)` a ojo la deja como una mancha solida que se come la
        curva de Shannon y los MODCOD de debajo.
        """
        return self.prohibida.animate.set_opacity(self.OPACIDAD_PROHIBIDA)

    def eficiencia(self, snr_db):
        """log2(1 + SNR) en bits/s/Hz. El numero que el clip puede rotular."""
        return float(np.log2(1 + 10 ** (float(snr_db) / 10)))

    def _en(self, snr_db, eficiencia):
        x = (float(snr_db) - self._snr[0]) / (self._snr[1] - self._snr[0])
        y = (float(eficiencia) - self._ef[0]) / (self._ef[1] - self._ef[0])
        desplazamiento = self.get_center() - self._centro_original
        return (self._origen
                + np.array([np.clip(x, 0, 1) * self._ancho,
                            np.clip(y, 0, 1) * self._alto, 0.0])
                + desplazamiento)


    def punto_de(self, snr_db):
        """Punto SOBRE la curva de Shannon a ese SNR."""
        return self._en(snr_db, self.eficiencia(snr_db))

    def punto_modcod(self, snr_db, eficiencia):
        """Punto de un MODCOD real, en sus propias coordenadas (siempre bajo
        la curva: si alguien pasa una eficiencia imposible, se recorta al
        techo y se ve pegado a el, que es la verdad fisica)."""
        techo = self.eficiencia(snr_db)
        return self._en(snr_db, min(float(eficiencia), techo))


def curva_shannon(snr_db=(-5.0, 25.0), ancho=5.6, alto=2.8,
                  color=COLOR_MARGEN, color_ejes=COLOR_EJE, font_size=14,
                  muestras=200, color_prohibida=COLOR_PERDIDA):
    """Ejes (SNR dB ->, bits/s/Hz ^) con el limite de Shannon y la region
    prohibida sobre el (translucida, `opacity` 0 al construir para FadeIn)."""
    muestras = _validar_muestras("curva_shannon", muestras)
    s0, s1 = float(snr_db[0]), float(snr_db[1])
    snrs = np.linspace(s0, s1, muestras)
    ef = np.log2(1 + 10 ** (snrs / 10))
    ef_max = float(ef.max()) * 1.06

    ejes, origen = _ejes_xy(ancho, alto, color_ejes)
    x = (snrs - s0) / (s1 - s0)
    y = ef / ef_max
    pts = origen + np.column_stack([x * ancho, y * alto, np.zeros_like(x)])
    curva = _curva(pts, color, grosor=2.8)

    # La region prohibida: el area entre la curva y el techo de la caja.
    borde = np.vstack([pts,
                       [origen[0] + ancho, origen[1] + alto, 0.0],
                       [origen[0], origen[1] + alto, 0.0]])
    prohibida = Polygon(*borde, stroke_width=0, fill_color=color_prohibida,
                        fill_opacity=CurvaShannon.OPACIDAD_PROHIBIDA)
    prohibida.set_opacity(0)

    tag_x = _texto_hud("SNR dB", font_size=font_size - 1)
    tag_x.next_to(ejes[0], DOWN, buff=0.16)
    tag_y = _texto_hud("BITS/S/HZ", font_size=font_size - 1)
    tag_y.next_to(ejes[1], UP, buff=0.14)
    ejes.add(tag_x, tag_y)

    return CurvaShannon(ejes, curva, prohibida, (s0, s1), (0.0, ef_max),
                        ancho, alto, origen)


class NubeSimbolos(VGroup):
    """Constelacion: cada simbolo ideal rodeado de su nube de ruido."""

    def __init__(self, nubes, orden, dispersion, params, **kwargs):
        super().__init__(*nubes, **kwargs)
        self.orden = int(orden)
        self.dispersion = float(dispersion)
        self._params = params

    def _variante(self, orden, dispersion):
        otra = nube_simbolos(orden=orden, dispersion=dispersion,
                             **self._params)
        otra.move_to(self.get_center())
        return otra

    def con_orden(self, n):
        """Misma constelacion con otro orden (4 -> 8 -> 16 -> 32)."""
        return self._variante(n, self.dispersion)

    def con_dispersion(self, d):
        """Misma constelacion con mas o menos ruido en cada nube."""
        return self._variante(self.orden, d)


def nube_simbolos(orden=4, dispersion=0.06, escala=1.1, semilla=3,
                  color=COLOR_SENAL, por_simbolo=24):
    """Constelacion QPSK (4), 8PSK (8) o APSK en anillos (16, 32).

    Los ordenes altos se reparten en dos anillos, como el APSK real de
    DVB-S2X: 16 = 4 + 12, 32 = 4 + 12 + 16. La nube alrededor de cada simbolo
    es determinista, y su tamaño (`dispersion`) es la lectura del ruido.
    """
    n = int(orden)
    if n * int(por_simbolo) > SIMBOLOS_MAX * 8:
        raise ValueError(f"nube_simbolos: {n} simbolos x {por_simbolo} puntos "
                         "es demasiado para un render del VPS")
    if n > SIMBOLOS_MAX:
        raise ValueError(f"nube_simbolos: orden={n} supera "
                         f"SIMBOLOS_MAX={SIMBOLOS_MAX}")
    rng = np.random.default_rng(int(semilla))

    # Reparto en anillos, estilo APSK: (radio_relativo, cuantos).
    if n <= 8:
        anillos = [(1.0, n)]
    elif n <= 16:
        anillos = [(0.55, 4), (1.0, n - 4)]
    else:
        anillos = [(0.42, 4), (0.75, 12), (1.0, n - 16)]

    ideales = []
    for radio, cuantos in anillos:
        if cuantos <= 0:
            continue
        fase = np.pi / cuantos
        for k in range(cuantos):
            a = 2 * np.pi * k / cuantos + fase
            ideales.append((radio * escala * np.cos(a),
                            radio * escala * np.sin(a)))

    nubes = []
    for cx, cy in ideales:
        puntos = VGroup()
        for _ in range(int(por_simbolo)):
            dx, dy = rng.normal(0, dispersion, 2)
            puntos.add(Dot((cx + dx, cy + dy, 0), radius=0.018, color=color)
                       .set_opacity(0.75))
        nubes.append(puntos)

    params = {"escala": escala, "semilla": semilla, "color": color,
              "por_simbolo": por_simbolo}
    return NubeSimbolos(nubes, n, dispersion, params)


# --- el margen ---------------------------------------------------------
class EscaleraModcod(VGroup):
    """Los peldaños de eficiencia por los que ACM sube y baja."""

    def __init__(self, escalones, marcador, centros, datos, **kwargs):
        super().__init__(*escalones, **kwargs)
        self._escalones = list(escalones)
        self._centros = list(centros)
        self._datos = list(datos)
        self.marcador = marcador
        self._activo = 0

    def peldano(self, i):
        return self._escalones[i % len(self._escalones)]

    def centro_de(self, i):
        """Centro actual del peldaño i (valido tras mover el grupo)."""
        return self.peldano(i)[0].get_center()

    def bits_hz(self, i):
        """Eficiencia del peldaño i, para que el clip rotule el numero real."""
        return self._datos[i % len(self._datos)][2]

    def activo(self):
        return self._activo

    def mover_a(self, i):
        """Animacion del marcador al peldaño i (subir o bajar de MODCOD).

        No fija `run_time`: lo pone el clip en `self.play(...)`, como con
        cualquier otra animacion (fijarlo aqui haria que un run_time en el
        play chocara con el del `.animate`).
        """
        destino = self.centro_de(i) + LEFT * (self.peldano(i)[0].width / 2
                                              + 0.30)
        self._activo = i % len(self._escalones)
        return self.marcador.animate.move_to(destino)


def escalera_modcod(peldanos, ancho=4.6, alto=2.6, font_size=14,
                    color=COLOR_MARGEN, color_eje=COLOR_EJE):
    """Escalera de MODCODs: cada peldaño a la altura de su eficiencia.

    `peldanos` es una lista de (etiqueta, snr_db, bits_hz) ordenada de menor a
    mayor eficiencia. La x de cada peldaño crece con su SNR requerido: subir
    de MODCOD es ir arriba Y a la derecha, que es la intuicion correcta (mas
    bits cuestan mas señal).
    """
    items = [(str(e), float(s), float(b)) for e, s, b in peldanos]
    if not items:
        raise ValueError("escalera_modcod: hace falta al menos un peldaño")
    if len(items) > PELDANOS_MAX:
        raise ValueError(f"escalera_modcod: {len(items)} peldaños supera "
                         f"PELDANOS_MAX={PELDANOS_MAX}")

    snrs = [s for _, s, _ in items]
    bits = [b for _, _, b in items]
    s0, s1 = min(snrs), max(snrs)
    b0, b1 = min(bits), max(bits)
    ancho_peldano = min(1.5, ancho / len(items) * 1.15)

    escalones = []
    centros = []
    for etiqueta, snr, bph in items:
        fx = (snr - s0) / max(s1 - s0, _EPS)
        fy = (bph - b0) / max(b1 - b0, _EPS)
        x = -ancho / 2 + ancho_peldano / 2 + fx * (ancho - ancho_peldano)
        y = -alto / 2 + fy * alto
        barra = Line((x - ancho_peldano / 2, y, 0),
                     (x + ancho_peldano / 2, y, 0), stroke_width=3.0,
                     color=color)
        tag = _texto_hud(etiqueta, font_size=font_size, color=color)
        tag.next_to(barra, UP, buff=0.10)
        # La eficiencia va a la DERECHA del peldaño, no debajo: con etiqueta
        # arriba y numero abajo, cada peldaño ocupa mas alto del que hay entre
        # dos peldaños y el numero de uno se encima con el nombre del de
        # arriba. A la derecha, el hueco que usa es el que la escalera ya deja
        # libre por su propia forma.
        num = _texto_hud(f"{bph:.2f}", font_size=font_size - 2,
                         color=color_eje)
        num.next_to(barra, RIGHT, buff=0.14)
        escalones.append(VGroup(barra, tag, num))
        centros.append(np.array([x, y, 0.0]))

    marcador = Dot(radius=0.07, color=color)
    marcador.move_to(centros[0] + LEFT * (ancho_peldano / 2 + 0.30))
    esc = EscaleraModcod(escalones, marcador, centros, items)
    esc.add(marcador)
    return esc


class BarraMargen(VGroup):
    """Lo que sobra al cerrar la cuenta, y lo que se lo va comiendo."""

    def __init__(self, marco, columna, umbral, rotulo, margen_db, tope_db,
                 alto, ancho, font_size, color, color_perdida, **kwargs):
        super().__init__(marco, umbral, columna, rotulo, **kwargs)
        self.marco = marco
        self.columna = columna
        self.umbral = umbral
        self.rotulo = rotulo
        self._margen = float(margen_db)
        self._tope = float(tope_db)
        self._alto = float(alto)
        self._ancho = float(ancho)
        self._font_size = font_size
        self._color = color
        self._color_perdida = color_perdida
        self.comido = VGroup()
        self.add(self.comido)

    def valor(self):
        """Margen restante en dB (negativo si el enlace ya no cierra)."""
        return self._margen

    def _y_de(self, db):
        frac = float(np.clip(db / self._tope, 0.0, 1.0))
        return self.umbral.get_center()[1] + frac * self._alto

    def comer(self, db):
        """La lluvia se lleva `db` decibelios: se pintan de rojo DESDE ARRIBA
        y el rotulo se reescribe en la misma animacion.

        Si se come mas de lo que hay, la barra queda vacia y el rotulo lo dice
        con signo negativo: el enlace no cierra, que es el momento dramatico
        del clip 8.
        """
        db = float(db)
        if db < 0:
            return self.devolver(-db)
        y_alto = self._y_de(self._margen)
        restante = self._margen - db
        y_bajo = self._y_de(max(restante, 0.0))

        trozo = Rectangle(width=self._ancho, height=max(y_alto - y_bajo, 0.02),
                          stroke_width=0, fill_color=self._color_perdida,
                          fill_opacity=0.85)
        trozo.move_to((self.marco.get_center()[0], (y_alto + y_bajo) / 2, 0))
        trozo.set_opacity(0)
        self.comido.add(trozo)

        return AnimationGroup(FadeIn(trozo.set_opacity(0.85)),
                              *self._recolocar(restante))

    def devolver(self, db):
        """Lo contrario de `comer`: el margen que se recupera al bajar de
        MODCOD. No pinta nada de rojo — lo comido por la lluvia sigue comido;
        lo que cambia es cuanto margen necesita el enlace."""
        return AnimationGroup(*self._recolocar(self._margen + abs(float(db))))

    def _recolocar(self, restante):
        """Columna y rotulo para un margen dado, como par de animaciones que
        van SIEMPRE juntas (barra y numero no pueden desincronizarse)."""
        y_cero = self.umbral.get_center()[1]
        y_bajo = self._y_de(max(restante, 0.0))
        nueva = Rectangle(width=self._ancho,
                          height=max(y_bajo - y_cero, 0.02),
                          stroke_width=0, fill_color=self._color,
                          fill_opacity=0.85)
        nueva.move_to((self.marco.get_center()[0], (y_bajo + y_cero) / 2, 0))

        self._margen = restante
        color_txt = self._color if restante >= 0 else self._color_perdida
        nuevo_rotulo = _texto_hud(f"{restante:+.1f} dB",
                                  font_size=self._font_size, color=color_txt)
        nuevo_rotulo.move_to(self.rotulo.get_center())
        return (Transform(self.columna, nueva),
                Transform(self.rotulo, nuevo_rotulo))


def barra_margen(margen_db=6.0, tope_db=12.0, alto=2.6, ancho=0.5,
                 font_size=15, color=COLOR_MARGEN,
                 color_perdida=COLOR_PERDIDA, color_eje=COLOR_EJE):
    """Barra vertical del margen sobre la linea de umbral (cierra / no cierra).

    El cero no esta abajo del todo: queda a una quinta parte de la caja, para
    que un margen negativo tenga sitio donde dibujarse.
    """
    margen_db = float(margen_db)
    tope_db = float(tope_db)
    caja_alto = alto * 1.25
    marco = Rectangle(width=ancho, height=caja_alto, stroke_width=1.8,
                      color=color_eje)
    y_cero = marco.get_bottom()[1] + caja_alto * 0.2

    umbral = Line((marco.get_left()[0] - 0.22, y_cero, 0),
                  (marco.get_right()[0] + 0.22, y_cero, 0),
                  stroke_width=2.0, color=color_eje)
    tag = _texto_hud("CIERRA", font_size=font_size - 3, color=color_eje)
    tag.next_to(umbral, LEFT, buff=0.10)

    frac = float(np.clip(margen_db / tope_db, 0.0, 1.0))
    columna = Rectangle(width=ancho, height=max(alto * frac, 0.02),
                        stroke_width=0, fill_color=color, fill_opacity=0.85)
    columna.move_to((marco.get_center()[0], y_cero + columna.height / 2, 0))

    rotulo = _texto_hud(f"{margen_db:+.1f} dB", font_size=font_size,
                        color=color)
    rotulo.next_to(marco, DOWN, buff=0.18)

    barra = BarraMargen(marco, columna, umbral, rotulo, margen_db, tope_db,
                        alto, ancho, font_size, color, color_perdida)
    barra.add(tag)
    return barra
