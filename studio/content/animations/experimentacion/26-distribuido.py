import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from distribuido import (COLOR_FALLO, COLOR_MENSAJE, COLOR_NODO, COLOR_OK,
                         COLOR_TIEMPO, anillo_hash, corona, curva_caidas,
                         diagrama_lamport, indices_caidos,
                         interseccion_quorum, linea_latencia, nodos_quorum,
                         par_centros, prob_alguna_caida, rejilla_nodos,
                         rtt_ms)
from code_brand import FUENTE_HUD, registrar_fuentes


class DemoDistribuido(Scene):
    """Demo de distribuido.py: la rejilla de nodos con unos cuantos
    caidos (`indices_caidos`) junto a la curva 1 - p^N que rotula, con
    `.en(1000)`, la probabilidad de que alguna de 1000 maquinas este
    caida en un instante dado; el mapa de latencia con las tres
    ciudades a escala real y sus arcos de mensaje rotulados con el
    piso fisico `rtt_ms`; el diagrama de Lamport con los relojes
    logicos CALCULADOS al recibir cada mensaje (`.reloj(p, i)`); los
    dos centros de datos separados por `.corte()`, la particion de
    red; la fila de nodos del quorum con los aros de escritura y
    lectura, la interseccion garantizada por
    `interseccion_quorum(5, 3, 3)` y la corona sobre el nodo que
    ambos conjuntos comparten; y por ultimo el anillo de hash
    consistente con `.con_nodo_extra("nodo-nuevo-0")` entrando y la
    fraccion de claves reubicadas MEDIDA con
    `.fraccion_movida("nodo-nuevo-0")`.

    Todo es determinista: mismo script, mismo render. Los numeros
    (probabilidad de caida, distancias y RTT, relojes de Lamport, la
    interseccion del quorum, la fraccion movida del anillo) salen de
    funciones y metodos de la libreria, medidos o calculados, nunca a
    mano.
    """

    def construct(self):
        registrar_fuentes()
        titulo = Text("Sistemas distribuidos: la nube por dentro",
                      font_size=24, color=COLOR_NODO)
        titulo.to_edge(UP, buff=0.22)
        self.add(titulo)

        # --- acto 1: la rejilla de nodos y la curva de caidas ---
        filas, columnas = 4, 8
        caidos = indices_caidos(filas * columnas, 4)
        rejilla = rejilla_nodos(filas=filas, columnas=columnas)
        rejilla.move_to(LEFT * 3.5 + UP * 0.5)
        self.play(FadeIn(rejilla.nodos), run_time=0.6)

        apagados = rejilla.apaga(caidos)
        self.play(*[Indicate(d, color=COLOR_FALLO, scale_factor=1.8)
                    for d in apagados], run_time=0.6)

        curva = curva_caidas()
        curva.move_to(RIGHT * 3.3 + UP * 0.3)
        self.play(FadeIn(curva.ejes), run_time=0.3)
        self.play(Create(curva.curva), run_time=1.0)

        prob_1000 = prob_alguna_caida(1000)
        punto_1000 = Dot(curva.en(1000), radius=0.06, color=COLOR_FALLO)
        etiqueta_prob = Text(
            f"P(alguna caida en 1000 maquinas) = {prob_1000:.1%}",
            font=FUENTE_HUD, font_size=13, color=COLOR_FALLO)
        etiqueta_prob.to_edge(DOWN, buff=0.6)
        self.play(FadeIn(punto_1000), FadeIn(etiqueta_prob), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(rejilla), FadeOut(curva), FadeOut(punto_1000),
                  FadeOut(etiqueta_prob), run_time=0.5)

        # --- acto 2: la latencia entre ciudades, a escala real ---
        origen = "CDMX"
        destinos = ("Nueva York", "Madrid", "Tokio")
        linea = linea_latencia(origen=origen, destinos=destinos)
        linea.move_to(UP * 0.1)
        ciudades = VGroup(linea.ciudad(origen),
                          *[linea.ciudad(d) for d in destinos])
        self.play(FadeIn(linea.base), run_time=0.3)
        self.play(FadeIn(ciudades), run_time=0.4)

        arcos = VGroup()
        etiquetas_rtt = VGroup()
        for destino in destinos:
            arco = linea.arco(destino)
            arcos.add(arco)
            self.play(Create(arco), run_time=0.6)
            rtt = rtt_ms(origen, destino)
            etiqueta = Text(f"{destino}: {rtt:.0f} ms", font=FUENTE_HUD,
                            font_size=11, color=COLOR_MENSAJE)
            etiqueta.next_to(linea.ciudad(destino), UP, buff=0.15)
            etiquetas_rtt.add(etiqueta)
            self.play(FadeIn(etiqueta), run_time=0.3)
        self.wait(0.3)
        self.play(FadeOut(linea), FadeOut(arcos), FadeOut(etiquetas_rtt),
                  run_time=0.5)

        # --- acto 3: el diagrama de Lamport ---
        diagrama = diagrama_lamport()
        diagrama.move_to(DOWN * 0.1)
        eventos_grupo = VGroup(*diagrama.eventos.values())
        self.play(FadeIn(diagrama.lineas), run_time=0.4)
        self.play(FadeIn(eventos_grupo), run_time=0.4)
        self.play(LaggedStart(*[GrowArrow(f) for f in diagrama.flechas],
                              lag_ratio=0.4), run_time=1.2)

        etiquetas_reloj = VGroup()
        for (p, i) in ((1, 1), (2, 1), (0, 2)):
            valor = diagrama.reloj(p, i)
            et = Text(str(valor), font=FUENTE_HUD, font_size=13,
                     color=COLOR_TIEMPO)
            et.next_to(diagrama.evento(p, i), RIGHT, buff=0.12)
            etiquetas_reloj.add(et)
        self.play(FadeIn(etiquetas_reloj), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(diagrama), FadeOut(etiquetas_reloj), run_time=0.5)

        # --- acto 4: los dos centros de datos y la particion ---
        centros = par_centros()
        centros.move_to(UP * 0.2)
        self.play(FadeIn(centros.cajas), run_time=0.4)
        self.play(Create(centros.enlace), run_time=0.5)

        corte = centros.corte()
        self.play(*[Create(t) for t in corte], run_time=0.5)
        etiqueta_corte = Text("particion de red", font=FUENTE_HUD,
                              font_size=13, color=COLOR_FALLO)
        etiqueta_corte.next_to(corte, DOWN, buff=0.35)
        self.play(FadeIn(etiqueta_corte), run_time=0.4)
        self.wait(0.4)
        self.play(FadeOut(centros), FadeOut(corte), FadeOut(etiqueta_corte),
                  run_time=0.5)

        # --- acto 5: el quorum, su interseccion y la corona ---
        quorum = nodos_quorum(n=5)
        quorum.move_to(UP * 0.1)
        self.play(FadeIn(quorum.nodos), run_time=0.5)

        idx_w, idx_r = (0, 1, 2), (2, 3, 4)
        aros_w = quorum.aro(idx_w, color=COLOR_MENSAJE, radio=0.30)
        aros_r = quorum.aro(idx_r, color=COLOR_OK, radio=0.42)
        self.play(FadeIn(aros_w), run_time=0.5)
        self.play(FadeIn(aros_r), run_time=0.5)

        interseccion = interseccion_quorum(5, 3, 3)
        comunes = quorum.interseccion(idx_w, idx_r)
        etiqueta_quorum = Text(
            f"interseccion_quorum(5,3,3) = {interseccion}",
            font=FUENTE_HUD, font_size=13, color=COLOR_OK)
        etiqueta_quorum.next_to(quorum, DOWN, buff=0.6)
        self.play(FadeIn(etiqueta_quorum), run_time=0.4)

        lider = quorum.nodo(comunes[0])
        cor = corona()
        cor.next_to(lider, UP, buff=0.08)
        self.play(FadeIn(cor), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(quorum), FadeOut(aros_w), FadeOut(aros_r),
                  FadeOut(etiqueta_quorum), FadeOut(cor), run_time=0.5)

        # --- acto 6: el anillo de hash consistente ---
        anillo = anillo_hash()
        anillo.move_to(LEFT * 3.3 + DOWN * 0.2)
        self.play(Create(anillo.circulo), run_time=0.6)
        self.play(FadeIn(VGroup(*anillo.nodos.values())), run_time=0.4)
        self.play(FadeIn(VGroup(*anillo.claves.values())), run_time=0.5)

        anillo_extra = anillo.con_nodo_extra("nodo-nuevo-0")
        anillo_extra.move_to(RIGHT * 3.3 + DOWN * 0.2)
        self.play(FadeIn(anillo_extra), run_time=0.6)

        frac = anillo.fraccion_movida("nodo-nuevo-0")
        etiqueta_anillo = Text(
            f'fraccion_movida("nodo-nuevo-0") = {frac:.1%}',
            font=FUENTE_HUD, font_size=13, color=COLOR_TIEMPO)
        etiqueta_anillo.next_to(VGroup(anillo, anillo_extra), DOWN,
                                buff=0.55)
        self.play(FadeIn(etiqueta_anillo), run_time=0.5)
        self.wait(0.5)
        self.play(FadeOut(anillo), FadeOut(anillo_extra),
                  FadeOut(etiqueta_anillo), run_time=0.5)
