class Clip4(Scene):
    """9.1.4 - Nadie regala nada: promediar cuesta resolucion, y elegir el
    trozo es elegir el compromiso. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 09"))
        rot.mostrar(titulo_curso("Lo que cuesta"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        piso = -25.0
        rf = respuesta_dibujo(F_W[256], DB_W[256], ancho=10.0, alto=2.8,
                              piso_db=piso, techo_db=12.0, color=C_SALIDA)
        rf.move_to(DOWN * 0.55)
        et_256 = tag_hud(f"trozo 256", font_size=19, color=C_SALIDA)
        et_256.next_to(rf, UP, buff=0.28)
        self.play(FadeIn(rf), FadeIn(et_256), run_time=1.0)
        rot.mostrar(cifra_pie(f"resolucion {fmt(RESOL[256], 2)} Hz"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- trozos mas largos: mejor resolucion, mas temblor -------------
        # OJO: 256 y 512 dan 129 y 257 bins. NO son gemelas (lo son las
        # que comparten eje), asi que se dibuja una pieza aparte sobre el
        # mismo rango en Hz en vez de Transform.
        rf2 = respuesta_dibujo(F_W[512], DB_W[512], ancho=10.0, alto=2.8,
                               piso_db=piso, techo_db=12.0, color=C_MUESTRA)
        rf2.move_to(DOWN * 0.55)
        et_512 = tag_hud(f"trozo 512", font_size=19, color=C_MUESTRA)
        et_512.next_to(rf, UP, buff=0.28)
        self.play(rf.curva.animate.set_stroke(opacity=0.30),
                  Create(rf2.curva), Transform(et_256, et_512),
                  run_time=1.6)
        self.add(rf2.curva)
        rot.mostrar(cifra_pie(f"resolucion {fmt(RESOL[512], 2)} Hz"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)
        rot.mostrar(cifra_pie(f"dispersion {fmt(DISP_W[512], 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        panel = panel_cifras(
            (f"256: {fmt(RESOL[256], 2)} Hz  {fmt(DISP_W[256], 2)} dB",
             C_SALIDA),
            (f"512: {fmt(RESOL[512], 2)} Hz  {fmt(DISP_W[512], 2)} dB",
             C_MUESTRA))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.0)
        rot.mostrar(formula_pie(r"\Delta f = f_s / L"), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        cierre_leccion(self, rot, "Un espectro medido una vez",
                       "no es el espectro.", rf, rf2.curva, et_256, panel)
