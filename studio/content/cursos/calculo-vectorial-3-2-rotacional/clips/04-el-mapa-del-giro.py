class Clip4(Scene):
    """3.2.4 - El plano coloreado por el signo del rotacional (fucsia
    antihorario, rojo horario) para un campo cuyo giro CAMBIA de signo;
    tres ruedecitas sembradas giran, cada una a su propio ritmo medido.
    Cierre de la leccion. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El mapa del giro")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el mapa, cuadro a cuadro por el signo del giro --------
        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.7)
        rot.mostrar(pie_curso("Coloreemos el plano por el signo del "
                              "rotacional: fucsia donde gira antihorario, "
                              "rojo donde gira horario."), zona="abajo",
                    run_time=0.5)

        malla = MALLA_MAPA
        xs = np.arange(malla["x0"], malla["x1"] + 1e-9, malla["paso"])
        ys = np.arange(malla["y0"], malla["y1"] + 1e-9, malla["paso"])
        puntos_malla = [(x, y) for y in ys for x in xs]
        rots_malla = [rot_num(CAMPO_MAPA, np.array(p)) for p in puntos_malla]
        max_rot = max(1e-6, max(abs(r) for r in rots_malla))
        lado_px = malla["paso"] * pl.unidad * 0.92
        cuadros = VGroup()
        for (x, y), r in zip(puntos_malla, rots_malla):
            color = C_FLUJO if r >= 0 else C_VEC
            op = 0.12 + 0.75 * min(1.0, abs(r) / max_rot)
            cu = Square(side_length=lado_px, stroke_width=0,
                       fill_color=color, fill_opacity=op)
            cu.move_to(pl.p(x, y))
            cuadros.add(cu)
        cuadros.set_z_index(-1)
        self.play(FadeIn(cuadros), run_time=1.4)
        self.wait(3.2)

        # --- momento: tres ruedecitas sembradas -----------------------------
        rot.mostrar(pie_curso("Sembremos tres ruedecitas: una en cada "
                              "franja, y midamos su giro."), zona="abajo",
                    run_time=0.5)
        ruedas = VGroup(*[rueda(pl, p) for p in PUNTOS_RUEDAS_MAPA])
        rots_local = [rot_num(CAMPO_MAPA, p) for p in PUNTOS_RUEDAS_MAPA]
        cifras = VGroup()
        for rd, p, r in zip(ruedas, PUNTOS_RUEDAS_MAPA, rots_local):
            col = C_FLUJO if r >= 0 else C_VEC
            c = tag_hud(f"rot = {fmt(r)}", font_size=16, color=col)
            c.next_to(rd, UP, buff=0.12)
            cifras.add(_con_fondo(c, buff=0.08, opacidad=0.85))
        self.play(LaggedStart(*[FadeIn(rd, scale=0.6) for rd in ruedas],
                              lag_ratio=0.3), run_time=1.2)
        self.play(FadeIn(cifras), run_time=0.6)
        self.wait(3.0)

        # --- momento: cada una gira a su propio ritmo, con su propio sentido --
        rot.mostrar(pie_curso("Cada ruedecita gira a su propia velocidad, "
                              "y algunas al revés que sus vecinas."),
                    zona="abajo", run_time=0.5)
        T = 4.5
        self.play(*[Rotate(rd.aspas, angle=(r / 2.0) * T,
                           about_point=rd.centro())
                    for rd, r in zip(ruedas, rots_local)], run_time=T,
                  rate_func=linear)
        self.wait(1.6)

        rot.mostrar(pie_curso("El signo cambia de franja en franja: el "
                              "rotacional también es un mapa, punto a "
                              "punto."), zona="abajo", run_time=0.5)
        self.wait(3.6)

        # --- cierre -----------------------------------------------------------
        cierre_leccion(self, rot,
                       "El rotacional es la ruedecita.",
                       "Gira aunque el río vaya recto.",
                       "Siguiente lección: campos conservativos, el "
                       "camino no importa.",
                       pl, cuadros, ruedas, cifras)
