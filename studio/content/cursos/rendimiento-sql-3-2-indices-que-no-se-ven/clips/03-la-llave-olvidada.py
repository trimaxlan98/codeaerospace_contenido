class Clip3(Scene):
    """3.2.3 - detalle_pedido no tiene indice en id_pedido: para juntar las
    lineas de UN pedido el motor recorre la tabla entera. El contador sube
    hasta las paginas de la tabla; al final aparece el ticket real: una
    sola linea. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La llave olvidada"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        q = S.codigo(["SELECT * FROM detalle_pedido",
                      "WHERE id_pedido = 750000"], font_size=20)
        q.to_corner(UL, buff=0.6).shift(DOWN * 0.8)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        marca = SurroundingRectangle(q.lineas[1], color=C_MALO, buff=0.07,
                                     stroke_width=2.4)
        self.play(Create(marca), run_time=0.5)
        sin = tag_junto(q, "llave sin indice", DOWN, buff=0.18, color=C_MALO)
        self.play(FadeIn(sin), run_time=0.4)
        self.wait(2.2)

        cols, fils = 30, 14
        muro = S.MuroPaginas(columnas=cols, filas=fils, lado=0.165, sep=0.045,
                             color=C_TENUE, opacidad=0.14)
        muro.move_to(RIGHT * 2.9 + DOWN * 0.35)
        nom = Text("detalle_pedido", font_size=22, color=C_TITULO)
        nom.next_to(muro, UP, buff=0.2).align_to(muro, LEFT)
        self.play(FadeIn(nom), run_time=0.4)
        self.play(FadeIn(muro), run_time=0.9)
        self.wait(0.8)

        cont = Contador(0, rotulo="paginas", font_size=38, digitos=6)
        cont.next_to(sin, DOWN, buff=0.65).align_to(q, LEFT)
        self.play(FadeIn(cont), run_time=0.4)
        cont.anim(self, PAG_DETALLE, run_time=4.5,
                  extra=[LaggedStart(*muro.encender(range(len(muro)), C_MALO, 0.5),
                                     lag_ratio=0.003)])
        self.wait(1.0)
        rot.mostrar(motor_pie(f"{S.miles(PAG_DETALLE)} paginas"), zona="abajo", run_time=0.5)
        self.wait(2.8)
        rot.mostrar(cifra_pie(f"{S.miles(DETALLE_TOTAL)} renglones"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- el ticket real: una sola linea -------------------------------
        self.play(muro.animate.set_fill(C_TENUE, 0.08).set_stroke(C_TENUE, opacity=0.3),
                  run_time=0.8)
        # un ticket son 1-4 renglones: cabe en una pagina (el numero exacto
        # de este pedido no se rotula: la sonda solo valida el total)
        ticket = VGroup(S.pagina(0.6, 0.78, renglones=2, color=C_BUENO,
                                 relleno=0.3))
        ticket.next_to(cont, DOWN, buff=0.6).align_to(q, LEFT)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in ticket],
                              lag_ratio=0.3), run_time=0.8)
        et = tag_junto(ticket, "el ticket cabe aqui", RIGHT, buff=0.3, color=C_BUENO)
        self.play(FadeIn(et), run_time=0.4)
        self.wait(6.5)
