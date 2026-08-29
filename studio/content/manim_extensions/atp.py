# =====================================================================
# CO.DE Academy - Libreria de la familia "Sistemas ATP" (curso 30).
#
# ATP = Acquisition, Tracking and Pointing. Nueve lecciones que recorren
# la cadena entera: de un TLE a una prediccion de pase, de la prediccion
# a una trayectoria, de la trayectoria a un lazo de control, del lazo a
# una campaña Monte Carlo, y de ahi a un numero de decibelios.
#
# REGLAS DE ESTA LIBRERIA
#   * Todo lo que se rotula en pantalla se CALCULA aqui, con numpy y
#     semilla fija. Cero cifras escritas a mano en los clips.
#   * Cada funcion que devuelve una cifra dice en su docstring bajo QUE
#     CONDICION vale. Una cifra sin su condicion miente.
#   * Las piezas de dibujo del curso 9 (`apuntado.py`) se reutilizan tal
#     cual: vista polar, mascara, traza de pase, cono de keyhole,
#     antena, tarjeta TLE, curva S y aguja de velocidad. Aqui solo se
#     añade lo que aquel curso no necesitaba.
#
# El modelo de pase es geometria esferica honesta (orbita circular, gran
# circulo, Tierra esferica). NO es SGP4: SGP4 se EXPLICA en la leccion
# 1.2 y se declara como tal. Reproduce las cifras del curso fuente:
#   h=550 el_max=85 -> d=551 km, dAz/dt=9.05 grados/s
#   h=550 el_max=30 -> d=990 km, dAz/dt=0.51 grados/s
#   h=550 mascara=5 -> arco central 36.9 grados, pase 9.8 min
# =====================================================================
import numpy as np

# --- constantes -------------------------------------------------------
R_TIERRA_KM = 6371.0          # radio medio terrestre
MU_TIERRA = 398600.0          # km^3/s^2, parametro gravitacional estandar
C_LUZ_M_S = 299792458.0       # m/s (exacta por definicion)
K_BOLTZMANN_DB = 228.6        # -10 log10(k), dB

# --- la paleta (el color dice el PAPEL) -------------------------------
C_CALCULO = "#22d3ee"    # cifra calculada AQUI, y la antena/montura
C_SAT = "#f59e0b"        # el satelite, su traza, la referencia, el p95
C_CIELO = "#a78bfa"      # el cielo, los marcos, lo predicho
C_PELIGRO = "#f43f5e"    # keyhole, saturacion, error fuera de presupuesto
C_OK = "#34d399"         # enganche, dentro de presupuesto, enlace cerrado
C_EJE = "#31414f"        # mobiliario
C_DATO = "#94a0b0"       # dato publico NO calculado aqui

# --- los numeros de la estacion del curso -----------------------------
# Una sola estacion para las nueve lecciones, para que las cifras de una
# leccion se puedan comparar con las de otra.
H_LEO_KM = 550.0              # altitud de referencia
MASCARA_DEG = 5.0             # mascara de elevacion de la estacion
J_EJE = 2.0                   # kg m^2, inercia reflejada al eje
B_EJE = 0.5                   # N m s/rad, friccion viscosa
DIAMETRO_PLATO_M = 3.0        # plato de la estacion tipo OrbitEye
T_SISTEMA_K = 150.0           # temperatura de ruido del sistema
OBJETIVO_DEG = 0.1            # EL objetivo de apuntamiento del curso


# =====================================================================
# 1. Mecanica orbital minima
# =====================================================================

def velocidad_circular(h_km):
    """Rapidez orbital (km/s) de una orbita CIRCULAR a esa altitud."""
    r = R_TIERRA_KM + float(h_km)
    return float(np.sqrt(MU_TIERRA / r))


def periodo_orbital(h_km):
    """Periodo (s) de una orbita circular por la tercera de Kepler."""
    r = R_TIERRA_KM + float(h_km)
    return float(2.0 * np.pi * np.sqrt(r ** 3 / MU_TIERRA))


def velocidad_angular_cenit(h_km):
    """Velocidad angular aparente (grados/s) de la linea de vista EN EL
    CENIT, donde la velocidad del satelite es perpendicular a ella y el
    rango vale exactamente la altitud: omega = v/h.

    A 550 km da 0.79 grados/s; a 400 km, 1.10. Cuanto mas baja la
    orbita, mas rapido barre el cielo.
    """
    v = velocidad_circular(h_km)
    return float(np.degrees(v / float(h_km)))


def altitud_de_movimiento_medio(n_rev_dia):
    """Altitud (km) de la orbita circular cuyo movimiento medio es `n`
    revoluciones por dia. Es la cuenta que cierra un TLE con Kepler.

    n = 15.5 -> 424 km (regimen de la ISS); n = 15.0 -> 574 km.
    """
    n = float(n_rev_dia)
    t_seg = 86400.0 / n
    a = (MU_TIERRA * t_seg ** 2 / (4.0 * np.pi ** 2)) ** (1.0 / 3.0)
    return float(a - R_TIERRA_KM)


# =====================================================================
# 2. Geometria del pase
# =====================================================================

def angulo_central(h_km, el_deg):
    """Angulo central Tierra-estacion-satelite (grados) para una
    elevacion dada. Es la relacion que convierte "cuan alto lo veo" en
    "cuan lejos esta su punto subsatelite".

    En el cenit vale 0; en el horizonte (el=0) a 550 km vale 22.91.
    """
    el = np.radians(np.asarray(el_deg, dtype=float))
    razon = R_TIERRA_KM / (R_TIERRA_KM + float(h_km))
    lam = np.arccos(np.clip(razon * np.cos(el), -1.0, 1.0)) - el
    return np.degrees(lam)


def elevacion_de_angulo_central(h_km, lam_deg):
    """La inversa de `angulo_central`: elevacion (grados) que se ve
    cuando el punto subsatelite esta a `lam_deg` de la estacion."""
    lam = np.radians(np.asarray(lam_deg, dtype=float))
    r = R_TIERRA_KM + float(h_km)
    # tan(el) = (cos lam - R/r) / sin lam
    num = np.cos(lam) - R_TIERRA_KM / r
    den = np.sin(lam)
    el = np.where(den > 1e-12, np.arctan2(num, np.where(den > 1e-12, den, 1.0)),
                  np.pi / 2.0)
    return np.degrees(el)


def rango_oblicuo(h_km, el_deg):
    """Distancia real estacion-satelite (km) para una elevacion dada.

    En el cenit vale exactamente la altitud; a 5 grados y 550 km de
    altitud vale 2205 km, cuatro veces mas.
    """
    lam = np.radians(angulo_central(h_km, el_deg))
    r = R_TIERRA_KM + float(h_km)
    d2 = R_TIERRA_KM ** 2 + r ** 2 - 2.0 * R_TIERRA_KM * r * np.cos(lam)
    return np.sqrt(np.maximum(d2, 0.0))


def tasa_acimut(h_km, el_deg, el_max_deg=None):
    """Velocidad angular (grados/s) EXIGIDA AL EJE DE ACIMUT.

    Es el `1/cos(el)` que hace divergir la montura Az/El en el cenit:
    la velocidad angular total de la linea de vista se reparte entre los
    dos ejes, y cerca de la culminacion casi toda cae en acimut.

    Con `el_max_deg` se evalua EN LA CULMINACION de ese pase (que es
    donde la cifra es maxima y donde tiene sentido citarla); si se omite,
    se supone que `el_deg` ES la culminacion.
    """
    el = float(el_deg) if el_max_deg is None else float(el_max_deg)
    d = float(rango_oblicuo(h_km, el))
    v = velocidad_circular(h_km)
    omega_total = np.degrees(v / d)          # grados/s de la linea de vista
    return float(omega_total / max(np.cos(np.radians(el)), 1e-9))


def duracion_pase(h_km, el_max_deg=90.0, mascara_deg=MASCARA_DEG):
    """Duracion (s) del pase entre AOS y LOS, para un pase cuya
    culminacion es `el_max_deg` y una estacion con esa mascara.

    El satelite recorre un arco de gran circulo; el arco util es el que
    queda por encima de la mascara. Un pase CENITAL a 550 km con
    mascara de 5 grados recorre 36.9 grados centrales y dura 9.8 min.
    """
    lam_mask = float(angulo_central(h_km, mascara_deg))
    lam_min = float(angulo_central(h_km, el_max_deg))
    if lam_min >= lam_mask:
        return 0.0
    # Triangulo esferico rectangulo: cos(lam) = cos(lam_min) cos(u).
    cos_u = np.cos(np.radians(lam_mask)) / np.cos(np.radians(lam_min))
    u_max = np.degrees(np.arccos(np.clip(cos_u, -1.0, 1.0)))   # semiarco
    per = periodo_orbital(h_km)
    return float(2.0 * u_max / 360.0 * per)


def arco_central_pase(h_km, el_max_deg=90.0, mascara_deg=MASCARA_DEG):
    """Arco central TOTAL recorrido durante el pase util, en grados.
    Cenital a 550 km con mascara de 5: 36.9 grados."""
    per = periodo_orbital(h_km)
    return float(duracion_pase(h_km, el_max_deg, mascara_deg) / per * 360.0)


