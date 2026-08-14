"""Sistemas distribuidos: fallas, latencia, Lamport, quorum y el anillo.

Pensado para el curso "Sistemas distribuidos: la nube por dentro". Todo
el calculo es python/numpy puro y determinista (el unico azar va con
semilla; el hash del anillo es md5, determinista por definicion): mismo
script -> mismo render, condicion necesaria para `--disable_caching`.
Nada de red, nada de disco.

La regla de color del curso, que es tambien la de esta libreria: los
MENSAJES (datos viajando) son ambar, los NODOS (replicas, lo medido)
cian, la MAYORIA y lo disponible verde, las CAIDAS y la particion rojo,
el TIEMPO LOGICO y el anillo de hash violeta. Mobiliario en `COLOR_EJE`.

Piezas:
    rejilla_nodos     la nube: grid de nodos; `.apaga(indices)` en rojo
    curva_caidas      1 - p^N contra N (x log); `.en(n)`
    linea_latencia    ciudades A ESCALA de distancia real + arcos RTT
    diagrama_lamport  3 procesos, eventos, mensajes; relojes CALCULADOS
    par_centros       dos centros de datos + enlace; `.corte()`
    nodos_quorum      N nodos; `.aro(indices)` marca conjuntos W y R
    anillo_hash       claves y nodos en el circulo; `.con_nodo_extra()`
                      y `.fraccion_movida()` MEDIDA contando claves
    corona            la corona del lider electo

Los NUMEROS que se rotulan salen de funciones (`prob_alguna_caida`,
`disponibilidad_replicas`, `distancia_km`, `rtt_ms`,
`relojes_lamport`, `interseccion_quorum`, `rondas_eleccion`,
`fraccion_movida`), nunca a mano. La fraccion del anillo y la
interseccion del quorum se MIDEN sobre los datos del dibujo.

Topes duros para no castigar el VPS: `NODOS_MAX`, `CLAVES_MAX`,
`EVENTOS_MAX`, `MUESTRAS_MAX` levantan ValueError.

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from distribuido import anillo_hash, rtt_ms

    anillo = anillo_hash()
    self.play(Create(anillo.circulo))
"""

import hashlib
import math

import numpy as np

from manim import (ArcBetweenPoints, Arrow, Circle, Dot, Line,
                   Polygon, RoundedRectangle, Text, VGroup, VMobject,
                   DOWN, LEFT, ORIGIN, RIGHT, TAU, UP)

from code_brand import FUENTE_HUD, registrar_fuentes

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
NODOS_MAX = 64
CLAVES_MAX = 120
EVENTOS_MAX = 12       # eventos por proceso en el diagrama de Lamport
MUESTRAS_MAX = 600

# Paleta propia de la libreria (coincide con la del curso).
COLOR_MENSAJE = "#f59e0b"   # los mensajes, los datos viajando
COLOR_NODO = "#22d3ee"      # los nodos, las replicas, lo medido
COLOR_OK = "#34d399"        # la mayoria, el quorum, lo disponible
COLOR_FALLO = "#f43f5e"     # las caidas, la particion, el split-brain
COLOR_TIEMPO = "#a78bfa"    # los relojes logicos, el anillo de hash
COLOR_EJE = "#31414f"       # mobiliario

C_MENSAJE, C_NODO, C_OK = COLOR_MENSAJE, COLOR_NODO, COLOR_OK
C_FALLO, C_TIEMPO, C_EJE = COLOR_FALLO, COLOR_TIEMPO, COLOR_EJE

# --- Los numeros del mundo -------------------------------------------
# Ciudades (lat, lon) y velocidad de la luz en fibra (c / indice ~1.5,
# cita estandar). La disponibilidad tipica de una maquina: 99.9 %.
CIUDADES = {"CDMX": (19.43, -99.13),
            "Nueva York": (40.71, -74.01),
            "Madrid": (40.42, -3.70),
            "Tokio": (35.68, 139.69)}
V_FIBRA_KMS = 2.0e5          # km/s
P_MAQUINA = 0.999
RADIO_TIERRA_KM = 6371.0

_EPS = 1e-12


# --- nucleo: los numeros ----------------------------------------------
def prob_alguna_caida(n, p=P_MAQUINA):
    """P(al menos una de n maquinas caida) = 1 - p^n (63.2 % con 1000)."""
    n = int(n)
    if n < 1:
        raise ValueError(f"prob_alguna_caida: n={n} < 1")
    return 1.0 - float(p) ** n


