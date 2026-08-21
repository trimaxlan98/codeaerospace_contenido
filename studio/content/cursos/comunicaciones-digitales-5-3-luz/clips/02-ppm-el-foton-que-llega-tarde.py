class Clip2(Scene):
    """5.3.2 - PPM: el simbolo es la RANURA donde caen los fotones
    (`ranuras_ppm` + `ppm_fotones`, cuentas MEDIDAS, semilla fija); 4
    bits por simbolo en `tren_bits`; segunda tanda con otra semilla;
    LCRD/DSOC citados en el pie. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("PPM: el fotón que llega tarde")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: M ranuras esperan --------------------------------
        rot.mostrar(pie_curso("El PPM no cambia la fase: cambia CUÁNDO "
                              "llega el fotón. Dieciséis ranuras esperan "
                              "su turno."),
                    zona="abajo", run_time=0.5)
        ranuras = ranuras_ppm(M_PPM, CUENTAS_PPM_1, ancho=6.6)
        ranuras.move_to(UP * 0.85)
        et_m = tag_hud(f"M = {M_PPM} ranuras", font_size=18, color=C_BANDA)
        et_m.next_to(ranuras, UP, buff=0.28)
        self.play(FadeIn(ranuras), FadeIn(et_m), run_time=1.2)
        self.wait(3.8)

        # --- momento: el ruido salpica, la senal se amontona ---------------
        rot.mostrar(pie_curso("El ruido de fondo salpica todas las "
                              "ranuras; los fotones de la señal se "
                              "amontonan en UNA."),
                    zona="abajo", run_time=0.5)
        ganadora_1 = ranuras.ranura(GANADOR_PPM_1)
        et_gan = tag_hud(f"argmax -> simbolo {GANADOR_PPM_1}",
                         font_size=19, color=C_CIFRA)
        et_gan.next_to(ranuras, DOWN, buff=0.35)
        self.play(ganadora_1.animate.set_stroke(C_CIFRA, width=3.2),
                  FadeIn(et_gan, shift=0.1 * UP), run_time=1.0)
        self.wait(4.1)

        # --- momento: esa ranura ES el simbolo ------------------------------
        rot.mostrar(pie_curso("Esa ranura ES el símbolo: log2(16) = 4 "
                              "bits, sin tocar fase ni amplitud."),
                    zona="abajo", run_time=0.5)
        tren = tren_bits(BITS_PPM_1, lado=0.52)
        tren.move_to(DOWN * 2.0)
        et_tren = tag_junto(tren, "4 bits del símbolo", direccion=DOWN,
                            buff=0.2)
        self.play(TransformFromCopy(ganadora_1, tren), run_time=1.1)
        self.play(FadeIn(et_tren), run_time=0.4)
        self.wait(3.9)

        # --- momento: otra rafaga, otra semilla -----------------------------
        rot.mostrar(pie_curso("Otra ráfaga, otra semilla: la ranura "
                              "ganadora cambia, y los bits la siguen."),
                    zona="abajo", run_time=0.5)
        ranuras2 = ranuras.con_cuentas(CUENTAS_PPM_2)
        et_gan2 = tag_hud(f"argmax -> simbolo {GANADOR_PPM_2}",
                          font_size=19, color=C_CIFRA)
        et_gan2.move_to(et_gan)
        tren2 = tren.con_bits(BITS_PPM_2)
        self.play(ganadora_1.animate.set_stroke(C_EJE, width=1.1),
                  Transform(ranuras, ranuras2), Transform(et_gan, et_gan2),
                  Transform(tren, tren2), run_time=1.3)
        ganadora_2 = ranuras.ranura(GANADOR_PPM_2)
        self.play(ganadora_2.animate.set_stroke(C_CIFRA, width=3.2),
                  run_time=0.6)
        self.wait(3.6)

        # --- momento: un puñado de fotones habla desde muy lejos ------------
        rot.mostrar(pie_curso(
            f"Con un puñado de fotones por bit, así habla LCRD desde la "
            f"Luna ({fmt(LCRD_GBPS, 1)} Gb/s) y DSOC desde "
            f"{fmt(DSOC_DIST_MKM, 0)} millones de km."),
            zona="abajo", run_time=0.5)
        self.play(FadeOut(ranuras, et_gan, tren, et_tren, et_m),
                  run_time=0.7)

        enl = enlace_tierra(dist=3.6, radio_tierra=0.42, curva=0.32)
        enl.rotate(PI)
        enl.move_to(DOWN * 0.4 + RIGHT * 2.2)
        cam_ida = enl.camino.copy().reverse_points()
        self.play(FadeIn(enl), run_time=0.7)
        fotones = VGroup()
        for k, frac in enumerate((0.0, 0.35, 0.7)):
            f = Dot(cam_ida.point_from_proportion(frac), radius=0.045,
                   color=C_BIT)
            fotones.add(f)
        self.play(LaggedStart(
            *[PulsoDeSenal(f, cam_ida, rate_func=linear) for f in fotones],
            lag_ratio=0.4), run_time=3.2)
        self.wait(2.4)
