"""Datos y línea de tiempo de la serie de reels «CO.DE Triage» (39-reels-triage.py). Tema: Espectro.

Fuente: el repositorio code-triage (Co.De Triage: clasificador de grabaciones de pases de satélite de la red abierta SatNOGS),
commit 65c93e0. Pedido del dueño (2026-10-07): DIVULGAR la ciencia de base y el funcionamiento de la plataforma, SIN cifras de
nicho que exijan contexto. Por eso las pocas cifras van traducidas a lenguaje llano («95 de cada 100», «casi el doble de momios»)
y cada una conserva aquí su archivo de origen.

Las cascadas (espectrogramas) de los reels son ILUSTRACIONES generadas con semilla (no son grabaciones de SatNOGS): en pantalla
lo dice el chip. Nada de la tesis doctoral ni de clientes.
"""
import numpy as np

import divulgacion_fisica as F

# ── Cifras (con su fuente en code-triage) ────────────────────────────────────────────────────────────────────────────
N_GRABACIONES = 7499          # waterfalls etiquetados (docs/fase5-whitepaper-es.md §2; plataformas 2026-07-30)
N_ESTACIONES = 402            # estaciones distintas en esa muestra (whitepaper §2)
N_EXAMEN = 731                # «test intacto», nunca usado para entrenar (docs/HANDOFF-tier-b-arch.md)
AUC_CLASIFICADOR = 0.9491     # convnext_nano afinado, en producción (HANDOFF-tier-b-arch.md; SUPER-ANALISIS-2026-09-25 §7)
PRECISION_OBJETIVO = 0.95     # el umbral se fija para que de lo marcado «con señal», ≥ 95 % lo sea (HANDOFF-tier-b-arch.md)
INGESTA_MIN = 30              # cada 30 min consulta SatNOGS (docs/mvp-triage-senales-satelitales.md)
# Estudio causal (docs/fase5-whitepaper-es.md §4): razones de momios (odds ratio) con ajuste por estación y satélite
OR_ELEVACION = 1.84           # pase que culmina sobre 40°
OR_DURACION = 1.58            # pase de ≥ 584 s (~10 min)
OR_ALTITUD_ESTACION = 0.96    # sin efecto (el intervalo incluye 1)
OR_HORA_DIURNA = 0.72         # parecía un efecto…
OR_HORA_PLACEBO = 1.15        # …pero con los datos barajados seguía apareciendo (3 de 3) → artefacto
PLACEBO_REPETICIONES = 3
# Pronóstico (docs/fase6-tecnologia-producto.md F6.T1–T2)
PRON_APARENTE = 0.883         # AUC reportada del modelo con «trampa»
PRON_FECHA_GAIN = 0.51        # la fecha de recolección: 51 % de la importancia
PRON_SIN_FECHA = 0.664        # al anular la fecha
PRON_HONESTO = 0.806          # modelo limpio, en estaciones que nunca vio


def de_cada(x, n=100):
    """0.9491 → 95 (de cada 100)."""
    return int(round(x * n))


# ── Cascadas ilustrativas (viridis, el mapa de color real de los waterfalls de SatNOGS) ───────────────────────────────
_VIRIDIS = np.array([[68, 1, 84], [72, 40, 120], [62, 74, 137], [49, 104, 142], [38, 130, 142], [31, 158, 137],
                     [53, 183, 121], [109, 205, 89], [180, 222, 44], [253, 231, 37]], float)


def viridis(v):
    v = np.clip(np.asarray(v, float), 0, 1) * (len(_VIRIDIS) - 1)
    i = np.minimum(v.astype(int), len(_VIRIDIS) - 2)
    f = (v - i)[..., None]
    return (_VIRIDIS[i] * (1 - f) + _VIRIDIS[i + 1] * f).astype(np.uint8)


def cascada(filas=180, cols=240, semilla=3, senal=True, curva=0.30, ancho=0.010, ruido=0.18, falla=False, debil=1.0):
    """Matriz [filas × cols] en 0–1: ruido + (opcional) la traza de un satélite que dibuja una S por el Doppler.
    `falla` corta la grabación (filas en negro y una franja dañada). Devuelve (matriz, x_de_la_traza_por_fila)."""
    rng = np.random.default_rng(semilla)
    t = np.linspace(0, 1, filas)[:, None]
    x = np.linspace(0, 1, cols)[None, :]
    base = 0.22 + ruido * np.abs(rng.standard_normal((filas, cols)))
    base += 0.05 * np.sin(2 * np.pi * (x * 3 + rng.random()))                         # ondulación suave del piso de ruido
    centro = 0.5 - curva * np.tanh((t - 0.5) / 0.14)                                 # la S del Doppler
    amp = np.exp(-((t - 0.5) / 0.33) ** 2)                                           # más fuerte en el punto más cercano
    if senal:
        base += debil * 0.85 * amp * np.exp(-((x - centro) / ancho) ** 2)
    for xs in (0.12, 0.83):                                                          # dos interferencias locales fijas
        base += 0.18 * np.exp(-((x - xs) / 0.004) ** 2)
    if falla:
        base[int(filas * 0.55):] = 0.03 + 0.02 * rng.random((filas - int(filas * 0.55), cols))
        base[int(filas * 0.40):int(filas * 0.47)] = 0.9 * rng.random((int(filas * 0.47) - int(filas * 0.40), cols))
    return np.clip(base, 0, 1), centro[:, 0]


# ── Línea de tiempo (s del cuerpo) ───────────────────────────────────────────────────────────────────────────────────
CUERPO = {"ReelTriCascada": 19.0, "ReelTriDoppler": 18.0, "ReelTriRuido": 18.0, "ReelTriRedNeuronal": 19.0,
          "ReelTriAprender": 20.0, "ReelTriBuenPase": 19.0, "ReelTriPlacebo": 20.0, "ReelTriTrampa": 20.0,
          "ReelTriPlataforma": 20.0, "ReelTriPronostico": 19.0}
LEYENDAS = {"ReelTriCascada": (0.0, 5.0, 10.5), "ReelTriDoppler": (0.0, 5.5, 11.0), "ReelTriRuido": (0.0, 5.0, 11.0),
            "ReelTriRedNeuronal": (0.0, 5.5, 11.5), "ReelTriAprender": (0.0, 6.0, 12.0), "ReelTriBuenPase": (0.0, 6.0, 12.0),
            "ReelTriPlacebo": (0.0, 5.5, 12.0), "ReelTriTrampa": (0.0, 5.5, 12.0), "ReelTriPlataforma": (0.0, 6.5, 12.5),
            "ReelTriPronostico": (0.0, 6.0, 12.0)}
H0 = F.H0


def duracion(nombre):
    return F.duracion_total(CUERPO[nombre])
