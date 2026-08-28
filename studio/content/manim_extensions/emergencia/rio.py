# =====================================================================
# emergencia/rio.py — clip 12 "el rio" (curso 29, vertical).
#
# Que simula: un rio de verdad, celda a celda. Lattice-Boltzmann D2Q9 con
# colision BGK sobre una malla VERTICAL (el flujo baja por el lienzo 9:16)
# con un cilindro cruzado a un cuarto de la altura. Aqui no se resuelve
# Navier-Stokes: se mueven POBLACIONES de particulas por nueve direcciones
# y la viscosidad, la presion y los remolinos salen solos. Tras unos miles
# de pasos la estela se desestabiliza y aparece la calle de vortices de
# von Karman: remolinos que se desprenden alternos, uno de cada lado.
#
# Las reglas (son las que el clip pone como HUD, 1-3 palabras cada una):
#   TRANSPORTE  cada poblacion se mueve una celda en su direccion
#   COLISION    en cada celda se relaja hacia el equilibrio local (BGK)
#   REBOTE      lo que toca el cilindro se devuelve por donde vino
#
# Unidades de RED (todo el modulo trabaja en ellas y asi se declaran las
# cifras): el paso de malla y el paso de tiempo valen 1. Por defecto
#   D = 20 celdas (diametro del cilindro), u = 0.13 celdas/paso (entrada),
#   nu = u*D/Re = 0.01444  ->  tau = 3*nu + 0.5 = 0.5433  (omega = 1.840)
# Re = u*D/nu = 180: dentro de la ventana 150-200 donde la calle es clara
# y todavia periodica. tau se queda con margen sobre 0.5 (el limite de
# estabilidad); el modulo aborta si se pide tau <= 0.505. El numero de
# Mach de red es u*sqrt(3) = 0.23: el error de compresibilidad va como
# Ma^2 (~5 %) y es el precio de que la calle quepa en 7790 pasos.
#
# Malla y lienzo: la simulacion vive en una malla de (W/2, H/2) celdas
# —135x240 con la resolucion base, 32400 celdas— y al pintar se sube al
# doble con un 1-2-1 en cada eje (el campo queda continuo, no a bloques);
# el cilindro se dibuja DESPUES, a resolucion plena, para que su borde
# quede nitido. Simular a 270x480 costaria 4 veces mas y no se ve.
#
# Paredes laterales PERIODICAS (el rio no tiene orillas), entrada de
# velocidad impuesta por equilibrio arriba y salida abierta (gradiente
# nulo) abajo.
#
# Ritmo del clip: el arranque no se tira, se acelera. Los primeros 130
# frames graban 1 de cada 17 pasos (el rio se pone en marcha y la estela
# se desestabiliza en los 4 primeros segundos de pantalla) y los 620
# restantes 1 de cada 9, ya a velocidad de crucero: unos 83 frames por
# desprendimiento, 2.8 s por remolino a 30 fps.
#
# Colores por rol: VORTICIDAD (rot de la velocidad) con la LUT divergente
# "vorticidad" — violeta `C_ORDEN` el giro de un lado, naranja `C_ENERGIA`
# el del otro, fondo donde no gira; encima, una capa tenue en gris
# `C_EXTERNO` con lo que va MAS RAPIDO que la corriente de entrada (pintar
# la rapidez cruda deja el rio entero gris y se come el contraste); el
# cilindro en gris tinta (`C_MOBILIARIO` con borde `C_EXTERNO`). Nada en
# cian: el cian es solo para la cifra.
#
# T = 750 frames (25 s a 30 fps), 7790 pasos de LBM.
#
# Coste medido en el contenedor (2026-08-28, semilla 1, T=750):
#   res (270,480), malla 135x240, D=20: 22-27 s de CPU, pila 292 MB,
#                                       pico de memoria 0.57 GB.
#   res (360,640), malla 180x320, D=26: 41 s de CPU, pila 518 MB.
#   medir() (sin pintar) a res base: 11-15 s.
# Las dos dentro del presupuesto de 90 s y del tope de 1 GB. El paso de
# LBM cuesta 1.37 ms a 32400 celdas (ver la trampa del float64 abajo).
# Los dos campos que se guardan para pintar (vorticidad y rapidez) van en
# float16: en float32 pesaban 194 MB y el pico de memoria subia a 0.87 GB;
# a 0.05 % de resolucion en el valor maximo la imagen es la misma.
#
# TRAMPA: `EX`/`EY` son np.int64 y en numpy 2 multiplicar un array float32
# por un escalar np.int64 promociona a float64. El equilibrio se calculaba
# entero en doble precision: 7.3 ms/paso en vez de 1.37 (5.3 veces mas
# lento) sin ningun aviso. Con `float(EX[i])` todo se queda en float32.
#
# Cifras (medidas sobre lo simulado; las de red son las declaradas):
#   reynolds              u*D/nu en unidades de red             180.0
#   strouhal_medido       f*D/u, con f del pico de la FFT de la
#                         sonda (velocidad transversal 3 diametros
#                         aguas abajo, en el eje)               0.2053
#                         [dato externo, gris: la literatura da ~0.19 para
#                         un cilindro libre a Re 180; aqui el canal tiene
#                         solo 6.75 D de ancho y el bloqueo (0.148) sube
#                         el Strouhal ~8 %]
#   vortices_desprendidos remolinos contados en la ventana simulada,
#                         por cruces con histeresis de la sonda       16
#   ciclos_medidos        pares de vortices (un ciclo = uno por lado)   8
#   ciclos_fft            los mismos ciclos segun la FFT (control)   7.44
#   periodo_pasos         pasos por desprendimiento               749.5
#   diametro_celdas / velocidad_red / viscosidad_red / tau  (declarados)
#   celdas / pasos        32400 celdas, 7790 pasos
#
# extra:
#   centro_cilindro_px  (x, y) del centro del cilindro EN PIXELES.
#   radio_px            radio del cilindro en pixeles (20.0).
#   sonda_px            (x, y) del punto de la sonda en pixeles.
#   serie_sonda         (pasos,) float32, velocidad TRANSVERSAL en la
#                       sonda paso a paso: la senal de la que sale
#                       Strouhal (util para dibujarla en el HUD).
#   paso_inicio_crucero indice en `serie_sonda` donde acaba el arranque.
#   frames_arranque     cuantos frames del principio van acelerados.
#   pasos_por_frame     pasos entre frames en el tramo de crucero.
#   vorticidad_max      el valor con el que se normalizo el color.
#   res                 (W, H) con la que se pinto.
#
# Con res=(360,640) hay que subir `diametro` a 26 para mantener el mismo
# bloqueo; las cifras cambian un poco (St medido 0.2083) porque el canal
# ya no mide lo mismo en diametros. Medido, no supuesto.
# =====================================================================
import numpy as np

