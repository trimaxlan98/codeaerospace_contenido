"""Caos y gravedad: las simulaciones de la serie de reels «Caos y gravedad» (46-reels-caos.py).

numpy + scipy (solve_ivp, DOP853 con tolerancias estrictas), deterministas, sin red ni disco. Cada trayectoria y cada cifra que
la serie dibuja sale de aquí, evaluada en `datos_co.py`; `python3 caos_gravedad.py` corre las pruebas (conservación de energía,
constante de Jacobi, puntos de Lagrange, periodo de la figura ocho...).

    tres_cuerpos        N cuerpos en el plano con G = 1 (figura ocho de Chenciner–Montgomery y sus «gemelas» perturbadas)
    energia_n           energía total del sistema de N cuerpos (para comprobar la integración)
    cr3bp               problema restringido de tres cuerpos en el marco que gira (Tierra–Luna, Sol–Tierra...)
    jacobi / potencial  constante de Jacobi y potencial efectivo (los «cerros y valles» del marco que gira)
    puntos_lagrange     L1..L5 (raíces de la ecuación del eje y triángulos equiláteros)
    separacion          dos trayectorias que empiezan a una distancia δ: cuánto se separan con el tiempo
    coorbitales         Saturno + Jano + Epimeteo con masas reales: el intercambio de órbitas en herradura
    giro_orbita         rotación de una luna alargada en una órbita excéntrica (modelo de Wisdom–Peale–Mignard, 1984)
    sobrevuelo          asistencia gravitatoria: ángulo de giro de la hipérbola y Δv en el marco del Sol
    kessler             cascada de choques: modelo de juguete N' = L − N/τ + k·N²
    horizonte_lyapunov  cuánto crece un error δ0·e^(t/τ) y cuándo alcanza un tamaño dado
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

# ── N cuerpos en el plano (G = 1) ──────────────────────────────────────────────────────────────────────────────────────────
OCHO_X1 = np.array([0.97000436, -0.24308753])
OCHO_V3 = np.array([-0.93240737, -0.86473146])
OCHO_T = 6.32591398                                  # periodo de la figura ocho (Chenciner y Montgomery, 2000; C. Moore, 1993)


def ocho_inicial(dv=(0.0, 0.0)):
    """Posiciones y velocidades de la figura ocho (masas 1); `dv` se suma a la velocidad del cuerpo 3 (una «gemela» perturbada)."""
    x = np.array([OCHO_X1, -OCHO_X1, [0.0, 0.0]])
    v3 = OCHO_V3 + np.asarray(dv, float)
    v = np.array([-OCHO_V3 / 2, -OCHO_V3 / 2, v3])
    return x, v


def _deriv_n(t, y, m, suave=0.0):
    n = len(m)
    x = y[:2 * n].reshape(n, 2); v = y[2 * n:].reshape(n, 2)
    a = np.zeros_like(x)
    for i in range(n):
        for j in range(n):
            if i != j:
                d = x[j] - x[i]
                a[i] += m[j] * d / (d @ d + suave * suave) ** 1.5
    return np.concatenate([v.ravel(), a.ravel()])


def tres_cuerpos(x0, v0, m, t_fin, n_puntos=2000, suave=0.0):
    """Integra N cuerpos; devuelve (t, x[t, cuerpo, 2])."""
    n = len(m)
    y0 = np.concatenate([np.asarray(x0, float).ravel(), np.asarray(v0, float).ravel()])
    ts = np.linspace(0, t_fin, n_puntos)
    s = solve_ivp(_deriv_n, (0, t_fin), y0, t_eval=ts, args=(np.asarray(m, float), suave), method="DOP853", rtol=1e-11, atol=1e-12)
    return s.t, s.y[:2 * n].T.reshape(-1, n, 2), s.y[2 * n:].T.reshape(-1, n, 2)


def energia_n(x, v, m):
    k = 0.5 * sum(m[i] * v[i] @ v[i] for i in range(len(m)))
    u = -sum(m[i] * m[j] / np.linalg.norm(x[i] - x[j]) for i in range(len(m)) for j in range(i + 1, len(m)))
    return k + u


# ── Problema restringido de tres cuerpos (marco que gira, unidades: distancia entre primarios = 1, periodo = 2π) ─────────────
def _deriv_cr3bp(t, s, mu):
    x, y, vx, vy = s
    r1 = np.hypot(x + mu, y); r2 = np.hypot(x - 1 + mu, y)
    ax = 2 * vy + x - (1 - mu) * (x + mu) / r1 ** 3 - mu * (x - 1 + mu) / r2 ** 3
    ay = -2 * vx + y - (1 - mu) * y / r1 ** 3 - mu * y / r2 ** 3
    return [vx, vy, ax, ay]


def cr3bp(s0, mu, t_fin, n_puntos=3000, rtol=1e-12):
    ts = np.linspace(0, t_fin, n_puntos)
    s = solve_ivp(_deriv_cr3bp, (0, t_fin), s0, t_eval=ts, args=(mu,), method="DOP853", rtol=rtol, atol=1e-13)
    return s.t, s.y.T


def potencial(x, y, mu):
    """Potencial efectivo Ω (con signo: los «cerros» de Ω son valles del dibujo); Jacobi C = 2Ω − v²."""
    r1 = np.hypot(x + mu, y); r2 = np.hypot(x - 1 + mu, y)
    return 0.5 * (x * x + y * y) + (1 - mu) / r1 + mu / r2


def jacobi(s, mu):
    s = np.atleast_2d(s)
    return 2 * potencial(s[:, 0], s[:, 1], mu) - (s[:, 2] ** 2 + s[:, 3] ** 2)


def puntos_lagrange(mu):
    def fx(x):
        r1 = abs(x + mu); r2 = abs(x - 1 + mu)
        return x - (1 - mu) * (x + mu) / r1 ** 3 - mu * (x - 1 + mu) / r2 ** 3
    e = 1e-9
    L1 = brentq(fx, -mu + e, 1 - mu - e)
    L2 = brentq(fx, 1 - mu + e, 2.0)
    L3 = brentq(fx, -2.0, -mu - e)
    return {"L1": (L1, 0.0), "L2": (L2, 0.0), "L3": (L3, 0.0),
            "L4": (0.5 - mu, np.sqrt(3) / 2), "L5": (0.5 - mu, -np.sqrt(3) / 2)}


def separacion(s0, mu, delta, t_fin, n_puntos=3000, direccion=(1.0, 0.0, 0.0, 0.0)):
    """Dos trayectorias: la original y otra desplazada `delta` (en la dirección dada). Devuelve t, A, B y |A−B| (posición)."""
    d = np.asarray(direccion, float); d /= np.linalg.norm(d)
    t, a = cr3bp(s0, mu, t_fin, n_puntos)
    _, b = cr3bp(np.asarray(s0, float) + delta * d, mu, t_fin, n_puntos)
    return t, a, b, np.hypot(a[:, 0] - b[:, 0], a[:, 1] - b[:, 1])


# ── Coorbitales: Saturno + Jano + Epimeteo ───────────────────────────────────────────────────────────────────────────────
GM_SATURNO = 3.7931187e16            # m³/s²
M_SATURNO = 5.6834e26                # kg
M_JANO, M_EPIMETEO = 1.8975e18, 5.266e17      # kg (Cassini)
A_JANO = 151.46e6                    # m (semieje mayor medio de ambos, ~151 460 km)
DA_COORB = 50e3                      # m: diferencia entre sus órbitas (~50 km)


def coorbitales(anios=9.0, n_puntos=6000, fase_inicial=np.radians(60.0)):
    """Integra Saturno (en el origen, con su reflejo) + Jano + Epimeteo en el plano, masas reales, órbitas circulares separadas
    DA_COORB. Devuelve t (años), ángulo relativo (rad) y diferencia de radios (km) de Epimeteo respecto a Jano."""
    m = np.array([1.0, M_JANO / M_SATURNO, M_EPIMETEO / M_SATURNO])
    a0 = A_JANO
    escala_t = np.sqrt(a0 ** 3 / GM_SATURNO)                  # unidades: a0 = 1, GM = 1 → periodo 2π
    r_j, r_e = 1.0 + DA_COORB / 2 / a0, 1.0 - DA_COORB / 2 / a0
    x = np.array([[0.0, 0.0], [r_j, 0.0], [r_e * np.cos(fase_inicial), r_e * np.sin(fase_inicial)]])
    vj, ve = np.sqrt((1 + m[1]) / r_j), np.sqrt((1 + m[2]) / r_e)
    v = np.array([[0.0, 0.0], [0.0, vj], [-ve * np.sin(fase_inicial), ve * np.cos(fase_inicial)]])
    v[0] = -(m[1] * v[1] + m[2] * v[2])                       # centro de masa quieto
    t_fin = anios * 365.25 * 86400 / escala_t
    t, X, _ = tres_cuerpos(x, v, m, t_fin, n_puntos)
    rel_j = X[:, 1] - X[:, 0]; rel_e = X[:, 2] - X[:, 0]
    ang = np.unwrap(np.arctan2(rel_e[:, 1], rel_e[:, 0]) - np.arctan2(rel_j[:, 1], rel_j[:, 0]))
    dr = (np.hypot(*rel_e.T) - np.hypot(*rel_j.T)) * a0 / 1e3
    return t * escala_t / (365.25 * 86400), ang, dr


# ── Giro de una luna alargada en órbita excéntrica (Wisdom, Peale y Mignard, 1984) ─────────────────────────────────────────
def kepler_f_r(M, e):
    E = M.copy()
    for _ in range(50):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    f = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))
    return f, 1 - e * np.cos(E)


def giro_orbita(omega0, e, theta0, dtheta0, n_orbitas, n_puntos=4000):
    """θ'' = −(ω0²/2r³)·sin 2(θ − f), tiempo en órbitas×2π (n = 1), a = 1. Devuelve t (órbitas), θ, θ' (en unidades de n)."""
    def d(t, s):
        f, r = kepler_f_r(np.array([t]), e)
        return [s[1], -(omega0 ** 2) / (2 * r[0] ** 3) * np.sin(2 * (s[0] - f[0]))]
    ts = np.linspace(0, 2 * np.pi * n_orbitas, n_puntos)
    s = solve_ivp(d, (0, ts[-1]), [theta0, dtheta0], t_eval=ts, method="DOP853", rtol=1e-10, atol=1e-12)
    return s.t / (2 * np.pi), s.y[0], s.y[1]


