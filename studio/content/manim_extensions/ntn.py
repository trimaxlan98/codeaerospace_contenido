"""NTN para la tesis 6G: pase LEO, Doppler, handover, quorum PBFT, MA y gates.

La numerica es DETERMINISTA (`np.random.default_rng(semilla)`, nunca el
generador global) y no reimplementa lo que ya existe en la casa: la mecanica
orbital sale de `satelites.py` (`periodo_orbital`, `_subsat_uno`,
`ventana_visibilidad`, `azimut`) y el presupuesto de enlace de `enlace.py`
(`fspl_db`, `FSPL_K`). Lo que anade este modulo es lo que la tesis necesita y
no estaba:

  - `pase_leo(...)`  geometria completa de un pase: elevacion, distancia
    oblicua, AOS / TCA / LOS, duracion y traza terrestre.
  - `doppler(...)` y `retardo_ida_ms(...)` sobre esa geometria.
  - `handover(...)` cascada de cobertura de un tren de satelites, con los
    instantes de relevo y el hueco (si lo hay).
  - `quorum_pbft(n)` / `f_max(n)`: n >= 3f+1, quorum 2f+1 y los mensajes por
    fase (total exacto 2n(n-1)).
  - `margen_adaptativo(...)` y `gate(...)`: MA = (R_oraculo - R_best) /
    |R_best| con umbral 0.25, e IC95 % por bootstrap con semilla.
  - Dibujos (`curva_elevacion`, `cascada_handover`, `diagrama_pbft`,
    `curva_ma`, `traza_tierra`) construidos sobre `figura.py`, asi que salen
    igual en el tema `paper` de un articulo y en el tema `marca` de un video.

Constantes: las de `satelites.py` (R_T = 6371 km, mu = 398600.4418 km^3/s^2,
c = 299792.458 km/s, dia sidereo 86164 s). En pantalla van en GRIS: son dadas,
no medidas aqui.

Uso:
    import sys
    sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    import figura as fg, ntn

    fg.Figura(tema="paper", columnas=1)
    p = ntn.pase_leo(600.0, 53.0, lat_gs=19.43, lon_gs=-99.13)
    grupo = ntn.curva_elevacion(p)
"""

import numpy as np
from manim import (Circle, DashedLine, Dot, Group, Line, VGroup,
                   VMobject)

import enlace
import figura as fg
import satelites as sat

VERSION = "1.0"

# ── constantes (dadas, no medidas aqui) ─────────────────────────────────────
R_TIERRA_KM = sat.R_TIERRA_KM          # 6371.0
MU_TIERRA = sat.MU_TIERRA              # 398600.4418 km^3/s^2
C_LUZ_KM_S = sat.C_LUZ_KM_S            # 299792.458 km/s
OMEGA_TIERRA = sat.OMEGA_TIERRA        # rad/s (dia sidereo)
FSPL_K = enlace.FSPL_K                 # 92.45, el termino de la formula del curso

# El escenario del banco de pruebas de la tesis
# (pada-ntn-testbed/src/topology/scenarios.leo600.csv): un pase LEO-600 en
# nueve ticks, del borde del cono a la maxima elevacion y de vuelta.
TICKS_LEO600_MS = (12.9, 10.0, 8.0, 6.0, 4.5, 6.0, 8.0, 10.0, 12.9)
ALTURA_LEO600_KM = 600.0
ELEVACION_MINIMA_DEG = 10.0

# Umbral del margen adaptativo de la tesis (gates G0-G4).
UMBRAL_MA = 0.25
SEMILLAS_TESIS = (42, 43, 44)


# =============================================================================
# Presupuesto de enlace: dos formulas para el mismo numero
# =============================================================================

def fspl_db(d_km, f_ghz):
    """FSPL con la constante del curso (92.45). Es `enlace.fspl_db`."""
    return enlace.fspl_db(d_km, f_ghz)


def fspl_exacto_db(d_km, f_ghz):
    """FSPL sin constante redondeada: 20 log10(4 pi d f / c).

    Existe para poder MEDIR cuanto miente el 92.45 en vez de suponerlo. La
    constante exacta es 20 log10(4 pi 1e9 / 299792458 * 1e3) = 92.44778 dB,
    asi que la formula del curso sobra 0.0022 dB: por debajo de cualquier
    cifra que se rotule, y por eso se puede usar tranquilamente.
    """
    d = np.asarray(d_km, dtype=np.float64) * 1e3      # m
    f = np.asarray(f_ghz, dtype=np.float64) * 1e9     # Hz
    return 20.0 * np.log10(4.0 * np.pi * d * f / (C_LUZ_KM_S * 1e3))


def retardo_ida_s(d_km):
    """Retardo de propagacion de IDA (no ida y vuelta), en segundos."""
    return np.asarray(d_km, dtype=np.float64) / C_LUZ_KM_S


def retardo_ida_ms(d_km):
    return retardo_ida_s(d_km) * 1e3


# =============================================================================
# Geometria de un pase LEO
# =============================================================================

def distancia_oblicua_km(elev_deg, h_km):
    """Distancia estacion-satelite a partir de la elevacion (Tierra esferica).

    De la ley del coseno en el triangulo centro-estacion-satelite:
        (R+h)^2 = R^2 + d^2 + 2 R d sen(el)
    de donde d = -R sen(el) + sqrt(R^2 sen^2(el) + h^2 + 2 R h).
    """
    s = np.sin(np.radians(np.asarray(elev_deg, dtype=np.float64)))
    h = float(h_km)
    return -R_TIERRA_KM * s + np.sqrt((R_TIERRA_KM * s) ** 2
                                      + h * h + 2 * R_TIERRA_KM * h)