def perfil_pase(h_km=H_LEO_KM, el_max_deg=70.0, mascara_deg=MASCARA_DEG,
                az_culminacion_deg=140.0, n=1200):
    """LA PIEZA CENTRAL: el pase entero muestreado.

    Modelo: orbita circular, Tierra esferica, el satelite recorre un
    gran circulo que pasa a `lam_min` del cenit de la estacion. Es
    geometria exacta para ese modelo -- no es SGP4, y la leccion 1.2 lo
    declara.

    Devuelve un dict con arrays de longitud n:
      t   (s, 0 en AOS)      el  (grados)      az  (grados, 0-360)
      d   (km, rango)        vr  (km/s, radial, + = se aleja)
      az_pto (grados/s)      el_pto (grados/s)
    y los escalares `t_culminacion`, `duracion`, `d_min`, `el_max`,
    `az_barrido` (cuanto acimut recorre en total) y `vr_max`.

    El barrido de acimut es lo que hace el keyhole: en un pase cenital
    tiende a 180 grados ejecutados en un instante.
    """
    n = int(max(16, n))
    h_km = float(h_km)
    lam_min = float(angulo_central(h_km, el_max_deg))
    lam_mask = float(angulo_central(h_km, mascara_deg))
    if lam_min >= lam_mask:
        raise ValueError(
            f"perfil_pase: un pase que culmina a {el_max_deg} grados no "
            f"supera la mascara de {mascara_deg}.")

    cos_u = np.cos(np.radians(lam_mask)) / np.cos(np.radians(lam_min))
    u_max = np.arccos(np.clip(cos_u, -1.0, 1.0))        # rad, semiarco
    per = periodo_orbital(h_km)
    w_orb = 2.0 * np.pi / per                           # rad/s

    u = np.linspace(-u_max, u_max, n)                   # angulo a lo largo
    t = (u + u_max) / w_orb

    lam_r = np.arccos(np.clip(np.cos(np.radians(lam_min)) * np.cos(u),
                              -1.0, 1.0))
    el = elevacion_de_angulo_central(h_km, np.degrees(lam_r))
    d = rango_oblicuo(h_km, el)

    # Acimut: en el triangulo esferico rectangulo (angulo recto en el
    # punto de maxima aproximacion), el angulo en la estacion entre la
    # direccion de culminacion y la del satelite cumple
    #     tan(psi) = tan(u) / sin(lam_min)
    # Con lam_min -> 0 (pase cenital) psi salta a +-90: los 180 grados
    # de barrido instantaneo que definen el keyhole.
    sin_lam_min = max(np.sin(np.radians(lam_min)), 1e-12)
    psi = np.degrees(np.arctan(np.tan(u) / sin_lam_min))
    az = (float(az_culminacion_deg) + psi) % 360.0

    dt = np.gradient(t)
    vr = np.gradient(d) / dt                            # km/s
    az_desenroscado = np.degrees(np.unwrap(np.radians(az)))
    az_pto = np.gradient(az_desenroscado) / dt
    el_pto = np.gradient(el) / dt

    return {
        "t": t, "el": el, "az": az, "az_continuo": az_desenroscado,
        "d": d, "vr": vr, "az_pto": az_pto, "el_pto": el_pto,
        "t_culminacion": float(t[n // 2]),
        "duracion": float(t[-1]),
        "d_min": float(np.min(d)),
        "el_max": float(np.max(el)),
        "az_barrido": float(az_desenroscado[-1] - az_desenroscado[0]),
        "vr_max": float(np.max(np.abs(vr))),
        "az_pto_max": float(np.max(np.abs(az_pto))),
        "h_km": h_km, "mascara_deg": float(mascara_deg),
    }


def radio_keyhole(h_km=H_LEO_KM, vel_max_deg_s=6.0):
    """Semiangulo (grados desde el CENIT) del cono en el que un rotor
    limitado a `vel_max_deg_s` en acimut ya no puede seguir.

    Se resuelve la elevacion en la que la demanda `tasa_acimut` iguala
    el tope del rotor; el radio del cono es 90 menos esa elevacion.
    Devuelve 0.0 si el rotor aguanta hasta el cenit mismo (no ocurre:
    la demanda diverge).
    """
    els = np.linspace(89.999, 1.0, 4000)
    demanda = np.array([tasa_acimut(h_km, e) for e in els])
    dentro = np.where(demanda <= float(vel_max_deg_s))[0]
    if len(dentro) == 0:
        return 89.0
    return float(90.0 - els[dentro[0]])


def error_por_reloj(dt_s, h_km=H_LEO_KM, el_deg=90.0):
    """Error de apuntamiento (grados) que introduce un reloj
    desincronizado `dt_s` segundos, EN EL CENIT de un pase a `h_km`.

    Es el caso peor: donde la linea de vista se mueve mas rapido. Un
    solo segundo cuesta 0.79 grados a 550 km -- ocho veces el
    presupuesto entero de 0.1.
    """
    return float(abs(float(dt_s)) * velocidad_angular_cenit(h_km))


def enu_a_azel(e, n, u):
    """Del marco topocentrico Este-Norte-Arriba a (acimut, elevacion,
    rango). Unidades libres: las tres componentes en la misma.

    OJO AL ORDEN: el acimut se mide desde el NORTE hacia el ESTE, asi
    que el primer argumento de atan2 es la componente ESTE y el segundo
    la NORTE -- al reves de la convencion matematica. Es el error de
    signo mas frecuente al implementar la cadena por primera vez.

    e=400, n=300, u=500 -> Az 53.13, El 45.00, d 707.1
    """
    e, n, u = float(e), float(n), float(u)
    d = float(np.sqrt(e * e + n * n + u * u))
    az = float(np.degrees(np.arctan2(e, n)) % 360.0)
    el = float(np.degrees(np.arcsin(u / d))) if d > 0 else 0.0
    return az, el, d


# =====================================================================
# 3. Doppler
# =====================================================================

def velocidad_radial_max(h_km=H_LEO_KM):
    """Velocidad radial maxima (km/s) EN EL HORIZONTE de un pase cuyo
    plano contiene a la estacion.

    La condicion importa: NO es la velocidad orbital entera. A 550 km da
    7.0 km/s, no 7.59. Es el caso que acota por arriba.
    """
    v = velocidad_circular(h_km)
    lam = np.radians(float(angulo_central(h_km, 0.0)))
    d = float(rango_oblicuo(h_km, 0.0))
    return float(v * R_TIERRA_KM * np.sin(lam) / d)


def doppler_hz(vr_m_s, f0_hz):
    """Corrimiento Doppler (Hz) no relativista: fd = -vr/c * f0.

    `vr` positiva = el satelite SE ALEJA -> fd negativo (la frecuencia
    recibida baja). Un satelite a 7.6 km/s va a 2.5e-5 veces c, asi que
    la aproximacion no relativista es excelente.
    """
    return float(-float(vr_m_s) / C_LUZ_M_S * float(f0_hz))


BANDAS_ATP = (
    ("VHF 145 MHz", 145e6),
    ("UHF 437 MHz", 437e6),
    ("S 2200 MHz", 2200e6),
    ("X 8400 MHz", 8400e6),
)


def tabla_doppler(h_km=H_LEO_KM, bandas=BANDAS_ATP):
    """Para cada banda: corrimiento maximo y excursion total del pase,
    en Hz, con la velocidad radial maxima de `velocidad_radial_max`.

    Devuelve lista de dicts con `nombre`, `f0_hz`, `fd_hz`, `excursion_hz`.
    La excursion es el DOBLE del corrimiento: la señal recorre de +fd a
    -fd durante el pase.
    """
    vr = velocidad_radial_max(h_km) * 1000.0        # m/s
    filas = []
    for nombre, f0 in bandas:
        fd = abs(doppler_hz(vr, f0))
        filas.append({"nombre": nombre, "f0_hz": float(f0),
                      "fd_hz": float(fd), "excursion_hz": float(2.0 * fd)})
    return filas


def tasa_doppler(h_km=H_LEO_KM, f0_hz=437e6):
    """Tasa de cambio del Doppler (Hz/s) EN LA CULMINACION de un pase
    CENITAL, que es donde es maxima.

    La aceleracion radial en el cenit vale v^2/d con d = h. A 437 MHz y
    550 km da del orden de 150 Hz/s: la frecuencia se mueve mas rapido
    justo cuando la señal es mas fuerte y el keyhole aprieta la
    mecanica. Todo pasa a la vez.
    """
    v = velocidad_circular(h_km) * 1000.0           # m/s
    d = float(h_km) * 1000.0                        # m (cenit)
    a_r = v * v / d                                 # m/s^2
    return float(a_r / C_LUZ_M_S * float(f0_hz))


def curva_doppler(perfil, f0_hz=437e6):
    """La curva S completa: corrimiento (Hz) en cada instante del
    `perfil` que devuelve `perfil_pase`. Alta en AOS, cruza cero en la
    maxima aproximacion, baja en LOS."""
    return np.array([doppler_hz(v * 1000.0, f0_hz) for v in perfil["vr"]])


# =====================================================================
# 4. La montura: dinamica de un eje
# =====================================================================

def matrices_eje(J=J_EJE, b=B_EJE):
    """Espacio de estados de UN eje con x = [theta, omega].

    J theta'' + b theta' = u  ->  A = [[0,1],[0,-b/J]], B = [0, 1/J].
    Con J=2, b=0.5: A = [[0,1],[0,-0.25]], B = [0, 0.5].
    """
    J, b = float(J), float(b)
    A = np.array([[0.0, 1.0], [0.0, -b / J]])
    B = np.array([[0.0], [1.0 / J]])
    return A, B


def constante_mecanica(J=J_EJE, b=B_EJE):
    """Constante de tiempo mecanica J/b (s). Con J=2 y b=0.5 son 4 s:
    una montura empujada y soltada tarda una eternidad en pararse. Por
    eso casi siempre necesita accion derivativa."""
    return float(float(J) / float(b))


def par_necesario(J=J_EJE, b=B_EJE, alpha_deg_s2=5.0, w_deg_s=1.0):
    """Par (N m) EN EL EJE DE CARGA para acelerar a `alpha_deg_s2`
    mientras el eje ya gira a `w_deg_s`.

    Devuelve dict con `inercial`, `friccion` y `total`. Con J=2, b=0.5,
    alpha=5 grados/s^2 y w=1 grado/s: 0.175 + 0.009 = 0.184 N m.

    OJO: es el par en el EJE DE CARGA. El del motor esta al otro lado
    del reductor y es N*eta veces menor -- no se comparan directamente.
    """
    a = np.radians(float(alpha_deg_s2))
    w = np.radians(float(w_deg_s))
    ti = float(J) * a
    tf = float(b) * w
    return {"inercial": float(ti), "friccion": float(tf),
            "total": float(ti + tf)}


def par_motor(par_carga_nm, reduccion=1000.0, rendimiento=0.7):
    """Par (N m) que debe entregar el MOTOR para dar `par_carga_nm` en
    el eje de carga, a traves de un reductor de relacion N y
    rendimiento eta: tau_motor = tau_carga / (N eta).

    Con 0.184 N m, N=1000 y eta=0.7 son 0.26 mN m. El reductor regala
    par y cobra velocidad: divide por N la velocidad disponible, que es
    justo la variable que el keyhole pone contra las cuerdas.
    """
    return float(float(par_carga_nm) / (float(reduccion) * float(rendimiento)))


def par_viento(v_m_s=10.0, diametro_m=DIAMETRO_PLATO_M, brazo_m=0.15,
               cd=1.2, rho=1.225):
    """Par (N m) de una rafaga sobre el plato, tratado como un disco:
    tau = 1/2 rho v^2 Cd A r.

    Con un plato de 3 m (A = 7.07 m^2), brazo 0.15 m y rafaga de
    10 m/s da ~78 N m. Comparado con los 0.184 N m de acelerar la
    inercia son unas 425 veces mas: una montura real se dimensiona por
    VIENTO, no por aceleracion.

    DOS CONDICIONES, y las dos hay que decirlas al rotular la razon:
    1. Los dos pares estan en el EJE DE CARGA. Compararlos con el par
       del MOTOR (0.26 mN m, al otro lado del reductor) no seria
       legitimo: van multiplicados por N eta.
    2. El par de viento se calcula sobre el plato REAL de 3 m, mientras
       que J = 2 kg m^2 es la inercia de ESCALA DIDACTICA que usa el
       curso fuente (un plato de 3 m de verdad ronda los cientos de
       kg m^2). La conclusion cualitativa -- el viento manda -- es
       solida y no depende de la escala; el "425x" concreto SI depende
       de ella, y por eso se rotula junto a su condicion y nunca solo.
    """
    area = np.pi * (float(diametro_m) / 2.0) ** 2
    return float(0.5 * float(rho) * float(v_m_s) ** 2 * float(cd)
                 * area * float(brazo_m))


def resolucion_encoder(bits=16, recorrido_deg=360.0):
    """Resolucion angular (grados) de un encoder de `bits` sobre el
    recorrido dado. 16 bits sobre 360 grados: 0.0055 grados, comodo
    frente a un objetivo de 0.1 -- pero es tambien un piso de ruido que
    el termino derivativo amplifica."""
    return float(float(recorrido_deg) / (2 ** int(bits)))


def traza_backlash(holgura_deg=0.3, amplitud_deg=1.2, periodos=2.0, n=600):
    """Ciclo de histeresis del backlash al invertir el sentido de giro.

    El eje de entrada recorre una sinusoide; el de salida se queda
    ANCLADO mientras la entrada cruza la zona muerta de `holgura_deg`, y
    solo entonces vuelve a arrastrar. Devuelve dict con `entrada`,
    `salida`, `t` y `perdido_deg` (cuanto se queda quieta la salida en
    cada inversion, que es la holgura entera).

    Con 0.3 grados de holgura y un presupuesto de 0.1, la salida se come
    el requisito ENTERO antes de que el controlador haya opinado.
    """
    n = int(max(32, n))
    t = np.linspace(0.0, float(periodos), n)
    entrada = float(amplitud_deg) * np.sin(2.0 * np.pi * t)
    salida = np.zeros(n)
    y = entrada[0]
    mitad = float(holgura_deg) / 2.0
    for i in range(n):
        x = entrada[i]
        if x - y > mitad:
            y = x - mitad
        elif y - x > mitad:
            y = x + mitad
        salida[i] = y
    return {"t": t, "entrada": entrada, "salida": salida,
            "perdido_deg": float(holgura_deg),
            "amplitud_deg": float(amplitud_deg)}


# =====================================================================
# 5. El lazo: PID sobre una rampa
# =====================================================================

def error_arrastre(v_deg_s, b=B_EJE, kp=10.0):
    """Rezago PERMANENTE (grados) de un control proporcional ante una
    referencia en RAMPA de pendiente `v_deg_s`: e = v b / kp.

    La planta ya trae un integrador, asi que el lazo es de tipo 1: sigue
    un escalon sin error, pero ante rampa se queda constantemente
    rezagado. No es ruido ni perturbacion: es determinista, y ningun kd
    lo corrige.

    v=1 grado/s -> 0.05 (dentro del presupuesto)
    v=5 grados/s -> 0.25 (dos veces y media por encima)
    """
    return float(float(v_deg_s) * float(b) / float(kp))


def kp_para_arrastre(v_deg_s, error_deg=OBJETIVO_DEG, b=B_EJE):
    """El kp que hace falta para que el arrastre ante esa rampa quepa en
    `error_deg`. Con v=5 grados/s y objetivo 0.1: kp = 25."""
    return float(float(v_deg_s) * float(b) / float(error_deg))


def zeta_wn(kp=10.0, kd=0.0, J=J_EJE, b=B_EJE):
    """Amortiguamiento y frecuencia natural del lazo cerrado con control
    PD sobre J s^2 + b s: la caracteristica es
    J s^2 + (b + kd) s + kp = 0.

    wn = sqrt(kp/J), zeta = (b + kd) / (2 sqrt(kp J)).
    Con kp=10, J=2, kd=0: wn=2.24 rad/s, zeta=0.056 (casi nulo).
    """
    J, b = float(J), float(b)
    kp, kd = float(kp), float(kd)
    wn = float(np.sqrt(kp / J))
    zeta = float((b + kd) / (2.0 * np.sqrt(kp * J)))
    return zeta, wn


def kd_para_zeta(zeta_objetivo=0.7, kp=10.0, J=J_EJE, b=B_EJE):
    """El kd que da el amortiguamiento pedido: kd = 2 zeta sqrt(kp J) - b.
    Con zeta=0.7, kp=10, J=2, b=0.5: kd = 5.76."""
    return float(2.0 * float(zeta_objetivo) * np.sqrt(float(kp) * float(J))
                 - float(b))


def sobreimpulso(zeta):
    """Sobreimpulso (FRACCION, no porcentaje) de un segundo orden:
    Mp = exp(-pi zeta / sqrt(1 - zeta^2)).

    zeta=0.056 -> 0.84 (84 %); zeta=0.7 -> 0.046 (4.6 %).
    """
    z = float(np.clip(float(zeta), 0.0, 0.999999))
    return float(np.exp(-np.pi * z / np.sqrt(1.0 - z * z)))


def t_establecimiento(zeta, wn, banda=0.02):
    """Tiempo de establecimiento (s) al `banda` (2 % por defecto):
    aproximacion clasica t_s = -ln(banda) / (zeta wn), que para el 2 %
    es el familiar 4/(zeta wn).

    zeta=0.056, wn=2.24 -> 32 s. zeta=0.7, wn=2.24 -> 2.6 s.
    """
    z, w = float(zeta), float(wn)
    if z <= 0 or w <= 0:
        return float("inf")
    return float(-np.log(float(banda)) / (z * w))


def simular_adquisicion(salto_deg=60.0, kp=25.0, ki=2.0, kd=8.0, J=J_EJE,
                        b=B_EJE, u_max=0.5, antiwindup=True, f_lazo=20.0,
                        dt=0.005, t_total=40.0, tau_derivada=0.08):
    """EL WINDUP, en el unico sitio donde ocurre de verdad: la fase de
    ADQUISICION, cuando la montura estaba aparcada y tiene que
    preposicionarse en el punto de AOS antes de que empiece el pase.

    POR QUE AQUI Y NO EN UNA RAFAGA. Se midio: con esta planta
    (J = 2 kg m^2) y un accionamiento de 0.5 N m, una rafaga que supera
    el tope del motor NO produce windup, produce PERDIDA DE CONTROL --
    la montura se va a 14, 120 o 900 grados de error segun el golpe,
    porque ya nada la sujeta. El windup de libro necesita que el
    actuador saturado siga pudiendo recuperar, y eso pasa con un
    ESCALON DE REFERENCIA grande, no con un par externo mayor que el
    motor. Es ademas la situacion real: el preposicionamiento es un
    salto de decenas de grados y satura el accionamiento durante
    segundos.

    Devuelve dict con `t, ref, real, error, u, saturado`, `sobreimpulso`
    (grados por encima del objetivo), `t_asentamiento` (a 0.1 grados) y
    `frac_saturado`.
    """
    J, b = float(J), float(b)
    n = int(float(t_total) / float(dt)) + 1
    t = np.linspace(0.0, float(t_total), n)
    ref = np.full(n, float(salto_deg))
    ref[0] = 0.0
    ref_rad = np.radians(ref)

    theta = 0.0
    omega = 0.0
    integral = 0.0
    e_prev = float(ref_rad[0])
    d_filt = 0.0
    u_cmd = 0.0
    paso_lazo = max(1, int(round(1.0 / (float(f_lazo) * float(dt)))))

    real = np.zeros(n)
    error = np.zeros(n)
    u_hist = np.zeros(n)
    saturado = np.zeros(n, dtype=bool)

    for i in range(n):
        if i % paso_lazo == 0:
            e = ref_rad[i] - theta
            dt_lazo = paso_lazo * float(dt)
            d_bruta = (e - e_prev) / dt_lazo
            alfa = dt_lazo / (float(tau_derivada) + dt_lazo)
            d_filt = d_filt + alfa * (d_bruta - d_filt)
            u_sin_sat = kp * e + ki * integral + kd * d_filt
            u_cmd = float(np.clip(u_sin_sat, -float(u_max), float(u_max)))
            hay_sat = abs(u_sin_sat) > float(u_max) + 1e-12
            if not (antiwindup and hay_sat and (u_sin_sat * e > 0.0)):
                integral += e * dt_lazo
            e_prev = e

        # mismo criterio que en `simular_pase`: el estado de t[i] se
        # registra ANTES de integrar el paso
        real[i] = np.degrees(theta)
        error[i] = ref[i] - real[i]
        u_hist[i] = u_cmd
        saturado[i] = abs(u_cmd) >= float(u_max) - 1e-9

        alpha = (u_cmd - b * omega) / J
        omega += alpha * float(dt)
        theta += omega * float(dt)

    sobre = float(max(0.0, np.max(real) - float(salto_deg)))
    dentro = np.where(np.abs(error) <= OBJETIVO_DEG)[0]
    t_as = float("inf")
    if len(dentro):
        # primer instante a partir del cual YA NO se sale del umbral
        fuera = np.where(np.abs(error) > OBJETIVO_DEG)[0]
        idx = (fuera[-1] + 1) if len(fuera) else 0
        t_as = float(t[idx]) if idx < n else float("inf")
    return {"t": t, "ref": ref, "real": real, "error": error, "u": u_hist,
            "saturado": saturado, "sobreimpulso": sobre,
            "sobreimpulso_rel": float(sobre / float(salto_deg)),
            "t_asentamiento": t_as,
            "frac_saturado": float(np.mean(saturado))}


def simular_pase(perfil=None, kp=25.0, ki=2.0, kd=8.0, J=J_EJE, b=B_EJE,
                 u_max=8.0, antiwindup=True, f_lazo=20.0, dt=0.005,
                 eje="az", ruido_encoder_deg=0.0, sesgo_deg=0.0,
                 par_perturbacion=0.0, rafaga=None, semilla=7,
                 tau_derivada=0.08):
    """LA OTRA PIEZA CENTRAL: el lazo cerrado siguiendo un pase real.

    Integra J theta'' + b theta' = u_sat + perturbacion con un PID
    DIGITAL a `f_lazo` Hz (la derivada filtrada paso bajo, como debe
    ser) y saturacion de par en +-u_max. El anti-windup es por clamping:
    cuando el mando esta saturado y el error empuja el integrador en la
    misma direccion, se congela la integracion.

    `eje` elige que seguir del perfil: "az" (el exigente, con el
    keyhole) o "el".

    `rafaga` es `(t_inicio_s, duracion_s, par_nm)`: un golpe de viento.
    IMPORTA que exista, y aqui esta el porque, MEDIDO en esta libreria:
    el par de SEGUIMIENTO de este eje pica en 0.108 N m, asi que un
    motor dimensionado por viento (78 N m, ver `par_viento`) NO satura
    nunca siguiendo el pase, ni siquiera el cenital. El windup de la
    leccion 2.3 no nace del seguimiento: nace de una RAFAGA que mete al
    accionamiento en su tope. Forzarlo con un actuador ridiculo habria
    sido una demo falsa.

    Devuelve dict con `t, ref, real, error, u, saturado` (arrays) y las
    metricas `rms`, `max`, `frac_saturado`, todas medidas SOBRE EL PASE
    DIBUJADO, no sobre una corrida mas larga.
    """
    if perfil is None:
        perfil = perfil_pase()
    J, b = float(J), float(b)
    rng = np.random.default_rng(int(semilla))

    t_p = perfil["t"]
    ref_p = perfil["az_continuo"] if eje == "az" else perfil["el"]

    t_fin = float(t_p[-1])
    n = int(t_fin / float(dt)) + 1
    t = np.linspace(0.0, t_fin, n)
    ref = np.interp(t, t_p, ref_p)          # grados (lo que se dibuja)

    # El lazo se integra en RADIANES, que es donde vale J th'' + b th' = u
    # (el par esta en N m). La referencia y todo lo que sale del dict van
    # en GRADOS, que es como se rotula. Mezclar los dos fue el primer
    # defecto de esta libreria.
    ref_rad = np.radians(ref)
    theta = float(ref_rad[0])
    omega = 0.0
    integral = 0.0
    e_prev = 0.0
    d_filt = 0.0
    u_cmd = 0.0
    paso_lazo = max(1, int(round(1.0 / (float(f_lazo) * float(dt)))))

    real = np.zeros(n)
    error = np.zeros(n)
    u_hist = np.zeros(n)
    saturado = np.zeros(n, dtype=bool)

    sesgo_rad = np.radians(float(sesgo_deg))
    ruido_rad = np.radians(float(ruido_encoder_deg))
    for i in range(n):
        if i % paso_lazo == 0:
            medida = theta + sesgo_rad
            if ruido_rad > 0:
                medida += rng.normal(0.0, ruido_rad)
            e = ref_rad[i] - medida
            dt_lazo = paso_lazo * float(dt)
            # derivada filtrada (nunca cruda: el encoder esta cuantizado)
            d_bruta = (e - e_prev) / dt_lazo
            alfa = dt_lazo / (float(tau_derivada) + dt_lazo)
            d_filt = d_filt + alfa * (d_bruta - d_filt)
            u_sin_sat = kp * e + ki * integral + kd * d_filt
            u_cmd = float(np.clip(u_sin_sat, -float(u_max), float(u_max)))
            hay_sat = abs(u_sin_sat) > float(u_max) + 1e-12
            # clamping: solo se integra si no empuja mas hacia la saturacion
            if not (antiwindup and hay_sat and (u_sin_sat * e > 0.0)):
                integral += e * dt_lazo
            e_prev = e

        # Se registra el estado que hay EN t[i], antes de integrar el
        # paso. Registrarlo despues (que era el primer intento) empareja
        # theta(t_i + dt) con ref(t_i) y mete un sesgo de exactamente
        # v*dt en el error: con dt=0.005 y una rampa de 5 grados/s, el
        # arrastre salia 0.225 en vez de 0.250, un 10 % por debajo de lo
        # que dice `error_arrastre`. Lo cazo un agente comparando lo
        # dibujado con lo rotulable.
        real[i] = np.degrees(theta)
        error[i] = ref[i] - real[i]
        u_hist[i] = u_cmd
        saturado[i] = abs(u_cmd) >= float(u_max) - 1e-9

        par_ext = float(par_perturbacion)
        if rafaga is not None:
            t0, dur, p_nm = rafaga
            if float(t0) <= t[i] < float(t0) + float(dur):
                par_ext += float(p_nm)
        par = u_cmd + par_ext
        # integracion semi-implicita (estable y barata), en radianes
        alpha = (par - b * omega) / J
        omega += alpha * float(dt)
        theta += omega * float(dt)

    return {
        "t": t, "ref": ref, "real": real, "error": error, "u": u_hist,
        "saturado": saturado,
        "rms": float(np.sqrt(np.mean(error ** 2))),
        "max": float(np.max(np.abs(error))),
        "frac_saturado": float(np.mean(saturado)),
    }


# =====================================================================
# 6. LQR y robustez
# =====================================================================

def controlabilidad(A, B):
    """Matriz de controlabilidad [B AB] y su determinante/rango.

    Para el eje del curso da det = -0.25, rango 2: el eje es
    controlable, y por tanto se le pueden colocar los polos donde se
    quiera. Es el permiso matematico para diseñar por realimentacion de
    estados.
    """
    A, B = np.asarray(A, float), np.asarray(B, float).reshape(-1, 1)
    C = np.hstack([B, A @ B])
    return {"matriz": C, "rango": int(np.linalg.matrix_rank(C)),
            "det": float(np.linalg.det(C))}


def lqr(A, B, Q, R):
    """Regulador lineal cuadratico: resuelve la ecuacion algebraica de
    Riccati A'P + PA - PBR^-1B'P + Q = 0 y devuelve (K, P) con
    K = R^-1 B' P.

    Se resuelve por la matriz hamiltoniana (autovectores del semiplano
    izquierdo), no iterando a mano. Comprobado contra la forma cerrada
    del doble integrador con Q = diag(q,0), R = r:
        k1 = sqrt(q/r),  k2 = sqrt(2 k1)
    """
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float).reshape(A.shape[0], -1)
    Q = np.asarray(Q, dtype=float)
    R = np.atleast_2d(np.asarray(R, dtype=float))
    n = A.shape[0]

    Rinv = np.linalg.inv(R)
    H = np.block([[A, -B @ Rinv @ B.T],
                  [-Q, -A.T]])
    vals, vecs = np.linalg.eig(H)
    orden = np.argsort(vals.real)
    estables = orden[:n]                     # los de parte real negativa
    U = vecs[:, estables]
    X1, X2 = U[:n, :], U[n:, :]
    P = np.real(X2 @ np.linalg.inv(X1))
    P = (P + P.T) / 2.0
    K = Rinv @ B.T @ P
    return K, P


def lqr_doble_integrador(q, r):
    """Forma CERRADA del LQR sobre un doble integrador con Q=diag(q,0):
    k1 = sqrt(q/r), k2 = sqrt(2 k1), y de ahi wn = sqrt(k1) = (q/r)^(1/4)
    y zeta = 1/sqrt(2) = 0.707 PARA CUALQUIER q y r.

    Ese es el regalo del metodo: el amortiguamiento de libro que en el
    PID habia que buscar a tientas viene garantizado, y lo unico que se
    elige con q/r es cuan rapido va el lazo.
    """
    k1 = float(np.sqrt(float(q) / float(r)))
    k2 = float(np.sqrt(2.0 * k1))
    wn = float(np.sqrt(k1))
    zeta = float(k2 / (2.0 * wn))
    return {"k1": k1, "k2": k2, "wn": wn, "zeta": zeta,
            "t_est": t_establecimiento(zeta, wn)}


def margenes(A, B, K, w=None):
    """Margen de ganancia (dB) y de fase (grados) del lazo abierto
    L(s) = K (sI - A)^-1 B, medidos barriendo frecuencia.

    Devuelve dict con `margen_ganancia_db` (inf cuando la fase nunca
    cruza -180, que es el caso del LQR con R diagonal),
    `margen_fase_deg`, `wc` (frecuencia de cruce de ganancia) y las
    curvas `w`, `mag_db`, `fase_deg` por si el clip las dibuja.

    El LQR garantiza por construccion margen de ganancia infinito hacia
    arriba y margen de fase de al menos 60 grados. Se COMPRUEBA aqui en
    vez de citarse.
    """
    A = np.asarray(A, float)
    B = np.asarray(B, float).reshape(A.shape[0], -1)
    K = np.asarray(K, float).reshape(1, -1)
    if w is None:
        w = np.logspace(-2, 3, 2000)
    n = A.shape[0]
    L = np.zeros(len(w), dtype=complex)
    I = np.eye(n)
    for i, wi in enumerate(w):
        L[i] = (K @ np.linalg.solve(1j * wi * I - A, B))[0, 0]
    mag_db = 20.0 * np.log10(np.abs(L))
    fase = np.degrees(np.unwrap(np.angle(L)))

    # cruce de ganancia (|L| = 1) -> margen de fase
    mf, wc = float("nan"), float("nan")
    idx = np.where(np.diff(np.sign(mag_db)))[0]
    if len(idx):
        i0 = idx[0]
        frac = -mag_db[i0] / (mag_db[i0 + 1] - mag_db[i0])
        wc = float(w[i0] + frac * (w[i0 + 1] - w[i0]))
        f_c = float(fase[i0] + frac * (fase[i0 + 1] - fase[i0]))
        mf = float(180.0 + f_c)

    # cruce de fase (-180) -> margen de ganancia
    mg = float("inf")
    cruces = np.where(np.diff(np.sign(fase + 180.0)))[0]
    if len(cruces):
        i0 = cruces[0]
        frac = (-180.0 - fase[i0]) / (fase[i0 + 1] - fase[i0])
        m_c = float(mag_db[i0] + frac * (mag_db[i0 + 1] - mag_db[i0]))
        mg = float(-m_c)

    return {"margen_ganancia_db": mg, "margen_fase_deg": mf, "wc": wc,
            "w": w, "mag_db": mag_db, "fase_deg": fase}


def margen_fase_con_retardo(A, B, K, retardo_s):
    """Margen de fase (grados) que queda cuando el lazo añade un retardo
    puro de `retardo_s` (muestreo + computo + bus + driver).

    Un retardo no cambia la magnitud: resta wc * retardo radianes de
    fase en el cruce. Es exactamente lo que se come el margen cuando
    alguien baja la frecuencia del lazo "para que respire".
    """
    m = margenes(A, B, K)
    if not np.isfinite(m["wc"]):
        return m["margen_fase_deg"]
    perdida = np.degrees(m["wc"] * float(retardo_s))
    return float(m["margen_fase_deg"] - perdida)


# =====================================================================
# 7. Perturbaciones y Monte Carlo
# =====================================================================

def presupuesto_cuadratura(terminos):
    """Suma en cuadratura de contribuciones INDEPENDIENTES:
    RMS = sqrt(sum e_i^2), porque RMS^2 = sesgo^2 + varianza.

    `terminos` es un dict nombre -> grados. Devuelve dict con `total`,
    `dominante` (el nombre del termino mayor) y `fraccion` de cada uno
    sobre el total al cuadrado.

    Con sesgo 0.03, viento 0.05, ruido 0.02 y latencia 0.04 da 0.073
    grados: cabe bajo el objetivo de 0.1 con 27 % de margen. Y enseña lo
    que enseña la cuadratura: reducir el termino GRANDE mueve el total,
    reducir el pequeño casi no.
    """
    nombres = list(terminos.keys())
    vals = np.array([float(terminos[k]) for k in nombres])
    total = float(np.sqrt(np.sum(vals ** 2)))
    dominante = nombres[int(np.argmax(vals))] if len(vals) else None
    frac = (vals ** 2 / np.sum(vals ** 2)) if np.sum(vals ** 2) > 0 else vals
    return {"total": total, "dominante": dominante,
            "fraccion": {k: float(f) for k, f in zip(nombres, frac)},
            "margen_rel": float((OBJETIVO_DEG - total) / OBJETIVO_DEG)}


def elmax_aleatorio(n, h_km=H_LEO_KM, mascara_deg=MASCARA_DEG, rng=None):
    """Elevacion maxima (grados) de `n` pases AL AZAR sobre la estacion.

    No es uniforme, y esto importa: el desplazamiento del gran circulo
    respecto al cenit es lo que se reparte uniforme, asi que
    `lam_min ~ U(0, lam_mascara)` y de ahi sale la elevacion. El
    resultado es que los pases altos son RAROS -- mediana ~22 grados y
    solo un 10 % por encima de 68 -- que es lo que cualquiera observa
    con una estacion real.

    Sortear `el_max` uniforme entre 10 y 89 (que fue el primer intento
    de esta libreria) inventa una poblacion de pases cenitales que no
    existe, e infla la cola del Monte Carlo al doble.
    """
    rng = np.random.default_rng() if rng is None else rng
    lam_mask = float(angulo_central(h_km, mascara_deg))
    lam_min = rng.uniform(0.0, lam_mask, int(n))
    return np.asarray(elevacion_de_angulo_central(h_km, lam_min), dtype=float)


def campana_montecarlo(n=500, sigma_viento_nm=0.010, sigma_ruido_deg=0.02,
                       sesgo_max_deg=0.03, latencia_max_s=0.045,
                       kp=25.0, h_km=H_LEO_KM, mascara_deg=MASCARA_DEG,
                       vel_max_deg_s=6.0, semilla=2029):
    """Campaña Monte Carlo VECTORIZADA: `n` pases al azar, cada uno con
    sus perturbaciones muestreadas de su distribucion.

    CADA TERMINO SALE DE SU FISICA, no de un factor de forma inventado
    (el primer intento de esta libreria escalaba todo por 1/cos(el) y
    inflaba la cola al quintuple):

      - la GEOMETRIA se sortea primero con `elmax_aleatorio`, y de ella
        sale la demanda de acimut en la culminacion (`tasa_acimut`),
        **acotada al tope del rotor**: mas alla, la estacion no
        persigue, aplica una de las cuatro salidas del keyhole de la
        leccion 1.3, y el error no se dispara sin limite;
      - **viento**: un par de rafaga gaussiano de sigma
        `sigma_viento_nm` deflecta el lazo `tau/kp` radianes en
        regimen. NO escala con la velocidad del pase: la rafaga pega
        igual apunte donde apunte;
      - **latencia**: un retardo puro de `dt` segundos sobre una
        referencia que va a `v` grados/s cuesta exactamente `v dt`
        grados. ESTE si escala con el pase, y es el que fabrica la
        cola: un pase cenital con 45 ms de retardo rezaga 0.27 grados;
      - **ruido** de encoder: gaussiano de media cero;
      - **sesgo**: UNIFORME en +-sesgo_max (cero de encoder,
        alineacion al norte). NO tiene media cero: se suma integro y no
        se promedia ni se filtra.

    RMS de cada corrida por cuadratura, que es la definicion:
    RMS^2 = sesgo^2 + varianza.

    Devuelve dict con `rms` (array de n), `el_max`, `demanda`, los
    terminos por separado, `p50`, `p95`, `peor`, `n` y `pasa`. Semilla
    fija: misma semilla, mismo histograma, exactamente.
    """
    n = int(max(1, n))
    rng = np.random.default_rng(int(semilla))

    el_max = elmax_aleatorio(n, h_km, mascara_deg, rng)
    demanda = np.array([tasa_acimut(h_km, e) for e in el_max])
    demanda = np.minimum(demanda, float(vel_max_deg_s))

    # viento: deflexion del lazo contra el par, tau/kp radianes -> grados
    par_rafaga = np.abs(rng.normal(0.0, float(sigma_viento_nm), n))
    viento = np.degrees(par_rafaga / float(kp))
    # latencia: v * dt, el rezago puro de un retardo sobre una rampa
    latencia = demanda * rng.uniform(0.0, float(latencia_max_s), n)
    ruido = np.abs(rng.normal(0.0, float(sigma_ruido_deg), n))
    sesgo = rng.uniform(-float(sesgo_max_deg), float(sesgo_max_deg), n)

    rms = np.sqrt(viento ** 2 + ruido ** 2 + sesgo ** 2 + latencia ** 2)
    return {"rms": rms, "el_max": el_max, "demanda": demanda,
            "viento": viento, "latencia": latencia, "ruido": ruido,
            "sesgo": sesgo, "n": n, **percentiles(rms)}


def percentiles(muestras):
    """p50, p95 y peor caso de un array de corridas.

    La mediana NO sirve para aceptar un sistema: describe el pase
    tipico e ignora que uno de cada veinte ira mucho peor. El criterio
    de aceptacion del curso es p95 < 0.1 grados.
    """
    m = np.asarray(muestras, dtype=float)
    return {"p50": float(np.percentile(m, 50)),
            "p95": float(np.percentile(m, 95)),
            "peor": float(np.max(m)),
            "pasa": bool(np.percentile(m, 95) < OBJETIVO_DEG)}


def incertidumbre_percentil(n, p=0.95):
    """Cuanto se confia en un percentil estimado con `n` corridas.

    El numero de corridas por debajo del umbral es binomial, con
    desviacion sqrt(N p (1-p)). Con N=500 y p=0.95 son 4.9 corridas,
    algo mas de +-1 punto percentil; con N=2000, 9.7 sobre 2000, unos
    +-0.5 puntos.

    Regla practica: la precision mejora como sqrt(N), asi que
    CUADRUPLICAR las corridas solo DUPLICA la confianza.
    """
    n = float(n)
    p = float(p)
    sd = float(np.sqrt(n * p * (1.0 - p)))
    return {"corridas_sd": sd, "puntos_percentil": float(100.0 * sd / n),
            "n": int(n)}


def histograma_datos(muestras, bins=26):
    """Alturas y centros de un histograma, ya normalizados a la barra
    mas alta (para dibujarlo sin pelearse con la escala)."""
    m = np.asarray(muestras, dtype=float)
    conteo, bordes = np.histogram(m, bins=int(bins))
    centros = 0.5 * (bordes[:-1] + bordes[1:])
    alto = conteo / max(1, conteo.max())
    return {"centros": centros, "alturas": alto, "conteo": conteo,
            "bordes": bordes}


# =====================================================================
# 8. Enlace: por que 0.1 grados
# =====================================================================

def ancho_haz(diametro_m=DIAMETRO_PLATO_M, f_hz=2.2e9):
    """Ancho de haz a media potencia (grados): theta3dB ~ 70 lambda / D.

    La constante 70 engloba la iluminacion tipica del reflector (65-75
    segun el alimentador), asi que es una APROXIMACION DE INGENIERIA,
    no una identidad. Vale solo con D >> lambda.

    Plato de 3 m: banda S (2.2 GHz) 3.18 grados; banda Ka (30 GHz)
    0.233 grados.
    """
    lam = C_LUZ_M_S / float(f_hz)
    return float(70.0 * lam / float(diametro_m))


def perdida_apuntamiento(error_deg, theta3_deg):
    """Perdida por desapuntamiento (dB), aproximacion gaussiana del
    lobulo principal: L = 12 (theta/theta3dB)^2.

    Coherencia de la formula: en theta = theta3dB/2 da exactamente
    3 dB, la mitad de potencia en el borde del haz de media potencia.
    La dependencia es CUADRATICA: duplicar el error cuadruplica la
    perdida en dB.
    """
    return float(12.0 * (float(error_deg) / float(theta3_deg)) ** 2)


def ganancia_plato(diametro_m=DIAMETRO_PLATO_M, f_hz=2.2e9, eta=0.6):
    """Ganancia (dBi) de un reflector circular: G = eta (pi D / lambda)^2.

    Plato de 3 m a 2.2 GHz con eta=0.6: 34.6 dBi.
    """
    lam = C_LUZ_M_S / float(f_hz)
    g = float(eta) * (np.pi * float(diametro_m) / lam) ** 2
    return float(10.0 * np.log10(g))


def fspl_db(d_km, f_ghz):
    """Perdida de espacio libre (dB): 92.45 + 20log10(d_km) +
    20log10(f_GHz). Misma formula que `enlace.py` y `satelites.py`."""
    return float(92.45 + 20.0 * np.log10(float(d_km))
                 + 20.0 * np.log10(float(f_ghz)))


def g_sobre_t(diametro_m=DIAMETRO_PLATO_M, f_hz=2.2e9, eta=0.6,
              t_sys_k=T_SISTEMA_K):
    """G/T de la estacion (dB/K): ganancia menos temperatura de ruido en
    dB. Plato de 3 m, 2.2 GHz, eta 0.6, Tsys 150 K -> 12.8 dB/K."""
    return float(ganancia_plato(diametro_m, f_hz, eta)
                 - 10.0 * np.log10(float(t_sys_k)))


def presupuesto_cn0(eirp_dbw=9.0, d_km=1815.0, f_ghz=2.2,
                    perdidas_varias_db=3.0, error_deg=OBJETIVO_DEG,
                    diametro_m=DIAMETRO_PLATO_M, eta=0.6,
                    t_sys_k=T_SISTEMA_K):
    """El presupuesto de enlace en una linea:

        C/N0 = EIRP - FSPL - L_otras - L_point + G/T + 228.6   [dB-Hz]

    Devuelve dict con cada termino por separado (para dibujar la
    cascada) y el total. Los valores por defecto son el caso del curso:
    un CubeSat de banda S con 2 W y un parche de 6 dBi (EIRP 9 dBW)
    visto a 10 grados de elevacion.

    OJO: `d_km` es el rango OBLICUO, no la altitud. A 10 grados de
    elevacion un satelite a 550 km esta a 1815 km.
    """
    f_hz = float(f_ghz) * 1e9
    th3 = ancho_haz(diametro_m, f_hz)
    l_point = perdida_apuntamiento(error_deg, th3)
    fspl = fspl_db(d_km, f_ghz)
    gt = g_sobre_t(diametro_m, f_hz, eta, t_sys_k)
    total = (float(eirp_dbw) - fspl - float(perdidas_varias_db)
             - l_point + gt + K_BOLTZMANN_DB)
    return {"eirp_dbw": float(eirp_dbw), "fspl_db": fspl,
            "perdidas_db": float(perdidas_varias_db),
            "l_point_db": l_point, "theta3_deg": th3, "g_t_db": gt,
            "k_db": K_BOLTZMANN_DB, "cn0_dbhz": float(total),
            "d_km": float(d_km), "f_ghz": float(f_ghz)}


def eb_n0(cn0_dbhz, tasa_bps):
    """Eb/N0 (dB) = C/N0 - 10log10(Rb). Con 82.9 dB-Hz y 1 Mbps quedan
    22.9 dB, muy por encima de los ~10.5 que pide QPSK para BER 1e-6."""
    return float(float(cn0_dbhz) - 10.0 * np.log10(float(tasa_bps)))


def comparar_bandas(error_deg=OBJETIVO_DEG, diametro_m=DIAMETRO_PLATO_M,
                    bandas=(("S 2.2 GHz", 2.2e9), ("X 8.4 GHz", 8.4e9),
                            ("Ka 30 GHz", 30.0e9))):
    """El mismo error mecanico sobre el mismo plato, banda a banda.

    Devuelve lista de dicts con `nombre`, `theta3_deg`, `perdida_db` y
    `razon_haz` (que fraccion del haz se come el error). Es la cuenta
    que responde la pregunta del curso: 0.1 grados no describe una
    antena, describe una BANDA.
    """
    filas = []
    for nombre, f in bandas:
        th3 = ancho_haz(diametro_m, f)
        filas.append({"nombre": nombre, "f_hz": float(f),
                      "theta3_deg": th3,
                      "perdida_db": perdida_apuntamiento(error_deg, th3),
                      "razon_haz": float(float(error_deg) / th3)})
    return filas


def error_admisible(perdida_db, theta3_deg):
    """El error de apuntamiento (grados) que agota un presupuesto de
    `perdida_db`. Invierte la cuadratica: theta = theta3 sqrt(L/12).

    En Ka con este plato, admitir solo 0.1 dB exige ~0.02 grados -- y
    eso ya no lo da un rotor comercial.
    """
    return float(float(theta3_deg) * np.sqrt(float(perdida_db) / 12.0))


# =====================================================================
# 9. Piezas de dibujo
# =====================================================================
#
# Convenciones (las mismas de `apuntado.py`, que es el sustrato):
#   * Todo grupo nace centrado en ORIGIN salvo que se diga: `.move_to()`
#     normal para colocarlo.
#   * Las piezas que cambian exponen `.gemela(...)`, que construye una
#     copia de ESTRUCTURA IDENTICA con otros datos. Es la unica forma
#     legitima de hacerles `Transform`: dos piezas construidas por
#     separado casi nunca son gemelas y el Transform rompe glifos.
#   * Los localizadores (`.punto_en`, `.pivote`, `.cima`) se calculan
#     sobre la geometria ACTUAL, asi que siguen valiendo tras mover o
#     escalar el mobject.
#   * Nada de escalar el VGroup entero para que quepa: eso encoge la
#     letra. Se pasan `ancho`, `alto` y `fs`.

from manim import (Annulus, Arc, Circle, DashedLine, DashedVMobject,  # noqa: E402
                   AnnularSector, Dot, Line, Polygon, Rectangle,
                   RoundedRectangle, Text, VGroup, VMobject, ORIGIN, UP, DOWN,
                   LEFT, RIGHT, PI, TAU)

from code_brand import (CODE_BG, CODE_INK, CODE_MUTED, FUENTE_HUD,  # noqa: E402
                        registrar_fuentes)

MUESTRAS_MAX = 400      # tope duro de muestras de una curva parametrica


def _validar_muestras(nombre, muestras):
    m = int(muestras)
    if m < 8:
        raise ValueError(f"{nombre}: al menos 8 muestras, llegaron {m}")
    if m > MUESTRAS_MAX:
        raise ValueError(
            f"{nombre}: {m} muestras pasan del tope {MUESTRAS_MAX} "
            f"(el VPS tiene 2 vCPU). Baja la resolucion de la curva.")
    return m


def _hud(texto, font_size=15, color=C_EJE):
    """Rotulo de mobiliario en Space Mono (SOLO ASCII: la fuente no trae
    acentos ni griegas ni superindices)."""
    registrar_fuentes()
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size,
                color=color)


