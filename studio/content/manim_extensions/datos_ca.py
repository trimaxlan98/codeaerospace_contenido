"""Datos y línea de tiempo de la serie de reels «Cálculo en el espacio» (45-reels-calculo.py). Tema: Cálculo (medianoche con tiza
ámbar e índigo), fondo vertical propio (fondos_reel.calculo: un paisaje de curvas de nivel como horizonte, con ejes, una tangente y
rectángulos de Riemann; resplandor ámbar que sube).

Cada reel es UNA idea del cálculo (derivada, integral, máximo, pasos numéricos, aceleración centrípeta, tasas, exponencial,
aproximación, ecuación diferencial) con una aplicación espacial. Las cuentas salen de `calculo_espacio.py` (con sus pruebas)
evaluadas aquí con supuestos declarados; los datos públicos (Voyager, atmósfera) van citados en el ⚠️ de los pies. Sin mediciones
propias, sin tesis ni clientes. Regla del dueño: pocas cifras, cada una con una comparación cotidiana.
"""
import divulgacion_fisica as F
import calculo_espacio as C

H_ISS = 420e3                                              # altura de ejemplo de la ISS (varía ~410–430 km)

# ── 1 · Derivada: la pendiente de la posición es la velocidad; la sombra de la ISS cruza México ───────────────────────────────
V_ISS_KM_S = C.v_circular(H_ISS) / 1e3                     # ≈ 7.66 km/s
V_SUELO_KM_S = C.v_suelo(H_ISS) / 1e3                      # ≈ 7.19 km/s sobre el suelo
MEXICO_KM = C.distancia_km(32.53, -117.02, 21.16, -86.85)  # Tijuana → Cancún en línea recta ≈ 3 235 km
MEXICO_MIN = MEXICO_KM / V_SUELO_KM_S / 60                 # ≈ 7.5 min

# ── 2 · Integral: el área bajo la velocidad es la distancia; 1 minuto de ISS vs. 1 minuto de auto ──────────────────────────────
ISS_1MIN_KM = V_ISS_KM_S * 60                              # ≈ 460 km
CDMX_GDL_KM = C.distancia_km(19.43, -99.13, 20.67, -103.35)    # ≈ 462 km en línea recta
AUTO_KMH = 100
AUTO_1MIN_KM = AUTO_KMH / 60                               # ≈ 1.7 km

# ── 3 · Máximo: derivada cero en lo más alto; el mismo impulso que sube 0.5 m en la Tierra, en la Luna ─────────────────────────
SALTO_TIERRA_M = 0.5
V_SALTO = (2 * C.G0 * SALTO_TIERRA_M) ** 0.5               # ≈ 3.1 m/s
SALTO_LUNA_M = C.altura_max(V_SALTO, C.G_LUNA)             # ≈ 3.0 m
T_AIRE_TIERRA_S = 2 * V_SALTO / C.G0                       # ≈ 0.64 s
T_AIRE_LUNA_S = 2 * V_SALTO / C.G_LUNA                     # ≈ 3.9 s

# ── 4 · Pasos de Euler: la computadora avanza la órbita a pasitos ────────────────────────────────────────────────────────────
PASOS_MAL, PASOS_BIEN = 20, 2000
PTS_MAL, R_MAL = C.orbita_euler(PASOS_MAL, 1.0)            # termina a ~3.6 veces el radio
PTS_BIEN, R_BIEN = C.orbita_euler(PASOS_BIEN, 1.0)         # error ~4 %
ERR_BIEN = abs(R_BIEN - 1)
ERR_10X = abs(C.orbita_euler(10 * PASOS_BIEN, 1.0)[1] - 1)     # ~0.4 %: 10× pasos, 10× menos error

# ── 5 · Gravedad artificial: a = ω²r; 1 g a 100 m de radio ──────────────────────────────────────────────────────────────────
RADIO_GIRO_M = 100.0
RPM_1G = C.rpm_gravedad(RADIO_GIRO_M)                      # ≈ 3 vueltas por minuto
SEG_VUELTA = 60 / RPM_1G                                   # ≈ 20 s
RPM_10M = C.rpm_gravedad(10.0)                             # ≈ 9.5 con 10 m de radio

# ── 6 · Tasas relacionadas: la Tierra «alcanza» a Marte cada 26 meses ────────────────────────────────────────────────────────
T_TIERRA_D, T_MARTE_D = 365.256, 686.98
SINODICO_D = C.periodo_sinodico(T_TIERRA_D, T_MARTE_D)     # ≈ 780 días
SINODICO_MESES = SINODICO_D / 30.44                        # ≈ 25.6 → «cada 26 meses»

# ── 7 · Exponencial: el plutonio del Voyager ───────────────────────────────────────────────────────────────────────────────
PU_MITAD_ANIOS = 87.7
VOYAGER_ANIOS = 2026 - 1977                                # 49 años
CALOR_RESTANTE = C.fraccion_restante(VOYAGER_ANIOS, PU_MITAD_ANIOS)    # ≈ 0.68
VOYAGER_W0, VOYAGER_W_HOY = 470, 230                       # electricidad: ~470 W al lanzar, ~230 W en 2026 (fuentes públicas)

# ── 8 · Exponencial hacia arriba: el aire se reduce a la mitad cada ~5.5 km ─────────────────────────────────────────────────
MITAD_AIRE_KM = 5.5                                        # la mitad de la masa del aire queda debajo de ~5.5 km
EVEREST_KM = 8.85
AIRE_EVEREST = 2 ** (-EVEREST_KM / MITAD_AIRE_KM)          # ≈ 1/3 (modelo; tabla estándar: ~0.31)
P_100KM_ATM = 0.032 / 101325                               # ≈ 3e-7 atm (atmósfera estándar de EE. UU., 1976)

# ── 9 · Aproximación: hasta dónde se ve el horizonte ───────────────────────────────────────────────────────────────────────
OJOS_M = 2.0
HORIZONTE_PLAYA_KM = C.horizonte_km(OJOS_M)                # ≈ 5 km
HORIZONTE_AVION_KM = C.horizonte_km(10e3)                  # ≈ 357 km
HORIZONTE_ISS_KM = C.horizonte_km(H_ISS)                   # ≈ 2 350 km
TJ_CDMX_KM = C.distancia_km(32.53, -117.02, 19.43, -99.13)  # ≈ 2 300 km en línea recta

# ── 10 · Ecuación diferencial: un túnel recto a través de la Tierra ───────────────────────────────────────────────────────
TUNEL_MIN = C.tunel_min()                                  # ≈ 42 min (sin aire ni fricción, Tierra uniforme)
ORBITA_RAS_MIN = C.periodo_s(0.0) / 60                     # ≈ 84 min = el doble: mismo reloj que una órbita a ras del suelo


CUERPO = {n: 20.0 for n in ("ReelCADerivada", "ReelCAIntegral", "ReelCAMaximo", "ReelCAPasos", "ReelCAGiro",
                            "ReelCATasas", "ReelCAPlutonio", "ReelCAAire", "ReelCAHorizonte", "ReelCATunel")}
LEYENDAS = {n: (0.0, 6.0, 12.5) for n in CUERPO}
H0 = F.H0


def duracion(nombre):
    return F.duracion_total(CUERPO[nombre])


if __name__ == "__main__":
    for k, v in sorted(globals().items()):
        if k.isupper() and isinstance(v, (int, float)):
            print(f"{k} = {v}")