def disponibilidad_replicas(k=3, p=P_MAQUINA):
    """1 - (1-p)^k: con 3 replicas al 99.9 %, nueve nueves."""
    k = int(k)
    if k < 1:
        raise ValueError(f"disponibilidad_replicas: k={k} < 1")
    return 1.0 - (1.0 - float(p)) ** k


def distancia_km(ciudad_a, ciudad_b):
    """Gran circulo (haversine) entre dos ciudades de `CIUDADES`, en km."""
    la1, lo1 = (math.radians(v) for v in CIUDADES[ciudad_a])
    la2, lo2 = (math.radians(v) for v in CIUDADES[ciudad_b])
    h = (math.sin((la2 - la1) / 2.0) ** 2
         + math.cos(la1) * math.cos(la2)
         * math.sin((lo2 - lo1) / 2.0) ** 2)
    return 2.0 * RADIO_TIERRA_KM * math.asin(math.sqrt(h))


def rtt_ms(ciudad_a, ciudad_b):
    """PISO fisico de ida y vuelta: 2 d / v_fibra, en ms. La latencia
    real es mayor (rutas, colas): esto es lo que la fisica no perdona."""
    return 2.0 * distancia_km(ciudad_a, ciudad_b) / V_FIBRA_KMS * 1000.0


def relojes_lamport(eventos, mensajes):
    """Relojes logicos de Lamport para un diagrama de procesos.

    `eventos`: tupla con el numero de eventos de cada proceso.
    `mensajes`: tuplas (p_origen, i_origen, p_destino, i_destino): el
    evento i_origen ENVIA y el evento i_destino RECIBE.
    Regla: local = anterior + 1; recepcion = max(anterior, emisor) + 1.
    Devuelve dict {(p, i): reloj}. Itera hasta punto fijo (los diagramas
    del curso son acicíclicos y convergen en 2-3 pasadas).
    """
    for n in eventos:
        _validar("relojes_lamport.eventos", n, EVENTOS_MAX)
    reloj = {(p, i): 1 for p, n in enumerate(eventos) for i in range(n)}
    for _ in range(10):
        cambiado = False
        for p, n in enumerate(eventos):
            for i in range(n):
                v = 1 if i == 0 else reloj[(p, i - 1)] + 1
                for (po, io, pd, idn) in mensajes:
                    if pd == p and idn == i:
                        v = max(v, reloj[(po, io)] + 1)
                if v != reloj[(p, i)]:
                    reloj[(p, i)] = v
                    cambiado = True
        if not cambiado:
            break
    return reloj


def interseccion_quorum(n=5, w=3, r=3):
    """Nodos garantizados en comun entre escritura y lectura: W+R-N
    (palomar). Con 5/3/3 es 1: toda lectura pisa el dato nuevo."""
    return max(int(w) + int(r) - int(n), 0)


def _hash_unidad(nombre):
    """md5(nombre) llevado a [0, 1): determinista por definicion."""
    entero = int(hashlib.md5(str(nombre).encode()).hexdigest(), 16)
    return entero / float(1 << 128)


def posiciones_anillo(nombres):
    """Posicion [0,1) de cada nombre en el anillo, por hash md5."""
    return {n: _hash_unidad(n) for n in nombres}


def asignacion_anillo(claves, nodos):
    """Cada clave pertenece al primer nodo a favor de las manecillas.

    Devuelve dict {clave: nodo}. `claves` y `nodos` son nombres.
    """
    pos_n = sorted((_hash_unidad(n), n) for n in nodos)
    resultado = {}
    for c in claves:
        h = _hash_unidad(c)
        duenio = next((n for p, n in pos_n if p >= h), pos_n[0][1])
        resultado[c] = duenio
    return resultado


