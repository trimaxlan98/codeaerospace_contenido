class Clip4(Scene):
    """4.3.4 - Deshacer un eco es invertirlo: solo funciona si su cero
    esta DENTRO del circulo. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))
        rot.mostrar(titulo_curso("El eco que se deshace"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- el eco: dos golpes ---------------------------------------------
        eco = Secuencia(ECO_BUENO, 0, (0.0, 1.65), ancho=1.7, alto=0.95,
                        color=C_MUESTRA, radio=0.06)
        eco.move_to(LEFT * 4.0 + UP * 2.05)
        et_eco = tag_hud("eco 1 y 0.6", font_size=18, color=C_MUESTRA)
        et_eco.next_to(eco, UP, buff=0.18)
        self.play(FadeIn(eco), FadeIn(et_eco), run_time=0.8)
        rot.mostrar(formula_pie(r"H(z) = 1 + a\,z^{-1}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)

        # --- su cero, dentro del circulo -------------------------------------
        ceros_b = np.roots(ECO_BUENO)
        pz = plano_z(ceros_b, [], unidad=1.05, alcance=1.70)
        pz.move_to(LEFT * 4.0 + DOWN * 0.45)
        p_cero = pz.en(ceros_b[0].real) + DOWN * 1.45
        et_cero = _con_fondo(tag_hud(f"cero en {fmt(ceros_b[0].real, 1)}",
                                     font_size=18,
                                     color=C_SALIDA).move_to(p_cero))
        self.play(FadeIn(pz.ejes), run_time=0.4)
        self.play(Create(pz.circulo), run_time=1.1)
        self.play(FadeIn(pz.ceros[0], scale=0.5), FadeIn(et_cero),
                  run_time=0.7)
        self.wait(1.8)

        # --- el inverso se apaga ---------------------------------------------
        m_b = float(np.max(np.abs(INV_BUENO))) * 1.2
        inv_b = Secuencia(INV_BUENO, 0, (-m_b, m_b), ancho=7.0, alto=1.9,
                          color=C_SALIDA, radio=0.04, grosor=1.8)
        inv_b.move_to(RIGHT * 2.7 + UP * 1.15)
        et_inv_b = tag_hud("inverso", font_size=18, color=C_SALIDA)
        et_inv_b.next_to(inv_b, LEFT, buff=0.24)
        et_esc_b = tag_hud(f"escala {float(np.max(np.abs(INV_BUENO))):.0f}",
                           font_size=18, color=C_SALIDA)
        et_esc_b.next_to(inv_b, UP, buff=0.16)
        self.play(FadeIn(inv_b.ejes), FadeIn(et_inv_b), FadeIn(et_esc_b),
                  run_time=0.4)
        self.play(LaggedStart(*[FadeIn(inv_b.tallo(i))
                                for i in range(len(INV_BUENO))],
                              lag_ratio=0.03),
                  LaggedStart(*[FadeIn(inv_b.punto(i))
                                for i in range(len(INV_BUENO))],
                              lag_ratio=0.03), run_time=1.8)
        cola_b = inv_b.marcar(len(INV_BUENO) - 1, color=C_CALCULO)
        self.play(Create(cola_b), run_time=0.5)
        self.wait(3.6)

        # --- el mismo eco, con el cero FUERA ---------------------------------
        ceros_m = np.roots(ECO_MALO)
        gem_pz = pz.con_pz(ceros_m, [])
        gem_eco = eco.con_valores(ECO_MALO)
        et_cero2 = _con_fondo(tag_hud(f"cero en {fmt(ceros_m[0].real, 1)}",
                                      font_size=18,
                                      color=C_RUIDO).move_to(p_cero))
        et_eco2 = tag_hud("eco 1 y 1.4", font_size=18, color=C_MUESTRA)
        et_eco2.move_to(et_eco.get_center())
        self.play(Transform(pz, gem_pz), Transform(eco, gem_eco),
                  Transform(et_cero, et_cero2), Transform(et_eco, et_eco2),
                  run_time=1.6)
        # Transform mete `pz` ENTERO en la escena (sus partes entraron
        # sueltas con FadeIn/Create): sin esto el eje vertical queda POR
        # ENCIMA del rotulo y lo cruza. Se devuelven al frente.
        self.add(et_cero, et_eco)
        self.wait(2.0)

        # --- y su inverso revienta -------------------------------------------
        m_m = COLA_MALA * 1.2
        inv_m = Secuencia(INV_MALO, 0, (-m_m, m_m), ancho=7.0, alto=1.9,
                          color=C_RUIDO, radio=0.04, grosor=1.8)
        inv_m.move_to(RIGHT * 2.7 + DOWN * 1.55)
        et_inv_m = tag_hud("inverso", font_size=18, color=C_RUIDO)
        et_inv_m.next_to(inv_m, LEFT, buff=0.24)
        et_esc_m = tag_hud(f"escala {COLA_MALA:.0e}", font_size=18,
                           color=C_RUIDO)
        et_esc_m.next_to(inv_m, UP, buff=0.14)
        self.play(FadeIn(inv_m.ejes), FadeIn(et_inv_m), FadeIn(et_esc_m),
                  run_time=0.4)
        self.play(LaggedStart(*[FadeIn(inv_m.tallo(i))
                                for i in range(len(INV_MALO))],
                              lag_ratio=0.03),
                  LaggedStart(*[FadeIn(inv_m.punto(i))
                                for i in range(len(INV_MALO))],
                              lag_ratio=0.03), run_time=1.8)
        cola_m = inv_m.marcar(len(INV_MALO) - 1, color=C_CALCULO)
        self.play(Create(cola_m), run_time=0.5)
        rot.mostrar(cifra_pie(f"cola {COLA_BUENA:.0e} y {COLA_MALA:.0e}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        cierre_leccion(self, rot, "El modulo no cuenta toda la historia.",
                       "La fase dice cuando llega cada cosa.",
                       pz, eco, et_eco, et_cero, inv_b, et_inv_b,
                       et_esc_b, cola_b, inv_m, et_inv_m, et_esc_m,
                       cola_m)
