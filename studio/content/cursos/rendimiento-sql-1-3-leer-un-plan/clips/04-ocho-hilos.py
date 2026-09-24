class Clip4(Scene):
    """1.3.4 - El scan de pedidos (filtrado por id_cliente = 501, la misma
    consulta del resto de la leccion) se reparte en 8 franjas de UN solo
    matiz que se leen A LA VEZ; el motor LEE las 1,500,000 filas de la
    tabla pero solo 191 pasan el filtro, y esas son las que Gather Streams
    entrega. Scan count = 9 (motor, ambar) = 8 hilos + 1 coordinador
    (aritmetica, cian). Cierre de la leccion. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Ocho hilos"), zona="arriba", run_time=0.6)
        self.wait(0.5)

        # --- de que consulta se trata -----------------------------------
        consulta = S.codigo(["SELECT id_pedido, total", "FROM pedidos",
                             "WHERE id_cliente = 501"], font_size=20)

        # --- el muro, partido en 8 franjas de UN matiz (no papeles) ------
        colores = paleta_categorica(8)
        muro = S.MuroPaginas(columnas=24, filas=5, lado=0.24, sep=0.04,
                             color=C_TENUE, opacidad=0.16)
        et_leidas = tag_hud(f"{S.miles(FILAS_PED)} filas leidas", font_size=22)

        # --- 8 hilos, mismo matiz que su franja ---------------------------
        hilos = VGroup()
        for i in range(8):
            caja = Rectangle(width=0.6, height=0.46, stroke_color=colores[i],
                             stroke_width=2.4, fill_color=colores[i],
                             fill_opacity=0.22)
            num = Text(str(i + 1), font=FUENTE_HUD, font_size=22, color=C_TITULO)
            num.move_to(caja)
            hilos.add(VGroup(caja, num))
        hilos.arrange(RIGHT, buff=0.2)

        gather = S.operador("Gather Streams", color=C_TITULO, ancho=3.4,
                            font_size=24)

        # la consulta a la izquierda; el scan paralelo, apilado a la derecha
        # (asi el bloque no baja hasta el carril de la cifra)
        consulta.move_to(LEFT * 4.3 + UP * 1.6)
        resto = VGroup(muro, et_leidas, hilos, gather)
        resto.arrange(DOWN, buff=0.3)
        resto.move_to(RIGHT * 1.8 + UP * 0.25)

        self.play(FadeIn(consulta, shift=UP * 0.15), run_time=0.6)
        self.wait(0.6)
        self.play(FadeIn(muro), run_time=0.6)
        self.wait(0.3)

        anims = []
        anchopor = muro.columnas // 8
        for s in range(8):
            idx = [f * muro.columnas + c for f in range(muro.filas)
                   for c in range(s * anchopor, (s + 1) * anchopor)]
            anims += muro.encender(idx, colores[s], 0.85)
        self.play(*anims, run_time=1.3)
        self.play(FadeIn(et_leidas), run_time=0.4)
        self.wait(1.8)

        self.play(FadeIn(hilos), run_time=0.5)
        self.wait(0.8)

        lineas = VGroup(*[Line(h.get_bottom(), gather.get_top(), buff=0.05,
                              stroke_color=colores[i], stroke_width=1.8)
                          for i, h in enumerate(hilos)])
        self.play(Create(lineas), run_time=0.9)
        self.play(FadeIn(gather, shift=UP * 0.15), run_time=0.6)
        self.wait(1.0)

        # --- lo que SALE de Gather Streams: solo lo que paso el filtro ---
        ini_flecha = gather.get_left() + LEFT * 0.4
        fin_flecha = ini_flecha + LEFT * 2.3
        flecha = S.flecha_plan(ini_flecha, fin_flecha, C501, color=C_TENUE)
        et_filas = tag_hud(f"{S.miles(C501)} filas", font_size=20)
        et_filas.move_to((ini_flecha + fin_flecha) / 2 + DOWN * 0.32)
        self.play(Create(flecha), FadeIn(et_filas), run_time=0.7)
        self.wait(2.4)

        rot.mostrar(motor_pie(f"Scan count {HILOS_TOTAL}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)
        rot.mostrar(cifra_pie(f"{HILOS} hilos + 1 coordinador"), zona="abajo",
                    run_time=0.5)
        self.wait(4.2)

        cierre_leccion(self, rot, "El plan es un mapa.",
                       "Las flechas gruesas son el costo.",
                       consulta, muro, et_leidas, hilos, lineas, gather,
                       flecha, et_filas)
