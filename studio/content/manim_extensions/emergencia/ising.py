# =====================================================================
# emergencia/ising.py — clip 08 "el iman que decide".
#
# QUE SIMULA
#   El modelo de Ising 2D: una malla de espines que solo pueden valer +1
#   o -1 y que solo saben del vecino de al lado. Se enfria la malla desde
#   T=3.5 J/k hasta T=1.2 J/k pasando DESPACIO por la temperatura critica
#   Tc=2.269 (el 40 % de los frames se gasta en la franja 2.6-2.0). Arriba
#   de Tc es ruido; en Tc aparecen dominios de TODOS los tamaños; abajo,
#   uno de los dos signos se come la malla entera.
#
# REGLAS (las tres lineas del HUD)
#   1. cada celda mira a sus 4 vecinas: E = -J * s * (suma de vecinas)
#   2. voltea si baja la energia; si la sube, voltea con prob. exp(-dE/T)
#   3. T baja con el tiempo: 3.5 -> 1.2 (Tc = 2.269)
#
# COMO
#   Metropolis en TABLERO DE AJEDREZ vectorizado: en un barrido se
#   proponen a la vez todas las celdas "negras" (i+j par) y luego todas
#   las "blancas"; como ninguna celda negra es vecina de otra negra, el
#   paralelo es exacto (no hay dos vecinas decidiendo a la vez). La
#   probabilidad de aceptar sale de una tabla de 9 valores indexada por
#   s*vecinos+4 (en el borde abierto hay celdas con 3 y 2 vecinas), no de
#   un exp() por celda.
#
#   AVISO (2026-08-28): la primera version usaba 5 valores con >>1 y era
#   incorrecta en el borde abierto (el perimetro quedaba caliente y abajo
#   de Tc nucleaba dominios que se comian el interior: los saltos de |M|
#   0.93 -> 0.13 -> 0.95 -> 0.05 del primer temple eran ESO, no fisica).
#   Las conclusiones de abajo sobre el "sorteo" y sobre la frontera
#   periodica se midieron con esa dinamica y ya no valen: con la tabla
#   correcta, el toro (periodica=True, barridos_max=110) da |M| final
#   0.9973 frente a 0.997026 de Onsager a T=1.2. El clip 08 usa el toro.
#
#   Frontera ABIERTA (un iman finito, no un toro). Es una decision, no un
#   descuido: con frontera periodica el temple congela una franja que
#   cruza la caja de lado a lado en ~la mitad de las semillas y |M| final
#   se queda en 0.0-0.6; con frontera abierta las paredes de dominio se
#   escapan por el borde y el iman decide de verdad.
#
#   Convenio de signo: al terminar se elige el signo global (s -> -s) para
#   que el ganador quede violeta. Con campo externo nulo el hamiltoniano
#   es exactamente simetrico bajo esa inversion, asi que la trayectoria
#   pintada es tan valida como la calculada; solo se fija el color.
#
# AVISO: EL FINAL DEPENDE DE LA SEMILLA (no es un bug, es el modelo)
#   Con campo nulo las dos fases son EXACTAMENTE degeneradas: una pared de
#   dominio que cruza la caja no tiene ninguna fuerza que la empuje, solo
#   difunde, y tarda ~L^2 barridos (L = 240 celdas del lado largo, o sea
#   ~58 000 barridos) en salirse por un extremo. El temple entero cuesta
#   57 000. Resultado: a veces el iman decide y a veces se queda congelado
#   en dos dominios. |M| final medida con `medir(semilla=s)` y todo lo
#   demas por defecto:
#       s=1 -> 0.97   s=2 -> 0.98   s=3 -> 0.73   s=4 -> 0.04
#       s=5 -> 0.70   s=6 -> 0.27   s=7 -> 0.73
#   La semilla 1 (la de por defecto) es de las que deciden: |M| = 0.97.
#   Se probo lo obvio y NO arregla el sorteo: mas barridos (44 000 con
#   otro reparto dio 0.13 con s=1), malla mas gruesa (celda=3, 117 000
#   barridos, s=1 -> 0.03) ni frontera periodica (que es peor: la franja
#   que da la vuelta al toro no se puede escapar por ningun borde).
#   Arreglarlo de verdad pide o 3-5x de CPU, o un campo externo minusculo
#   -- y entonces quien decide es el campo, no el iman, que es justo lo
#   que el clip 08 NO quiere decir. Se deja la fisica como es y se fija
#   la semilla; `medir()` esta para que la sonda lo vigile.
#
# IMAGEN
#   Dos colores planos, pixel duro (usar Pelicula con nearest=True):
#   espin +1 en violeta C_ORDEN (lo ordenado), espin -1 en naranja muy
#   apagado (C_FONDO mezclado con C_ENERGIA al 32 %). Celda de 2x2 px por
#   defecto: la malla es 240x135 celdas pintada a 480x270 px, que a
#   1080x1920 son bloques de 8x8 y se leen en un telefono.
#
# COSTE MEDIDO (contenedor codeaerospace_contenido-manim, 2026-08-28)
#   simular(pasos=800): 49 s de CPU, 56 852 barridos de 32 400 celdas
#   (1.8e9 propuestas de volteo), pila de 311 MB (800 frames de
#   480x270x3). medir(): 45 s (misma fisica, sin pintar ni guardar la
#   historia). El presupuesto son 90 s: cabe con holgura.
#
# CIFRAS (medidas sobre lo simulado, salvo la de literatura)
#   Tc_literatura ....... 2.269 (Onsager; NO se mide aqui)
#   M_abs_en_T3 ......... |M| medida al pasar por T=3.0
#   M_abs_en_Tc ......... |M| medida al pasar por Tc=2.269
#   M_abs_final ......... |M| a T=1.2
#   T_cruce_M_0_5 ....... T a la que |M| cruza 0.5 y ya no vuelve a bajar
#   energia_por_espin_final
# =====================================================================
import time

