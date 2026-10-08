"""Datos y línea de tiempo de la serie de reels «Estación ATP» (37-… es la serie de física; 38-reels-ats.py es esta).

Fuente: ros2-workspace (Estación ATP, ROS 2 Jazzy, SIMULADA de punta a punta; SGP4 con TLE reales de CelesTrak). Nada de esto
es medida con hardware: en pantalla siempre va el chip «Simulación · ROS 2».

  · Series y métricas de pases: `studio/content/datos_ats/ats_muestra.json` (lo arma `studio/tools/ats_congelar.py` desde
    `contenido/datasets/*.json`, `docs/pnt_resultados/tabla_C.json` y `docs/mpc_resultados/keyhole.json`, con la procedencia).
  · Cifras de las tablas de los documentos (no hay JSON): van abajo, cada una con su archivo y sección de origen.
Regla de la Estación: «cada cifra se calcula y se contrasta con una fuente». Aquí, cada cifra tiene la suya.
"""
import json
from pathlib import Path

import numpy as np

import divulgacion_fisica as F

_RUTA = Path(__file__).resolve().parents[1] / "datos_ats/ats_muestra.json"
_CACHE = []


def muestra():
    if not _CACHE:
        _CACHE.append(json.loads(_RUTA.read_text(encoding="utf-8")))
    return _CACHE[0]


def pase(nombre):
    """Pase simulado: dict con 'metricas' y 'series' (np.array)."""
    p = muestra()["pases"][nombre]
    return {"metricas": p["metricas"], "args": p["argumentos"], "series": {k: np.array(v, float) for k, v in p["series"].items()}}


# ── Keyhole (docs/SEGUIDOR.md §3.1 y §4.2: 550 km, rotor de 6 °/s, haz de S de 3.18°) ───────────────────────────────
KH_OMEGA = 0.79                # °/s: velocidad angular del satélite en el cenit a 550 km (§3.1)
KH_ROTOR = 6.0                 # °/s: tope del rotor (§2)
KH_SATURA_EL = 82.5            # ° de elevación máxima desde la que el rotor satura a 550 km (§3.1)
KH_SEMIHAZ_S = 1.59            # ° (§2: semihaz de la banda S)
KH_ERR_MAX_89_9 = {"ingenua": 15.75, "anticipada": 4.52, "sobre_cenit": 0.16}      # ° (§4.2, pase sintético de 89.9°)
KH_FUERA_S_89_9 = {"ingenua": 26.3, "anticipada": 23.6, "sobre_cenit": 0.0}        # s fuera del haz de S (§4.2)
KH_M = 0.1                     # ° de distancia mínima al cenit (el_max = 89.9°)


def keyhole_sim(dt=0.02, t0=-8.0, t1=40.0):
    """Modelo plano de §3.1 (az = atan2(Ωt, m)) con el acimut de la antena limitado a KH_ROTOR (estrategia ingenua).
    Devuelve (t, sat_xy, ant_xy, az_pedido, az_real) con posiciones en el plano del cielo (°) centrado en el cenit."""
    ts = np.arange(t0, t1, dt)
    u, w = KH_OMEGA * ts, KH_M
    zeta = np.hypot(u, w)
    az = np.degrees(np.arctan2(u, w))
    az_a = np.empty_like(az)
    az_a[0] = az[0]
    for i in range(1, len(ts)):
        d = (az[i] - az_a[i - 1] + 180) % 360 - 180
        az_a[i] = az_a[i - 1] + np.clip(d, -KH_ROTOR * dt, KH_ROTOR * dt)
    sat = np.stack([zeta * np.sin(np.radians(az)), zeta * np.cos(np.radians(az))], 1)
    ant = np.stack([zeta * np.sin(np.radians(az_a)), zeta * np.cos(np.radians(az_a))], 1)
    return ts, sat, ant, az, az_a


# ── Autotrack (README.md «Escalera de validación» N5; src/atp_sdr/README.md) ────────────────────────────────────────
KA_HAZ = 0.233                 # ° (ancho de haz de 3 dB, plato de 3 m en Ka)
LUNA_LLENA = 0.52              # ° diámetro angular aproximado de la Luna

