class Clip4(Scene):
    """8.1.4 - El filtro que quita las imagenes va DESPUES de meter los
    ceros: simetria exacta con el filtro que va ANTES de diezmar. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 08"))
        rot.mostrar(titulo_curso("El filtro va despues"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- en el tiempo: la señal ya suave, con la malla mas fina ---------
        ventana = X_INTERP[80:112]
        sec = Secuencia(ventana, 0, (-1.6, 1.6), ancho=10.4, alto=1.9,
                        color=C_SALIDA, radio=0.04)
        sec.move_to(UP * 2.3)
        self.play(FadeIn(sec.ejes), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i))
                                for i in range(len(ventana))], lag_ratio=0.02),
                  LaggedStart(*[FadeIn(sec.punto(i))
                                for i in range(len(ventana))], lag_ratio=0.02),
                  run_time=1.6)
        self.wait(3.0)

        # --- el espectro: las imagenes ya no estan --------------------------
        ed = EspectroDoble(F_EJE_I2, DB_I2, piso_db=-90.0, ancho=9.6, alto=2.1,
                           color=C_BANDA)
        ed.move_to(DOWN * 1.55)
        self.play(FadeIn(ed.ejes), run_time=0.4)
        self.play(Create(ed.curva), FadeIn(ed.area), run_time=1.4)
        self.wait(2.0)

        imagen_ix = int(np.argmin(np.abs(F_EJE_I2 - F_IMAGEN_1)))
        db_imagen_despues = float(DB_I2[imagen_ix])
        marca_img = ed.marca_f(F_IMAGEN_1, color=C_SALIDA)
        et_img = tag_hud("sin imagen", font_size=18, color=C_SALIDA)
        et_img.next_to(ed.en(F_IMAGEN_1, 0.0), UP, buff=0.14)
        self.play(Create(marca_img), FadeIn(et_img), run_time=0.8)
        rot.mostrar(cifra_pie(f"{fmt(db_imagen_despues, 1)} dB en la imagen"),
                    zona="abajo", run_time=0.5)
        self.wait(3.8)

        self.play(FadeOut(sec.ejes), FadeOut(sec.tallos), FadeOut(sec.puntos),
                  run_time=0.6)

        panel = panel_cifras((f"diezmar: filtro antes", C_MUESTRA),
                             (f"interpolar: filtro despues", C_SALIDA))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.4)

        cierre_leccion(self, rot,
                       "Cambiar de ritmo no es tirar muestras.",
                       "Es filtrar y luego tirarlas.",
                       ed.ejes, ed.curva, ed.area, marca_img, et_img, panel,
                       espera=9.0)
