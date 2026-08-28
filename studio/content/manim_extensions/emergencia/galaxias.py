# =====================================================================
# emergencia/galaxias.py — clip 13 "dos galaxias" (curso 29, vertical).
#
# Que simula: dos galaxias de disco que se cruzan. La gravedad es la de
# siempre, 1/r^2, sin nada mas: no hay ninguna regla que diga "haz un
# brazo espiral" ni "tiende un puente". Los brazos, el puente de marea y
# las dos colas largas salen de que la parte del disco mas cercana a la
# otra galaxia es tirada mas fuerte que su propio nucleo. Es el modelo de
# Toomre & Toomre (1972): los dos NUCLEOS pesan y se atraen entre si, y
# las 4000 particulas del disco son de PRUEBA (sin masa, solo caen). Asi
# el paso cuesta O(n) en vez de O(n^2) y caben 4000 en el presupuesto.
#
# Las reglas (son las que el clip pone como HUD, 1-3 palabras cada una):
#   ATRACCION   todo tira de todo como 1/r^2 (con nucleo de Plummer)
#   MAREA       tira mas del lado cercano: eso estira el disco
#   LEAPFROG    medio empujon, un salto, medio empujon (KDK, reversible)
#
# Unidades: G = 1, masa del nucleo A = 1.0 y del B = 0.7, softening de
# Plummer eps = 0.6 (evita el infinito de 1/r^2 en un encuentro cercano).
# Orbita PARABOLICA (E = 0) de pericentro 13, separacion inicial 42,
# inclinada 0.35 rad respecto a la vertical del lienzo. Los dos discos
# giran en el mismo sentido que la orbita (prograda): es la unica manera
# de que salgan colas largas y finas — en retrogrado apenas se despeinan.
# Discos: A 2200 particulas entre r 0.8 y 8, B 1800 entre 0.7 y 6.5, con
# perfil exponencial (h = r_max/3) y velocidad circular exacta del
# potencial de Plummer de su nucleo.
#
# Camara FIJA en el centro de masas (que no se mueve: la cantidad de
# movimiento total de los nucleos es cero por construccion). El mundo
# visible mide `alto_mundo` = 105 unidades de alto; los dos nucleos nunca
# se acercan a menos de 60 px del borde, y lo unico que sale del lienzo
# son las puntas de las colas.
#
# Ritmo: 900 frames x 2 pasos de dt = 0.171 -> t = 308. El pericentro cae
# en el frame 386 (43 % de la pieza): antes, la aproximacion; despues,
# 170 unidades de tiempo (casi dos giros del disco) para que las colas y
# el puente se dibujen.
#
# Colores por rol: disco A en verde `C_VIVO` y disco B en ambar
# `C_REGLA`, con `salpicar` (nucleo gaussiano de radio 1) y estela CORTA
# (decaimiento 0.68: se lee el movimiento sin dejar rastro de bengala);
# los dos nucleos, mas grandes y claros (`#c7f9e5` y `#fff1c2`). Fondo
# `C_FONDO` sumado al volcar cada frame — si se pinta dentro del lienzo,
# la estela lo va apagando y el fondo parpadea. Nada en cian.
#
# T = 900 frames (30 s a 30 fps), 1800 pasos de leapfrog.
#
# Coste medido en el contenedor (2026-08-28, semilla 1, T=900):
#   res (270,480): 12-14 s de CPU, pila 350 MB.
#   res (360,640): 9.4 s de CPU, pila 622 MB (mismo numero de particulas:
#                  solo cambia el lienzo, y `salpicar` domina poco).
#   medir() (sin pintar): 0.7 s.
# El integrador cuesta nada; casi todo el tiempo es pintar los 900 frames.
#
# AUTOGRAVEDAD COMPLETA, medida: con `autogravedad=True` (y `masa_disco`
# repartida entre las particulas) el paso pasa a ser O(n^2) por sumas
# directas en trozos. Medido en el contenedor: 0.371 s/paso con n = 4002
# -> 669 s los 1800 pasos, SIETE VECES el presupuesto de 90 s (con
# n = 1000, 0.0276 s/paso -> 50 s, si que cabria). Por eso el modo por
# defecto es el restringido. El camino esta implementado y probado
# (n = 700, 300 pasos, 3.5 s) y en ese modo se mide ademas la energia
# TOTAL del sistema, que si se conserva: deriva 0.002 %.
#
# TRAMPA: la orbita es parabolica, o sea E de los nucleos = 0 por
# construccion. Dividir la deriva por |E0| daba "62 %" de un numero que
# era ruido de redondeo (E0 = 1.7e-06). La deriva se normaliza con la
# escala de energia del problema, G*mA*mB/pericentro = 0.0538, y se
# declara junto a la cifra.
#
# Cifras (medidas sobre lo simulado):
#   deriva_energia_nucleos_pct     max|E-E0| de los dos nucleos, en % de
#                                  G*mA*mB/rp                   2.85e-04
#   energia_nucleos_inicial        E0 (ha de ser ~0: parabolica) 1.7e-06
#   escala_energia                 G*mA*mB/rp, la referencia      0.0538
#   deriva_energia_particulas_pct  deriva de la energia especifica media
#                                  en una corrida de CONTROL con un solo
#                                  nucleo quieto (ahi SI se conserva; en
#                                  el encuentro real cambia de verdad
#                                  porque el potencial se mueve) 3.63e-04
#   distancia_minima               entre nucleos, en unidades      13.013
#   distancia_minima_px            la misma, en pixeles              59.5
#   frame_pericentro               frame del maximo acercamiento      386
#   A_capturadas_por_B_pct         del disco A, las que acaban ligadas
#                                  al nucleo B (energia < 0 respecto a
#                                  el)                                8.3
#   B_capturadas_por_A_pct         idem al reves                      8.3
#   escapan_pct                    del total, las que quedan sueltas de
#                                  los dos nucleos Y del par            0.2
#   en_el_puente_pct               ligadas al par pero a ningun nucleo  0.0
#   A_siguen_en_A_pct / B_siguen_en_B_pct   las que aguantan  91.7 / 91.3
#   particulas / pasos / tiempo_simulado    4000 / 1800 / 307.8
#   deriva_energia_sistema_pct     SOLO con autogravedad=True
#
# extra:
#   nucleo_a_px, nucleo_b_px  (T,2) float32, trayectoria de cada nucleo
#                             EN PIXELES (para el enfasis vectorial y
#                             para `seguir(...)` del nucleo si se quiere
#                             camara pegada a uno de los dos).
#   distancia_nucleos         (T,) float32, separacion en unidades por
#                             frame (para el HUD vivo y para marcar el
#                             pericentro).
#   escala_px_por_unidad      px por unidad de mundo (4.571 a res base).
#   alto_mundo                alto del mundo visible, en unidades.
#   clase_final               (n,) int8: 0 ligada a A, 1 ligada a B,
#                             2 ligada al par, 3 escapa. Las primeras
#                             n_a son del disco A.
#   res                       (W, H) con la que se pinto.
# =====================================================================
import numpy as np