from . import (C_EXTERNO, C_FONDO, C_MOBILIARIO, LUTS, colorear, hex_a_rgb,
               validar_pila)

# D2Q9. El eje y va hacia ABAJO (fila creciente = aguas abajo), asi que la
# direccion 1 (+y) es la de la corriente.
EX = np.array([0, 0, 0, 1, -1, 1, -1, 1, -1], dtype=np.int64)
EY = np.array([0, 1, -1, 0, 0, 1, 1, -1, -1], dtype=np.int64)
W9 = np.array([4 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 9,
               1 / 36, 1 / 36, 1 / 36, 1 / 36], dtype=np.float32)
OPUESTO = np.array([0, 2, 1, 4, 3, 8, 7, 6, 5], dtype=np.int64)
I_BAJA = np.where(EY > 0)[0]      # entran por arriba
I_SUBE = np.where(EY < 0)[0]      # salen por arriba / entran por abajo
I_PLANO = np.where(EY == 0)[0]

_EXf = EX.astype(np.float32)[:, None, None]
_EYf = EY.astype(np.float32)[:, None, None]
_W9 = W9[:, None, None]


PARES = ((1, 2), (3, 4), (5, 8), (6, 7))   # direccion y su opuesta


def _equilibrio(rho, ux, uy, salida=None):
    """feq (9, ny, nx) float32. Usa el par (i, opuesta) para calcular una
    sola vez el termino par: feq_i = A + B, feq_opuesta = A - B."""
    if salida is None:
        salida = np.empty((9,) + rho.shape, dtype=np.float32)
    u2 = 1.5 * (ux * ux + uy * uy)
    uno_menos = 1.0 - u2
    salida[0] = float(W9[0]) * rho * uno_menos
    for i, j in PARES:
        # OJO: EX/EY son np.int64 y multiplicar un float32 por np.int64
        # promociona a float64 (numpy 2). Con float() puros el paso entero
        # se queda en float32 y cuesta la mitad (medido: 1.54 -> 0.75 ms).
        ex, ey = float(EX[i]), float(EY[i])
        cu = 3.0 * (ex * ux + ey * uy)
        w_rho = float(W9[i]) * rho
        a = w_rho * (uno_menos + 0.5 * cu * cu)
        b = w_rho * cu
        salida[i] = a + b
        salida[j] = a - b
    return salida


