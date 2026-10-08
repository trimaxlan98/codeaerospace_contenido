"""Datos y línea de tiempo de la serie de reels «Clima espacial» (40-reels-clima.py). Tema: Solar, fondo vertical propio.

Divulgación general (no es un proyecto de Co.De): cómo el Sol afecta a la Tierra, a los satélites, al GPS y a la radio.
Regla del dueño (2026-10-07): ciencia de base en lenguaje llano y POCAS cifras, todas con una comparación cotidiana.
Cada cifra lleva su fuente pública (NASA, NOAA SWPC, ESA, comunicados oficiales). Nada de tesis ni de clientes.
"""
import numpy as np

import divulgacion_fisica as F

C_KM_S = 299_792                # velocidad de la luz
UA_KM = 149_597_871             # distancia media Tierra–Sol
LUZ_S = UA_KM / C_KM_S          # ≈ 499 s = 8 min 19 s (NASA: «about 8 minutes and 20 seconds»)
VIENTO_KM_S = 400               # viento solar lento típico, 300–800 km/s (NOAA SWPC, «Solar Wind»)
CDMX_MTY_KM = 700               # distancia en línea recta aproximada (cálculo propio, ~705 km)
MANCHA_C, FOTOSFERA_C = 3_500, 5_500   # °C aprox. (NASA/NOAA: manchas ~3 500–4 500 °C vs ~5 500 °C)
CICLO_ANOS = 11
# Ciclos solares 22–25: (mínimo previo, máximo, número de manchas suavizado en el máximo) — SILSO/NOAA, aproximados
CICLOS = [(1986.8, 1989.6, 214), (1996.4, 2001.9, 180), (2008.9, 2014.3, 116), (2019.9, 2024.8, 161)]
FIN_CURVA = 2026.8              # el reel llega a la fecha de publicación (fase de bajada del ciclo 25)
CME_TON = "mil millones"        # masa típica ~1e12 kg (NASA: «a billion tons»)
CME_DIAS = (1, 3)               # tiempo de tránsito típico (NOAA SWPC)
STARLINK = (40, 49)             # feb 2022: hasta 40 de 49 satélites (comunicado de SpaceX, 8-feb-2022)
AURORA_KM = {"nitrógeno": (85, 100), "oxígeno verde": (100, 250), "oxígeno rojo": (250, 400)}   # NOAA SWPC «Aurora»
ISS_KM, AVION_KM = 400, 10
CARRINGTON, QUEBEC, GANNON = 1859, 1989, 2024
QUEBEC_HORAS, QUEBEC_MILLONES = 9, 6     # 13-mar-1989, Hydro-Québec
GANNON_ANOS = 20                          # mayo 2024: primera G5 desde 2003 (NOAA SWPC)


def manchas(anio):
    """Curva aproximada del número de manchas (forma suave entre mínimos; picos de CICLOS)."""
    a = np.asarray(anio, float)
    y = np.zeros_like(a)
    mins = [c[0] for c in CICLOS] + [2030.9]
    for k, (m0, mx, pico) in enumerate(CICLOS):
        m1 = mins[k + 1]
        sube = (a >= m0) & (a < mx)
        baja = (a >= mx) & (a < m1)
        y = np.where(sube, pico * np.sin(np.pi / 2 * (a - m0) / (mx - m0)) ** 2, y)
        y = np.where(baja, pico * np.cos(np.pi / 2 * (a - mx) / (m1 - mx)) ** 1.6, y)
    return y + 8


CUERPO = {"ReelSolLuz": 19.0, "ReelSolViento": 19.0, "ReelSolEscudo": 20.0, "ReelSolAurora": 20.0, "ReelSolManchas": 20.0,
          "ReelSolLlamarada": 19.0, "ReelSolEyeccion": 20.0, "ReelSolSatelites": 20.0, "ReelSolGps": 20.0, "ReelSolTormenta": 21.0}
LEYENDAS = {"ReelSolLuz": (0.0, 5.0, 11.5), "ReelSolViento": (0.0, 5.5, 11.0), "ReelSolEscudo": (0.0, 6.0, 12.5),
            "ReelSolAurora": (0.0, 6.0, 12.5), "ReelSolManchas": (0.0, 6.5, 13.0), "ReelSolLlamarada": (0.0, 5.0, 10.5),
            "ReelSolEyeccion": (0.0, 5.5, 12.0), "ReelSolSatelites": (0.0, 6.0, 12.5), "ReelSolGps": (0.0, 6.0, 12.5),
            "ReelSolTormenta": (0.0, 6.0, 12.0)}
H0 = F.H0


def duracion(nombre):
    return F.duracion_total(CUERPO[nombre])
