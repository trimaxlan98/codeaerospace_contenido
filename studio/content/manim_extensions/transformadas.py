# =====================================================================
# CO.DE Academy - transformadas.py
# La libreria del curso 32: dieciocho transformadas, en estilo LIENZO.
#
# Dos mitades, como en esp32.py:
#
#   1. NUMERICA. numpy puro, sin manim. Aqui viven TODAS las cifras que
#      salen en pantalla. Ninguna se escribe a mano en un clip. Se puede
#      importar en el contenedor sin manim (lo hace la sonda), y por eso
#      los imports de manim van detras de `_HAY_MANIM`.
#   2. DE DIBUJO. Las piezas que los clips componen. Todo con trazo y
#      relleno cero: en el curso 31 quedo medido que el ambar traslucido
#      sobre este azul da verde oliva (72,62,45 al 26 %), asi que en este
#      estilo el acento es TRAZO, nunca masa.
#
# La regla de honestidad de la casa, que aqui aprieta especialmente porque
# el curso no tiene voz: la CIFRA es lo que este render calculo. Si un
# numero es un PARAMETRO elegido (el orden de un filtro, el numero de
# muestras, la semilla) su etiqueta va en APAGADO, no en ambar. Un
# parametro no es una medida por mucho que este en el codigo.
#
# Determinismo: todo lo aleatorio pasa por `default_rng(SEMILLA)`. Dos
# renders de la misma pieza dan el mismo pixel y la misma cifra.
# =====================================================================
import numpy as np

SEMILLA = 32              # el numero del curso, para no elegirlo dos veces

try:
    from manim import (DOWN, LEFT, RIGHT, UP, Arrow, Circle, DashedVMobject,
                       Dot, Group, ImageMobject, Line, Rectangle,
                       RESAMPLING_ALGORITHMS, VGroup, VMobject)

    import lienzo as _lz
    _HAY_MANIM = True
except Exception:          # la sonda corre sin manim
    _HAY_MANIM = False


# =====================================================================
#  MITAD NUMERICA
# =====================================================================

# --- 01 · Serie de Fourier -------------------------------------------
def serie_cuadrada(n_armonicos, N=4096, periodos=1.0):
    """Suma parcial de la serie de Fourier de una onda cuadrada impar.

    x(t) = (4/pi) * sum_{k impar <= n} sin(2 pi k t) / k

    Devuelve (t, suma, cuadrada). La cuadrada vale +-1, asi que el
    sobreimpulso se lee directamente como exceso sobre 1."""
    t = np.linspace(0.0, float(periodos), int(N), endpoint=False)
    suma = np.zeros_like(t)
    for k in range(1, int(n_armonicos) + 1, 2):
        suma += np.sin(2.0 * np.pi * k * t) / k
    suma *= 4.0 / np.pi
    cuadrada = np.sign(np.sin(2.0 * np.pi * t))
    cuadrada[cuadrada == 0] = 1.0
    return t, suma, cuadrada


def gibbs_por_ciento(n_armonicos, N=8192):
    """El sobreimpulso de la suma parcial, en % del SALTO.

    La cuenta se hace sobre el salto (que vale 2: de -1 a +1) y no sobre
    la amplitud, que es la convencion con la que la constante de Gibbs es
    el 8.95 % que cita todo el mundo. Medido sobre la amplitud saldria el
    doble, 17.9 %, y seria un numero correcto que nadie reconoce. Lo cazo
    la sonda comparando con la constante.

    Es LA cifra de la pieza 01 porque NO baja: con 5 armonicos vale ~9 % y
    con 401 tambien. Lo que se encoge es su anchura, no su altura."""
    _, suma, _ = serie_cuadrada(n_armonicos, N=N)
    salto = 2.0
    return (float(np.max(suma)) - 1.0) / salto * 100.0


def error_rms_cuadrada(n_armonicos, N=8192):
    """Error cuadratico medio entre la suma parcial y la cuadrada."""
    _, suma, cuad = serie_cuadrada(n_armonicos, N=N)
    return float(np.sqrt(np.mean((suma - cuad) ** 2)))


# --- 02 · Transformada de Fourier ------------------------------------
def pulso_y_espectro(ancho, T=8.0, N=4096):
    """Un pulso rectangular de `ancho` segundos y su espectro.

    Devuelve (t, x, f, mag) con `mag` normalizada a 1. El espectro de un
    rectangulo es un sinc cuyo PRIMER NULO cae en 1/ancho: esa es la
    relacion que la pieza mide en vez de afirmarla."""
    t = np.linspace(-T / 2, T / 2, int(N), endpoint=False)
    x = (np.abs(t) < ancho / 2).astype(float)
    dt = t[1] - t[0]
    X = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(x))) * dt
    f = np.fft.fftshift(np.fft.fftfreq(int(N), d=dt))
    mag = np.abs(X)
    mag /= max(np.max(mag), 1e-12)
    return t, x, f, mag


def primer_nulo(f, mag, corte=0.2):
    """La frecuencia del primer cero del espectro, MEDIDA sobre la malla.

    Se busca el primer MINIMO LOCAL por debajo de `corte` veces el pico,
    no el primer punto que baje de un umbral absoluto. La primera version
    usaba un umbral de 1e-3 y devolvia 42.9 Hz para un pulso de 1 s: en
    una malla discreta el nulo del sinc casi nunca cae exactamente sobre
    una muestra, asi que no hay ningun punto tan bajo cerca del nulo de
    verdad y la busqueda se iba a vagar por el ruido numerico de lejos.
    El producto tiempo-banda salia 42.9 en vez de 1.

    Se devuelve la POSICION y no la profundidad: la profundidad de un
    nulo depende de la malla y la posicion no (leccion del curso 27)."""
    centro = int(np.argmax(mag))
    tope = float(np.max(mag)) * float(corte)
    for i in range(centro + 1, len(mag) - 1):
        if mag[i] < tope and mag[i] <= mag[i - 1] and mag[i] <= mag[i + 1]:
            return float(abs(f[i]))
    raise ValueError("no se encontro el primer nulo: sube el corte")


def producto_tiempo_banda(ancho, T=8.0, N=4096):
    """ancho_del_pulso x primer_nulo_del_espectro. Vale 1 y no cambia.

    Es el corazon de la pieza 02: estrechar el pulso ensancha el espectro
    en la misma proporcion, asi que el producto es invariante."""
    _, _, f, mag = pulso_y_espectro(ancho, T=T, N=N)
    return float(ancho) * primer_nulo(f, mag)


# --- 03 · DFT y la fuga espectral -------------------------------------
def dft_tono(k, N=64):
    """|DFT| de un tono de k ciclos por ventana, normalizada a 1.

    Con k entero el tono cabe un numero exacto de veces en la ventana y
    el espectro es UNA raya. Con k=8.5 no cabe, la ventana lo corta a
    mitad de ciclo y la energia se derrama por todos los bins: eso es la
    fuga espectral, y es la razon de que existan las ventanas."""
    n = np.arange(int(N))
    x = np.cos(2.0 * np.pi * float(k) * n / N)
    mag = np.abs(np.fft.rfft(x))
    return mag / max(np.max(mag), 1e-12)


def bins_encendidos(mag, umbral=0.01):
    """Cuantos bins pasan del `umbral` (fraccion del maximo)."""
    return int(np.sum(mag >= float(umbral)))


# --- 04 · FFT ---------------------------------------------------------
def coste_dft(N):
    """Multiplicaciones complejas de la DFT directa: N^2."""
    return int(N) ** 2