def _macro(f):
    """rho, ux, uy sin temporales (9,ny,nx): sumas direccion a direccion."""
    rho = f[0] + f[1] + f[2] + f[3] + f[4] + f[5] + f[6] + f[7] + f[8]
    jx = f[3] + f[5] + f[7] - f[4] - f[6] - f[8]
    jy = f[1] + f[5] + f[6] - f[2] - f[7] - f[8]
    return rho, jx / rho, jy / rho


def _eq_escalar(rho, ux, uy):
    """Equilibrio (9,) de un solo estado macroscopico (para la entrada)."""
    cu = 3.0 * (EX.astype(np.float64) * ux + EY.astype(np.float64) * uy)
    u2 = 1.5 * (ux * ux + uy * uy)
    return (W9 * rho * (1.0 + cu + 0.5 * cu * cu - u2)).astype(np.float32)


def _cilindro(nx, ny, frac_alto, diametro):
    """Mascara booleana (ny, nx) del cilindro y su centro (cx, cy)."""
    cx = nx / 2.0 - 0.5
    cy = frac_alto * ny
    y, x = np.mgrid[0:ny, 0:nx]
    r = diametro / 2.0
    return ((x - cx) ** 2 + (y - cy) ** 2) <= r * r, cx, cy


def _vorticidad(ux, uy):
    """rot_z = d(uy)/dx - d(ux)/dy, en 1/paso, por diferencias centradas.

    En x la malla SI es periodica (paredes laterales periodicas: el rio no
    tiene orillas), asi que ahi vale `roll`; en y no lo es, y usar `roll`
    pegaba la fila de la salida con la de la entrada y pintaba una raya de
    color en los dos bordes del lienzo. En y, diferencia centrada dentro y
    lateral en las dos filas de fuera."""
    duy_dx = 0.5 * (np.roll(uy, -1, axis=1) - np.roll(uy, 1, axis=1))
    dux_dy = np.empty_like(ux)
    dux_dy[1:-1] = 0.5 * (ux[2:] - ux[:-2])
    dux_dy[0] = ux[1] - ux[0]
    dux_dy[-1] = ux[-1] - ux[-2]
    return duy_dx - dux_dy


def _cruces(senal, umbral):
    """Ciclos completos: disparador de Schmitt sobre la senal centrada."""
    alto = senal > umbral
    bajo = senal < -umbral
    estado = 0
    ciclos = 0
    for i in range(senal.size):          # bucle sobre UNA serie 1D corta
        if estado <= 0 and alto[i]:
            if estado == -1:
                ciclos += 1
            estado = 1
        elif estado >= 0 and bajo[i]:
            estado = -1
    return ciclos


def _frecuencia(senal):
    """Frecuencia dominante (ciclos/paso) por FFT con ventana de Hann y
    refinado parabolico del pico. Devuelve 0.0 si no hay pico claro."""
    x = np.asarray(senal, dtype=np.float64)
    n = x.size
    if n < 64:
        return 0.0
    x = x - x.mean()
    if np.max(np.abs(x)) < 1e-12:
        return 0.0
    esp = np.abs(np.fft.rfft(x * np.hanning(n)))
    esp[0] = 0.0
    k = int(np.argmax(esp))
    if k <= 0 or k >= esp.size - 1:
        return float(k) / n
    a, b, c = esp[k - 1], esp[k], esp[k + 1]
    den = a - 2 * b + c
    corr = 0.0 if abs(den) < 1e-30 else 0.5 * (a - c) / den
    return float(k + corr) / n


