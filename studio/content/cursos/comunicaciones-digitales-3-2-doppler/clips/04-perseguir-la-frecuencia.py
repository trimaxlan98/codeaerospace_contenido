class Clip4(Scene):
    """3.2.4 - El receptor conoce el pase de antemano (efemerides): la
    prediccion coincide con la curva medida y, al restarla, el residual
    queda plano en 0 kHz. Cierre de la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Perseguir la frecuencia")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.6)

        # --- momento: la curva medida, otra vez ---------------------------
        rot.mostrar(pie_curso("Esta es la curva medida: la frecuencia "
                              "que de verdad llega al receptor."),
                    zona="abajo", run_time=0.5)
        on = onda(T_MIN, FD_KHZ, rango_y=(-13.0, 13.0), ancho=8.6,
                  alto=3.2, color=C_SENAL)
        on.move_to(DOWN * 0.35)
        et_medida = tag_junto(on, "medida", direccion=DOWN, buff=0.28,
                              color=C_SENAL)
        self.play(FadeIn(on.ejes), run_time=0.4)
        self.play(Create(on.curva), FadeIn(et_medida), run_time=2.2)
        self.wait(3.4)

        # --- momento: el receptor la conoce de antemano --------------------
        rot.mostrar(pie_curso("Pero el receptor conoce el pase de "
                              "antemano (efemerides): predice esta "
                              "misma curva."), zona="abajo", run_time=0.5)
        predicha = DashedVMobject(
            on.curva_de(T_MIN, FD_PREDICHA_KHZ, color=C_CIFRA, grosor=3.0),
            num_dashes=44)
        et_pred = tag_junto(on, "predicha (efemerides)", direccion=UP,
                            buff=0.28, color=C_CIFRA)
        self.play(FadeIn(predicha), FadeIn(et_pred), run_time=1.0)
        self.wait(4.4)

        # --- momento: restar la prediccion deja el residual en 0 ----------
        rot.mostrar(pie_curso("Al restar la prediccion de lo medido, lo "
                              "que sobra es el residual."), zona="abajo",
                    run_time=0.5)
        corregida = on.con_serie(FD_CORREGIDA_KHZ, color=C_COD)
        self.play(FadeOut(predicha), FadeOut(et_pred), FadeOut(et_medida),
                  run_time=0.5)
        self.play(Transform(on.curva, corregida.curva), run_time=1.6)
        et_cero = tag_hud(
            f"residual maximo = {fmt(np.max(np.abs(FD_CORREGIDA_KHZ)), 1)}"
            " kHz", font_size=20, color=C_COD)
        et_cero.next_to(on.en(0.0, 0.0), UP, buff=0.4)
        self.play(FadeIn(et_cero), run_time=0.5)
        self.wait(5.0)

        # --- cierre de la leccion --------------------------------------------
        cierre_leccion(
            self, rot,
            "El cielo nunca da la frecuencia prometida.",
            "Da la que hay que saber perseguir.",
            "Siguiente leccion: encontrar donde empieza la señal.",
            on, et_cero)
