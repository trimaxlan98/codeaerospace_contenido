from comunicaciones import Onda  # noqa: E402


class Clip2(Scene):
    """4.3.2 - A escala ilustrativa (declarada en pantalla): una portadora
    de pocos ciclos por medio bit, con el SIGNO real que da el codigo
    bifase de S.rds_banda_base sobre 6 bits (dif. acumulada, +-1 por medio
    bit). Cada cambio de signo real es la onda "dando la vuelta" 180
    grados (marca roja). 192 muestras por bit es la cifra real (cian); el
    salto de 180 grados es la norma bifase (gris). (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La fase que salta"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        # --- el signo real por medio bit: la MISMA cuenta diferencial de
        # S.rds_banda_base (dif acumulada XOR, simbolo = 2*dif - 1) --------
        bits_ctx = [int(b) for b in BITS_PS[:16]]
        dif, prev = [], 0
        for b in bits_ctx:
            prev ^= b
            dif.append(prev)
        sim = [2 * d - 1 for d in dif]
        bits_mostrados = bits_ctx[5:11]
        sim_mostrados = sim[5:11]

        # --- portadora ilustrativa: FASE CONTINUA (sin reiniciar en cada
        # medio bit) multiplicada por el signo real: donde el signo se
        # mantiene la onda sigue igual; donde cambia, la onda salta de
        # signo en seco (el giro de 180 grados se ve, no se disimula).
        # Pocos ciclos por medio bit para que el salto se note. -------------
        ciclos_medio = 1
        ppc = 36
        n_medio = ciclos_medio * ppc
        signos = []
        for s in sim_mostrados:
            signos.append(s)
            signos.append(-s)
        n_total = n_medio * len(signos)
        fase = np.linspace(0.0, 2 * np.pi * ciclos_medio * len(signos),
                           n_total, endpoint=False)
        signo_muestra = np.repeat(signos, n_medio)
        onda_ilus = np.cos(fase) * signo_muestra
        t = np.arange(n_total, dtype=float)

        ow = Onda(t, onda_ilus, rango_y=(-1.15, 1.15), ancho=11.0, alto=2.6,
                 color=C_SENAL, grosor=2.8)
        ow.move_to(UP * 0.6)

        self.play(Create(ow.ejes), run_time=0.5)
        self.wait(0.3)
        self.play(Create(ow.curva), run_time=2.0)
        self.wait(1.2)

        et_ilus = tag_dato("escala ilustrativa")
        et_ilus.next_to(ow, UP, buff=0.2)
        self.play(FadeIn(et_ilus), run_time=0.5)
        self.wait(1.8)

        # --- una linea roja vertical, de pico a valle, en CADA cambio de
        # signo real: ahi el valor pasa de +1 a -1 en una sola muestra ------
        saltos = VGroup()
        for k in range(1, len(signos)):
            if signos[k] != signos[k - 1]:
                tb = float(k * n_medio)
                a, b = ow.en(tb, -1.0), ow.en(tb, 1.0)
                saltos.add(Line(a, b, color=C_RUIDO, stroke_width=2.6))
        self.play(Create(saltos), run_time=1.0)
        self.wait(2.2)

        # --- los bits debajo: casillas grandes, 1 ambar / 0 gris ------------
        lado_bit = 0.75
        fila_y = ow.get_bottom()[1] - 0.55 - lado_bit / 2
        celdas = VGroup()
        digitos = VGroup()
        for k, b in enumerate(bits_mostrados):
            tc = float((2 * k + 1) * n_medio)
            x = ow.en(tc, 0.0)[0]
            color_b = C_SENAL if b else C_TENUE
            c = Square(lado_bit, color=color_b, stroke_width=2.2)
            c.move_to(np.array([x, fila_y, 0.0]))
            d = Text(str(b), font_size=28, color=color_b)
            d.move_to(c)
            celdas.add(c)
            digitos.add(d)
        self.play(Create(celdas), run_time=0.9)
        self.wait(0.5)
        self.play(FadeIn(digitos), run_time=0.6)
        self.wait(2.2)

        rot.mostrar(cifra_pie(f"{S.MUESTRAS_BIT} muestras por bit"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)
        rot.mostrar(dato_pie("salto de 180 grados"), zona="abajo",
                    run_time=0.5)
        self.wait(8.0)