def coste_fft(N):
    """Multiplicaciones complejas de la FFT radix-2: (N/2) log2 N.

    Es el numero de MARIPOSAS, que es lo que se dibuja en la pieza. La
    cuenta habitual "N log2 N" cuenta sumas y productos juntos; aqui se
    cuenta lo mismo en los dos lados para que el cociente signifique
    algo."""
    N = int(N)
    if N & (N - 1):
        raise ValueError(f"N={N} no es potencia de dos")
    return (N // 2) * int(np.log2(N))


def ahorro_fft(N):
    """Cuantas veces menos cuentas hace la FFT. Para N=4096 son 682."""
    return coste_dft(N) / coste_fft(N)


def niveles_fft(N):
    """log2(N): las veces que la malla se parte por la mitad."""
    return int(np.log2(int(N)))


# --- 05 · DCT ---------------------------------------------------------
def _dct1(x):
    """DCT-II ortonormal de un vector, via FFT de la señal reflejada."""
    x = np.asarray(x, dtype=float)
    N = x.size
    v = np.concatenate([x, x[::-1]])
    V = np.fft.fft(v)[:N]
    k = np.arange(N)
    X = np.real(V * np.exp(-1j * np.pi * k / (2 * N)))
    X[0] *= np.sqrt(1.0 / (4 * N))
    X[1:] *= np.sqrt(1.0 / (2 * N))
    return X


def dct2(bloque):
    """DCT-II ortonormal 2D: por filas y luego por columnas."""
    b = np.apply_along_axis(_dct1, 1, np.asarray(bloque, dtype=float))
    return np.apply_along_axis(_dct1, 0, b)


def _idct1(X):
    X = np.asarray(X, dtype=float)
    N = X.size
    n = np.arange(N)
    base = np.cos(np.pi * (2 * n[None, :] + 1) * n[:, None] / (2 * N))
    peso = np.full(N, np.sqrt(2.0 / N))
    peso[0] = np.sqrt(1.0 / N)
    return (X * peso) @ base


def idct2(C):
    b = np.apply_along_axis(_idct1, 0, np.asarray(C, dtype=float))
    return np.apply_along_axis(_idct1, 1, b)


def bloque_ejemplo(n=8):
    """El bloque 8x8 de la pieza 05: un degradado con un borde suave.

    No es ruido ni una foto: es el caso que hace que la DCT brille, un
    trozo de imagen donde casi todo varia despacio. Elegido, no medido —
    su etiqueta va en apagado."""
    y, x = np.mgrid[0:n, 0:n] / (n - 1.0)
    campo = 0.55 + 0.35 * np.cos(np.pi * x * 0.9) - 0.18 * y
    campo += 0.12 * np.tanh(6.0 * (x + 0.35 * y - 0.75))
    campo += 0.05 * np.cos(np.pi * (2.6 * x + 1.7 * y))
    return campo


def energia_en_mayores(bloque, cuantos):
    """Fraccion de energia que guardan los `cuantos` mayores coeficientes.

    Se mide sobre la DCT del bloque. La DCT es ortonormal, asi que la
    suma de cuadrados de los coeficientes ES la energia de la imagen
    (Parseval) y la fraccion significa exactamente lo que parece."""
    C = dct2(bloque)
    plano = np.sort(np.abs(C).ravel())[::-1]
    total = float(np.sum(plano ** 2))
    return float(np.sum(plano[:int(cuantos)] ** 2) / max(total, 1e-18))


def reconstruir_con(bloque, cuantos):
    """El bloque rehecho con solo los `cuantos` mayores coeficientes."""
    C = dct2(bloque)
    umbral = np.sort(np.abs(C).ravel())[::-1][int(cuantos) - 1]
    return idct2(np.where(np.abs(C) >= umbral, C, 0.0))


# --- 06 · Hartley -----------------------------------------------------
def dht(x):
    """Transformada de Hartley discreta. Real entra, real sale.

    H[k] = sum x[n] (cos + sin)(2 pi k n / N). Se calcula con la FFT:
    H = Re(X) - Im(X), que es exacto y no una aproximacion."""
    X = np.fft.fft(np.asarray(x, dtype=float))
    return np.real(X) - np.imag(X)


def espectro_desde_hartley(H):
    """|X[k]| reconstruido a partir SOLO de los numeros reales de Hartley.

    |X[k]|^2 = (H[k]^2 + H[N-k]^2) / 2. Es la prueba de la pieza 06: la
    informacion completa estaba en la mitad de numeros."""
    H = np.asarray(H, dtype=float)
    N = H.size
    Hr = H[(-np.arange(N)) % N]
    return np.sqrt((H ** 2 + Hr ** 2) / 2.0)


def error_hartley(x):
    """Diferencia maxima entre |FFT| y el espectro sacado de Hartley.

    Sale del orden de 1e-13: no es que se parezcan, es que son el mismo
    numero salvo el redondeo del coma flotante."""
    x = np.asarray(x, dtype=float)
    return float(np.max(np.abs(np.abs(np.fft.fft(x))
                               - espectro_desde_hartley(dht(x)))))


def señal_ejemplo(N=1024, semilla=SEMILLA):
    """Señal de prueba comun a las piezas 06 y 07: tres tonos y un poco
    de ruido. Los tres tonos son parametros elegidos (apagado); lo que se
    mide es lo que las transformadas hacen con ellos."""
    rng = np.random.default_rng(semilla)
    n = np.arange(int(N))
    x = (1.00 * np.sin(2 * np.pi * 5 * n / N)
         + 0.50 * np.sin(2 * np.pi * 17 * n / N)
         + 0.25 * np.sin(2 * np.pi * 41 * n / N))
    return x + 0.05 * rng.standard_normal(int(N))


def memoria_real_vs_compleja(N):
    """Numeros que hay que guardar: DFT compleja vs Hartley real.

    La DFT de una señal real de N muestras son N numeros complejos = 2N
    reales; Hartley son N reales. Factor 2, exacto."""
    return 2 * int(N), int(N)


# --- 07 · Walsh-Hadamard ----------------------------------------------
def hadamard(N):
    """Matriz de Hadamard por la construccion de Sylvester (+-1)."""
    N = int(N)
    if N & (N - 1):
        raise ValueError(f"N={N} no es potencia de dos")
    H = np.array([[1.0]])
    while H.shape[0] < N:
        H = np.block([[H, H], [H, -H]])
    return H


def orden_secuencial(N):
    """El orden de Walsh (por numero de cambios de signo, la 'secuencia').

    Es lo que hace comparable la base de Walsh con la de Fourier: las
    filas quedan ordenadas de menos a mas oscilante, igual que los
    armonicos."""
    H = hadamard(N)
    cambios = np.sum(np.abs(np.diff(np.sign(H), axis=1)) > 0, axis=1)
    return np.argsort(cambios, kind="stable")


def fwht(x):
    """Walsh-Hadamard rapida, en el sitio. SOLO sumas y restas."""
    a = np.array(x, dtype=float, copy=True)
    N = a.size
    if N & (N - 1):
        raise ValueError(f"N={N} no es potencia de dos")
    h = 1
    while h < N:
        for i in range(0, N, h * 2):
            u = a[i:i + h].copy()
            v = a[i + h:i + 2 * h].copy()
            a[i:i + h] = u + v
            a[i + h:i + 2 * h] = u - v
        h *= 2
    return a


def coste_wht(N):
    """(sumas, multiplicaciones) de la WHT rapida. Las segundas son CERO,
    y esa es toda la pieza 07."""
    N = int(N)
    return N * int(np.log2(N)), 0


# --- 08 · Laplace -----------------------------------------------------
def polos_segundo_orden(wn=1.0, z=0.5):
    """Los dos polos de wn^2 / (s^2 + 2 z wn s + wn^2)."""
    wd = wn * np.sqrt(max(1.0 - z * z, 0.0))
    return np.array([complex(-z * wn, wd), complex(-z * wn, -wd)])


def escalon_segundo_orden(wn=1.0, z=0.5, T=20.0, N=4000):
    """Respuesta al escalon, integrada numericamente (Runge-Kutta 4).

    Se integra en vez de usar la formula cerrada a proposito: la pieza
    enseña que los POLOS predicen la forma, y para que eso sea una
    prediccion comprobada la respuesta tiene que venir de otro sitio."""
    t = np.linspace(0.0, float(T), int(N))
    h = t[1] - t[0]

    def f(_, y):
        return np.array([y[1], wn * wn * (1.0 - y[0]) - 2 * z * wn * y[1]])

    y = np.zeros((int(N), 2))
    for i in range(int(N) - 1):
        k1 = f(t[i], y[i])
        k2 = f(t[i] + h / 2, y[i] + h / 2 * k1)
        k3 = f(t[i] + h / 2, y[i] + h / 2 * k2)
        k4 = f(t[i] + h, y[i] + h * k3)
        y[i + 1] = y[i] + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return t, y[:, 0]


def sobreimpulso_medido(wn=1.0, z=0.5, **kw):
    """El pico de la respuesta integrada, en % sobre el valor final."""
    _, y = escalon_segundo_orden(wn=wn, z=z, **kw)
    return (float(np.max(y)) - 1.0) * 100.0


def sobreimpulso_desde_polos(z=0.5):
    """Lo que los polos PREDICEN: exp(-pi z / sqrt(1 - z^2)) x 100."""
    return float(np.exp(-np.pi * z / np.sqrt(1.0 - z * z)) * 100.0)


# --- 09 · Transformada Z ----------------------------------------------
def respuesta_polo(a, N=60):
    """y[n] = a y[n-1] + x[n] con x = impulso. El polo esta en z = a."""
    y = np.zeros(int(N))
    y[0] = 1.0
    for n in range(1, int(N)):
        y[n] = float(a) * y[n - 1]
    return np.arange(int(N)), y


def radio_polo(a):
    return float(abs(a))


def crecimiento(a, N=60):
    """Cuanto vale la respuesta al final respecto al principio.

    Menor que 1: se apaga. Mayor: explota. El umbral es el radio 1, y en
    la pieza se ve como el polo cruzando el circulo unidad."""
    _, y = respuesta_polo(a, N=N)
    return float(abs(y[-1]) / max(abs(y[0]), 1e-18))


# --- 10 · Chirp-Z -----------------------------------------------------
def czt(x, M, w, a):
    """Chirp-Z por el algoritmo de Bluestein.

    Evalua la transformada Z en M puntos de la espiral z_k = a w^-k. Con
    |a| = |w| = 1 son M puntos de un ARCO de la circunferencia unidad, y
    ahi esta la gracia: la DFT reparte sus N puntos por la circunferencia
    entera, la chirp-Z los gasta todos en el trozo que interesa."""
    x = np.asarray(x, dtype=complex)
    N = x.size
    M = int(M)
    L = 1 << int(np.ceil(np.log2(N + M - 1)))
    k = np.arange(max(N, M))
    w_pot = w ** (k * k / 2.0)
    y = np.zeros(L, dtype=complex)
    y[:N] = x * (a ** -np.arange(N)) * w_pot[:N]
    v = np.zeros(L, dtype=complex)
    v[:M] = w_pot[:M] ** -1
    v[L - N + 1:] = w_pot[1:N][::-1] ** -1
    g = np.fft.ifft(np.fft.fft(y) * np.fft.fft(v))
    return g[:M] * w_pot[:M]


def dos_tonos(f1, f2, N=256):
    """Dos tonos, en ciclos por ventana (pueden no ser enteros).

    Van SEPARADOS mas de un ciclo por ventana a proposito. La primera
    version los puso a 0.4 ciclos y la sonda tumbo la pieza entera: por
    debajo de un ciclo por ventana no los separa NINGUN metodo lineal,
    ni la chirp-Z ni nada, porque esa informacion no esta en la señal.
    La chirp-Z no da resolucion, da PUNTOS donde interesan — que es otra
    cosa y es la que cuenta la pieza."""
    n = np.arange(int(N))
    return (np.cos(2 * np.pi * float(f1) * n / N)
            + np.cos(2 * np.pi * float(f2) * n / N))


def zoom_czt(x, f_ini, f_fin, M=256):
    """|CZT| sobre el arco [f_ini, f_fin] en ciclos por ventana."""
    N = np.asarray(x).size
    a = np.exp(2j * np.pi * float(f_ini) / N)
    w = np.exp(-2j * np.pi * (float(f_fin) - float(f_ini)) / (N * int(M)))
    return np.abs(czt(x, M, w, a))


def factor_zoom(N, f_ini, f_fin, M=256):
    """Cuantas veces mas fina es la malla de la chirp-Z que la de la DFT.

    Ojo con lo que significa: mas fina la MALLA, no mas fina la
    resolucion. La DFT pone un punto por ciclo de ventana; la chirp-Z
    reparte M puntos en el trozo pedido. Los dos ven lo mismo, pero uno
    puede decir donde esta el pico y el otro solo entre que dos enteros.
    """
    paso_czt = (float(f_fin) - float(f_ini)) / int(M)
    return 1.0 / paso_czt


def pico_interpolado(mag, f_ini, f_fin):
    """La frecuencia del maximo de |CZT| sobre el arco, en ciclos.

    Es lo que la DFT no puede dar: su maximo cae siempre en un entero."""
    M = np.asarray(mag).size
    i = int(np.argmax(mag))
    return float(f_ini) + i * (float(f_fin) - float(f_ini)) / M


# --- 11 · STFT y el limite de Gabor ------------------------------------
def chirp(f0, f1, T=1.0, fs=1024.0):
    """Barrido lineal de f0 a f1 en T segundos."""
    t = np.arange(0.0, float(T), 1.0 / float(fs))
    k = (float(f1) - float(f0)) / float(T)
    return t, np.cos(2 * np.pi * (f0 * t + k * t * t / 2.0))


def ventana_gauss(L, sigma_rel=0.15):
    n = np.arange(int(L)) - (int(L) - 1) / 2.0
    return np.exp(-0.5 * (n / (sigma_rel * int(L))) ** 2)


def stft(x, L, salto, fs=1024.0, sigma_rel=0.15):
    """Espectrograma: |STFT|, con ventana gaussiana."""
    x = np.asarray(x, dtype=float)
    w = ventana_gauss(L, sigma_rel)
    inicios = np.arange(0, x.size - int(L) + 1, int(salto))
    S = np.stack([np.abs(np.fft.rfft(x[i:i + int(L)] * w)) for i in inicios])
    f = np.fft.rfftfreq(int(L), d=1.0 / float(fs))
    t = (inicios + int(L) / 2.0) / float(fs)
    return t, f, S.T


def dispersion_ventana(L, fs=1024.0, sigma_rel=0.15):
    """(sigma_t, sigma_f) de la ventana: sus anchuras rms en los dos lados.

    Se miden como desviaciones tipicas de |w|^2 y de |W|^2, que es la
    definicion con la que el limite de Gabor vale 1/(4 pi)."""
    w = ventana_gauss(L, sigma_rel)
    t = (np.arange(int(L)) - (int(L) - 1) / 2.0) / float(fs)
    p = w ** 2
    p = p / np.sum(p)
    sig_t = float(np.sqrt(np.sum(p * t ** 2)))
    W = np.abs(np.fft.fftshift(np.fft.fft(w))) ** 2
    f = np.fft.fftshift(np.fft.fftfreq(int(L), d=1.0 / float(fs)))
    q = W / np.sum(W)
    sig_f = float(np.sqrt(np.sum(q * f ** 2)))
    return sig_t, sig_f


def producto_gabor(L, **kw):
    """sigma_t x sigma_f. Para una gaussiana toca el minimo, 1/(4 pi).

    Es LA cifra de la pieza 11: cambiar el tamaño de la ventana mueve los
    dos factores en direcciones opuestas y deja el producto quieto. No se
    puede saber a la vez cuando y a que frecuencia."""
    st, sf = dispersion_ventana(L, **kw)
    return st * sf


LIMITE_GABOR = 1.0 / (4.0 * np.pi)


# --- 12 · Wavelet de Haar ---------------------------------------------
def dwt_haar(x, niveles=None):
    """DWT de Haar ortonormal. Devuelve (aprox, [detalles por nivel])."""
    a = np.asarray(x, dtype=float).copy()
    if a.size & (a.size - 1):
        raise ValueError("la DWT de Haar pide potencia de dos")
    niveles = int(np.log2(a.size)) if niveles is None else int(niveles)
    detalles = []
    r = np.sqrt(2.0)
    for _ in range(niveles):
        par, impar = a[0::2], a[1::2]
        detalles.append((par - impar) / r)
        a = (par + impar) / r
    return a, detalles


def coeficientes_haar(x, niveles=None):
    """Todos los coeficientes en un solo vector, del mas grueso al mas
    fino. Es lo que se cuenta para comparar con Fourier."""
    a, det = dwt_haar(x, niveles)
    return np.concatenate([a] + det[::-1])


def señal_con_salto(N=512, n_salto=384, semilla=SEMILLA):
    """Una rampa suave con UN escalon. Fourier necesita cientos de senos
    para dibujar ese escalon; Haar lo resuelve con un puñado."""
    n = np.arange(int(N))
    x = 0.6 * np.sin(2 * np.pi * 2 * n / N)
    x[n >= int(n_salto)] += 1.0
    return x


def cuantos_para_energia(coefs, fraccion=0.99):
    """Cuantos coeficientes (los mayores) hacen falta para `fraccion` de
    la energia. Es la comparacion justa entre dos bases ortonormales."""
    e = np.sort(np.abs(np.asarray(coefs)) ** 2)[::-1]
    total = float(np.sum(e))
    acum = np.cumsum(e) / max(total, 1e-18)
    return int(np.searchsorted(acum, float(fraccion)) + 1)


def coefs_fourier_ortonormales(x):
    """Los N coeficientes REALES de x en la base de Fourier ortonormal.

    Contar los N complejos de la FFT seria hacer trampa a favor de Haar:
    la mitad son el conjugado de la otra mitad. La base honrada es la
    real —1/sqrt(N), y los cos y sin con sqrt(2/N)—, que tiene
    exactamente N vectores ortonormales igual que Haar, cumple Parseval
    exacto y hace que "cuantos coeficientes hacen falta" signifique lo
    mismo en los dos lados."""
    x = np.asarray(x, dtype=float)
    N = x.size
    X = np.fft.rfft(x) / np.sqrt(N)
    coefs = [np.real(X[0])]
    fin = N // 2
    coefs += list(np.real(X[1:fin]) * np.sqrt(2.0))
    coefs += list(-np.imag(X[1:fin]) * np.sqrt(2.0))
    if N % 2 == 0:
        coefs.append(np.real(X[fin]))
    return np.array(coefs)


# --- 13 · Fourier fraccional ------------------------------------------
def wigner(x, M=None):
    """Distribucion de Wigner-Ville: la señal repartida en el plano
    tiempo-frecuencia a la vez.

    W(n, k) = 2 sum_m z(n+m) z*(n-m) exp(-4 pi i m k / L), con z la señal
    analitica (asi no aparecen los terminos cruzados entre la frecuencia
    positiva y la negativa, que no significan nada).

    Es REAL, y sus dos marginales son las dos transformadas de siempre:
    sumando por frecuencias sale |z(t)|^2 y sumando por tiempos sale
    |Z(f)|^2. La sonda comprueba las dos, que es lo unico que demuestra
    que esta bien calculada."""
    z = np.asarray(x, dtype=complex)
    if np.isrealobj(x):
        z = analitica(np.asarray(x, dtype=float))
    N = z.size
    M = int(M or N // 2)
    L = 2 * M
    W = np.zeros((L, N))
    for n in range(N):
        m = np.arange(-M, M)
        a, b = n + m, n - m
        ok = (a >= 0) & (a < N) & (b >= 0) & (b < N)
        r = np.zeros(L, dtype=complex)
        r[ok] = z[a[ok]] * np.conj(z[b[ok]])
        W[:, n] = np.real(np.fft.fftshift(np.fft.fft(np.fft.ifftshift(r))))
    return W / L


def proyeccion_wigner(W, grados):
    """La sombra del plano de Wigner girado `grados`. Es |FrFT|^2.

    El teorema de Radon-Wigner dice exactamente esto: el modulo al
    cuadrado de la transformada fraccional de orden a es la PROYECCION de
    la distribucion de Wigner sobre un eje girado alpha = a pi/2. Por eso
    la pieza puede enseñar la FrFT sin dibujar ninguna formula: se gira el
    plano y se mira su sombra.

    A 0 grados sale la señal en el tiempo; a 90, su espectro. Todo lo de
    en medio son las transformadas fraccionales."""
    return np.sum(_rotar(np.asarray(W, dtype=float), float(grados)), axis=0)


# El eje de frecuencia de la matriz de Wigner va al DOBLE que el de una
# FFT normal: la correlacion se toma a desfase 2m, asi que un tono de f0
# ciclos por muestra cae a 2L*f0 bins del centro. Medido: f0 = 0.05, 0.10
# y 0.20 caen a 26, 51 y 102 bins con L = 256, o sea 512*f0. Y por encima
# de 0.25 ciclos ALIASA (0.30 salio a -102): por eso se usa la señal
# analitica y por eso las señales de la pieza se quedan por debajo.
ESCALA_FRECUENCIA_WIGNER = 2.0


def pendiente_cresta(beta):
    """La inclinacion de la cresta del chirp EN LA MATRIZ, en bins por
    columna. Vale 2*beta y no depende de N.

    Sale de encadenar dos cosas: la frecuencia instantanea del chirp de
    `chirp_complejo` es f = beta*t/N ciclos por muestra, y un desvio de f
    son 2N bins. El producto da 2*beta, y la sonda lo comprueba midiendo
    la cresta."""
    return ESCALA_FRECUENCIA_WIGNER * float(beta)


def angulo_optimo(beta):
    """El giro que endereza un chirp exp(i pi beta t^2), deducido.

    En el plano tiempo-frecuencia el chirp es una RECTA. Para que su
    sombra sea un pico hay que dejarla perpendicular al eje sobre el que
    se proyecta: 90 grados menos su inclinacion.

    Ojo con la inclinacion, que fue el error de la primera version: NO es
    arctan(beta) sino arctan(2*beta), porque el eje de frecuencia de la
    matriz de Wigner va al doble. Con arctan(beta) la teoria decia 73.3
    grados donde la medida daba 59.0, y las dos cosas eran ciertas: la
    formula estaba bien y los ejes no."""
    return float(90.0 - np.degrees(np.arctan(pendiente_cresta(beta))))


def chirp_complejo(N=256, beta=0.6):
    """exp(i pi beta t^2) muestreado: una recta en el plano de Wigner."""
    t = np.arange(int(N)) - int(N) / 2.0
    return t, np.exp(1j * np.pi * float(beta) * (t / np.sqrt(int(N))) ** 2)


def concentracion(y):
    """Cuanta energia hay en el pico: max|y|^2 / sum|y|^2.

    Es la medida con la que la pieza 13 BUSCA el angulo: se barre el
    orden y se queda el que mas concentra."""
    p = np.abs(np.asarray(y)) ** 2
    return float(np.max(p) / max(np.sum(p), 1e-18))


def barrido_wigner(W, angulos):
    """La concentracion de la sombra para cada giro. El maximo es el
    angulo que endereza el chirp."""
    return np.array([concentracion(proyeccion_wigner(W, g)) for g in angulos])


# --- 14 · Hilbert -----------------------------------------------------
def analitica(x):
    """Señal analitica: se anulan las frecuencias negativas y se dobla el
    resto. La parte imaginaria es la transformada de Hilbert de x."""
    x = np.asarray(x, dtype=float)
    N = x.size
    X = np.fft.fft(x)
    h = np.zeros(N)
    h[0] = 1.0
    if N % 2 == 0:
        h[N // 2] = 1.0
        h[1:N // 2] = 2.0
    else:
        h[1:(N + 1) // 2] = 2.0
    return np.fft.ifft(X * h)


def señal_modulada(N=1024, f=24.0):
    """Una nota pulsada: ataque rapido, caida lenta, portadora dentro.

    La envolvente NO es un seno suave a proposito. Con una envolvente
    bandlimitada la reconstruccion sale exacta (error 1e-14) y la pieza
    enseñaria un caso de laboratorio: aqui hay un ataque abrupto, que es
    lo que tiene un sonido de verdad y lo que le cuesta a la
    transformada. El error que salga es el error de verdad.

    La envolvente no se le pasa a la transformada: solo se usa al final
    para medir cuanto se acerco."""
    t = np.arange(int(N)) / int(N)
    env = (1.0 - np.exp(-60.0 * t)) * np.exp(-2.2 * t)
    env = env / np.max(env)
    return t, env, env * np.cos(2 * np.pi * float(f) * t)


def error_envolvente(N=1024, f=24.0, borde=64):
    """Error maximo, en %, entre |analitica| y la envolvente verdadera.

    Se descartan `borde` muestras de cada extremo: la FFT supone que la
    señal es periodica y en los bordes la envolvente recuperada tiene el
    error del salto, que no es de la transformada sino de la ventana. Se
    dice en pantalla, no se esconde."""
    _, env, x = señal_modulada(N=N, f=f)
    rec = np.abs(analitica(x))
    b = int(borde)
    d = np.abs(rec[b:-b] - env[b:-b]) / np.max(env)
    return float(np.max(d) * 100.0)


# --- 15 · Mellin ------------------------------------------------------
def mellin_escala(x_de_t, t_min=0.05, t_max=8.0, M=1024):
    """|Mellin| via remuestreo exponencial + FFT.

    El truco entero de Mellin: con t = e^u, escalar t por `s` es DESPLAZAR
    u por log(s). Y un desplazamiento no cambia el modulo de la FFT. Por
    eso el modulo de Mellin es invariante a la escala."""
    u = np.linspace(np.log(t_min), np.log(t_max), int(M))
    t = np.exp(u)
    g = np.asarray([x_de_t(ti) for ti in t], dtype=float) * np.sqrt(t)
    return np.abs(np.fft.rfft(g))


def forma_ejemplo(escala=1.0, centro=1.2, ancho=0.45):
    """Un bulto suave; `escala` lo estira sobre el eje del tiempo."""
    def f(t):
        z = (t / float(escala) - centro) / ancho
        return float(np.exp(-z * z) * np.cos(2.5 * z))
    return f


def pico_fourier(x_de_t, t_max=8.0, N=1024):
    """Frecuencia del maximo del espectro de Fourier, en la malla dada.

    Es lo que SE MUEVE al escalar la forma, y es la mitad de la pieza 15:
    la otra mitad es que el de Mellin no se mueve."""
    t = np.linspace(0.0, float(t_max), int(N), endpoint=False)
    g = np.asarray([x_de_t(ti) for ti in t], dtype=float)
    mag = np.abs(np.fft.rfft(g))
    f = np.fft.rfftfreq(int(N), d=t[1] - t[0])
    return float(f[int(np.argmax(mag))])


def pico_mellin(x_de_t, **kw):
    """Indice del maximo del modulo de Mellin. No se mueve con la escala."""
    mag = mellin_escala(x_de_t, **kw)
    return int(np.argmax(mag))


# --- 16 · Radon -------------------------------------------------------
def fantasma(n=128):
    """El objeto de la pieza 16: dos discos y una barra dentro de un
    contorno. Se conoce entero, asi que el error de reconstruccion se
    puede MEDIR en vez de estimarse."""
    n = int(n)
    y, x = np.mgrid[0:n, 0:n]
    x = (x - n / 2.0) / (n / 2.0)
    y = (y - n / 2.0) / (n / 2.0)
    img = np.zeros((n, n))
    img[(x ** 2 + y ** 2) < 0.85 ** 2] = 0.25
    img[((x + 0.28) ** 2 + (y + 0.18) ** 2) < 0.22 ** 2] = 1.0
    img[((x - 0.30) ** 2 + (y - 0.25) ** 2) < 0.14 ** 2] = 0.75
    img[(np.abs(x - 0.10) < 0.05) & (np.abs(y + 0.42) < 0.26)] = 0.9
    return img


def _rotar(img, grados):
    """Rotacion bilineal, sin scipy (el contenedor no lo trae)."""
    n = img.shape[0]
    c = (n - 1) / 2.0
    th = np.deg2rad(float(grados))
    y, x = np.mgrid[0:n, 0:n].astype(float)
    xs = (x - c) * np.cos(th) + (y - c) * np.sin(th) + c
    ys = -(x - c) * np.sin(th) + (y - c) * np.cos(th) + c
    x0 = np.floor(xs).astype(int)
    y0 = np.floor(ys).astype(int)
    dx, dy = xs - x0, ys - y0
    out = np.zeros_like(img)
    ok = (x0 >= 0) & (x0 < n - 1) & (y0 >= 0) & (y0 < n - 1)
    xi, yi = np.clip(x0, 0, n - 2), np.clip(y0, 0, n - 2)
    val = (img[yi, xi] * (1 - dx) * (1 - dy)
           + img[yi, xi + 1] * dx * (1 - dy)
           + img[yi + 1, xi] * (1 - dx) * dy
           + img[yi + 1, xi + 1] * dx * dy)
    out[ok] = val[ok]
    return out


def radon(img, angulos):
    """El sinograma: una columna por angulo, cada una la sombra del objeto.

    Sumar los pixeles de cada columna tras rotar ES la integral de linea:
    exactamente lo que mide un detector de rayos X."""
    return np.stack([np.sum(_rotar(img, a), axis=0) for a in angulos], axis=1)


def _filtro_rampa(sino):
    """El filtro |w| de la retroproyeccion filtrada.

    Sin el, la reconstruccion sale borrosa: cada retroproyeccion reparte
    la sombra por toda la linea y las bajas frecuencias se suman de mas."""
    n = sino.shape[0]
    L = int(2 ** np.ceil(np.log2(2 * n)))
    f = np.abs(np.fft.fftfreq(L)) * 2.0
    S = np.fft.fft(sino, n=L, axis=0) * f[:, None]
    return np.real(np.fft.ifft(S, axis=0))[:n]


def retroproyeccion(sino, angulos, n=None):
    """Reconstruye la imagen a partir del sinograma (FBP).

    Cada sombra filtrada se estira sobre toda la imagen (no sabemos DONDE
    de la linea estaba la materia, solo cuanta habia) y se gira hasta el
    angulo desde el que se tomo. Sumando todas, lo que estaba de verdad
    se refuerza y lo demas se cancela."""
    n = int(n or sino.shape[0])
    filtrado = _filtro_rampa(sino)
    acc = np.zeros((n, n))
    for i, ang in enumerate(angulos):
        banda = np.tile(filtrado[:, i], (n, 1))     # constante en y
        acc += _rotar(banda, -float(ang))
    return acc * np.pi / max(len(angulos), 1)


def error_reconstruccion(n_angulos, n=128):
    """Error rms de la reconstruccion respecto al fantasma, normalizado.

    Con pocos angulos aparecen las rayas del aliasing; con muchos, la
    imagen. La cifra es el error, y baja de verdad."""
    img = fantasma(n)
    ang = np.linspace(0.0, 180.0, int(n_angulos), endpoint=False)
    rec = retroproyeccion(radon(img, ang), ang, n=n)
    a, b = img.ravel(), rec.ravel()
    k = float(np.dot(a, b) / max(np.dot(b, b), 1e-18))   # escala global
    return float(np.sqrt(np.mean((a - k * b) ** 2)) / max(np.max(a), 1e-18))


# --- 17 · Hough -------------------------------------------------------
def nube_con_recta(n_recta=24, n_ruido=60, m=0.6, b=-0.2, ruido=0.008,
                   semilla=SEMILLA):
    """Puntos sobre una recta, ahogados en puntos sueltos.

    `n_recta`, `n_ruido` y la recta son parametros elegidos (etiqueta
    apagada). Lo que se MIDE es cuantos votos junta el pico."""
    rng = np.random.default_rng(semilla)
    x = rng.uniform(-0.9, 0.9, int(n_recta))
    y = m * x + b + rng.normal(0.0, ruido, int(n_recta))
    xr = rng.uniform(-0.95, 0.95, int(n_ruido))
    yr = rng.uniform(-0.95, 0.95, int(n_ruido))
    return (np.concatenate([x, xr]), np.concatenate([y, yr]))


def hough(px, py, n_theta=180, n_rho=121, rho_max=1.5):
    """Acumulador de Hough. Cada punto vota una senoide entera.

    rho = x cos(theta) + y sin(theta). Los puntos alineados votan
    senoides distintas que se cruzan TODAS en la misma casilla: esa
    casilla es la recta.

    El voto va a la casilla MAS CERCANA. La primera version usaba
    `searchsorted`, que devuelve el sitio donde habria que insertar y por
    tanto desplaza cada voto medio escalon: el pico se repartia entre dos
    filas y de 24 puntos alineados solo juntaba 11."""
    th = np.linspace(0.0, np.pi, int(n_theta), endpoint=False)
    paso = 2.0 * float(rho_max) / (int(n_rho) - 1)
    rho = -float(rho_max) + paso * np.arange(int(n_rho))
    acc = np.zeros((int(n_rho), int(n_theta)), dtype=int)
    for x, y in zip(np.asarray(px), np.asarray(py)):
        r = x * np.cos(th) + y * np.sin(th)
        idx = np.clip(np.rint((r + rho_max) / paso).astype(int),
                      0, int(n_rho) - 1)
        acc[idx, np.arange(int(n_theta))] += 1
    return th, rho, acc


def pico_hough(acc):
    """(votos, fila, columna) de la casilla mas votada."""
    i = int(np.argmax(acc))
    fila, col = np.unravel_index(i, acc.shape)
    return int(acc[fila, col]), int(fila), int(col)


def senoide_hough(x, y, th):
    return x * np.cos(th) + y * np.sin(th)


# --- 18 · Karhunen-Loeve ----------------------------------------------
def nube_correlada(n=220, sx=1.0, sy=0.28, giro=28.0, semilla=SEMILLA):
    """Una nube alargada y torcida. El giro es un parametro elegido; lo
    que se mide es que la KL lo ENCUENTRA sin que se lo digan."""
    rng = np.random.default_rng(semilla)
    p = np.stack([rng.normal(0, sx, int(n)), rng.normal(0, sy, int(n))])
    th = np.deg2rad(float(giro))
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    return (R @ p).T


def base_kl(puntos):
    """(valores, vectores, angulo_grados) de la base de Karhunen-Loeve.

    Es la base propia de la covarianza: los ejes que la nube misma
    dicta. Ordenados de mas a menos varianza."""
    X = np.asarray(puntos, dtype=float)
    X = X - X.mean(axis=0)
    C = np.cov(X, rowvar=False)
    val, vec = np.linalg.eigh(C)
    orden = np.argsort(val)[::-1]
    val, vec = val[orden], vec[:, orden]
    # El signo de un autovector es arbitrario, asi que el angulo de un
    # EJE vive modulo 180: sin esto la sonda leia -152.25 donde la nube
    # estaba girada 27.75 grados, que es el mismo eje.
    ang = float(np.degrees(np.arctan2(vec[1, 0], vec[0, 0])))
    ang = (ang + 90.0) % 180.0 - 90.0
    return val, vec, ang


def varianza_explicada(puntos, k=1):
    """Fraccion de la varianza total que guardan las `k` primeras
    componentes. Es la cifra de la pieza 18."""
    val, _, _ = base_kl(puntos)
    return float(np.sum(val[:int(k)]) / max(np.sum(val), 1e-18))


# =====================================================================
#  MITAD DE DIBUJO
#
#  Todas devuelven mobjects centrados en el origen. NO animan y NO deciden
#  donde van: de eso se encarga `lienzo.encajar`.
# =====================================================================

def _exige_manim():
    if not _HAY_MANIM:
        raise RuntimeError(
            "las piezas de dibujo de transformadas.py necesitan manim y "
            "lienzo; la mitad numerica se importa sin ellos a proposito")


TRAZO = 3.0
TRAZO_FINO = 1.6
TRAZO_PELO = 1.0

# Relleno de las piezas de area: CERO. Medido en el curso 31 sobre este
# fondo, el ambar traslucido da verde oliva (72,62,45 al 26 %) y al 14 %
# un gris. No hay ventana buena. La unica excepcion son los mapas y las
# mallas de imagen, que representan intensidad y por tanto SON masa: esos
# van del azul del fondo a la tinta, nunca por el ambar.


# --- Curvas y ejes ----------------------------------------------------
def traza(x, y, ancho=4.8, alto=2.2, color=None, grosor=TRAZO,
          rango_y=None, rango_x=None, escalones=False):
    """Una serie convertida en polilinea dentro de una caja ancho x alto.

    Devuelve (mobject, punto) — `punto(xi, yi)` sitúa cualquier par de
    coordenadas de los datos en el dibujo, que es lo que permite colgar un
    rotulo de un valor concreto sin rehacer la transformacion a mano."""
    _exige_manim()
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x0, x1 = rango_x if rango_x else (float(x.min()), float(x.max()))
    y0, y1 = rango_y if rango_y else (float(y.min()), float(y.max()))
    dx = (x1 - x0) or 1.0
    dy = (y1 - y0) or 1.0

    def punto(xi, yi):
        return np.array([(float(xi) - x0) / dx * ancho - ancho / 2,
                         (float(yi) - y0) / dy * alto - alto / 2, 0.0])

    if escalones:
        puntos = []
        for i in range(len(x)):
            puntos.append(punto(x[i], y[i]))
            if i + 1 < len(x):
                puntos.append(punto(x[i + 1], y[i]))
    else:
        puntos = [punto(x[i], y[i]) for i in range(len(x))]
    linea = VMobject(stroke_color=color or _lz.TINTA, stroke_width=grosor)
    linea.set_points_as_corners(puntos)
    return linea, punto


def eje_ele(ancho=4.8, alto=2.2, color=None, grosor=TRAZO_FINO):
    """Solo dos lineas: abajo e izquierda. Sin marcas ni numeros — la
    escala la pone la cifra de abajo, no el eje."""
    _exige_manim()
    color = color or _lz.LINEA
    return VGroup(
        Line([-ancho / 2, -alto / 2, 0], [ancho / 2, -alto / 2, 0],
             stroke_color=color, stroke_width=grosor),
        Line([-ancho / 2, -alto / 2, 0], [-ancho / 2, alto / 2, 0],
             stroke_color=color, stroke_width=grosor))


def cero(ancho=4.8, y=0.0, color=None, grosor=TRAZO_PELO):
    """La horizontal del cero, para las señales que van de + a -."""
    _exige_manim()
    return Line([-ancho / 2, y, 0], [ancho / 2, y, 0],
                stroke_color=color or _lz.LINEA, stroke_width=grosor)


def nivel(y_dato, punto, ancho=4.8, color=None, discontinua=True):
    """Una horizontal de referencia a la altura de un valor de los datos."""
    _exige_manim()
    y = punto(0, y_dato)[1]
    ln = Line([-ancho / 2, y, 0], [ancho / 2, y, 0],
              stroke_color=color or _lz.APAGADO, stroke_width=TRAZO_FINO)
    return DashedVMobject(ln, num_dashes=26, dashed_ratio=0.45) \
        if discontinua else ln


def tallos(valores, ancho=4.8, alto=2.2, color=None, grosor=TRAZO_FINO,
           punta=0.045, rango_y=None):
    """Un espectro discreto: una raya por bin, con su punto arriba.

    Es el dibujo honrado de una DFT. Unir los bins con una curva sugiere
    que hay algo entre ellos, y no lo hay: la DFT solo existe en esos
    puntos."""
    _exige_manim()
    v = np.asarray(valores, dtype=float)
    n = v.size
    y0, y1 = rango_y if rango_y else (min(0.0, float(v.min())),
                                      float(v.max()) or 1.0)
    dy = (y1 - y0) or 1.0
    paso = ancho / max(n - 1, 1)
    grupo = VGroup()
    base = -alto / 2 + (0.0 - y0) / dy * alto
    for i, vi in enumerate(v):
        x = -ancho / 2 + i * paso
        y = -alto / 2 + (vi - y0) / dy * alto
        grupo.add(Line([x, base, 0], [x, y, 0],
                       stroke_color=color or _lz.TINTA, stroke_width=grosor))
        if punta:
            grupo.add(Dot([x, y, 0], radius=punta,
                          color=color or _lz.TINTA))
    return grupo


# --- El plano complejo -------------------------------------------------
def plano_z(radio=1.35, color=None, con_circulo=True):
    """Los dos ejes y el circulo unidad. El mapa de las piezas 08 y 09."""
    _exige_manim()
    color = color or _lz.LINEA
    g = VGroup(
        Line([-radio * 1.35, 0, 0], [radio * 1.35, 0, 0],
             stroke_color=color, stroke_width=TRAZO_PELO),
        Line([0, -radio * 1.25, 0], [0, radio * 1.25, 0],
             stroke_color=color, stroke_width=TRAZO_PELO))
    if con_circulo:
        g.add(Circle(radius=radio, stroke_color=_lz.APAGADO,
                     stroke_width=TRAZO_FINO, fill_opacity=0.0))
    return g


def aspa(z, radio=1.35, escala=1.0, color=None, lado=0.13):
    """El aspa de un polo, en la posicion compleja `z`.

    Un polo se marca con un aspa y un cero con un circulito: es la
    notacion de toda la ingenieria de control y no hay razon para
    inventar otra."""
    _exige_manim()
    c = np.array([float(np.real(z)) * radio * escala,
                  float(np.imag(z)) * radio * escala, 0.0])
    col = color or _lz.AMBAR
    return VGroup(
        Line(c + [-lado, -lado, 0], c + [lado, lado, 0],
             stroke_color=col, stroke_width=TRAZO),
        Line(c + [-lado, lado, 0], c + [lado, -lado, 0],
             stroke_color=col, stroke_width=TRAZO))


# --- Barras ------------------------------------------------------------
def barras(valores, ancho=4.6, alto=2.0, color=None, hueco=0.28,
           colores=None, minimo_visible=0.02):
    """Barras verticales proporcionales al valor, sin mentir de escala.

    `minimo_visible` NO estira la barra: le pone un grosor de trazo
    suficiente para verse cuando su valor es minusculo. En el curso 31 un
    agente inflo una barra un 52 % 'para que se viera' y hubo que
    rechazarlo: lo que no se ve se dibuja con su tamaño real y se le sube
    el trazo, o se cambia de dibujo."""
    _exige_manim()
    v = np.asarray(valores, dtype=float)
    tope = float(np.max(np.abs(v))) or 1.0
    n = v.size
    w = ancho / (n + (n - 1) * hueco)
    g = VGroup()
    for i, vi in enumerate(v):
        h = abs(vi) / tope * alto
        col = (colores[i] if colores else None) or color or _lz.TINTA
        x = -ancho / 2 + i * w * (1 + hueco) + w / 2
        if h < minimo_visible * alto:
            g.add(Line([x - w / 2, -alto / 2, 0], [x + w / 2, -alto / 2, 0],
                       stroke_color=col, stroke_width=TRAZO))
            continue
        r = Rectangle(width=w, height=h, stroke_color=col,
                      stroke_width=TRAZO_FINO, fill_color=_lz.AZUL,
                      fill_opacity=1.0)
        r.move_to([x, -alto / 2 + h / 2, 0])
        g.add(r)
    return g


# --- Mapas de intensidad -----------------------------------------------
def _rampa(m, color_alto=None):
    """Matriz 0..1 -> RGB, del azul del fondo al color alto.

    Va del FONDO a la tinta y no de negro a blanco: asi el valor cero es
    exactamente el lienzo y el mapa no lleva marco. Un mapa que empieza en
    negro se recorta contra el azul y parece una foto pegada encima."""
    _exige_manim()
    from manim.utils.color import ManimColor
    c0 = np.array(ManimColor(_lz.AZUL).to_rgb()) * 255.0
    c1 = np.array(ManimColor(color_alto or _lz.TINTA).to_rgb()) * 255.0
    m = np.clip(np.asarray(m, dtype=float), 0.0, 1.0)
    rgb = np.zeros(m.shape + (3,), dtype=np.uint8)
    for i in range(3):
        rgb[..., i] = np.clip(c0[i] + (c1[i] - c0[i]) * m, 0, 255)
    return rgb


def mapa(matriz, ancho=None, alto=None, color_alto=None, gamma=1.0,
         voltear=True, rango=None):
    """Un mapa de intensidad (espectrograma, sinograma, acumulador...).

    Va como `ImageMobject` y no como miles de rectangulos: un
    espectrograma de 128x64 son 8192 celdas, y dibujarlas una a una haria
    el render inviable ademas de dejar costuras entre celdas.

    `voltear` pone la fila 0 ABAJO, que es lo que espera cualquiera que
    mire un espectrograma: en una imagen la fila 0 es la de arriba y en
    una matriz de frecuencias es la de la frecuencia mas baja."""
    _exige_manim()
    m = np.asarray(matriz, dtype=float)
    lo, hi = rango if rango else (float(np.min(m)), float(np.max(m)))
    m = (m - float(lo)) / ((float(hi) - float(lo)) or 1.0)
    if gamma != 1.0:
        m = m ** float(gamma)
    if voltear:
        m = m[::-1]
    img = ImageMobject(_rampa(m, color_alto))
    img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    if alto:
        img.height = float(alto)
    if ancho:
        img.width = float(ancho)
    return img


def malla(valores, lado=2.4, color_alto=None, rejilla=True, rango=None):
    """Una imagen pequeña celda a celda, con su rejilla.

    Para el bloque 8x8 de la DCT SI se dibujan celdas: son 64, se ven
    individualmente y la pieza va justamente de que cada una es un numero.
    Por encima de ~20x20 hay que usar `mapa`.

    `rango=(lo, hi)` fija la escala de color en vez de sacarla de la
    propia matriz, y hace falta SIEMPRE que se comparen dos imagenes. Sin
    el, cada una se normaliza por su minimo y su maximo: en la pieza 05
    el bloque rehecho tiene menos rango que el original (0.579 contra
    0.644) y salia mas contrastado de lo que es, o sea MAS distinto del
    original de lo que realmente era — justo al reves de lo que la pieza
    afirma. Lo levanto el agente que la escribio.

    Y ademas resuelve un caso degenerado: una matriz constante (la
    reconstruccion con un solo coeficiente) tiene rango cero y sin
    `rango` se pinta entera del color del fondo, o sea invisible."""
    _exige_manim()
    m = np.asarray(valores, dtype=float)
    n = m.shape[0]
    lo, hi = rango if rango else (float(np.min(m)), float(np.max(m)))
    norm = (m - float(lo)) / ((float(hi) - float(lo)) or 1.0)
    norm = np.clip(norm, 0.0, 1.0)
    from manim.utils.color import ManimColor
    c0 = np.array(ManimColor(_lz.AZUL).to_rgb())
    c1 = np.array(ManimColor(color_alto or _lz.TINTA).to_rgb())
    celda = lado / n
    g = VGroup()
    for i in range(n):
        for j in range(m.shape[1]):
            c = c0 + (c1 - c0) * norm[i, j]
            r = Rectangle(
                width=celda, height=celda,
                stroke_color=_lz.LINEA if rejilla else None,
                stroke_width=TRAZO_PELO if rejilla else 0.0,
                fill_color=ManimColor(tuple(np.clip(c, 0, 1))),
                fill_opacity=1.0)
            r.move_to([(j + 0.5) * celda - lado / 2,
                       lado / 2 - (i + 0.5) * celda, 0])
            g.add(r)
    return g


# --- Nubes de puntos ---------------------------------------------------
def nube(puntos, ancho=4.4, alto=2.6, color=None, radio=0.035,
         rango=None):
    """Una nube de puntos 2D dentro de una caja. Devuelve (grupo, punto)."""
    _exige_manim()
    P = np.asarray(puntos, dtype=float)
    if rango:
        (x0, x1), (y0, y1) = rango
    else:
        x0, x1 = float(P[:, 0].min()), float(P[:, 0].max())
        y0, y1 = float(P[:, 1].min()), float(P[:, 1].max())
    dx = (x1 - x0) or 1.0
    dy = (y1 - y0) or 1.0

    def punto(xi, yi):
        return np.array([(float(xi) - x0) / dx * ancho - ancho / 2,
                         (float(yi) - y0) / dy * alto - alto / 2, 0.0])

    g = VGroup(*[Dot(punto(p[0], p[1]), radius=radio,
                     color=color or _lz.APAGADO) for p in P])
    return g, punto


def eje_propio(angulo_grados, largo=2.2, color=None, punta=True):
    """Un eje con direccion, para la base de Karhunen-Loeve."""
    _exige_manim()
    th = np.deg2rad(float(angulo_grados))
    d = np.array([np.cos(th), np.sin(th), 0.0]) * largo / 2
    col = color or _lz.AMBAR
    if punta:
        return Arrow(-d, d, buff=0.0, stroke_width=TRAZO,
                     color=col, max_tip_length_to_length_ratio=0.10)
    return Line(-d, d, stroke_color=col, stroke_width=TRAZO)


# --- Piezas propias de una transformada --------------------------------
def mariposa(niveles=3, ancho=4.2, alto=2.4, color=None, activo=None):
    """El grafo de la FFT: los cruces que parten el problema por la mitad.

    `activo` (0..niveles-1) pinta en ambar SOLO las aristas de esa etapa,
    que es como la pieza 04 enseña que cada nivel vuelve a partir."""
    _exige_manim()
    n = 2 ** int(niveles)
    col = color or _lz.LINEA
    xs = np.linspace(-ancho / 2, ancho / 2, int(niveles) + 1)
    ys = np.linspace(alto / 2, -alto / 2, n)
    g = VGroup()
    for etapa in range(int(niveles)):
        salto = 2 ** etapa
        resalta = (activo is not None and etapa == activo)
        c = _lz.AMBAR if resalta else col
        for i in range(n):
            j = i ^ salto
            g.add(Line([xs[etapa], ys[i], 0], [xs[etapa + 1], ys[j], 0],
                       stroke_color=c,
                       stroke_width=TRAZO_FINO if resalta else TRAZO_PELO,
                       stroke_opacity=1.0 if resalta else 0.55))
    for i in range(n):
        g.add(Dot([xs[0], ys[i], 0], radius=0.032, color=_lz.APAGADO))
        g.add(Dot([xs[-1], ys[i], 0], radius=0.032, color=_lz.APAGADO))
    return g


def ondas_walsh(cuantos=4, ancho=4.4, alto=0.42, hueco=0.20, N=32,
                color=None):
    """Las primeras funciones de Walsh, ordenadas por secuencia.

    Son las 'ondas' de esta base: solo valen +1 o -1, y por eso
    proyectarse sobre ellas no necesita ni una multiplicacion."""
    _exige_manim()
    H = hadamard(N)[orden_secuencial(N)]
    g = VGroup()
    for k in range(int(cuantos)):
        fila = H[k]
        linea, _ = traza(np.arange(N), fila, ancho=ancho, alto=alto,
                         color=color or _lz.TINTA, grosor=TRAZO_FINO,
                         rango_y=(-1.3, 1.3), escalones=True)
        g.add(linea)
    return g.arrange(DOWN, buff=hueco)


def ventana_sobre(x, inicio, largo, ancho=4.8, alto=2.2, color=None):
    """El rectangulo de la ventana deslizante de la STFT, ya colocado
    sobre la traza de la señal."""
    _exige_manim()
    n = np.asarray(x).size
    w = largo / n * ancho
    r = Rectangle(width=w, height=alto, stroke_color=color or _lz.AMBAR,
                  stroke_width=TRAZO_FINO, fill_opacity=0.0)
    r.move_to([-ancho / 2 + (inicio + largo / 2) / n * ancho, 0, 0])
    return r


def haz_rayos(angulo_grados, radio=1.25, cuantos=9, largo=3.0, color=None):
    """El haz que atraviesa el objeto en la pieza 16, a un angulo dado."""
    _exige_manim()
    th = np.deg2rad(float(angulo_grados))
    d = np.array([np.cos(th), np.sin(th), 0.0])
    perp = np.array([-np.sin(th), np.cos(th), 0.0])
    g = VGroup()
    for s in np.linspace(-radio, radio, int(cuantos)):
        c = perp * s
        g.add(Line(c - d * largo / 2, c + d * largo / 2,
                   stroke_color=color or _lz.APAGADO,
                   stroke_width=TRAZO_PELO, stroke_opacity=0.7))
    return g


def senoides_hough(px, py, ancho=4.4, alto=2.4, color=None, n_theta=180,
                   rho_max=1.5, grosor=TRAZO_PELO):
    """Una senoide por punto, en el plano (theta, rho).

    Es el dibujo entero de la pieza 17: donde se cruzan todas, esta la
    recta."""
    _exige_manim()
    th = np.linspace(0.0, np.pi, int(n_theta))
    g = VGroup()
    for x, y in zip(np.asarray(px), np.asarray(py)):
        r = senoide_hough(x, y, th)
        linea, _ = traza(th, r, ancho=ancho, alto=alto,
                         color=color or _lz.APAGADO, grosor=grosor,
                         rango_x=(0.0, np.pi),
                         rango_y=(-rho_max, rho_max))
        linea.set_stroke(opacity=0.55)
        g.add(linea)
    return g
