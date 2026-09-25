class Clip3(Scene):
    """3.2.3 - La cascada: una sola etapa de 219 coeficientes cuesta 52.6 M
    MAC/s; dos etapas mas baratas (39 anchos + 45 estrechos, dibujadas a la
    MISMA escala de frecuencia para que se note la diferencia) cuestan casi
    la mitad, 29.5 M MAC/s. Dos barras en la misma escala. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La cascada"), zona="arriba", run_time=0.6)
        self.wait(0.9)

        # --- las formas de las dos transiciones, grandes, mitad superior ----
        # `puntos` por encima del numero de muestras de la ventana: asi
        # `S.para_dibujar` NO recorta la cola derecha (su reduccion por
        # bloques de `puntos` en `puntos` deja fuera el resto de la
        # division, y con una ventana simetrica eso rompe la simetria del
        # panel). Medido en el contenedor: sin este margen la ventana
        # +-240 kHz de h1 llegaba solo hasta +198.6 kHz por la derecha.
        f0, d0 = S.para_dibujar(*S.respuesta_db(H, FS, n=8192), puntos=4000,
                                f_lo=-5e5, f_hi=5e5)
        h1 = S.fir_paso_bajo(A1, 120e3, FS, aten_db=60.0)
        fs1 = FS / 5
        h2 = S.fir_paso_bajo(A2, 120e3, fs1, aten_db=60.0)
        # las DOS etapas de la cascada, a la MISMA escala de frecuencia
        # (la de la segunda etapa, 480 kS/s, eje +-240 kHz): asi se ve que
        # la primera transicion es mucho mas ancha que la segunda.
        f1, d1 = S.para_dibujar(*S.respuesta_db(h1, FS, n=8192), puntos=2000,
                                f_lo=-2.4e5, f_hi=2.4e5)
        f2, d2 = S.para_dibujar(*S.respuesta_db(h2, fs1, n=8192), puntos=9000,
                                f_lo=-2.4e5, f_hi=2.4e5)

        y_fila = 1.0
        x_sep = 4.1
        filtro0 = S.Espectro(f0, d0, piso=-70.0, techo=4.0, ancho=3.4,
                             alto=2.7, color=C_LO, area=False, grosor=2.8)
        filtro0.move_to(LEFT * x_sep + UP * y_fila)
        filtro1 = S.Espectro(f1, d1, piso=-70.0, techo=4.0, ancho=3.4,
                             alto=2.7, color=C_LO, area=False, grosor=2.8)
        filtro1.move_to(UP * y_fila)
        filtro2 = S.Espectro(f2, d2, piso=-70.0, techo=4.0, ancho=3.4,
                             alto=2.7, color=C_LO, area=False, grosor=2.8)
        filtro2.move_to(RIGHT * x_sep + UP * y_fila)

        # un solo rotulo "kHz", al final del ultimo panel: los tres ejes
        # comparten unidad y los numeros de paneles vecinos ya no chocan.
        ticks0 = filtro0.marcas([-4e5, 0.0, 4e5], ["-400", "0", "400"])
        ticks1 = filtro1.marcas([-2e5, 0.0, 2e5], ["-200", "0", "200"])
        ticks2 = filtro2.marcas([-2e5, 0.0, 2e5], ["-200", "0", "200"])
        u2 = tag_junto(ticks2[-1], "kHz", RIGHT, buff=0.14, font_size=18)

        # --- cabecera compacta arriba de cada panel: descripcion + coefs ----
        d_una = tag_junto(filtro0, "una etapa", UP, buff=0.5, font_size=18)
        et_219 = tag_hud(f"{N_TAPS} coeficientes", font_size=19)
        et_219.next_to(d_una, UP, buff=0.1)
        self.play(Create(filtro0.ejes), Create(filtro0.curva),
                  FadeIn(ticks0), FadeIn(d_una), run_time=1.3)
        self.wait(1.2)
        self.play(FadeIn(et_219, shift=UP * 0.1), run_time=0.5)
        self.wait(3.2)

        d_dos = tag_junto(VGroup(filtro1, filtro2), "dos etapas", UP,
                          buff=0.5, font_size=18)
        et_39 = tag_hud(f"{A1}", font_size=20)
        et_39.next_to(filtro1, UP, buff=0.1)
        et_45 = tag_hud(f"{A2}", font_size=20)
        et_45.next_to(filtro2, UP, buff=0.1)
        self.play(Create(filtro1.ejes), Create(filtro1.curva),
                  FadeIn(ticks1),
                  Create(filtro2.ejes), Create(filtro2.curva),
                  FadeIn(ticks2), FadeIn(u2), FadeIn(d_dos), run_time=1.7)
        self.wait(1.2)
        self.play(FadeIn(et_39, shift=UP * 0.1), FadeIn(et_45, shift=UP * 0.1),
                  run_time=0.5)
        self.wait(4.2)

        # --- dos barras de MAC/s, misma escala, mitad inferior --------------
        # largo_max deja sitio a la cifra a la derecha sin tocar el borde
        # (>=0.5 u): la barra mas larga termina bien dentro del cuadro.
        largo_max = 8.4
        escala = largo_max / MAC1
        x0 = LEFT * 4.9

        b1 = Rectangle(width=largo_max, height=0.55, stroke_width=0,
                       fill_color=C_CALCULO, fill_opacity=0.85)
        b1.move_to(x0 + RIGHT * largo_max / 2 + DOWN * 1.25)
        largo2 = escala * MAC2
        b2 = Rectangle(width=largo2, height=0.55, stroke_width=0,
                       fill_color=C_CALCULO, fill_opacity=0.85)
        b2.move_to(x0 + RIGHT * largo2 / 2 + DOWN * 2.15)

        t1 = tag_hud(f"{fmt(MAC1 / 1e6, 1)} M MAC/s", font_size=22)
        t1.next_to(b1, RIGHT, buff=0.25)
        t2 = tag_hud(f"{fmt(MAC2 / 1e6, 1)} M MAC/s", font_size=22)
        t2.next_to(b2, RIGHT, buff=0.25)

        self.play(GrowFromEdge(b1, LEFT), FadeIn(t1), run_time=1.3)
        self.wait(3.0)
        self.play(GrowFromEdge(b2, LEFT), FadeIn(t2), run_time=1.3)
        self.wait(9.5)
