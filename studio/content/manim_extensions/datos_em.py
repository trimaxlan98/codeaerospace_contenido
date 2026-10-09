"""Datos y línea de tiempo de la serie de reels «Electromagnetismo en el espacio» (43-reels-em.py). Tema: Electromagnetismo,
fondo vertical propio (fondos_reel.electromagnetismo: limbo de la Tierra con aurora y líneas de campo).

Divulgación de física de base aplicada a sistemas espaciales. Cada cifra sale de una función de `electromagnetismo.py` (la misma
física del curso de electromagnetismo, con sus pruebas) evaluada aquí con supuestos declarados; no hay mediciones propias.
Regla del dueño (2026-10-07): pocas cifras, cada una con una comparación cotidiana; lo técnico y los supuestos van al ⚠️.
Sin tesis ni clientes.
"""
import numpy as np

import divulgacion_fisica as F
import electromagnetismo as E

R_TIERRA_KM = 6371.0
H_LEO = 550e3                                           # altura de ejemplo de un satélite pequeño (m)
R_LEO = 1 + H_LEO / (R_TIERRA_KM * 1e3)                 # en radios terrestres

# ── 1 · Escudo: campo del dipolo en el ecuador (superficie) y en LEO; un imán de refrigerador típico ~5 mT (orden de magnitud) ─
B_SUPERFICIE_UT = E.b_tierra(1.0) * 1e6                 # 31.2 µT
B_LEO_UT = E.b_tierra(R_LEO) * 1e6                      # ≈ 24 µT
B_IMAN_REFRI_UT = 5000.0                                # supuesto de comparación (imanes de nevera: ~1–10 mT)
VECES_IMAN = B_IMAN_REFRI_UT / B_SUPERFICIE_UT          # ≈ 160 → «unas 150 veces»

# ── 2 · Espiral: electrón de 1 keV en 30 µT (cinturones, orden de magnitud) ─────────────────────────────────────────────────
_V_E = float(np.sqrt(2 * 1e3 * E.Q_E / E.M_ELECTRON))
GIRO_E_HZ = E.frecuencia_giro(E.Q_E, E.M_ELECTRON, 30e-6)              # ≈ 840 000 vueltas por segundo
RADIO_E_M = E.radio_larmor(E.Q_E, E.M_ELECTRON, _V_E, 30e-6)           # ≈ 3.6 m

# ── 3 · Aurora: alturas y colores (oxígeno 557.7 nm verde ~100–250 km; 630 nm rojo más arriba; nitrógeno azul/violeta) ─────────
AURORA_KM = (100, 300)
VERDE_NM, ROJO_NM = 557.7, 630.0

# ── 4 · Magnetotorque: 1U (I = 0.002 kg·m²), m = 0.2 A·m², 90° desde el reposo (cota optimista: sin frenar al final) ───────────
TORQ_M, TORQ_I = 0.2, 0.002
TORQ_LEO_S = E.tiempo_giro_torquer(TORQ_M, E.b_tierra(R_LEO), TORQ_I, 90)     # ≈ 36 s a 550 km
TORQ_GEO_S = E.tiempo_giro_torquer(TORQ_M, E.b_tierra(6.61), TORQ_I, 90)      # ≈ 9 min en GEO (campo ~200× más débil)

# ── 5 · Luz: c de μ0 y ε0 (mesas de laboratorio) ────────────────────────────────────────────────────────────────────────────
C_KM_S = E.c_de_constantes() / 1e3                     # 299 792 km/s
VUELTAS_TIERRA_1S = E.c_de_constantes() / (2 * np.pi * R_TIERRA_KM * 1e3)     # ≈ 7.5

# ── 6 · Bandas: tamaño de la onda (λ = c/f) para frecuencias típicas de satélites ─────────────────────────────────────────────
BANDAS = [("UHF", 437e6, "cubesats"), ("S", 2.2e9, "telemetría"), ("X", 8.4e9, "sondas"), ("Ka", 30e9, "internet")]
LAMBDAS_CM = {n: E.lambda_de(f) * 100 for n, f, _ in BANDAS}                   # 69, 13.6, 3.6, 1.0 cm
VISIBLE_NM = 550

# ── 7 · Antena: dipolo de media onda para 437 MHz ─────────────────────────────────────────────────────────────────────────
DIPOLO_CM = E.lambda_de(437e6) / 2 * 100                # ≈ 34 cm

# ── 8 · Ionosfera: frecuencia de plasma con Ne = 1e12 m⁻³ (pico diurno de la capa F, orden de magnitud) ──────────────────────
FP_MHZ = E.frecuencia_plasma(1e12) / 1e6                # ≈ 9 MHz

# ── 9 · Cable en órbita: fem por km de cable perpendicular a v y B, a 550 km (cota: geometría ideal) ───────────────────────────
V_LEO_KM_S = E.v_orbital(H_LEO) / 1e3                   # ≈ 7.6 km/s
VOLT_POR_KM = E.v_orbital(H_LEO) * E.b_tierra(R_LEO) * 1e3                    # ≈ 185 V por km

# ── 10 · La señal llega débil: 1 W isótropo a 1000 km en 437 MHz ──────────────────────────────────────────────────────────
FSPL_DB = E.fspl_db(1000e3, 437e6)                      # ≈ 145 dB
P_RX_W = 10 ** (-FSPL_DB / 10)                          # ≈ 3e-15 W con antenas isótropas


CUERPO = {"ReelEMEscudo": 20.0, "ReelEMEspiral": 20.0, "ReelEMAurora": 20.0, "ReelEMTorque": 20.0, "ReelEMLuz": 20.0,
          "ReelEMBandas": 20.0, "ReelEMAntena": 20.0, "ReelEMIonosfera": 20.0, "ReelEMCable": 20.0, "ReelEMSenal": 20.0}
LEYENDAS = {n: (0.0, 6.0, 12.5) for n in CUERPO}
H0 = F.H0


def duracion(nombre):
    return F.duracion_total(CUERPO[nombre])


if __name__ == "__main__":
    for k, v in sorted(globals().items()):
        if k.isupper() and isinstance(v, (int, float, tuple, dict)):
            print(f"{k} = {v}")
