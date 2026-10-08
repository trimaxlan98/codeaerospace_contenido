import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "studio/content/manim_extensions"))

from manim import *
from scipy.ndimage import gaussian_filter

import datos_clima as DC
from estilo_reel import Viva, cerrar_serie, chip, cola, leyenda, preparar_serie, punto, texto
from reels_promo import polilinea, suave

# SERIE «CLIMA ESPACIAL» — divulgación: cómo el Sol afecta a la Tierra, a los satélites, al GPS y a la radio.
# Tema SOLAR con fondo vertical propio (fondos_reel.py): el limbo del Sol vive en la franja de abajo y el centro NO se
# atenúa (al dueño no le gustó la «sombra oscura»). Mismo formato de película: título → cuerpo → logo → loop exacto.
# Pocas cifras, siempre con comparación cotidiana; fuentes en datos_clima.py.

FIN = 3.0
KICKER = "Clima espacial"
SERIE = dict(tema="solar", fondo="reel")
AZUL = "#3B8FD9"
VERDE, ROJO, VIOLETA = "#4ADE80", "#F87171", "#A78BFA"


def leyendas(escena, est, pel, nombre, textos):
    ts = list(DC.LEYENDAS[nombre]) + [DC.CUERPO[nombre] + FIN]
    for (g, p), a, b in zip(textos, ts[:-1], ts[1:]):
        leyenda(escena, est, pel, g, p, a, b)


def rampa(t, a, d=0.6):
    return suave((t - a) / d)


def fundir(m, k):
    """set_opacity(k) relativo al relleno y trazo originales (no vuelve opacos los rellenos transparentes)."""
    if not hasattr(m, "_base_op"):
        m._base_op = [(x, x.get_fill_opacity(), x.get_stroke_opacity()) for x in m.get_family() if isinstance(x, VMobject)]
    for x, f, s_ in m._base_op:
        x.set_fill(opacity=f * k, family=False).set_stroke(opacity=s_ * k, family=False)
    return m


def aparece(m, pel, t0, d=0.6, hasta=None):
    m.add_updater(lambda x: fundir(x, rampa(pel.t, t0, d) * (1 - rampa(pel.t, hasta, d) if hasta else 1)))
    fundir(m, 0)
    return m


def panel(est, x0, x1, y0, y1, op=0.55):
    return RoundedRectangle(corner_radius=0.2, width=x1 - x0, height=y1 - y0, stroke_width=1.6, stroke_color=est.linea,
                            fill_color=est.fondo, fill_opacity=op).move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0]).set_z_index(2)


def tierra(est, pos, r, dia_abajo=True):
    """La Tierra azul con el lado de noche hacia arriba (el Sol del fondo está abajo)."""
    g = VGroup(Circle(radius=r).set_fill(est.mezcla(est.fondo, AZUL, 0.62), 1).set_stroke(AZUL, 3))
    noche = AnnularSector(inner_radius=0, outer_radius=r * 0.985, angle=PI, start_angle=0).set_fill("#000000", 0.45).set_stroke(width=0)
    if not dia_abajo:
        noche.rotate(PI, about_point=ORIGIN)
    g.add(noche)
    g.add(Arc(radius=r * 0.75, start_angle=PI + 0.5, angle=0.9).set_stroke("#FFFFFF", 2.5, 0.35))
    return g.move_to(pos).set_z_index(6)


def flujo(x0, y0, a, y_max, paso=0.04, n=900):
    """Línea de corriente de un flujo uniforme hacia +y alrededor de un círculo de radio a (centro en el origen)."""
    def vel(x, y):
        z = complex(y, -x)                                   # marco girado: el flujo va hacia +x'
        if abs(z) < 1e-6:
            return 0.0, 1.0
        w = 1 - a * a / (z * z)
        u, v = w.real, -w.imag
        return -v, u
    pts = [(x0, y0)]
    x, y = x0, y0
    for _ in range(n):
        vx, vy = vel(x, y)
        xm, ym = x + vx * paso / 2, y + vy * paso / 2
        vx, vy = vel(xm, ym)
        x, y = x + vx * paso, y + vy * paso
        pts.append((x, y))
        if y > y_max:
            break
    p = np.array(pts)
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    return p, s


def zona(pos, arriba=5.3, abajo=-5.9, borde=0.7):
    """Opacidad que apaga lo que sale de la zona del diagrama (no pasa sobre el título ni la leyenda)."""
    y = pos[1]
    return float(np.clip((arriba - y) / borde, 0, 1) * np.clip((y - abajo) / borde, 0, 1))


def en_camino(p, s, d):
    d = float(np.clip(d, 0, s[-1]))
    return np.array([np.interp(d, s, p[:, 0]), np.interp(d, s, p[:, 1]), 0])


def disco_sol(n=420, semilla=5, manchas=()):
    yy, xx = np.mgrid[0:n, 0:n] / (n - 1) * 2 - 1
    r = np.hypot(xx, yy)
    mu = np.sqrt(np.clip(1 - r ** 2, 0, 1))
    rng = np.random.default_rng(semilla)
    g = gaussian_filter(rng.random((n, n)), 1.6); g = (g - g.min()) / (g.max() - g.min())
    b = (0.35 + 0.65 * mu ** 0.5) * (0.7 + 0.45 * g)
    for (mx, my, s) in manchas:
        d = np.hypot(xx - mx, yy - my)
        b *= 1 - 0.8 * np.exp(-(d / s) ** 2) - 0.25 * np.exp(-(d / (2.3 * s)) ** 2)
    cs = np.array([[90, 20, 2], [184, 54, 10], [234, 88, 12], [251, 146, 60], [253, 186, 116], [255, 241, 208]], float)
    v = np.clip(b, 0, 1) * (len(cs) - 1); i = np.minimum(v.astype(int), len(cs) - 2); f = (v - i)[..., None]
    rgb = cs[i] * (1 - f) + cs[i + 1] * f
    a = np.clip((1 - r) * n / 2, 0, 1) * 255
    return np.dstack([rgb, a]).astype(np.uint8)


