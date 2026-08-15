class Clip1(Scene):
    """1 - Un microradian son cinco metros. El blanco visto desde el haz:
    huella de 98.7 m de diametro (9.87 urad a 5000 km) sobre el receptor.
    Con 1 urad de error la huella se corre 5 m y el satelite sigue dentro;
    con 10 urad se corre 50 m y se sale por 66 cm: el enlace se cae. Cierra
    con la cita geometrica del cabello a cien metros. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Un microradián son cinco metros"),
                    zona="arriba", run_time=0.6)

        # La pieza vive a la IZQUIERDA (receptor en x = -2.2): con 10 urad la
        # huella se corre 1.58 u en direccion (1, 0.35) y llega hasta x = 0.85,
        # asi que la columna de cifras de la derecha (x >= 1.9) nunca la toca.
        # Se coloca por `centro()` (el receptor) y no por la caja: la caja
        # cambia cuando la huella se sale.
        centro_rx = LEFT * 2.2

        def blanco(urad):
            g = punteria(R_km=R_ISL_KM, theta_urad=DIV_ISL_URAD,
                         error_urad=urad, ancho=5.2)
            g.shift(centro_rx - g.centro())
            return g

        def cifra(texto, y, color=None, font_size=16):
            t = tag_hud(texto, font_size=font_size, color=color)
            t.move_to(np.array([1.9, y, 0.0]), aligned_edge=LEFT)
            return t

        p = blanco(0.0)

        # --- momento: el blanco visto desde el haz --------------------------
        rot.mostrar(pie_curso(
            f"Así ve el haz a su blanco: el receptor dentro de una huella de "
            f"{HUELLA_ISL_M:.0f} metros."), zona="abajo")
        self.play(FadeIn(p, shift=0.14 * UP), run_time=0.9)
        t_huella = cifra(f"huella {HUELLA_ISL_M:.1f} m de diametro", 1.85,
                         color=C_FRANJA)
        self.play(FadeIn(t_huella), run_time=0.4)
        self.wait(4.2)

        # --- momento: un microradian -----------------------------------------
        rot.mostrar(pie_curso("A cinco mil kilómetros, un error de un "
                              "microrradián mueve la mancha cinco metros."),
                    zona="abajo")
        p1 = blanco(1.0)
        self.play(Transform(p, p1), run_time=1.1)
        t_1 = cifra(f"1 urad -> {JITTER_1URAD_M:.0f} m", 1.05)
        self.play(FadeIn(t_1), run_time=0.4)
        self.wait(3.9)

        # --- momento: con diez, se cae ---------------------------------------
        rot.mostrar(pie_curso("Con diez, la mancha ya no toca al satélite: "
                              "el enlace se cae."), zona="abajo")
        # La huella de 1 urad se queda de sombra para que el ultimo frame
        # muestre los DOS errores (dentro y fuera), como pide el final_state.
        sombra = p.huella_circulo.copy()
        sombra.set_stroke(width=1.6, opacity=0.50)
        sombra.set_fill(C_FRANJA, opacity=0.07)
        et_sombra = tag_hud("1 urad", font_size=14, color=C_FRANJA)
        et_sombra.next_to(sombra, DOWN, buff=0.12)
        self.add(sombra, et_sombra)

        p10 = blanco(10.0)
        self.play(Transform(p, p10), run_time=1.2)
        et_10 = tag_hud("10 urad", font_size=14, color=C_FRANJA)
        et_10.next_to(p.huella_circulo, UP, buff=0.12)
        d10_m = desplazamiento_por_jitter(10e-6, R_ISL_KM * 1e3)
        t_10 = cifra(f"10 urad -> {d10_m:.0f} m", 0.25)
        # `acierta()` lo dice la pieza, no el guion: 50.0 m > 49.3 m de radio.
        t_perdido = cifra("enlace perdido" if not p10.acierta() else "enlace",
                          -0.45, color=C_HAZ)
        self.play(FadeIn(et_10), FadeIn(t_10), run_time=0.4)
        self.play(FadeIn(t_perdido),
                  Flash(p.receptor, color=C_HAZ, line_length=0.18,
                        num_lines=14, flash_radius=0.62), run_time=0.7)
        self.wait(3.4)

        # --- momento: cuanto es un microradian -------------------------------
        rot.mostrar(pie_curso("Un microrradián es el grosor de un cabello "
                              "visto a cien metros."), zona="abajo")
        mm_100 = desplazamiento_por_jitter(1e-6, 100.0) * 1e3
        t_cabello = cifra(f"1 urad ~ {mm_100:.1f} mm a 100 m", -1.35,
                          color=C_TENUE, font_size=15)
        self.play(FadeIn(t_cabello), run_time=0.4)
        self.wait(4.6)

        # --- cierre ------------------------------------------------------------
        rot.mostrar(pie_curso("Apuntar así no es óptica: es control de "
                              "precisión."), zona="abajo")
        self.wait(5.0)
