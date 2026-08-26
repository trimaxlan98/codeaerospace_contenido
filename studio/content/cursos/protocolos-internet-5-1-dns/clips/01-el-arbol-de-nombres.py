class Clip1(Scene):
    """5.1.1 - La jerarquia DNS por niveles (Arbol): quien manda en cada
    nivel, y por que se resuelve al reves de lo esperado: de derecha a
    izquierda. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El arbol de nombres")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la jerarquia, sin marcar -----------------------------
        rot.mostrar(pie_curso("Nadie escribe direcciones IP: hay una capa "
                              "de nombres organizada en niveles."),
                    zona="abajo", run_time=0.5)
        arb = arbol(ARBOL_NIVELES, marcados=(), ancho=9.4, alto=3.3, fs=14)
        arb.shift(UP * 0.35)
        self.play(Create(arb.ramas), FadeIn(arb.cajas, arb.textos),
                  run_time=1.3)
        self.wait(5.0)

        # --- momento: quien manda en cada nivel ----------------------------
        rot.mostrar(pie_curso("La raiz manda sobre los TLD; el TLD, sobre "
                              "sus dominios; el dominio, sobre sus "
                              "subdominios."),
                    zona="abajo", run_time=0.5)
        marcado = arb.con_marcados(ARBOL_SUB)
        marcado.shift(arb.get_center() - marcado.get_center())
        self.play(Transform(arb, marcado), run_time=1.1)
        self.wait(5.2)

        # --- momento: se lee al reves de lo esperado -----------------------
        rot.mostrar(pie_curso("Pero se resuelve al reves de lo esperado: "
                              "de derecha a izquierda."),
                    zona="abajo", run_time=0.5)
        n1 = tag_hud("1", font_size=20, color=C_PAQUETE)
        n1.next_to(arb.nodo(3, 2), RIGHT, buff=0.18)
        n2 = tag_hud("2", font_size=20, color=C_PAQUETE)
        n2.next_to(arb.nodo(1, 2), RIGHT, buff=0.18)
        n3 = tag_hud("3", font_size=20, color=C_PAQUETE)
        n3.next_to(arb.nodo(0, 0), RIGHT, buff=0.18)
        self.play(FadeIn(n1), run_time=0.4)
        self.wait(0.5)
        self.play(FadeIn(n2), run_time=0.4)
        self.wait(0.5)
        self.play(FadeIn(n3), run_time=0.4)
        self.wait(4.8)

        # --- momento cierre del clip (no de la leccion) --------------------
        rot.mostrar(pie_curso("www.ejemplo.org, luego .org, luego la raiz: "
                              "primero lo especifico, al final quien manda "
                              "sobre todos."),
                    zona="abajo", run_time=0.5)
        self.wait(6.0)
