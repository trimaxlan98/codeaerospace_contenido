"""Datos y línea de tiempo de la serie de reels «Electrónica espacial» (44-reels-electronica.py). Tema: Electrónica (verde de
placa de circuito y cobre), fondo vertical propio (fondos_reel.electronica: el borde de una placa con pistas, pads y un chip
como horizonte, resplandor verde que sube).

Divulgación de electrónica aplicada a sistemas espaciales: radiación y fallas (SEU, latch-up, dosis), cómo se protegen
(votación triple, código de Hamming), energía (paneles, batería en eclipse), calor en el vacío, enlace de bajada y por qué
las computadoras de vuelo son «lentas». Las cuentas salen de `electronica_espacio.py` (con sus pruebas) evaluadas aquí con
supuestos declarados; las cifras de componentes reales son de fuentes públicas (citadas en el ⚠️ de los pies). No hay
mediciones propias. Regla del dueño: pocas cifras, cada una con una comparación cotidiana. Sin tesis ni clientes.
"""
import divulgacion_fisica as F
import electronica_espacio as E

# ── 1 · Bit volteado: ion con LET 10 MeV·cm²/mg cruzando 1 µm de silicio vs. carga crítica de una celda SRAM moderna (~1 fC) ──
LET_EJ = 10.0
CARGA_ION_FC = E.carga_depositada_fc(LET_EJ, 1.0)          # ≈ 104 fC
Q_CRITICA_FC = 1.0                                         # orden de magnitud (SRAM de 65 nm: ~1–1.5 fC)
VECES_BIT = CARGA_ION_FC / Q_CRITICA_FC                    # ≈ 100

# ── 2 · Tres computadoras votan: si una copia falla con p = 1/1000, el voto falla ~3 en un millón ───────────────────────────
P_COPIA = 1e-3
P_VOTO = E.falla_tmr(P_COPIA)                              # ≈ 3.0e-6
VECES_TMR = P_COPIA / P_VOTO                               # ≈ 330

# ── 3 · Hamming (7,4): un dato de 4 bits, se voltea el bit 6, el síndrome lo señala ─────────────────────────────────────────
DATO = [1, 0, 1, 1]
PALABRA = E.hamming74(DATO)                                # [p1 p2 d1 p4 d2 d3 d4]
BIT_MALO = 6
RECIBIDA = [b ^ (1 if i + 1 == BIT_MALO else 0) for i, b in enumerate(PALABRA)]
SINDROME = E.sindrome(RECIBIDA)                            # = 6
assert SINDROME == BIT_MALO

# ── 4 · Dosis acumulada (krad de silicio, órdenes de magnitud de fuentes públicas) ──────────────────────────────────────────
DOSIS_HUMANO_KRAD = 0.5            # ~5 Gy de cuerpo entero (dosis letal media aproximada)
DOSIS_COMERCIAL_KRAD = 5.0         # muchos chips comerciales: ~5 krad (algunos fallan antes de 1 krad)
DOSIS_ENDURECIDO_KRAD = 300.0      # endurecidos: 100 krad a 1 Mrad (se dibuja 300, a la mitad en escala log)
DOSIS_LEO_ANUAL_KRAD = 1.0         # ~1 krad/año detrás de ~1–2.5 mm de aluminio (NASA NEPP, 780 km)
VECES_COMERCIAL = DOSIS_COMERCIAL_KRAD / DOSIS_HUMANO_KRAD                 # 10

# ── 6 · Panel de un cubesat 1U: dos celdas de triple unión de 26.5 cm² al 28 %, de frente al Sol ─────────────────────────────
CELDAS, CELDA_CM2, EFIC = 2, 26.5, 0.28
PANEL_W = E.potencia_celdas_w(CELDAS, CELDA_CM2, EFIC)     # ≈ 2.0 W
CARGADOR_W = 5.0                                           # cargador de celular básico

# ── 7 · Batería: 550 km, noches por día, minutos de noche y ciclos por año ─────────────────────────────────────────────────
H_LEO = 550e3
PERIODO_MIN = E.periodo_min(H_LEO)                         # ≈ 95.5 min
NOCHE_MIN = E.fraccion_eclipse(H_LEO) * PERIODO_MIN        # ≈ 35.5 min (peor caso, β = 0)
VUELTAS_DIA = 1440 / PERIODO_MIN                           # ≈ 15
CICLOS_ANIO = VUELTAS_DIA * 365                            # ≈ 5500
VECES_CELULAR = VUELTAS_DIA                                # un celular: ~1 ciclo al día

# ── 8 · Calor sin aire: placa negra al Sol (trasera aislada) y radiador para 1 W a 20 °C ────────────────────────────────────
T_PLACA_SOL_C = E.temp_equilibrio_c()                      # ≈ 120 °C
RADIADOR_1W_CM2 = E.area_radiador_cm2(1.0, 20.0, 0.9)     # ≈ 27 cm² → «una placa de 5 × 5 cm»

# ── 9 · Bajar una foto: 3 MB a 9600 bit/s (UHF de aficionado), pases de ~10 min ─────────────────────────────────────────────
FOTO_MB, TASA_BPS, PASE_MIN = 3.0, 9600, 10.0
BAJADA_MIN = E.tiempo_bajada_s(FOTO_MB, TASA_BPS) / 60     # ≈ 42 min
PASES = BAJADA_MIN / PASE_MIN                              # ≈ 4.2 → «unos 4–5 pases»

# ── 10 · Computadora de vuelo: RAD750 (hasta 200 MHz, Curiosity/Perseverance) vs. un celular (~3 GHz por núcleo) ──────────
RAD750_MHZ, CELULAR_MHZ = 200, 3000
VECES_RELOJ = CELULAR_MHZ / RAD750_MHZ                     # 15


CUERPO = {n: 20.0 for n in ("ReelELBit", "ReelELVoto", "ReelELHamming", "ReelELDosis", "ReelELLatch",
                            "ReelELPanel", "ReelELBateria", "ReelELCalor", "ReelELBajada", "ReelELLento")}
LEYENDAS = {n: (0.0, 6.0, 12.5) for n in CUERPO}
H0 = F.H0


def duracion(nombre):
    return F.duracion_total(CUERPO[nombre])


if __name__ == "__main__":
    for k, v in sorted(globals().items()):
        if k.isupper() and isinstance(v, (int, float, list)):
            print(f"{k} = {v}")
