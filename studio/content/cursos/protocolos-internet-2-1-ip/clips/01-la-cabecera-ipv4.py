class Clip1(Scene):
    """2.1.1 - La cabecera IPv4 real de 20 bytes: doce campos, solo cuatro
    deciden algo, y el checksum se calcula en pantalla. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La cabecera IPv4")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: veinte bytes iguales para todo el mundo -------------
        rot.mostrar(pie_curso("Todo lo que cruza Internet empieza igual: "
                              "veinte bytes de cabecera."),
                    zona="abajo", run_time=0.5)
        cab = cabecera(CAMPOS_IPV4, CAB_VAL, ancho=CAB_ANCHO,
                       alto_fila=CAB_ALTO, fs=CAB_FS)
        cab.move_to(UP * 1.32)
        self.play(FadeIn(cab), run_time=1.2)
        grupo_hex = VGroup(
            tag_hud(CAB_HEX, font_size=19, color=C_CAPA),
            tag_hud("los %d bytes reales, en hexadecimal" % len(CAB_BYTES),
                    font_size=16, color=C_EJE),
        ).arrange(DOWN, buff=0.16)
        grupo_hex.move_to(DOWN * 0.75)
        self.play(FadeIn(grupo_hex), run_time=0.6)
        self.wait(4.4)

        # --- momento: solo cuatro deciden algo ---------------------------
        rot.mostrar(pie_curso("Doce campos, y solo cuatro deciden algo. "
                              "El resto es burocracia del formato."),
                    zona="abajo", run_time=0.5)
        cab_dec = cab.con_valores({})
        for nombre in CAMPOS_DECIDEN:
            cab_dec.iluminar(nombre)
        self.play(FadeOut(grupo_hex), run_time=0.35)
        self.play(Transform(cab, cab_dec), run_time=0.9)
        notas = VGroup(
            tag_hud("origen y destino   ->  quien habla y con quien",
                    font_size=20),
            tag_hud("TTL                ->  cuanta vida le queda",
                    font_size=20),
            tag_hud("Protocolo          ->  quien lee la carga al llegar",
                    font_size=20),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        notas.move_to(DOWN * 1.40)
        self.play(LaggedStart(*[FadeIn(n, shift=0.12 * UP) for n in notas],
                              lag_ratio=0.35), run_time=1.4)
        self.wait(4.2)

        # --- momento: el checksum se CALCULA ------------------------------
        rot.mostrar(pie_curso("El checksum no se escribe: se calcula, "
                              "sumando la cabecera en palabras de 16 bits."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(notas), run_time=0.35)
        cab_ck = cab.con_valores({})
        cab_ck.iluminar("Checksum")
        self.play(Transform(cab, cab_ck), run_time=0.7)
        cuentas = VGroup(
            tag_hud("  ".join("%04x" % w for w in CK_PALABRAS[:5]),
                    font_size=21, color=C_CAPA),
            tag_hud("  ".join("%04x" % w for w in CK_PALABRAS[5:]),
                    font_size=21, color=C_CAPA),
            tag_hud("las diez palabras, con el propio campo de checksum "
                    "puesto a cero", font_size=16, color=C_EJE),
            tag_hud("suma  0x%05x     pliega el acarreo  0x%04x + 0x%x  "
                    "=  0x%04x" % (CK_SUMA, CK_BAJA, CK_ACARREO, CK_PLEGADA),
                    font_size=20),
            tag_hud("complemento a uno  =  0x%04x" % CK_FINAL,
                    font_size=23),
        ).arrange(DOWN, buff=0.19, aligned_edge=LEFT)
        cuentas.move_to(DOWN * 1.45)
        self.play(LaggedStart(*[FadeIn(c, shift=0.10 * UP) for c in cuentas],
                              lag_ratio=0.32), run_time=1.9)
        self.wait(3.6)

        # --- momento: en cada salto se vuelve a sumar ---------------------
        rot.mostrar(pie_curso("En cada salto el router la vuelve a sumar. "
                              "Si no da cero, la tira sin avisar a nadie."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cuentas), run_time=0.35)
        ok = tag_hud("cabecera intacta           verificacion = %d"
                     % CK_INTACTA, font_size=22, color=C_OK)
        mal = tag_hud("un bit del TTL volteado    verificacion = %d"
                      % CK_ROTA, font_size=22, color=C_PERDIDA)
        veredicto = VGroup(ok, mal).arrange(DOWN, buff=0.30,
                                            aligned_edge=LEFT)
        veredicto.move_to(DOWN * 1.55)
        self.play(FadeIn(ok, shift=0.10 * UP), run_time=0.6)
        self.wait(1.8)
        cab_rota = cab.con_valores({"TTL": str(TTL_ROTO)})
        cab_rota.iluminar("TTL", C_PERDIDA)
        self.play(Transform(cab, cab_rota), run_time=0.7)
        self.play(FadeIn(mal, shift=0.10 * UP), run_time=0.6)
        et_tirada = tag_hud("descartada", font_size=24, color=C_PERDIDA)
        et_tirada.next_to(veredicto, DOWN, buff=0.28)
        self.play(FadeIn(et_tirada, scale=1.2), run_time=0.5)
        self.wait(3.6)
