"""Datos y línea de tiempo de la serie de reels «Caos y gravedad» (46-reels-caos.py). Tema: Caos (ámbar, rosa y violeta sobre casi
negro), fondo vertical propio (fondos_reel.caos: el diagrama de bifurcación del mapa logístico como horizonte).

Casi todo sale de SIMULACIONES de `caos_gravedad.py` congeladas por `studio/tools/caos_congelar.py` en `studio/content/datos_caos/`
(el render no recalcula ni usa la red): figura ocho, problema pitagórico y su gemela, Jano y Epimeteo con masas reales, el giro de
Hiperión, y el histograma real del cinturón de asteroides (NASA/JPL SBDB). Las cifras públicas (Webb, Iridium–Cosmos, Fengyun-1C,
Laskar, GRAIL, Voyager) van citadas en el ⚠️ de los pies. Sin mediciones propias, sin tesis ni clientes.
"""
import json
from pathlib import Path

import numpy as np

import caos_gravedad as G
import divulgacion_fisica as F

_D = Path(__file__).resolve().parents[1] / "datos_caos"


def _npz(n):
    return np.load(_D / f"{n}.npz")


# ── 1–2 · Tres cuerpos: figura ocho y problema pitagórico (masas 3, 4, 5; gemela a 1e-6) ────────────────────────────────────
OCHO = _npz("ocho")
PIT = _npz("pitagorico")
PIT_T, PIT_A, PIT_B, PIT_M = PIT["t"], PIT["A"], PIT["B"], PIT["m"]
PIT_SEP = np.linalg.norm(PIT_A - PIT_B, axis=2).max(axis=1)
PIT_DELTA0 = 1e-6


def t_separa(umbral):
    return float(PIT_T[np.argmax(PIT_SEP > umbral)])


T_SEPARA_VISIBLE = t_separa(0.05)                         # cuándo la diferencia ya se ve (≈ 45 en unidades de la simulación)

# ── 3 · Puntos de Lagrange: dibujo con masas exageradas; cifras reales del Sol–Tierra ─────────────────────────────────────────
MU_DIBUJO = 0.02                                           # masa del planeta exagerada (L4/L5 estables si μ < 0.0385)
L_DIBUJO = G.puntos_lagrange(MU_DIBUJO)
MU_SOL_TIERRA = 3.0035e-6
UA_KM = 1.495978707e8
L2_KM = (G.puntos_lagrange(MU_SOL_TIERRA)["L2"][0] - (1 - MU_SOL_TIERRA)) * UA_KM      # ≈ 1.5 millones de km
LUNA_KM = 384400.0
L2_VECES_LUNA = L2_KM / LUNA_KM                            # ≈ 3.9
KIRK = json.load(open(_D / "kirkwood.json"))
TROYANOS = KIRK["troyanos_jupiter"]                        # conteo JPL a la fecha de la consulta
FECHA_JPL = KIRK["fecha_consulta"]

# ── 4 · Jano y Epimeteo (simulación con masas reales) ─────────────────────────────────────────────────────────────────────
CO = _npz("coorbitales")
CO_T, CO_ANG, CO_DR = CO["t"], CO["ang"], CO["dr"]
_cambios = CO_T[1:][np.diff(np.sign(CO_DR)) != 0]
CO_CAMBIOS = [float(c) for c in _cambios]                  # años en que cambian de órbita
CO_PERIODO_ANIOS = float(np.diff(_cambios).mean()) if len(_cambios) > 1 else float("nan")    # ≈ 4.0
_ang = (CO_ANG + np.pi) % (2 * np.pi) - np.pi
CO_MIN_KM = float(np.abs(_ang).min() * G.A_JANO / 1e3)     # acercamiento mínimo (cuerda ≈ arco)
DA_KM = G.DA_COORB / 1e3                                   # 50 km

# ── 5 · Hiperión ──────────────────────────────────────────────────────────────────────────────────────────────────────────
HIP = _npz("hiperion")
HIP_T, HIP_TH, HIP_W, LUNA_TH, LUNA_W = HIP["t"], HIP["theta"], HIP["w"], HIP["theta_luna"], HIP["w_luna"]
HIP_E, HIP_W0 = 0.1, 0.89
HIP_W_MIN, HIP_W_MAX = float(HIP_W.min()), float(HIP_W.max())