from . import (C_FONDO, C_REGLA, C_VIVO, a_uint8, estela, hex_a_rgb,
               salpicar, validar_pila)

G = 1.0
CADA_ENERGIA = 25           # frames entre medidas de la energia total
COLOR_A = C_VIVO            # verde: el disco de la galaxia A
COLOR_NUCLEO_A = "#c7f9e5"  # su nucleo, mas claro
COLOR_B = C_REGLA           # ambar: el disco de la galaxia B
COLOR_NUCLEO_B = "#fff1c2"


def _acel_nucleos(pos, masas, eps2):
    """Aceleracion mutua de los dos nucleos (2,2) con softening Plummer."""
    d = pos[1] - pos[0]
    r2 = d @ d + eps2
    inv = 1.0 / (r2 * np.sqrt(r2))
    return np.stack([G * masas[1] * inv * d, -G * masas[0] * inv * d])


def _acel_prueba(xy, pos, masas, eps2):
    """Aceleracion (n,2) de las particulas de prueba: solo la sienten los
    dos nucleos. O(n) por paso, no O(n^2)."""
    a = np.zeros_like(xy)
    for k in range(pos.shape[0]):
        d = pos[k] - xy
        r2 = d[:, 0] ** 2 + d[:, 1] ** 2 + eps2
        a += (G * masas[k] / (r2 * np.sqrt(r2)))[:, None] * d
    return a


