# =====================================================================
# CO.DE Academy - esp32.py
# Libreria del curso 31, "ESP32: el chip por dentro" (vertical, estilo
# LIENZO).
#
# Dos mitades, como en toda la casa:
#
#   1. FUNCIONES NUMERICAS. numpy puro, sin manim, deterministas
#      (default_rng con semilla fija). TODA cifra que aparece en pantalla
#      sale de aqui durante el render. Se pueden importar sin manim, que es
#      lo que permite que `studio/tools/sonda_esp32.py` las verifique.
#
#   2. PIEZAS DE DIBUJO. Devuelven mobjects colocados en el origen; NO
#      animan y NO deciden donde van (de eso se encarga `lienzo.encajar`).
#
# Honestidad: lo que sale de la hoja de datos de Espressif vive en HOJA y
# se rotula con etiqueta APAGADA. Lo que calcula esta libreria se rotula en
# AMBAR. La regla la impone `lienzo.etiqueta(medido=...)`.
# =====================================================================
import numpy as np

# --- Constantes fisicas ----------------------------------------------
C_LUZ = 299_792_458.0        # m/s, exacta por definicion del metro

# --- Hoja de datos de Espressif (ESP32-D0WD, rev. 3) ------------------
# Nada de esto lo mide la libreria: son cifras publicadas. Se rotulan en
# gris para que el ambar siga significando "calculado aqui".
HOJA = {
    "f_cpu": 240e6,             # Hz, reloj maximo de CPU
    "f_cristal": 40e6,          # Hz, cristal externo tipico
    "nucleos": 2,               # Xtensa LX6
    "sram_kb": 520,             # KB de SRAM interna
    "rom_kb": 448,              # KB de ROM
    "flash_mb": 4,              # MB de flash externa en el modulo tipico
    "gpio": 34,                 # pads GPIO fisicos
    "adc_bits": 12,             # SAR ADC
    "dac_bits": 8,
    "vdd": 3.3,                 # V
    "lado_encapsulado_mm": 5.0,  # QFN 5x5
    "i_activo_ma": 160.0,       # mA, Wi-Fi transmitiendo (valor tipico)
    "i_modem_sleep_ma": 20.0,   # mA, CPU a 240 MHz y radio apagada
    "i_light_sleep_ua": 800.0,  # uA
    "i_deep_sleep_ua": 10.0,    # uA, temporizador RTC + memoria RTC
    "i_ble_tx_ma": 130.0,       # mA durante la ventana de anuncio
    "z_salida_ohm": 25.0,       # ohmios, impedancia tipica de un pad GPIO
}


# =====================================================================
#  1. FUNCIONES NUMERICAS
# =====================================================================

# --- 01 · ciclos ------------------------------------------------------
def ciclos(segundos, f_cpu=None):
    """Ciclos de reloj en un intervalo. La cuenta del clip 01: cuantos
    ciclos pasan mientras alguien mira el reel."""
    f = HOJA["f_cpu"] if f_cpu is None else f_cpu
    return int(round(f * float(segundos)))


def serie_ciclos(t, f_cpu=None):
    """Ciclos acumulados en cada instante de `t` (array), en MILLONES.

    Se devuelve en millones a proposito: 8 160 millones cabe en el carril
    de la cifra y 8 160 000 000 no (el guardian del lienzo lo aborta)."""
    f = HOJA["f_cpu"] if f_cpu is None else f_cpu
    return np.asarray(t, dtype=float) * f / 1e6


# --- 02 · reparto entre dos nucleos -----------------------------------
def tareas(n=12, semilla=31):
    """Duraciones (ms) de un lote de tareas independientes."""
    rng = np.random.default_rng(semilla)
    return np.round(rng.uniform(3.0, 22.0, size=n), 1)


def reparto(duraciones, nucleos=2):
    """Reparto greedy LPT: la tarea mas larga al nucleo que antes queda
    libre. Devuelve (asignacion, carga_por_nucleo, makespan).

    Es el algoritmo, no una estimacion: el makespan que se rotula es el
    que produce ESTE reparto sobre ESTAS duraciones."""
    dur = np.asarray(duraciones, dtype=float)
    orden = np.argsort(-dur)                       # de mas larga a mas corta
    carga = np.zeros(int(nucleos))
    asignacion = np.zeros(len(dur), dtype=int)
    inicio = np.zeros(len(dur))
    for i in orden:
        k = int(np.argmin(carga))
        asignacion[i] = k
        inicio[i] = carga[k]
        carga[k] += dur[i]
    return asignacion, inicio, carga, float(carga.max())