# ── 6 · Huecos de Kirkwood (datos reales) y resonancias con Júpiter ─────────────────────────────────────────────────────────
KIRK_BORDES = np.array(KIRK["bordes_ua"])
KIRK_CUENTA = np.array(KIRK["cuenta"])
ASTEROIDES = KIRK["asteroides"]
A_JUPITER = 5.2026
RESONANCIAS = {f"{p}:{q}": A_JUPITER * (q / p) ** (2 / 3) for p, q in ((3, 1), (5, 2), (7, 3), (2, 1))}   # 2.50, 2.82, 2.96, 3.28 UA

# ── 7 · Asistencia gravitatoria en Júpiter ───────────────────────────────────────────────────────────────────────────────
V_INF = 10.0                                               # km/s, llegada (ejemplo)
RP = 5 * G.R_JUPITER                                       # pasa a 5 radios de Júpiter del centro
GIRO_RAD, DV_KMS = G.sobrevuelo(V_INF, RP)                 # ≈ 102°, ≈ 15.5 km/s
GIRO_DEG = float(np.degrees(GIRO_RAD))
VJ = np.array([G.V_JUPITER, 0.0])                          # Júpiter va hacia +x
# la nave cruza por detrás de Júpiter: sale en la dirección en que Júpiter avanza (la ganancia máxima para este giro)
V_OUT_REL = V_INF * np.array([1.0, 0.0])
V_IN_REL = V_INF * np.array([np.cos(-GIRO_RAD), np.sin(-GIRO_RAD)])
V_IN_SOL = V_IN_REL + VJ
V_OUT_SOL = V_OUT_REL + VJ
VEL_IN, VEL_OUT = float(np.linalg.norm(V_IN_SOL)), float(np.linalg.norm(V_OUT_SOL))
GANANCIA_KMS = VEL_OUT - VEL_IN

# ── 8 · Kessler (modelo de juguete, adimensional) ───────────────────────────────────────────────────────────────────────
K_TAU, K_K = 10.0, 1e-3                                    # vida media 10 «años»; umbral N* = 1/(k·τ) = 100
K_UMBRAL = 1 / (K_K * K_TAU)
K_T, K_BAJO = G.kessler(80, 0.0, K_TAU, K_K, 40)
_, K_ALTO = G.kessler(120, 0.0, K_TAU, K_K, 40)
FRAG_IRIDIUM_COSMOS = 2000                                 # «más de 2 000» catalogados (≈ 2 300)
FRAG_FENGYUN = 3000                                        # «más de 3 000» catalogados (≈ 3 400–3 500)

# ── 9 · Horizonte de predicción (Laskar) ────────────────────────────────────────────────────────────────────────────────
LYAP_MYR = 5.0                                             # tiempo de Lyapunov del sistema solar interior
DUPLICA_MYR = LYAP_MYR * np.log(2)                         # ≈ 3.5 millones de años
ERR0_M = 15.0
HORIZONTE_MYR = G.horizonte_lyapunov(ERR0_M, LYAP_MYR, 1.5e11) # ≈ 115 → «unos 100 millones de años»
CLIMA_DIAS = 14

# ── 10 · Atajos de baja energía ───────────────────────────────────────────────────────────────────────────────────────────
APOLO_DIAS = 3
GRAIL_MESES = 3.5
GRAIL_AHORRO_MS = 130
GRAIL_LEJOS_KM = 1.5e6

CUERPO = {n: 20.0 for n in ("ReelCOOcho", "ReelCOMariposa", "ReelCOLagrange", "ReelCOHerradura", "ReelCOHiperion",
                            "ReelCOKirkwood", "ReelCOHonda", "ReelCOKessler", "ReelCOPrediccion", "ReelCOAtajo")}
LEYENDAS = {n: (0.0, 6.0, 12.5) for n in CUERPO}
H0 = F.H0


def duracion(nombre):
    return F.duracion_total(CUERPO[nombre])


if __name__ == "__main__":
    for k, v in sorted(globals().items()):
        if k.isupper() and isinstance(v, (int, float, list, dict, str)) and not isinstance(v, bool):
            print(f"{k} = {v if not isinstance(v, list) or len(v) < 8 else v[:8]}")