def _acel_completa(xy, masas, eps2, trozo=512):
    """Autogravedad TOTAL O(n^2) por sumas directas, en trozos para no
    reservar (n,n,2). Se mide en la prueba y NO es la opcion por defecto:
    ver el coste anotado en la cabecera."""
    n = xy.shape[0]
    a = np.zeros_like(xy)
    for i in range(0, n, trozo):
        j = min(i + trozo, n)
        d = xy[None, :, :] - xy[i:j, None, :]
        r2 = d[:, :, 0] ** 2 + d[:, :, 1] ** 2 + eps2
        inv = masas[None, :] / (r2 * np.sqrt(r2))
        a[i:j] = np.einsum("ij,ijk->ik", inv, d) * G
    return a


def _energia_total(xy, v, masas, eps2, trozo=512):
    """Energia total del sistema COMPLETO (cinetica + potencial de todos
    los pares, con el mismo softening). Es O(n^2), asi que solo se usa con
    `autogravedad=True` y cada `CADA_ENERGIA` frames: en ese modo la
    energia de los dos nucleos ya NO se conserva (el disco pesa y les da
    y les quita), y la que hay que vigilar es esta."""
    cin = 0.5 * float((masas * (v ** 2).sum(axis=1)).sum())
    pares = 0.0
    n = xy.shape[0]
    for i in range(0, n, trozo):
        j = min(i + trozo, n)
        d = xy[None, :, :] - xy[i:j, None, :]
        r = np.sqrt(d[:, :, 0] ** 2 + d[:, :, 1] ** 2 + eps2)
        pares += float((masas[i:j, None] * masas[None, :] / r).sum())
        pares -= float((masas[i:j] ** 2).sum() / np.sqrt(eps2))
    return cin - 0.5 * G * pares


def _orbita(masas, separacion, pericentro, inclinacion, eps2):
    """Estado inicial de los dos nucleos en una orbita PARABOLICA (E=0)
    de pericentro `pericentro`, con la separacion inclinada `inclinacion`
    radianes respecto a la vertical del lienzo y el centro de masas en el
    origen y en reposo."""
    m = masas.sum()
    u = np.array([np.sin(inclinacion), np.cos(inclinacion)])
    t = np.array([-u[1], u[0]])
    v = np.sqrt(2.0 * G * m / separacion)          # parabolica: v_esc
    ell = np.sqrt(2.0 * G * m * pericentro)        # L de un pericentro rp
    vt = ell / separacion
    vr = -np.sqrt(max(v * v - vt * vt, 0.0))
    rel = separacion * u
    vrel = vr * u + vt * t
    pos = np.stack([-masas[1] / m * rel, masas[0] / m * rel])
    vel = np.stack([-masas[1] / m * vrel, masas[0] / m * vrel])
    return pos, vel


def _radios(rng, n, r_min, r_max):
    """Radios de un disco EXPONENCIAL truncado (densidad superficial
    proporcional a exp(-r/h), h = r_max/3), invirtiendo su acumulada con
    una tabla. Con radios log-uniformes el disco salia con un borde duro
    —un aro brillante— y con un agujero negro en el centro; asi el brillo
    baja hacia fuera y no se ve donde acaba."""
    h = r_max / 3.0
    rr = np.linspace(r_min, r_max, 512)
    acu = 1.0 - (1.0 + rr / h) * np.exp(-rr / h)
    acu = (acu - acu[0]) / (acu[-1] - acu[0])
    return np.interp(rng.random(n), acu, rr)


def _disco(rng, n, centro, vel_centro, masa, r_min, r_max, sentido, eps2):
    """Disco de particulas de prueba en orbitas circulares alrededor de un
    nucleo, con perfil exponencial; `sentido` +1/-1 fija el giro."""
    r = _radios(rng, n, r_min, r_max)
    th = rng.random(n) * 2.0 * np.pi
    xy = np.stack([r * np.cos(th), r * np.sin(th)], axis=1) + centro
    # velocidad circular en el potencial de Plummer del nucleo
    vc = np.sqrt(G * masa * r * r / (r * r + eps2) ** 1.5)
    tang = np.stack([-np.sin(th), np.cos(th)], axis=1) * sentido
    return xy.astype(np.float64), (tang * vc[:, None] + vel_centro)


def _energia_nucleos(pos, vel, masas, eps2):
    d = pos[1] - pos[0]
    r = np.sqrt(d @ d + eps2)
    cin = 0.5 * (masas * (vel ** 2).sum(axis=1)).sum()
    return float(cin - G * masas[0] * masas[1] / r)