def aceleracion(duraciones, nucleos=2):
    """Cuanto se gana repartiendo. 1 nucleo = la suma; N nucleos = el
    makespan del reparto. El limite teorico es N y no se alcanza porque
    las tareas no se parten."""
    dur = np.asarray(duraciones, dtype=float)
    _, _, _, mk = reparto(dur, nucleos)
    return float(dur.sum() / mk)


# --- 03 · lo que cabe en la memoria -----------------------------------
def bytes_fotograma(ancho=240, alto=240, bits_por_pixel=16):
    return int(ancho * alto * bits_por_pixel // 8)


def caben(bytes_totales, bytes_pieza):
    """Cuantas piezas enteras caben. Division entera, sin redondear hacia
    arriba: media imagen no es una imagen."""
    return int(bytes_totales // bytes_pieza)


def memoria_kb(kb):
    return int(kb) * 1024


# --- 04 · el reloj ----------------------------------------------------
def periodo(f):
    return 1.0 / float(f)


def luz_por_ciclo(f):
    """Metros que recorre la luz en un ciclo de reloj."""
    return C_LUZ * periodo(f)


def multiplicador_pll(f_cpu=None, f_cristal=None):
    f_cpu = HOJA["f_cpu"] if f_cpu is None else f_cpu
    f_x = HOJA["f_cristal"] if f_cristal is None else f_cristal
    return f_cpu / f_x


# --- 05 · un pin es un bit --------------------------------------------
def combinaciones(bits=32):
    return 2 ** int(bits)


def flanco_rc(R=None, C=100e-12, V=None, t=None):
    """Carga de una capacidad a traves de la impedancia de salida del pad.

    Devuelve (t, v, t_subida_10_90). El tiempo de subida NO se estima: se
    mide sobre la curva muestreada, que es la misma que se dibuja."""
    R = HOJA["z_salida_ohm"] if R is None else R
    V = HOJA["vdd"] if V is None else V
    tau = R * C
    if t is None:
        t = np.linspace(0.0, 8.0 * tau, 2001)
    t = np.asarray(t, dtype=float)
    v = V * (1.0 - np.exp(-t / tau))
    t10 = float(np.interp(0.10 * V, v, t))
    t90 = float(np.interp(0.90 * V, v, t))
    return t, v, t90 - t10


# --- 06 · PWM y el filtro RC ------------------------------------------
def pwm(duty, f_pwm=5000.0, V=None, ciclos_n=40, muestras=20000):
    """Tren PWM ideal. Devuelve (t, v)."""
    V = HOJA["vdd"] if V is None else V
    T = 1.0 / f_pwm
    t = np.linspace(0.0, ciclos_n * T, int(muestras), endpoint=False)
    fase = np.mod(t, T) / T
    return t, np.where(fase < float(duty), V, 0.0)


def filtro_rc(t, v, R=10e3, C=1e-6, v0=0.0):
    """Paso bajo RC integrado paso a paso (Euler hacia atras, estable).

    Se integra la MISMA señal que se dibuja: la media y el rizado que se
    rotulan salen de esta salida, no de una formula aparte."""
    t = np.asarray(t, dtype=float)
    v = np.asarray(v, dtype=float)
    tau = R * C
    y = np.empty_like(v)
    y[0] = v0
    dt = np.diff(t)
    for i in range(1, len(v)):
        a = dt[i - 1] / (tau + dt[i - 1])
        y[i] = y[i - 1] + a * (v[i] - y[i - 1])
    return y


def media_y_rizado(t, y, desde=0.0):
    """Media y rizado pico a pico sobre la ventana que se le pasa.

    Se le pasa la ventana DIBUJADA, no la simulacion entera: la regla de
    la casa es que la estadistica rotulada se mide sobre lo que el
    espectador ve."""
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    corte = t[0] + desde * (t[-1] - t[0])
    m = t >= corte
    return float(y[m].mean()), float(y[m].max() - y[m].min())


def pwm_filtrado(duty, f_pwm=5000.0, R=10e3, C=1e-6, V=None,
                 ciclos_vista=4, taus_previos=8.0, por_ciclo=400):
    """PWM + filtro RC, simulado hasta el REGIMEN y devuelto en dos piezas.

    El error que costo la primera pasada de la sonda: con tau = 10 ms y una
    ventana de 8 ms, el condensador todavia se esta cargando, asi que la
    "media" salia 0.74 V en vez de 1.65 y el "rizado" 372 mV en vez de 16.
    No era un fallo del filtro: era medir el transitorio.

    Aqui se simulan primero `taus_previos` constantes de tiempo (que no se
    dibujan) y solo despues los `ciclos_vista` que se enseñan y se miden.

    Devuelve (t, v, y, i0): las tres series completas y el indice donde
    empieza la ventana visible. Se dibuja y se mide de `i0` en adelante."""
    V = HOJA["vdd"] if V is None else V
    T = 1.0 / float(f_pwm)
    tau = float(R) * float(C)
    n_previos = int(np.ceil(float(taus_previos) * tau / T))
    n_total = n_previos + int(ciclos_vista)
    t, v = pwm(duty, f_pwm, V, ciclos_n=n_total,
               muestras=n_total * int(por_ciclo))
    y = filtro_rc(t, v, R, C)
    i0 = int(n_previos * por_ciclo)
    return t, v, y, i0


# --- 07 · el ADC ------------------------------------------------------
def cuantizar(x, bits=None, vref=None):
    """Cuantizacion uniforme por redondeo. Devuelve (y, escalon)."""
    bits = HOJA["adc_bits"] if bits is None else bits
    vref = HOJA["vdd"] if vref is None else vref
    niveles = 2 ** int(bits)
    q = vref / niveles
    x = np.asarray(x, dtype=float)
    codigo = np.clip(np.round(x / q), 0, niveles - 1)
    return codigo * q, q


def error_cuantizacion(x, bits=None, vref=None):
    """RMS del error MEDIDO sobre la señal dada (no q/sqrt(12) de memoria).

    Coinciden hasta la tercera cifra cuando la señal recorre muchos
    escalones; si no, la medida manda."""
    y, q = cuantizar(x, bits, vref)
    e = np.asarray(x, dtype=float) - y
    return float(np.sqrt(np.mean(e ** 2))), q


def snr_ideal(bits=None):
    """SNR de un cuantizador ideal con entrada senoidal a fondo de escala:
    6.02 N + 1.76 dB. Es teoria, no medida: se rotula como tal."""
    bits = HOJA["adc_bits"] if bits is None else bits
    return 6.02 * int(bits) + 1.76


def snr_medido(bits=None, vref=None, muestras=200_000, periodos=101.0):
    """SNR real de cuantizar una senoide a fondo de escala, medido.

    `periodos` no entero a proposito: con un numero entero de periodos las
    muestras caen siempre en los mismos puntos de la onda y el error de
    cuantizacion sale correlacionado (da hasta 2 dB de mas)."""
    bits = HOJA["adc_bits"] if bits is None else bits
    vref = HOJA["vdd"] if vref is None else vref
    t = np.linspace(0.0, 1.0, int(muestras), endpoint=False)
    x = 0.5 * vref * (1.0 + np.sin(2 * np.pi * periodos * t))
    y, _ = cuantizar(x, bits, vref)
    e = x - y
    return float(10.0 * np.log10(np.mean((x - x.mean()) ** 2)
                                 / np.mean(e ** 2)))


# --- 08 · los buses ---------------------------------------------------
def tiempo_i2c(n_bytes, f=400e3):
    """Cada byte cuesta 9 bits en I2C: los 8 de datos mas el ACK del
    esclavo. Se suman el start, la direccion con su ACK y el stop."""
    bits = 9 * int(n_bytes) + 9 + 2
    return bits / float(f)


def tiempo_spi(n_bytes, f=40e6):
    """SPI no lleva ACK: 8 bits por byte y a correr."""
    return 8 * int(n_bytes) / float(f)


def ventaja_spi(n_bytes=1024, f_i2c=400e3, f_spi=40e6):
    return tiempo_i2c(n_bytes, f_i2c) / tiempo_spi(n_bytes, f_spi)


# --- 09 · la antena ---------------------------------------------------
def longitud_onda(f=2.437e9):
    return C_LUZ / float(f)


def cuarto_de_onda(f=2.437e9, eps_ef=1.0):
    """Un cuarto de onda, acortado por el medio si se pide.

    En una pista de FR4 la onda va mas despacio y la antena impresa sale
    mas corta: ese es el motivo de que quepa en una placa de 25 mm."""
    return longitud_onda(f) / (4.0 * np.sqrt(float(eps_ef)))


# --- 10 · lo que de verdad viaja por el aire --------------------------
# Tiempos de 802.11n en 20 MHz, formato HT-mixed. Son del estandar, no
# medidos aqui: entran como parametros con su valor por defecto.
WIFI = {
    "preambulo_us": 36.0,       # L-STF+L-LTF+L-SIG+HT-SIG+HT-STF+HT-LTF
    "sifs_us": 16.0,
    "difs_us": 34.0,
    "ranura_us": 9.0,
    "cw_min": 15,               # ventana de contienda inicial
    "ack_us": 24.0,             # ACK a velocidad basica, con su preambulo
    "cabecera_mac": 34,         # bytes: MAC + FCS
    "cabecera_ip_udp": 28,      # bytes: IPv4 + UDP
    "tasa_mbps": 65.0,          # MCS7, 20 MHz, intervalo de guarda largo
}


def tiempo_trama(payload, cfg=None):
    """Tiempo de aire de UNA trama con su ACK y su espera. Devuelve un
    dict con cada tramo, para poder dibujarlos con su ancho real."""
    c = dict(WIFI)
    c.update(cfg or {})
    bytes_aire = int(payload) + c["cabecera_mac"] + c["cabecera_ip_udp"]
    datos_us = bytes_aire * 8 / c["tasa_mbps"]        # us = bits / (Mbit/s)
    backoff_us = 0.5 * c["cw_min"] * c["ranura_us"]   # espera media
    tramos = {
        "difs": c["difs_us"],
        "backoff": backoff_us,
        "preambulo": c["preambulo_us"],
        "datos": datos_us,
        "sifs": c["sifs_us"],
        "ack": c["ack_us"],
    }
    return tramos, float(sum(tramos.values()))


def eficiencia_aire(payload=1500, cfg=None):
    """Fraccion del tiempo de aire que transporta datos del usuario.

    No es la fraccion del tramo "datos": ese tramo tambien lleva las
    cabeceras. Se cuenta solo el payload."""
    c = dict(WIFI)
    c.update(cfg or {})
    _, total_us = tiempo_trama(payload, cfg)
    util_us = int(payload) * 8 / c["tasa_mbps"]
    return util_us / total_us


def caudal_util_mbps(payload=1500, cfg=None):
    c = dict(WIFI)
    c.update(cfg or {})
    _, total_us = tiempo_trama(payload, cfg)
    return int(payload) * 8 / total_us


# --- 11 · BLE: hablar poco --------------------------------------------
def anuncio_ble(payload=31, canales=3, tasa_mbps=1.0, rampa_us=150.0):
    """Duracion de un evento de anuncio: tres canales, cada uno con su
    paquete y su rampa de radio. Devuelve (us_por_canal, us_evento)."""
    bytes_paquete = 1 + 4 + 2 + 6 + int(payload) + 3   # pre+AA+cab+dir+dat+CRC
    us_paquete = bytes_paquete * 8 / float(tasa_mbps)
    us_canal = us_paquete + float(rampa_us)
    return us_canal, us_canal * int(canales)


def ciclo_trabajo(encendido_s, periodo_s):
    return float(encendido_s) / float(periodo_s)


def corriente_media(i_on_ma, t_on_s, i_off_ma, periodo_s):
    """Media ponderada por tiempo. Es una integral, no un promedio de los
    dos valores: el estado apagado dura mil veces mas."""
    t_off = float(periodo_s) - float(t_on_s)
    if t_off < 0:
        raise ValueError("el encendido no cabe en el periodo")
    return (float(i_on_ma) * float(t_on_s) + float(i_off_ma) * t_off) \
        / float(periodo_s)


# --- 12 · sondeo contra interrupcion ----------------------------------
def latencias_sondeo(periodo_ms=10.0, n=400, semilla=31):
    """El evento cae en cualquier momento; el bucle lo ve en su siguiente
    pasada. La latencia es lo que falta hasta esa pasada."""
    rng = np.random.default_rng(semilla)
    fase = rng.uniform(0.0, float(periodo_ms), size=int(n))
    return float(periodo_ms) - fase


def latencias_isr(base_us=1.8, jitter_us=0.9, n=400, semilla=31):
    """La interrupcion no espera al bucle: entra en cuanto la CPU termina
    la instruccion en curso. El jitter es el del contexto."""
    rng = np.random.default_rng(semilla + 1)
    return (base_us + rng.uniform(0.0, jitter_us, size=int(n))) / 1000.0


# --- 13 · el planificador ---------------------------------------------
def planificar(periodo_ms=10.0, ejecucion_ms=1.0, tick_ms=1.0,
               acaparador_ms=0.0, n=120, semilla=31):
    """Tarea periodica sobre un nucleo con un acaparador de la MISMA
    prioridad, que solo suelta la CPU en el tick del planificador.

    Devuelve (instantes_reales, jitter_ms). El jitter es la desviacion
    tipica del retraso respecto al instante ideal, medida sobre los `n`
    despertares simulados."""
    rng = np.random.default_rng(semilla)
    ideal = np.arange(int(n)) * float(periodo_ms)
    if acaparador_ms <= 0:
        retraso = rng.uniform(0.0, 0.02, size=int(n))
    else:
        # El despertar solo se atiende en el siguiente tick, y ademas hay
        # que esperar a que el acaparador agote su rodaja.
        fase = rng.uniform(0.0, float(tick_ms), size=int(n))
        espera_tick = float(tick_ms) - fase
        rodaja = rng.uniform(0.0, float(acaparador_ms), size=int(n))
        retraso = espera_tick + rodaja
    real = ideal + retraso
    return real, float(np.std(retraso))


# --- 14 · la vida de una pila -----------------------------------------
def consumo_medio_ua(t_despierto_s, periodo_s, i_activo_ma=None,
                     i_dormido_ua=None):
    i_on = HOJA["i_activo_ma"] if i_activo_ma is None else i_activo_ma
    i_off = HOJA["i_deep_sleep_ua"] if i_dormido_ua is None else i_dormido_ua
    carga = i_on * 1000.0 * float(t_despierto_s) \
        + float(i_off) * (float(periodo_s) - float(t_despierto_s))
    return carga / float(periodo_s)          # uA


def autonomia_dias(capacidad_mah=2000.0, t_despierto_s=2.0, periodo_s=3600.0,
                   i_activo_ma=None, i_dormido_ua=None,
                   autodescarga_por_ano=0.0):
    """Dias de vida. Con `autodescarga_por_ano` (fraccion de la capacidad
    que la pila pierde sola al año) la cuenta deja de ser una division: a
    consumos muy bajos, la pila se gasta antes por si misma que por el
    circuito, y eso es justo lo que remata el curso."""
    i_ua = consumo_medio_ua(t_despierto_s, periodo_s, i_activo_ma,
                            i_dormido_ua)
    fuga_ua = float(autodescarga_por_ano) * float(capacidad_mah) * 1000.0 \
        / (365.0 * 24.0)
    total_ua = i_ua + fuga_ua
    horas = float(capacidad_mah) * 1000.0 / total_ua
    return horas / 24.0


def barrido_autonomia(periodos_s, **kw):
    return np.array([autonomia_dias(periodo_s=p, **kw) for p in periodos_s])


# =====================================================================
#  2. PIEZAS DE DIBUJO
#
#  Manim se importa AQUI y de forma tolerante: la mitad numerica de arriba
#  tiene que poder importarse sin manim, que es lo que permite a
#  `studio/tools/sonda_esp32.py` verificar las cifras sin escena.
# =====================================================================
try:
    from manim import (DL, DOWN, LEFT, RIGHT, UP, Circle, Dot, Line,
                       RoundedRectangle, VGroup, VMobject)
    import lienzo as _lz
    _HAY_MANIM = True
except Exception:                                    # pragma: no cover
    _HAY_MANIM = False


def _exige_manim():
    if not _HAY_MANIM:
        raise RuntimeError(
            "las piezas de dibujo de esp32.py necesitan manim y lienzo; "
            "la mitad numerica se importa sin ellos a proposito")


# Grosores del estilo: uno para lo protagonista y otro para el mobiliario.
TRAZO = 3.0
TRAZO_FINO = 1.6


# --- El encapsulado ---------------------------------------------------
def encapsulado(lado=3.2, pines_por_lado=9, color=None, relleno=True):
    """El chip visto desde arriba: QFN cuadrado con sus pads.

    El punto ambar de la esquina es el pin 1, que es como se orienta un
    encapsulado de verdad. Es el unico adorno del dibujo."""
    _exige_manim()
    color = color or _lz.APAGADO
    cuerpo = RoundedRectangle(width=lado, height=lado, corner_radius=0.16,
                              stroke_color=color, stroke_width=TRAZO,
                              fill_color=_lz.AZUL,
                              fill_opacity=1.0 if relleno else 0.0)
    pads = VGroup()
    largo, ancho = 0.16, 0.055
    paso = lado / (pines_por_lado + 1)
    for i in range(pines_por_lado):
        d = -lado / 2 + paso * (i + 1)
        for (x, y, w, h) in ((d, lado / 2 + largo / 2, ancho, largo),
                             (d, -lado / 2 - largo / 2, ancho, largo),
                             (-lado / 2 - largo / 2, d, largo, ancho),
                             (lado / 2 + largo / 2, d, largo, ancho)):
            pad = RoundedRectangle(width=w, height=h, corner_radius=w / 3,
                                   stroke_width=0, fill_color=color,
                                   fill_opacity=0.55)
            pad.move_to([x, y, 0])
            pads.add(pad)
    pin1 = Dot([-lado / 2 + 0.30, lado / 2 - 0.30, 0], radius=0.055,
               color=_lz.AMBAR)
    return VGroup(cuerpo, pads, pin1)


def bloque(texto, ancho=1.5, alto=0.7, color=None, acento=False):
    """Una caja rotulada. El bloque interno del diagrama del chip."""
    _exige_manim()
    color = color or (_lz.AMBAR if acento else _lz.APAGADO)
    caja = RoundedRectangle(width=ancho, height=alto, corner_radius=0.10,
                            stroke_color=color, stroke_width=TRAZO_FINO,
                            fill_color=_lz.AZUL, fill_opacity=1.0)
    rot = _lz.rotulo(texto, color=color, font_size=_lz.MICRO)
    if rot.width > ancho - 0.16:
        rot.scale((ancho - 0.16) / rot.width)
    rot.move_to(caja.get_center())
    return VGroup(caja, rot)


def rejilla_bloques(specs, columnas=2, buff=0.16, ancho=1.5, alto=0.7):
    """Los bloques del chip en cuadricula. `specs` son textos, o pares
    (texto, acento)."""
    _exige_manim()
    filas = VGroup()
    fila = VGroup()
    for spec in specs:
        txt, ac = spec if isinstance(spec, (tuple, list)) else (spec, False)
        fila.add(bloque(txt, ancho, alto, acento=ac))
        if len(fila) == columnas:
            filas.add(fila.arrange(RIGHT, buff=buff))
            fila = VGroup()
    if len(fila):
        filas.add(fila.arrange(RIGHT, buff=buff))
    return filas.arrange(DOWN, buff=buff)


# --- Trazas y ejes ----------------------------------------------------
def traza(x, y, ancho=4.8, alto=2.4, color=None, grosor=TRAZO,
          rango_y=None, escalones=False):
    """Una serie convertida en polilinea dentro de una caja de ancho x alto.

    Devuelve (mobject, escala) — la escala hace falta para colocar rotulos
    sobre un valor concreto de la serie sin recalcular la transformacion.

    `escalones=True` dibuja la serie como escalera (retencion de orden
    cero), que es lo que de verdad hace un ADC o un PWM: unir sus muestras
    con rectas mentiria sobre la forma."""
    _exige_manim()
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x0, x1 = float(x.min()), float(x.max())
    if rango_y is None:
        y0, y1 = float(y.min()), float(y.max())
    else:
        y0, y1 = float(rango_y[0]), float(rango_y[1])
    dx = (x1 - x0) or 1.0
    dy = (y1 - y0) or 1.0

    def punto(xi, yi):
        return np.array([(xi - x0) / dx * ancho - ancho / 2,
                         (yi - y0) / dy * alto - alto / 2, 0.0])

    puntos = []
    if escalones:
        for i in range(len(x)):
            puntos.append(punto(x[i], y[i]))
            if i + 1 < len(x):
                puntos.append(punto(x[i + 1], y[i]))
    else:
        puntos = [punto(x[i], y[i]) for i in range(len(x))]
    linea = VMobject(stroke_color=color or _lz.TINTA, stroke_width=grosor)
    linea.set_points_as_corners(puntos)
    return linea, punto


def eje_ele(ancho=4.8, alto=2.4, color=None, grosor=TRAZO_FINO):
    """Solo dos lineas: abajo e izquierda. Ni marcas, ni numeros, ni caja.

    Un eje completo con su rejilla es exactamente el ruido visual que este
    curso no quiere: la escala la pone la cifra de abajo, no el eje."""
    _exige_manim()
    color = color or _lz.LINEA
    return VGroup(
        Line([-ancho / 2, -alto / 2, 0], [ancho / 2, -alto / 2, 0],
             stroke_color=color, stroke_width=grosor),
        Line([-ancho / 2, -alto / 2, 0], [-ancho / 2, alto / 2, 0],
             stroke_color=color, stroke_width=grosor))


def nivel(y_valor, punto, ancho=4.8, color=None, grosor=TRAZO_FINO,
          discontinua=True):
    """Una horizontal de referencia a la altura de un valor de la serie."""
    _exige_manim()
    from manim import DashedVMobject
    y = punto(0, y_valor)[1]
    ln = Line([-ancho / 2, y, 0], [ancho / 2, y, 0],
              stroke_color=color or _lz.APAGADO, stroke_width=grosor)
    return DashedVMobject(ln, num_dashes=26, dashed_ratio=0.45) \
        if discontinua else ln


# --- Barras -----------------------------------------------------------
def gantt(duraciones, asignacion, inicio, ancho=5.0, alto_barra=0.42,
          buff=0.30, colores=None, escala=None):
    """El reparto de tareas entre nucleos, a escala de tiempo real.

    Cada barra mide lo que dura su tarea: el makespan se VE, no se rotula
    aparte."""
    _exige_manim()
    dur = np.asarray(duraciones, dtype=float)
    asig = np.asarray(asignacion, dtype=int)
    ini = np.asarray(inicio, dtype=float)
    n_nucleos = int(asig.max()) + 1
    colores = colores or [_lz.AMBAR, _lz.CIAN]
    fin = float((ini + dur).max())
    escala = escala or (ancho / fin)
    filas = VGroup()
    for k in range(n_nucleos):
        fila = VGroup()
        for i in np.where(asig == k)[0]:
            barra = RoundedRectangle(
                width=max(dur[i] * escala, 0.05), height=alto_barra,
                corner_radius=min(0.06, dur[i] * escala / 3),
                stroke_width=0, fill_color=colores[k % len(colores)],
                fill_opacity=0.85)
            barra.move_to([ini[i] * escala + dur[i] * escala / 2,
                           -k * (alto_barra + buff), 0])
            fila.add(barra)
        filas.add(fila)
    filas.shift(LEFT * ancho / 2)
    return filas, escala


def barra_apilada(partes, ancho=5.0, alto=0.62, buff=0.03):
    """Barra de segmentos proporcionales. `partes` son (etiqueta, valor,
    color); la etiqueta puede ser None para un tramo sin rotular."""
    _exige_manim()
    total = float(sum(v for _, v, _ in partes)) or 1.0
    grupo = VGroup()
    x = -ancho / 2
    rotulos = VGroup()
    for texto, valor, color in partes:
        w = ancho * float(valor) / total - buff
        if w <= 0.004:
            x += ancho * float(valor) / total
            continue
        seg = RoundedRectangle(width=w, height=alto,
                               corner_radius=min(0.07, w / 3),
                               stroke_width=0, fill_color=color,
                               fill_opacity=0.85)
        seg.move_to([x + w / 2 + buff / 2, 0, 0])
        grupo.add(seg)
        if texto:
            rot = _lz.rotulo(texto, color=color, font_size=_lz.MICRO)
            rot.next_to(seg, DOWN, buff=0.16)
            if len(rotulos) and (rot.get_left()[0]
                                 < rotulos[-1].get_right()[0] + 0.10):
                # No se recorta ni se deja caer en silencio: en el primer
                # render "DIFS" y "BACKOFF" salieron pegados leyendose
                # "DIFBACKOFF", y en el frame de revision parecia una
                # palabra rara, no un fallo. Mejor que el render pare.
                raise ValueError(
                    f"barra_apilada: el rotulo '{texto}' se encima con el "
                    f"anterior (empieza en {rot.get_left()[0]:.2f} y el "
                    f"otro acaba en {rotulos[-1].get_right()[0]:.2f}). "
                    f"Rotula solo los tramos que importan: en este estilo "
                    f"la barra se explica con uno o dos, no con todos.")
            rotulos.add(rot)
        x += ancho * float(valor) / total
    return VGroup(grupo, rotulos)


# --- Bits y pines -----------------------------------------------------
def bits(valor, n=32, por_fila=8, lado=0.30, buff=0.09, color=None):
    """Los n bits de un registro como casillas. El 1 se pinta ambar."""
    _exige_manim()
    color = color or _lz.APAGADO
    filas = VGroup()
    fila = VGroup()
    for i in range(n - 1, -1, -1):
        encendido = bool((int(valor) >> i) & 1)
        c = RoundedRectangle(
            width=lado, height=lado, corner_radius=0.05,
            stroke_color=_lz.AMBAR if encendido else color,
            stroke_width=TRAZO_FINO,
            fill_color=_lz.AMBAR, fill_opacity=0.85 if encendido else 0.0)
        fila.add(c)
        if len(fila) == por_fila:
            filas.add(fila.arrange(RIGHT, buff=buff))
            fila = VGroup()
    if len(fila):
        filas.add(fila.arrange(RIGHT, buff=buff))
    return filas.arrange(DOWN, buff=buff)


def pines(n=8, largo=0.55, buff=0.26, color=None, encendidos=()):
    """Una fila de pines saliendo de un borde."""
    _exige_manim()
    color = color or _lz.APAGADO
    grupo = VGroup()
    for i in range(n):
        c = _lz.AMBAR if i in encendidos else color
        ln = Line([0, 0, 0], [0, largo, 0], stroke_color=c,
                  stroke_width=TRAZO if i in encendidos else TRAZO_FINO)
        grupo.add(ln)
    return grupo.arrange(RIGHT, buff=buff, aligned_edge=DOWN)


# --- Radio ------------------------------------------------------------
def seno(ciclos=3.0, ancho=4.8, amplitud=0.9, color=None, puntos=600,
         fase=0.0, grosor=TRAZO):
    """Una senoide limpia, sin ejes."""
    _exige_manim()
    x = np.linspace(0, 1, int(puntos))
    y = np.sin(2 * np.pi * float(ciclos) * x + float(fase))
    ln, _ = traza(x, y, ancho=ancho, alto=2 * amplitud,
                  color=color or _lz.CIAN, grosor=grosor, rango_y=(-1, 1))
    return ln


def meandro(vueltas=4, ancho=1.6, alto=0.9, color=None, grosor=TRAZO):
    """La antena impresa: la pista que va y viene para caber en la placa."""
    _exige_manim()
    puntos = [np.array([-ancho / 2, -alto / 2, 0.0])]
    paso = ancho / (2.0 * vueltas)
    arriba = True
    x = -ancho / 2
    for _ in range(2 * vueltas):
        puntos.append(np.array([x, alto / 2 if arriba else -alto / 2, 0.0]))
        x += paso
        puntos.append(np.array([x, alto / 2 if arriba else -alto / 2, 0.0]))
        arriba = not arriba
    ln = VMobject(stroke_color=color or _lz.AMBAR, stroke_width=grosor)
    ln.set_points_as_corners(puntos)
    return ln


def placa(ancho=3.0, alto=4.2, color=None):
    """Silueta de la placa, con la esquina de la antena recortada."""
    _exige_manim()
    return RoundedRectangle(width=ancho, height=alto, corner_radius=0.14,
                            stroke_color=color or _lz.LINEA,
                            stroke_width=TRAZO_FINO,
                            fill_color=_lz.AZUL, fill_opacity=1.0)


# --- Tiempo -----------------------------------------------------------
def pulsos(n=6, duty=0.5, ancho=4.8, alto=1.0, color=None,
           grosor=TRAZO):
    """Tren de pulsos cuadrado, dibujado como escalera de verdad."""
    _exige_manim()
    m = int(n) * 200
    x = np.linspace(0, n, m, endpoint=False)
    y = (np.mod(x, 1.0) < float(duty)).astype(float)
    ln, _ = traza(x, y, ancho=ancho, alto=alto, color=color or _lz.TINTA,
                  grosor=grosor, rango_y=(-0.05, 1.05), escalones=True)
    return ln


def marcas_tiempo(instantes, y=0.0, ancho=5.0, alto=0.34, t_max=None,
                  color=None, grosor=TRAZO):
    """Sucesos sobre una linea de tiempo: una rayita por instante."""
    _exige_manim()
    instantes = np.asarray(instantes, dtype=float)
    t_max = float(t_max or instantes.max() or 1.0)
    grupo = VGroup()
    for t in instantes:
        px = float(t) / t_max * ancho - ancho / 2
        grupo.add(Line([px, y - alto / 2, 0], [px, y + alto / 2, 0],
                       stroke_color=color or _lz.AMBAR,
                       stroke_width=grosor))
    return grupo


def escalones_log(valores, etiquetas=None, ancho=5.0, alto=3.0,
                  color=None, colores=None):
    """Escalera de consumo en decadas: cada estado, su barra.

    En escala logaritmica porque los cuatro estados del chip van de 10 uA a
    160 mA — cuatro ordenes de magnitud. En lineal, tres de las cuatro
    barras serian una raya."""
    _exige_manim()
    v = np.asarray(valores, dtype=float)
    lo = np.log10(v.min())
    hi = np.log10(v.max())
    rango = (hi - lo) or 1.0
    w = ancho / len(v) * 0.62
    paso = ancho / len(v)
    grupo = VGroup()
    rots = VGroup()
    for i, val in enumerate(v):
        h = 0.10 + (np.log10(val) - lo) / rango * (alto - 0.10)
        c = (colores[i] if colores else (color or _lz.APAGADO))
        barra = RoundedRectangle(width=w, height=h, corner_radius=0.06,
                                 stroke_width=0, fill_color=c,
                                 fill_opacity=0.85)
        barra.move_to([-ancho / 2 + paso * (i + 0.5), -alto / 2 + h / 2, 0])
        grupo.add(barra)
        if etiquetas:
            rot = _lz.rotulo(etiquetas[i], color=c, font_size=_lz.MICRO)
            if rot.width > paso * 0.95:
                rot.scale(paso * 0.95 / rot.width)
            rot.next_to(barra, DOWN, buff=0.14)
            rots.add(rot)
    return VGroup(grupo, rots)
