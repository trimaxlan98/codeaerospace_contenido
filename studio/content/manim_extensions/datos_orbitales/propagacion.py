"""SGP4 → TEME → ECEF → geodésicas (WGS-84). Sin movimiento polar (error < 10 m, irrelevante para divulgación)."""
from datetime import datetime, timezone

import numpy as np
from sgp4 import omm as _omm
from sgp4.api import Satrec

OMEGA_T = 7.2921158553e-5          # rad/s, rotación de la Tierra
RT = 6378.137                      # km, radio ecuatorial WGS-84
F = 1 / 298.257223563
E2 = F * (2 - F)


def satrec(el):
    s = Satrec()
    _omm.initialize(s, el.omm)
    return s


def a_unix(t):
    """datetime (con zona; sin zona = UTC), lista de datetimes o array de segundos Unix → array float64 de segundos Unix."""
    if isinstance(t, datetime):
        t = [t]
    t = list(t) if not isinstance(t, np.ndarray) else t
    if len(t) and isinstance(t[0], datetime):
        return np.array([(x if x.tzinfo else x.replace(tzinfo=timezone.utc)).timestamp() for x in t], dtype=np.float64)
    return np.atleast_1d(np.asarray(t, dtype=np.float64))


def jd_fr(unix):
    total = unix / 86400.0 + 2440587.5
    jd = np.floor(total - 0.5) + 0.5
    return jd, total - jd


def gmst(jd, fr):
    """Tiempo sidéreo de Greenwich (rad), IAU-82, con UT1 ≈ UTC."""
    T = (jd + fr - 2451545.0) / 36525.0
    seg = 67310.54841 + (876600.0 * 3600 + 8640184.812866) * T + 0.093104 * T ** 2 - 6.2e-6 * T ** 3
    return np.deg2rad((seg % 86400.0) / 240.0)


def _rz(ang, v):
    c, s = np.cos(ang), np.sin(ang)
    return np.stack([c * v[:, 0] + s * v[:, 1], -s * v[:, 0] + c * v[:, 1], v[:, 2]], axis=1)


def posicion_teme(el, t):
    """r, v (km, km/s) en TEME para cada instante de `t`. Lanza ValueError si SGP4 reporta error."""
    unix = a_unix(t)
    jd, fr = jd_fr(unix)
    e, r, v = satrec(el).sgp4_array(jd, fr)
    if np.any(e != 0):
        raise ValueError(f"SGP4 falló (códigos {sorted(set(e.tolist()))}) para {el.nombre}")
    return r, v


def posicion_ecef(el, t):
    """r, v (km, km/s) en ECEF (v respecto a la Tierra que gira) y los (jd, fr) usados."""
    unix = a_unix(t)
    jd, fr = jd_fr(unix)
    r, v = posicion_teme(el, unix)
    g = gmst(jd, fr)
    r_e = _rz(g, r)
    v_e = _rz(g, v) - np.cross([0, 0, OMEGA_T], r_e)
    return r_e, v_e, jd, fr


def ecef_a_geodetica(r):
    """(lat°, lon°, h km) de posiciones ECEF (N,3), Bowring con 3 iteraciones."""
    x, y, z = r[:, 0], r[:, 1], r[:, 2]
    lon = np.arctan2(y, x)
    p = np.hypot(x, y)
    lat = np.arctan2(z, p * (1 - E2))
    for _ in range(3):
        N = RT / np.sqrt(1 - E2 * np.sin(lat) ** 2)
        h = p / np.cos(lat) - N
        lat = np.arctan2(z, p * (1 - E2 * N / (N + h)))
    N = RT / np.sqrt(1 - E2 * np.sin(lat) ** 2)
    h = p / np.cos(lat) - N
    return np.rad2deg(lat), np.rad2deg(lon), h


def posicion_geodetica(el, t):
    r, _, _, _ = posicion_ecef(el, t)
    return ecef_a_geodetica(r)
