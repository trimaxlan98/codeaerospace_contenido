class Clip4(Scene):
    """2.1.4 - El transformador: dos devanados sobre el mismo nucleo, con
    las espiras contadas. El doble de vueltas, el doble de tension: subir
    para viajar lejos, bajar para usar. Cierra la leccion con el gancho
    hacia Maxwell. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El transformador")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: los dos devanados sobre el mismo nucleo -----------------
        tra = transformador(n1=N1_TRAFO, n2=N2_TRAFO)
        self.play(FadeIn(tra), run_time=0.7)
        rot.mostrar(pie_curso("Dos devanados sobre el mismo núcleo. "
                              "Cuenta las espiras de cada uno."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: cuenta el primario ----------------------------------------
        llave_1 = llave(tra.primario, f"{N1_TRAFO} espiras", direccion=LEFT)
        rot.mostrar(pie_curso("El primario, donde entra la corriente: "
                              f"{N1_TRAFO} vueltas."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(llave_1), run_time=0.7)
        self.wait(4.6)

        # --- momento: cuenta el secundario --------------------------------------
        llave_2 = llave(tra.secundario, f"{N2_TRAFO} espiras",
                        direccion=RIGHT)
        rot.mostrar(pie_curso("El secundario, donde sale: "
                              f"{N2_TRAFO} vueltas. El doble."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(llave_2), run_time=0.7)
        self.wait(4.6)

        # --- momento: la relacion calculada --------------------------------------
        rot.mostrar(formula_pie(
            rf"\frac{{V_2}}{{V_1}} = \frac{{N_2}}{{N_1}} = "
            rf"{tra.relacion():.1f}"), zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("El doble de espiras: el doble de "
                              "tensión. Subir para viajar lejos con "
                              "menos pérdidas, bajar para usarla."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        # --- cierre de la leccion: pantalla limpia -------------------------------
        self.play(FadeOut(tra), FadeOut(llave_1), FadeOut(llave_2),
                  run_time=0.8)
        rot.limpiar("arriba", run_time=0.4)
        linea1 = Text("Mover un imán hace corriente.", font_size=40,
                      color=C_TITULO)
        linea2 = Text("¿Y si nada se moviera?", font_size=40,
                      color=C_CALCULO)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        rot.mostrar(pie_curso("La corriente ya es tuya. La pregunta "
                              "grande la abre Maxwell."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.7)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.7)
        self.wait(4.6)