def _curva(puntos, color, grosor=3.0):
    v = VMobject()
    v.set_points_as_corners([np.asarray(p, dtype=float) for p in puntos])
    v.set_stroke(color=color, width=grosor)
    return v


def _ejes(ancho, alto, etiqueta_x=None, etiqueta_y=None, color=C_EJE,
          font_size=15):
    """Ejes minimos con origen abajo-izquierda, centrados en ORIGIN."""
    o = np.array([-ancho / 2.0, -alto / 2.0, 0.0])
    ex = Line(o, o + np.array([ancho, 0.0, 0.0]), stroke_width=2.4,
              color=color)
    ey = Line(o, o + np.array([0.0, alto, 0.0]), stroke_width=2.4,
              color=color)
    g = VGroup(ex, ey)
    if etiqueta_x:
        tx = _hud(etiqueta_x, font_size, color=CODE_MUTED)
        tx.next_to(ex, DOWN, buff=0.14).align_to(ex, RIGHT)
        g.add(tx)
    if etiqueta_y:
        ty = _hud(etiqueta_y, font_size, color=CODE_MUTED)
        ty.next_to(ey, UP, buff=0.14)
        g.add(ty)
    return g


# --- la montura de dos ejes -------------------------------------------

class Montura(VGroup):
    """Montura Az/El de perfil, con sus DOS ejes moviendose (la crea
    `montura`).

    `.apuntar(az_deg, el_deg)` gira el anillo de acimut y levanta el
    brazo de elevacion. `.saturar(True)` pone el eje de acimut en rojo,
    que es como se ve el keyhole en pantalla.

    `.pivote` es el punto de cruce de los dos ejes: la pieza es
    ASIMETRICA, asi que colocarla con `move_to` centra su bounding box y
    NO el pivote. Para anclarla por el pivote:
        m.shift(destino - m.pivote)

    OJO, VERRUGA CONOCIDA: `pivote`, `base_izq` y `base_der` son
    atributos FIJOS, guardados al construir, no propiedades calculadas
    sobre la geometria actual (a diferencia de `apuntado.AgujaVelocidad`,
    que si las calcula). Despues de un `shift` quedan desfasados, y
    `apuntar(az)` deja la marca del anillo donde la pieza NACIO. Dos
    salidas, las dos usadas en esta familia:
      * llamar a `apuntar()` ANTES de mover la pieza (lo hace el molde), o
      * arrastrar los tres atributos con el mismo delta tras el shift.
    No se convirtieron en propiedades a mitad de la produccion del curso
    30 porque varios clips ya compensaban a mano y el cambio los habria
    roto en silencio. Para la familia siguiente: conviene arreglarlo.
    """

    def apuntar(self, az_deg=None, el_deg=None):
        if el_deg is not None:
            el = float(np.clip(el_deg, 0.0, 90.0))
            delta = el - self._el
            if abs(delta) > 1e-9:
                self.brazo.rotate(np.radians(delta), about_point=self.pivote)
            self._el = el
        if az_deg is not None:
            az = float(az_deg)
            # el acimut se ve de perfil como un desplazamiento del anillo:
            # se representa girando la elipse de la base
            self._az = az
            frac = (np.cos(np.radians(az)) + 1.0) / 2.0
            self.marca_az.move_to(
                self.base_izq + (self.base_der - self.base_izq) * frac)
        return self

    def saturar(self, si=True):
        col = C_PELIGRO if si else C_CALCULO
        self.anillo.set_stroke(color=col)
        self.marca_az.set_color(col)
        return self

    @property
    def direccion(self):
        """Vector unitario en el que apunta el plato, AHORA."""
        v = self.plato.get_center() - self.pivote
        n = np.linalg.norm(v)
        return v / n if n > 1e-9 else RIGHT


