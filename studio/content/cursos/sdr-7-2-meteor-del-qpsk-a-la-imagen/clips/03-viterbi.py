class Clip3(Scene):
    """7.2.3 - Viterbi (k = 7, tasa 1/2: norma, gris). A la izquierda 24
    bits CODIFICADOS tal como salen de la decision dura (con sus errores
    en rojo); a la derecha los 12 bits de datos que decodifica, en verde.
    Los bits duros se recalculan con la misma cadena que S.cadena_meteor
    (conv_k7 + qpsk_de_bits + ruido_complejo, semilla 4, rotacion 1) y se
    comprueba que dan BER_CRUDA. Cian: 5.6 % -> 0 errores. (~36 s)"""

    def construct(self):
        # --- la cadena, recalculada con la libreria --------------------------
        datos = S._bits_de_imagen(IMG)
        asm = np.array(S._a_bits(S.ASM, 32), int)
        cod = S.conv_k7(np.concatenate([asm, datos, np.zeros(6, int)]))
        n_sim = len(cod) // 2
        rx = S.qpsk_de_bits(cod) * np.exp(1j * np.pi / 2) \
            + S.ruido_complejo(n_sim, 10 ** (-ESN0 / 10), 4)
        z = rx * np.exp(-1j * np.pi / 2 * ROT)
        duros = np.empty(2 * n_sim, int)
        duros[0::2] = z.real < 0
        duros[1::2] = z.imag < 0
        err = duros != cod
        assert abs(err.mean() - BER_CRUDA) < 1e-12
        n_err = int(err.sum())
        dec = S._bits_de_imagen(IMG_RX)
        # el primer tramo de 12 bits de datos cuyos 24 bits codificados
        # traen exactamente 2 errores
        i0 = next(i for i in range(0, len(datos) - 12, 12)
                  if err[2 * (32 + i):2 * (32 + i + 12)].sum() == 2)
        c0 = 2 * (32 + i0)
        crudos, malos = duros[c0:c0 + 24], err[c0:c0 + 24]
        salida = dec[i0:i0 + 12]
        assert (salida == datos[i0:i0 + 12]).all()

        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Viterbi"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- la caja ---------------------------------------------------------
        caja = bloque("VITERBI", ancho=2.8, alto=1.5, color=C_EJE,
                      color_texto=C_TITULO, tamano=30)
        caja.move_to(UP * 1.05)
        norma = tag_dato("k = 7   tasa 1/2", font_size=22)
        norma.next_to(caja, DOWN, buff=0.22)
        self.play(FadeIn(caja), run_time=0.7)
        self.play(FadeIn(norma), run_time=0.5)
        self.wait(1.0)

        # --- los bits crudos (codificados) -----------------------------------
        def fila(bs, color):
            g = VGroup(*[Text(str(int(b)), font=FUENTE_HUD, font_size=30,
                              color=color) for b in bs])
            g.arrange(RIGHT, buff=0.13)
            return g

        izq = VGroup(fila(crudos[:12], C_TITULO),
                     fila(crudos[12:], C_TITULO)).arrange(DOWN, buff=0.3)
        izq.move_to(np.array([-4.35, caja.get_center()[1], 0]))
        der = fila(salida, C_OK)
        der.move_to(np.array([4.35, caja.get_center()[1], 0]))
        f1 = Arrow(izq.get_right(), caja.get_left(), buff=0.2,
                   color=C_EJE, stroke_width=3)
        f2 = Arrow(caja.get_right(), der.get_left(), buff=0.2,
                   color=C_EJE, stroke_width=3)
        t_izq = tag_junto(izq, "bits crudos", UP, buff=0.3, font_size=24)
        t_der = tag_junto(der, "datos", UP, buff=0.3, font_size=24,
                          color=C_OK)
        t_der.align_to(t_izq, DOWN)
        n24 = tag_junto(izq, f"{len(crudos)} bits", DOWN, buff=0.3,
                        font_size=22)
        n12 = tag_junto(der, f"{len(salida)} bits", DOWN, buff=0.3,
                        font_size=22)
        n12.align_to(n24, DOWN)

        self.play(FadeIn(t_izq), LaggedStart(*[FadeIn(b) for b in izq[0]],
                                              *[FadeIn(b) for b in izq[1]],
                                              lag_ratio=0.06),
                  run_time=1.8)
        self.play(FadeIn(n24), run_time=0.4)
        self.wait(1.0)
        rojos = [b for b, m in zip([*izq[0], *izq[1]], malos) if m]
        self.play(*[b.animate.set_color(C_RUIDO).scale(1.25) for b in rojos],
                  run_time=0.8)
        t_err = tag_junto(VGroup(*rojos), "errores", DOWN, buff=0.0,
                          font_size=22, color=C_RUIDO)
        t_err.next_to(n24, DOWN, buff=0.18)
        self.play(FadeIn(t_err), run_time=0.4)
        self.wait(2.0)

        # --- Viterbi decide ----------------------------------------------------
        self.play(GrowArrow(f1), run_time=0.6)
        self.play(caja[0].animate.set_fill(C_TITULO, opacity=0.3), run_time=0.5)
        self.play(caja[0].animate.set_fill(C_EJE, opacity=0.12),
                  GrowArrow(f2), run_time=0.6)
        self.play(FadeIn(t_der), LaggedStart(*[FadeIn(b) for b in der],
                                             lag_ratio=0.1),
                  run_time=1.4)
        self.play(FadeIn(n12), run_time=0.4)
        self.wait(2.2)

        # --- toda la imagen: los errores crudos contra los que quedan --------
        c_crudo = Contador(0.0, rotulo="errores crudos", dec=0,
                           muestra="8888", font_size=60)
        c_crudo.move_to(np.array([-4.6, -1.75, 0]))
        c_vit = Contador(0.0, rotulo="tras Viterbi", dec=0, muestra="8888",
                         font_size=60, color=C_OK)
        c_vit.move_to(np.array([4.1, -1.75, 0]))
        de_n = tag_hud(f"de {len(cod)}", font_size=24)
        de_n.next_to(c_crudo.muestra, RIGHT, buff=0.25)
        de_n.align_to(c_crudo.muestra, DOWN)
        self.play(FadeOut(n24), FadeOut(n12), FadeOut(t_err),
                  FadeIn(c_crudo.num), FadeIn(c_crudo.rot),
                  FadeIn(c_vit.num), FadeIn(c_vit.rot), run_time=0.6)
        c_crudo.anim(self, n_err, run_time=2.4)
        self.play(FadeIn(de_n), run_time=0.4)
        c_vit.fijar(ERR_VIT)
        self.wait(1.6)
        rot.mostrar(cifra_pie(f"{fmt(100 * BER_CRUDA, 1)} % -> {ERR_VIT}"
                              " errores"), zona="abajo", run_time=0.5)
        self.wait(3.0)
        self.play(Indicate(c_vit.num, color=C_OK, scale_factor=1.15),
                  run_time=1.0)
        self.wait(8.0)