def fraccion_movida(n_nodos=4, n_claves=24, nodo_nuevo="nodo-nuevo"):
    """Fraccion de claves que cambia de duenio al entrar un nodo, MEDIDA
    contando (no el 1/(n+1) teorico, aunque coincide en promedio)."""
    n_nodos = _validar("fraccion_movida.n_nodos", n_nodos, NODOS_MAX)
    n_claves = _validar("fraccion_movida.n_claves", n_claves, CLAVES_MAX)
    claves = [f"clave-{i}" for i in range(n_claves)]
    nodos = [f"nodo-{j}" for j in range(n_nodos)]
    antes = asignacion_anillo(claves, nodos)
    despues = asignacion_anillo(claves, nodos + [nodo_nuevo])
    movidas = sum(1 for c in claves if antes[c] != despues[c])
    return movidas / float(n_claves)


def rondas_eleccion(semilla, n=5, muere_lider=True, max_terminos=6,
                    retardo_red=18.0):
    """Eleccion de lider al estilo Raft, simplificada y SEMBRADA.

    Por termino: cada nodo vivo sortea un timeout U(150, 300) ms; los
    que expiran a menos de `retardo_red` ms del primero se candidatean
    (no alcanzaron a oir la peticion del otro). Cada nodo restante vota
    por el candidato cuya peticion le llega primero (timeout del
    candidato + jitter de red sembrado). Mayoria estricta de N gana; si
    nadie la junta, nuevo termino. Tras la primera eleccion, si
    `muere_lider`, el lider cae y se repite entre los vivos (la mayoria
    sigue siendo de N: los muertos no votan pero si cuentan).

    Devuelve lista de rondas: dicts con termino, vivos, timeouts,
    candidatos, votos {votante: candidato} y lider (o None).
    """
    n = _validar("rondas_eleccion.n", n, NODOS_MAX)
    rng = np.random.default_rng(int(semilla))
    mayoria = n // 2 + 1
    vivos = list(range(n))
    rondas, termino, fase_muerte = [], 0, False
    while termino < max_terminos:
        termino += 1
        timeouts = {i: float(rng.uniform(150.0, 300.0)) for i in vivos}
        primero = min(timeouts.values())
        candidatos = [i for i in vivos
                      if timeouts[i] - primero < retardo_red]
        votos = {}
        for i in vivos:
            if i in candidatos:
                votos[i] = i          # cada candidato se vota a si mismo
                continue
            llegadas = {c: timeouts[c] + float(rng.uniform(0.0, retardo_red))
                        for c in candidatos}
            votos[i] = min(llegadas, key=llegadas.get)
        conteo = {c: sum(1 for v in votos.values() if v == c)
                  for c in candidatos}
        lider = next((c for c, k in conteo.items() if k >= mayoria), None)
        rondas.append({"termino": termino, "vivos": list(vivos),
                       "timeouts": timeouts, "candidatos": candidatos,
                       "votos": votos, "lider": lider})
        if lider is not None:
            if muere_lider and not fase_muerte:
                vivos = [i for i in vivos if i != lider]
                fase_muerte = True
            else:
                break
    return rondas


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
# La rejilla de nodos (la nube)
# =====================================================================
class RejillaNodos(VGroup):
    """Grid de nodos cian; `.apaga(indices)` los pinta de rojo."""

    def __init__(self, ancla, nodos, params, **kwargs):
        super().__init__(ancla, nodos, **kwargs)
        self._ancla = ancla            # el centro
        self.nodos = nodos
        self._params = params

    def nodo(self, i):
        return self.nodos[int(i)]

    def apaga(self, indices):
        """Pinta esos nodos de COLOR_FALLO (mutante); devuelve el VGroup
        de los apagados, por si el clip quiere animarlos."""
        apagados = VGroup()
        for i in indices:
            d = self.nodos[int(i)]
            d.set_color(COLOR_FALLO)
            apagados.add(d)
        return apagados


def indices_caidos(total, k, semilla=11):
    """k indices distintos, deterministas por semilla: los caidos."""
    rng = np.random.default_rng(int(semilla))
    return sorted(int(i) for i in
                  rng.choice(int(total), size=int(k), replace=False))


def rejilla_nodos(filas=4, columnas=8, paso=0.58, radio=0.09,
                  color=COLOR_NODO):
    """La nube sin marketing: filas x columnas nodos identicos."""
    _validar("rejilla_nodos.filas", filas, 8)
    _validar("rejilla_nodos.columnas", columnas, 12)
    ancho = (columnas - 1) * paso
    alto = (filas - 1) * paso
    nodos = VGroup()
    for f in range(filas):
        for c in range(columnas):
            p = np.array([c * paso - ancho / 2.0,
                          alto / 2.0 - f * paso, 0.0])
            nodos.add(Dot(p, radius=radio, color=color))
    params = {"filas": filas, "columnas": columnas, "paso": paso}
    return RejillaNodos(_ancla(ORIGIN), nodos, params)


