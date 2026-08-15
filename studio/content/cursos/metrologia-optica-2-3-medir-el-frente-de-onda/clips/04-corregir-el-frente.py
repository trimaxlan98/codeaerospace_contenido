class Clip4(Scene):
    """4 - Corregir el frente. El espejo deformable empuja con siete
    actuadores hasta aplanar el residual: el Strehl (`espejo.strehl()`)
    sube de 0.30 a 0.80 cuando el RMS baja a lambda/14, el limite de
    Marechal (STREHL_L14, la version lineal de la misma formula). Cierra a
    pantalla limpia con la frase doble de la leccion. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Corregir el frente"), zona="arriba",
                    run_time=0.6)

        # El espejo ocupa la columna izquierda (x de -3.2 a +0.9) y las
        # cifras la derecha (x ~ +3.5, lejos de la marca de agua).
        esp = espejo_deformable(n_act=7, ancho=5.2)
        # La lectura propia de la pieza se retira: este clip rotula el
        # Strehl con el criterio de Marechal (0.80, `strehl_lineal`) y no
        # con la exponencial (0.82), y no puede haber dos cifras distintas
        # en pantalla. `a_correccion` la reescribiria en cada frame, asi
        # que tambien se anula su relectura (sin tocar la libreria).
        esp.remove(esp.lectura)
        esp._relectura = lambda viejo, texto, **kwargs: viejo
        # Sin corregir, el residual nace montado sobre los rotulos de la
        # propia pieza (baja hasta y = 0.14 y "espejo deformable" ocupa
        # hasta 0.44; sube hasta 2.46 y "frente residual" arranca en 2.32).
        # Se sube la banda del residual 0.55 con su eje y su rotulo ANTES
        # de escalar: `a_correccion` recalcula la curva desde
        # `_params["y_res"]`, asi que el arreglo persiste.
        dy = 0.55
        esp._params["y_res"] += dy
        esp.eje.shift(UP * dy)
        esp.residual.shift(UP * dy)
        esp.rotulos[0].shift(UP * (dy + 0.30))
        esp.scale(0.75)
        esp.move_to(LEFT * 1.15 + DOWN * 0.30)

        x_col = 3.55

        # --- momento: los actuadores compensan el frente -------------------
        rot.mostrar(pie_curso("Un espejo deformable empuja con actuadores "
                              "para compensar el frente."), zona="abajo")
        self.play(FadeIn(esp, shift=0.14 * UP), run_time=1.2)
        t_strehl = tag_hud(f"Strehl = {esp.strehl():.2f}", font_size=22)
        t_strehl.move_to(np.array([x_col, 1.20, 0.0]))
        t_esc = tag_hud("escala vertical exagerada", font_size=13,
                        color=C_TENUE)
        t_esc.move_to(np.array([x_col, -1.55, 0.0]))
        self.play(FadeIn(t_strehl), FadeIn(t_esc), run_time=0.5)
        self.wait(5.0)

        # --- momento: la razon de Strehl -----------------------------------
        rot.mostrar(pie_curso("La calidad se mide con la razón de Strehl: "
                              "uno es perfecto."), zona="abajo")
        formula = MathTex(r"S \approx e^{-(2\pi\sigma/\lambda)^2}",
                          font_size=36, color=C_ONDA)
        if formula.width > 3.4:
            formula.scale_to_fit_width(3.4)
        formula.move_to(np.array([x_col, 0.15, 0.0]))
        self.play(Write(formula), run_time=1.4)
        self.wait(5.0)

        # --- momento: lambda/14, el limite de Marechal ---------------------
        rot.mostrar(pie_curso("Con un residuo de lambda sobre catorce, "
                              "Strehl 0.8: el límite de Maréchal."),
                    zona="abajo")
        tracker = ValueTracker(0.0)

        def _corregir(mob):
            mob.a_correccion(tracker.get_value())

        esp.add_updater(_corregir)
        self.play(tracker.animate.set_value(1.0), run_time=3.0,
                  rate_func=smooth)
        esp.remove_updater(_corregir)

        t_final = tag_hud(f"Strehl = {STREHL_L14:.2f}", font_size=22)
        t_final.move_to(t_strehl.get_center())
        self.play(ReplacementTransform(t_strehl, t_final), run_time=0.6)
        t_marechal = tag_hud("RMS = lambda/14 (Marechal)", font_size=16)
        t_marechal.move_to(np.array([x_col, -0.85, 0.0]))
        self.play(FadeIn(t_marechal, shift=0.10 * UP), run_time=0.5)
        self.wait(3.4)

        # --- cierre a pantalla limpia ---------------------------------------
        self.play(FadeOut(esp), FadeOut(t_final), FadeOut(t_marechal),
                  FadeOut(t_esc), FadeOut(formula), run_time=0.7)
        rot.limpiar(run_time=0.4)
        cierre = VGroup(
            Text("Medir el frente es el primer paso.", font_size=34,
                 color=C_MEDIDA),
            Text("Corregirlo, el segundo.", font_size=34, color=C_MEDIDA),
        ).arrange(DOWN, buff=0.46)
        cierre.move_to(ORIGIN)
        self.play(FadeIn(cierre[0], shift=0.12 * UP), run_time=0.7)
        self.play(FadeIn(cierre[1], shift=0.12 * UP), run_time=0.7)
        self.wait(5.0)