# ── Doppler del receptor (docs/SEGUIDOR.md §5.2–5.3) ──────────────────────────────────────────────────────────────
DOP_VENTANA_S = (60.1, 3.0)    # kHz: ± de la ventana de búsqueda, sin precompensar → con la órbita de la OD
DOP_VENTANA_UHF = (12.0, 0.6)
DOP_MUESTREO_S = (200, 50)     # kHz
DOP_ENGANCHE = (62, 69)        # % del pase enganchado en las cuatro configuraciones, a 25 dB-Hz (§5.3)

# ── Órbita (docs/OD.md §3.2, §4 vía docs/INNOVACION.md CD-2026-08) ─────────────────────────────────────────────────
OD_TLE_KM = ((0.5, 1.6), (1.0, 2.1), (2.0, 6.4), (3.0, 11.0), (5.0, 40.0))   # (días de edad, km de error del TLE)
OD_MEJORA = (70, 370)          # veces mejor que el TLE en el pase siguiente (OD de 3 pases en 12 h)
OD_AOS_PCT = (3, 100)          # % de pases con error en AOS < 0.117° (haz de Ka): TLE → OD de 3 pases
OD_HAZ_KA = 0.117

# ── Calibración con el Sol (docs/PUESTA_EN_MARCHA.md §7; docs/APUNTAMIENTO.md §2) ─────────────────────────────────
SOL_RESIDUO = (0.5207, 0.0072)  # ° rms de la montura simulada: sin calibrar → calibrada (×72)
SOL_DENTRO = (0.0, 100.0)       # % de muestras dentro de 0.1°
SOL_OD_KM = (18.437, 0.232)     # km de error de posición de la órbita estimada
SOL_DIAMETRO = 0.53             # ° (el Sol)

# ── Láser entre satélites (src/sat_isl/README.md; docs/INNOVACION.md CD-2026-12) ───────────────────────────────────
ISL_SEMIHAZ_URAD = 29.6         # µrad (5 cm a 1550 nm, γ óptimo 1.121)
ISL_CUERDA_KM = 5494.0          # km (patrón 3×8 a 800 km)
ISL_ADELANTO_URAD = 50.7        # µrad de point-ahead (7.6 km/s)
ISL_ADQ_MEDIANA_S = 1.05        # s (planta completa); Monte Carlo puro 0.95 s
ISL_FINO_URAD = 0.681           # µrad rms del lazo fino (p95 1.180)
ISL_CERRADO_PCT, ISL_MBPS = 99.2, 1250

# ── Lockstep (docs/INNOVACION.md CD-2026-01; docs/CALIDAD.md §6.4) ─────────────────────────────────────────────────
LOCK_RMS_ANTES = (0.0036, 0.0044)   # ° rms del autotrack N5 en 4 corridas con la CPU limitada, antes del cierre
LOCK_FILAS = 3115                   # filas idénticas byte a byte después


def pnt_cep():
    """[(etiqueta, CEP50 en m)] de la constelación Walker 72/8/1 (docs/pnt_resultados/tabla_C.json)."""
    filas = [f for f in muestra()["pnt_tabla_C"]["filas"] if f["grupo"].startswith("Walker")]
    et = {"precisa": "órbita exacta", "TLE 0 d": "TLE de hoy", "TLE 1 d": "TLE de 1 día", "TLE 3 d": "TLE de 3 días", "TLE 7 d": "TLE de 7 días"}
    return [(et[f["efemeride"]], f["cep50_m"]) for f in filas]


def mpc_keyhole_89_9():
    """Error máximo (°) a 89.9° de elevación (docs/mpc_resultados/keyhole.json)."""
    c = muestra()["keyhole_mpc"]["celdas"]
    return {"reactivo (PID)": c["89.9|pid_ingenua"]["max_deg"], "MPC, mira 2 s": c["89.9|mpc_horizonte_2s"]["max_deg"],
            "planificador (LP)": c["89.9|pid_anticipada"]["max_deg"], "MPC, mira 36 s": c["89.9|mpc_q_int_bajo"]["max_deg"]}