import numpy as np

from . import C_ORDEN, LUTS, RES_BASE, hex_a_rgb, validar_pila

TC_LITERATURA = 2.269          # Onsager, 2/ln(1+sqrt(2)), en J/k
T_ALTA = 3.5
T_BAJA = 1.2

# tramos del enfriamiento: (fraccion de frames, T al final del tramo).
# el tramo 0.30-0.70 (el 40 % de la pieza) recorre 2.6 -> 2.0, la franja
# critica donde se ven los dominios de todos los tamaños.
_TRAMOS_U = (0.00, 0.30, 0.70, 1.00)
_TRAMOS_T = (T_ALTA, 2.60, 2.00, T_BAJA)

# color del espin -1: naranja muy apagado sobre el fondo (32 % de la rampa)
C_ABAJO = LUTS["energia"][int(0.24 * 255)]


def temperatura(u):
    """T(u) del enfriamiento, con u = fraccion de la pieza (0-1)."""
    return np.interp(u, _TRAMOS_U, _TRAMOS_T)


def _tabla_aceptacion(T, J=1.0):
    """9 probabilidades de Metropolis, indexadas por k = s*vecinos + 4.

    Con cuatro vecinas s*vecinos es par (-4,-2,0,2,4) y bastaban 5
    entradas indexadas por (s*vecinos+4)>>1. Pero con frontera ABIERTA las
    celdas del borde tienen 3 vecinas (y las esquinas 2): s*vecinos es
    impar, el >>1 redondeaba hacia abajo y el perimetro aceptaba volteos
    que suben la energia con probabilidad 1 (medido por el agente del clip
    08: en una malla 64x64 a T=1.25 el tablero daba |M| 0.86-0.94 con
    saltos, y el Metropolis secuencial 0.992; con esta tabla, 0.997). La
    tabla de 9 entradas cubre todos los casos: dE = 2*J*(k-4).
    """
    dE = 2.0 * J * (np.arange(9) - 4.0)
    return np.minimum(1.0, np.exp(-dE / T)).astype(np.float32)


def _vecinos(s, periodica):
    if periodica:
        return (np.roll(s, 1, 0) + np.roll(s, -1, 0)
                + np.roll(s, 1, 1) + np.roll(s, -1, 1))
    nb = np.zeros_like(s)
    nb[1:, :] += s[:-1, :]
    nb[:-1, :] += s[1:, :]
    nb[:, 1:] += s[:, :-1]
    nb[:, :-1] += s[:, 1:]
    return nb