def montura(alto=2.2, color=C_CALCULO, color_eje=C_EJE, font_size=15,
            etiquetas=True):
    """Montura Az/El de perfil: pedestal, anillo de acimut y brazo de
    elevacion con el plato en la punta.

    Nace apuntando a el = 30 grados. El grupo se centra en ORIGIN, pero
    para anclar por el cruce de ejes usa `.pivote` (ver `Montura`).
    """
    alto = float(max(0.8, alto))
    ancho = alto * 0.9

    base = Line(LEFT * ancho / 2.0, RIGHT * ancho / 2.0,
                stroke_width=3.4, color=color_eje)
    base.shift(DOWN * alto / 2.0)
    pedestal = Line(base.get_center(), base.get_center() + UP * alto * 0.42,
                    stroke_width=4.0, color=color_eje)
    pivote = pedestal.get_end()

    # el anillo de acimut, visto de perfil como una elipse aplastada
    anillo = Circle(radius=ancho * 0.30, color=color, stroke_width=2.6)
    anillo.stretch(0.26, dim=1)
    anillo.move_to(pivote)
    base_izq = pivote + LEFT * ancho * 0.30
    base_der = pivote + RIGHT * ancho * 0.30
    marca_az = Dot(base_der, radius=0.055, color=color)

    # el brazo de elevacion con el plato
    largo = alto * 0.46
    brazo_linea = Line(pivote, pivote + RIGHT * largo, stroke_width=4.0,
                       color=color)
    # El plato tiene que abrir HACIA AFUERA (+X) y APOYARSE en la punta
    # del brazo. Un Arc vive a `radius` de SU centro, asi que el centro
    # va UN RADIO MAS ALLA de la punta: entonces el punto del arco a
    # 180 grados cae justo en la punta y la concavidad mira afuera.
    # Puesto el centro EN la punta, el arco caia por detras y cruzaba el
    # brazo (salia una X); puesto con move_to, abria hacia el pivote.
    r_plato = largo * 0.46
    plato = Arc(radius=r_plato, start_angle=PI * 0.72,
                angle=PI * 0.56, color=color, stroke_width=4.0)
    plato.move_arc_center_to(pivote + RIGHT * (largo + r_plato))
    brazo = VGroup(brazo_linea, plato)
    brazo.rotate(np.radians(30.0), about_point=pivote)

    g = Montura(pedestal, base, anillo, marca_az, brazo)
    g.base, g.pedestal, g.anillo = base, pedestal, anillo
    g.marca_az, g.brazo = marca_az, brazo
    g.brazo_linea, g.plato = brazo_linea, plato
    g.pivote = np.array(pivote, dtype=float)
    g.base_izq = np.array(base_izq, dtype=float)
    g.base_der = np.array(base_der, dtype=float)
    g._el, g._az = 30.0, 0.0

    if etiquetas:
        # Los dos rotulos van pegados a SU eje y en carriles distintos:
        # Az bajo el anillo, El a la izquierda del pivote. Colgar El de
        # una altura fija lo dejaba flotando lejos del brazo.
        t_az = _hud("Az", font_size, color=CODE_MUTED)
        t_az.next_to(anillo, DOWN, buff=0.09)
        t_el = _hud("El", font_size, color=CODE_MUTED)
        t_el.move_to(pivote + LEFT * (ancho * 0.30) + UP * 0.20)
        g.add(t_az, t_el)
        g.t_az, g.t_el = t_az, t_el
    return g