def satelite(est, s=1.0, color=None):
    color = color or est.tinta
    cuerpo = Square(0.36 * s).set_fill(est.fondo, 1).set_stroke(color, 3)
    p1 = Rectangle(width=0.6 * s, height=0.26 * s).set_fill(AZUL, 0.6).set_stroke(color, 2).next_to(cuerpo, LEFT, buff=0.08 * s)
    p2 = p1.copy().next_to(cuerpo, RIGHT, buff=0.08 * s)
    return VGroup(p1, p2, cuerpo).set_z_index(8)


def torre(est, pos, s=1.0, color=None):
    color = color or est.tinta
    g = VGroup(Line(pos + LEFT * 0.3 * s, pos + UP * 0.9 * s, stroke_width=4, color=color),
               Line(pos + RIGHT * 0.3 * s, pos + UP * 0.9 * s, stroke_width=4, color=color),
               Line(pos + LEFT * 0.15 * s + UP * 0.45 * s, pos + RIGHT * 0.15 * s + UP * 0.45 * s, stroke_width=3, color=color))
    return g.set_z_index(8)


def ondas(pos, color, n=3, r0=0.25, paso=0.22):
    return VGroup(*[Arc(radius=r0 + paso * k, start_angle=-0.7, angle=1.4, stroke_width=4, color=color).shift(pos)
                    for k in range(n)] + [Arc(radius=r0 + paso * k, start_angle=PI - 0.7, angle=1.4, stroke_width=4, color=color).shift(pos)
                                          for k in range(n)]).set_z_index(8)


# ══ 1 · La luz del Sol tarda 8 minutos ═══════════════════════════════════════════════════════════════════════════════

