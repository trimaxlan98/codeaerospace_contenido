"""Cálculo aplicado al espacio: las cuentas de la serie de reels «Cálculo en el espacio» (45-reels-calculo.py).

numpy puro y determinista (sin red ni disco). Cada cifra que la serie rotula sale de una de estas funciones, evaluada en
`datos_ca.py` con supuestos declarados. `python3 calculo_espacio.py` corre las pruebas.

    distancia_km            gran círculo entre dos puntos (haversine, Tierra esférica)
    v_circular / periodo_s  órbita circular: v = √(μ/r), T = 2π√(r³/μ)
    v_suelo                 velocidad de la «sombra» del satélite sobre el suelo: v·R/r
    altura_max              derivada cero: h = v²/2g (el punto más alto de un salto)
    orbita_euler            integrar la órbita con pasos de Euler: con pasos grandes la energía crece y el satélite se escapa
    rpm_gravedad            gravedad artificial: a = ω²r → rpm para 1 g a un radio dado
    periodo_sinodico        tasas relacionadas: 1/S = 1/T1 − 1/T2 (cada cuánto se repite la alineación Tierra–Marte)
    fraccion_restante       decaimiento exponencial: 2^(−t/T½)
    horizonte_km            tangente desde una altura h: d = √(2Rh + h²) ≈ √(2Rh)
    tunel_min               ecuación diferencial x'' = −(g/R)x: ir de un lado al otro por un túnel recto = medio periodo
"""
import numpy as np

MU = 3.986004418e14          # m³/s²
R_T = 6371e3                 # m (radio medio)
G0 = 9.80665                 # m/s²
G_LUNA = 1.62                # m/s²


def distancia_km(lat1, lon1, lat2, lon2):
    f1, f2 = np.radians(lat1), np.radians(lat2)
    df, dl = f2 - f1, np.radians(lon2 - lon1)
    a = np.sin(df / 2) ** 2 + np.cos(f1) * np.cos(f2) * np.sin(dl / 2) ** 2
    return float(2 * R_T * np.arcsin(np.sqrt(a)) / 1e3)


def v_circular(h_m):
    return float(np.sqrt(MU / (R_T + h_m)))


def periodo_s(h_m):
    return float(2 * np.pi * np.sqrt((R_T + h_m) ** 3 / MU))


def v_suelo(h_m):
    return v_circular(h_m) * R_T / (R_T + h_m)


def altura_max(v0, g):
    return v0 * v0 / (2 * g)


def orbita_euler(pasos_por_vuelta, vueltas=1.0, r0=1.0, mu=1.0):
    """Euler explícito en unidades adimensionales (órbita circular de radio 1). Devuelve los puntos y el radio final."""
    T = 2 * np.pi * np.sqrt(r0 ** 3 / mu)
    dt = T / pasos_por_vuelta
    p, v = np.array([r0, 0.0]), np.array([0.0, np.sqrt(mu / r0)])
    pts = [p.copy()]
    for _ in range(int(round(pasos_por_vuelta * vueltas))):
        a = -mu * p / np.linalg.norm(p) ** 3
        p, v = p + v * dt, v + a * dt
        pts.append(p.copy())
    return np.array(pts), float(np.linalg.norm(p))


def rpm_gravedad(radio_m, g=G0):
    return float(np.sqrt(g / radio_m) * 60 / (2 * np.pi))


def periodo_sinodico(t1, t2):
    return 1.0 / abs(1.0 / t1 - 1.0 / t2)


def fraccion_restante(t, t_mitad):
    return 2.0 ** (-t / t_mitad)


def horizonte_km(h_m):
    return float(np.sqrt(2 * R_T * h_m + h_m * h_m) / 1e3)


def tunel_min():
    return float(np.pi * np.sqrt(R_T / G0) / 60)


if __name__ == "__main__":
    assert abs(distancia_km(0, 0, 0, 1) - 111.19) < 0.1
    assert abs(v_circular(400e3) - 7672) < 5
    assert abs(periodo_s(400e3) / 60 - 92.6) < 0.2
    assert abs(altura_max(3.13, G0) - 0.5) < 0.01
    _, r_mal = orbita_euler(20)
    _, r_bien = orbita_euler(2000)
    assert r_mal > 1.5 and abs(r_bien - 1) < 0.05 and abs(orbita_euler(20000)[1] - 1) < 0.005    # primer orden: 10× pasos → 10× menos error
    assert abs(rpm_gravedad(100) - 2.99) < 0.02
    assert abs(periodo_sinodico(365.256, 686.98) - 779.9) < 0.5
    assert abs(fraccion_restante(87.7, 87.7) - 0.5) < 1e-12
    assert abs(horizonte_km(400e3) - 2293) < 3
    assert abs(tunel_min() - 42.2) < 0.2
    print("calculo_espacio: pruebas OK")
