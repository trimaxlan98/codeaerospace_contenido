class Clip1(Scene):
    """3.1.1 - Una cajita en el campo radial: una flecha por lado con lo
    que entra o sale; sumadas dan el flujo, y el flujo por unidad de area
    es la divergencia (aqui positiva: la caja se vacia). (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La cajita contable")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el campo radial llena el plano -----------------------
        pl = plano_leccion()
        campo = campo_flechas(pl, CAMPO_FUENTE, paso=1.0, escala=0.4,
                              opacidad=0.55)
        self.play(FadeIn(pl), run_time=0.6)
        self.play(FadeIn(campo), run_time=1.0)
        rot.mostrar(pie_curso("Este es el campo radial: en todo punto, "
                              "F apunta hacia afuera del origen."),
                    zona="abajo", run_time=0.5)
        self.wait(3.6)

        # --- momento: la cajita y sus cuatro lados --------------------------
        rot.mostrar(pie_curso("Pongamos una cajita ahí y contemos lo que "
                              "cruza cada uno de sus cuatro lados."),
                    zona="abajo", run_time=0.5)
        cj = caja_conteo(pl, CAMPO_FUENTE, P_CAJA, lado=LADO_CAJA)
        self.play(FadeIn(cj.submobjects[0]), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(f, scale=0.6) for f in cj.flechas],
                              lag_ratio=0.3), run_time=1.4)
        self.wait(3.4)

        # --- momento: una cifra por lado (verde sale, rojo entra) -----------
        rot.mostrar(pie_curso("Verde: sale más de lo que entra por ese "
                              "lado. Cada lado tiene su propia cifra."),
                    zona="abajo", run_time=0.5)
        direcciones = [RIGHT, UP, LEFT, DOWN]
        etiquetas = VGroup()
        for i, d in enumerate(direcciones):
            v = cj.flujos_lados[i]
            t = tag_hud(fmt(v), font_size=15,
                       color=(C_RES if v >= 0 else C_VEC))
            t.next_to(cj.flechas[i], d, buff=0.09)
            etiquetas.add(t)
        self.play(LaggedStart(*[FadeIn(t) for t in etiquetas], lag_ratio=0.25),
                  run_time=1.4)
        self.wait(3.8)

        # --- momento: la suma es el flujo, el balance de la caja ------------
        rot.mostrar(pie_curso("Sumando los cuatro lados: eso es el "
                              "FLUJO, el balance total de la caja."),
                    zona="abajo", run_time=0.5)
        flujo_t = tag_hud(f"flujo = {fmt(cj.flujo)}", font_size=20,
                          color=C_RES)
        area_t = tag_hud(f"area = {fmt(LADO_CAJA * LADO_CAJA)}", font_size=16)
        panel = panel_derecha(flujo_t, area_t, buff=0.16)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(3.6)

        # --- momento: el balance por area es la divergencia -----------------
        rot.mostrar(pie_curso("El flujo por unidad de área es la "
                              "divergencia: aquí, positiva. La caja se "
                              "vacía."), zona="abajo", run_time=0.5)
        div_t = tag_hud(f"div = flujo / area = {fmt(cj.div)}", font_size=18,
                        color=C_CALCULO)
        div_t.next_to(panel, DOWN, buff=0.16).align_to(panel, RIGHT)
        self.play(FadeIn(div_t, shift=0.1 * UP), run_time=0.6)
        self.play(Indicate(div_t, color=C_GRAD, scale_factor=1.08),
                  run_time=0.9)
        self.wait(4.2)
