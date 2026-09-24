"""Libreria del curso 37 «Rendimiento de SQL Server» (familia Rendimiento SQL).

Dos fuentes de cifras, y cada una tiene su color en pantalla:

* CALCULADO AQUI (cian). `pedidos()` y `clientes()` reproducen en numpy,
  fila por fila, el generador determinista de la base TiendaPerf
  (optimiza-sql/sql/01_crear_TiendaPerf.sql: HASHBYTES('MD5', CAST(n AS
  BINARY(4))) y SUBSTRING de 3 bytes). Todo conteo (filas del cliente 501,
  cancelados de 2025, densidad del histograma...) se cuenta aqui sobre esa
  reproduccion. La sonda comprueba que coincide con lo que midio el motor
  (el cliente 1 da 149,970 filas: el EQ_ROWS de SQL Server).
* MEDIDO EN EL MOTOR (ambar). Las lecturas logicas, paginas y tiempos de
  `MEDIDO` los midio SQL Server 2025 CU9 (Linux, laptop de 8 nucleos, base
  reiniciada con el script 00) el 23-sep-2026. No se pueden calcular aqui:
  se citan tal cual y se rotulan en su color propio.

Los MODELOS (lecturas de un lookup, punto de inflexion, umbral de
estadisticas) son aritmetica sobre esas dos fuentes y van en cian; la sonda
exige que el modelo caiga cerca de la medicion antes de dejarlo en pantalla.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import math
from functools import lru_cache

import numpy as np

# ---------------------------------------------------------------------
# Constantes del motor (documentacion publica de SQL Server)
# ---------------------------------------------------------------------
PAGINA_KB = 8
PAGINA_UTIL_B = 8096          # bytes de datos por pagina (8192 - cabecera 96)
FILAS_ROWGROUP = 1_048_576    # filas maximas de un rowgroup de columnstore
FILAS_LOTE = 900              # ~filas por lote en modo batch (orden de magnitud)
PASOS_HISTOGRAMA = 200        # pasos maximos de un histograma
UMBRAL_ESCALAMIENTO = 5000    # bloqueos por objeto antes de escalar

# ---------------------------------------------------------------------
# Lo que midio SQL Server 2025 CU9 (ambar en pantalla). Fuente:
# optimiza-sql/guia/guia_instructor.md y app/renderer/contenido/curso.js
# ---------------------------------------------------------------------
MEDIDO = {
    # tamanos
    "paginas_pedidos": 22_183, "paginas_detalle": 17_606,
    "filas_pedidos": 1_500_000, "filas_detalle": 3_750_000,
    "filas_clientes": 200_000, "filas_productos": 2_000,
    # 1 · metodo
    "pk_seek": 3,                    # WHERE id_pedido = 750000
    "scan_pedidos": 22_363,          # clustered scan de pedidos (8 hilos)
    "scan_count_paralelo": 9,        # 8 hilos + coordinador
    # 2 · indices
    "c501_lookup": 597,              # seek + key lookup
    "c1_scan": 22_363,               # el optimizador vuelve al scan
    "c501_cubriente": 4,
    "c1_cubriente": 785,
    "c501_select_estrella": 597,     # SELECT * vuelve al lookup
    "canc2025_fecha_estatus": 1_978,
    "canc2025_estatus_fecha": 161,
    "pendientes_lecturas": 13, "pendientes_paginas": 14,
    "ticket_sin_indice": 18_016, "ticket_con_indice": 3,
    "cs_filas": 16_468, "cs_lob_1hilo": 6_512, "cs_lob_8hilos": 24_700,
    # 4 · sargabilidad
    "year_scan": 7_182, "year_rango": 1_975,
    "cast_date": 17,
    "dateadd_mal": 7_182, "dateadd_bien": 227,
    "email_nvarchar": 960, "email_varchar": 3,
    "like_prefijo": 55, "like_sufijo": 1_012,
    "isnull_mal": 535, "isnull_bien": 3,
    "or_dos_seeks": 14,
    # 5 · estimaciones
    "eq_rows_c1": 149_970,
    "variable_local": 450_173, "literal_c1": 22_363,
    "tvar_140_s": 1.8, "tvar_170_s": 0.67,
    "udf_140_s": 17.6, "udf_170_s": 0.85,
    # 6 · parametros
    "sniff_501_luego_1": (597, 459_555),
    "sniff_1_luego_501": (22_363, 22_363),
    "remedio_indice": (6, 1_974),
    "psp_variantes": 0,
    "oppo_variantes": 2, "catchall_sin_oppo": 20_010, "catchall_oppo": 6,
    "catchall_otros": 20_005, "dinamico": 6,
    # 7 · produccion
    "error_abort": 8778, "error_deadlock": 1205,
    "caso_antes_s": 53.0, "caso_despues_s": 3.9,
    "caso_peticiones": 300,
}

INICIO = _dt.date(2021, 1, 1)             # dia 0 de fecha_pedido
CORTE_RECIENTES = _dt.date(2026, 9, 14)   # desde aqui: pendiente | enviado
ESTATUS = ("pendiente", "enviado", "entregado", "cancelado")
METODOS = ("tarjeta",) * 6 + ("transferencia",) * 2 + ("efectivo",) * 2
APELLIDOS = ("Hernandez", "Garcia", "Martinez", "Lopez", "Gonzalez", "Perez",
             "Rodriguez", "Sanchez", "Ramirez", "Cruz", "Flores", "Gomez",
             "Morales", "Vazquez", "Reyes", "Jimenez", "Torres", "Diaz",
             "Ruiz", "Mendoza")
DOMINIOS = ("gmail.com", "hotmail.com", "outlook.com", "yahoo.com.mx")


def dia(fecha) -> int:
    """Dias desde 2021-01-01 (la escala de `pedidos()['dia']`)."""
    if isinstance(fecha, str):
        fecha = _dt.date.fromisoformat(fecha)
    return (fecha - INICIO).days


# ---------------------------------------------------------------------
# Reproduccion de TiendaPerf
# ---------------------------------------------------------------------
def _md5_bytes(inicio: int, n: int, desplazamiento: int = 0) -> np.ndarray:
    """HASHBYTES('MD5', CAST(k AS BINARY(4))) para k = inicio..inicio+n-1
    (+ desplazamiento). El INT se castea big-endian."""
    out = np.empty((n, 16), dtype=np.uint8)
    md5 = hashlib.md5
    for i in range(n):
        out[i] = np.frombuffer(
            md5((inicio + i + desplazamiento).to_bytes(4, "big")).digest(),
            dtype=np.uint8)
    return out


def _sub3(h: np.ndarray, a: int) -> np.ndarray:
    """CAST(SUBSTRING(h, a+1, 3) AS INT): 3 bytes big-endian."""
    return ((h[:, a].astype(np.int64) << 16) | (h[:, a + 1].astype(np.int64) << 8)
            | h[:, a + 2].astype(np.int64))


@lru_cache(maxsize=1)
def pedidos() -> dict:
    """Los 1,500,000 pedidos, EN ORDEN DE id_pedido (el INSERT va ORDER BY
    fecha, n sobre una llave IDENTITY). Arrays:
    id_cliente, dia (desde 2021-01-01), seg (del dia), estatus (0..3 de
    ESTATUS), metodo (indice de METODOS), comentario (bool)."""
    n = MEDIDO["filas_pedidos"]
    h = _md5_bytes(1, n, 1_000_000_000)
    r1, r2, r3, r4 = _sub3(h, 0), _sub3(h, 4), _sub3(h, 8), _sub3(h, 12)
    m10 = r1 % 10
    cli = np.where(m10 == 0, 1,
                   np.where((m10 == 1) | (m10 == 2), 2 + (r2 % 1999),
                            2001 + (r2 % 188000)))
    d = np.floor(2088 * np.sqrt((r3 % 1_000_000) / 1_000_000.0)).astype(np.int64)
    seg = r4 % 86400
    corte = dia(CORTE_RECIENTES)
    est = np.where(d >= corte, np.where(r2 % 3 == 0, 0, 1),
                   np.where(r4 % 100 < 8, 3, 2))
    met = (r1 // 10) % 10
    com = (r3 % 10) < 3
    orden = np.lexsort((np.arange(n), d * 86400 + seg))
    return {"id_cliente": cli[orden], "dia": d[orden], "seg": seg[orden],
            "estatus": est[orden], "metodo": met[orden],
            "comentario": com[orden]}


@lru_cache(maxsize=1)
def clientes() -> dict:
    """Los 200,000 clientes en orden de id. Arrays: apellido (indice de
    APELLIDOS), dominio (indice de DOMINIOS), telefono_nulo (bool),
    telefono (int, -1 si es NULL), mayorista (bool)."""
    n = MEDIDO["filas_clientes"]
    h = _md5_bytes(1, n)
    r1, r3, r4 = _sub3(h, 0), _sub3(h, 8), _sub3(h, 12)
    ids = np.arange(1, n + 1)
    ap = (r1 // 30) % 20
    ap[0] = -1                                   # el cliente 1 es la distribuidora
    nulo = (r4 % 5) == 0
    tel = np.where(nulo, -1, 5_500_000_000 + (r4 % 100_000_000))
    return {"apellido": ap, "dominio": r3 % 4, "telefono_nulo": nulo,
            "telefono": tel, "mayorista": ids <= 2000}


def email(id_cliente: int) -> str:
    if id_cliente == 1:
        return "compras@mayoristacentro.mx"
    return f"cliente{id_cliente}@{DOMINIOS[int(clientes()['dominio'][id_cliente - 1])]}"


def lineas_detalle(id_pedido) -> np.ndarray:
    """Renglones de detalle de un pedido: 1 + (CHECKSUM(id*13) & 0x7FFFFFFF) % 4.
    SUPUESTO: CHECKSUM de un solo INT devuelve el propio entero. La sonda
    solo verifica el TOTAL (3,750,000), y cualquier multiplicador impar da
    ese mismo total: el conteo de UN pedido concreto NO esta validado y no
    se rotula en pantalla. Usala solo para totales."""
    x = (np.asarray(id_pedido, dtype=np.int64) * 13) & 0x7FFFFFFF
    return 1 + x % 4


# ---------------------------------------------------------------------
# Conteos (cian)
# ---------------------------------------------------------------------
def filas_cliente(c: int) -> int:
    return int((pedidos()["id_cliente"] == c).sum())


@lru_cache(maxsize=1)
def _frecuencias():
    ids, cnt = np.unique(pedidos()["id_cliente"], return_counts=True)
    return ids, cnt


def clientes_distintos() -> int:
    return int(len(_frecuencias()[0]))


def densidad() -> float:
    """All density del indice por id_cliente: 1 / valores distintos."""
    return 1.0 / clientes_distintos()


def estimado_variable() -> float:
    """Filas que estima el optimizador para `id_cliente = @variable`:
    filas x densidad (no conoce el valor al compilar)."""
    return MEDIDO["filas_pedidos"] * densidad()


def filas_rango(desde, hasta, estatus: str | None = None) -> int:
    """Pedidos con desde <= fecha < hasta (fechas ISO), opcionalmente de un estatus."""
    p = pedidos()
    m = (p["dia"] >= dia(desde)) & (p["dia"] < dia(hasta))
    if estatus is not None:
        m &= p["estatus"] == ESTATUS.index(estatus)
    return int(m.sum())


def filas_estatus(estatus: str) -> int:
    return int((pedidos()["estatus"] == ESTATUS.index(estatus)).sum())


def fraccion_estatus() -> dict:
    n = MEDIDO["filas_pedidos"]
    return {e: filas_estatus(e) / n for e in ESTATUS}


def filas_dia(fecha) -> int:
    return int((pedidos()["dia"] == dia(fecha)).sum())


def filas_apellido(apellido: str) -> int:
    return int((clientes()["apellido"] == APELLIDOS.index(apellido)).sum())


def filas_telefono(numero: int) -> int:
    return int((clientes()["telefono"] == numero).sum())


def telefonos_nulos() -> int:
    return int(clientes()["telefono_nulo"].sum())


def pedidos_por_dia() -> tuple[np.ndarray, np.ndarray]:
    """(dias, pedidos de ese dia): la densidad crece hacia el presente."""
    d = pedidos()["dia"]
    return np.arange(d.max() + 1), np.bincount(d)


def detalle_total() -> int:
    return int(lineas_detalle(np.arange(1, MEDIDO["filas_pedidos"] + 1)).sum())


# ---------------------------------------------------------------------
# Histograma (modelo)
# ---------------------------------------------------------------------
def histograma(pasos: int = PASOS_HISTOGRAMA) -> list[dict]:
    """Histograma de id_cliente al estilo de SQL Server, con FULLSCAN:
    a lo sumo `pasos` pasos; cada paso termina en RANGE_HI_KEY, cuenta sus
    iguales (EQ_ROWS) y lo que queda entre el paso anterior y el
    (RANGE_ROWS, DISTINCT_RANGE_ROWS). Los valores mas pesados se quedan
    con un paso propio. Es un MODELO del algoritmo (el del motor es
    propietario): el EQ_ROWS de un valor con paso propio es exacto."""
    ids, cnt = _frecuencias()
    n = cnt.sum()
    objetivo = n / pasos
    # pasos propios para los valores que por si solos llenan un paso
    fijos = set(ids[cnt >= objetivo].tolist())
    fijos.add(int(ids[0]))
    fijos.add(int(ids[-1]))
    res, acum, dist = [], 0, 0
    for k, c in zip(ids.tolist(), cnt.tolist()):
        if k in fijos or acum + c >= objetivo:
            res.append({"hi": k, "eq": c, "range": acum, "distinct": dist})
            acum, dist = 0, 0
        else:
            acum += c
            dist += 1
    return res[:pasos]


def paso_de(histo: list[dict], valor: int) -> dict:
    for p in histo:
        if valor <= p["hi"]:
            return p
    return histo[-1]


def umbral_estadisticas(filas: int) -> float:
    """Umbral dinamico de auto-actualizacion (SQL 2016+): RAIZ(1000 x filas)."""
    return math.sqrt(1000.0 * filas)


def umbral_estadisticas_viejo(filas: int) -> float:
    """El de antes: 500 + 20 % de las filas."""
    return 500 + 0.20 * filas


# ---------------------------------------------------------------------
# Modelos de lecturas (cian) — la sonda los contrasta con MEDIDO
# ---------------------------------------------------------------------
def filas_por_pagina(filas: int, paginas: int) -> float:
    return filas / paginas


def bytes_por_fila(filas: int, paginas: int) -> float:
    return PAGINA_UTIL_B * paginas / filas


def profundidad(filas: int, filas_hoja: float, fanout: float) -> int:
    """Niveles de un arbol B: hojas = filas / filas_hoja; cada nivel de
    arriba divide entre `fanout` hasta que queda una pagina (la raiz)."""
    paginas = math.ceil(filas / filas_hoja)
    niveles = 1
    while paginas > 1:
        paginas = math.ceil(paginas / fanout)
        niveles += 1
    return niveles


def fanout_int(bytes_llave: int = 4) -> int:
    """Entradas por pagina de un nivel intermedio: llave + puntero de
    pagina (6) + cabecera de fila (~1) + ranura (2)."""
    return PAGINA_UTIL_B // (bytes_llave + 6 + 1 + 2)


def lecturas_lookup(filas: int, prof: int = 3) -> int:
    """Un key lookup por fila, cada uno baja `prof` niveles del agrupado."""
    return filas * prof


def lecturas_seek_lookup(filas: int, prof_nc: int = 3, prof_cl: int = 3) -> int:
    return prof_nc + lecturas_lookup(filas, prof_cl)


def punto_inflexion(lecturas_scan: int | None = None, prof: int = 3) -> dict:
    """Filas a partir de las cuales los lookups cuestan mas que el scan."""
    s = MEDIDO["scan_pedidos"] if lecturas_scan is None else lecturas_scan
    filas = s / prof
    return {"filas": filas, "fraccion": filas / MEDIDO["filas_pedidos"]}


def rowgroups(filas: int = MEDIDO["filas_detalle"]) -> int:
    return math.ceil(filas / FILAS_ROWGROUP)


def razon(a: float, b: float) -> float:
    return a / b


def miles(x) -> str:
    """Entero con separador de miles: 22363 -> '22,363'."""
    return f"{int(round(x)):,}"


# =====================================================================
# Dibujo (manim se importa aqui abajo para que la parte numerica sirva
# sin manim, p. ej. en la sonda)
# =====================================================================
try:
    from manim import (DOWN, LEFT, RIGHT, UP, ORIGIN, Arrow, DashedLine, Line,
                       Rectangle, RoundedRectangle, Text, VGroup, VMobject,
                       config)
except Exception:          # pragma: no cover - sonda sin manim
    VGroup = None

# Paleta por ROL (el style_block la re-exporta con sus nombres C_*)
CIAN = "#22d3ee"        # calculado aqui
AMBAR = "#f59e0b"       # medido en el motor
TINTA = "#e8edf3"
TENUE = "#94a0b0"
VERDE = "#34d399"       # el camino barato: seek, plan bueno
ROJO = "#f43f5e"        # el camino caro: scan de mas, plan malo
AZUL = "#3b82f6"        # un indice (estructura)
VIOLETA = "#a78bfa"     # lo que el optimizador CREE (estimacion)
FONDO_PANEL = "#0b1119"
MONO = "Space Mono"


def texto(*args, **kwargs):
    """Text sin los glifos vacios de los espacios: en manim 0.20.1 quedan
    anclados en el origen e inflan el bounding box (y descuadran cualquier
    indice de glifo). TODA pieza de esta libreria crea su texto aqui."""
    t = Text(*args, **kwargs)
    t.submobjects = [g for g in t.submobjects if g.has_points()]
    return t


def pagina(ancho=0.5, alto=0.66, renglones=5, color=TENUE, relleno=0.0,
           grosor=2.0):
    """Una pagina de 8 KB: marco, franja de cabecera y renglones."""
    marco = Rectangle(width=ancho, height=alto, stroke_color=color,
                      stroke_width=grosor, fill_color=color,
                      fill_opacity=relleno)
    cab = Line(marco.get_corner(UP + LEFT) + DOWN * alto * 0.16,
               marco.get_corner(UP + RIGHT) + DOWN * alto * 0.16,
               stroke_color=color, stroke_width=grosor * 0.8)
    filas = VGroup()
    for k in range(renglones):
        y = alto * (0.5 - 0.16) - (k + 1) * alto * 0.84 / (renglones + 1)
        filas.add(Line(LEFT * ancho * 0.36 + UP * y, RIGHT * ancho * 0.36 + UP * y,
                       stroke_color=color, stroke_width=grosor * 0.6,
                       stroke_opacity=0.7))
    filas.move_to(marco.get_center() + DOWN * alto * 0.08)
    g = VGroup(marco, cab, filas)
    g.marco = marco
    return g


class MuroPaginas(VGroup):
    """Un muro de `columnas x filas` paginas pequenas: la tabla entera.
    `celda(i)` da la i-esima en orden de lectura (por renglones)."""

    def __init__(self, columnas=24, filas=10, lado=0.22, sep=0.06,
                 color=TENUE, opacidad=0.18, **kw):
        super().__init__(**kw)
        for j in range(filas):
            for i in range(columnas):
                r = Rectangle(width=lado, height=lado * 1.3, stroke_width=1.2,
                              stroke_color=color, fill_color=color,
                              fill_opacity=opacidad)
                r.move_to(RIGHT * i * (lado + sep) + DOWN * j * (lado * 1.3 + sep))
                self.add(r)
        self.columnas, self.filas = columnas, filas
        self.move_to(ORIGIN)

    def celda(self, i):
        return self.submobjects[i]

    def encender(self, indices, color, opacidad=0.85):
        """Animaciones para iluminar un conjunto de celdas."""
        return [self.submobjects[i].animate.set_fill(color, opacidad)
                .set_stroke(color) for i in indices]


class ArbolB(VGroup):
    """Arbol B de `len(anchos)` niveles: raiz arriba, hojas abajo.
    `anchos` = paginas dibujadas por nivel (p. ej. (1, 4, 12)). Las hojas
    quedan en orden de llave, de izquierda a derecha."""

    def __init__(self, anchos=(1, 4, 12), ancho=10.0, alto=3.6, lado=0.42,
                 color=AZUL, **kw):
        super().__init__(**kw)
        self.niveles = []
        n_niv = len(anchos)
        for k, m in enumerate(anchos):
            y = alto / 2 - k * alto / max(n_niv - 1, 1)
            fila = VGroup()
            paso = ancho / m
            for i in range(m):
                x = -ancho / 2 + paso * (i + 0.5)
                fila.add(pagina(lado, lado * 1.3, renglones=3, color=color,
                                grosor=1.6).move_to([x, y, 0]))
            self.niveles.append(fila)
        self.aristas = VGroup()
        self._padre = []
        for k in range(1, n_niv):
            arriba, abajo = self.niveles[k - 1], self.niveles[k]
            mapa = []
            for i, hijo in enumerate(abajo):
                p = min(int(i * len(arriba) / len(abajo)), len(arriba) - 1)
                mapa.append(p)
                self.aristas.add(Line(arriba[p].get_bottom(), hijo.get_top(),
                                      stroke_color=color, stroke_width=1.4,
                                      stroke_opacity=0.55))
            self._padre.append(mapa)
        self.add(self.aristas, *self.niveles)
        self.hojas = self.niveles[-1]

    def ruta(self, hoja: int) -> list:
        """Paginas de la raiz a la hoja `hoja` (una por nivel)."""
        idx = [hoja]
        for mapa in reversed(self._padre):
            idx.append(mapa[idx[-1]])
        idx.reverse()
        return [self.niveles[k][i] for k, i in enumerate(idx)]


def contador_texto(valor, color=AMBAR, font_size=40, digitos=7):
    """Numero con separador de miles, ancho fijo (monoespaciado)."""
    s = f"{int(round(valor)):,}"
    return texto(s, font=MONO, font_size=font_size, color=color)


def barra_lecturas(valor, maximo, largo=8.0, alto=0.36, color=AMBAR,
                   log=True):
    """Barra horizontal (anclada a la izquierda en ORIGIN) proporcional a
    `valor`; en escala log10 si `log` (1 lectura = casi nada)."""
    if log:
        f = math.log10(max(valor, 1)) / math.log10(max(maximo, 10))
    else:
        f = valor / maximo
    w = max(largo * f, 0.04)
    r = Rectangle(width=w, height=alto, stroke_width=0, fill_color=color,
                  fill_opacity=0.9)
    r.move_to(ORIGIN, aligned_edge=LEFT)
    return r


def flecha_plan(inicio, fin, filas, color=TENUE, max_filas=1_500_000):
    """Flecha de un plan (de derecha a izquierda): el GROSOR es el numero
    de filas, en escala log10, como en el visor de planes."""
    g = 1.5 + 10.5 * math.log10(max(filas, 1)) / math.log10(max_filas)
    return Arrow(inicio, fin, buff=0.08, stroke_width=g, color=color,
                 max_tip_length_to_length_ratio=0.12,
                 max_stroke_width_to_length_ratio=40)


def operador(nombre, color=TINTA, ancho=2.3, alto=0.78, font_size=22):
    """Caja de un operador del plan (nombre en ASCII, <= 3 palabras)."""
    caja = RoundedRectangle(width=ancho, height=alto, corner_radius=0.1,
                            stroke_color=color, stroke_width=2.2,
                            fill_color=FONDO_PANEL, fill_opacity=0.95)
    t = texto(nombre, font_size=font_size, color=color)
    if t.width > ancho - 0.25:
        t.scale_to_fit_width(ancho - 0.25)
    t.move_to(caja)
    g = VGroup(caja, t)
    g.caja, g.texto = caja, t
    return g


_CLAVES = {"SELECT", "FROM", "WHERE", "AND", "OR", "JOIN", "ON", "GROUP", "BY",
           "ORDER", "TOP", "INCLUDE", "CREATE", "INDEX", "EXEC", "DECLARE",
           "LIKE", "IS", "NULL", "OPTION", "UNION", "BEGIN", "TRAN", "UPDATE",
           "SET", "AS", "IN", "WITH", "NOT", "COUNT", "SUM", "INT", "VARCHAR",
           "NVARCHAR", "DATE", "CAST", "YEAR", "ISNULL", "DATEADD", "DESC",
           "RECOMPILE", "OPTIMIZE", "FOR", "ROLLBACK", "COMMIT", "IF", "ALTER",
           "PROCEDURE", "WHILE", "COLUMNSTORE", "NONCLUSTERED", "CONVERT"}

MAX_LINEAS_CODIGO = 5
MAX_CHARS_CODIGO = 46


LITERAL = "#f0abfc"     # literales del codigo: fucsia claro (NO es ambar:
                        # el ambar es solo lo que midio el motor)


def codigo(lineas, font_size=22, ancho=None, color=TINTA, clave=AZUL,
           literal=LITERAL):
    """Panel de T-SQL: palabras clave en azul, literales ('..', numeros
    sueltos) en fucsia claro, el resto en tinta. Maximo 5 lineas de 46
    caracteres: es CODIGO, no prosa; lo que no quepa va en la voz."""
    if isinstance(lineas, str):
        lineas = [lineas]
    if len(lineas) > MAX_LINEAS_CODIGO:
        raise ValueError(f"codigo(): {len(lineas)} lineas (max {MAX_LINEAS_CODIGO})")
    filas = VGroup()
    for ln in lineas:
        if len(ln) > MAX_CHARS_CODIGO:
            raise ValueError(f"codigo(): linea de {len(ln)} caracteres "
                             f"(max {MAX_CHARS_CODIGO}): {ln!r}")
        if any(ord(c) > 127 for c in ln):
            raise ValueError(f"codigo(): solo ASCII: {ln!r}")
        t = texto(ln if ln.strip() else ".", font=MONO, font_size=font_size,
                 color=color)
        if not ln.strip():
            t.set_opacity(0)
        else:
            _colorear(t, ln, clave, literal)
        filas.add(t)
    filas.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
    w = (ancho or filas.width + 0.6)
    fondo = RoundedRectangle(width=w, height=filas.height + 0.5,
                             corner_radius=0.08, stroke_color=TENUE,
                             stroke_width=1.2, stroke_opacity=0.5,
                             fill_color=FONDO_PANEL, fill_opacity=0.96)
    filas.move_to(fondo).align_to(fondo, LEFT).shift(RIGHT * 0.3)
    g = VGroup(fondo, filas)
    g.fondo, g.lineas = fondo, filas
    return g


def _colorear(t, ln, clave, literal):
    """Colorea por token. `texto()` ya quito los glifos de los espacios,
    asi que el indice de glifo avanza solo con caracteres no blancos."""
    glifos = [s for s in t.submobjects]
    k = 0
    i = 0
    n = len(ln)
    while i < n:
        c = ln[i]
        if c.isspace():
            i += 1
            continue
        j = i
        if c == "'":
            j = ln.find("'", i + 1)
            j = n - 1 if j < 0 else j
            tok, col = ln[i:j + 1], literal
            j += 1
        elif c.isalnum() or c in "_@":
            while j < n and (ln[j].isalnum() or ln[j] in "_@"):
                j += 1
            tok = ln[i:j]
            col = (clave if tok.upper() in _CLAVES
                   else literal if tok.isdigit() else None)
        else:
            tok, col = c, None
            j = i + 1
        largo = sum(1 for ch in tok if not ch.isspace())
        if col is not None:
            for g in glifos[k:k + largo]:
                g.set_color(col)
        k += largo
        i = j


def marco_datos(ancho, alto, color=TENUE):
    """Marco simple (sin ejes de manim) para una grafica hecha a mano."""
    return Rectangle(width=ancho, height=alto, stroke_color=color,
                     stroke_width=1.5, stroke_opacity=0.6)