def _correr(semilla=1, res=(270, 480), pasos_por_frame=9,
            frames_arranque=130, pasos_arranque=17, frames=750,
            reynolds=180.0, velocidad=0.13, diametro=20.0,
            alto_cilindro=0.25, pasos_empuje=900, amplitud_empuje=0.08,
            grabar=True):
    """Motor comun de `simular` y `medir`. Con `grabar=False` no pinta."""
    W, H = int(res[0]), int(res[1])
    if abs(H / W - 16 / 9) > 1e-6:
        raise ValueError(f"res tiene que ser 9:16; llego {res}")
    escala = 2
    nx, ny = W // escala, H // escala
    T = int(frames)
    n_arr = int(min(frames_arranque, T))
    rng = np.random.default_rng(semilla)

    nu = velocidad * diametro / reynolds
    tau = 3.0 * nu + 0.5
    if tau <= 0.505:
        raise ValueError(f"tau={tau:.4f} demasiado cerca de 0.5: inestable")
    omega = np.float32(1.0 / tau)

    obst, cx, cy = _cilindro(nx, ny, alto_cilindro, diametro)
    i_obst = np.flatnonzero(obst.ravel())

    # Arranque: corriente uniforme hacia abajo. La estela de un cilindro
    # es simetrica hasta que algo la desnivela, y con la simetria perfecta
    # de una malla la calle tarda decenas de miles de pasos en decidirse;
    # se la empuja con una RACHA transversal en la entrada durante los
    # primeros `pasos_empuje` pasos (amplitud 8 % de u) y luego se apaga:
    # la calle ya vive sola, con su propia frecuencia.
    x = np.arange(nx, dtype=np.float32)
    arruga = 1e-3 * np.sin(2 * np.pi * 3 * x / nx)[None, :]
    ux0 = np.zeros((ny, nx), dtype=np.float32) + arruga * velocidad
    ux0 += (rng.random((ny, nx), dtype=np.float32) - 0.5) * 1e-4 * velocidad
    uy0 = np.full((ny, nx), velocidad, dtype=np.float32)
    rho0 = np.ones((ny, nx), dtype=np.float32)
    f = np.ascontiguousarray(_equilibrio(rho0, ux0, uy0))
    buf = np.empty_like(f)
    feq = np.empty_like(f)

    periodo_est = diametro / (0.17 * velocidad)     # solo para la racha
    sonda_x = int(round(cx))
    sonda_y = int(min(ny - 3, round(cy + 3.0 * diametro)))

    pasos_tot = n_arr * pasos_arranque + (T - n_arr) * pasos_por_frame
    serie = np.zeros(pasos_tot, dtype=np.float32)
    if grabar:
        # float16: son campos que solo se van a PINTAR (la vorticidad
        # maxima vale 0.036 y ahi el paso de un float16 es 2e-5, 0.05 %).
        # En float32 las dos pilas de campo pesaban 194 MB y el pico de
        # memoria del modulo se iba a 0.87 GB.
        vort = np.zeros((T, ny, nx), dtype=np.float16)
        rapidez = np.zeros((T, ny, nx), dtype=np.float16)

    paso = 0
    for k in range(T):
        n_paso = pasos_arranque if k < n_arr else pasos_por_frame
        for _ in range(n_paso):
            # salida abierta: gradiente nulo en la ultima fila para las
            # direcciones que vuelven hacia dentro
            f[I_SUBE, -1, :] = f[I_SUBE, -2, :]

            rho, ux, uy = _macro(f)
            serie[paso] = ux[sonda_y, sonda_x]

            _equilibrio(rho, ux, uy, salida=feq)
            plano = f.reshape(9, -1)
            f_obst = plano[:, i_obst]              # pre-colision (rebote)
            np.subtract(feq, f, out=feq)
            feq *= omega
            f += feq                                # BGK en sitio
            plano[:, i_obst] = f_obst[OPUESTO]      # rebote en el cilindro

            # entrada: equilibrio con la velocidad impuesta (+ racha)
            if paso < pasos_empuje:
                ux_ent = (amplitud_empuje * velocidad
                          * np.sin(2 * np.pi * paso / periodo_est))
            else:
                ux_ent = 0.0
            f[:, 0, :] = _eq_escalar(1.0, ux_ent, velocidad)[:, None]

            buf[0] = f[0]
            for i in range(1, 9):
                buf[i] = np.roll(f[i], (int(EY[i]), int(EX[i])), axis=(0, 1))
            f, buf = buf, f

            paso += 1

        if grabar:
            _, ux, uy = _macro(f)
            ux = np.where(obst, 0.0, ux)
            uy = np.where(obst, 0.0, uy)
            vort[k] = _vorticidad(ux, uy)
            rapidez[k] = np.sqrt(ux * ux + uy * uy)

    if not np.all(np.isfinite(serie)):
        raise FloatingPointError("la simulacion diverge: baja omega o u")

    inicio = n_arr * pasos_arranque
    crucero = serie[inicio:] if serie.size - inicio >= 256 else serie
    frec = _frecuencia(crucero)
    centrada = serie - serie.mean()
    ciclos_cruce = _cruces(centrada, 0.25 * float(centrada.std() + 1e-30))
    st = frec * diametro / velocidad
    ciclos_fft = frec * crucero.size
    cifras = {
        "reynolds": round(float(velocidad * diametro / nu), 1),
        "strouhal_medido": round(float(st), 4),
        "vortices_desprendidos": int(2 * ciclos_cruce),
        "ciclos_medidos": int(ciclos_cruce),
        "ciclos_fft": round(float(ciclos_fft), 2),
        "periodo_pasos": round(float(1.0 / frec), 1) if frec > 0 else -1.0,
        "diametro_celdas": float(diametro),
        "velocidad_red": float(velocidad),
        "viscosidad_red": round(float(nu), 5),
        "tau": round(float(tau), 4),
        "celdas": int(nx * ny),
        "pasos": int(pasos_tot),
    }
    extra = {
        "centro_cilindro_px": (float(cx * escala + 0.5),
                               float(cy * escala + 0.5)),
        "radio_px": float(diametro / 2 * escala),
        "sonda_px": (float(sonda_x * escala + 0.5),
                     float(sonda_y * escala + 0.5)),
        "serie_sonda": serie,
        "paso_inicio_crucero": int(inicio),
        "frames_arranque": int(n_arr),
        "pasos_por_frame": int(pasos_por_frame),
        "res": (W, H),
    }
    if not grabar:
        return cifras, extra, None, None, None, cx, cy
    return cifras, extra, vort, rapidez, T, cx, cy


