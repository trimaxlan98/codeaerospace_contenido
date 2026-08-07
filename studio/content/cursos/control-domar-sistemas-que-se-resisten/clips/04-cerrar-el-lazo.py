class Clip4(Scene):
    """4 - Cerrar el lazo. El lazo abierto ordena a ciegas; cerrarlo agrega
    una rama de realimentacion que mide lo que paso y lo resta de lo
    pedido, y ese resto -el error- es la señal que corrige cien veces por
    segundo. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo ------------------------------------------
        modulo = hud_modulo("Modulo 04")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("Cerrar el lazo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el lazo ABIERTO, r -> control -> planta -> y ------------
        # Se construye completo pero solo se muestran las piezas de ida: sin
        # la rama de retorno (y con el sumador mudo del "-") se lee "a
        # ciegas".
        lazo = lazo_cerrado(ancho=6.4, font_size=16)
        lazo.move_to(np.array([0.0, 0.2, 0.0]))

        self.play(FadeIn(VGroup(lazo.eti_r, lazo.eti_y), shift=0.12 * RIGHT),
                  FadeIn(VGroup(lazo.circulo, lazo.signo_mas), scale=0.85),
                  FadeIn(lazo.control, shift=0.1 * UP),
                  FadeIn(lazo.planta, shift=0.1 * UP),
                  Create(lazo.flecha_r), Create(lazo.flecha_control),
                  Create(lazo.flecha_planta), Create(lazo.flecha_y),
                  run_time=1.3)

        rot.mostrar(pie_curso("A ciegas: ordenas y rezas. Cualquier viento "
                              "arruina el plan."), zona="abajo", run_time=0.5)
        self.wait(6.8)

        # --- momento: cerrar el lazo: la rama de realimentacion --------------
        # El pie cambia ANTES del transform (aqui, del Create) que ilustra.
        rot.mostrar(pie_curso("Cerrar el lazo: medir lo que pasó, restarlo "
                              "de lo pedido..."), zona="abajo", run_time=0.5)
        self.play(Create(lazo.rama_retro),
                  FadeIn(lazo.signo_menos, scale=0.7), run_time=1.1)
        self.wait(6.8)

        # --- momento: el flujo de la señal, dos vueltas completas -------------
        rot.mostrar(pie_curso("...y corregir con el error. Cien veces por "
                              "segundo."), zona="abajo", run_time=0.5)
        camino = lazo.camino()
        for _ in range(2):
            for tramo in camino:
                self.play(destello(tramo), run_time=0.4)
        self.wait(3.4)

        # --- momento: el error, e = r - y --------------------------------------
        hud_error = etiqueta_hud("e = r - y")
        hud_error.move_to(np.array([0.0, -1.5, 0.0]))
        self.play(FadeIn(hud_error, shift=0.1 * UP), run_time=0.5)
        self.wait(0.3)

        rot.mostrar(pie_curso("Ese pequeño resto, el error, es la señal "
                              "más importante del sistema."), zona="abajo",
                   run_time=0.5)
        self.wait(5.8)
