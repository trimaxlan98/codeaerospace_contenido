# =====================================================================
# chladni — clip 07 "la placa que canta".
#
# Que simula: 40 000 granos de arena sobre una placa cuadrada que vibra
# en un modo estacionario. Los granos hacen descenso de gradiente sobre
# |u|^2 (se van de donde la placa se mueve mucho) mas un ruido
# proporcional a la amplitud local |u| (donde la placa esta quieta, el
# grano tambien): el resultado es que la arena dibuja sola las LINEAS
# NODALES. La frecuencia "sube" y pasa por cuatro modos; en cada cambio
# la arena salta y vuelve a organizarse.
#
# Aproximacion del modo (anotada a proposito): se usa la forma clasica de
# Chladni-Ritz para una placa cuadrada de bordes LIBRES,
#
#     u(x,y) = cos(n*pi*x) * cos(m*pi*y) - cos(m*pi*x) * cos(n*pi*y)
#
# con x, y en [0,1]. NO es una solucion exacta de la ecuacion de placas
# de Kirchhoff con bordes libres (esa no tiene forma cerrada): es la
# combinacion de productos de cosenos que Chladni y Ritz usaron y que
# reproduce las figuras observadas. La diagonal x = y es siempre nodal,
# como en la placa real cuadrada. La frecuencia relativa se toma como
# f ~ (m^2 + n^2), normalizada al primer modo.
#
# Reglas (las tres lineas del HUD):
#   1. el grano huye de donde la placa vibra;
#   2. donde la placa esta quieta, el grano se queda;
#   3. sube la frecuencia y el dibujo entero cambia.
#
# Coste medido en el contenedor (2026-08-28), simular() por defecto:
#   T = 800 frames, res 270x480, 40 000 granos, 4 modos de 200 frames
#   -> 23-27 s de CPU segun carga, pila de 311.0 MB.
#   medir() (sin pintar): 9-12 s.
#
# Cifras (medidas sobre lo simulado; promedio de los ultimos 40 frames de
# cada modo, porque la fraccion respira con el latido del plato):
#   fraccion_nodal_modo_1 / frac_nodos_modo_1_pct  (1,2)  86.1 %  f_rel  1.0
#   fraccion_nodal_modo_2 / frac_nodos_modo_2_pct  (2,3)  83.2 %  f_rel  2.6
#   fraccion_nodal_modo_3 / frac_nodos_modo_3_pct  (3,5)  82.4 %  f_rel  6.8
#   fraccion_nodal_modo_4 / frac_nodos_modo_4_pct  (5,7)  81.3 %  f_rel 14.8
#   umbral_nodo_px = 3.0  (distancia al nodo estimada por |u| / |grad u|)
# La cifra BAJA al subir la frecuencia, y esa es la historia: cuanto mas
# rapido vibra la placa, mas le cuesta a la arena quedarse en la linea.
#
# Las longitudes por defecto estan pensadas para (270, 480). A (360, 640)
# funciona igual (la placa se escala con el ancho) y la pila pesa 553 MB.
#
# Notas de imagen: la arena va en ambar C_REGLA con `salpicar` (aditivo:
# donde se juntan muchos granos, quema), sobre el campo |u| pintado muy
# tenue en violeta (LUT "orden": es el patron que emerge) y latiendo al
# ritmo del modo — el periodo del latido baja como 1/f_rel, asi que se VE
# que la frecuencia sube. La placa lleva un marco de 1 px en
# C_MOBILIARIO. Cian: ninguno; el numero medido lo pone el clip.
# =====================================================================
import numpy as np

from . import (C_FONDO, C_MOBILIARIO, LUTS, RES_BASE, colorear, estela,
               hex_a_rgb, salpicar, validar_pila)

MODOS = ((1, 2), (2, 3), (3, 5), (5, 7))
PERIODO_BASE = 150.0        # frames del latido del primer modo


