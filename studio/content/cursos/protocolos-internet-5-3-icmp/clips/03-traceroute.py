class Clip3(Scene):
    """5.3.3 - Traceroute REAL (7 saltos, uno mudo): TTL=1, 2, 3... cada
    router se queja de tiempo excedido y delata su nombre, salvo el
    salto 4, que no contesta -- el asterisco de un traceroute de
    verdad. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Traceroute")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: TTL 1, 2, 3... cada vez mas lejos ----------------------
        rot.mostrar(pie_curso("La idea: mandar el mismo paquete con TTL=1, "
                              "2, 3... cada uno muere un salto mas lejos."),
                    zona="abajo", run_time=0.5)
        esc = escalera(ACTORES_TR, EVENTOS_TR, ancho=10.0, alto=3.9, fs=11)
        esc.move_to(DOWN * 0.30)
        self.play(FadeIn(esc.actores), Create(esc.vidas), run_time=1.0)
        self.wait(1.6)

        rot.mostrar(pie_curso("Y cada router al que le llega el TTL en "
                              "cero se queja: tiempo excedido, con su "
                              "nombre."),
                    zona="abajo", run_time=0.5)
        for k in range(3):
            self.play(Create(esc.paso(k)), run_time=0.65)
        self.wait(1.6)

        # --- momento: el salto mudo -------------------------------------
        rot.mostrar(pie_curso("El salto 4 no contesta: sale el asterisco. "
                              "No significa que la ruta se rompio, solo "
                              "que ese router calla."),
                    zona="abajo", run_time=0.5)
        self.play(Create(esc.paso(3)), run_time=0.8)
        self.wait(3.2)

        # --- momento: los siguientes si contestan, mas lejos -----------------
        rot.mostrar(pie_curso("Los siguientes routers si contestan, cada "
                              "uno mas lejos que el anterior."),
                    zona="abajo", run_time=0.5)
        for k in (4, 5):
            self.play(Create(esc.paso(k)), run_time=0.7)
        self.wait(2.6)

        # --- momento: el ultimo salto ya no es un error -----------------
        rot.mostrar(pie_curso("En el ultimo salto la respuesta ya no es "
                              "un error: es un eco real. Ahi esta el "
                              "destino."),
                    zona="abajo", run_time=0.5)
        self.play(Create(esc.paso(6)), run_time=0.9)
        self.wait(3.4)

        # --- momento: el mapa completo, con su hueco -----------------------
        rot.mostrar(pie_curso("Siete saltos, seis nombres y un hueco: asi "
                              "se ve un traceroute de verdad."),
                    zona="abajo", run_time=0.5)
        resumen = tag_hud("total hasta el destino: %s ms   (salto 4: sin "
                          "dato)" % fmt(TRACE["total_ms"], 1), font_size=19,
                          color=C_CIFRA)
        resumen.next_to(esc, UP, buff=0.30)
        self.play(FadeIn(resumen), run_time=0.5)
        self.wait(5.0)
