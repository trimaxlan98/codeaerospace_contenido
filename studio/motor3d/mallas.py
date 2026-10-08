"""Geometría: esfera UV, cajas con material, cilindros, conos y el CubeSat 3U.

Toda malla es un arreglo float32 de vértices intercalados:
pos(3) normal(3) uv(2) albedo(3) metal rugosidad tipo   -> 14 floats.
`tipo`: 0 liso, 1 celdas solares (rejilla), 2 reflectarray (parches), 3 emisivo.
"""
import math

import numpy as np

CAMPOS = "3f 3f 2f 3f 1f 1f 1f"
ATRIBUTOS = ("in_pos", "in_nrm", "in_uv", "in_alb", "in_met", "in_rug", "in_tipo")


def esfera(nlon=256, nlat=128, radio=1.0):
    """Esfera UV en ECEF: u = (lon+180)/360, v = (90-lat)/180 (equirectangular, norte arriba)."""
    lon = np.linspace(-math.pi, math.pi, nlon + 1)
    lat = np.linspace(math.pi / 2, -math.pi / 2, nlat + 1)
    LO, LA = np.meshgrid(lon, lat)
    p = np.stack([np.cos(LA) * np.cos(LO), np.cos(LA) * np.sin(LO), np.sin(LA)], -1)
    uv = np.stack([(LO + math.pi) / (2 * math.pi), (math.pi / 2 - LA) / math.pi], -1)
    v = np.concatenate([p * radio, p, uv], -1).reshape(-1, 8)
    i = np.arange((nlat + 1) * (nlon + 1)).reshape(nlat + 1, nlon + 1)
    a, b, c, d = i[:-1, :-1], i[:-1, 1:], i[1:, :-1], i[1:, 1:]
    tri = np.stack([a, c, b, b, c, d], -1).reshape(-1)
    return v[tri].astype("f4")


def _material(v8, alb, met=0.0, rug=0.6, tipo=0):
    n = len(v8)
    m = np.tile(np.array([*alb, met, rug, tipo], "f4"), (n, 1))
    return np.concatenate([v8, m], 1).astype("f4")


def caja(centro, tam, alb, met=0.0, rug=0.6, tipo=0, tipo_caras=None):
    """Caja alineada; `tipo_caras` = {'+x': tipo, ...} para dar material distinto por cara."""
    cx, cy, cz = centro
    sx, sy, sz = (t / 2 for t in tam)
    caras = {
        "+x": ((1, 0, 0), [(sx, -sy, -sz), (sx, sy, -sz), (sx, sy, sz), (sx, -sy, sz)]),
        "-x": ((-1, 0, 0), [(-sx, sy, -sz), (-sx, -sy, -sz), (-sx, -sy, sz), (-sx, sy, sz)]),
        "+y": ((0, 1, 0), [(sx, sy, -sz), (-sx, sy, -sz), (-sx, sy, sz), (sx, sy, sz)]),
        "-y": ((0, -1, 0), [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, -sy, sz), (-sx, -sy, sz)]),
        "+z": ((0, 0, 1), [(-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]),
        "-z": ((0, 0, -1), [(-sx, sy, -sz), (sx, sy, -sz), (sx, -sy, -sz), (-sx, -sy, -sz)]),
    }
    out = []
    for nombre, (n, q) in caras.items():
        q = [np.add(p, (cx, cy, cz)) for p in q]
        uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
        v = [np.concatenate([q[k], n, uvs[k]]) for k in (0, 1, 2, 0, 2, 3)]
        t = (tipo_caras or {}).get(nombre, tipo)
        out.append(_material(np.array(v, "f4"), alb, met, rug, t))
    return np.concatenate(out)


def cilindro(p0, p1, radio, alb, met=0.8, rug=0.35, tipo=0, n=24):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    eje = p1 - p0
    L = np.linalg.norm(eje)
    w = eje / L
    u = np.cross(w, [0, 0, 1] if abs(w[2]) < 0.9 else [1, 0, 0])
    u /= np.linalg.norm(u)
    v = np.cross(w, u)
    out = []
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        n0, n1 = math.cos(a0) * u + math.sin(a0) * v, math.cos(a1) * u + math.sin(a1) * v
        A, B, C, D = p0 + radio * n0, p0 + radio * n1, p1 + radio * n1, p1 + radio * n0
        for p, nn, uv in ((A, n0, (k / n, 0)), (B, n1, ((k + 1) / n, 0)), (C, n1, ((k + 1) / n, 1)),
                          (A, n0, (k / n, 0)), (C, n1, ((k + 1) / n, 1)), (D, n0, (k / n, 1))):
            out.append(np.concatenate([p, nn, uv]))
        for c, nn, P, Q in ((p0, -w, B, A), (p1, w, D, C)):      # tapas
            for p in (c, P, Q):
                out.append(np.concatenate([p, nn, (0.5, 0.5)]))
    return _material(np.array(out, "f4"), alb, met, rug, tipo)