def _campo(m, n, x, y):
    """u y sus derivadas en (x, y) normalizados a [0,1]. Vectorizado:
    x, y pueden ser escalares, vectores de particulas o mallas."""
    pn, pm = np.pi * n, np.pi * m
    cnx, snx = np.cos(pn * x), np.sin(pn * x)
    cmx, smx = np.cos(pm * x), np.sin(pm * x)
    cny, sny = np.cos(pn * y), np.sin(pn * y)
    cmy, smy = np.cos(pm * y), np.sin(pm * y)
    u = cnx * cmy - cmx * cny
    ux = -pn * snx * cmy + pm * smx * cny
    uy = -pm * cnx * smy + pn * cmx * sny
    return u, ux, uy


def _distancia_nodal(u, ux, uy):
    """Distancia de cada grano a la linea nodal mas cercana, estimada a
    primer orden como |u| / |grad u| (exacta en el limite en que el grano
    ya esta cerca de la linea). En unidades de placa: multiplicar por
    `lado` para tenerla en pixeles."""
    return np.abs(u) / (np.hypot(ux, uy) + 1e-9)


def _correr(pasos, res, semilla, granos, modos, umbral_px, k_conv,
            paso_max, ruido, piso, agitacion, tau_agit, margen_px,
            densidad_ref, guardar):
    W, H = int(res[0]), int(res[1])
    if abs(H / W - 16.0 / 9.0) > 1e-6:
        raise ValueError(f"la resolucion {res} no es 9:16")
    T = int(pasos)
    modos = [tuple(int(v) for v in par) for par in modos]
    n_modos = len(modos)
    largo = T // n_modos                       # frames por modo
    cambios = [i * largo for i in range(n_modos)]

    lado = W - 2 * int(margen_px)
    x0 = (W - lado) // 2
    y0 = (H - lado) // 2
    umbral = float(umbral_px) / lado           # umbral en normalizadas

    f_rel = [(m * m + n * n) / float(modos[0][0] ** 2 + modos[0][1] ** 2)
             for (m, n) in modos]
    periodo = [max(10.0, PERIODO_BASE / f) for f in f_rel]

    rng = np.random.default_rng(semilla)
    x = rng.random(granos).astype(np.float64)
    y = rng.random(granos).astype(np.float64)

    frac_frame = np.empty(T, dtype=np.float64)

    if guardar:
        frames = np.empty((T, H, W, 3), dtype=np.uint8)
        fondo = hex_a_rgb(C_FONDO)
        gris = hex_a_rgb(C_MOBILIARIO)
        rej = (np.arange(lado) + 0.5) / lado
        gx, gy = np.meshgrid(rej, rej)         # gy recorre las filas
        campos = np.stack([np.abs(_campo(m, n, gx, gy)[0])
                           for (m, n) in modos]).astype(np.float32)
        arena = np.zeros((H, W, 3), dtype=np.float32)
        if densidad_ref is None:
            # densidad tipica de una linea nodal ya cuajada, escalada al
            # numero de granos y al tamaño de la placa
            densidad_ref = 25.0 * (granos / 40000.0) * (258.0 / lado)
    else:
        frames = None
        campos = None

    i_modo = -1
    k_cambio = 0
    m, n = modos[0]
    for k in range(T):
        if i_modo + 1 < n_modos and k >= cambios[i_modo + 1]:
            i_modo += 1
            m, n = modos[i_modo]
            k_cambio = k
        # el plato canta: la amplitud instantanea late al ritmo del modo
        fase = 2.0 * np.pi * (k - k_cambio) / periodo[i_modo]
        env = 0.30 + 0.70 * abs(np.cos(fase))
        # tras el salto de frecuencia la arena brinca y vuelve a migrar
        agit = 1.0 + agitacion * np.exp(-(k - k_cambio) / tau_agit)

        u, ux, uy = _campo(m, n, x, y)
        g = np.hypot(ux, uy) + 1e-9
        dist = _distancia_nodal(u, ux, uy)
        frac_frame[k] = float(np.mean(dist < umbral))

        if guardar:
            capa = colorear(campos[i_modo] * env, LUTS["orden"],
                            vmin=0.0, vmax=2.0).astype(np.float32)
            img = np.empty((H, W, 3), dtype=np.float32)
            img[:] = fondo
            img[y0:y0 + lado, x0:x0 + lado] += 0.30 * (capa - fondo)
            img[y0 - 1, x0 - 1:x0 + lado + 1] = gris
            img[y0 + lado, x0 - 1:x0 + lado + 1] = gris
            img[y0 - 1:y0 + lado + 1, x0 - 1] = gris
            img[y0 - 1:y0 + lado + 1, x0 + lado] = gris
            estela(arena, 0.35)
            xy = np.empty((granos, 2), dtype=np.float64)
            xy[:, 0] = x0 + x * lado
            xy[:, 1] = y0 + y * lado
            # se acumula DENSIDAD en blanco y se colorea despues: si se
            # salpicara ya en ambar, al amontonarse los granos cada canal
            # saturaria por su cuenta y la linea saldria blanca, no ambar.
            # radio 0.9 = un solo pixel por grano (`salpicar` con radio
            # 1.0 hace nueve `np.add.at` y cuesta 55 ms por frame); el
            # nucleo de radio 1 se recupera despues con un desenfoque
            # separable de tres tomas, de peso total equivalente.
            salpicar(arena, xy, "#ffffff", peso=1.0, radio=0.9)
            d = arena[:, :, 0]
            v = d.copy()
            v[1:] += 0.333 * d[:-1]
            v[:-1] += 0.333 * d[1:]
            dens = v.copy()
            dens[:, 1:] += 0.333 * v[:, :-1]
            dens[:, :-1] += 0.333 * v[:, 1:]
            b = np.clip(dens / densidad_ref, 0.0, 1.0) ** 0.45
            capa_arena = colorear(b, LUTS["regla"], vmin=0.0, vmax=1.0)
            img += capa_arena.astype(np.float32) - fondo
            frames[k] = np.clip(img, 0, 255).astype(np.uint8)

        # --- el grano huye de donde la placa vibra --------------------
        # direccion: la del gradiente de |u|^2, que es -sign(u)*grad(u);
        # modulo: Newton amortiguado min(k_conv*dist, paso_max), estable
        # tambien en los modos altos, donde |grad u| es grande y un paso
        # proporcional al gradiente se pasaria de largo y oscilaria.
        vel = np.minimum(k_conv * dist, paso_max)
        sg = np.sign(u) / g * vel
        x -= ux * sg
        y -= uy * sg
        # temblor: proporcional a la amplitud local mas un piso (el plato
        # entero tiembla). Sin ese piso la arena caeria EXACTAMENTE sobre
        # la linea y la cifra seria un 100 % que ninguna placa real da.
        s = ruido * agit * env * (np.abs(u) + piso)
        x += s * rng.standard_normal(granos)
        y += s * rng.standard_normal(granos)
        np.abs(x, out=x)
        np.abs(y, out=y)
        np.subtract(2.0, x, out=x, where=x > 1.0)
        np.subtract(2.0, y, out=y, where=y > 1.0)

    # la cifra de cada modo es el promedio del ultimo tramo, no el valor
    # de un frame suelto: la fraccion respira con el latido del plato
    # (mas ruido en el maximo de amplitud) y un frame cualquiera daria un
    # numero que depende de la fase.
    cola = max(10, largo // 5)
    frac_modo = [float(np.mean(frac_frame[c + largo - cola:c + largo]))
                 for c in cambios]

    cifras = {}
    # `fraccion_nodal_*` (0-1) son los nombres que lee
    # studio/tools/sonda_emergencia.py; los `_pct` son los que el clip
    # pone en pantalla.
    for i in range(n_modos):
        cifras[f"fraccion_nodal_modo_{i + 1}"] = round(frac_modo[i], 4)
    for i in range(n_modos):
        cifras[f"frac_nodos_modo_{i + 1}_pct"] = round(
            100.0 * frac_modo[i], 1)
    cifras["frac_nodos_final_pct"] = round(100.0 * frac_modo[-1], 1)
    cifras["umbral_nodo_px"] = float(umbral_px)
    cifras["modos"] = [list(par) for par in modos]
    cifras["frecuencia_relativa"] = [round(v, 2) for v in f_rel]
    cifras["granos"] = int(granos)

    extra = {
        "frames_cambio_modo": list(cambios),
        "frames_por_modo": largo,
        "modos": [list(par) for par in modos],
        "frecuencia_relativa": [round(v, 2) for v in f_rel],
        "periodo_latido_frames": [round(v, 1) for v in periodo],
        "placa_px": (x0, y0, lado),
        "fraccion_por_frame": frac_frame,
        "granos": int(granos),
    }
    if campos is not None:
        extra["campo_u_abs"] = campos
    return frames, cifras, extra


def simular(semilla=1, pasos=800, res=RES_BASE, granos=40000, modos=MODOS,
            umbral_px=3.0, k_conv=0.12, paso_max=0.004, ruido=0.0045,
            piso=1.2, agitacion=5.0, tau_agit=15.0, margen_px=6,
            densidad_ref=None):
    """La placa que canta: arena que se junta en las lineas nodales.

    Parametros:
      pasos      frames T (800: cuatro modos de 200 frames cada uno).
      res        (W, H) 9:16; (270, 480) o (360, 640).
      granos     numero de particulas de arena (40 000).
      modos      pares (m, n) en orden de frecuencia creciente.
      umbral_px  a cuantos pixeles de una linea nodal cuenta un grano
                 como "en el nodo" (3 px).
      k_conv     fraccion de la distancia al nodo que se recorre por
                 frame (Newton amortiguado, 0.12).
      paso_max   tope del paso por frame, en unidades de placa (0.004 =
                 1.03 px con la placa de 258 px).
      ruido      amplitud del temblor, multiplicada por (|u| + piso).
      piso       temblor de fondo, el que no depende de |u| (1.2). Es lo
                 que impide que la cifra sea un 100 % irreal.
      densidad_ref  densidad de granos por pixel que satura la linea al
                 pintar; None = se deduce de `granos` y del lado.
      agitacion  cuanto brinca la arena justo despues de un cambio de
                 modo (x6 al principio, decayendo con `tau_agit`).
      margen_px  aire entre la placa y el borde del encuadre.

    Devuelve dict(frames uint8 (T,H,W,3), cifras, extra).

    `extra` trae `frames_cambio_modo` (el frame en que arranca cada modo),
    `frames_por_modo`, `modos`, `frecuencia_relativa`,
    `periodo_latido_frames`, `placa_px` = (x0, y0, lado) en pixeles,
    `fraccion_por_frame` (T,) con la fraccion de granos en el nodo frame a
    frame (para dibujar la curva encima) y `campo_u_abs` (4, lado, lado)
    con |u| de cada modo por si el clip quiere resaltar las lineas.
    """
    frames, cifras, extra = _correr(
        pasos, res, semilla, granos, modos, umbral_px, k_conv, paso_max,
        ruido, piso, agitacion, tau_agit, margen_px, densidad_ref,
        guardar=True)
    return {"frames": validar_pila(frames), "cifras": cifras,
            "extra": extra}


def medir(semilla=1, pasos=800, res=RES_BASE, granos=40000, modos=MODOS,
          umbral_px=3.0, k_conv=0.12, paso_max=0.004, ruido=0.0045,
          piso=1.2, agitacion=5.0, tau_agit=15.0, margen_px=6,
          densidad_ref=None):
    """Solo las cifras (misma dinamica, sin pintar ni guardar frames)."""
    _, cifras, _ = _correr(
        pasos, res, semilla, granos, modos, umbral_px, k_conv, paso_max,
        ruido, piso, agitacion, tau_agit, margen_px, densidad_ref,
        guardar=False)
    return cifras
