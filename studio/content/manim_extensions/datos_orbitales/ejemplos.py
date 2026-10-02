"""Ejemplo reproducible para las piezas «Doppler real»: el pase más alto de la ISS sobre Ciudad de México.

Usa la muestra congelada (sin red) para que el carrusel, el reel y las pruebas den EXACTAMENTE las mismas cifras.
Frecuencia: f0 es un valor DE EJEMPLO (437 MHz, banda de 70 cm); no afirma que la ISS transmita ahí en ese pase.
"""
from datetime import timedelta

import numpy as np

from .doppler import C_KM_S, curva_doppler
from .fuentes import MUESTRAS, cargar
from .observador import CDMX, pases, trayectoria
from .sello import sello

F0_EJEMPLO = 437e6


def pase_estrella(muestra="iss_2026-10-02.json", dias=3.0, f0=F0_EJEMPLO, obs=CDMX):
    el = cargar(MUESTRAS / muestra)
    ps = pases(el, obs, el.epoca, dias=dias, el_min=10)
    p = max(ps, key=lambda q: q.el_max)
    d = curva_doppler(el, obs, p, f0, n=240)
    tr = trayectoria(el, obs, p, n=240)
    i_max, i_min = int(np.argmax(d["df"])), int(np.argmin(d["df"]))
    return {
        "el": el, "obs": obs, "pase": p, "doppler": d, "tray": tr, "f0": f0, "sello": sello(el, 3.0, ahora=el.epoca + timedelta(days=1)),
        "df_pico_khz": float(np.abs(d["df"]).max() / 1e3), "t_pico_s": float(d["t"][i_max]),
        "rr_aos_kms": float(tr["rangedot"][0]), "df_aos_khz": float(d["df"][0] / 1e3),
        "pendiente_hz_s": d["pendiente_max"], "t_cruce_s": d["t_cruce"],
        "aos_local": obs.local(p.aos), "los_local": obs.local(p.los), "tca_local": obs.local(p.tca),
        "i_max": i_max, "i_min": i_min,
    }