def elevacion_de_distancia_deg(d_km, h_km):
    """La inversa de `distancia_oblicua_km`. Negativa = bajo el horizonte.

    Dos respuestas distintas que conviene no confundir:

    - Una distancia MAYOR que la del horizonte (a 600 km, 2829.35 km) da
      elevacion NEGATIVA: el satelite existe, pero esta al otro lado del
      limbo y la Tierra tapa la linea de vista. Un retardo que implique esa
      distancia no puede ser propagacion directa.
    - Una distancia geometricamente imposible para esa altura (menor que `h`,
      o mayor que 2R+h) da `nan`: no hay ningun punto de la esfera de radio
      R+h a esa distancia de la superficie.
    """
    d = np.asarray(d_km, dtype=np.float64)
    h = float(h_km)
    s = (h * h + 2 * R_TIERRA_KM * h - d * d) / (2 * d * R_TIERRA_KM)
    return np.where(np.abs(s) <= 1.0, np.degrees(np.arcsin(np.clip(s, -1, 1))),
                    np.nan)


def distancia_horizonte_km(h_km):
    """Distancia oblicua maxima (elevacion 0): sqrt((R+h)^2 - R^2)."""
    r = R_TIERRA_KM + float(h_km)
    return float(np.sqrt(r * r - R_TIERRA_KM * R_TIERRA_KM))


def _geometria(lat_gs, lon_gs, lonlat_sat, h_km):
    """(elevacion_deg, distancia_km, angulo_central_deg) por muestra.

    La elevacion la calcula `satelites.ventana_visibilidad` (no se
    reimplementa); la distancia sale del angulo central por la ley del coseno,
    que es la definicion, no una aproximacion desde la elevacion. Que las dos
    vias coincidan es un invariante de la sonda.
    """
    lonlat = np.atleast_2d(np.asarray(lonlat_sat, dtype=np.float64))
    _, elev = sat.ventana_visibilidad(lat_gs, lon_gs, lonlat, h_km)
    le, ce = np.radians(lat_gs), np.radians(lon_gs)
    ls, cs = np.radians(lonlat[:, 1]), np.radians(lonlat[:, 0])
    cos_c = np.clip(np.sin(le) * np.sin(ls)
                    + np.cos(le) * np.cos(ls) * np.cos(cs - ce), -1.0, 1.0)
    r = R_TIERRA_KM + float(h_km)
    d = np.sqrt(R_TIERRA_KM ** 2 + r * r - 2 * R_TIERRA_KM * r * cos_c)
    return elev, d, np.degrees(np.arccos(cos_c))


