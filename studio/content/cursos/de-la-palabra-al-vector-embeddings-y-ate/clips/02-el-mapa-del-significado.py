class Clip2(Scene):
    """2 - El mapa del significado. Un plano donde cada palabra es un
    punto: los animales quedan juntos, y la resta rey - hombre + mujer
    aterriza junto a 'reina'. La geometria capta el significado."""

    def construct(self):
        rot = Rotulos(self)

        # --- Titulo del clip ---------------------------------------------
        titulo = titulo_curso("El mapa del significado")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.5)

        # --- El plano semantico ---------------------------------------------
        ejes = ejes_plano()
        self.play(Create(ejes), run_time=1.2)
        self.wait(0.6)

        # --- Grupo 1: los animales, juntos -----------------------------------
        # Direcciones pensadas una a una: las cuatro etiquetas del grupo
        # deben separarse entre si (no hay flechas todavia por aqui).
        # Hacia FUERA del racimo: perro es el mas alto (arriba), gato el
        # del borde derecho (derecha), felino arriba-izquierda y pez
        # abajo-izquierda. Con DOWN/RIGHT hacia dentro se pisaban.
        direcciones_animales = {
            "gato": RIGHT,
            "perro": UP,
            "felino": UL,
            "pez": DL,
        }
        animales = mapa_embeddings(ejes, ["gato", "perro", "felino", "pez"],
                                   direcciones=direcciones_animales)
        self.play(FadeIn(animales, lag_ratio=0.2), run_time=1.3)
        self.wait(0.3)

        # --- Grupo 2: realeza y personas --------------------------------------
        # Direcciones en diagonal/lateral: mas adelante origen->rey y
        # origen->hombre cruzan este cuadrante, asi que las etiquetas se
        # apartan de esa zona central.
        direcciones_personas = {
            "hombre": DOWN,
            "mujer": LEFT,
            "rey": RIGHT,
            "reina": UP,
        }
        personas = mapa_embeddings(ejes, ["rey", "reina", "hombre", "mujer"],
                                   direcciones=direcciones_personas)
        self.play(FadeIn(personas, lag_ratio=0.2), run_time=1.3)
        self.wait(0.3)

        # --- Grupo 3: el cielo -------------------------------------------------
        direcciones_cielo = {
            "sol": UP,
            "luna": DOWN,
        }
        cielo = mapa_embeddings(ejes, ["sol", "luna"],
                                direcciones=direcciones_cielo)
        self.play(FadeIn(cielo, lag_ratio=0.2), run_time=0.9)

        rot.mostrar(pie_curso("Cada palabra, un punto: cerca = parecido."),
                   zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- Vecinos: gato, perro y felino se acercan --------------------------
        trio = VGroup(animales.puntos["gato"], animales.puntos["perro"],
                     animales.puntos["felino"])
        self.play(Indicate(trio, color=C_VECTOR), run_time=1.3)
        rot.mostrar(pie_curso("'Gato' y 'felino', vecinos al fin."),
                   zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- Acto 2: rey - hombre + mujer ~ reina --------------------------------
        # Sin flechas de origen: 'hombre' cae casi sobre la linea
        # origen->rey y los remates se amontonaban sobre su punto y su
        # etiqueta. La version clasica es mas limpia: la flecha
        # hombre->rey es "la direccion realeza", y su copia desde 'mujer'
        # aterriza junto a 'reina'. Dos flechas paralelas, zona despejada.
        flecha_realeza = flecha_vector(ejes, "hombre", "rey",
                                       color=C_VECTOR)
        self.play(GrowArrow(flecha_realeza), run_time=1.3)
        self.wait(1.8)

        # La resta se calcula sobre los EMBEDDINGS reales: la flecha ambar
        # sale de 'mujer' con la misma direccion que hombre -> rey.
        hombre_arr = np.array(EMBEDDINGS["hombre"])
        rey_arr = np.array(EMBEDDINGS["rey"])
        mujer_arr = np.array(EMBEDDINGS["mujer"])
        destino = tuple(mujer_arr + (rey_arr - hombre_arr))

        flecha_resta = flecha_vector(ejes, "mujer", destino, color=C_ACENTO)
        self.play(GrowArrow(flecha_resta), run_time=1.4)
        self.wait(0.8)

        brillo_reina = punto_brillante(punto=ejes.c2p(*EMBEDDINGS["reina"]),
                                       color=C_ACENTO)
        self.play(FadeIn(brillo_reina), run_time=0.9)
        self.wait(1.2)

        rot.mostrar(formula_pie(r"\vec{rey} - \vec{hombre} + \vec{mujer} "
                                r"\approx \vec{reina}"), zona="abajo",
                   run_time=0.6)
        self.wait(3.4)

        # --- Cierre: solo queda la flecha ambar como conclusion -------------
        self.play(FadeOut(flecha_realeza), run_time=0.6)
        rot.mostrar(pie_curso("La geometría captura el significado."),
                   zona="abajo", run_time=0.5)
        self.wait(3.8)