# --- el error contra el tiempo, con su banda de presupuesto -----------

class TrazaError(VGroup):
    """Error de apuntamiento contra tiempo, con la banda del presupuesto
    YA dibujada (la crea `traza_error`).

    El presupuesto se VE: cuando la curva se sale, se sale por encima de
    una linea que ya estaba ahi. `.gemela(error)` da una pieza de
    estructura identica con otra curva, apta para `Transform`.
    """

    def gemela(self, error, color=None):
        return traza_error(self._t, error, ancho=self._ancho,
                           alto=self._alto, umbral=self._umbral,
                           y_max=self._y_max, font_size=self._fs,
                           color=self._color if color is None else color,
                           etiqueta_x=self._ex, etiqueta_y=self._ey)

    def punto_en(self, frac):
        """Punto de la curva a la fraccion `frac` del eje de tiempo."""
        pts = self.curva.get_points()
        i = int(np.clip(frac, 0.0, 1.0) * (len(pts) - 1))
        return np.array(pts[i], dtype=float)


def traza_error(t, error, ancho=5.8, alto=2.4, umbral=OBJETIVO_DEG,
                y_max=None, color=C_SAT, font_size=15, muestras=200,
                etiqueta_x="t", etiqueta_y="error"):
    """Curva de error con la banda de +-`umbral` sombreada en cian.

    `y_max` fija la escala vertical; si se omite se toma el mayor entre
    el pico del error y 1.6 veces el umbral, para que la banda siempre
    se vea aunque el error sea diminuto.
    """
    t = np.asarray(t, dtype=float)
    error = np.asarray(error, dtype=float)
    muestras = _validar_muestras("traza_error", min(muestras, len(t)))
    idx = np.linspace(0, len(t) - 1, muestras).astype(int)
    tt, ee = t[idx], error[idx]

    # Con un error muy por dentro del presupuesto (el caso del PID bien
    # sintonizado: 0.004 frente a 0.1) la banda se comia el dibujo y la
    # curva quedaba aplastada en el centro. Se deja el umbral cerca del
    # techo, y un clip que quiera ampliar la curva pasa `y_max` a mano.
    pico = float(np.max(np.abs(ee))) if len(ee) else umbral
    y_max = float(y_max) if y_max else max(pico * 1.30, umbral * 1.12)
    o = np.array([-ancho / 2.0, 0.0, 0.0])

    def punto(ti, ei):
        fx = (ti - tt[0]) / max(tt[-1] - tt[0], 1e-12)
        return o + np.array([fx * ancho, ei / y_max * (alto / 2.0), 0.0])

    # El eje x se sube al CERO del error, asi que su etiqueta NO puede
    # colgar del eje: quedaba dentro de la banda del presupuesto.
    ejes = _ejes(ancho, alto, None, etiqueta_y, font_size=font_size)
    ejes.shift(UP * alto / 2.0)
    cero = Line(o, o + RIGHT * ancho, stroke_width=1.6, color=C_EJE)

    h_banda = umbral / y_max * (alto / 2.0)
    banda = Rectangle(width=ancho, height=2.0 * h_banda,
                      stroke_width=0, fill_color=C_CALCULO,
                      fill_opacity=0.14)
    banda.move_to(o + RIGHT * ancho / 2.0)
    borde_sup = DashedVMobject(
        Line(o + UP * h_banda, o + RIGHT * ancho + UP * h_banda,
             stroke_width=1.8, color=C_CALCULO), num_dashes=42)
    borde_inf = DashedVMobject(
        Line(o + DOWN * h_banda, o + RIGHT * ancho + DOWN * h_banda,
             stroke_width=1.8, color=C_CALCULO), num_dashes=42)

    curva = _curva([punto(a, b) for a, b in zip(tt, ee)], color, 3.0)

    if etiqueta_x:
        tx = _hud(etiqueta_x, font_size, color=CODE_MUTED)
        tx.move_to(o + RIGHT * ancho + DOWN * 0.28)
        ejes.add(tx)

    g = TrazaError(banda, borde_sup, borde_inf, cero, ejes, curva)
    g.banda, g.curva, g.ejes = banda, curva, ejes
    g.borde_sup, g.borde_inf, g.cero = borde_sup, borde_inf, cero
    g._t, g._ancho, g._alto = t, ancho, alto
    g._umbral, g._y_max, g._fs, g._color = umbral, y_max, font_size, color
    g._ex, g._ey = etiqueta_x, etiqueta_y
    g.y_max = y_max
    g.origen = o
    return g


