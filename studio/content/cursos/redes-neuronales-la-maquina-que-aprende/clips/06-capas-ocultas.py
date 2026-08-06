class Clip6(Scene):
    """6 - Capas ocultas: doblar el espacio. Una red 2-4-1 a la
    izquierda late con cada pasada; a la derecha, la frontera de
    decision sobre los datos de XOR se curva en tres pasos (modelo
    inicial, intermedio y final) hasta encerrar los racimos."""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD de modulo y titulo -------------------------------------
        modulo = hud_modulo("Modulo 06")
        titulo = titulo_curso("Capas ocultas: doblar el espacio")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.2)

        # --- La red: dos entradas, cuatro ocultas, una salida -------------
        red = RedNeuronal(capas=(2, 4, 1), color_neurona=C_DATO_A,
                          color_conexion=C_EJE)
        red.move_to(LEFT * 3.6)
        self.play(Create(red), run_time=1.4)
        self.play(red.activacion(color=C_DATO_A))
        self.wait(1.3)

        rot.mostrar(pie_curso("Dos entradas, cuatro neuronas ocultas, "
                              "una salida."), zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- El plano XOR a la derecha -------------------------------------
        ejes = ejes_plano(lado=4.2)
        ejes.move_to(RIGHT * 2.6)
        self.play(Create(ejes), run_time=1.1)

        X, y = datos_xor()
        puntos = puntos_datos(ejes, X, y)
        self.play(FadeIn(puntos, lag_ratio=0.05), run_time=1.4)
        self.wait(1.8)

        # --- La frontera se curva: modelo inicial ---------------------------
        entren = entrenar_mlp(X, y, ocultas=4, epocas=1200, lr=0.9,
                              semilla=3, instantaneas=12)
        modelos = entren.modelos
        frontera = frontera_imagen(ejes, modelos[0])
        self.play(FadeIn(frontera, run_time=1.2), red.activacion(color=C_DATO_A))
        self.wait(1.6)

        # --- La frontera se curva: modelo intermedio -------------------------
        frontera_media = frontera_imagen(ejes, modelos[len(modelos) // 2])
        self.play(FadeTransform(frontera, frontera_media, run_time=1.3),
                  red.activacion(color=C_DATO_A))
        frontera = frontera_media
        self.wait(1.6)

        # --- La frontera se curva: modelo final ------------------------------
        frontera_final = frontera_imagen(ejes, modelos[-1])
        self.play(FadeTransform(frontera, frontera_final, run_time=1.3),
                  red.activacion(color=C_DATO_A))
        frontera = frontera_final
        self.wait(2.2)

        # --- El muro, derribado ------------------------------------------------
        rot.mostrar(pie_curso("La red dobla el espacio hasta que una "
                              "recta basta."), zona="abajo", run_time=0.5)
        self.wait(2.6)
        rot.mostrar(pie_curso("El muro de XOR, derribado."),
                   zona="abajo", run_time=0.5)
        self.wait(3.2)
