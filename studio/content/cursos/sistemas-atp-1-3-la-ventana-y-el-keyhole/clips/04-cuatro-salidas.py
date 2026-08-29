class Clip4(Scene):
    """1.3.4 - Las cuatro respuestas de ingenieria al keyhole: aceptar
    el hueco, flip de acimut, desapuntar y montura X-Y. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Cuatro salidas"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- las cifras de cada salida (todas de la libreria) -------------
        # El tiempo DENTRO del cono ciego es la duracion de ese mismo pase
        # por encima de la elevacion en la que el rotor se planta.
        T_HUECO = duracion_pase(H_LEO, EL_MAX_ALTO, 90.0 - R_KEYHOLE)
        AZ_BARRIDO = float(PERFIL_ALTO["az_barrido"])
        T_FLIP = AZ_BARRIDO / ROTOR_MAX
        W_CENIT = velocidad_angular_cenit(H_LEO)

        XS = (-5.25, -1.75, 1.75, 5.25)
        Y_CELDA = 0.45
        Y_TAG = -1.42
        RADIO = 1.32
        R_CONO = RADIO * R_KEYHOLE / 90.0      # el cono, a la escala de la carta
        piezas = []

        def celda(i):
            v = vista_polar(radio=RADIO, font_size=13)
            v.move_to(np.array([XS[i], Y_CELDA, 0.0]))
            return v

        def rotulo(i, texto, color=None):
            t = tag_junto(Dot(ORIGIN), texto, direccion=DOWN, buff=0.0,
                          color=color)
            t.move_to(np.array([XS[i], Y_TAG, 0.0]))
            return t

        def numero(i):
            t = tag_hud(str(i + 1), font_size=22, color=C_TENUE)
            t.move_to(np.array([XS[i], Y_CELDA + RADIO + 0.72, 0.0]))
            return t

        def tramo(traza, el_min, n=601):
            ts = np.linspace(0.0, 1.0, n)
            dentro = [t for t in ts if traza.el_en(t) >= el_min]
            return float(dentro[0]), float(dentro[-1])

        # --- 1. aceptar el hueco -----------------------------------------
        v1, n1 = celda(0), numero(0)
        tr1 = traza_pase(v1, el_max=EL_MAX_ALTO, az_culminacion=67.5,
                         muestras=120, color=C_SAT)
        cono1 = cono_keyhole(v1, radio_deg=R_KEYHOLE, color=C_PELIGRO)
        cono1.set_stroke(width=2.6)
        a1, b1 = tramo(tr1, 90.0 - R_KEYHOLE)
        arcos1 = VGroup(
            Line(tr1.punto_en(0.0), tr1.punto_en(a1), color=C_SAT,
                 stroke_width=3.4),
            Line(tr1.punto_en(b1), tr1.punto_en(1.0), color=C_SAT,
                 stroke_width=3.4))
        bordes1 = VGroup(Dot(tr1.punto_en(a1), radius=0.055, color=C_PELIGRO),
                         Dot(tr1.punto_en(b1), radius=0.055, color=C_PELIGRO))
        # el satelite sigue pasando por el hueco: lo que se pierde es el
        # seguimiento, y por eso el trozo va a trazos y apagado.
        hueco1 = DashedVMobject(
            Line(tr1.punto_en(a1), tr1.punto_en(b1), color=C_SAT,
                 stroke_width=2.2).set_stroke(opacity=0.40), num_dashes=6)
        r1 = rotulo(0, "aceptar el hueco")
        self.play(FadeIn(n1), Create(v1), run_time=1.0)
        self.play(FadeIn(cono1), run_time=0.6)
        self.play(Create(arcos1), run_time=0.9)
        self.play(FadeIn(bordes1), FadeIn(hueco1), FadeIn(r1),
                  run_time=0.6)
        rot.mostrar(cifra_pie(f"hueco {fmt(T_HUECO, 1)} s"), zona="abajo")
        piezas += [n1, v1, cono1, arcos1, bordes1, hueco1, r1]
        self.wait(2.0)

        # --- 2. flip de acimut --------------------------------------------
        n2 = numero(1)
        mont = montura(alto=2.35, font_size=13)
        # `pivote`, `base_izq` y `base_der` son atributos FIJOS: al mover la
        # montura hay que arrastrarlos, o `apuntar(az)` deja la marca del
        # anillo en el sitio donde nacio la pieza.
        delta = np.array([XS[1], Y_CELDA - 0.28, 0.0]) - mont.pivote
        mont.shift(delta)
        mont.pivote = mont.pivote + delta
        mont.base_izq = mont.base_izq + delta
        mont.base_der = mont.base_der + delta
        t_barrido = tag_hud(f"barrido {fmt(AZ_BARRIDO, 0)} deg",
                            font_size=18, color=C_TENUE)
        t_barrido.move_to(np.array([XS[1], Y_CELDA + RADIO + 0.14, 0.0]))
        r2 = rotulo(1, "flip de acimut")
        self.play(FadeIn(n2), FadeIn(mont), run_time=1.0)
        self.play(FadeIn(t_barrido), run_time=0.4)

        az_t = ValueTracker(0.0)
        mont.add_updater(lambda m: m.apuntar(az_deg=az_t.get_value()))
        mont.saturar(True)
        self.play(az_t.animate.set_value(180.0), run_time=2.0)
        mont.clear_updaters()
        mont.saturar(False)
        self.play(FadeIn(r2), run_time=0.5)
        rot.mostrar(cifra_pie(f"flip {fmt(T_FLIP, 1)} s"), zona="abajo")
        piezas += [n2, mont, t_barrido, r2]
        self.wait(2.0)

        # --- 3. desapuntar a proposito ------------------------------------
        v3, n3 = celda(2), numero(2)
        tr3 = traza_pase(v3, el_max=EL_MAX_ALTO, az_culminacion=67.5,
                         muestras=120, color=C_SAT)
        tr3.set_stroke(opacity=0.45)
        cono3 = cono_keyhole(v3, radio_deg=R_KEYHOLE, color=C_PELIGRO)
        cono3.set_stroke(width=2.6)
        centro3 = v3.centro()
        a3, b3 = tramo(tr3, 90.0 - R_KEYHOLE)
        pa, pb = tr3.punto_en(a3), tr3.punto_en(b3)
        th_a = float(np.arctan2(pa[1] - centro3[1], pa[0] - centro3[0]))
        th_b = float(np.arctan2(pb[1] - centro3[1], pb[0] - centro3[0]))
        rodeo = Arc(radius=R_CONO, start_angle=th_a,
                    angle=float((th_b - th_a) % (2.0 * np.pi)),
                    color=C_CALCULO, stroke_width=5.0)
        rodeo.move_arc_center_to(centro3)
        camino = VGroup(
            Line(tr3.punto_en(0.0), rodeo.get_start(), color=C_CALCULO,
                 stroke_width=4.0),
            rodeo,
            Line(rodeo.get_end(), tr3.punto_en(1.0), color=C_CALCULO,
                 stroke_width=4.0))
        r3 = rotulo(2, "desapuntar")
        self.play(FadeIn(n3), Create(v3), run_time=1.0)
        self.play(Create(tr3), FadeIn(cono3), run_time=0.8)
        self.play(Create(camino), run_time=1.2)
        self.play(FadeIn(r3), run_time=0.5)
        rot.mostrar(cifra_pie(f"desvio {fmt(R_KEYHOLE, 1)} deg"),
                    zona="abajo")
        piezas += [n3, v3, tr3, cono3, camino, r3]
        self.wait(2.0)

        # --- 4. montura X-Y: la singularidad se va al horizonte ------------
        v4, n4 = celda(3), numero(3)
        tr4 = traza_pase(v4, el_max=EL_MAX_ALTO, az_culminacion=67.5,
                         muestras=120, color=C_OK)
        lobulos = VGroup()
        for az in (70.0, 250.0):
            lob = Circle(radius=R_CONO, color=C_PELIGRO, stroke_width=1.8)
            lob.set_fill(color=C_PELIGRO, opacity=0.25)
            lob.set_stroke(color=C_PELIGRO, opacity=0.85)
            lob.move_to(v4.punto(az, 0.0))
            lobulos.add(lob)
        limpio = Dot(v4.centro(), radius=0.06, color=C_OK)
        r4 = rotulo(3, "montura X-Y")
        self.play(FadeIn(n4), Create(v4), run_time=1.0)
        self.play(FadeIn(lobulos), run_time=0.7)
        self.play(Create(tr4), FadeIn(limpio), run_time=1.0)
        self.play(FadeIn(r4), run_time=0.5)
        rot.mostrar(cifra_pie(f"X-Y cenit {fmt(W_CENIT, 2)} deg/s"),
                    zona="abajo")
        piezas += [n4, v4, tr4, lobulos, limpio, r4]
        self.wait(2.8)

        # --- el cierre -----------------------------------------------------
        cierre_leccion(self, rot,
                       "El mejor pase del enlace",
                       "es el peor de la mecanica.",
                       *piezas, espera=4.4)