# --- el histograma con su p95 -----------------------------------------

class Histograma(VGroup):
    """Histograma de una campaña con su p95 en ambar y el umbral en cian
    (lo crea `histograma`).

    `.gemela(muestras)` mantiene el MISMO numero de barras (`bins`) y la
    misma escala, que es lo que hace legitimo el `Transform`. Dos
    histogramas con distinto numero de barras NO son gemelos.
    """

    def gemela(self, muestras):
        return histograma(muestras, bins=self._bins, ancho=self._ancho,
                          alto=self._alto, umbral=self._umbral,
                          x_max=self._x_max, font_size=self._fs)

    def barra(self, i):
        return self.barras[i]


def histograma(muestras, bins=26, ancho=5.6, alto=2.3, umbral=OBJETIVO_DEG,
               x_max=None, font_size=15, color=C_CIELO):
    """Barras del histograma, con la linea del p95 (ambar) y la del
    umbral de aceptacion (cian)."""
    m = np.asarray(muestras, dtype=float)
    x_max = float(x_max) if x_max else float(max(np.max(m), umbral * 1.35))
    conteo, bordes = np.histogram(m, bins=int(bins), range=(0.0, x_max))
    alturas = conteo / max(1, conteo.max())
    o = np.array([-ancho / 2.0, -alto / 2.0, 0.0])
    w = ancho / float(bins)

    barras = VGroup()
    for i, h in enumerate(alturas):
        b = Rectangle(width=w * 0.86, height=max(float(h) * alto, 1e-3),
                      stroke_width=0, fill_color=color, fill_opacity=0.75)
        b.move_to(o + RIGHT * (i + 0.5) * w
                  + UP * max(float(h) * alto, 1e-3) / 2.0)
        barras.add(b)

    ejes = _ejes(ancho, alto, "error RMS", None, font_size=font_size)

    def x_de(v):
        return o + RIGHT * float(np.clip(v / x_max, 0.0, 1.0)) * ancho

    p95 = float(np.percentile(m, 95))
    l_p95 = DashedVMobject(Line(x_de(p95), x_de(p95) + UP * alto,
                                stroke_width=2.6, color=C_SAT),
                           num_dashes=16)
    l_umb = DashedVMobject(Line(x_de(umbral), x_de(umbral) + UP * alto,
                                stroke_width=2.6, color=C_CALCULO),
                           num_dashes=16)
    t_p95 = _hud("p95", font_size, color=C_SAT)
    t_umb = _hud(f"{umbral:g} deg", font_size, color=C_CALCULO)
    # Cuando el diseño pasa por los pelos, p95 y umbral caen casi en la
    # MISMA x y los dos rotulos se escriben uno encima del otro (paso:
    # "0.1 deg" y "p95" salieron superpuestos e ilegibles). Si estan
    # cerca se reparten en dos carriles y se alinean por fuera.
    juntos = abs(p95 - umbral) / max(x_max, 1e-9) < 0.12
    if juntos:
        t_p95.next_to(l_p95, UP, buff=0.10).shift(LEFT * 0.30)
        t_umb.next_to(l_umb, UP, buff=0.10).shift(
            RIGHT * 0.34 + UP * (t_p95.height + 0.10))
    else:
        t_p95.next_to(l_p95, UP, buff=0.10)
        t_umb.next_to(l_umb, UP, buff=0.10)

    g = Histograma(ejes, barras, l_umb, t_umb, l_p95, t_p95)
    g.barras, g.ejes = barras, ejes
    g.linea_p95, g.linea_umbral = l_p95, l_umb
    g.tag_p95, g.tag_umbral = t_p95, t_umb
    g._bins, g._ancho, g._alto = int(bins), ancho, alto
    g._umbral, g._x_max, g._fs = umbral, x_max, font_size
    g.p95, g.x_max, g.origen = p95, x_max, o
    return g


