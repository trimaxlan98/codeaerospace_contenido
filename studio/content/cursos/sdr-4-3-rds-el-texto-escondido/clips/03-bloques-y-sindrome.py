from comunicaciones import TrenBits  # noqa: E402


class Clip3(Scene):
    """4.3.3 - Un bloque de 26 bits (16 datos + 10 de comprobacion). El
    sindrome calculado cae en el offset A cuando el bloque esta intacto;
    tras voltear un bit deja de coincidir con ningun offset. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Bloques y sindrome"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        bits26 = [(BLOQUE_A >> (25 - i)) & 1 for i in range(26)]
        datos_bits, check_bits = bits26[:16], bits26[16:]

        tb_datos = TrenBits(datos_bits, lado=0.46, color=C_SENAL)
        tb_check = TrenBits(check_bits, lado=0.46, color=C_TENUE)
        tb_check.next_to(tb_datos, RIGHT, buff=0.0)
        fila = VGroup(tb_datos, tb_check)

        et_datos = tag_junto(tb_datos, f"{len(datos_bits)} datos", DOWN,
                             buff=0.28, font_size=20, color=C_SENAL)
        et_check = tag_junto(tb_check, f"{len(check_bits)} control", DOWN,
                             buff=0.28, font_size=20, color=C_TENUE)
        bloque = VGroup(fila, et_datos, et_check)

        flecha = Arrow(UP * 0.8, DOWN * 0.8, color=C_CALCULO,
                      stroke_width=3.2, max_tip_length_to_length_ratio=0.22)
        sind_ok = S.sindrome(BLOQUE_A)
        sind_txt = tag_hud(f"sindrome {sind_ok:010b}", font_size=21,
                           color=C_CALCULO)

        pila = VGroup(bloque, flecha, sind_txt).arrange(DOWN, buff=0.45)
        pila.move_to(UP * 0.05)

        self.play(Create(tb_datos.celdas), Create(tb_check.celdas),
                  run_time=1.2)
        self.wait(0.5)
        self.play(FadeIn(tb_datos.digitos), FadeIn(tb_check.digitos),
                  run_time=0.8)
        self.wait(0.7)
        self.play(FadeIn(et_datos), FadeIn(et_check), run_time=0.5)
        self.wait(1.6)

        self.play(GrowArrow(flecha), run_time=0.6)
        self.wait(0.3)
        self.play(FadeIn(sind_txt), run_time=0.5)
        self.wait(1.6)

        # --- el sindrome cae en el offset A -------------------------------
        offset_ok = S.que_offset(BLOQUE_A)
        resultado = Text(offset_ok, font_size=60, color=C_OK)
        resultado.next_to(sind_txt, DOWN, buff=0.4)
        marco = SurroundingRectangle(fila, color=C_OK, buff=0.14,
                                     stroke_width=2.8)
        self.play(Create(marco), FadeIn(resultado, shift=DOWN * 0.12),
                  run_time=0.8)
        rot.mostrar(cifra_pie(f"offset {offset_ok}", color=C_OK),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        # --- se voltea un bit ------------------------------------------------
        self.play(FadeOut(marco), run_time=0.5)
        bloque_malo = BLOQUE_A ^ (1 << 7)
        i_flip = 25 - 7
        i_local = i_flip - len(datos_bits)
        nuevo_bit = 1 - check_bits[i_local]
        nuevo_digito = tag_hud(str(nuevo_bit), font_size=17, color=C_RUIDO)
        nuevo_digito.move_to(tb_check.digito(i_local))
        self.play(Transform(tb_check.digito(i_local), nuevo_digito),
                  tb_check.celda(i_local).animate.set_stroke(C_RUIDO,
                                                             width=2.8),
                  run_time=0.9)
        self.wait(0.6)
        self.play(Indicate(tb_check.celda(i_local), color=C_RUIDO,
                           scale_factor=1.35), run_time=0.8)
        self.wait(1.0)

        sind_malo = S.sindrome(bloque_malo)
        sind_txt2 = tag_hud(f"sindrome {sind_malo:010b}", font_size=21,
                            color=C_CALCULO)
        sind_txt2.move_to(sind_txt)
        self.play(Transform(sind_txt, sind_txt2), run_time=0.6)
        self.wait(1.2)

        offset_malo = S.que_offset(bloque_malo)
        texto_malo = f"offset {offset_malo}" if offset_malo else \
            "ningun offset"
        equis = Cross(resultado, stroke_color=C_RUIDO, stroke_width=5.0)
        self.play(FadeOut(resultado), Create(equis), run_time=0.7)
        rot.mostrar(cifra_pie(texto_malo, color=C_RUIDO), zona="abajo",
                    run_time=0.5)
        self.wait(6.8)
