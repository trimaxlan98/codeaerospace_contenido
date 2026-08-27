class Clip1(Scene):
    """2.1.1 - El sistema como caja: entra un impulso, sale h[n]. h[n] no
    es una propiedad del sistema, ES el sistema. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("La caja y el impulso"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        caja = bloque("Sistema", ancho=2.4, alto=1.05, color=C_TENUE,
                      color_texto=C_TITULO, tamano=24)
        caja.move_to(DOWN * 0.15)

        entrada = Secuencia(DELTA, 0, (-1.2, 1.2), ancho=2.6, alto=1.6,
                            color=C_SENAL)
        entrada.next_to(caja, LEFT, buff=0.9)
        salida = Secuencia(H_IMPULSO, 0, ancho=4.2, alto=1.6,
                           color=C_MUESTRA)
        salida.next_to(caja, RIGHT, buff=0.9)

        self.play(FadeIn(caja), run_time=0.7)
        self.wait(0.7)

        self.play(FadeIn(entrada.ejes), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(entrada.tallo(i)) for i in
                                range(len(DELTA))], lag_ratio=0.08),
                  LaggedStart(*[FadeIn(entrada.punto(i)) for i in
                                range(len(DELTA))], lag_ratio=0.08),
                  run_time=1.5)
        marca_d = entrada.marcar(0, color=C_CALCULO)
        et_d = tag_junto(entrada.punto(0), "impulso", UP, buff=0.14,
                         font_size=18, color=C_CALCULO)
        self.play(Create(marca_d), FadeIn(et_d), run_time=0.9)
        self.wait(1.8)

        c1 = conectar(entrada, caja, color=C_TENUE)
        c2 = conectar(caja, salida, color=C_TENUE)
        self.play(Create(c1), run_time=0.7)
        self.play(flujo([c1]),
                  Indicate(caja, color=C_CALCULO, scale_factor=1.08),
                  run_time=1.1)
        self.wait(1.0)

        self.play(Create(c2), FadeIn(salida.ejes), run_time=0.8)
        self.play(flujo([c2]), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(salida.tallo(i)) for i in
                                range(len(H_IMPULSO))], lag_ratio=0.09),
                  LaggedStart(*[FadeIn(salida.punto(i)) for i in
                                range(len(H_IMPULSO))], lag_ratio=0.09),
                  run_time=2.4)
        self.wait(2.0)

        self.play(FadeOut(marca_d), FadeOut(et_d), run_time=0.5)

        marcas = VGroup(*[salida.marcar(i, color=C_CALCULO) for i in
                          range(5)])
        valores = VGroup(*[tag_hud(f"{H_IMPULSO[i]:.2f}", font_size=19)
                           for i in range(5)])
        valores.arrange(RIGHT, buff=0.28)
        valores.next_to(salida, DOWN, buff=0.42)
        self.play(LaggedStart(*[Create(m) for m in marcas], lag_ratio=0.14),
                  run_time=1.3)
        self.play(LaggedStart(*[FadeIn(v, shift=0.12 * UP) for v in
                                valores], lag_ratio=0.18), run_time=1.8)
        self.wait(2.8)

        rot.mostrar(cifra_pie(f"suma h = {fmt(SUMA_H, 3)}"), zona="abajo",
                    run_time=0.5)
        self.wait(5.6)