# --- el presupuesto de error en cuadratura ----------------------------

class Presupuesto(VGroup):
    """Barras de las contribuciones al error y la barra del total en
    cuadratura, con el objetivo dibujado (lo crea `presupuesto_barras`).

    Ensena de un vistazo lo que ensena la cuadratura: el termino grande
    manda. `.gemela(terminos)` conserva el NUMERO de barras.
    """

    def gemela(self, terminos):
        if len(terminos) != self._n:
            raise ValueError(
                f"Presupuesto.gemela: la gemela necesita las MISMAS "
                f"{self._n} barras y le llegaron {len(terminos)}. Dos "
                f"presupuestos con distinto numero de terminos no son "
                f"gemelos: dibujalos como dos piezas.")
        return presupuesto_barras(terminos, ancho=self._ancho,
                                  alto=self._alto, objetivo=self._obj,
                                  font_size=self._fs, y_max=self._y_max)


def presupuesto_barras(terminos, ancho=5.4, alto=2.3, objetivo=OBJETIVO_DEG,
                       font_size=15, y_max=None):
    """`terminos` es un dict nombre -> grados. Dibuja una barra por
    termino (gris), la barra del TOTAL en cuadratura (cian si cabe bajo
    el objetivo, rojo si no) y la linea del objetivo."""
    nombres = list(terminos.keys())
    vals = [float(terminos[k]) for k in nombres]
    total = float(np.sqrt(np.sum(np.square(vals))))
    y_max = float(y_max) if y_max else max(max(vals + [total]),
                                           objetivo) * 1.35
    n = len(nombres) + 1
    o = np.array([-ancho / 2.0, -alto / 2.0, 0.0])
    w = ancho / n
    i_dom = int(np.argmax(vals))

    barras, rotulos = VGroup(), VGroup()
    for i, (nom, v) in enumerate(zip(nombres, vals)):
        h = max(v / y_max * alto, 1e-3)
        col = C_SAT if i == i_dom else CODE_MUTED
        b = Rectangle(width=w * 0.6, height=h, stroke_width=0,
                      fill_color=col, fill_opacity=0.85)
        b.move_to(o + RIGHT * (i + 0.5) * w + UP * h / 2.0)
        barras.add(b)
        t = _hud(nom[:9], font_size - 1, color=CODE_MUTED)
        t.next_to(b, DOWN, buff=0.10)
        rotulos.add(t)

    cabe = total <= objetivo
    h_t = max(total / y_max * alto, 1e-3)
    b_tot = Rectangle(width=w * 0.6, height=h_t, stroke_width=0,
                      fill_color=C_CALCULO if cabe else C_PELIGRO,
                      fill_opacity=0.95)
    b_tot.move_to(o + RIGHT * (n - 0.5) * w + UP * h_t / 2.0)
    barras.add(b_tot)
    t_tot = _hud("TOTAL", font_size - 1,
                 color=C_CALCULO if cabe else C_PELIGRO)
    t_tot.next_to(b_tot, DOWN, buff=0.10)
    rotulos.add(t_tot)

    h_obj = objetivo / y_max * alto
    l_obj = DashedVMobject(Line(o + UP * h_obj,
                                o + RIGHT * ancho + UP * h_obj,
                                stroke_width=2.4, color=C_CALCULO),
                           num_dashes=34)
    ejes = _ejes(ancho, alto, None, "deg", font_size=font_size)

    g = Presupuesto(ejes, barras, rotulos, l_obj)
    g.barras, g.rotulos, g.linea_objetivo, g.ejes = barras, rotulos, l_obj, ejes
    g.barra_total, g.total, g.cabe = b_tot, total, cabe
    g.dominante = nombres[i_dom]
    g._n, g._ancho, g._alto = len(nombres), ancho, alto
    g._obj, g._fs, g._y_max = objetivo, font_size, y_max
    return g