def _suavizar(campo):
    """Sube un campo (n, ny, nx) al doble por celdas y le pasa un 1-2-1 en
    cada eje: la vorticidad queda continua en vez de a bloques de 2x2 (el
    cilindro se dibuja DESPUES, a resolucion plena, para que su borde no
    se emborrone)."""
    campo = np.asarray(campo, dtype=np.float32)
    g = np.repeat(np.repeat(campo, 2, axis=-2), 2, axis=-1)
    # eje x: periodico (el canal lo es); eje y: NO (entrada arriba, salida
    # abajo): un np.roll en y pegaba la fila de entrada con la de salida y
    # dejaba una franja de color de 1-2 px en el borde superior del lienzo.
    g = 0.25 * (np.roll(g, 1, axis=-1) + 2.0 * g + np.roll(g, -1, axis=-1))
    arriba = np.concatenate([g[..., :1, :], g[..., :-1, :]], axis=-2)
    abajo = np.concatenate([g[..., 1:, :], g[..., -1:, :]], axis=-2)
    g = 0.25 * (arriba + 2.0 * g + abajo)
    return g.astype(np.float32)


def _pintar(vort, rapidez, W, H, cx, cy, diametro, u_ent, luz_velocidad):
    """Vorticidad divergente + capa tenue de rapidez + cilindro gris tinta."""
    T = vort.shape[0]
    estable = np.abs(vort[T // 3:].astype(np.float32))
    vmax = max(float(np.percentile(estable, 99.6)), 1e-9)
    umax = max(float(np.percentile(rapidez[T // 3:].astype(np.float32),
                                   99.5)), 1e-9)
    del estable

    fondo = hex_a_rgb(C_FONDO)
    tinte = (hex_a_rgb(C_EXTERNO) - fondo) * luz_velocidad
    relleno = hex_a_rgb(C_MOBILIARIO)
    borde_rgb = hex_a_rgb(C_EXTERNO)

    # cilindro a resolucion plena (la malla es la mitad en cada eje)
    y, x = np.mgrid[0:H, 0:W]
    r_px = diametro          # 2 px por celda -> el radio en px es D/2*2 = D
    d2 = (x - (2 * cx + 0.5)) ** 2 + (y - (2 * cy + 0.5)) ** 2
    disco = d2 <= r_px ** 2
    borde = disco & (d2 >= (r_px - 1.6) ** 2)

    frames = np.empty((T, H, W, 3), dtype=np.uint8)
    lote = 20
    for a in range(0, T, lote):
        b = min(a + lote, T)
        # realce con raiz: el remolino debil tambien se ve
        w = np.clip(_suavizar(vort[a:b]) / vmax, -1.0, 1.0)
        w = np.sign(w) * np.abs(w) ** 0.7
        img = colorear(w, LUTS["vorticidad"], vmin=-1.0, vmax=1.0)
        # solo lo que va MAS RAPIDO que la corriente de entrada: si se
        # pinta la rapidez cruda, el rio entero (que se mueve a u) queda
        # gris y se come el contraste de la vorticidad.
        capa = np.clip((_suavizar(rapidez[a:b]) - u_ent) / (umax - u_ent),
                       0.0, 1.0)[..., None]
        img = np.clip(img.astype(np.float32) + capa * tinte, 0, 255)
        img[:, disco] = relleno
        img[:, borde] = borde_rgb
        frames[a:b] = img.astype(np.uint8)
    return frames, vmax


def simular(semilla=1, pasos=9, res=(270, 480), frames=750,
            frames_arranque=130, pasos_arranque=17, reynolds=180.0,
            velocidad=0.13, diametro=20.0, alto_cilindro=0.25,
            pasos_empuje=900, amplitud_empuje=0.08, luz_velocidad=0.40):
    """Lattice-Boltzmann D2Q9: la calle de vortices de von Karman.

    `pasos` = pasos de LBM entre frames grabados en el tramo de crucero
    (el arranque graba 1 de cada `pasos_arranque`, acelerado). `res` admite
    (270,480) y (360,640); la malla es la mitad en cada eje.

    frames: uint8 (T, H, W, 3) con la vorticidad (violeta/naranja).
    cifras: reynolds, strouhal_medido, vortices_desprendidos, y los
            parametros de red declarados (D, u, nu, tau).
    extra:  centro_cilindro_px, radio_px, sonda_px, serie_sonda (T pasos),
            paso_inicio_crucero, frames_arranque, pasos_por_frame, res.
    """
    cifras, extra, vort, rapidez, T, cx, cy = _correr(
        semilla=semilla, res=res, pasos_por_frame=pasos, frames=frames,
        frames_arranque=frames_arranque, pasos_arranque=pasos_arranque,
        reynolds=reynolds, velocidad=velocidad, diametro=diametro,
        alto_cilindro=alto_cilindro, pasos_empuje=pasos_empuje,
        amplitud_empuje=amplitud_empuje, grabar=True)
    pila, vmax = _pintar(vort, rapidez, int(res[0]), int(res[1]), cx, cy,
                         diametro, velocidad, luz_velocidad)
    extra["vorticidad_max"] = float(vmax)
    return {"frames": validar_pila(pila), "cifras": cifras, "extra": extra}


def medir(semilla=1, pasos=9, res=(270, 480), frames=750,
          frames_arranque=130, pasos_arranque=17, reynolds=180.0,
          velocidad=0.13, diametro=20.0, alto_cilindro=0.25,
          pasos_empuje=900, amplitud_empuje=0.08, luz_velocidad=0.40):
    """Solo las cifras (sin pintar), para la sonda. Mismos parametros."""
    cifras = _correr(
        semilla=semilla, res=res, pasos_por_frame=pasos, frames=frames,
        frames_arranque=frames_arranque, pasos_arranque=pasos_arranque,
        reynolds=reynolds, velocidad=velocidad, diametro=diametro,
        alto_cilindro=alto_cilindro, pasos_empuje=pasos_empuje,
        amplitud_empuje=amplitud_empuje, grabar=False)[0]
    return cifras
