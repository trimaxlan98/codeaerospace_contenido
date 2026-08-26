class Clip2(Scene):
    """5.1.2 - resolver_dns real: cuatro viajes hasta la respuesta, RTT
    acumulado 2 -> 32 -> 77 -> 137 ms. Cada nivel dice "no la se, pregunta
    a...", hasta el autoritativo. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La resolucion paso a paso")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el resolutor no sabe la respuesta --------------------
        rot.mostrar(pie_curso("El resolutor no conoce el nombre: tiene que "
                              "preguntar, nivel por nivel."),
                    zona="abajo", run_time=0.5)
        esc = escalera(ACTORES_DNS, EVENTOS_DNS, ancho=6.6, alto=3.6, fs=14)
        esc.shift(UP * 0.15)
        self.play(FadeIn(esc.actores), Create(esc.vidas), run_time=1.0)
        self.wait(3.4)

        # --- momento: viaje 1, cliente a resolutor --------------------------
        rot.mostrar(pie_curso("Primero, el cliente le pasa el nombre a su "
                              "propio resolutor."),
                    zona="abajo", run_time=0.5)
        self.play(Create(esc.paso(0)), run_time=0.7)
        self.wait(3.4)

        # --- momento: viaje 2, a la raiz -------------------------------------
        rot.mostrar(pie_curso("El resolutor no la sabe: pregunta a la raiz, "
                              "que contesta 'pregunta al de .org'."),
                    zona="abajo", run_time=0.5)
        self.play(Create(esc.paso(1)), run_time=0.7)
        self.wait(3.6)

        # --- momento: viaje 3, al TLD ------------------------------------
        rot.mostrar(pie_curso("El TLD .org tampoco la tiene: 'pregunta al "
                              "autoritativo de ejemplo.org'."),
                    zona="abajo", run_time=0.5)
        self.play(Create(esc.paso(2)), run_time=0.7)
        self.wait(3.6)

        # --- momento: viaje 4, el autoritativo responde ----------------------
        rot.mostrar(pie_curso("El autoritativo si la conoce: responde la "
                              "direccion real."),
                    zona="abajo", run_time=0.5)
        self.play(Create(esc.paso(3)), run_time=0.7)
        self.wait(3.4)

        # --- momento cierre del clip ------------------------------------
        rot.mostrar(pie_curso("Cuatro viajes, ciento treinta y siete "
                              "milisegundos, antes de la primera pagina."),
                    zona="abajo", run_time=0.5)
        resumen = tag_hud("%d viajes  ->  %s ms"
                          % (VIAJES_DNS, fmt(TOTAL_DNS_MS, 0)),
                          font_size=24)
        resumen.move_to(DOWN * 2.35)
        self.play(FadeIn(resumen, shift=0.15 * UP), run_time=0.5)
        self.wait(5.4)