def cubesat_3u():
    """CubeSat 3U de sat_adcs: 100×100×340 mm, +Z = bore-sight de la antena.

    La antena es el reflectarray desplegable de 0.3 m (README de sat_adcs: supuesto de la misión);
    rieles, celdas y alimentador son ILUSTRATIVOS (la simulación no los modela)."""
    a, L = 0.100, 0.340
    partes = [caja((0, 0, 0), (a - 0.004, a - 0.004, L - 0.01), (0.05, 0.07, 0.16), 0.3, 0.35, 1,
                   tipo_caras={"+z": 0, "-z": 0})]
    al = (0.80, 0.80, 0.82)
    for sx in (-1, 1):                                        # rieles de aluminio
        for sy in (-1, 1):
            partes.append(caja((sx * (a / 2 - 0.004), sy * (a / 2 - 0.004), 0), (0.0085, 0.0085, L), al, 0.9, 0.3))
    partes.append(caja((0, 0, -L / 2 + 0.003), (a, a, 0.006), al, 0.9, 0.4))
    partes.append(caja((0, 0, L / 2 - 0.003), (a, a, 0.006), al, 0.9, 0.4))
    # reflectarray de 0.3 m en +Z, sobre dos brazos; alimentador en el foco
    z_pan = L / 2 + 0.018
    partes.append(caja((0, 0, z_pan), (0.30, 0.30, 0.005), (0.80, 0.55, 0.20), 0.85, 0.3, 2))
    partes.append(caja((0, 0, z_pan - 0.004), (0.30, 0.30, 0.003), (0.15, 0.15, 0.17), 0.2, 0.7))
    for s in (-1, 1):
        partes.append(cilindro((s * 0.03, 0, L / 2), (s * 0.03, 0, z_pan), 0.004, al))
    for ang in (0, 120, 240):                                 # trípode del alimentador
        r = 0.13
        x, y = r * math.cos(math.radians(ang)), r * math.sin(math.radians(ang))
        partes.append(cilindro((x, y, z_pan), (0, 0, z_pan + 0.20), 0.0025, (0.85, 0.85, 0.85), 0.7, 0.4))
    partes.append(cilindro((0, 0, z_pan + 0.19), (0, 0, z_pan + 0.23), 0.012, (0.9, 0.9, 0.9), 0.6, 0.3))
    return np.concatenate(partes).astype("f4")


def cono(apice, eje, largo, semiangulo_rad, n=64):
    """Cono abierto (haz de antena) en coordenadas del mundo: pos, normal, uv (v = 0 en el ápice)."""
    apice, eje = np.asarray(apice, float), np.asarray(eje, float) / np.linalg.norm(eje)
    u = np.cross(eje, [0, 0, 1] if abs(eje[2]) < 0.9 else [1, 0, 0])
    u /= np.linalg.norm(u)
    v = np.cross(eje, u)
    R = largo * math.tan(semiangulo_rad)
    out = []
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        b0 = apice + largo * eje + R * (math.cos(a0) * u + math.sin(a0) * v)
        b1 = apice + largo * eje + R * (math.cos(a1) * u + math.sin(a1) * v)
        n0 = math.cos(a0) * u + math.sin(a0) * v
        n1 = math.cos(a1) * u + math.sin(a1) * v
        for p, nn, uv in ((apice, n0, (k / n, 0)), (b0, n0, (k / n, 1)), (b1, n1, ((k + 1) / n, 1))):
            out.append(np.concatenate([p, nn, uv]))
    return np.array(out, "f4")


def estrellas(n=9000, semilla=73):
    """Campo de estrellas determinista (procedural, NO un catálogo): más denso en el plano galáctico real.

    Devuelve (dirs Nx3 en ecuatoriales, brillo N, color Nx3)."""
    rng = np.random.default_rng(semilla)
    # polo norte galáctico (J2000): AR 192.86°, Dec 27.13°
    ra, de = math.radians(192.86), math.radians(27.13)
    polo = np.array([math.cos(de) * math.cos(ra), math.cos(de) * math.sin(ra), math.sin(de)])
    d = rng.normal(size=(n * 3, 3))
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    b = np.abs(d @ polo)                                        # |sin latitud galáctica|
    keep = rng.random(n * 3) < (0.25 + 0.75 * np.exp(-(b / 0.18) ** 2))
    d = d[keep][:n]
    mag = rng.power(0.22, len(d))                               # muchas débiles, pocas brillantes
    brillo = 0.05 + 2.2 * (1 - mag) ** 6
    temp = rng.random(len(d))
    color = np.where(temp[:, None] < 0.15, [0.75, 0.82, 1.0], np.where(temp[:, None] > 0.85, [1.0, 0.85, 0.7], [1, 1, 1]))
    return d.astype("f4"), brillo.astype("f4"), color.astype("f4")