def pase_leo(h_km=ALTURA_LEO600_KM, inc_deg=53.0, lat_gs=19.43, lon_gs=-99.13,
             elev_min_deg=ELEVACION_MINIMA_DEG, raan_deg=None, fase0=0.0,
             muestras=2400):
    """El pase visto desde una estacion: elevacion, distancia, AOS/TCA/LOS.

    Con `raan_deg=None` barre el nodo del plano y se queda con el pase MAS
    ALTO — el que un espectador reconoceria como «el bueno». El knob es el
    RAAN y no la fase: desplazar la fase recorre la MISMA traza desde otro
    punto (`satelites.pase` lo midio y lo dejo escrito).

    Devuelve un dict con `t_s` (segundos desde AOS), `elev_deg`, `dist_km`,
    `azim_deg`, `lonlat`, `aos_s`, `tca_s`, `los_s`, `duracion_s`,
    `elev_max_deg`, `dist_min_km`, `dist_aos_km` y los parametros.
    """
    h = float(h_km)
    per = sat.periodo_orbital(h)["segundos"]
    t = np.linspace(0.0, per, int(muestras))

    if raan_deg is None:
        def _mejor(barrido, mejor=-90.0, mejor_raan=0.0):
            for r in barrido:
                ll = sat._subsat_uno(t, h, inc_deg, float(r), fase0)
                e, _, _ = _geometria(lat_gs, lon_gs, ll, h)
                if e.max() > mejor:
                    mejor, mejor_raan = float(e.max()), float(r)
            return mejor, mejor_raan
        m, r0 = _mejor(np.linspace(0.0, 360.0, 72, endpoint=False))
        # Refinar de verdad: con un solo paso fino de 0.25 deg el «pase
        # cenital» se quedaba en 89.13 grados, y una prueba de simetria sobre
        # ese pase no demuestra nada. Cuatro pasadas dejan el nodo a 0.005 deg.
        for anchura in (5.0, 0.5, 0.05, 0.005):
            m, r0 = _mejor(np.linspace(r0 - anchura, r0 + anchura, 21), m, r0)
        raan_deg = r0

    def _elev(tiempos):
        ll = sat._subsat_uno(tiempos, h, inc_deg, float(raan_deg), fase0)
        e, dd, gg = _geometria(lat_gs, lon_gs, ll, h)
        return ll, e, dd, gg

    def _bordes(e, i_pico):
        """AOS y LOS del pase que CONTIENE el pico, no del primero del dia."""
        vis = e >= elev_min_deg
        a = b = i_pico
        while a > 0 and vis[a - 1]:
            a -= 1
        while b < len(e) - 1 and vis[b + 1]:
            b += 1
        return a, b

    _, elev, _, _ = _elev(t)
    if elev.max() < elev_min_deg:
        raise ValueError(
            f"pase_leo: con RAAN {raan_deg:.1f} deg la elevacion maxima es "
            f"{elev.max():.2f} deg y el umbral es {elev_min_deg:.1f}: no hay "
            f"pase que dibujar")
    # Paso 1: recentrar la ventana en el TCA. Sin esto, un pase que cae sobre
    # el borde de [0, periodo] sale cortado y la duracion medida es menor que
    # la real, sin que nada avise.
    t = t + (t[int(np.argmax(elev))] - per / 2.0)
    _, elev, _, _ = _elev(t)
    i_tca = int(np.argmax(elev))
    i_aos, i_los = _bordes(elev, i_tca)
    if i_aos == 0 or i_los == len(elev) - 1:
        raise ValueError("pase_leo: el pase toca el borde de la ventana; la "
                         "duracion medida seria menor que la real")

    # La traza terrestre del dibujo es la de la ORBITA entera, no la del pase:
    # el mapa ensena por donde va el satelite y donde de ese recorrido lo ve la
    # estacion.
    lonlat_orbita = sat._subsat_uno(t, h, inc_deg, float(raan_deg), fase0)

    # Paso 2: volver a muestrear SOLO el pase. Sobre el periodo entero el paso
    # de tiempo es de segundos, y cerca del cenit la elevacion cae ~1 grado
    # cada 1.5 s: un pase cenital medido sobre la rejilla gruesa daba 89.13
    # grados en vez de 90, y la simetria alrededor del TCA fallaba por 1.7
    # grados. Lo que se mide es el PASE, asi que la rejilla es la del pase.
    margen = 0.03 * (t[i_los] - t[i_aos])
    t = np.linspace(t[i_aos] - margen, t[i_los] + margen, int(muestras))
    lonlat, elev, dist, gamma = _elev(t)
    azim = sat.azimut(lat_gs, lon_gs, lonlat)
    i_tca = int(np.argmax(elev))
    i_aos, i_los = _bordes(elev, i_tca)

    # Paso 3: el TCA no es una MUESTRA, es un instante. Cerca del cenit la
    # elevacion cae ~1 grado cada 1.5 s, asi que la muestra mas alta de una
    # rejilla de 0.23 s se queda a 0.08 grados del maximo: un pase cenital
    # rotulaba «89.92» donde la geometria dice 90. Se afina por seccion
    # ternaria sobre el intervalo de las dos muestras vecinas.
    a_t, b_t = float(t[max(i_tca - 1, 0)]), float(t[min(i_tca + 1, len(t) - 1)])
    for _ in range(80):
        m1 = a_t + (b_t - a_t) / 3.0
        m2 = b_t - (b_t - a_t) / 3.0
        _, e1, _, _ = _elev(np.array([m1]))
        _, e2, _, _ = _elev(np.array([m2]))
        if e1[0] < e2[0]:
            a_t = m1
        else:
            b_t = m2
    t_tca = 0.5 * (a_t + b_t)
    _, e_tca, d_tca, _ = _elev(np.array([t_tca]))

    corte = slice(i_aos, i_los + 1)
    t_rel = t[corte] - t[i_aos]
    return {
        "t_s": t_rel, "elev_deg": elev[corte], "dist_km": dist[corte],
        "azim_deg": azim[corte], "gamma_deg": gamma[corte],
        "lonlat": lonlat[corte], "lonlat_orbita": lonlat_orbita,
        "aos_s": 0.0, "tca_s": float(t_tca - t[i_aos]),
        "aos_abs_s": float(t[i_aos]), "tca_abs_s": float(t_tca),
        "los_abs_s": float(t[i_los]),
        "los_s": float(t[i_los] - t[i_aos]),
        "duracion_s": float(t[i_los] - t[i_aos]),
        "elev_max_deg": float(e_tca[0]),
        "dist_min_km": float(d_tca[0]),
        "dist_aos_km": float(dist[i_aos]),
        "h_km": h, "inc_deg": float(inc_deg), "raan_deg": float(raan_deg),
        "lat_gs": float(lat_gs), "lon_gs": float(lon_gs),
        "elev_min_deg": float(elev_min_deg),
        "periodo_s": float(per),
    }


def doppler(f_hz, t_s, dist_km):
    """Corrimiento Doppler (Hz) de una portadora `f_hz` durante el pase.

    df = -f * (dr/dt) / c: positivo mientras el satelite SE ACERCA (dr/dt < 0)
    y negativo cuando se aleja. Cambia de signo exactamente en el TCA, donde
    la distancia tiene su minimo y la velocidad radial se anula.
    """
    t = np.asarray(t_s, dtype=np.float64)
    d = np.asarray(dist_km, dtype=np.float64)
    if t.shape != d.shape or t.size < 3:
        raise ValueError("doppler: t_s y dist_km tienen que tener la misma "
                         "forma y al menos 3 muestras")
    vr = np.gradient(d, t)                     # km/s, positivo alejandose
    return -float(f_hz) * vr / C_LUZ_KM_S


def resumen_doppler(pase, f_hz):
    """Las cifras del Doppler de un pase, ya medidas."""
    df = doppler(f_hz, pase["t_s"], pase["dist_km"])
    i_tca = int(np.argmin(np.abs(pase["t_s"] - pase["tca_s"])))
    return {"df_hz": df, "df_max_hz": float(np.max(df)),
            "df_min_hz": float(np.min(df)),
            "df_en_tca_hz": float(df[i_tca]),
            "f_hz": float(f_hz),
            "ppm_max": float(np.max(np.abs(df)) / float(f_hz) * 1e6)}


