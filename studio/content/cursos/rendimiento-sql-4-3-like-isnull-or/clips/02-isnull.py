class Clip2(Scene):
    """4.3.2 - ISNULL(telefono, '') envuelve la columna: el motor ya no
    puede saltar por el indice y revisa cliente por cliente (535, ambar).
    telefono = '...' sin envolver, con el mismo indice, es un seek (3,
    ambar). El motivo de escribir ISNULL: hay telefonos nulos de verdad
    (39,854, cian) y sin el ISNULL esos clientes no aparecerian. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("ISNULL envuelve la columna"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        q = S.codigo(["SELECT id_cliente", "FROM clientes",
                      "WHERE ISNULL(telefono, '')", "  = '5500000000'"],
                     font_size=20)
        q.to_corner(UL, buff=0.55).shift(DOWN * 0.55)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        marca = SurroundingRectangle(q.lineas[2], color=C_MALO, buff=0.07,
                                     stroke_width=2.4)
        self.play(Create(marca), run_time=0.5)
        et_env = tag_junto(q, "envuelve la columna", DOWN, buff=0.2,
                           color=C_MALO)
        self.play(FadeIn(et_env), run_time=0.4)
        self.wait(2.6)

        # --- duelo en escala logaritmica: envuelta contra directa. Las
        # barras empiezan en x=0 (nunca a la derecha de x=0) para que, con
        # su etiqueta numerica pegada a la punta, quepan enteras dentro del
        # cuadro (largo 4.6 + tag ~1.5 = 6.1, dentro de x <= 6.3). ------------
        largo, alto = 4.6, 0.5
        maximo = ISNULL_MAL

        bar_rojo = S.barra_lecturas(ISNULL_MAL, maximo, largo=largo, alto=alto,
                                    color=C_MALO, log=True)
        bar_rojo.shift(UP * 0.55)
        bar_verde = S.barra_lecturas(ISNULL_BIEN, maximo, largo=largo,
                                     alto=alto, color=C_BUENO, log=True)
        bar_verde.shift(DOWN * 1.15)

        base = Line([0, 0.95, 0], [0, -1.75, 0], stroke_color=C_TENUE,
                   stroke_width=2)
        self.play(Create(base), run_time=0.5)
        aviso = tag_junto(base, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.5)

        lab_r = tag_junto(bar_rojo, "columna envuelta", LEFT, buff=0.3,
                          color=C_MALO)
        self.play(GrowFromEdge(bar_rojo, LEFT), FadeIn(lab_r), run_time=0.9)
        tag_r = tag_motor(lecturas(ISNULL_MAL))
        tag_r.next_to(bar_rojo, RIGHT, buff=0.22)
        self.play(FadeIn(tag_r), run_time=0.4)
        self.wait(1.8)

        lab_v = tag_junto(bar_verde, "comparacion directa", LEFT, buff=0.3,
                          color=C_BUENO)
        self.play(GrowFromEdge(bar_verde, LEFT), FadeIn(lab_v), run_time=0.9)
        tag_v = tag_motor(lecturas(ISNULL_BIEN))
        tag_v.next_to(bar_verde, RIGHT, buff=0.22)
        self.play(FadeIn(tag_v), run_time=0.4)
        self.wait(2.4)

        razon = S.razon(ISNULL_MAL, ISNULL_BIEN)
        rot.mostrar(cifra_pie(f"{S.miles(round(razon))}x menos lecturas"),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(bar_rojo, color=C_MALO, scale_factor=1.03),
                  Indicate(bar_verde, color=C_BUENO, scale_factor=1.08),
                  run_time=1.0)
        self.wait(4.2)

        # --- por que alguien escribio el ISNULL ------------------------------
        rot.mostrar(cifra_pie(f"{S.miles(TEL_NULOS)} sin telefono"),
                    zona="abajo", run_time=0.5)
        self.wait(8.5)
