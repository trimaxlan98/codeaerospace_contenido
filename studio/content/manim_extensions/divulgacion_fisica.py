"""Física y LÍNEA DE TIEMPO compartidas por los reels de divulgación (37-reels-divulgacion.py) y su audio
(studio/tools/sonido_reels.py). Solo numpy: el audio importa esto sin Manim, así los eventos sonoros caen
exactamente en el cuadro del video (antes los tiempos se copiaban a mano entre escena y audio).

Todo es física de libro con constantes estándar; cada cifra que sale en pantalla se calcula aquí, no se teclea.
"""
import numpy as np

MU = 398600.4418          # km³/s², parámetro gravitacional de la Tierra (WGS-84)
R_T = 6371.0              # km, radio medio de la Tierra
C_LUZ = 299792.458        # km/s
DIA_SIDEREO = 86164.0905  # s


def v_circular(r):
    return np.sqrt(MU / r)


def periodo(a):
    return 2 * np.pi * np.sqrt(a ** 3 / MU)


def v_visviva(r, a):
    return np.sqrt(MU * (2 / r - 1 / a))


def kepler_E(M, e):
    """Anomalía excéntrica desde la media (Newton; converge para e < 1)."""
    M = np.asarray(M, float)
    E = M + e * np.sin(M) if e < 0.8 else np.pi * np.ones_like(M)
    for _ in range(40):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    return E


def anomalia_verdadera(M, e):
    E = kepler_E(M, e)
    return 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))


# ── Estructura de cada reel (ronda 5, 2026-10-07) ────────────────────────────────────────────────────
#   [0, H0)                   título: el cuadro inicial se sostiene (también es la portada y el empalme del loop)
#   [H0, H0 + TB)             CUERPO: la animación y sus textos, a ritmo de lectura, terminando en una pausa con el mensaje
#   [H0 + TB, V)              CIERRE: el logo de Co.De sobre el fondo Órbita (se dibuja, se sostiene) y se DISUELVE en
#                             el título del inicio ⇒ el último cuadro = el primero y el loop no se corta.
# El reloj de la escena vale 0 fuera del cuerpo, así que lo que está bajo el logo se reinicia sin que se vea.
H0 = 0.6
LOGO_FADE_IN = 0.7                             # el fondo Órbita del cierre aparece mientras se traza el logo
LOGO_RETRASO = 0.6                             # espera antes de trazar el logo (el fondo ya cubre)
LOGO_ANIM = 2.6                                # animar_entrada(estilo="trazo")
LOGO_HOLD = 1.5
LOGO_FADE_OUT = 0.9
LOGO_TOTAL = LOGO_RETRASO + LOGO_ANIM + (LOGO_HOLD + LOGO_FADE_OUT - LOGO_RETRASO)   # 5.0 s


def duracion_total(cuerpo):
    return round(H0 + cuerpo + LOGO_TOTAL, 1)


def hm(seg):
    """Segundos → «5 h 17 min» / «96 min»."""
    m = int(round(seg / 60))
    return f"{m // 60} h {m % 60} min" if m >= 60 else f"{m} min"


# ── 1 · Por qué no se cae (cañón de Newton) ───────────────────────────────────────────────────────
# Tiro horizontal desde lo alto de una montaña exagerada (r0 = 1.15 R). Con v = k·v_circ(r0) la órbita es una
# elipse con apoapsis en el cañón y e = 1 − k². En pantalla la vuelta circular dura P1 s; las demás se integran
# con la misma gravedad. Sin aire (experimento mental de Newton).
N_R0 = 1.15
N_K = (0.50, 0.72, 0.87, 1.0)
N_P = 10.0                                  # s en pantalla para la vuelta circular
N_V_SUP = v_circular(R_T)                  # 7.9 km/s: velocidad circular a ras de suelo