def escenario_leo600(ticks_ms=TICKS_LEO600_MS, h_km=ALTURA_LEO600_KM):
    """Que geometria implica cada tick del escenario LEO-600 del banco.

    El CSV del banco (`scenarios.leo600.csv`) da un `delay_ms` por tick sin
    decir si es de ida o de ida y vuelta. Aqui se calculan las DOS lecturas y
    se dice cual es geometricamente posible a 600 km. El resultado importa: la
    lectura «de ida» es IMPOSIBLE ya en el primer tick (12.9 ms serian
    3866 km, mas que los 2829 km del horizonte), mientras que la lectura
    «ida y vuelta» da 9.98 deg de elevacion — justo la mascara de 10 deg del
    escenario. Los ticks del CSV son RTT.

    Devuelve una lista de dicts por tick.
    """
    d_horizonte = distancia_horizonte_km(h_km)
    salida = []
    for i, ms in enumerate(ticks_ms):
        d_ida = float(ms) * 1e-3 * C_LUZ_KM_S
        d_rtt = d_ida / 2.0
        salida.append({
            "tick": i, "delay_ms": float(ms),
            "d_si_ida_km": d_ida, "d_si_rtt_km": d_rtt,
            "posible_si_ida": bool(d_ida <= d_horizonte),
            "posible_si_rtt": bool(d_rtt <= d_horizonte),
            "elev_si_ida_deg": float(elevacion_de_distancia_deg(d_ida, h_km)),
            "elev_si_rtt_deg": float(elevacion_de_distancia_deg(d_rtt, h_km)),
        })
    return {"ticks": salida, "d_horizonte_km": d_horizonte,
            "h_km": float(h_km)}


# =============================================================================
# Handover: la cascada de cobertura
# =============================================================================

def fase0_k(k, paso_fase):
    """Fase inicial del satelite k de un tren separado `paso_fase` de periodo."""
    return -float(k) * float(paso_fase)


def handover(n_sats=4, h_km=ALTURA_LEO600_KM, inc_deg=53.0, lat_gs=19.43,
             lon_gs=-99.13, elev_min_deg=ELEVACION_MINIMA_DEG, solape=0.25,
             raan_deg=None, muestras=1200):
    """Cascada de cobertura de un tren de `n_sats` en el mismo plano.

    Los satelites van separados en fase lo justo para que cada uno entre
    cuando al anterior le queda `solape` de su pase: la separacion NO se elige
    a ojo, se CALCULA a partir de la duracion del pase de referencia. Con
    `solape=0` los pases se tocan y con `solape<0` queda hueco (el
    contraejemplo que la sonda usa para comprobar que el hueco se detecta).

    Devuelve un dict con `t_s`, `elev` (n_sats x T), `servidor` (indice del
    satelite con mas elevacion por encima del umbral, o -1), `relevos_s`,
    `cobertura` (fraccion de tiempo servido), `hueco_s` (el mayor hueco) y
    `duracion_servicio_s` por satelite.
    """
    ref = pase_leo(h_km, inc_deg, lat_gs, lon_gs, elev_min_deg,
                   raan_deg=raan_deg, muestras=muestras)
    per = ref["periodo_s"]
    n_sats = int(n_sats)
    paso_fase = (1.0 - float(solape)) * ref["duracion_s"] / per

    # El satelite k va RETRASADO k*paso_fase de periodo respecto del 0: con
    # fase0 = -k*paso_fase se cumple u_k(t) = u_0(t - k*paso_fase*periodo), y
    # la rotacion terrestre NO se compensa, asi que cada satelite del tren
    # pasa un poco mas al oeste que el anterior. Eso es lo que de verdad
    # ocurre, y por eso las elevaciones maximas del tren no son iguales.
    t0 = ref["aos_abs_s"] - 0.15 * ref["duracion_s"]
    t1 = (ref["aos_abs_s"] + (n_sats - 1) * paso_fase * per
          + 1.15 * ref["duracion_s"])
    t_absoluto = np.linspace(t0, t1, int(muestras) * 2)
    elev = np.zeros((int(n_sats), t_absoluto.size))
    for k in range(int(n_sats)):
        ll = sat._subsat_uno(t_absoluto, h_km, inc_deg, ref["raan_deg"],
                             fase0=fase0_k(k, paso_fase))
        e, _, _ = _geometria(lat_gs, lon_gs, ll, h_km)
        elev[k] = e
    t_abs = t_absoluto - t0

    visible = elev >= elev_min_deg
    mejor = np.argmax(elev, axis=0)
    servidor = np.where(visible.any(axis=0), mejor, -1)
    cambios = np.nonzero(np.diff(servidor) != 0)[0]
    relevos = [float(t_abs[i + 1]) for i in cambios
               if servidor[i] >= 0 and servidor[i + 1] >= 0]

    dt = float(np.mean(np.diff(t_abs)))
    servido = servidor >= 0
    # La cobertura se mide DENTRO de la ventana de servicio (del primer
    # instante servido al ultimo), no sobre el lienzo entero: el relleno que
    # se deja a los lados para que se vea entrar al primer satelite contaba
    # como hueco de handover y daba 0.9375 de cobertura con 77 s de «hueco»
    # que en realidad era el margen del dibujo. Un hueco de handover es el que
    # queda ENTRE dos pases, y eso es lo que se cuenta aqui.
    indices = np.nonzero(servido)[0]
    if indices.size == 0:
        raise ValueError("handover: ningun satelite del tren sirve nunca")
    i0, i1 = int(indices[0]), int(indices[-1])
    interior = servido[i0:i1 + 1]
    cobertura = float(np.mean(interior))
    huecos, actual = [], 0.0
    for s in interior:
        if s:
            if actual > 0:
                huecos.append(actual)
            actual = 0.0
        else:
            actual += dt
    duracion = [float(np.sum(servidor == k) * dt) for k in range(n_sats)]

    return {"t_s": t_abs, "elev": elev, "servidor": servidor,
            "relevos_s": relevos, "cobertura": cobertura,
            "ventana_servicio_s": (float(t_abs[i0]), float(t_abs[i1])),
            "hueco_s": float(max(huecos)) if huecos else 0.0,
            "duracion_servicio_s": duracion, "paso_fase": float(paso_fase),
            "solape": float(solape), "pase_ref": ref,
            "n_sats": int(n_sats), "elev_min_deg": float(elev_min_deg)}