# ══ Línea de tiempo de cada reel: cuerpo TB (s), instantes en que cambia la leyenda y eventos ═══════════════════════════
H0 = F.H0
PASE_T0, PASE_T1 = 1.0, 17.0           # reel «Pase»: el pase de 583 s se reproduce entre estos instantes del cuerpo
KH_T0, KH_T1, KH_SIM_X = 1.0, 15.0, 3.0   # el pase del keyhole va a ×3
AT_T0, AT_T1 = 1.0, 15.0
DOP_T0, DOP_T1 = 1.0, 6.0
OD_PASOS = (1.0, 3.0, 5.0, 7.0, 9.0)   # instantes en que el TLE «cumple» 0.5, 1, 2, 3 y 5 días
SOL_BARRIDO_AZ, SOL_BARRIDO_EL, SOL_CORRIGE = (1.5, 4.5), (5.1, 8.1), 8.8
LASER_BUSCA = (1.5, 7.5)               # la espiral de adquisición
LASER_ENCUENTRA = 7.8                  # se encuentran 1.05 s × 6 después de empezar (cámara lenta ×6)

CUERPO = {"ReelAtpPase": 24.0, "ReelAtpKeyhole": 26.0, "ReelAtpAutotrack": 22.0, "ReelAtpDoppler": 22.0, "ReelAtpOrbita": 22.0,
          "ReelAtpSol": 24.0, "ReelAtpPnt": 24.0, "ReelAtpLaser": 22.0, "ReelAtpMpc": 22.0, "ReelAtpLockstep": 20.0}

LEYENDAS = {"ReelAtpPase": (0.0, 6.5, 12.5), "ReelAtpKeyhole": (0.0, 5.0, 10.5, 17.5), "ReelAtpAutotrack": (0.0, 5.0, 10.0),
            "ReelAtpDoppler": (0.0, 6.0, 11.5, 16.5), "ReelAtpOrbita": (0.0, 6.5, 12.5), "ReelAtpSol": (0.0, 4.6, 8.8, 14.0),
            "ReelAtpPnt": (0.0, 6.0, 12.0, 18.0), "ReelAtpLaser": (0.0, 4.2, 9.5), "ReelAtpMpc": (0.0, 6.5, 13.0),
            "ReelAtpLockstep": (0.0, 6.0, 12.5)}


def duracion(nombre):
    return F.duracion_total(CUERPO[nombre])


if __name__ == "__main__":
    m = muestra()
    print("congelado", m["congelado"], "workspace", m["workspace_commit"])
    for n in CUERPO:
        print(f"{n:18s} cuerpo {CUERPO[n]:5.1f} s · total {duracion(n):5.1f} s")
    print("PNT:", [(a, round(b, 1)) for a, b in pnt_cep()])
    print("MPC:", {k: round(v, 2) for k, v in mpc_keyhole_89_9().items()})
    ts, sat, ant, az, aza = keyhole_sim()
    err = np.linalg.norm(sat - ant, axis=1)
    print("keyhole plano: error máx", round(err.max(), 2), "° · fuera del semihaz", round((err > KH_SEMIHAZ_S).sum() * 0.02, 1), "s")
    p = pase("demo-n5b")["series"]
    ep = p["e_pt"]; print("n5b e_pt máx", ep.max())
    # relación entre e_pt y (e_az, e_el)
    q = pase("demo-n5a")["series"]
    cand1 = np.hypot(q["e_az"] * np.cos(np.radians(q["el"])), q["e_el"]); cand2 = np.hypot(q["e_az"], q["e_el"])
    print("e_pt ≈ hypot(e_az·cos el, e_el):", float(np.abs(cand1 - q["e_pt"]).max()), " | hypot(e_az, e_el):", float(np.abs(cand2 - q["e_pt"]).max()))
