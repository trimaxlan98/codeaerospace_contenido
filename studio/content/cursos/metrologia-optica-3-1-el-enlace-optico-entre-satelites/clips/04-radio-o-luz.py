class Clip4(Scene):
    """4 - Radio o luz. Tabla comparativa: ancho de haz, ganancia, tasa y
    espectro favorecen al optico (9.87 urad vs 6.36 mrad de ancho, 106.1
    vs 50.0 dBi, decenas de Gbps sin licencia); a cambio exige apuntar a
    microrradianes. Cierre a pantalla limpia. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Radio o luz"), zona="arriba", run_time=0.6)

        x_et, x_rf, x_opt = -3.55, -0.20, 3.05
        y_header, paso_y = 1.95, 0.62
        nombres = ["ancho de haz", "ganancia", "tasa", "espectro",
                  "puntería"]

        lam_rf = C_LUZ / 30e9
        th_rf_mrad = divergencia_gauss(lam_rf, 1.0 / 2.0) * 1e3
        datos = {
            "ancho de haz": (f"{th_rf_mrad:.2f} mrad",
                             f"{DIV_ISL_URAD:.2f} urad"),
            "ganancia": (f"{G_RF_DBI:.1f} dBi", f"{G_OPT_DBI:.1f} dBi"),
            "tasa": ("Gbps", "decenas Gbps"),
            "espectro": ("licencia", "libre"),
            "puntería": ("facil", "microrradianes"),
        }

        def fila(nombre, i, color_valor=None):
            y = y_header - 0.62 - i * paso_y
            et = tag_hud(nombre.replace("puntería", "punteria"),
                        font_size=16, color=C_TENUE)
            et.move_to(np.array([x_et, y, 0.0]), aligned_edge=LEFT)
            v_rf = tag_hud(datos[nombre][0], font_size=18,
                          color=C_MEDIDA if color_valor is None
                          else color_valor)
            v_rf.move_to(np.array([x_rf, y, 0.0]))
            v_opt = tag_hud(datos[nombre][1], font_size=18,
                            color=C_MEDIDA if color_valor is None
                            else color_valor)
            v_opt.move_to(np.array([x_opt, y, 0.0]))
            return VGroup(et, v_rf, v_opt)

        cab_rf = tag_hud("RADIO 30 GHz", font_size=18, color=C_OBJETO)
        cab_rf.move_to(np.array([x_rf, y_header, 0.0]))
        cab_opt = tag_hud("OPTICO 1550 nm", font_size=18, color=C_HAZ)
        cab_opt.move_to(np.array([x_opt, y_header, 0.0]))
        sep = Line(np.array([x_et - 0.06, y_header - 0.34, 0.0]),
                  np.array([x_opt + 1.10, y_header - 0.34, 0.0]),
                  stroke_width=1.4, color=C_EJE)

        filas_grp = VGroup(*(fila(n, i) for i, n in enumerate(nombres[:4])))

        # --- momento 1: aparecen las filas -----------------------------------
        rot.mostrar(pie_curso("Comparemos."), zona="abajo")
        self.play(FadeIn(cab_rf, shift=0.10 * UP),
                  FadeIn(cab_opt, shift=0.10 * UP), run_time=0.5)
        self.play(Create(sep), run_time=0.4)
        for i in range(4):
            self.play(FadeIn(filas_grp[i], shift=0.10 * UP), run_time=0.45)
        self.wait(4.5)

        # --- momento 2: la luz gana ------------------------------------------
        rot.mostrar(pie_curso("La luz gana en ganancia, tasa y espectro "
                              "sin licencia."), zona="abajo")
        columna_opt = VGroup(cab_opt, *(filas_grp[i][2] for i in range(4)))
        self.play(Indicate(columna_opt, color=C_MEDIDA, scale_factor=1.08),
                  run_time=1.1)
        self.wait(4.6)

        # --- momento 3: lo que cuesta ------------------------------------------
        rot.mostrar(pie_curso("Y pierde en una sola cosa: hay que apuntar "
                              "a microrradianes."), zona="abajo")
        fila_pun = fila("puntería", 4, color_valor=C_HAZ)
        self.play(FadeIn(fila_pun, shift=0.10 * UP), run_time=0.6)
        self.wait(4.8)

        # --- cierre a pantalla limpia -----------------------------------------
        self.play(FadeOut(cab_rf), FadeOut(cab_opt), FadeOut(sep),
                  FadeOut(filas_grp), FadeOut(fila_pun), run_time=0.6)
        rot.limpiar("arriba", run_time=0.3)
        rot.limpiar("abajo", run_time=0.3)
        linea1 = Text("El láser regala ganancia.", font_size=38, color=C_HAZ)
        linea2 = Text("La cobra en puntería.", font_size=38, color=C_HAZ)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        self.play(FadeIn(linea1, shift=0.18 * UP), run_time=0.7)
        self.play(FadeIn(linea2, shift=0.18 * UP), run_time=0.7)
        self.wait(6.0)