# =====================================================================
# La curva de caidas
# =====================================================================
class CurvaCaidas(VGroup):
    """1 - p^N contra N (x en log10); `.en(n)` sobre geometria ACTUAL."""

    def __init__(self, ancla, ejes, curva, params, **kwargs):
        super().__init__(ancla, ejes, curva, **kwargs)
        self._ancla = ancla            # esquina inferior izquierda
        self.ejes = ejes
        self.curva = curva
        self._params = params

    def _escala_actual(self):
        return self.ejes[0].get_length() / max(self._params["ancho"], _EPS)

    def en(self, n):
        """Punto de escena sobre la curva para N maquinas."""
        p = self._params
        esc = self._escala_actual()
        fx = math.log10(max(float(n), 1.0)) / math.log10(p["n_max"])
        fy = prob_alguna_caida(n, p["p"])
        return (self._ancla.get_center() + RIGHT * fx * p["ancho"] * esc
                + UP * fy * p["alto"] * esc)


def curva_caidas(n_max=1000, p=P_MAQUINA, ancho=5.2, alto=2.8,
                 color=COLOR_FALLO, muestras=220):
    """La cuenta cruel: P(alguna caida) contra el numero de maquinas."""
    muestras = _validar("curva_caidas.muestras", muestras, MUESTRAS_MAX)
    n_max, ancho, alto = float(n_max), float(ancho), float(alto)
    origen = np.array([-ancho / 2.0, -alto / 2.0, 0.0])

    ejes = VGroup(
        Line(origen, origen + RIGHT * ancho, stroke_width=2.0,
             color=COLOR_EJE),
        Line(origen, origen + UP * alto, stroke_width=2.0,
             color=COLOR_EJE))

    ns = np.logspace(0.0, math.log10(n_max), muestras)
    pts = [origen
           + RIGHT * (math.log10(n) / math.log10(n_max)) * ancho
           + UP * (1.0 - float(p) ** n) * alto for n in ns]
    curva = _poligonal(pts, color, 3.0)

    params = {"n_max": n_max, "p": float(p), "ancho": ancho, "alto": alto}
    return CurvaCaidas(_ancla(origen), ejes, curva, params)


# =====================================================================
# La linea de latencia (ciudades a escala)
# =====================================================================
class LineaLatencia(VGroup):
    """Ciudades sobre una linea, a escala de distancia real."""

    def __init__(self, ancla, base, puntos, params, **kwargs):
        super().__init__(ancla, base, puntos, **kwargs)
        self._ancla = ancla            # la ciudad origen
        self.base = base
        self.puntos = puntos           # dict nombre -> Dot
        self._params = params
        self.origen = params["origen"]

    def ciudad(self, nombre):
        return self.puntos[nombre]

    def rtt(self, destino):
        """El piso fisico de ida y vuelta, en ms (rtt_ms del nucleo)."""
        return rtt_ms(self.origen, destino)

    def arco(self, destino, color=COLOR_MENSAJE, grosor=2.6,
             comba=0.55):
        """Arco de mensaje origen -> destino sobre geometria ACTUAL."""
        a = self._ancla.get_center()
        b = self.puntos[destino].get_center()
        return ArcBetweenPoints(a, b, angle=-comba, stroke_width=grosor,
                                color=color)


def linea_latencia(origen="CDMX", destinos=("Nueva York", "Madrid",
                                            "Tokio"),
                   ancho=10.4, color=COLOR_NODO):
    """El mapa sin mapa: las ciudades separadas por su distancia REAL
    (gran circulo), proyectadas a una linea. El arco y su cifra son el
    piso fisico de la fibra."""
    dists = {d: distancia_km(origen, d) for d in destinos}
    d_max = max(dists.values())
    esc = float(ancho) / d_max

    base = Line(LEFT * 0.3, RIGHT * (ancho + 0.3), stroke_width=1.8,
                color=COLOR_EJE)
    base.set_stroke(opacity=0.7)
    puntos = {origen: Dot(ORIGIN, radius=0.085, color=COLOR_OK)}
    grupo_puntos = VGroup(puntos[origen])
    for d in destinos:
        p = Dot(RIGHT * dists[d] * esc, radius=0.075, color=color)
        puntos[d] = p
        grupo_puntos.add(p)

    pieza = LineaLatencia(_ancla(ORIGIN), base, grupo_puntos,
                          {"origen": origen, "ancho": float(ancho)})
    pieza.puntos = puntos
    pieza.shift(LEFT * ancho / 2.0)
    return pieza