def _energia_especifica(xy, v, pos, masas, eps2):
    """Energia por unidad de masa de cada particula respecto a CADA nucleo
    (n,2): 0.5|v-v_nucleo|^2 - G*M/sqrt(r^2+eps^2)."""
    salida = np.empty((xy.shape[0], pos.shape[0]))
    for k in range(pos.shape[0]):
        d = xy - pos[k]
        r = np.sqrt(d[:, 0] ** 2 + d[:, 1] ** 2 + eps2)
        salida[:, k] = 0.5 * ((v[:, 0]) ** 2 + (v[:, 1]) ** 2) \
            - G * masas[k] / r
    return salida


def _clasificar(xy, v, vel_nuc, pos, masas, eps2):
    """Para cada particula: 0 ligada a A, 1 ligada a B, 2 ligada al par
    (puente/halo, no a un nucleo solo), 3 escapa."""
    e = np.empty((xy.shape[0], 2))
    pot = np.zeros(xy.shape[0])
    for k in range(2):
        d = xy - pos[k]
        r = np.sqrt(d[:, 0] ** 2 + d[:, 1] ** 2 + eps2)
        dv = v - vel_nuc[k]
        e[:, k] = 0.5 * (dv[:, 0] ** 2 + dv[:, 1] ** 2) - G * masas[k] / r
        pot -= G * masas[k] / r
    e_par = 0.5 * (v[:, 0] ** 2 + v[:, 1] ** 2) + pot
    clase = np.full(xy.shape[0], 3, dtype=np.int8)
    ligada = e < 0.0
    clase[ligada[:, 0]] = 0
    clase[ligada[:, 1]] = 1
    ambas = ligada[:, 0] & ligada[:, 1]
    clase[ambas] = np.argmin(e[ambas], axis=1).astype(np.int8)
    sueltas = ~ligada[:, 0] & ~ligada[:, 1]
    clase[sueltas & (e_par < 0.0)] = 2
    return clase


def _control_particulas(rng_semilla, n, masa, r_min, r_max, eps2, dt, pasos):
    """Corrida de CONTROL: el mismo disco y el mismo leapfrog, pero con un
    solo nucleo quieto en el origen. Ahi la energia especifica de cada
    particula SI se conserva, asi que su deriva mide el integrador (en el
    encuentro real la energia de una particula cambia de verdad: el
    potencial se mueve)."""
    rng = np.random.default_rng(rng_semilla)
    cero = np.zeros(2)
    xy, v = _disco(rng, n, cero, cero, masa, r_min, r_max, 1.0, eps2)
    pos = np.zeros((1, 2))
    masas = np.array([masa])
    e0 = _energia_especifica(xy, v, pos, masas, eps2)[:, 0].mean()
    a = _acel_prueba(xy, pos, masas, eps2)
    peor = 0.0
    for i in range(pasos):
        v += 0.5 * dt * a
        xy += dt * v
        a = _acel_prueba(xy, pos, masas, eps2)
        v += 0.5 * dt * a
        if i % 25 == 0:
            e = _energia_especifica(xy, v, pos, masas, eps2)[:, 0].mean()
            peor = max(peor, abs(e - e0) / abs(e0))
    return 100.0 * peor