# --- el haz de la antena ----------------------------------------------

class Haz(VGroup):
    """Cono de media potencia con el satelite dentro o fuera (lo crea
    `haz`). `.gemela(theta3, error)` conserva la estructura."""

    def gemela(self, theta3_deg, error_deg=None):
        return haz(theta3_deg,
                   self._err if error_deg is None else error_deg,
                   largo=self._largo, font_size=self._fs,
                   escala_ang=self._esc)


def haz(theta3_deg, error_deg=OBJETIVO_DEG, largo=3.0, font_size=15,
        escala_ang=None, color=C_CALCULO):
    """El haz como sector, con la marca del satelite desviada
    `error_deg` del eje.

    `escala_ang` es grados de haz por radian dibujado: se pasa el MISMO
    valor a dos haces que se vayan a comparar, o el de Ka (0.23 grados)
    saldria del tamano del de S (3.18) y la comparacion mentiria. Si se
    omite, se ajusta para que este haz ocupe 40 grados en pantalla.
    """
    th = float(theta3_deg)
    err = float(error_deg)
    esc = float(escala_ang) if escala_ang else (th / 40.0)
    ang_dib = np.radians(th / esc)          # apertura dibujada, rad
    err_dib = np.radians(err / esc)

    vertice = LEFT * largo / 2.0
    # AnnularSector con radio interior 0: `Sector` cambio de firma
    # (ya no acepta outer_radius) y revienta en esta version de manim.
    sector = AnnularSector(inner_radius=0.0, outer_radius=largo,
                           angle=ang_dib, start_angle=-ang_dib / 2.0,
                           fill_color=color, fill_opacity=0.18,
                           stroke_width=0)
    sector.move_arc_center_to(vertice)
    borde_a = Line(vertice, vertice + np.array(
        [np.cos(ang_dib / 2.0), np.sin(ang_dib / 2.0), 0.0]) * largo,
        stroke_width=2.0, color=color)
    borde_b = Line(vertice, vertice + np.array(
        [np.cos(-ang_dib / 2.0), np.sin(-ang_dib / 2.0), 0.0]) * largo,
        stroke_width=2.0, color=color)
    eje = DashedVMobject(Line(vertice, vertice + RIGHT * largo,
                              stroke_width=1.6, color=CODE_MUTED),
                         num_dashes=24)

    dentro = abs(err) <= th / 2.0
    pos = vertice + np.array([np.cos(err_dib), np.sin(err_dib), 0.0]) * largo
    sat = Dot(pos, radius=0.075, color=C_SAT if dentro else C_PELIGRO)

    g = Haz(sector, borde_a, borde_b, eje, sat)
    g.sector, g.eje, g.satelite = sector, eje, sat
    g.bordes = VGroup(borde_a, borde_b)
    g.vertice = np.array(vertice, dtype=float)
    g.dentro, g.theta3, g.escala_ang = dentro, th, esc
    g._largo, g._fs, g._esc, g._err = largo, font_size, esc, err
    return g


# --- el compromiso Q / R ----------------------------------------------

def plano_qr(qs=(1.0, 10.0, 100.0, 1000.0, 10000.0), r=1.0, ancho=5.2,
             alto=2.4, font_size=15):
    """La curva del compromiso: wn del lazo contra la relacion q/r, en
    escala logaritmica, con la nota de que zeta se queda en 0.707 pase
    lo que pase.

    Devuelve un VGroup con `.curva`, `.ejes` y `.puntos` (un Dot por
    cada q), y `.punto_en(i)` para colgarles etiquetas.
    """
    qs = list(qs)
    wns = [lqr_doble_integrador(q, r)["wn"] for q in qs]
    lx = np.log10(np.array(qs) / float(r))
    o = np.array([-ancho / 2.0, -alto / 2.0, 0.0])
    lx_min, lx_max = float(lx.min()), float(lx.max())
    wn_max = float(max(wns)) * 1.1

    def punto(a, b):
        fx = (a - lx_min) / max(lx_max - lx_min, 1e-12)
        return o + np.array([fx * ancho, b / wn_max * alto, 0.0])

    pts = [punto(a, b) for a, b in zip(lx, wns)]
    curva = _curva(pts, C_CALCULO, 3.0)
    ejes = _ejes(ancho, alto, "q/r  (log)", "wn", font_size=font_size)
    puntos = VGroup(*[Dot(p, radius=0.055, color=C_SAT) for p in pts])

    g = VGroup(ejes, curva, puntos)
    g.curva, g.ejes, g.puntos = curva, ejes, puntos
    g.valores = list(zip(qs, wns))
    g.punto_en = lambda i: np.array(pts[int(i)], dtype=float)
    return g


# --- la cadena de marcos ----------------------------------------------

class Cadena(VGroup):
    """Cadena de eslabones con uno ENCENDIDO (la crea `cadena`).

    `.encender(i)` apaga todos y enciende el i-esimo; devuelve la lista
    de mobjects que cambiaron, por si el clip quiere animarlos.
    """

    def encender(self, i):
        for k, (caja, txt) in enumerate(zip(self.cajas, self.textos)):
            activo = (k == int(i))
            caja.set_stroke(color=C_CALCULO if activo else C_EJE,
                            width=2.6 if activo else 1.8)
            caja.set_fill(color=C_CALCULO,
                          opacity=0.16 if activo else 0.0)
            txt.set_color(CODE_INK if activo else CODE_MUTED)
        return self

    def caja_en(self, i):
        return self.cajas[int(i)]


def cadena(etiquetas=("TLE", "SGP4", "ECI", "ECEF", "ENU", "Az/El"),
           ancho_caja=1.28, alto_caja=0.62, buff=0.30, font_size=17):
    """La cadena de marcos de referencia, en fila y con flechas.

    Nace con todos los eslabones apagados: llama a `.encender(i)`.
    """
    cajas, textos, flechas = VGroup(), VGroup(), VGroup()
    total = len(etiquetas) * ancho_caja + (len(etiquetas) - 1) * buff
    x = -total / 2.0 + ancho_caja / 2.0
    for et in etiquetas:
        c = RoundedRectangle(width=ancho_caja, height=alto_caja,
                             corner_radius=0.10, stroke_width=1.8,
                             color=C_EJE)
        c.set_fill(color=C_CALCULO, opacity=0.0)
        c.move_to(RIGHT * x)
        t = _hud(et, font_size, color=CODE_MUTED)
        t.move_to(c.get_center())
        cajas.add(c)
        textos.add(t)
        x += ancho_caja + buff
    for a, b in zip(cajas[:-1], cajas[1:]):
        f = Line(a.get_right(), b.get_left(), stroke_width=2.0,
                 color=C_EJE, buff=0.06)
        f.add_tip(tip_length=0.14)
        flechas.add(f)

    g = Cadena(flechas, cajas, textos)
    g.cajas, g.textos, g.flechas = cajas, textos, flechas
    return g


# --- barras de comparacion genericas ----------------------------------

def barras_comparar(valores, etiquetas, ancho=5.4, alto=2.2, font_size=15,
                    colores=None, log=False, unidad=""):
    """Barras para comparar magnitudes muy dispares (viento contra
    inercia, Doppler por banda).

    `log=True` dibuja el logaritmo: OBLIGATORIO cuando la razon pasa de
    ~20, o la barra pequena queda de un pixel y no se lee. Cuando se usa
    log, la pieza lo dice en su `.nota` para que el clip lo rotule --
    una comparacion en log que se presente como lineal miente.
    """
    vals = np.asarray([float(v) for v in valores], dtype=float)
    if log:
        base = np.log10(np.maximum(vals, 1e-12))
        base = base - base.min() + 0.35
    else:
        base = vals.copy()
    top = float(base.max()) if base.max() > 0 else 1.0
    n = len(vals)
    o = np.array([-ancho / 2.0, -alto / 2.0, 0.0])
    w = ancho / n
    if colores is None:
        colores = [C_CALCULO] * n

    barras, rotulos = VGroup(), VGroup()
    for i in range(n):
        h = max(float(base[i]) / top * alto, 1e-3)
        b = Rectangle(width=w * 0.58, height=h, stroke_width=0,
                      fill_color=colores[i % len(colores)], fill_opacity=0.85)
        b.move_to(o + RIGHT * (i + 0.5) * w + UP * h / 2.0)
        barras.add(b)
        t = _hud(str(etiquetas[i])[:11], font_size - 1, color=CODE_MUTED)
        t.next_to(b, DOWN, buff=0.10)
        rotulos.add(t)

    ejes = _ejes(ancho, alto, None, unidad or None, font_size=font_size)
    g = VGroup(ejes, barras, rotulos)
    # Una comparacion en log presentada como lineal MIENTE: dos barras
    # cuya razon real es 425 salen en 8.5 a 1. El aviso no se deja a que
    # el clip se acuerde de ponerlo, lo trae la pieza.
    if log:
        nota = _hud("escala log", font_size - 2, color=CODE_MUTED)
        nota.next_to(ejes, UP, buff=0.10).align_to(ejes, RIGHT)
        g.add(nota)
        g.tag_log = nota
    g.barras, g.rotulos, g.ejes = barras, rotulos, ejes
    g.valores = vals
    g.nota = "escala log" if log else ""
    g.cima_de = lambda i: np.array(barras[int(i)].get_top(), dtype=float)
    return g
