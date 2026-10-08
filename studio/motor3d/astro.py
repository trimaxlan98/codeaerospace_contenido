"""Astronomía mínima para el render: Sol, rotación de la Tierra, sombra y cuaterniones.

Marco del mundo = TEME (el de SGP4), en radios terrestres (R = 6378.137 km).
"""
import math
from datetime import datetime, timezone

import numpy as np

R_TIERRA_KM = 6378.137


def jd(utc: datetime) -> float:
    """Fecha juliana (UTC tomado como UT1: error < 1 s, despreciable para dibujar)."""
    if utc.tzinfo is None:
        utc = utc.replace(tzinfo=timezone.utc)
    return utc.timestamp() / 86400.0 + 2440587.5


def gmst(jdu: float) -> float:
    """GMST IAU-82 en rad (la misma rotación que usa SGP4 para TEME -> ECEF)."""
    t = (jdu - 2451545.0) / 36525.0
    s = 67310.54841 + (876600.0 * 3600 + 8640184.812866) * t + 0.093104 * t * t - 6.2e-6 * t ** 3
    return math.radians((s % 86400.0) / 240.0) % (2 * math.pi)


def sol_teme(jdu: float) -> np.ndarray:
    """Dirección unitaria al Sol (Almanaque Astronómico, ~0.01°; TEME ≈ ecuatorial de la fecha, < 0.4°)."""
    n = jdu - 2451545.0
    L = math.radians((280.460 + 0.9856474 * n) % 360)
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lam = L + math.radians(1.915) * math.sin(g) + math.radians(0.020) * math.sin(2 * g)
    eps = math.radians(23.439 - 4e-7 * n)
    return np.array([math.cos(lam), math.cos(eps) * math.sin(lam), math.sin(eps) * math.sin(lam)])


def rz(a: float) -> np.ndarray:
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])


def sombra_cilindrica(r: np.ndarray, sol: np.ndarray, suave_km: float = 0.0) -> float:
    """Iluminación 0..1 con la sombra cilíndrica (el mismo modelo de sat_adcs: sin penumbra).

    `r` en radios terrestres. `suave_km` > 0 suaviza el borde solo para el dibujo."""
    s = float(np.dot(r, sol))
    if s >= 0:
        return 1.0
    d = float(np.linalg.norm(r - s * sol))          # distancia al eje de la sombra
    if suave_km <= 0:
        return 1.0 if d > 1.0 else 0.0
    w = suave_km / R_TIERRA_KM
    return float(np.clip((d - 1.0) / w + 0.5, 0.0, 1.0))


def geodetica_a_ecef(lat_deg, lon_deg, alt_km=0.0):
    """WGS-84 -> ECEF en radios terrestres."""
    a, f = 1.0, 1 / 298.257223563
    e2 = f * (2 - f)
    la, lo = math.radians(lat_deg), math.radians(lon_deg)
    n = a / math.sqrt(1 - e2 * math.sin(la) ** 2)
    h = alt_km / R_TIERRA_KM
    return np.array([(n + h) * math.cos(la) * math.cos(lo), (n + h) * math.cos(la) * math.sin(lo),
                     (n * (1 - e2) + h) * math.sin(la)])


# ---------- cuaterniones (escalar primero, Hamilton; q = cuerpo -> inercial, como sat_adcs) ----------
def q_a_matriz(q) -> np.ndarray:
    w, x, y, z = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
                     [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
                     [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]])


def slerp(q0, q1, u):
    q0, q1 = np.asarray(q0, float), np.asarray(q1, float)
    d = float(np.dot(q0, q1))
    if d < 0:                       # el camino corto (q y -q son la misma actitud)
        q1, d = -q1, -d
    if d > 0.9995:
        q = q0 + u * (q1 - q0)
        return q / np.linalg.norm(q)
    th = math.acos(d)
    return (math.sin((1 - u) * th) * q0 + math.sin(u * th) * q1) / math.sin(th)


def angulo_entre(q0, q1) -> float:
    """Ángulo (rad) de la rotación que lleva q0 a q1."""
    d = abs(float(np.dot(q0, q1)) / (np.linalg.norm(q0) * np.linalg.norm(q1)))
    return 2 * math.acos(min(1.0, d))