# =====================================================================
# El diagrama de Lamport
# =====================================================================
class DiagramaLamport(VGroup):
    """Procesos verticales, eventos y mensajes; el tiempo sube."""

    def __init__(self, ancla, lineas, eventos_vg, flechas, params,
                 **kwargs):
        super().__init__(ancla, lineas, eventos_vg, flechas, **kwargs)
        self._ancla = ancla            # pie del proceso 0
        self.lineas = lineas
        self.eventos = {}              # dict (p, i) -> Dot (se asigna
                                       # tras construir; el VGroup ya
                                       # viaja dentro del grupo)
        self.flechas = flechas         # VGroup de Arrow, orden de spec
        self._params = params
        self.relojes = params["relojes"]

    def evento(self, p, i):
        return self.eventos[(int(p), int(i))]

    def reloj(self, p, i):
        """El numero de Lamport CALCULADO de ese evento."""
        return self.relojes[(int(p), int(i))]


def diagrama_lamport(eventos=(3, 3, 3),
                     mensajes=((0, 0, 1, 1), (1, 1, 2, 1), (2, 2, 0, 2)),
                     ancho=6.4, alto=3.6, color_linea=COLOR_EJE,
                     color_evento=COLOR_NODO, color_msg=COLOR_MENSAJE):
    """Diagrama espacio-tiempo con relojes de Lamport calculados.

    El tiempo SUBE. Los eventos de cada proceso se reparten en su linea;
    `mensajes` son (p_origen, i_origen, p_destino, i_destino). Los
    numeros que se rotulan salen de `.reloj(p, i)`, nunca a mano.
    """
    n_proc = len(eventos)
    _validar("diagrama_lamport.procesos", n_proc, 5)
    relojes = relojes_lamport(eventos, mensajes)

    ancho, alto = float(ancho), float(alto)
    paso_x = ancho / max(n_proc - 1, 1)
    base = np.array([0.0, -alto / 2.0, 0.0])

    lineas = VGroup()
    eventos_g = {}
    todos_eventos = VGroup()
    for p in range(n_proc):
        x = p * paso_x - ancho / 2.0
        pie = np.array([x, -alto / 2.0, 0.0])
        lineas.add(Line(pie, pie + UP * alto, stroke_width=2.2,
                        color=color_linea))
        n = eventos[p]
        for i in range(n):
            y = -alto / 2.0 + alto * (i + 1) / (n + 1)
            d = Dot(np.array([x, y, 0.0]), radius=0.075,
                    color=color_evento)
            eventos_g[(p, i)] = d
            todos_eventos.add(d)

    flechas = VGroup()
    for (po, io, pd, idn) in mensajes:
        a = eventos_g[(po, io)].get_center()
        b = eventos_g[(pd, idn)].get_center()
        flechas.add(Arrow(a, b, buff=0.09, stroke_width=2.6,
                          color=color_msg, max_tip_length_to_length_ratio=0.09))

    params = {"eventos": tuple(eventos), "mensajes": tuple(mensajes),
              "relojes": relojes, "ancho": ancho, "alto": alto}
    pieza = DiagramaLamport(_ancla(np.array([-ancho / 2.0, -alto / 2.0,
                                             0.0])),
                            lineas, todos_eventos, flechas, params)
    pieza.eventos = eventos_g
    return pieza