def newton_tiro(k, n=900):
    """(t, θ, r) en unidades de R = 1 y tiempo de pantalla; θ desde la vertical del cañón, sentido horario."""
    e = 1 - k ** 2
    a = N_R0 / (1 + e)
    th = np.linspace(0, 2 * np.pi, n)
    r = a * (1 - e ** 2) / (1 - e * np.cos(th))
    if k < 1:
        dentro = np.nonzero(r <= 1.0)[0]
        fin = dentro[0] if len(dentro) else n
        th, r = th[: fin + 1], np.minimum(r[: fin + 1], 1.0 + 1e-9)
    mu_s = (2 * np.pi / N_P) ** 2 * N_R0 ** 3
    h = np.sqrt(mu_s * a * (1 - e ** 2))
    dt = np.r_[0, np.cumsum(0.5 * (r[1:] ** 2 + r[:-1] ** 2) / h * np.diff(th))]
    return dt, th, r


def _plan_newton():
    plan, t = [], 0.6
    for k in N_K:
        dur = newton_tiro(k)[0][-1]
        plan.append((k, t, dur))
        t += dur + (1.0 if k < 1 else 0.0)
    return plan, float(np.ceil(plan[-1][1] + plan[-1][2] + 4.5))   # la vuelta circular se completa y queda una pausa de lectura


NEWTON_PLAN, NEWTON_T = _plan_newton()


# ── 2 · Tres alturas (LEO/MEO/GEO a escala, 1 día sidéreo = T) ─────────────────────────────────────
# Vueltas enteras por día para que el loop cierre: GEO 1, MEO (GPS) 2, LEO 15 (≈ 96 min ⇒ ≈ 560 km).
ALT_T = 16.0                               # un día sidéreo
ALT_VENTANAS = ((0.0, 5.5), (5.5, 11.0), (11.0, 16.5))     # LEO · MEO · GEO
ALT_TB = 21.5
ALT_VUELTAS = {"LEO": 15, "MEO": 2, "GEO": 1}


def _altura_por_vueltas(n):
    a = (MU * (DIA_SIDEREO / n / (2 * np.pi)) ** 2) ** (1 / 3)
    return a


ALT_A = {k: _altura_por_vueltas(n) for k, n in ALT_VUELTAS.items()}


# ── 3 · Hohmann LEO 400 km ↔ GEO (a escala, plano ecuatorial) ───────────────────────────────────────
HOH_R1, HOH_R2 = R_T + 400.0, 42164.0
HOH_A = (HOH_R1 + HOH_R2) / 2
HOH_E = (HOH_R2 - HOH_R1) / (HOH_R2 + HOH_R1)
HOH_DV1 = v_visviva(HOH_R1, HOH_A) - v_circular(HOH_R1)
HOH_DV2 = v_circular(HOH_R2) - v_visviva(HOH_R2, HOH_A)
HOH_VIAJE = periodo(HOH_A) / 2
# Segmentos (s de pantalla): LEO media vuelta · subida · GEO media vuelta · bajada. Encendidos en las uniones.
HOH_SEG = (("leo", 4.2), ("sube", 4.6), ("geo", 4.4), ("baja", 4.6))
HOH_T = sum(d for _, d in HOH_SEG)
HOH_QUEMAS = tuple(float(x) for x in np.cumsum([d for _, d in HOH_SEG]))   # 4.2 (sube), 8.8, 13.2 (frena), 17.8 (vuelve a LEO)
HOH_TB = HOH_T + HOH_SEG[0][1]            # tras volver a LEO, otra media vuelta de pausa (sin quemar de nuevo)


