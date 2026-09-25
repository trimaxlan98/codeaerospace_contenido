class Clip2(Scene):
    """8.2.2 - La misma geometria del clip 1 (frentes, dos antenas, d =
    lambda/2), ahora leida como un angulo: la relacion Delta-phi = 2 pi
    (d/lambda) sen theta y su despeje dan theta = 25.0 grados (ANG_05[0],
    SNR 10 dB). (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El angulo"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- la misma geometria: antenas, frentes, normal y arco -------------
        D_VIS = 2.9
        Y0 = -0.55
        a_izq = np.array([-D_VIS / 2, Y0, 0.0])
        a_der = np.array([D_VIS / 2, Y0, 0.0])

        def antena(pos):
            palo = Line(pos, pos + UP * 0.4, color=C_TENUE, stroke_width=2.6)
            base = Dot(pos, radius=0.075, color=C_TENUE)
            return VGroup(palo, base)

        an1, an2 = antena(a_izq), antena(a_der)
        base_linea = Line(a_izq, a_der, color=C_EJE, stroke_width=1.8)
        centro = (a_izq + a_der) / 2.0

        th = math.radians(THETA)
        p = np.array([math.sin(th), -math.cos(th), 0.0])   # propagacion
        w = np.array([math.cos(th), math.sin(th), 0.0])    # a lo largo
        # Los frentes viven del lado de -p (de donde VIENE la onda, igual
        # que la flecha): ARRIBA de las antenas, nunca por debajo. El t
        # minimo (1.4) y el semilargo (2.6) se eligieron para que ningun
        # frente baje de la base ni se salga del cuadro por arriba.
        L_FRENTE = 2.0
        frentes = VGroup(*[
            Line(centro - p * t - w * L_FRENTE, centro - p * t + w * L_FRENTE,
                color=C_SENAL, stroke_width=2.0, stroke_opacity=0.55)
            for t in (1.2, 1.75, 2.3)])

        normal = DashedLine(centro, centro + UP * 2.3, color=C_TENUE,
                            stroke_width=2.0, dash_length=0.1)
        et_normal = tag_junto(normal, "normal", DOWN, buff=0.18, font_size=18)
        flecha = Arrow(centro - p * 2.7, centro, color=C_SENAL,
                      stroke_width=3.0, tip_length=0.2, buff=0.0)
        arco = Arc(radius=0.85, start_angle=PI / 2, angle=-th,
                  arc_center=centro, color=C_DATO, stroke_width=2.4)

        grupo = VGroup(frentes, base_linea, an1, an2, normal, et_normal,
                       flecha, arco)
        self.play(FadeIn(frentes), Create(base_linea), FadeIn(an1),
                  FadeIn(an2), run_time=1.0)
        self.play(Create(normal), FadeIn(et_normal), GrowArrow(flecha),
                  run_time=1.0)
        self.play(Create(arco), run_time=0.6)
        self.wait(2.2)

        # --- la relacion entre la fase y el angulo ---------------------------
        rot.mostrar(formula_pie(
            r"\Delta\varphi = 2\pi \frac{d}{\lambda} \sin\theta"),
            zona="abajo", run_time=0.5)
        self.wait(3.6)

        # --- el despeje --------------------------------------------------------
        rot.mostrar(formula_pie(
            r"\theta = \arcsin\left(\frac{\lambda\,\Delta\varphi}"
            r"{2\pi d}\right)"), zona="abajo", run_time=0.5)
        self.wait(3.8)

        # --- bajo que condicion se midio --------------------------------------
        rot.mostrar(dato_pie("SNR 10 dB"), zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- el resultado: el angulo, cian -------------------------------------
        et_ang = tag_hud(f"{fmt(ANG_05[0], 1)} grados", font_size=22)
        et_ang.next_to(arco, RIGHT, buff=0.35).shift(UP * 0.15)
        self.play(FadeIn(et_ang, shift=0.1 * RIGHT), run_time=0.6)
        rot.mostrar(cifra_pie(f"{fmt(ANG_05[0], 1)} grados"), zona="abajo",
                   run_time=0.5)
        self.wait(9.0)
