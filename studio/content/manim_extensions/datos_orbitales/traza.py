"""Traza terrestre y huella de cobertura."""
from datetime import timedelta

import numpy as np

from .propagacion import RT, a_unix, posicion_geodetica


def traza_terrestre(el, desde, minutos=180.0, paso_s=30.0):
    """(t_unix, lat°, lon°) con NaN donde la traza cruza el antimeridiano (para no dibujar la raya horizontal)."""
    t0 = a_unix(desde)[0]
    ts = t0 + np.arange(0, minutos * 60 + 1, paso_s)
    lat, lon, _ = posicion_geodetica(el, ts)
    salto = np.where(np.abs(np.diff(lon)) > 180)[0] + 1
    return (np.insert(ts, salto, np.nan), np.insert(lat, salto, np.nan), np.insert(lon, salto, np.nan))


def huella_radio_km(h_km, el_min_deg=0.0):
    """Radio (km sobre la superficie) del círculo desde el que se ve un satélite a altura h con elevación ≥ el_min."""
    e = np.deg2rad(el_min_deg)
    central = np.arccos(RT / (RT + h_km) * np.cos(e)) - e
    return float(RT * central)
