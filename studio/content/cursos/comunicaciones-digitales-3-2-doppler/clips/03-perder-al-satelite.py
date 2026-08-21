class Clip3(Scene):
    """3.2.3 - El receptor fijo solo engancha la señal mientras la curva
    S cae dentro del filtro (+-3 kHz): los segundos utiles, CONTADOS del
    array, son un fragmento breve alrededor del cenit. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Perder al satélite")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.6)

        # --- momento: el receptor escucha en una sola frecuencia ---------
        rot.mostrar(pie_curso("El receptor esta sintonizado fijo: solo "
                              "oye dentro de una franja estrecha."),
                    zona="abajo", run_time=0.5)
        on = onda(T_MIN, FD_KHZ, rango_y=(-13.0, 13.0), ancho=8.6,
                  alto=3.2, color=C_SENAL)
        on.move_to(DOWN * 0.35)
        self.play(FadeIn(on.ejes), run_time=0.4)
        self.play(Create(on.curva), run_time=2.0)
        franja = Polygon(on.en(on.x0, BANDA_FILTRO_KHZ),
                         on.en(on.x1, BANDA_FILTRO_KHZ),
                         on.en(on.x1, -BANDA_FILTRO_KHZ),
                         on.en(on.x0, -BANDA_FILTRO_KHZ),
                         color=C_BANDA, stroke_width=1.4)
        franja.set_fill(C_BANDA, opacity=0.16)
        et_franja = tag_hud(f"filtro +-{fmt(BANDA_FILTRO_KHZ, 0)} kHz",
                            font_size=18, color=C_BANDA)
        et_franja.next_to(on.en(on.x0, BANDA_FILTRO_KHZ), UP, buff=0.12)
        self.play(FadeIn(franja), FadeIn(et_franja), run_time=0.8)
        self.wait(4.2)

        # --- momento: dentro engancha, fuera se pierde --------------------
        rot.mostrar(pie_curso("Mientras la curva cae dentro de la "
                              "franja hay señal; en cuanto sale, se "
                              "pierde."), zona="abajo", run_time=0.5)
        idxs = np.where(_DENTRO)[0]
        i_s, i_e = int(idxs[0]), int(idxs[-1])
        seg_izq = on.curva_de(T_MIN[:i_s + 1], FD_KHZ[:i_s + 1],
                              color=C_RUIDO, grosor=3.0)
        seg_in = on.curva_de(T_MIN[i_s:i_e + 1], FD_KHZ[i_s:i_e + 1],
                             color=C_COD, grosor=3.4)
        seg_der = on.curva_de(T_MIN[i_e:], FD_KHZ[i_e:], color=C_RUIDO,
                              grosor=3.0)
        self.play(FadeOut(on.curva), run_time=0.5)
        self.play(Create(seg_izq), Create(seg_der), run_time=1.2)
        self.play(Create(seg_in), run_time=1.0)
        self.wait(4.6)

        # --- momento: la ventana de enganche, marcada ----------------------
        rot.mostrar(pie_curso("Solo un instante alrededor del cenit "
                              "queda dentro del filtro."), zona="abajo",
                    run_time=0.5)
        v_i = on.vertical_en(T_MIN[i_s], color=C_COD)
        v_f = on.vertical_en(T_MIN[i_e], color=C_COD)
        self.play(Create(v_i), Create(v_f), run_time=0.8)
        self.wait(3.4)

        # --- momento: los segundos contados ---------------------------------
        panel = panel_derecha(
            tag_hud(f"dentro: {fmt(S_ENGANCHE, 1)} s"),
            tag_hud(f"pase total: {fmt(T_TOTAL_S, 0)} s"),
            tag_hud(f"filtro +-{fmt(BANDA_FILTRO_KHZ, 0)} kHz"))
        rot.mostrar(pie_curso("Contados del propio array: apenas unos "
                              "segundos utiles de un pase de doce "
                              "minutos."), zona="abajo", run_time=0.5)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(6.6)