# ── Asistencia gravitatoria ───────────────────────────────────────────────────────────────────────────────────────────────
MU_JUPITER = 1.26686534e8           # km³/s²
R_JUPITER = 71492.0                 # km
V_JUPITER = 13.07                   # km/s, velocidad orbital media


def sobrevuelo(v_inf, r_p, mu=MU_JUPITER):
    """Ángulo de giro δ (rad) de una hipérbola con v∞ y periapsis r_p; |Δv| = 2·v∞·sen(δ/2) en el marco del Sol."""
    e = 1 + r_p * v_inf ** 2 / mu
    delta = 2 * np.arcsin(1 / e)
    return delta, 2 * v_inf * np.sin(delta / 2)


# ── Cascada de Kessler (juguete) ─────────────────────────────────────────────────────────────────────────────────────────
def kessler(n0, lanzamientos, tau, k, anios, n_puntos=400):
    def d(t, y):
        return [lanzamientos - y[0] / tau + k * y[0] ** 2]
    ts = np.linspace(0, anios, n_puntos)
    tope = lambda t, y: y[0] - 1e4
    tope.terminal = True
    s = solve_ivp(d, (0, anios), [n0], t_eval=ts, rtol=1e-8, events=tope)
    y = np.full_like(ts, np.nan); y[:len(s.y[0])] = s.y[0]
    return ts, y