def _energia_por_espin(s, periodica, J=1.0):
    f = s.astype(np.float32)
    if periodica:
        enl = f * (np.roll(f, -1, 0) + np.roll(f, -1, 1))
        return float(-J * enl.mean())
    enl = float((f[:-1, :] * f[1:, :]).sum() + (f[:, :-1] * f[:, 1:]).sum())
    return -J * enl / f.size


def _correr(semilla=1, pasos=800, res=RES_BASE, celda=2, barridos=8,
            barridos_max=260, exponente=3.0, periodica=False, J=1.0,
            pintar=True):
    """Nucleo compartido por `simular` y `medir`. Devuelve (historia|None,
    cifras, extra)."""
    W, H = int(res[0]), int(res[1])
    if abs(H / W - 16 / 9) > 1e-6:
        raise ValueError(f"res tiene que ser 9:16; llego {W}x{H}")
    celda = int(celda)
    if W % celda or H % celda:
        raise ValueError("la celda tiene que dividir a res")
    h, w = H // celda, W // celda

    rng = np.random.default_rng(semilla)
    s = np.where(rng.random((h, w)) < 0.5, np.int8(1), np.int8(-1))
    i, j = np.mgrid[0:h, 0:w]
    negras = ((i + j) % 2 == 0)
    sublattices = (negras, ~negras)

    historia = np.empty((pasos, h, w), dtype=np.int8) if pintar else None
    Ts = np.empty(pasos, dtype=np.float32)
    Ms = np.empty(pasos, dtype=np.float32)
    Es = np.empty(pasos, dtype=np.float32)
    total_barridos = 0

    t0 = time.perf_counter()
    for f in range(pasos):
        u = f / max(pasos - 1, 1)
        T = float(temperatura(u))
        # recocido: los barridos por frame suben de `barridos` a
        # `barridos_max` como u**exponente. Arriba de Tc la malla se
        # decorrelaciona en un barrido y sobran; abajo de Tc la dinamica
        # es difusiva (una pared de dominio tarda ~L^2 barridos en cruzar
        # la caja) y hacen falta cientos por frame para que el temple
        # siga siendo casi cuasiestatico y el iman llegue a decidir.
        b = int(round(barridos + (barridos_max - barridos) * u ** exponente))
        total_barridos += b
        tabla = _tabla_aceptacion(T, J)
        for _ in range(b):
            for m in sublattices:
                nb = _vecinos(s, periodica)
                k = s * nb + 4
                acepta = rng.random(s.shape, dtype=np.float32) < tabla[k]
                np.negative(s, out=s, where=(m & acepta))
        Ts[f] = T
        Ms[f] = abs(float(s.astype(np.float32).mean()))
        Es[f] = _energia_por_espin(s, periodica, J)
        if pintar:
            historia[f] = s
    coste = time.perf_counter() - t0

    # --- cifras medidas ----------------------------------------------
    i_T3 = int(np.argmin(np.abs(Ts - 3.0)))
    i_Tc = int(np.argmin(np.abs(Ts - TC_LITERATURA)))
    # cruce de 0.5: primer cruce de |M| SUAVIZADA con media movil de 15
    # frames (medio segundo). Sin suavizar, |M| tiembla y el cruce se lo
    # lleva un pico de ruido; con campo nulo las dos fases son degeneradas
    # y abajo de Tc una pared de dominio puede pasear y hacer que |M| baje
    # otra vez de 0.5 sin que eso sea "descristalizar".
    ventana = 15                      # medio segundo a 30 fps
    nucleo = np.ones(ventana, dtype=np.float64) / ventana
    Msuave = np.convolve(np.pad(Ms, ventana // 2, mode="edge"), nucleo,
                         mode="valid")[:pasos]
    arriba = np.where(Msuave >= 0.5)[0]
    f_cruce, T_cruce = -1, float("nan")
    if len(arriba):
        f_cruce = int(arriba[0])
        if f_cruce > 0:
            m0, m1 = float(Msuave[f_cruce - 1]), float(Msuave[f_cruce])
            frac = (0.5 - m0) / max(m1 - m0, 1e-9)
            T_cruce = float(Ts[f_cruce - 1]
                            + frac * (Ts[f_cruce] - Ts[f_cruce - 1]))
        else:
            T_cruce = float(Ts[0])

    cifras = {
        "Tc_literatura": TC_LITERATURA,
        "M_abs_en_T3": round(float(Ms[i_T3]), 4),
        "M_abs_en_Tc": round(float(Ms[i_Tc]), 4),
        "M_abs_final": round(float(Ms[-1]), 4),
        "T_cruce_M_0_5": round(T_cruce, 4),
        "energia_por_espin_final": round(float(Es[-1]), 4),
        "energia_por_espin_en_Tc": round(float(Es[i_Tc]), 4),
        "celdas": int(h * w),
        "barridos_totales": int(total_barridos),
        "segundos_cpu": round(coste, 1),
    }
    extra = {
        "temperatura": Ts,
        "M_abs_suave": Msuave.astype(np.float32),
        "M_abs": Ms,
        "energia_por_espin": Es,
        "frame_en_T3": i_T3,
        "frame_en_Tc": i_Tc,
        "frame_cruce_M_0_5": f_cruce,
        "barridos_por_frame": (barridos, barridos_max),
        "malla": (h, w),
        "celda_px": celda,
        "Tc_literatura": TC_LITERATURA,
        "colores": {"mas_uno": C_ORDEN, "menos_uno": _hex(C_ABAJO)},
    }
    return historia, cifras, extra


def _hex(rgb):
    r, g, b = (int(round(float(v))) for v in rgb)
    return f"#{r:02x}{g:02x}{b:02x}"


def _pintar(historia, celda):
    """(T,h,w) int8 -> (T, h*celda, w*celda, 3) uint8, dos colores planos."""
    paleta = np.stack([np.asarray(C_ABAJO, dtype=np.float32),
                       hex_a_rgb(C_ORDEN)]).astype(np.uint8)   # [-1, +1]
    idx = (historia > 0).astype(np.uint8)
    frames = paleta[idx]
    if celda > 1:
        frames = np.repeat(np.repeat(frames, celda, axis=1), celda, axis=2)
    return np.ascontiguousarray(frames)


def simular(semilla=1, pasos=800, res=RES_BASE, celda=2, barridos=8,
            barridos_max=260, exponente=3.0, periodica=False, J=1.0):
    """Enfria una malla de Ising 2D y devuelve la pelicula del temple.

    pasos ......... frames (800 = 26.7 s a 30 fps; la pieza dura 30-40 s)
    res ........... (W, H) en pixeles, 9:16; 270x480 por defecto
    celda ......... px por celda (2 -> malla de 240x135; 1 -> 480x270)
    barridos ...... barridos de Metropolis en el primer frame
    barridos_max .. barridos en el ultimo frame (recocido: suben como
                    u**exponente, con u = fraccion de la pieza)
    exponente ..... curvatura de esa subida
    periodica ..... True para frontera de toro (es lo que usa el clip 08;
                    ver el AVISO de la cabecera)

    Devuelve dict(frames=uint8 (T,H,W,3), cifras={...}, extra={...}).
    `extra` trae las series por frame `temperatura`, `M_abs` y
    `energia_por_espin` (todas (T,)), los indices de frame `frame_en_T3`,
    `frame_en_Tc` y `frame_cruce_M_0_5` (para camara lenta), la forma de
    la `malla`, `celda_px` y los `colores` usados.
    """
    historia, cifras, extra = _correr(semilla, pasos, res, celda, barridos,
                                      barridos_max, exponente, periodica, J,
                                      pintar=True)
    # convenio Z2: el ganador se pinta violeta (ver cabecera)
    if float(historia[-1].astype(np.float32).mean()) < 0:
        historia = -historia
    frames = _pintar(historia, celda)
    return {"frames": validar_pila(frames), "cifras": cifras, "extra": extra}


def medir(semilla=1, pasos=800, res=RES_BASE, celda=2, barridos=8,
          barridos_max=260, exponente=3.0, periodica=False, J=1.0):
    """Solo las cifras (misma fisica, sin pintar ni guardar la historia)."""
    _, cifras, _ = _correr(semilla, pasos, res, celda, barridos,
                           barridos_max, exponente, periodica, J,
                           pintar=False)
    return cifras
