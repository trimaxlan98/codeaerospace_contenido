"""Electrónica en el espacio: las cuentas de la serie de reels «Electrónica espacial» (44-reels-electronica.py).

numpy puro y determinista (sin red ni disco). Cada cifra que la serie rotula sale de una de estas funciones, evaluada en
`datos_el.py` con supuestos declarados. `python3 electronica_espacio.py` corre las pruebas.

    carga_depositada_fc     ion pesado en silicio: Q = LET · ρ · L · e / E_par  (≈ 1 pC/µm a 97 MeV·cm²/mg)
    falla_tmr               tres copias que votan: falla si fallan dos o tres → 3p² − 2p³
    hamming74 / sindrome    código de Hamming (7,4): 3 bits de paridad protegen 4 de datos; el síndrome señala el bit volteado
    periodo_min             periodo de una órbita circular (Kepler)
    fraccion_eclipse        fracción de la órbita en sombra (cilindro, β = 0, el peor caso)
    potencia_celdas_w       N celdas solares de área A y eficiencia η frente al Sol (1361 W/m²)
    temp_equilibrio_c       placa al Sol, sin aire: α·S = ε·σ·T⁴ (cara trasera aislada)
    area_radiador_cm2       superficie que tira P watts al espacio a T °C: P = ε·σ·T⁴·A (sin Sol)
    tiempo_bajada_s         bits / tasa: cuánto tarda en bajar un archivo
"""
import numpy as np

Q_E = 1.602176634e-19        # C
RHO_SI = 2.33                # g/cm³
E_PAR_SI = 3.6               # eV por par electrón-hueco en silicio
MU_TIERRA = 3.986004418e14   # m³/s²
R_TIERRA = 6371e3            # m (radio medio)
S_SOL = 1361.0               # W/m², constante solar (fuera de la atmósfera)
SIGMA = 5.670374419e-8       # W/(m²·K⁴)


def carga_depositada_fc(let_mev_cm2_mg, largo_um):
    """Carga (fC) que libera un ion de LET dada al cruzar `largo_um` micras de silicio."""
    mev_por_um = let_mev_cm2_mg * RHO_SI * 1e3 * 1e-4          # mg/cm³ · cm/µm
    pares = mev_por_um * 1e6 / E_PAR_SI * largo_um
    return pares * Q_E * 1e15


def falla_tmr(p):
    """Probabilidad de que el voto de 3 copias independientes salga mal (≥ 2 copias fallan a la vez)."""
    return 3 * p ** 2 - 2 * p ** 3


# Hamming (7,4), posiciones 1..7: paridades en 1, 2, 4; datos en 3, 5, 6, 7.
def hamming74(d):
    d1, d2, d3, d4 = (int(b) for b in d)
    p1, p2, p4 = d1 ^ d2 ^ d4, d1 ^ d3 ^ d4, d2 ^ d3 ^ d4
    return [p1, p2, d1, p4, d2, d3, d4]


def sindrome(c):
    """Posición (1..7) del bit volteado; 0 si la palabra está bien."""
    s = 0
    for k in (1, 2, 4):
        par = 0
        for pos in range(1, 8):
            if pos & k:
                par ^= int(c[pos - 1])
        s += k * par
    return s


def periodo_min(h_m):
    a = R_TIERRA + h_m
    return 2 * np.pi * np.sqrt(a ** 3 / MU_TIERRA) / 60


def fraccion_eclipse(h_m):
    """Sombra cilíndrica, Sol en el plano de la órbita (β = 0): la noche más larga."""
    return float(np.arcsin(R_TIERRA / (R_TIERRA + h_m)) / np.pi)


def potencia_celdas_w(n, area_cm2, eficiencia, coseno=1.0):
    return n * area_cm2 * 1e-4 * S_SOL * eficiencia * coseno


def temp_equilibrio_c(alfa=1.0, eps=1.0, s=S_SOL):
    return (alfa * s / (eps * SIGMA)) ** 0.25 - 273.15


def area_radiador_cm2(p_w, t_c, eps=0.9):
    return p_w / (eps * SIGMA * (t_c + 273.15) ** 4) * 1e4


def tiempo_bajada_s(megabytes, bps):
    return megabytes * 1e6 * 8 / bps


if __name__ == "__main__":
    assert abs(carga_depositada_fc(97, 1) - 1004) < 15                    # la regla de 1 pC/µm
    assert abs(falla_tmr(1e-3) - 2.998e-6) < 1e-9
    for k in range(16):
        d = [(k >> j) & 1 for j in range(4)]
        c = hamming74(d)
        assert sindrome(c) == 0
        for pos in range(1, 8):
            m = list(c); m[pos - 1] ^= 1
            assert sindrome(m) == pos
    assert abs(periodo_min(550e3) - 95.6) < 0.1
    assert abs(fraccion_eclipse(550e3) * periodo_min(550e3) - 35.6) < 0.3
    assert abs(temp_equilibrio_c() - 121) < 1.5
    assert abs(area_radiador_cm2(1, 20, 1.0) - 23.9) < 0.3
    assert abs(tiempo_bajada_s(3, 9600) - 2500) < 1e-6
    print("electronica_espacio: pruebas OK")