def horizonte_lyapunov(delta0, tau, tamano):
    """Tiempo para que un error delta0 crezca hasta `tamano` con e^(t/τ)."""
    return tau * np.log(tamano / delta0)


if __name__ == "__main__":
    x, v = ocho_inicial()
    m = np.ones(3)
    t, X, V = tres_cuerpos(x, v, m, OCHO_T, 400)
    assert np.abs(X[-1] - X[0]).max() < 1e-5                                   # la figura ocho cierra en un periodo
    assert abs(energia_n(X[-1], V[-1], m) - energia_n(X[0], V[0], m)) < 1e-9
    mu = 0.01215
    L = puntos_lagrange(mu)
    assert abs(L["L1"][0] - 0.8369) < 1e-3 and abs(L["L2"][0] - 1.1557) < 1e-3
    s0 = [L["L1"][0] - 0.01, 0.0, 0.0, 0.05]
    t, S = cr3bp(s0, mu, 10.0, 500)
    C = jacobi(S, mu)
    assert np.ptp(C) < 1e-8                                                     # Jacobi se conserva
    mu_se = 3.0035e-6                                                           # Sol–(Tierra+Luna)
    l2 = (puntos_lagrange(mu_se)["L2"][0] - (1 - mu_se)) * 1.496e8
    assert abs(l2 - 1.5e6) < 0.02e6
    d, dv = sobrevuelo(10.0, 5 * R_JUPITER)
    assert 1.7 < d < 1.9 and 15 < dv < 16
    assert abs(horizonte_lyapunov(15, 5e6, 1.5e11) - 5e6 * np.log(1e10)) < 1
    print("caos_gravedad: pruebas OK")
