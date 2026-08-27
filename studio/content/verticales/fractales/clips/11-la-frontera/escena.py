class Clip(Scene):
    """11 · La frontera — una curva que es tan gorda como el plano.

    Se dibuja la ORLA del conjunto: todos los puntos de fuera que estan a
    menos de epsilon de la frontera. Para una curva normal —una
    circunferencia, el borde de una hoja— el area de esa orla se parte por
    la mitad cuando epsilon se parte por la mitad. Aqui no: al afinar
    epsilon queda el 75, el 77, el 79 por ciento del area anterior. La orla
    se niega a adelgazar.

    De esa terquedad sale la dimension: A(eps) ~ eps^(2-D), asi que D es dos
    menos la pendiente del ajuste log-log. Sobre la malla de este clip
    (1400x1400, 1200 iteraciones) da **1.6170**, y sube cada vez que se
    afina la malla (1.593 a 900, 1.623 a 1600, 1.639 a 2200). La teoria
    —Shishikura, 1991—
    demuestra que el limite es exactamente 2; un conteo finito nunca llega,
    y eso se dice en pantalla, en gris, porque no es una cifra medida aqui.

    Distancias, areas y ajuste: `distancia_mandelbrot` y
    `dimension_frontera`.
    """

    RES = 1400
    ITER = 1200
    ESCALAS = (16, 8, 4, 2)      # en pixeles de la malla, de gruesa a fina
    ALTO = 6.0
    Y_IMG = 1.40

    def construct(self):
        hud_top = hud_pieza("11 . la frontera")
        self.play(FadeIn(hud_top, shift=DOWN * 0.15), run_time=0.7)

        dist, paso = fr.distancia_mandelbrot(res=self.RES, max_iter=self.ITER)
        medida_fr = fr.dimension_frontera(dist=dist, paso=paso,
                                          escalas=tuple(
                                              sorted(self.ESCALAS)))

        # el conjunto solo, sin orla
        base = fr.imagen_orla(dist, paso, 0.0, color=C_MEDIDO,
                              alto_escena=self.ALTO, interior=C_ATRAPADO)
        base.move_to(UP * self.Y_IMG)
        base.set_z_index(5)
        marco = Rectangle(width=base.width, height=base.height,
                          stroke_width=1.4, stroke_color=C_EJE,
                          fill_opacity=0.0)
        marco.move_to(UP * self.Y_IMG)
        marco.set_z_index(8)

        etiqueta = hud("la orla", font_size=20, color=CODE_MUTED)
        etiqueta.move_to(UP * Y_ETIQUETA)
        sub = hud("a eps del borde", font_size=17, color=C_REGLA)
        sub.move_to(UP * Y_SUB)
        numero = None

        self.play(FadeIn(base), Create(marco), run_time=1.6)
        self.play(FadeIn(etiqueta), FadeIn(sub), run_time=0.5)

        # =============================================================
        # 1. La orla, epsilon a epsilon
        # =============================================================
        capa = None
        areas = []
        for i, escala in enumerate(self.ESCALAS):
            eps = escala * paso
            areas.append(float(fr.orla_frontera(dist, paso, eps).sum())
                         * paso * paso)
            nueva = fr.imagen_orla(dist, paso, eps, color=C_MEDIDO,
                                   alto_escena=self.ALTO,
                                   interior=C_ATRAPADO)
            nueva.move_to(UP * self.Y_IMG)
            nueva.set_z_index(6)
            if capa is None:
                self.play(FadeIn(nueva), run_time=1.2)
                self.wait(1.4)
            else:
                self.remove(capa)
                self.add(nueva)
                razon = areas[i] / areas[i - 1]
                et_nuevo = hud("queda del area", font_size=20,
                               color=CODE_MUTED)
                et_nuevo.move_to(UP * Y_ETIQUETA)
                num_nuevo = cifra(f"{razon:.3f}", font_size=104)
                num_nuevo.move_to(UP * Y_NUMERO)
                sub_nuevo = hud("al partir eps por 2", font_size=17,
                                color=C_REGLA)
                sub_nuevo.move_to(UP * Y_SUB)
                cambiar(self, [etiqueta, numero, sub],
                        [et_nuevo, num_nuevo, sub_nuevo])
                etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
                self.wait(1.9)
            capa = nueva
            self.remove(base)
            self.add(base)
            self.remove(base)
            self.add(base, capa)

        # lo que daria una curva de verdad
        sub_curva = nota_externa("una curva: 0.500", font_size=17)
        sub_curva.move_to(UP * Y_SUB)
        cambiar(self, sub, sub_curva, salida=0.28, entrada=0.34)
        sub = sub_curva
        self.wait(2.9)

        # =============================================================
        # 2. Esa terquedad tiene nombre: la dimension
        # =============================================================
        et_nuevo = hud("dimension", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{medida_fr['D']:.4f}", font_size=104)
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud("de la frontera", font_size=18, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, [etiqueta, numero, sub],
                [et_nuevo, num_nuevo, sub_nuevo])
        etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
        self.play(Flash(numero, color=C_MEDIDO, line_length=0.24,
                        num_lines=14, flash_radius=1.0), run_time=0.9)
        self.wait(2.8)

        sub_sube = hud("y sube al afinar", font_size=17, color=C_REGLA)
        sub_sube.move_to(UP * Y_SUB)
        cambiar(self, sub, sub_sube, salida=0.26, entrada=0.32)
        sub = sub_sube
        self.wait(2.6)

        # el dato que NO calcula esta libreria va en gris, y se declara
        sub_teoria = nota_externa("shishikura 1991 : 2", font_size=17)
        sub_teoria.move_to(UP * Y_SUB)
        cambiar(self, sub, sub_teoria, salida=0.26, entrada=0.32)
        sub = sub_teoria
        self.wait(3.8)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in (hud_top, base, capa, marco,
                                         etiqueta, numero, sub)],
                  run_time=1.1)
        self.wait(0.5)