# =============================================================================
# Consenso: PBFT
# =============================================================================

def f_max(n):
    """Fallos bizantinos tolerables con `n` replicas: el mayor f con n>=3f+1."""
    n = int(n)
    if n < 1:
        raise ValueError("f_max: n tiene que ser >= 1")
    return (n - 1) // 3


def quorum_pbft(n):
    """Quorum y trafico de PBFT con `n` replicas.

    n >= 3f+1. La division ENTERA es lo que hace que n=6 tolere lo mismo que
    n=4 (f=1): las dos replicas de mas no compran nada, y ese es el
    contraejemplo que hay que ensenar. n=7 es el siguiente escalon (f=2).

    El quorum es ceil((n+f+1)/2), NO 2f+1. Los dos coinciden justo cuando
    n = 3f+1 —el caso que sale en todos los diagramas— y por eso «2f+1» se
    repite como si fuera la definicion. Con replicas de sobra deja de valer:
    con n=6 y f=1, 2f+1 = 3 no es ni mayoria de 6, asi que dos quorums de tres
    pueden no compartir NINGUNA replica correcta y el protocolo pierde la
    interseccion en la que se apoya. La formula correcta da 4. Lo cazo la
    sonda: la version anterior de esta funcion devolvia 3.

    Mensajes por fase, en la version clasica de Castro-Liskov:
      pre-prepare  n-1        (el primario a los demas)
      prepare      (n-1)^2    (cada respaldo a todos los demas)
      commit       n(n-1)     (todos a todos)
    Total 2n(n-1), que es la cota cuadratica que la tesis contrapone al coste
    de un enlace NTN.
    """
    n = int(n)
    f = f_max(n)
    fases = {"pre-prepare": n - 1, "prepare": (n - 1) ** 2, "commit": n * (n - 1)}
    quorum = -((-(n + f + 1)) // 2)          # ceil((n+f+1)/2), en enteros
    return {"n": n, "f": f, "quorum": quorum, "quorum_2f1": 2 * f + 1,
            "minimo_n": 3 * f + 1,
            "holgura": n - (3 * f + 1), "tolera": f > 0,
            "mensajes": fases, "mensajes_total": sum(fases.values())}


# =============================================================================
# Margen adaptativo y gates
# =============================================================================

def margen_adaptativo(r_oraculo, r_best):
    """MA = (R_oraculo - R_best_const) / |R_best_const|.

    El valor absoluto del denominador NO es cosmetico: las recompensas de la
    tesis son NEGATIVAS (coste), y dividir por el valor con signo le daria la
    vuelta al MA justo en el caso que interesa. Con R_best = -80 y
    R_oraculo = -60, el oraculo es MEJOR y MA sale +0.25; sin el valor
    absoluto saldria -0.25 y el gate leeria «peor».
    """
    r_o = np.asarray(r_oraculo, dtype=np.float64)
    r_b = np.asarray(r_best, dtype=np.float64)
    if np.any(np.abs(r_b) < 1e-12):
        raise ValueError("margen_adaptativo: R_best_const es cero; el margen "
                         "relativo no esta definido")
    return (r_o - r_b) / np.abs(r_b)


def _medias_por_semilla(muestras_por_semilla):
    if isinstance(muestras_por_semilla, dict):
        claves = sorted(muestras_por_semilla)
        grupos = [np.asarray(muestras_por_semilla[k], dtype=np.float64)
                  for k in claves]
    else:
        claves = list(range(len(muestras_por_semilla)))
        grupos = [np.asarray(g, dtype=np.float64)
                  for g in muestras_por_semilla]
    if not grupos:
        raise ValueError("gate: no hay ninguna semilla")
    for k, g in zip(claves, grupos):
        if g.size == 0:
            raise ValueError(f"gate: la semilla {k} no tiene muestras")
    return claves, np.array([float(np.mean(g)) for g in grupos])


def gate(muestras_por_semilla, umbral, ci=0.95, semilla=42, n_boot=10000,
         nombre="gate"):
    """Veredicto de un gate con IC por bootstrap sobre las MEDIAS por semilla.

    La unidad de remuestreo es la SEMILLA, no la muestra: dos corridas de la
    misma semilla no son independientes, y remuestrear muestras sueltas
    estrecharia el intervalo hasta hacerlo pasar siempre.

    Un gate solo PASA si el intervalo entero esta por encima del umbral. Si el
    intervalo lo CRUZA, el veredicto es «indeciso» y no pasa: con tres
    semillas (42/43/44) eso es lo normal, y decirlo es el resultado.

    Devuelve {media, ic_lo, ic_hi, pasa, veredicto, n_semillas, umbral, ci}.
    """
    claves, medias = _medias_por_semilla(muestras_por_semilla)
    rng = np.random.default_rng(int(semilla))
    n = medias.size
    idx = rng.integers(0, n, size=(int(n_boot), n))
    remuestras = medias[idx].mean(axis=1)
    alfa = (1.0 - float(ci)) / 2.0
    ic_lo, ic_hi = np.quantile(remuestras, [alfa, 1.0 - alfa])
    media = float(np.mean(medias))
    if ic_lo > umbral:
        veredicto = "pasa"
    elif ic_hi < umbral:
        veredicto = "no pasa"
    else:
        veredicto = "indeciso"
    return {"nombre": nombre, "media": media, "ic_lo": float(ic_lo),
            "ic_hi": float(ic_hi), "pasa": bool(ic_lo > umbral),
            "veredicto": veredicto, "n_semillas": n, "semillas": claves,
            "medias_por_semilla": medias, "umbral": float(umbral),
            "ci": float(ci), "semilla_bootstrap": int(semilla)}


def banda_ic_por_x(series_por_semilla, ci=0.95, semilla=42, n_boot=2000):
    """IC95 % punto a punto de varias corridas: (media, lo, hi).

    `series_por_semilla` es (n_semillas, T). Mismo bootstrap sobre semillas
    que `gate`, aplicado a cada x: la banda que dibuja `figura.banda_ic`.
    """
    y = np.atleast_2d(np.asarray(series_por_semilla, dtype=np.float64))
    n, _ = y.shape
    rng = np.random.default_rng(int(semilla))
    idx = rng.integers(0, n, size=(int(n_boot), n))
    remuestras = y[idx].mean(axis=1)          # (n_boot, T)
    alfa = (1.0 - float(ci)) / 2.0
    lo, hi = np.quantile(remuestras, [alfa, 1.0 - alfa], axis=0)
    return y.mean(axis=0), lo, hi


# =============================================================================
# Dibujos (sobre figura.py: valen en tema paper y en tema marca)
# =============================================================================

def curva_elevacion(pase, f_doppler_hz=None, xlabel="tiempo desde AOS (s)",
                    ylabel="elevacion (grados)", puntos_marca=5.5,
                    puntos_titulo=None, ancho_=None, alto_=None):
    """Elevacion vs tiempo con AOS, TCA y LOS marcados y medidos.

    Devuelve un VGroup con `.ax` y `.cifras` (dict con lo que se rotula).
    """
    th = fg.tema()
    t, e = pase["t_s"], pase["elev_deg"]
    techo = float(min(90.0, 10.0 * np.ceil(pase["elev_max_deg"] / 10.0 + 0.3)))
    ax = fg.ejes_paper((0.0, float(t[-1])), (0.0, techo), xlabel, ylabel,
                       puntos_marca=puntos_marca,
                       puntos_titulo=puntos_titulo or puntos_marca + 1.0,
                       ancho_=ancho_, alto_=alto_)
    grupo = VGroup(ax, fg.curva(ax, t, e, fg.color(0), 1.8))

    ppu = fg.activa().puntos_por_unidad()
    # AOS y LOS caen en los BORDES del cuadro: centrar ahi su rotulo lo saca
    # del area de dibujo y lo encima con los numeros del eje Y (medido: "AOS"
    # sobre el "25" del eje). Cada uno se ancla hacia dentro.
    marcas = [("AOS", pase["aos_s"], fg.IZQ), ("TCA", pase["tca_s"], None),
              ("LOS", pase["los_s"], fg.DER)]
    for nombre, ts, lado in marcas:
        i = int(np.argmin(np.abs(t - ts)))
        x = ax.c2p(float(t[i]), 0.0)
        y = ax.c2p(float(t[i]), float(e[i]))
        grupo.add(DashedLine(x, y, stroke_width=0.9, color=th["apagado"],
                             dash_length=0.05))
        grupo.add(Dot(y, radius=1.8 / ppu, color=fg.color(1)))
        et = fg.texto(nombre, puntos_marca, th["apagado"])
        anclaje = fg.ABJ if lado is None else fg.ABJ + lado
        fg.poner(et, y + fg.ARR * (2.5 / ppu), anclaje=anclaje)
        grupo.add(et)

    cifras = {"elev_max_deg": pase["elev_max_deg"],
              "duracion_s": pase["duracion_s"],
              "dist_min_km": pase["dist_min_km"],
              "dist_aos_km": pase["dist_aos_km"],
              "retardo_min_ms": float(retardo_ida_ms(pase["dist_min_km"])),
              "retardo_aos_ms": float(retardo_ida_ms(pase["dist_aos_km"]))}
    if f_doppler_hz:
        cifras.update(resumen_doppler(pase, f_doppler_hz))
    grupo.ax = ax
    grupo.cifras = cifras
    return grupo


def curva_doppler(pase, f_hz, xlabel="tiempo desde AOS (s)",
                  ylabel="Doppler (kHz)", puntos_marca=5.5,
                  puntos_titulo=None, ancho_=None, alto_=None):
    """Doppler vs tiempo, con el cruce por cero en el TCA marcado."""
    th = fg.tema()
    r = resumen_doppler(pase, f_hz)
    t, df = pase["t_s"], r["df_hz"] / 1e3
    tope = float(np.ceil(max(abs(df.min()), abs(df.max())) / 5.0) * 5.0)
    ax = fg.ejes_paper((0.0, float(t[-1])), (-tope, tope), xlabel, ylabel,
                       puntos_marca=puntos_marca,
                       puntos_titulo=puntos_titulo or puntos_marca + 1.0,
                       ancho_=ancho_, alto_=alto_)
    grupo = VGroup(ax, fg.curva(ax, t, df, fg.color(2), 1.8))
    i = int(np.argmin(np.abs(t - pase["tca_s"])))
    p = ax.c2p(float(t[i]), float(df[i]))
    grupo.add(Dot(p, radius=1.8 / fg.activa().puntos_por_unidad(),
                     color=fg.color(1)))
    grupo.add(fg.pegar(fg.texto("TCA", puntos_marca, th["apagado"]), p,
                       fg.ARR, 2.0 / fg.activa().puntos_por_unidad()))
    grupo.ax = ax
    grupo.cifras = r
    return grupo


def cascada_handover(h, xlabel="tiempo (s)", ylabel="elevacion (grados)",
                     puntos_marca=5.5, puntos_titulo=None, ancho_=None,
                     alto_=None):
    """Las curvas de elevacion del tren, con el satelite que sirve resaltado.

    Cada satelite lleva su color; el tramo en el que ES el servidor va grueso
    y el resto fino, para que el relevo se vea sin leer una leyenda.
    """
    th = fg.tema()
    t, elev = h["t_s"], h["elev"]
    techo = float(min(90.0, 10.0 * np.ceil(elev.max() / 10.0 + 0.3)))
    ax = fg.ejes_paper((float(t[0]), float(t[-1])), (0.0, techo),
                       xlabel, ylabel, puntos_marca=puntos_marca,
                       puntos_titulo=puntos_titulo or puntos_marca + 1.0,
                       ancho_=ancho_, alto_=alto_)
    grupo = VGroup(ax)
    for k in range(h["n_sats"]):
        col = fg.color(k)
        grupo.add(fg.curva(ax, t, elev[k], col, 0.9, opacidad=0.45))
        sirve = h["servidor"] == k
        y = np.where(sirve, elev[k], np.nan)
        grupo.add(fg.curva(ax, t, y, col, 2.0))
    ppu = fg.activa().puntos_por_unidad()
    umbral = h["elev_min_deg"]
    grupo.add(DashedLine(ax.c2p(float(t[0]), umbral),
                            ax.c2p(float(t[-1]), umbral),
                            stroke_width=0.9, color=th["apagado"],
                            dash_length=0.05))
    for ts in h["relevos_s"]:
        grupo.add(DashedLine(ax.c2p(ts, 0.0), ax.c2p(ts, techo),
                                stroke_width=0.8, color=th["series"][1],
                                dash_length=0.04))
    grupo.ax = ax
    grupo.cifras = {"cobertura": h["cobertura"], "hueco_s": h["hueco_s"],
                    "relevos": len(h["relevos_s"]),
                    "paso_fase": h["paso_fase"]}
    return grupo


def diagrama_pbft(n, puntos=6.0, ancho_=None, emisores=(0, 1, 2)):
    """Las tres fases de PBFT con `n` replicas y el quorum marcado.

    Una fila por fase: el rotulo ARRIBA (a la derecha de los nodos se encimaba
    con la ultima replica, medido a 480p) y debajo las `n` replicas con el
    abanico de mensajes que sale de UNA de ellas. Se dibuja una sola emisora
    por fase a proposito: las 21 aristas de un «todos a todos» con n=7 son una
    mancha, y la cifra de al lado —la que sale de `quorum_pbft`— ya dice
    cuantos mensajes son en total.

    El primario va en el color de acento, el quorum en el de serie y las
    replicas que sobran, apagadas.
    """
    th = fg.tema()
    q = quorum_pbft(n)
    fig = fg.activa()
    ppu = fig.puntos_por_unidad()
    an = float(ancho_) if ancho_ else fig.zona(margen_pt=10.0)[0] * 0.66
    paso = an / max(n - 1, 1)
    r = min(2.4 / ppu, paso * 0.22)
    arco = min(paso * 0.9, 9.0 / ppu)

    def _color(i):
        if i == 0:
            return fg.color(1)
        return fg.color(0) if i < q["quorum"] else th["apagado"]

    filas = VGroup()
    for j, (fase, cuantos) in enumerate(q["mensajes"].items()):
        emisor = int(emisores[j % len(emisores)]) % n
        nodos = VGroup(*[Dot([i * paso, 0.0, 0.0], radius=r, color=_color(i))
                         for i in range(n)])
        aristas = VGroup()
        for i in range(n):
            if i == emisor:
                continue
            a = np.array([emisor * paso, r, 0.0])
            b = np.array([i * paso, r, 0.0])
            medio = (a + b) / 2.0 + np.array([0.0, arco, 0.0])
            v = VMobject()
            v.set_points_as_corners([a, medio, b]).make_smooth()
            v.set_stroke(color=_color(emisor), width=0.8, opacity=0.55)
            v.set_fill(opacity=0.0)
            aristas.add(v)
        dibujo = VGroup(aristas, nodos)
        et = fg.texto(f"{fase}   {cuantos} mensajes", puntos, th["tinta"])
        fg.pegar(et, dibujo, fg.ARR, 2.5 / ppu)
        fg.poner(et, [0.0, fg.centro(et)[1], 0.0], anclaje=fg.IZQ)
        filas.add(VGroup(dibujo, et))

    for j in range(1, len(filas)):
        fg.pegar(filas[j], filas[j - 1], fg.ABJ, 7.0 / ppu)
        fg.poner(filas[j], [0.0, fg.centro(filas[j])[1], 0.0], anclaje=fg.IZQ)

    # La llave del quorum, bajo la ultima fila.
    ultima = filas[-1][0][1]
    y = fg.caja(ultima)[0][1] - 4.0 / ppu
    llave = Line([0.0, y, 0.0], [(q["quorum"] - 1) * paso, y, 0.0],
                 stroke_width=1.4, color=fg.color(0))
    et_q = fg.texto(f"quorum = {q['quorum']} de {n}   (f = {q['f']})",
                    puntos, fg.color(0))
    fg.pegar(et_q, llave, fg.ABJ, 2.5 / ppu)
    fg.poner(et_q, [fg.centro(llave)[0], fg.centro(et_q)[1], 0.0])

    grupo = VGroup(filas, llave, et_q)
    pie = fg.texto(f"n = {q['n']}   n >= 3f+1   "
                   f"{q['mensajes_total']} mensajes por ronda",
                   puntos, th["apagado"])
    fg.pegar(pie, grupo, fg.ABJ, 5.0 / ppu)
    fg.poner(pie, [fg.centro(grupo)[0], fg.centro(pie)[1], 0.0])
    grupo.add(pie)
    grupo.cifras = q
    return grupo


def curva_ma(x, ma, umbral=UMBRAL_MA, ic=None, xlabel="configuracion",
             ylabel="margen adaptativo MA", puntos_marca=5.5,
             etiquetas=None, puntos_titulo=None, ancho_=None, alto_=None):
    """Curva del margen adaptativo con su umbral y, si se da, su banda IC.

    `ic` es (lo, hi) del mismo largo que `ma`. La zona por encima del umbral
    se marca con una raya, no con un relleno: un relleno del semiplano compite
    con la banda del intervalo y las dos cosas se leen como una sola.
    """
    th = fg.tema()
    x = np.asarray(x, dtype=np.float64)
    ma = np.asarray(ma, dtype=np.float64)
    lo_dat = float(np.min(ic[0]) if ic is not None else np.min(ma))
    hi_dat = float(np.max(ic[1]) if ic is not None else np.max(ma))
    margen = 0.12 * max(hi_dat - lo_dat, 1e-6)
    y0 = float(min(lo_dat - margen, 0.0))
    y1 = float(max(hi_dat + margen, umbral * 1.25))
    ax = fg.ejes_paper((float(x[0]), float(x[-1])), (y0, y1), xlabel, ylabel,
                       puntos_marca=puntos_marca, decimales=(0, 2),
                       puntos_titulo=puntos_titulo or puntos_marca + 1.5,
                       ancho_=ancho_, alto_=alto_)
    grupo = VGroup(ax)
    if ic is not None:
        grupo.add(fg.banda_ic(ax, x, ic[0], ic[1], fg.color(0)))
    grupo.add(fg.curva(ax, x, ma, fg.color(0), 1.8))
    grupo.add(DashedLine(ax.c2p(float(x[0]), umbral),
                            ax.c2p(float(x[-1]), umbral),
                            stroke_width=1.1, color=fg.color(1),
                            dash_length=0.06))
    ppu = fg.activa().puntos_por_unidad()
    # El rotulo del umbral va DENTRO del cuadro, pegado por su borde derecho:
    # colgado del extremo de la raya se salia del lienzo por la derecha y la
    # figura exportada lo enseñaba cortado.
    et = fg.texto(f"umbral {umbral:.2f}", puntos_marca, fg.color(1))
    fg.poner(et, ax.c2p(float(x[-1]), umbral) + fg.ARR * (1.5 / ppu),
             anclaje=fg.DER + fg.ABJ)
    grupo.add(et)
    if etiquetas is not None:
        for xi, txt in zip(x, etiquetas):
            e = fg.texto(str(txt), puntos_marca, th["apagado"])
            grupo.add(fg.pegar(e, ax.c2p(float(xi), y0), fg.ABJ, 1.2 / ppu))
    grupo.ax = ax
    grupo.cifras = {"ma": ma, "umbral": float(umbral),
                    "sobre_umbral": int(np.sum(ma > umbral))}
    return grupo


def traza_tierra(pase, res=(960, 480), alto_escena=None, color_traza=None):
    """Traza terrestre del pase sobre el mapa de `satelites.py`, con la GS.

    No se reimplementa el mapa: es `satelites.imagen_mapa` + `traza_terrestre`
    + `puntos_en_mapa`, que ya estaban resueltos y medidos.
    """
    fig = fg.activa()
    alto_escena = float(alto_escena or fig.frame_height * 0.72)
    mapa = sat.imagen_mapa(res=res, alto_escena=alto_escena)
    traza = sat.traza_terrestre(pase["lonlat_orbita"], mapa,
                                color=color_traza or fg.color(0),
                                ancho=1.6, opacidad=0.85)
    visible = sat.traza_terrestre(pase["lonlat"], mapa,
                                  color=fg.color(1), ancho=2.4, opacidad=1.0)
    # `puntos_en_mapa` devuelve COORDENADAS (N,3), no un mobject: la estacion
    # hay que dibujarla. Marcarla con un punto y un anillo la separa de la
    # traza, que en el mapa pasa justo por encima.
    xyz = sat.puntos_en_mapa(mapa, [(pase["lon_gs"], pase["lat_gs"])])[0]
    r = 3.0 / fig.puntos_por_unidad()
    estacion = VGroup(Circle(radius=r * 1.9, stroke_width=1.2,
                             color=fg.tema()["tinta"]).move_to(xyz),
                      Dot(xyz, radius=r * 0.7, color=fg.tema()["tinta"]))
    return Group(mapa, traza, visible, estacion)