# =====================================================================
# Los dos centros de datos
# =====================================================================
class ParCentros(VGroup):
    """Dos cajas y su enlace; `.corte()` fabrica la particion."""

    def __init__(self, ancla, cajas, enlace, params, **kwargs):
        super().__init__(ancla, cajas, enlace, **kwargs)
        self._ancla = ancla            # centro del enlace
        self.cajas = cajas
        self.enlace = enlace
        self._params = params

    def caja(self, i):
        return self.cajas[int(i)]

    def punto_enlace(self, frac=0.5):
        """Punto del enlace a fraccion `frac` (geometria ACTUAL)."""
        a, b = self.enlace.get_start(), self.enlace.get_end()
        return a + float(frac) * (b - a)

    def corte(self, tamano=0.42, color=COLOR_FALLO):
        """El rayo de la particion: dos trazos cruzados sobre el centro
        del enlace (geometria ACTUAL)."""
        c = self.punto_enlace(0.5)
        v1 = np.array([0.6, 1.0, 0.0]) * tamano / 2.0
        v2 = np.array([-0.6, 1.0, 0.0]) * tamano / 2.0
        return VGroup(
            Line(c - v1, c + v1, stroke_width=4.0, color=color),
            Line(c - v2 + RIGHT * 0.14, c + v2 + RIGHT * 0.14,
                 stroke_width=4.0, color=color))


def par_centros(sep=5.6, ancho_caja=2.3, alto_caja=1.5,
                color=COLOR_NODO):
    """Dos centros de datos gemelos unidos por un enlace."""
    sep = float(sep)
    izq = RoundedRectangle(width=ancho_caja, height=alto_caja,
                           corner_radius=0.12, stroke_width=2.6,
                           color=color)
    der = izq.copy()
    izq.move_to(LEFT * sep / 2.0)
    der.move_to(RIGHT * sep / 2.0)
    enlace = Line(izq.get_right(), der.get_left(), stroke_width=2.6,
                  color=COLOR_EJE)
    return ParCentros(_ancla(ORIGIN), VGroup(izq, der), enlace,
                      {"sep": sep})


# =====================================================================
# El quorum
# =====================================================================
class NodosQuorum(VGroup):
    """N nodos en fila; `.aro(indices)` los rodea como conjunto."""

    def __init__(self, ancla, nodos, params, **kwargs):
        super().__init__(ancla, nodos, **kwargs)
        self._ancla = ancla            # el centro de la fila
        self.nodos = nodos
        self._params = params
        self.n = params["n"]

    def nodo(self, i):
        return self.nodos[int(i)]

    def aro(self, indices, color=COLOR_OK, radio=0.30):
        """Aros alrededor de esos nodos (geometria ACTUAL): un conjunto
        de quorum. Radios distintos permiten ver W y R a la vez."""
        aros = VGroup()
        for i in indices:
            c = Circle(radius=radio, stroke_width=2.6, color=color)
            c.move_to(self.nodos[int(i)].get_center())
            aros.add(c)
        return aros

    def interseccion(self, idx_w, idx_r):
        """Los nodos en ambos conjuntos, MEDIDOS sobre los indices (y
        garantizados >= interseccion_quorum)."""
        return sorted(set(int(i) for i in idx_w)
                      & set(int(i) for i in idx_r))


def nodos_quorum(n=5, paso=1.15, radio=0.16, color=COLOR_NODO):
    """N nodos en fila para marcar conjuntos de escritura y lectura."""
    n = _validar("nodos_quorum.n", n, 9)
    ancho = (n - 1) * paso
    nodos = VGroup(*[
        Dot(np.array([i * paso - ancho / 2.0, 0.0, 0.0]), radius=radio,
            color=color)
        for i in range(n)])
    return NodosQuorum(_ancla(ORIGIN), nodos, {"n": n, "paso": paso})


