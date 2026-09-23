class Clip1(Scene):
    """1.4.1 - El estado del mundo tiene 10 numeros; cada agente ve 6, y no
    los mismos. El canal degradado vive en el estado y en ninguna
    observacion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Lo que cada uno ve"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        def columna(nombres, x, color, alto=0.36):
            g = VGroup()
            for i, nm in enumerate(nombres):
                c = Rectangle(width=2.75, height=alto, stroke_color=color, stroke_width=2,
                              fill_color=color, fill_opacity=0.10)
                c.move_to([x, 2.0 - i * (alto + 0.06), 0])
                t = Text(nm, font=FUENTE_HUD, font_size=15, color=color)
                if t.width > 2.55:
                    t.scale_to_fit_width(2.55)
                t.move_to(c)
                g.add(VGroup(c, t))
            return g

        estado = columna(ESTADO, -4.3, C_PRIV)
        et_s = tag_hud(f"estado s: {len(ESTADO)}", font_size=19, color=C_PRIV)
        et_s.next_to(estado, UP, buff=0.18)
        self.play(FadeIn(et_s), LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in estado],
                                            lag_ratio=0.08), run_time=2.2)
        self.wait(3.4)
        rot.mostrar(dato_pie(f"estado de {E['dim_estado']} dimensiones"), zona="abajo", run_time=0.5)
        self.wait(2.4)

        # tres observaciones locales, una por agente
        xs = [-0.6, 2.3, 5.2]
        nombres = ["satelite 1", "satelite 2", "gateway"]
        obs_g = VGroup()
        for x, nm in zip(xs, nombres):
            col = columna(OBS, x, C_ADAPTA)
            et = tag_hud(f"o: {nm}", font_size=17, color=C_ADAPTA).next_to(col, UP, buff=0.18)
            obs_g.add(VGroup(et, col))
        self.play(LaggedStart(*[FadeIn(o) for o in obs_g], lag_ratio=0.25), run_time=2.4)
        self.wait(2.6)
        rot.mostrar(dato_pie(f"cada agente ve {E['dim_obs']}"), zona="abajo", run_time=0.5)
        self.wait(3.0)

        # lo que nadie ve: se apaga todo lo compartido y queda la fila huerfana
        i_oculto = ESTADO.index("canal degradado")
        compart = [i for i, nm in enumerate(ESTADO) if nm in OBS]
        self.play(*[m.animate.set_stroke(opacity=0.25).set_fill(opacity=0.03)
                    for i in range(len(ESTADO)) if i != i_oculto for m in [estado[i][0]]],
                  *[estado[i][1].animate.set_opacity(0.25) for i in range(len(ESTADO))
                    if i != i_oculto], run_time=0.8)
        marco = SurroundingRectangle(estado[i_oculto], color=C_NO, buff=0.06, stroke_width=4)
        # solo el trazo y el texto: set_opacity sobre el grupo enciende el
        # RELLENO del rectangulo y tapa la palabra (trampas.md)
        self.play(Create(marco), run_time=0.8)
        rot.mostrar(tag_hud("nadie observa el canal", font_size=24, color=C_NO).to_edge(DOWN, buff=MARGEN_PIE),
                    zona="abajo", run_time=0.5)
        self.wait(6.0)
        self.wait(1.8)
