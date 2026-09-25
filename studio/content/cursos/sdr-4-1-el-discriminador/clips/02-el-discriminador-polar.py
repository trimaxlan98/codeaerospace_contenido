class Clip2(Scene):
    """4.1.2 - El discriminador polar: dos fasores consecutivos x[n-1] y
    x[n], y el arco fucsia del angulo entre ellos, dan una muestra del
    mensaje (angulo * fs / 2pi). La curva recuperada (verde) cae sobre el
    mensaje original (ambar, a trozos): exacta salvo la primera muestra.
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El discriminador polar"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- senal ilustrativa GRUESA (pocas muestras, desviacion mayor):
        # asi el paso de una muestra a la siguiente se ve como un angulo
        # grande, no una fraccion de grado ----------------------------------
        N_A = 20
        DESV_A = 3.5
        t_A = np.linspace(0.0, 1.0, N_A)
        m_A = np.sin(np.pi * t_A)
        FS_A = float(N_A)
        X_A = S.fm_modular(m_A, FS_A, DESV_A)
        n_pick = N_A // 2

        # --- dos fasores consecutivos y el arco del angulo ----------------
        plano = S.PlanoIQ(unidad=1.95, alcance=1.15)
        plano.move_to(UP * 0.55)
        self.play(Create(plano), run_time=0.9)
        self.wait(0.4)

        origen = plano.p(0)
        x_prev = X_A[n_pick - 1]
        x_curr = X_A[n_pick]

        def _dir(z):
            v = np.array([float(np.real(z)), float(np.imag(z)), 0.0])
            n = np.linalg.norm(v)
            return v / n if n > 1e-9 else UP

        v_prev = Arrow(origen, plano.p(x_prev), buff=0, color=C_DATO,
                       stroke_width=4, max_tip_length_to_length_ratio=0.2)
        v_curr = Arrow(origen, plano.p(x_curr), buff=0, color=C_SENAL,
                       stroke_width=4.5, max_tip_length_to_length_ratio=0.2)
        et_prev = tag_junto(v_prev, "x[n-1]", direccion=_dir(x_prev),
                            buff=0.22, font_size=20, color=C_DATO)
        et_curr = tag_junto(v_curr, "x[n]", direccion=_dir(x_curr),
                            buff=0.22, font_size=20, color=C_SENAL)

        self.play(GrowArrow(v_prev), FadeIn(et_prev), run_time=0.7)
        self.wait(0.5)
        self.play(GrowArrow(v_curr), FadeIn(et_curr), run_time=0.7)
        self.wait(0.5)

        ang_prev = float(np.angle(x_prev))
        ang_curr = float(np.angle(x_curr))
        delta = ang_curr - ang_prev
        if delta > np.pi:
            delta -= 2 * np.pi
        elif delta < -np.pi:
            delta += 2 * np.pi
        arco = Arc(radius=0.55, start_angle=ang_prev, angle=delta,
                  arc_center=origen, color=C_LO, stroke_width=4.5)
        self.play(Create(arco), run_time=0.7)
        self.wait(0.7)

        rot.mostrar(dato_pie("escala ilustrativa"), zona="abajo",
                    run_time=0.5)
        self.wait(1.6)
        rot.mostrar(formula_pie(r"\angle\left(x[n]\,x^*[n-1]\right)"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        grupo_a = VGroup(plano, v_prev, v_curr, arco, et_prev, et_curr)
        self.play(FadeOut(grupo_a), run_time=0.8)

        # --- la curva recuperada sobre el mensaje original: senal fina
        # (muchas muestras) para que la curva se vea lisa ------------------
        N = 200
        t = np.linspace(0.0, 1.0, N)
        m = np.sin(np.pi * t)
        FS_IL = float(N)
        DESV_IL = 2.5
        X = S.fm_modular(m, FS_IL, DESV_IL)
        rec = S.discriminador(X, FS_IL) / DESV_IL

        msg = S.Espectro(t, m, piso=0.0, techo=1.05, ancho=10.5, alto=3.0,
                         color=C_SENAL, area=False)
        msg.move_to(DOWN * 0.3)
        original = DashedVMobject(msg.curva, num_dashes=70)
        msg2 = msg.con_db(rec, color=C_OK)
        recuperada = msg2.curva

        self.play(Create(msg.ejes), run_time=0.6)
        self.wait(0.4)
        self.play(Create(original), run_time=1.8)
        self.wait(1.0)
        self.play(Create(recuperada), run_time=2.2)
        self.wait(1.0)

        # --- un marcador recorre ambas curvas: coinciden punto a punto ----
        marcador = ValueTracker(0.0)

        def _tk():
            return min(int(marcador.get_value() * (N - 1)), N - 1)

        linea = always_redraw(lambda: msg.marca_f(t[_tk()], color=C_TENUE))
        p_o = always_redraw(lambda: Dot(msg.en(t[_tk()], m[_tk()]),
                                        radius=0.06, color=C_SENAL))
        p_r = always_redraw(lambda: Dot(msg.en(t[_tk()], rec[_tk()]),
                                        radius=0.06, color=C_OK))
        self.add(linea, p_o, p_r)
        self.play(marcador.animate.set_value(1.0), run_time=5.0,
                  rate_func=linear)
        self.wait(6.0)
