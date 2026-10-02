"""Observador en tierra: az/el/rango/velocidad radial, pases (AOS/TCA/LOS) y visibilidad óptica."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np

from .propagacion import E2, RT, a_unix, gmst, jd_fr, posicion_ecef


@dataclass(frozen=True)
class Observador:
    lat: float
    lon: float
    alt_m: float = 0.0
    nombre: str = "Observador"
    tz: str = "UTC"
    redondeo_deg: float | None = None      # privacidad: la ubicación PUBLICADA se redondea (ver `publicable`)

    def publicable(self):
        if not self.redondeo_deg:
            return self
        r = lambda x: round(x / self.redondeo_deg) * self.redondeo_deg
        return Observador(round(r(self.lat), 4), round(r(self.lon), 4), self.alt_m, self.nombre, self.tz, self.redondeo_deg)

    def local(self, dt):
        return dt.astimezone(ZoneInfo(self.tz))


CDMX = Observador(19.43, -99.13, 2240, "Ciudad de México", "America/Mexico_City", redondeo_deg=0.1)


def _ecef_obs(obs):
    lat, lon = np.deg2rad(obs.lat), np.deg2rad(obs.lon)
    N = RT / np.sqrt(1 - E2 * np.sin(lat) ** 2)
    h = obs.alt_m / 1000.0
    return np.array([(N + h) * np.cos(lat) * np.cos(lon), (N + h) * np.cos(lat) * np.sin(lon), (N * (1 - E2) + h) * np.sin(lat)])


def _enu(obs):
    lat, lon = np.deg2rad(obs.lat), np.deg2rad(obs.lon)
    e = np.array([-np.sin(lon), np.cos(lon), 0.0])
    n = np.array([-np.sin(lat) * np.cos(lon), -np.sin(lat) * np.sin(lon), np.cos(lat)])
    u = np.array([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])
    return e, n, u


def topocentrico(el, obs, t):
    """(az°, el°, rango km, vel. radial km/s) para cada instante; vel. radial > 0 = se aleja."""
    r, v, _, _ = posicion_ecef(el, t)
    rho = r - _ecef_obs(obs)
    d = np.linalg.norm(rho, axis=1)
    e, n, u = _enu(obs)
    E, N, U = rho @ e, rho @ n, rho @ u
    az = np.rad2deg(np.arctan2(E, N)) % 360
    elev = np.rad2deg(np.arcsin(U / d))
    rr = np.einsum("ij,ij->i", rho, v) / d
    return az, elev, d, rr


def sol_elevacion(obs, t):
    """Elevación del Sol (°) para el observador (Meeus de baja precisión, ~0.01°)."""
    unix = a_unix(t)
    jd, fr = jd_fr(unix)
    n = jd + fr - 2451545.0
    L = np.deg2rad((280.460 + 0.9856474 * n) % 360)
    g = np.deg2rad((357.528 + 0.9856003 * n) % 360)
    lam = L + np.deg2rad(1.915) * np.sin(g) + np.deg2rad(0.020) * np.sin(2 * g)
    eps = np.deg2rad(23.439 - 4e-7 * n)
    s_eci = np.stack([np.cos(lam), np.cos(eps) * np.sin(lam), np.sin(eps) * np.sin(lam)], axis=1)
    gm = gmst(jd, fr)
    c, s = np.cos(gm), np.sin(gm)
    s_ecef = np.stack([c * s_eci[:, 0] + s * s_eci[:, 1], -s * s_eci[:, 0] + c * s_eci[:, 1], s_eci[:, 2]], axis=1)
    return np.rad2deg(np.arcsin(s_ecef @ _enu(obs)[2]))


def iluminado(el, t):
    """True si el satélite recibe luz del Sol (sombra cilíndrica de la Tierra)."""
    from .propagacion import posicion_teme
    unix = a_unix(t)
    jd, fr = jd_fr(unix)
    n = jd + fr - 2451545.0
    L = np.deg2rad((280.460 + 0.9856474 * n) % 360)
    g = np.deg2rad((357.528 + 0.9856003 * n) % 360)
    lam = L + np.deg2rad(1.915) * np.sin(g) + np.deg2rad(0.020) * np.sin(2 * g)
    eps = np.deg2rad(23.439 - 4e-7 * n)
    sh = np.stack([np.cos(lam), np.cos(eps) * np.sin(lam), np.sin(eps) * np.sin(lam)], axis=1)
    r, _ = posicion_teme(el, unix)
    along = np.einsum("ij,ij->i", r, sh)
    perp = np.linalg.norm(r - along[:, None] * sh, axis=1)
    return ~((along < 0) & (perp < RT))


@dataclass(frozen=True)
class Pase:
    aos: datetime
    tca: datetime
    los: datetime
    az_aos: float
    az_tca: float
    az_los: float
    el_max: float
    rango_min_km: float
    visible: bool                   # observador de noche (Sol < −6°) y satélite iluminado

    @property
    def duracion_s(self):
        return (self.los - self.aos).total_seconds()


def _dt(u):
    return datetime.fromtimestamp(float(u), tz=timezone.utc)


def pases(el, obs, desde, dias=7.0, el_min=10.0, paso_s=20.0, solo_visibles=False):
    """Pases completos sobre `el_min` entre `desde` y `desde + dias`. AOS/LOS refinados por bisección (< 0.5 s)."""
    t0 = a_unix(desde)[0]
    ts = t0 + np.arange(int(dias * 86400 / paso_s) + 1) * paso_s
    _, elv, _, _ = topocentrico(el, obs, ts)
    arriba = elv >= el_min
    sube = np.where(~arriba[:-1] & arriba[1:])[0]
    baja = np.where(arriba[:-1] & ~arriba[1:])[0]
    f = lambda u: float(topocentrico(el, obs, [u])[1][0]) - el_min

    def cruce(a, b):
        fa = f(a)
        while b - a > 0.25:
            m = (a + b) / 2
            fm = f(m)
            if (fm >= 0) == (fa >= 0):
                a, fa = m, fm
            else:
                b = m
        return (a + b) / 2

    salida = []
    for i in sube:
        j = baja[baja > i]
        if not len(j):
            break
        aos, los = cruce(ts[i], ts[i + 1]), cruce(ts[j[0]], ts[j[0] + 1])
        g = np.arange(aos, los + 1, 1.0)
        az, e, d, _ = topocentrico(el, obs, g)
        k = int(np.argmax(e))
        tca = g[k]
        azs = topocentrico(el, obs, [aos, los])[0]
        noche = bool(sol_elevacion(obs, [tca])[0] < -6.0)
        visible = noche and bool(iluminado(el, [tca])[0])
        p = Pase(_dt(aos), _dt(tca), _dt(los), float(azs[0]), float(az[k]), float(azs[1]), float(e[k]), float(d.min()), visible)
        if visible or not solo_visibles:
            salida.append(p)
    return salida


def trayectoria(el, obs, pase, n=240):
    """Arreglos t (s desde AOS), az, el, rango y velocidad radial a lo largo de un pase."""
    u = np.linspace(pase.aos.timestamp(), pase.los.timestamp(), n)
    az, e, d, rr = topocentrico(el, obs, u)
    return {"t": u - u[0], "az": az, "el": e, "rango": d, "rangedot": rr}
