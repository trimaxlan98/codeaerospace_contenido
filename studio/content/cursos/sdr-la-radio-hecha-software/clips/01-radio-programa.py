class Clip1(Scene):
    """1 - Una radio que es un programa. Portada del curso SDR: la cadena
    clasica de circuitos fijos (MEZCLADOR-FILTRO-DETECTOR) se desvanece y
    da paso a ANTENA-ADC-SOFTWARE; junto al bloque SOFTWARE una etiqueta
    HUD releva el modo de recepcion, prueba de que el mismo hardware
    sirve para todo. (~34 s)"""

    def _releva_modo(self, anterior, texto, ancla):
        """Etiqueta HUD junto a SOFTWARE, en relevo (nunca dos a la vez)."""
        nuevo = etiqueta_hud(texto, color=C_ACENTO)
        nuevo.next_to(ancla, UP, buff=0.32)
        if anterior is None:
            self.play(FadeIn(nuevo, shift=0.12 * UP), run_time=0.4)
        else:
            self.play(FadeOut(anterior, shift=0.12 * DOWN), run_time=0.3)
            self.play(FadeIn(nuevo, shift=0.12 * UP), run_time=0.4)
        return nuevo

    def construct(self):
        rot = Rotulos(self)

        # --- momento: portada del curso ---------------------------------
        portada = VGroup(
            titulo_marca("SDR", font_size=46),
            Text("la radio hecha software", font_size=25, color=C_ACENTO),
        ).arrange(DOWN, buff=0.26)
        portada.move_to(ORIGIN)

        self.play(Write(portada[0]), run_time=1.3)
        self.play(FadeIn(portada[1], shift=0.18 * UP), run_time=0.7)
        self.wait(2.0)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.play(FadeOut(portada, shift=0.5 * UP), run_time=0.7)

        titulo = titulo_curso("Una radio que es un programa")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.0)

        # --- momento: la cadena clasica, un circuito por funcion ---------
        mezclador = bloque("MEZCLADOR", color=C_EJE, color_texto=C_TITULO)
        filtro = bloque("FILTRO", color=C_EJE, color_texto=C_TITULO)
        detector = bloque("DETECTOR", color=C_EJE, color_texto=C_TITULO)
        cadena_vieja = VGroup(mezclador, filtro, detector).arrange(
            RIGHT, buff=0.9)
        cadena_vieja.move_to(UP * 1.0)
        conex_vieja = VGroup(conectar(mezclador, filtro, color=C_EJE),
                             conectar(filtro, detector, color=C_EJE))

        self.play(FadeIn(cadena_vieja, lag_ratio=0.15, shift=0.15 * UP),
                  run_time=1.0)
        self.play(Create(conex_vieja), run_time=0.8)
        self.wait(1.0)

        rot.mostrar(pie_curso("Antes: un circuito para cada función. "
                              "Cambiar de modo era cambiar el aparato."),
                   zona="abajo", run_time=0.5)
        self.wait(5.4)

        # --- momento: la idea SDR, digitalizar lo antes posible ----------
        self.play(FadeOut(VGroup(cadena_vieja, conex_vieja),
                          shift=0.5 * UP), run_time=0.7)

        antena = bloque("ANTENA", color=C_EJE, color_texto=C_TITULO)
        adc = bloque("ADC", color=C_SENAL, color_texto=C_TITULO)
        software = bloque("SOFTWARE", color=C_I, ancho=2.6,
                          color_texto=C_TITULO)
        cadena_sdr = VGroup(antena, adc, software).arrange(RIGHT, buff=0.9)
        cadena_sdr.move_to(DOWN * 0.8)
        conex_sdr = [conectar(antena, adc, color=C_EJE),
                    conectar(adc, software, color=C_EJE)]

        self.play(FadeIn(cadena_sdr, lag_ratio=0.15, shift=0.15 * DOWN),
                  run_time=1.0)
        self.play(Create(VGroup(*conex_sdr)), run_time=0.7)
        self.play(flujo(conex_sdr, color=C_SENAL), run_time=1.0)

        rot.mostrar(pie_curso("La idea SDR: digitaliza lo antes posible. "
                              "El resto es código."), zona="abajo",
                   run_time=0.5)
        self.wait(5.4)

        # --- momento: el mismo hardware, distintos modos ------------------
        modo = self._releva_modo(None, "137 MHz · METEO", software)
        self.wait(1.0)
        modo = self._releva_modo(modo, "437 MHz · CUBESAT", software)
        self.wait(1.0)
        modo = self._releva_modo(modo, "1090 MHz · AVIONES", software)

        rot.mostrar(pie_curso("El mismo aparato de 30 dólares. Solo "
                              "cambia el programa."), zona="abajo",
                   run_time=0.5)
        self.wait(5.3)