# =====================================================================
# El anillo de hash
# =====================================================================
class AnilloHash(VGroup):
    """Claves y nodos en el circulo; el duenio es el siguiente nodo."""

    def __init__(self, ancla, circulo, nodos_g, claves_g, params,
                 **kwargs):
        super().__init__(ancla, circulo, nodos_g, claves_g, **kwargs)
        self._ancla = ancla            # el centro
        self.circulo = circulo
        self.nodos = nodos_g           # dict nombre -> Dot
        self.claves = claves_g         # dict nombre -> Dot
        self._params = params
        self.asignacion = params["asignacion"]

    def _radio_actual(self):
        return 0.5 * self.circulo.width

    def punto(self, frac, radio_rel=1.0):
        """Punto del anillo a fraccion `frac` de vuelta (12 en punto,
        horario), geometria ACTUAL."""
        ang = 0.25 * TAU - TAU * float(frac)
        return (self._ancla.get_center()
                + self._radio_actual() * float(radio_rel)
                * np.array([math.cos(ang), math.sin(ang), 0.0]))

    def nodo(self, nombre):
        return self.nodos[nombre]

    def clave(self, nombre):
        return self.claves[nombre]

    def con_nodo_extra(self, nombre="nodo-nuevo"):
        """El mismo anillo con un nodo mas, anclado por el centro."""
        params = dict(self._params)
        otro = anillo_hash(n_nodos=params["n_nodos"],
                           n_claves=params["n_claves"],
                           radio=params["radio"],
                           nodo_extra=nombre)
        otro.shift(self._ancla.get_center() - otro._ancla.get_center())
        return otro

    def claves_movidas(self, nombre="nodo-nuevo"):
        """Nombres de las claves que cambiarian de duenio si entrara
        ese nodo: MEDIDO comparando asignaciones."""
        claves = list(self.claves.keys())
        nodos = list(self.nodos.keys())
        despues = asignacion_anillo(claves, nodos + [nombre])
        return [c for c in claves if despues[c] != self.asignacion[c]]

    def fraccion_movida(self, nombre="nodo-nuevo"):
        """La cifra del clip 7: fraccion medida de claves reubicadas."""
        return len(self.claves_movidas(nombre)) / max(len(self.claves),
                                                      1)


def anillo_hash(n_nodos=4, n_claves=24, radio=2.1, nodo_extra=None,
                color_anillo=COLOR_TIEMPO, color_nodo=COLOR_NODO,
                color_clave=COLOR_MENSAJE):
    """El anillo de hash consistente: md5 real, nada de posiciones a
    mano. Los nodos son puntos grandes SOBRE el circulo; las claves,
    puntos chicos por dentro. `nodo_extra` agrega "nodo-nuevo" (verde)."""
    n_nodos = _validar("anillo_hash.n_nodos", n_nodos, NODOS_MAX)
    n_claves = _validar("anillo_hash.n_claves", n_claves, CLAVES_MAX)
    radio = float(radio)

    nombres_n = [f"nodo-{j}" for j in range(n_nodos)]
    extra = None
    if nodo_extra is not None:
        extra = str(nodo_extra)
        nombres_n = nombres_n + [extra]
    nombres_c = [f"clave-{i}" for i in range(n_claves)]

    circulo = Circle(radius=radio, stroke_width=2.6, color=color_anillo)

    def punto(frac, radio_rel=1.0):
        ang = 0.25 * TAU - TAU * frac
        return radio * radio_rel * np.array([math.cos(ang),
                                             math.sin(ang), 0.0])

    nodos_g, claves_g = {}, {}
    grupo_n, grupo_c = VGroup(), VGroup()
    for nombre in nombres_n:
        color = COLOR_OK if nombre == extra else color_nodo
        d = Dot(punto(_hash_unidad(nombre)), radius=0.11, color=color)
        nodos_g[nombre] = d
        grupo_n.add(d)
    for nombre in nombres_c:
        d = Dot(punto(_hash_unidad(nombre), 0.82), radius=0.055,
                color=color_clave)
        claves_g[nombre] = d
        grupo_c.add(d)

    params = {"n_nodos": n_nodos, "n_claves": n_claves, "radio": radio,
              "asignacion": asignacion_anillo(nombres_c, nombres_n)}
    pieza = AnilloHash(_ancla(ORIGIN), circulo, grupo_n, grupo_c, params)
    pieza.nodos = nodos_g
    pieza.claves = claves_g
    return pieza


# =====================================================================
# La corona del lider
# =====================================================================
def corona(ancho=0.34, alto=0.22, color=COLOR_MENSAJE):
    """Corona minima para poner sobre el nodo lider (el clip la coloca
    con next_to/shift)."""
    ancho, alto = float(ancho), float(alto)
    w2 = ancho / 2.0
    pieza = Polygon(
        np.array([-w2, 0.0, 0.0]), np.array([w2, 0.0, 0.0]),
        np.array([w2, alto * 0.55, 0.0]),
        np.array([ancho * 0.17, alto * 0.25, 0.0]),
        np.array([0.0, alto, 0.0]),
        np.array([-ancho * 0.17, alto * 0.25, 0.0]),
        np.array([-w2, alto * 0.55, 0.0]),
        stroke_width=2.2, color=color)
    pieza.set_fill(color, opacity=0.35)
    return pieza