def hohmann_pos(t):
    """(x, y) en km del satélite en la fase t del ciclo. Sentido antihorario; quemas abajo (θ = −90°) y arriba."""
    t = t % HOH_T
    for nombre, d in HOH_SEG:
        if t < d:
            u = t / d
            break
        t -= d
    if nombre == "leo":                     # de arriba (90°) a abajo (270°) por la izquierda
        th, r = np.pi / 2 + np.pi * u, HOH_R1
    elif nombre == "geo":
        th, r = np.pi / 2 + np.pi * u, HOH_R2
    else:                                   # media elipse con timing de Kepler (M de 0 a π)
        if nombre == "sube":                # perigeo abajo → apogeo arriba, por la derecha (rápido → lento)
            nu = anomalia_verdadera(np.pi * u, HOH_E)
            th = -np.pi / 2 + nu
        else:                               # apogeo abajo → perigeo arriba, por la derecha (lento → rápido)
            nu = anomalia_verdadera(np.pi + np.pi * u, HOH_E)
            th = np.pi / 2 + nu
        r = HOH_A * (1 - HOH_E ** 2) / (1 + HOH_E * np.cos(nu))
    return np.array([r * np.cos(th), r * np.sin(th)])


# ── 4 · La luz también tarda (latencia mínima al cenit) ────────────────────────────────────────────
LAT_LEO_H, LAT_GEO_H = 550.0, 35786.0
LAT_LEO_MS = 2 * LAT_LEO_H / C_LUZ * 1e3           # subir y bajar: 3.67 ms
LAT_GEO_MS = 2 * LAT_GEO_H / C_LUZ * 1e3           # 238.7 ms
LAT_VIAJES = int(LAT_GEO_MS // LAT_LEO_MS)          # 65
LAT_LENTO = 6.0 / (LAT_GEO_MS / 1e3)                # 239 ms de luz = 6 s de pantalla (≈ 25× más lento)
LAT_IDA = 0.6                                       # s: arranque del pulso
LAT_TB = 13.0                                       # 0.6 + 6 + pausa final de lectura


def lat_ms(t):
    """Milisegundos de luz transcurridos en el instante t del cuerpo (0 antes del disparo, tope al llegar)."""
    return float(np.clip((t - LAT_IDA) / LAT_LENTO * 1e3, 0, LAT_GEO_MS))


# ── 5 · Más cerca, más rápido (2.ª ley de Kepler, órbita tipo Molniya) ──────────────────────────────
MOL_T_REAL = DIA_SIDEREO / 2                        # 11 h 58 min
MOL_A = (MU * (MOL_T_REAL / (2 * np.pi)) ** 2) ** (1 / 3)
MOL_E = 0.74
MOL_RP, MOL_RA = MOL_A * (1 - MOL_E), MOL_A * (1 + MOL_E)
MOL_VP, MOL_VA = v_visviva(MOL_RP, MOL_A), v_visviva(MOL_RA, MOL_A)
MOL_T = 16.0                                        # una vuelta de 11 h 58 min: 1 s de pantalla ≈ 45 min
MOL_N = 12                                          # franjas de igual tiempo (≈ 1 h cada una)
MOL_TB = 21.0


def mol_pos(t):
    """(x, y) en km: foco (Tierra) en el origen, perigeo ABAJO y apogeo arriba; perigeo en t = 0."""
    M = 2 * np.pi * (np.asarray(t) % MOL_T) / MOL_T
    nu = anomalia_verdadera(M, MOL_E)
    r = MOL_A * (1 - MOL_E ** 2) / (1 + MOL_E * np.cos(nu))
    th = -np.pi / 2 + nu
    return np.stack([r * np.cos(th), r * np.sin(th)], -1)


# ── 6 · Ventana de contacto (pase cenital LEO 550 km, máscara de 10°) ───────────────────────────────
VEN_H, VEN_MASCARA = 550.0, 10.0
VEN_LAMBDA = np.arccos(R_T * np.cos(np.deg2rad(VEN_MASCARA)) / (R_T + VEN_H)) - np.deg2rad(VEN_MASCARA)
VEN_P = periodo(R_T + VEN_H)
VEN_VISIBLE = VEN_P * 2 * VEN_LAMBDA / (2 * np.pi)  # ≈ 8 min (sin rotación terrestre: mejor caso)
VEN_T = 20.0                                        # una vuelta de 96 min: 1 s ≈ 4.8 min ⇒ la ventana de 8 min dura 1.7 s
VEN_TB = 19.0


def ven_angulo(t):
    """Ángulo central desde la estación (0 = cenit), sentido horario; el pase está centrado en T/2."""
    return 2 * np.pi * (min(t, VEN_T) / VEN_T - 0.5)


def ven_visible(t):
    return abs(ven_angulo(t)) <= VEN_LAMBDA


VEN_AOS = VEN_T / 2 - VEN_LAMBDA / (2 * np.pi) * VEN_T
VEN_LOS = VEN_T / 2 + VEN_LAMBDA / (2 * np.pi) * VEN_T


# ══ Ronda 2 (2026-10-06) ══════════════════════════════════════════════════════════════════════════

# ── 7 · Velocidad de escape (cónicas desde 400 km) ─────────────────────────────────────────────────
ESC_R0 = R_T + 400.0
ESC_VC, ESC_VE = v_circular(ESC_R0), np.sqrt(2) * v_circular(ESC_R0)
ESC_K = (1.0, 1.22, np.sqrt(2), 1.62)       # círculo · elipse · parábola (escape) · hipérbola
ESC_D = 3.0                                  # s de pantalla por trayectoria (tiempo normalizado)
ESC_RMAX = 4.6                               # en unidades de r0: donde se corta la trayectoria abierta
ESC_PLAN = tuple((k, 0.6 + i * (ESC_D + 1.0)) for i, k in enumerate(ESC_K))
ESC_TB = float(np.ceil(ESC_PLAN[-1][1] + ESC_D + 5.0))


def escape_tiro(k, n=700):
    """(u, θ, r/r0): u ∈ [0, 1] es el tiempo normalizado (dt ∝ r² dθ). θ = 0 en el periapsis."""
    e = k ** 2 - 1
    if e < 1:
        th_max = 2 * np.pi
    else:
        th_max = np.arccos(-1 / e) - 1e-3
    th = np.linspace(0, th_max, n)
    r = (1 + e) / (1 + e * np.cos(th))
    dentro = r <= ESC_RMAX
    th, r = th[dentro], r[dentro]
    dt = np.r_[0, np.cumsum(0.5 * (r[1:] ** 2 + r[:-1] ** 2) * np.diff(th))]
    return dt / dt[-1], th, r


# ── 8 · ¿Cuánto de la Tierra ve un satélite? (huella al horizonte) ────────────────────────────────
COB_H = (550.0, 35786.0)
COB_TB = 15.0
COB_SUBE = (4.0, 8.5)                        # LEO hasta 4.0 s · sube · GEO desde 8.5 s


def cob_altura(t):
    """LEO → GEO (interpolación logarítmica, suave) y se queda en GEO."""
    s = lambda u: u * u * (3 - 2 * u)
    u = float(np.clip((t - COB_SUBE[0]) / (COB_SUBE[1] - COB_SUBE[0]), 0, 1))
    u = s(u)
    return COB_H[0] * (COB_H[1] / COB_H[0]) ** u


def cob_fraccion(h):
    return (1 - R_T / (R_T + h)) / 2       # casquete visible al horizonte (elevación 0°)


def cob_semiangulo(h):
    return np.arccos(R_T / (R_T + h))


# ── 9 · 16 amaneceres al día (ISS, sombra cilíndrica, β = 0) ───────────────────────────────────────
AMA_A = R_T + 420.0
AMA_P = periodo(AMA_A)
AMA_SOMBRA = np.arcsin(R_T / AMA_A) / np.pi         # fracción de la vuelta en la sombra
AMA_POR_DIA = 86400 / AMA_P
AMA_T = 16.0                                        # una vuelta de 93 min: 1 s ≈ 5.8 min
AMA_TB = 21.0


# ── 10 · Por qué un cohete es casi todo combustible (Tsiolkovsky, una etapa ideal) ─────────────────
COH_VE = 3.3                                  # km/s ≈ Isp 336 s (queroseno/oxígeno, vacío)
COH_DV = 9.4                                  # km/s típicos para llegar a LEO, con pérdidas
COH_FRAC = 1 - np.exp(-COH_DV / COH_VE)
COH_LLENA, COH_QUEMA = 2.5, 10.5              # [0, 2.5) se llena · [2.5, 10.5) quema · resto: lectura
COH_TB = 17.0


def coh_estado(t):
    """(fracción de propelente que queda, Δv acumulado km/s) en la fase t."""
    m_seca = 1 - COH_FRAC
    if t < COH_LLENA:
        u = t / COH_LLENA
        return u * u * (3 - 2 * u), 0.0
    if t < COH_QUEMA:
        u = (t - COH_LLENA) / (COH_QUEMA - COH_LLENA)
        m = 1 - COH_FRAC * u                      # gasto de masa constante
        return (m - m_seca) / COH_FRAC, COH_VE * np.log(1 / m)
    return 0.0, COH_DV


# ── 11 · ¿No hay gravedad en la ISS? ────────────────────────────────────────────────────────────────
GRA_G0 = MU / R_T ** 2 * 1e3                  # m/s²
GRA_GISS = MU / (R_T + 420.0) ** 2 * 1e3
GRA_FRAC = GRA_GISS / GRA_G0
GRA_T = 12.0                                        # una vuelta de la ISS en pantalla
GRA_TB = 15.0


# ── 12 · ¿Cuánto tarda un mensaje a Marte? (órbitas circulares coplanares) ─────────────────────────
UA = 149597870.7
MAR_A = 1.5237                                # UA
MAR_T = 16.0                                        # un periodo sinódico (≈ 780 días) en 16 s
MAR_TB = 19.0
MAR_PULSOS = 16                               # pulsos ilustrativos por ciclo


def mar_distancia(t):
    """Distancia Tierra–Marte (UA) cuando el ángulo entre ambos recorre una vuelta por ciclo (oposición en t = 0)."""
    phi = 2 * np.pi * t / MAR_T
    return np.sqrt(1 + MAR_A ** 2 - 2 * MAR_A * np.cos(phi))


def mar_minutos(t):
    return mar_distancia(t) * UA / C_LUZ / 60


MAR_MIN, MAR_MAX = (MAR_A - 1) * UA / C_LUZ / 60, (MAR_A + 1) * UA / C_LUZ / 60


# ── 13 · Tres satélites para todo el planeta (Clarke, 1945) ────────────────────────────────────────
CLA_R = 42164.0
CLA_SEMI = np.arccos(R_T / CLA_R)             # semiángulo de la huella al horizonte
CLA_LAT = np.rad2deg(CLA_SEMI)                # latitud máxima visible desde GEO (≈ 81°)
CLA_T = 12.0                                        # una vuelta de la vista inercial
CLA_TB = 18.0
CLA_APARECE = (0.6, 5.6, 6.6)                 # t en que entra cada satélite


# ── 14 · Láser a la Luna, en tiempo real ───────────────────────────────────────────────────────────
LUN_D = 384400.0                              # km, distancia media
LUN_IDA = LUN_D / C_LUZ                       # 1.28 s
LUN_CICLO = 4.4                               # ida + vuelta (2.56 s) + pausa
LUN_DISPAROS = (0.8, 0.8 + LUN_CICLO, 0.8 + 2 * LUN_CICLO)
LUN_TB = 13.0


CUERPO = {"ReelNoSeCae": NEWTON_T, "ReelTresAlturas": ALT_TB, "ReelHohmann": HOH_TB, "ReelLatencia": LAT_TB,
          "ReelAreasIguales": MOL_TB, "ReelVentanaContacto": VEN_TB, "ReelVelocidadEscape": ESC_TB, "ReelCobertura": COB_TB,
          "ReelAmaneceres": AMA_TB, "ReelCohete": COH_TB, "ReelGravedadISS": GRA_TB, "ReelMensajeMarte": MAR_TB,
          "ReelClarke": CLA_TB, "ReelLaserLuna": LUN_TB}


def leyendas(nombre):
    """Instantes (reloj del cuerpo) en que cambia la leyenda de cada reel: el audio marca cada cambio con una nota suave.
    Debe coincidir con las ventanas de `leyenda(...)` de 37-reels-divulgacion.py."""
    t_orb = NEWTON_PLAN[-1][1]
    q = HOH_QUEMAS
    return {"ReelNoSeCae": (0.0, t_orb - 0.4, t_orb + 5.6), "ReelTresAlturas": (0.0, 5.5, 11.0, 16.5),
            "ReelHohmann": (0.0, q[0] - 0.2, q[1] - 0.2, q[2] - 0.2, q[3] - 0.2), "ReelLatencia": (0.0, LAT_IDA + 6.4),
            "ReelAreasIguales": (0.0, 4.2, 8.0, 12.2), "ReelVentanaContacto": (0.0, 7.0, 13.5),
            "ReelVelocidadEscape": (0.0, ESC_PLAN[2][1] - 0.2, ESC_PLAN[3][1] - 0.2),
            "ReelCobertura": (0.0, COB_SUBE[0] + 0.2, COB_SUBE[1] + 0.2), "ReelAmaneceres": (0.0, 5.8, 11.8),
            "ReelCohete": (0.0, 6.2, COH_QUEMA + 1.0), "ReelGravedadISS": (0.0, 7.2), "ReelMensajeMarte": (0.0, 5.6, 11.6),
            "ReelClarke": (0.0, 5.4, 11.8), "ReelLaserLuna": (0.0, LUN_DISPAROS[1])}[nombre]


if __name__ == "__main__":
    print("Newton: TB", NEWTON_T, [(k, round(t0, 2), round(d, 2)) for k, t0, d in NEWTON_PLAN], "v_sup", round(N_V_SUP, 2))
    for k, a in ALT_A.items():
        print(k, f"alt {a - R_T:,.0f} km", hm(periodo(a)), f"{v_circular(a):.2f} km/s")
    print("Hohmann dv", round(HOH_DV1, 3), round(HOH_DV2, 3), "viaje", hm(HOH_VIAJE), "T", HOH_T, HOH_QUEMAS, "TB", HOH_TB)
    print("Latencia", round(LAT_LEO_MS, 2), round(LAT_GEO_MS, 1), LAT_VIAJES, "lento", round(LAT_LENTO, 1))
    print("Molniya a", round(MOL_A), "rp alt", round(MOL_RP - R_T), "ra alt", round(MOL_RA - R_T), "vp", round(MOL_VP, 2), "va", round(MOL_VA, 2))
    print("Ventana λ", round(np.rad2deg(VEN_LAMBDA), 2), "P", hm(VEN_P), "visible", round(VEN_VISIBLE / 60, 2), "min", VEN_AOS, VEN_LOS)
    print("Escape vc", round(ESC_VC, 2), "ve", round(ESC_VE, 2), "TB", ESC_TB, ESC_PLAN)
    print("Cobertura LEO", round(100 * cob_fraccion(550), 1), "% GEO", round(100 * cob_fraccion(35786), 1), "%")
    print("Amaneceres P", hm(AMA_P), "sombra", round(AMA_SOMBRA, 3), hm(AMA_P * AMA_SOMBRA), "por día", round(AMA_POR_DIA, 1))
    print("Cohete frac", round(COH_FRAC, 3))
    print("Gravedad", round(GRA_G0, 2), round(GRA_GISS, 2), round(GRA_FRAC, 3))
    print("Marte min", round(MAR_MIN, 1), "max", round(MAR_MAX, 1))
    print("Clarke lat", round(CLA_LAT, 1))
    print("Luna ida", round(LUN_IDA, 3), "ida y vuelta", round(2 * LUN_IDA, 2))
    print("Ventana λ visible", round(VEN_AOS, 2), round(VEN_LOS, 2))
    for n, tb in CUERPO.items():
        print(f"{n}: cuerpo {tb} s · total {duracion_total(tb)} s")