def _correr(semilla=1, res=(270, 480), pasos=2, frames=900, dt=0.171,
            masa_a=1.0, masa_b=0.7, n_a=2200, n_b=1800, radio_a=(0.8, 8.0),
            radio_b=(0.7, 6.5), separacion=42.0, pericentro=13.0,
            inclinacion=0.35, softening=0.6, alto_mundo=105.0,
            autogravedad=False, masa_disco=0.0, grabar=True,
            decaimiento=0.68, peso=0.42):
    """Motor comun de `simular` y `medir`. Con `grabar=False` no pinta."""
    W, H = int(res[0]), int(res[1])
    if abs(H / W - 16 / 9) > 1e-6:
        raise ValueError(f"res tiene que ser 9:16; llego {res}")
    T = int(frames)
    rng = np.random.default_rng(semilla)
    eps2 = float(softening) ** 2
    masas = np.array([float(masa_a), float(masa_b)])

    pos, vel = _orbita(masas, separacion, pericentro, inclinacion, eps2)
    xa, va = _disco(rng, n_a, pos[0], vel[0], masas[0], radio_a[0],
                    radio_a[1], 1.0, eps2)
    xb, vb = _disco(rng, n_b, pos[1], vel[1], masas[1], radio_b[0],
                    radio_b[1], 1.0, eps2)
    xy = np.concatenate([xa, xb])
    v = np.concatenate([va, vb])
    de_a = np.zeros(xy.shape[0], dtype=bool)
    de_a[:n_a] = True

    if autogravedad:
        m_par = np.full(xy.shape[0], masa_disco / max(xy.shape[0], 1))
        todo_m = np.concatenate([masas, m_par])

    escala = H / float(alto_mundo)
    centro_px = np.array([W / 2.0, H / 2.0])

    def a_px(p):
        """mundo (…,2) -> pixeles: x a la derecha, y hacia ARRIBA."""
        q = np.asarray(p, dtype=np.float64) * escala
        return np.stack([centro_px[0] + q[..., 0],
                         centro_px[1] - q[..., 1]], axis=-1)

    e0 = _energia_nucleos(pos, vel, masas, eps2)
    # La orbita es PARABOLICA: E0 vale cero por construccion, asi que
    # dividir la deriva por |E0| no significa nada (sale 60 % de un numero
    # que es ruido de redondeo). Se normaliza con la escala de energia del
    # problema: la ligadura de los dos nucleos en el pericentro.
    escala_e = G * masas[0] * masas[1] / pericentro
    peor_e = 0.0
    peor_sis = 0.0
    e_sis0 = None
    d_min = np.inf
    paso_min = 0
    traza_a = np.zeros((T, 2), dtype=np.float32)
    traza_b = np.zeros((T, 2), dtype=np.float32)
    distancias = np.zeros(T, dtype=np.float32)
    if grabar:
        frames_out = np.empty((T, H, W, 3), dtype=np.uint8)
        lienzo = np.zeros((H, W, 3), dtype=np.float32)
        # el fondo se SUMA al volcar, no se acumula en el lienzo: si se
        # pinta dentro, la estela lo va apagando y el fondo parpadea.
        fondo = (hex_a_rgb(C_FONDO) / 255.0).astype(np.float32)

    if autogravedad:
        todo = np.concatenate([pos, xy])
        todo_v = np.concatenate([vel, v])
        acc = _acel_completa(todo, todo_m, eps2)
    else:
        acc_n = _acel_nucleos(pos, masas, eps2)
        acc_p = _acel_prueba(xy, pos, masas, eps2)

    k_paso = 0
    for k in range(T):
        for _ in range(int(pasos)):
            if autogravedad:
                todo_v += 0.5 * dt * acc
                todo += dt * todo_v
                acc = _acel_completa(todo, todo_m, eps2)
                todo_v += 0.5 * dt * acc
                pos, xy = todo[:2], todo[2:]
                vel, v = todo_v[:2], todo_v[2:]
            else:
                vel += 0.5 * dt * acc_n
                v += 0.5 * dt * acc_p
                pos += dt * vel
                xy += dt * v
                acc_n = _acel_nucleos(pos, masas, eps2)
                acc_p = _acel_prueba(xy, pos, masas, eps2)
                vel += 0.5 * dt * acc_n
                v += 0.5 * dt * acc_p
            d = float(np.hypot(*(pos[1] - pos[0])))
            if d < d_min:
                d_min, paso_min = d, k_paso
            k_paso += 1
        e = _energia_nucleos(pos, vel, masas, eps2)
        peor_e = max(peor_e, abs(e - e0))
        if autogravedad and k % CADA_ENERGIA == 0:
            e_sis = _energia_total(todo, todo_v, todo_m, eps2)
            if e_sis0 is None:
                e_sis0 = e_sis
            peor_sis = max(peor_sis, abs(e_sis - e_sis0) / abs(e_sis0))
        traza_a[k] = a_px(pos[0])
        traza_b[k] = a_px(pos[1])
        distancias[k] = np.hypot(*(pos[1] - pos[0]))

        if grabar:
            estela(lienzo, decaimiento)
            p = a_px(xy)
            salpicar(lienzo, p[de_a], COLOR_A, peso=peso, radio=1.0)
            salpicar(lienzo, p[~de_a], COLOR_B, peso=peso, radio=1.0)
            n_px = a_px(pos)
            salpicar(lienzo, n_px[:1], COLOR_NUCLEO_A, peso=1.5, radio=3.2)
            salpicar(lienzo, n_px[1:], COLOR_NUCLEO_B, peso=1.5, radio=3.2)
            frames_out[k] = a_uint8(lienzo + fondo)

    clase = _clasificar(xy, v, vel, pos, masas, eps2)
    n_tot = clase.size
    ca = clase[de_a]
    cb = clase[~de_a]
    deriva_part = _control_particulas(semilla + 7, min(n_a, 800), masas[0],
                                      radio_a[0], radio_a[1], eps2, dt,
                                      T * int(pasos))
    cifras = {
        "deriva_energia_nucleos_pct": float("%.2e" % (100.0 * peor_e
                                                      / escala_e)),
        "energia_nucleos_inicial": float("%.2e" % e0),
        "escala_energia": round(float(escala_e), 4),
        "deriva_energia_particulas_pct": float("%.2e" % deriva_part),
        "distancia_minima": round(float(d_min), 3),
        "distancia_minima_px": round(float(d_min * escala), 1),
        "frame_pericentro": int(paso_min // max(int(pasos), 1)),
        "A_capturadas_por_B_pct": round(100.0 * float((ca == 1).mean()), 1),
        "B_capturadas_por_A_pct": round(100.0 * float((cb == 0).mean()), 1),
        "escapan_pct": round(100.0 * float((clase == 3).mean()), 1),
        "en_el_puente_pct": round(100.0 * float((clase == 2).mean()), 1),
        "A_siguen_en_A_pct": round(100.0 * float((ca == 0).mean()), 1),
        "B_siguen_en_B_pct": round(100.0 * float((cb == 1).mean()), 1),
        "particulas": int(n_tot),
        "pasos": int(T * int(pasos)),
        "tiempo_simulado": round(float(T * int(pasos) * dt), 1),
    }
    if autogravedad:
        cifras["deriva_energia_sistema_pct"] = float("%.2e"
                                                    % (100.0 * peor_sis))
    extra = {
        "nucleo_a_px": traza_a,
        "nucleo_b_px": traza_b,
        "distancia_nucleos": distancias,
        "escala_px_por_unidad": float(escala),
        "alto_mundo": float(alto_mundo),
        "clase_final": clase,
        "res": (W, H),
    }
    if not grabar:
        return cifras, extra, None
    return cifras, extra, frames_out


def simular(semilla=1, pasos=2, res=(270, 480), frames=900, dt=0.171,
            masa_a=1.0, masa_b=0.7, n_a=2200, n_b=1800, separacion=42.0,
            pericentro=13.0, softening=0.6, alto_mundo=105.0,
            autogravedad=False, masa_disco=0.0):
    """N cuerpos: dos discos que chocan y sacan brazos y colas de marea.

    `pasos` = pasos de leapfrog entre frames (dt por paso). `res` admite
    (270,480) y (360,640).

    frames: uint8 (T, H, W, 3), disco A en verde y disco B en ambar.
    cifras: derivas de energia (nucleos y particulas de control), distancia
            minima entre nucleos, y el reparto final de cada disco.
    extra:  nucleo_a_px / nucleo_b_px (T,2) en pixeles, distancia_nucleos,
            escala_px_por_unidad, alto_mundo, clase_final, res.
    """
    cifras, extra, pila = _correr(
        semilla=semilla, res=res, pasos=pasos, frames=frames, dt=dt,
        masa_a=masa_a, masa_b=masa_b, n_a=n_a, n_b=n_b,
        separacion=separacion, pericentro=pericentro, softening=softening,
        alto_mundo=alto_mundo, autogravedad=autogravedad,
        masa_disco=masa_disco, grabar=True)
    return {"frames": validar_pila(pila), "cifras": cifras, "extra": extra}


def medir(semilla=1, pasos=2, res=(270, 480), frames=900, dt=0.171,
          masa_a=1.0, masa_b=0.7, n_a=2200, n_b=1800, separacion=42.0,
          pericentro=13.0, softening=0.6, alto_mundo=105.0,
          autogravedad=False, masa_disco=0.0):
    """Solo las cifras (sin pintar), para la sonda. Mismos parametros."""
    return _correr(
        semilla=semilla, res=res, pasos=pasos, frames=frames, dt=dt,
        masa_a=masa_a, masa_b=masa_b, n_a=n_a, n_b=n_b,
        separacion=separacion, pericentro=pericentro, softening=softening,
        alto_mundo=alto_mundo, autogravedad=autogravedad,
        masa_disco=masa_disco, grabar=False)[0]