class ReelSolLuz(Scene):
    VAR = 0

    def construct(self):
        n = "ReelSolLuz"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "La luz del Sol\ntarda 8 minutos", self.VAR, chip_txt="Ilustración", **SERIE)
        XP, Y0, YT = 4.4, -5.4, 3.5
        T0, T1 = 1.5, 13.5
        self.add(tierra(est, [XP, YT + 0.75, 0], 0.62))
        self.add(texto(est, "Tierra", 30, est.tinta, "cuerpo", "SEMIBOLD").move_to([XP - 1.45, YT + 0.75, 0]).set_z_index(9))
        self.add(DashedLine([XP, Y0, 0], [XP, YT, 0], stroke_width=2.5, color=est.tenue, dash_length=0.15).set_opacity(0.6).set_z_index(3))
        self.add(Arrow([XP, Y0 + 0.2, 0], [XP, Y0 - 0.55, 0], buff=0, stroke_width=4, color=est.acento).set_z_index(6))
        self.add(texto(est, "Sol", 30, est.acento, "cuerpo", "SEMIBOLD").move_to([XP - 0.85, Y0 - 0.2, 0]).set_z_index(9))
        dist = texto(est, "150 millones de km", 28, est.tenue).rotate(PI / 2).move_to([XP + 0.6, (Y0 + YT) / 2, 0]).set_z_index(9)
        self.add(dist)
        u = lambda: float(np.clip((pel.t - T0) / (T1 - T0), 0, 1))
        foton = punto(est.calido, 0.15)
        foton.add_updater(lambda m: fundir(m.move_to([XP, Y0 + u() * (YT - Y0), 0]), rampa(pel.t, T0 - 0.4, 0.4) * (1 - rampa(pel.t, T1 + 0.3, 0.4))))
        self.add(foton)
        cola(self, foton, est.calido, n=18, ancho=7.0)

        def reloj():
            s = int(round(u() * DC.LUZ_S))
            return f"{s // 60}:{s % 60:02d}"
        self.add(Viva(est, reloj, [-1.7, 1.4, 0], 150, est.tinta, f_op=lambda: rampa(pel.t, 0.6)))
        self.add(aparece(texto(est, "minutos de viaje", 40, est.tenue).move_to([-1.7, -0.25, 0]).set_z_index(9), pel, 0.6))
        llega = Circle(radius=0.7).set_stroke(est.calido, 6).move_to([XP, YT + 0.75, 0]).set_z_index(7)
        llega.add_updater(lambda m: m.set_stroke(opacity=0.9 * rampa(pel.t, T1, 0.3) * (1 - rampa(pel.t, T1 + 1.2, 1.0))).set(width=1.4 + 1.6 * rampa(pel.t, T1, 1.6)))
        self.add(llega)
        self.add(aparece(texto(est, "¡llegó!", 44, est.calido, "cuerpo", "SEMIBOLD").move_to([-1.7, -1.4, 0]).set_z_index(9), pel, T1))

        leyendas(self, est, pel, n, [
            ("La luz es lo más rápido que existe", "unos 300 000 km cada segundo"),
            ("Aun así, del Sol a aquí tarda 8 minutos", "nos separan 150 millones de km"),
            ("Ves el Sol como era hace 8 minutos", "mirar lejos es mirar al pasado")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 2 · El Sol sopla (viento solar) ══════════════════════════════════════════════════════════════════════════════════

class ReelSolViento(Scene):
    VAR = 1

    def construct(self):
        n = "ReelSolViento"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "El Sol\nsopla", self.VAR, chip_txt="Ilustración", **SERIE)
        C = np.array([0.0, 2.4, 0.0]); A = 2.0
        self.add(tierra(est, C, 0.7))
        escudo = DashedVMobject(Arc(radius=A, start_angle=PI, angle=PI, stroke_width=4, color=est.acento, arc_center=C), num_dashes=26).set_z_index(5)
        self.add(aparece(escudo, pel, 10.5))
        self.add(aparece(texto(est, "campo magnético", 30, est.acento, "cuerpo", "SEMIBOLD").move_to(C + DOWN * (A + 0.45)).set_z_index(9), pel, 11.0))
        rng = np.random.default_rng(3)
        V = 2.6
        for k in range(96):
            x0 = rng.uniform(-6.6, 6.6)
            if abs(x0) < 0.12:
                x0 = 0.12 * np.sign(x0 + 1e-9)
            p, s = flujo(x0, -8.2 - C[1], A, 12.9 - C[1] + 0.5)
            off = rng.uniform(0, s[-1])
            d_ = punto(est.calido if k % 3 else est.acento, 0.075)

            def mover(m, p=p, s=s, off=off):
                d = (off + V * pel.t) % s[-1]
                q = C + en_camino(p, s, d)
                fundir(m.move_to(q), rampa(pel.t, 0.4, 0.8) * 0.9 * zona(q))
            d_.add_updater(mover)
            self.add(d_)
        self.add(Viva(est, lambda: "≈ 400 km por segundo" if pel.t > 5.5 else " ", [0, -2.0, 0], 54, est.calido, f_op=lambda: rampa(pel.t, 5.5)))
        self.add(aparece(texto(est, "de CDMX a Monterrey en menos de 2 segundos", 30, est.tinta).move_to([0, -2.85, 0]).set_z_index(9), pel, 6.2, hasta=10.8))

        leyendas(self, est, pel, n, [
            ("El Sol lanza partículas sin parar", "a ese chorro se le llama viento solar"),
            ("Viajan a unos 400 km por segundo", "y llegan a la Tierra en unos días"),
            ("La Tierra tiene un escudo", "su campo magnético desvía casi todo")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 3 · El escudo invisible (magnetosfera) ═══════════════════════════════════════════════════════════════════════════

class ReelSolEscudo(Scene):
    VAR = 2

    def construct(self):
        n = "ReelSolEscudo"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "El escudo invisible\nde la Tierra", self.VAR, chip_txt="Ilustración", **SERIE)
        C = np.array([0.0, 0.7, 0.0]); RE = 0.6
        self.add(tierra(est, C, RE))
        k_ = lambda: rampa(pel.t, 6.5, 2.5)
        th = np.linspace(0.06, PI - 0.06, 160)
        for L in (1.6, 2.2, 3.0, 3.9, 4.8):
            for lado in (1, -1):
                linea = VMobject().set_z_index(5)

                def act(m, L=L, lado=lado):
                    r = L * RE * np.sin(th) ** 2
                    x, y = r * np.cos(th), lado * r * np.sin(th)
                    k = k_()
                    y = np.where(y < 0, y * (1 - 0.38 * k), y * (1 + 0.55 * k * L / 4.8))
                    x = np.where(y > 0, x * (1 - 0.12 * k * L / 4.8), x)
                    f = rampa(pel.t, 0.6 + 0.35 * L, 1.6)
                    m_ = max(int(len(th) * f), 2)
                    i0 = (len(th) - m_) // 2
                    pts = np.stack([x, y, 0 * x], 1)[i0:i0 + m_] + C
                    m.set_points_smoothly(pts).set_stroke(est.acento, 2.6, 0.75 * rampa(pel.t, 0.4)).set_fill(opacity=0)
                linea.add_updater(act)
                act(linea)
                self.add(linea)
        # viento solar desde abajo, que rodea el escudo
        rng = np.random.default_rng(8)
        for k in range(46):
            x0 = rng.uniform(-6.6, 6.6)
            x0 = x0 if abs(x0) > 0.15 else 0.15
            p, s = flujo(x0, -8.0 - C[1], 3.6, 12.6 - C[1])
            off = rng.uniform(0, s[-1])
            d_ = punto(est.calido, 0.045)
            def mover(m, p=p, s=s, off=off):
                q = C + en_camino(p, s, (off + 2.4 * pel.t) % s[-1])
                fundir(m.move_to(q), rampa(pel.t, 5.5, 1.0) * 0.85 * zona(q))
            d_.add_updater(mover)
            self.add(d_)
        # partículas que se cuelan por los polos y encienden auroras
        for k in range(8):
            lado, polo = (1, -1)[k % 2], (1, -1)[(k // 2) % 2]
            d_ = punto(VERDE, 0.06)

            def caer(m, lado=lado, polo=polo, k=k):
                fase = ((pel.t - 12.5) * 0.45 + k / 8) % 1.0
                tt = PI / 2 + polo * (PI / 2 - 0.42) * fase
                r = 2.2 * RE * np.sin(tt) ** 2
                kk = k_()
                y = lado * r * np.sin(tt); y = y * (1 - 0.38 * kk) if y < 0 else y * (1 + 0.55 * kk * 2.2 / 4.8)
                fundir(m.move_to(C + np.array([r * np.cos(tt), y, 0])), rampa(pel.t, 12.5, 0.6))
            d_.add_updater(caer)
            self.add(d_)
        for sx in (-1, 1):
            g = VGroup(*[Circle(radius=r).set_fill(VERDE, 0.16).set_stroke(width=0) for r in (0.16, 0.28, 0.42)]).move_to(C + RIGHT * sx * RE * 1.02).set_z_index(7)
            g.add_updater(lambda m: fundir(m, rampa(pel.t, 13.2, 1.0) * (0.75 + 0.25 * np.sin(5 * pel.t))))
            fundir(g, 0)
            self.add(g)
            self.add(aparece(texto(est, "aurora", 30, VERDE, "cuerpo", "SEMIBOLD").move_to(C + RIGHT * sx * 2.2 + UP * 0.0).set_z_index(9), pel, 13.6))
        self.add(aparece(texto(est, "viento solar", 30, est.calido, "cuerpo", "SEMIBOLD").move_to([-4.4, -4.7, 0]).set_z_index(9), pel, 6.0))

        leyendas(self, est, pel, n, [
            ("La Tierra es un imán gigante", "el hierro fundido de su núcleo crea un campo magnético"),
            ("El viento solar lo aplasta y lo estira", "del lado del Sol se comprime; del otro, forma una cola"),
            ("Algunas partículas se cuelan por los polos", "ahí nacen las auroras")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 4 · ¿Por qué hay auroras? (colores según la altura y el gas) ══════════════════════════════════════════════════════

class ReelSolAurora(Scene):
    VAR = 0

    def construct(self):
        n = "ReelSolAurora"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "¿Por qué hay\nauroras?", self.VAR, chip_txt="Ilustración", **SERIE)
        Y0, Y1, KM = -5.0, 5.0, 400
        yk = lambda km: Y0 + km / KM * (Y1 - Y0)
        XR = -6.15
        self.add(Line([XR, Y0, 0], [XR, Y1, 0], stroke_width=2.5, color=est.tenue).set_z_index(5))
        for km in (100, 200, 300):
            self.add(Line([XR, yk(km), 0], [XR + 0.22, yk(km), 0], stroke_width=2.5, color=est.tenue).set_z_index(5))
            self.add(texto(est, f"{km} km", 24, est.tenue).move_to([XR + 0.35, yk(km), 0], aligned_edge=LEFT).set_z_index(9))
        self.add(texto(est, "Estación Espacial · 400 km", 24, est.tinta).move_to([XR + 0.3, yk(400) - 0.05, 0], aligned_edge=LEFT).set_z_index(9))
        self.add(texto(est, "aviones · 10 km", 24, est.tinta).move_to([XR + 0.3, yk(10) + 0.3, 0], aligned_edge=LEFT).set_z_index(9))
        rng = np.random.default_rng(12)
        xs = np.linspace(-0.6, 6.4, 110)
        fase = rng.uniform(0, TAU, len(xs))
        capas = [(85, 100, VIOLETA, 12.6), (100, 250, VERDE, 6.0), (250, 400, ROJO, 12.6)]
        for j, x in enumerate(xs):
            for (a, b, col, t0) in capas:
                ln = Line([x, yk(a), 0], [x, yk(b), 0], stroke_width=5.5, color=col).set_z_index(4)
                base = 0.8 if col == VERDE else (0.55 if col == ROJO else 0.7)
                env = np.exp(-((x - 2.9) / 3.0) ** 2)

                def act(m, x=x, a=a, b=b, t0=t0, base=base, env=env, j=j):
                    dx = 0.35 * np.sin(0.9 * x + 0.8 * pel.v) + 0.15 * np.sin(2.3 * x - 1.3 * pel.v)
                    m.put_start_and_end_on([x + dx, yk(a), 0], [x + dx * 1.4, yk(b), 0])
                    brillo = 0.6 + 0.4 * np.sin(1.7 * pel.v + fase[j])
                    m.set_stroke(opacity=base * env * brillo * rampa(pel.t, t0 + 0.006 * j, 0.8))
                ln.add_updater(act)
                act(ln)
                self.add(ln)
        for k in range(26):                                    # partículas que caen y chocan con el aire
            x0, h, t0 = rng.uniform(-0.4, 6.2), rng.uniform(110, 300), rng.uniform(0.8, 5.5)
            d_ = punto(est.calido, 0.05)

            def caer(m, x0=x0, h=h, t0=t0):
                e = (pel.t - t0) % 2.2
                y = Y1 + 0.6 - (Y1 + 0.6 - yk(h)) * min(e / 1.2, 1)
                op = rampa(pel.t, t0, 0.2) * (1 if e < 1.2 else max(0, 1 - (e - 1.2) / 0.3)) * (1 - rampa(pel.t, 7.5, 1.0))
                fundir(m.move_to([x0, y, 0]), op)
            d_.add_updater(caer)
            self.add(d_)
        monte = Polygon(*[[x, Y0 + 0.4 * np.sin(1.3 * x) * np.cos(0.4 * x) + 0.35, 0] for x in np.linspace(-7.2, 7.2, 40)], [7.2, Y0 - 0.6, 0], [-7.2, Y0 - 0.6, 0])
        self.add(monte.set_fill("#060201", 1).set_stroke(width=0).set_z_index(5))
        for s, col, km, t0 in (("oxígeno: verde", VERDE, 170, 7.0), ("oxígeno alto: rojo", ROJO, 320, 13.0), ("nitrógeno: violeta", VIOLETA, 70, 13.6)):
            self.add(aparece(texto(est, s, 30, col, "cuerpo", "SEMIBOLD", ancho_max=3.6).move_to([-2.65, yk(km), 0]).set_z_index(9), pel, t0))

        leyendas(self, est, pel, n, [
            ("Partículas del Sol chocan con el aire", "muy arriba: a más de 100 km de altura"),
            ("Cada gas brilla de un color", "el oxígeno da verde y rojo; el nitrógeno, violeta"),
            ("Como un letrero de neón gigante", "gas que brilla al recibir energía")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 5 · Manchas en el Sol (y el ciclo de 11 años) ════════════════════════════════════════════════════════════════════

class ReelSolManchas(Scene):
    VAR = 1

    def construct(self):
        n = "ReelSolManchas"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Manchas\nen el Sol", self.VAR, chip_txt="Curva aproximada", **SERIE)
        S = np.array([-1.9, 2.75, 0]); RS = 2.35
        disco = ImageMobject(disco_sol(manchas=((0.25, -0.15, 0.09), (0.36, -0.08, 0.05), (-0.35, 0.3, 0.07)))).set_z_index(5)
        disco.stretch_to_fit_width(2 * RS).stretch_to_fit_height(2 * RS).move_to(S)
        disco.add_updater(lambda m: m.set_opacity(rampa(pel.t, 0.3)))
        self.add(disco)
        p_mancha = S + RS * np.array([0.25, 0.15, 0])
        p_sup = S + RS * np.array([-0.55, -0.45, 0])
        for p, s, col, t0, y in ((p_sup, f"≈ {DC.FOTOSFERA_C:,} °C".replace(",", " "), est.calido, 1.5, 3.9), (p_mancha, f"≈ {DC.MANCHA_C:,} °C".replace(",", " "), est.tinta, 3.0, 2.2)):
            et = texto(est, s, 40, col, "cifra", "SEMIBOLD").move_to([4.3, y, 0]).set_z_index(9)
            ln = Line(p, et.get_left() + LEFT * 0.15, stroke_width=2.5, color=col).set_z_index(8)
            self.add(aparece(VGroup(ln, et), pel, t0))
        self.add(aparece(texto(est, "mancha: más fría", 28, est.tenue).move_to([4.3, 1.55, 0]).set_z_index(9), pel, 3.4))
        self.add(aparece(texto(est, "superficie", 28, est.tenue).move_to([4.3, 3.25, 0]).set_z_index(9), pel, 1.9))
        # la curva del ciclo solar
        X0, X1, GY0, GY1 = -5.6, 5.9, -5.3, -1.1
        A0, A1 = 1986.5, 2027.5
        fx = lambda a: X0 + (a - A0) / (A1 - A0) * (X1 - X0)
        fy = lambda v: GY0 + v / 230 * (GY1 - GY0)
        self.add(aparece(panel(est, X0 - 0.4, X1 + 0.35, GY0 - 0.75, GY1 + 0.35), pel, 6.0))
        for a in (1990, 2000, 2010, 2020):
            self.add(aparece(texto(est, str(a), 24, est.tenue).move_to([fx(a), GY0 - 0.38, 0]).set_z_index(9), pel, 6.2))
        anios = np.linspace(A0, DC.FIN_CURVA, 400)
        valores = DC.manchas(anios)
        curva = VMobject().set_z_index(7)

        def dibujar(m):
            f = rampa(pel.t, 6.8, 5.5)
            k = max(int(len(anios) * f), 2)
            m.set_points_smoothly([[fx(a), fy(v), 0] for a, v in zip(anios[:k], valores[:k])]).set_stroke(est.acento, 4.5, rampa(pel.t, 6.6, 0.3)).set_fill(opacity=0)
        curva.add_updater(dibujar)
        dibujar(curva)
        self.add(curva)
        m0, m1 = DC.CICLOS[2][0], DC.CICLOS[3][0]
        llave = VGroup(Line([fx(m0), fy(30), 0], [fx(m1), fy(30), 0], stroke_width=3, color=est.calido),
                       Line([fx(m0), fy(18), 0], [fx(m0), fy(42), 0], stroke_width=3, color=est.calido),
                       Line([fx(m1), fy(18), 0], [fx(m1), fy(42), 0], stroke_width=3, color=est.calido),
                       texto(est, "≈ 11 años", 28, est.calido, "cuerpo", "SEMIBOLD").move_to([(fx(m0) + fx(m1)) / 2, fy(56), 0])).set_z_index(8)
        self.add(aparece(llave, pel, 11.0))
        hoy = VGroup(Dot([fx(DC.FIN_CURVA), fy(float(DC.manchas(DC.FIN_CURVA))), 0], radius=0.11, color=est.calido),
                     texto(est, "hoy", 28, est.calido, "cuerpo", "SEMIBOLD").move_to([fx(DC.FIN_CURVA) + 0.05, fy(float(DC.manchas(DC.FIN_CURVA))) - 0.45, 0])).set_z_index(9)
        self.add(aparece(hoy, pel, 12.6))
        mx = DC.CICLOS[3][1]
        self.add(aparece(texto(est, "máximo", 26, est.tinta).move_to([fx(mx) - 0.2, fy(DC.CICLOS[3][2]) + 0.35, 0]).set_z_index(9), pel, 13.2))

        leyendas(self, est, pel, n, [
            ("Las manchas son zonas más frías", "unos 2 000 °C menos: por contraste se ven oscuras"),
            ("Su número sube y baja cada 11 años", "a eso se le llama el ciclo solar"),
            ("Acabamos de pasar un máximo", "más manchas, más tormentas solares")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 6 · Un destello que apaga la radio (llamarada) ═══════════════════════════════════════════════════════════════════

class ReelSolLlamarada(Scene):
    VAR = 2

    def construct(self):
        n = "ReelSolLlamarada"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Un destello que\napaga la radio", self.VAR, chip_txt="Ilustración", **SERIE)
        C = np.array([0.0, 2.7, 0.0]); RT = 1.35
        self.add(tierra(est, C, RT))
        F0, T0, T1 = 1.2, 2.0, 8.5
        destello = VGroup(*[Circle(radius=r).set_fill("#FFF4D6", 0.18).set_stroke(width=0) for r in (0.3, 0.6, 1.0, 1.6, 2.3)]).move_to([0.6, -6.0, 0]).set_z_index(6)
        destello.add_updater(lambda m: fundir(m, np.exp(-((pel.t - F0 - 0.5) / 0.6) ** 2) * 1.0 + 0.0))
        fundir(destello, 0)
        self.add(destello)
        frente = VMobject().set_z_index(6)
        CS = np.array([0.6, -7.2, 0])

        def onda(m):
            u = float(np.clip((pel.t - T0) / (T1 - T0), 0, 1))
            r = 1.6 + u * (np.linalg.norm(C - CS) - RT - 1.6)
            a = np.linspace(PI / 2 - 0.75, PI / 2 + 0.75, 60)
            m.set_points_smoothly([CS + r * np.array([np.cos(x), np.sin(x), 0]) for x in a])
            m.set_stroke(est.calido, 6, 0.9 * rampa(pel.t, T0, 0.3) * (1 - rampa(pel.t, T1, 0.4))).set_fill(opacity=0)
        frente.add_updater(onda)
        onda(frente)
        self.add(frente)
        self.add(Viva(est, lambda: f"{int(round(8 * float(np.clip((pel.t - T0) / (T1 - T0), 0, 1))))} min", [-4.3, -1.6, 0], 76, est.calido,
                      f_op=lambda: rampa(pel.t, T0, 0.4)))
        self.add(aparece(texto(est, "en llegar", 32, est.tenue).move_to([-4.3, -2.55, 0]).set_z_index(9), pel, T0))
        dia = Arc(radius=RT + 0.18, start_angle=PI, angle=PI, stroke_width=10, color=est.calido).move_arc_center_to(C).set_z_index(7)
        dia.add_updater(lambda m: m.set_stroke(opacity=0.85 * rampa(pel.t, T1, 0.5)))
        self.add(dia)
        pd, pn = C + np.array([-3.9, -1.4, 0]), C + np.array([3.9, 0.7, 0])
        self.add(torre(est, pd), torre(est, pn))
        o_d, o_n = ondas(pd + UP * 1.05, VERDE), ondas(pn + UP * 1.05, VERDE)
        o_d.add_updater(lambda m: fundir(m.set_color(ROJO if pel.t > T1 + 0.4 else VERDE), (0.25 if pel.t > T1 + 0.4 else 0.9) * rampa(pel.t, 0.5)))
        o_n.add_updater(lambda m: fundir(m, 0.9 * rampa(pel.t, 0.5)))
        self.add(o_d, o_n)
        tache = VGroup(Line(LEFT * 0.4 + DOWN * 0.4, RIGHT * 0.4 + UP * 0.4, stroke_width=8, color=ROJO), Line(LEFT * 0.4 + UP * 0.4, RIGHT * 0.4 + DOWN * 0.4, stroke_width=8, color=ROJO)).move_to(pd + UP * 1.05).set_z_index(9)
        self.add(aparece(tache, pel, T1 + 0.4))
        self.add(aparece(texto(est, "lado de día: sin radio", 30, ROJO, "cuerpo", "SEMIBOLD").move_to(pd + DOWN * 0.55 + RIGHT * 0.6).set_z_index(9), pel, T1 + 0.8))
        self.add(aparece(texto(est, "lado de noche: bien", 30, VERDE, "cuerpo", "SEMIBOLD").move_to(pn + DOWN * 0.55 + LEFT * 0.1).set_z_index(9), pel, T1 + 1.4))

        leyendas(self, est, pel, n, [
            ("Una llamarada es una explosión en el Sol", "libera muchísima energía en minutos"),
            ("Su luz llega en 8 minutos", "rayos X que alteran la capa alta del aire"),
            ("La radio de onda corta se cae", "del lado de la Tierra que mira al Sol")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 7 · Una nube de plasma (eyección de masa coronal) ════════════════════════════════════════════════════════════════

class ReelSolEyeccion(Scene):
    VAR = 0

    def construct(self):
        n = "ReelSolEyeccion"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Una nube\nde plasma", self.VAR, chip_txt="Ilustración", **SERIE)
        C = np.array([0.0, 3.6, 0.0]); RT = 0.72
        self.add(tierra(est, C, RT))
        T0, T1 = 1.0, 11.0
        golpe = lambda: rampa(pel.t, T1, 0.8)
        escudo = VMobject().set_z_index(5)

        def esc(m):
            g = golpe()
            r = 1.75 - 0.6 * g + 0.06 * g * np.sin(9 * pel.t)
            a = np.linspace(PI + 0.15, TAU - 0.15, 50)
            m.set_points_smoothly([C + np.array([r * 1.25 * np.cos(x), r * np.sin(x), 0]) for x in a])
            m.set_stroke(est.acento, 3.5, 0.8 * rampa(pel.t, 0.4)).set_fill(opacity=0)
        escudo.add_updater(esc)
        esc(escudo)
        self.add(escudo)
        nube = VMobject().set_z_index(6)
        CB = np.array([0.0, -5.9, 0])
        u = lambda: suave(float(np.clip((pel.t - T0) / (T1 - T0), 0, 1)))
        frente_max = (C[1] - 1.75 * 0.68) - CB[1]

        def bulbo(m):
            R = 1.2 + u() * (frente_max - 1.2)
            a = np.linspace(0.12, PI - 0.12, 90)
            rr = R * (0.55 + 0.45 * np.sin(a) ** 1.5) * (1 + 0.03 * np.sin(7 * a + 2 * pel.v))
            pts = [CB + np.array([r * 0.62 * np.cos(x), r * np.sin(x), 0]) for r, x in zip(rr, a)]
            op = rampa(pel.t, T0 - 0.2, 0.6) * (1 - rampa(pel.t, T1 + 1.5, 1.5))
            m.set_points_smoothly(pts).set_stroke(est.calido, 5, 0.9 * op).set_fill(est.acento, 0.14 * op)
        nube.add_updater(bulbo)
        bulbo(nube)
        self.add(nube)
        lazos = VMobject().set_z_index(6)

        def interiores(m):
            R = 1.2 + u() * (frente_max - 1.2)
            op = rampa(pel.t, T0, 0.6) * (1 - rampa(pel.t, T1 + 1.5, 1.5))
            g = VGroup(*[ArcBetweenPoints(CB + np.array([-0.62 * R * f, R * 0.15, 0]), CB + np.array([0.62 * R * f, R * 0.15, 0]), angle=-PI * 0.9)
                         for f in (0.35, 0.55, 0.75)])
            m.become(g.set_stroke(est.calido, 2.5, 0.45 * op).set_fill(opacity=0).set_z_index(6))
        lazos.add_updater(interiores)
        interiores(lazos)
        self.add(lazos)
        self.add(Viva(est, lambda: f"viaje: día {min(3, int(u() * 3) + 1)}" if T0 < pel.t < T1 + 0.5 else (" " if pel.t <= T0 else "¡llegó!"),
                      [-4.3, 3.6, 0], 46, est.calido, f_op=lambda: rampa(pel.t, T0)))
        aur = VGroup(*[Circle(radius=r).set_fill(VERDE, 0.18).set_stroke(width=0) for r in (0.15, 0.27, 0.4)])
        for sx in (-1, 1):
            g = aur.copy().move_to(C + RIGHT * sx * RT).set_z_index(7)
            g.add_updater(lambda m: fundir(m, golpe() * (0.7 + 0.3 * np.sin(6 * pel.t))))
            fundir(g, 0)
            self.add(g)
        self.add(aparece(chip(est, "tormenta geomagnética", ROJO, 30).move_to([3.9, 1.9, 0]), pel, T1 + 0.6))

        leyendas(self, est, pel, n, [
            ("A veces el Sol escupe una nube enorme", "unos mil millones de toneladas de gas caliente"),
            ("Tarda de 1 a 3 días en llegar", "por eso hay tiempo de avisar"),
            ("Al chocar, provoca una tormenta", "auroras, apagones y satélites en riesgo")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 8 · Cuando el Sol frena satélites (Starlink, febrero de 2022) ════════════════════════════════════════════════════

class ReelSolSatelites(Scene):
    VAR = 1

    def construct(self):
        n = "ReelSolSatelites"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Cuando el Sol\nfrena satélites", self.VAR, chip_txt="Hecho real · feb 2022", **SERIE)
        C = np.array([0.0, -0.5, 0.0]); RT, RO = 2.5, 3.55
        caps = lambda: 0.22 + 0.75 * rampa(pel.t, 5.5, 3.0)
        aire = VMobject().set_z_index(5)

        def inflar(m):
            h = caps()
            m.become(Annulus(inner_radius=RT, outer_radius=RT + h).move_to(C).set_fill(AZUL, 0.22 + 0.12 * rampa(pel.t, 5.5, 3.0)).set_stroke(width=0).set_z_index(5))
        aire.add_updater(inflar)
        inflar(aire)
        self.add(aire, tierra(est, C, RT))
        self.add(DashedVMobject(Circle(radius=RO).move_to(C).set_stroke(est.tenue, 2), num_dashes=70).set_opacity(0.5).set_z_index(4))
        tot, caen = DC.STARLINK[1], DC.STARLINK[0]
        rng = np.random.default_rng(22)
        condena = set(rng.choice(tot, caen, replace=False))
        tcaida = {i: 9.5 + rng.uniform(0, 5.0) for i in condena}
        W_ = 0.16
        for i in range(tot):
            a0 = np.radians(160 - i * 2.9)
            d_ = Dot(radius=0.07, color=est.calido).set_z_index(8)

            def mover(m, i=i, a0=a0):
                a = a0 - W_ * pel.t
                r = RO
                op = rampa(pel.t, 0.3 + 0.02 * i, 0.3)
                if i in condena:
                    e = max(pel.t - tcaida[i], 0)
                    r = RO - 0.35 * e ** 1.6
                    if r < RT + caps() * 0.4:
                        op *= max(0, 1 - (RT + caps() * 0.4 - r) / 0.25)
                    m.set_color(ROJO if e > 0 else est.calido)
                m.move_to(C + r * np.array([np.cos(a), np.sin(a), 0])).set_opacity(op)
            d_.add_updater(mover)
            self.add(d_)

        def cuenta():
            k = sum(1 for i in condena if RO - 0.35 * max(pel.t - tcaida[i], 0) ** 1.6 < RT + caps() * 0.4)
            return f"cayeron {k} de {tot}"
        self.add(Viva(est, cuenta, [0, -4.95, 0], 52, ROJO, f_op=lambda: rampa(pel.t, 9.5)))
        self.add(aparece(texto(est, "la atmósfera se infla", 32, AZUL, "cuerpo", "SEMIBOLD").move_to(C).set_z_index(9), pel, 6.0))
        self.add(aparece(texto(est, f"{tot} satélites recién lanzados", 30, est.calido).move_to([0, C[1] + RO + 0.55, 0]).set_z_index(9), pel, 0.8))

        leyendas(self, est, pel, n, [
            ("Una tormenta solar calienta el aire de arriba", "la atmósfera se infla como un globo"),
            ("Los satélites bajos se frenan y caen", "en 2022, unos 40 de 49 satélites nuevos se perdieron"),
            ("Por eso se vigila el clima espacial", "para decidir cuándo lanzar y cómo proteger")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 9 · El GPS también siente al Sol (ionosfera) ═════════════════════════════════════════════════════════════════════

class ReelSolGps(Scene):
    VAR = 2

    def construct(self):
        n = "ReelSolGps"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "El GPS también\nsiente al Sol", self.VAR, chip_txt="Ilustración", **SERIE)
        S = np.array([-3.6, 4.3, 0]); R = np.array([2.6, -1.25, 0])
        self.add(satelite(est).move_to(S), texto(est, "satélite GPS", 28, est.tenue).move_to(S + RIGHT * 2.3).set_z_index(9))
        k = lambda: rampa(pel.t, 6.5, 2.5)
        YB, YT_ = 1.0, 2.4
        xs = np.linspace(-7.1, 7.1, 80)
        capa = VMobject().set_z_index(4)

        def ondular(m):
            kk = k()
            arr = YT_ + (0.12 + 0.5 * kk) * np.sin(1.3 * xs + 1.2 * pel.v) + 0.25 * kk * np.sin(3.1 * xs - 2.1 * pel.v)
            aba = YB + (0.10 + 0.45 * kk) * np.sin(1.1 * xs - 1.0 * pel.v + 1) + 0.2 * kk * np.sin(2.7 * xs + 1.7 * pel.v)
            pts = [[x, y, 0] for x, y in zip(xs, arr)] + [[x, y, 0] for x, y in zip(xs[::-1], aba[::-1])]
            m.set_points_as_corners(pts + [pts[0]]).set_fill(VIOLETA, (0.16 + 0.16 * kk) * rampa(pel.t, 0.4)).set_stroke(VIOLETA, 2, 0.5 * rampa(pel.t, 0.4))
        capa.add_updater(ondular)
        ondular(capa)
        self.add(capa)
        self.add(aparece(texto(est, "ionosfera", 30, VIOLETA, "cuerpo", "SEMIBOLD").move_to([4.9, 3.25, 0]).set_z_index(9), pel, 1.0))
        rayo = VMobject().set_z_index(7)

        def trazar(m):
            kk = k()
            d = (R - S) / np.linalg.norm(R - S)
            p1 = S + d * (S[1] - YT_) / -d[1]
            p2 = S + d * (S[1] - YB) / -d[1] + np.array([0.9 * kk * np.sin(4 * pel.v) * 0.4 + 0.5 * kk, 0, 0])
            m.set_points_as_corners([S, p1, p2, R]).set_stroke(est.calido, 4, rampa(pel.t, 0.6)).set_fill(opacity=0)
        rayo.add_updater(trazar)
        trazar(rayo)
        self.add(rayo)
        tel = VGroup(RoundedRectangle(corner_radius=0.1, width=0.5, height=0.85).set_fill(est.fondo, 1).set_stroke(est.tinta, 3),
                     Circle(radius=0.05).set_fill(est.tinta, 1).set_stroke(width=0).shift(DOWN * 0.3)).move_to(R + DOWN * 0.3).set_z_index(8)
        self.add(tel)
        # mapa: el círculo de error crece
        MX0, MX1, MY0, MY1 = -6.2, 6.2, -5.5, -2.4
        self.add(panel(est, MX0, MX1, MY0, MY1, 0.7))
        for x in np.linspace(MX0 + 0.8, MX1 - 0.8, 8):
            self.add(Line([x, MY0 + 0.1, 0], [x + 0.6, MY1 - 0.1, 0], stroke_width=2, color=est.linea).set_z_index(3))
        for y in np.linspace(MY0 + 0.5, MY1 - 0.5, 4):
            self.add(Line([MX0 + 0.1, y, 0], [MX1 - 0.1, y, 0], stroke_width=2, color=est.linea).set_z_index(3))
        P = np.array([-1.8, (MY0 + MY1) / 2, 0])
        circ = Circle(radius=0.3).set_z_index(6)
        circ.add_updater(lambda m: m.become(Circle(radius=0.3 + 1.05 * k()).move_to(P).set_fill(est.acento, 0.22).set_stroke(est.acento, 3).set_z_index(6)))
        pin = VGroup(Circle(radius=0.16).set_fill(est.calido, 1).set_stroke(width=0), Triangle().scale(0.12).rotate(PI).set_fill(est.calido, 1).set_stroke(width=0).shift(DOWN * 0.2)).move_to(P + UP * 0.12).set_z_index(8)
        self.add(circ, pin)
        self.add(Viva(est, lambda: "error: unos metros" if k() < 0.5 else "error: decenas de metros", [2.9, P[1], 0], 40,
                      est.tinta, rol="cuerpo", f_op=lambda: rampa(pel.t, 0.8)))

        leyendas(self, est, pel, n, [
            ("La señal del GPS cruza la ionosfera", "una capa del aire cargada eléctricamente"),
            ("Con el Sol activo, esa capa se agita", "la señal se retrasa y se desvía"),
            ("Tu ubicación puede fallar por decenas de metros", "importa a aviones, barcos y al campo")])
        cerrar_serie(self, est, pel, self.VAR)


# ══ 10 · Auroras en México (tres tormentas históricas) ═══════════════════════════════════════════════════════════════

class ReelSolTormenta(Scene):
    VAR = 0

    def construct(self):
        n = "ReelSolTormenta"; TB = DC.CUERPO[n]
        est, pel = preparar_serie(self, TB, KICKER, "Tres tormentas\nque hicieron historia", self.VAR, chip_txt="Hechos reales", **SERIE)
        tarjetas = [(str(DC.CARRINGTON), "La tormenta más grande registrada", "los telégrafos soltaban chispas", 0.5, 4.0),
                    (str(DC.QUEBEC), "Quebec, Canadá, sin luz", f"{DC.QUEBEC_HORAS} horas, {DC.QUEBEC_MILLONES} millones de personas", 6.0, 1.45),
                    (str(DC.GANNON), "Auroras vistas desde México", f"la tormenta más fuerte en {DC.GANNON_ANOS} años", 12.0, -1.1)]
        self.add(Line([-5.9, 4.6, 0], [-5.9, -1.7, 0], stroke_width=3, color=est.linea).set_z_index(3))
        for k, (anio, a, b, t0, y) in enumerate(tarjetas):
            sig = tarjetas[k + 1][3] if k + 1 < len(tarjetas) else None
            caja = RoundedRectangle(corner_radius=0.18, width=11.9, height=2.15).set_fill(est.fondo, 0.75).set_stroke(est.calido if k == 2 else est.linea, 2.5).move_to([0.45, y, 0]).set_z_index(5)
            nodo = Dot([-5.9, y, 0], radius=0.15, color=est.calido).set_z_index(6)
            g = VGroup(caja, nodo,
                       texto(est, anio, 80, est.calido, "cifra", "SEMIBOLD").move_to([-4.0, y, 0]),
                       texto(est, a, 40, est.tinta, "cuerpo", "SEMIBOLD", ancho_max=8.0).move_to([-2.3, y + 0.42, 0], aligned_edge=LEFT),
                       texto(est, b, 34, est.tenue, "cuerpo", "MEDIUM", ancho_max=8.0).move_to([-2.3, y - 0.45, 0], aligned_edge=LEFT)).set_z_index(6)

            def act(m, t0=t0, sig=sig):
                fundir(m, rampa(pel.t, t0, 0.7) * (1 - 0.45 * (rampa(pel.t, sig, 0.7) if sig else 0)))
            g.add_updater(act)
            fundir(g, 0)
            self.add(g)
        # cielo de México con aurora roja (a baja latitud se ve roja y rosa)
        SX0, SX1, SY0, SY1 = -6.4, 6.4, -5.6, -2.6
        self.add(aparece(panel(est, SX0, SX1, SY0, SY1, 0.8), pel, 12.0))
        xs = np.linspace(SX0 + 0.3, SX1 - 0.3, 90)
        for j, x in enumerate(xs):
            ln = Line([x, SY0 + 0.6, 0], [x, SY1 - 0.2, 0]).set_z_index(4)

            def act(m, x=x, j=j):
                h = 0.55 + 0.35 * np.sin(0.8 * x + 0.9 * pel.v) + 0.15 * np.sin(2.1 * x - 1.4 * pel.v)
                m.put_start_and_end_on([x, SY0 + 0.7, 0], [x, SY0 + 0.7 + h * (SY1 - SY0 - 1.0), 0])
                m.set_stroke(ROJO if j % 3 else "#F9A8D4", 4, 0.45 * rampa(pel.t, 12.4 + 0.01 * j, 0.8) * (0.7 + 0.3 * np.sin(2 * pel.v + j)))
            ln.add_updater(act)
            act(ln)
            self.add(ln)
        cerro = Polygon(*[[x, SY0 + 0.55 + 0.35 * np.sin(1.1 * x) * np.cos(0.5 * x) + 0.2, 0] for x in np.linspace(SX0 + 0.05, SX1 - 0.05, 40)],
                        [SX1 - 0.05, SY0 + 0.05, 0], [SX0 + 0.05, SY0 + 0.05, 0]).set_fill("#060201", 1).set_stroke(width=0).set_z_index(5)
        self.add(aparece(cerro, pel, 12.0))

        leyendas(self, est, pel, n, [
            ("1859: la tormenta de Carrington", "hubo auroras casi hasta el Caribe"),
            ("1989: un apagón en Canadá", "la tormenta dañó la red eléctrica de Quebec"),
            ("2024: auroras en el cielo de México", "fenómenos raros que hoy podemos prever")])
        cerrar_serie(self, est, pel, self.VAR)
