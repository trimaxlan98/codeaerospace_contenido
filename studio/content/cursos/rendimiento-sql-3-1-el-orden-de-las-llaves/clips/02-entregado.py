class Clip2(Scene):
    """3.1.2 - 'entregado' es el 91.55% de la tabla: en los dos ordenes,
    el rango a recorrer es casi el mismo (aqui no hay lectura del motor
    que citar: solo la fraccion, calculada aqui). (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Entregado casi no cambia"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        ancla = Dot(UP * 2.6, radius=0.001)
        ancla.set_opacity(0)
        etiqueta_roja = tag_junto(ancla, "en rojo: entregado", DOWN,
                                  buff=0.05, color=C_MALO)
        self.play(FadeIn(etiqueta_roja), run_time=0.5)
        self.wait(1.8)

        top_y = 1.5

        # --- izquierda: por (fecha, estatus) -------------------------------
        grupos_izq = [
            ["entregado", "entregado", "entregado", "entregado", "cancelado"],
            ["entregado", "entregado", "entregado", "entregado"],
            ["entregado", "entregado", "entregado", "entregado", "pendiente"],
            ["entregado", "entregado", "entregado", "entregado"],
        ]
        col_izq, _ = lista_indice(grupos_izq, resaltado="entregado")
        col_izq.move_to(LEFT * 3.4)
        col_izq.shift(UP * (top_y - col_izq.get_top()[1]))
        tag_izq = tag_junto(col_izq, "orden: fecha, estatus", UP, buff=0.3)

        self.play(FadeIn(col_izq, shift=RIGHT * 0.2), run_time=1.2)
        self.play(FadeIn(tag_izq), run_time=0.5)
        self.wait(1.8)

        corchete_izq = corchete(col_izq, lado="izquierda")
        et_izq = tag_junto(corchete_izq, "casi todo", LEFT, buff=0.2,
                           color=C_CALCULO)
        self.play(Create(corchete_izq), FadeIn(et_izq), run_time=0.8)
        self.wait(2.2)

        # --- derecha: por (estatus, fecha) ---------------------------------
        grupos_der = [
            ["pendiente"],
            ["entregado"] * 16,
            ["cancelado"],
        ]
        col_der, bloques_der = lista_indice(grupos_der, resaltado="entregado")
        col_der.move_to(RIGHT * 3.4)
        col_der.shift(UP * (top_y - col_der.get_top()[1]))
        tag_der = tag_junto(col_der, "orden: estatus, fecha", UP, buff=0.3)

        self.play(FadeIn(col_der, shift=LEFT * 0.2), run_time=1.2)
        self.play(FadeIn(tag_der), run_time=0.5)
        self.wait(1.6)

        corchete_der = corchete(bloques_der[1], lado="derecha")
        et_der = tag_junto(corchete_der, "casi todo", RIGHT, buff=0.2,
                           color=C_CALCULO)
        self.play(Create(corchete_der), FadeIn(et_der), run_time=0.8)
        self.wait(2.2)

        rot.mostrar(cifra_pie(f"{FRAC_ENTREGADO * 100:.2f}% entregados"),
                    zona="abajo", run_time=0.5)
        self.wait(11.5)
