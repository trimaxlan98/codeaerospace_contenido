# 03 · Lo que cabe en 520 KB
#
# La SRAM como un contenedor VERTICAL de contorno (no relleno), y los
# fotogramas como piezas de trazo ambar que caen dentro, una a una, para
# que se puedan CONTAR. Cada pieza mide 112.5/520 del contenedor: es la
# proporcion real (`chip.bytes_fotograma`, `chip.caben`), no un dibujo a
# mano. Al llegar a la cuarta sobra un hueco mas bajo que una pieza — ese
# hueco ES el remate, y el clip termina ahi (nada de datos ajenos al
# dibujo que se ve).
class Clip(Pieza):
    NUMERO = 3

    def pieza(self):
        L = self.L

        total_kib = chip.HOJA["sram_kb"]                    # 520
        b = chip.bytes_fotograma(240, 240, 16)                # 115200 B
        kib = b / 1024.0                                      # 112.5 KiB
        n = chip.caben(chip.memoria_kb(total_kib), b)          # 4

        # --- geometria del contenedor: un rectangulo alto, de contorno ---
        cont_w, cont_h = 2.2, 5.0
        gap = 0.12
        pieza_w = cont_w - 0.36
        # `n` huecos reservados (uno bajo la primera pieza y uno entre
        # cada par); lo que queda se reparte proporcional a los KiB reales,
        # igual que hace `barra_apilada` con su buff.
        usable_h = cont_h - gap * n
        pieza_h = usable_h * (kib / total_kib)

        centro = lz.centro_banda()
        c_bottom = centro[1] - cont_h / 2

        def y_pieza(i):
            y_bottom = c_bottom + gap + (i - 1) * (pieza_h + gap)
            return y_bottom + pieza_h / 2

        # --- el contenedor, vacio -----------------------------------------
        contenedor = RoundedRectangle(width=cont_w, height=cont_h,
                                      corner_radius=0.14,
                                      stroke_color=APAGADO,
                                      stroke_width=chip.TRAZO_FINO,
                                      fill_opacity=0.0)
        L.escena(contenedor, animacion=Create(contenedor, run_time=1.2))
        L.dato(total_kib, "kilobytes de memoria interna", medido=False)
        self.wait(6.0)

        # --- cae el primer fotograma ---------------------------------------
        def pieza_i(i):
            # Trazo puro, con el fondo del lienzo dentro: un fill ambar
            # translucido sobre AZUL da un verde oliva sucio (medido: 30 %
            # de opacidad produce (81,68,44), y a menos opacidad ya no lee
            # como ambar). El relleno opaco es a proposito, tapa bien entre
            # piezas y contra el contenedor.
            p = RoundedRectangle(width=pieza_w, height=pieza_h,
                                 corner_radius=0.10, stroke_color=AMBAR,
                                 stroke_width=2.4, fill_color=AZUL,
                                 fill_opacity=1.0)
            p.move_to([centro[0], y_pieza(i), 0])
            return p

        p1 = pieza_i(1)
        self.play(Create(p1, run_time=0.6))
        L.dato(medido(kib, 1), "kilobytes de un fotograma", medido=True)
        self.wait(5.5)

        # --- el segundo, el tercero y el cuarto: contables, con aire -------
        for i in range(2, n + 1):
            pi = pieza_i(i)
            self.play(Create(pi, run_time=0.7))
            self.wait(1.7)

        # --- el quinto no cabe: el hueco de arriba es el remate -------------
        L.dato(n, "fotogramas y no mas", medido=True)
        self.wait(6.0)
