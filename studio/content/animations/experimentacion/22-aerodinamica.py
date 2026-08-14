import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

from manim import *
from aerodinamica import (COLOR_CALCULO, COLOR_EJE, COLOR_SUBSONICO,
                          REGIMENES_TOBERA,
                          COLOR_SUPERSONICO, COLOR_TRANSONICO,
                          balanza_energias, banda_regimenes, barras_calores,
                          barras_entalpia, conducto, curva_compresibilidad,
                          curva_anemometro, curva_area_mach, curva_mu,
                          curva_sonido, curvas_choque, curvas_isentropicas,
                          diagrama_ts, diagrama_xt, escalera_velocidades,
                          esquema_schlieren, frentes_moviles, perfil_choque,
                          perfil_isa, perfil_tobera, piston_gas,
                          pulso_conducto, remanso, tabla_isentropica,
                          volumen_control, abanico_expansion, curva_nu,
                          diagrama_theta_beta, interseccion_choques,
                          onda_oblicua, perfil_supersonico, reflexion_onda,
                          ala_flecha, comparacion_teorias,
                          curva_arrastre_transonico, curva_mach_critico,
                          curvas_correcciones, distribucion_area,
                          perfiles_transonicos)
from code_brand import FUENTE_HUD, registrar_fuentes


class DemoAerodinamica(Scene):
    """Demo de aerodinamica.py: el error del modelo incompresible, el Mach
    como reparto de energias, los cuatro regimenes, los frentes de una fuente
    movil, el gas ideal con su embolo, cp = cv + R, el volumen de control, el
    plano T-s, el pulso que define el sonido, a(T) y a(altitud), el cono que
    se cierra, el conducto de area variable, la entalpia total que no se
    mueve, el punto de remanso, las tres razones isentropicas, la tabla de
    NACA 1135 generada (no transcrita) y —del modulo 2— la coalescencia en
    el plano x-t, el espesor real del choque, el banco Schlieren, los
    saltos del choque normal, el error del anemometro, las cuatro
    velocidades, A/A* con sus dos ramas y la tobera regimen a regimen; y
    —del modulo 3— la onda oblicua con su descomposicion, el diagrama
    theta-beta-M, el abanico de Prandtl-Meyer, nu(M), las reflexiones, el
    cruce de choques y los dos perfiles supersonicos con sus presiones; y
    —del modulo 4— las tres correcciones de compresibilidad, el cruce que
    define el Mach critico, la divergencia del arrastre, el ala en flecha,
    los perfiles transonicos, la regla del area y Ackeret contra la exacta.

    Todo es geometrico y determinista: mismo script, mismo render. Los
    localizadores (.punto_de, .fuente, .garganta, .centro_zona, .punto) se
    leen de la posicion actual, y los NUMEROS (.error, .razon, .mu, .a,
    .valor, .fraccion, .area) salen de la misma fuente que el dibujo.
    """

    def construct(self):
        registrar_fuentes()
        titulo = Text("Aerodinámica", font_size=28, color=COLOR_CALCULO)
        titulo.to_edge(UP, buff=0.22)
        self.add(titulo)

        # --- acto 1: el limite del modelo incompresible y el reparto ---
        curva = curva_compresibilidad(ancho=4.6, alto=2.0)
        curva.move_to(LEFT * 3.4 + DOWN * 0.6)
        self.play(FadeIn(curva.ejes), Create(curva.curva), run_time=0.9)
        self.play(FadeIn(curva.banda), FadeIn(curva.umbral),
                  FadeIn(curva.etiquetas), run_time=0.5)
        # Los marcadores que se cuelgan de una pieza se guardan SIEMPRE en un
        # grupo: al acabar el acto tienen que irse con ella, o la demo va
        # acumulando puntos sueltos sobre lo que venga despues.
        marcas = VGroup(Dot(curva.punto_de(0.8), radius=0.06,
                            color=COLOR_TRANSONICO))
        self.add(marcas)

        balanza = balanza_energias(0.3, alto=1.8, ancho=0.5, separacion=1.2)
        balanza.move_to(RIGHT * 3.2 + DOWN * 0.6)
        self.play(FadeIn(balanza), run_time=0.5)
        self.play(balanza.a_mach(3.0), run_time=0.7)
        self.wait(0.3)
        self.play(FadeOut(VGroup(curva, balanza, marcas)), run_time=0.4)

        # --- acto 2: los regimenes y la fuente movil ---
        banda = banda_regimenes(ancho=8.0, alto=0.55)
        banda.move_to(DOWN * 2.4)
        self.play(FadeIn(banda), run_time=0.5)
        marcas = VGroup(*[Dot(banda.punto_de(m, 0.30), radius=0.055,
                              color=banda.color_de(m))
                          for m in (0.2, 0.9, 2.0, 9.0)])
        self.add(marcas)

        ondas = frentes_moviles(0.0, n_ondas=4, paso=0.34)
        ondas.shift(RIGHT * 1.6 + UP * 0.4 - ondas.fuente())
        self.play(FadeIn(ondas), run_time=0.5)
        for m in (1.0, 2.4):
            nuevas = ondas.con_mach(m)
            self.play(ReplacementTransform(ondas, nuevas), run_time=0.6)
            ondas = nuevas
        mu = Text(f"mu = {ondas.mu():.1f}", font=FUENTE_HUD, font_size=16,
                  color=COLOR_SUPERSONICO)
        mu.move_to(ondas.fuente() + LEFT * 1.3 + UP * 1.35)
        self.play(FadeIn(mu), run_time=0.3)
        self.wait(0.3)
        self.play(FadeOut(VGroup(ondas, mu, banda, marcas)), run_time=0.4)

        # --- acto 3: termodinamica ---
        cilindro = piston_gas(1.0, largo=3.0, alto=1.5, n_particulas=34)
        cilindro.move_to(LEFT * 3.0 + UP * 0.2)
        self.play(FadeIn(cilindro), run_time=0.5)
        self.play(cilindro.a_fraccion(0.4), run_time=0.7)

        calores = barras_calores(ancho=4.4, alto=0.34, separacion=0.46,
                                 font_size=14)
        calores.move_to(RIGHT * 3.0 + UP * 0.4)
        self.play(FadeIn(calores), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(VGroup(cilindro, calores)), run_time=0.4)

        vc = volumen_control(ancho=2.6, alto=1.5, font_size=14)
        vc.move_to(LEFT * 3.2 + DOWN * 0.2)
        ts = diagrama_ts(ancho=3.4, alto=2.0, font_size=13)
        ts.move_to(RIGHT * 3.0 + DOWN * 0.2)
        self.play(FadeIn(vc), FadeIn(ts.ejes), run_time=0.6)
        caminos = VGroup(
            ts.trayecto([(0.2, 0.85), (0.2, 0.3)], color=COLOR_SUBSONICO),
            ts.trayecto([(0.2, 0.85), (0.5, 0.6), (0.7, 0.45)],
                        color=COLOR_SUPERSONICO, punteado=True))
        self.play(*[Create(c) for c in caminos], run_time=0.8)
        self.wait(0.3)
        self.play(FadeOut(VGroup(vc, ts, caminos)), run_time=0.4)

        # --- acto 4: la velocidad del sonido ---
        pulso = pulso_conducto(0.2, largo=5.0, alto=0.9, salto=0.34,
                               color_tubo=COLOR_EJE)
        pulso.move_to(UP * 1.3)
        self.play(FadeIn(pulso), run_time=0.5)
        self.play(pulso.a_avance(0.9), run_time=0.8)

        sonido = curva_sonido(ancho=3.0, alto=1.6, font_size=12)
        sonido.move_to(LEFT * 3.6 + DOWN * 1.4)
        isa_perfil = perfil_isa(ancho=2.4, alto=1.8, font_size=12)
        isa_perfil.move_to(DOWN * 1.4)
        mus = curva_mu(ancho=2.8, alto=1.6, font_size=12)
        mus.move_to(RIGHT * 3.6 + DOWN * 1.4)
        self.play(FadeIn(sonido), FadeIn(isa_perfil), FadeIn(mus),
                  run_time=0.7)
        marcas = VGroup(
            Dot(sonido.punto_de(288.15), radius=0.05, color=COLOR_TRANSONICO),
            Dot(isa_perfil.punto_de(11000.0), radius=0.05,
                color=COLOR_TRANSONICO),
            Dot(mus.punto_de(2.0), radius=0.05, color=COLOR_SUPERSONICO))
        self.add(marcas)
        self.wait(0.3)
        self.play(FadeOut(VGroup(pulso, sonido, isa_perfil, mus, marcas)),
                  run_time=0.4)

        # --- acto 5: el conducto y la entalpia total ---
        tubo = conducto("delaval", largo=5.0, alto=1.9, color=COLOR_EJE)
        tubo.move_to(LEFT * 1.6 + DOWN * 0.2)
        self.play(Create(tubo.paredes), FadeIn(tubo.eje), run_time=0.9)
        garganta = Line(tubo.punto_de(0.5, -1.0), tubo.punto_de(0.5, 1.0),
                        stroke_width=2.4, color=COLOR_SUPERSONICO)
        self.add(garganta)

        entalpia = barras_entalpia(0.0, alto=2.0, ancho=0.7, font_size=13)
        entalpia.move_to(RIGHT * 4.4 + DOWN * 0.2)
        self.play(FadeIn(entalpia), run_time=0.5)
        self.play(entalpia.a_mach(2.5), run_time=0.8)
        self.wait(0.3)
        self.play(FadeOut(VGroup(tubo, garganta, entalpia)), run_time=0.4)
        self.play(FadeOut(VGroup(tubo, garganta, entalpia)), run_time=0.4)

        # --- acto 6: estancamiento, razones isentropicas y la tabla ---
        flujo = remanso(radio=0.55, n_lineas=5, separacion=0.32, largo=2.0,
                        color=COLOR_TRANSONICO)
        flujo.move_to(LEFT * 4.3 + UP * 1.2)
        curvas = curvas_isentropicas(m_max=3.0, ancho=3.2, alto=1.8,
                                     font_size=12)
        curvas.move_to(RIGHT * 2.3 + UP * 1.2)
        self.play(FadeIn(flujo), FadeIn(curvas), run_time=0.8)
        marcas = VGroup(Dot(flujo.punto(), radius=0.06,
                            color=COLOR_SUPERSONICO),
                        *[Dot(curvas.punto_de(i, 1.0), radius=0.05,
                              color=curvas.color_de(i)) for i in range(3)],
                        curvas.vertical_en(1.0))
        self.add(marcas)

        tabla = tabla_isentropica(machs=(1.0, 2.0, 3.0), ancho_col=1.30,
                                  alto_fila=0.40, font_size=15)
        tabla.move_to(DOWN * 1.9)
        franja = tabla.resaltar(1)
        self.play(FadeIn(tabla), run_time=0.6)
        self.play(FadeIn(franja), run_time=0.4)
        self.wait(0.6)
        self.play(FadeOut(VGroup(flujo, curvas, marcas, tabla, franja)),
                  run_time=0.4)

        # --- acto 7: como nace un choque, y como se mide ---
        xt = diagrama_xt(n_ondas=5, ancho=3.0, alto=1.8, font_size=11)
        xt.move_to(LEFT * 4.4 + UP * 1.2)
        pc = perfil_choque(salto=4.5, ancho=3.0, alto=1.6, font_size=11,
                           etiqueta="200 nm")
        pc.move_to(LEFT * 0.6 + UP * 1.2)
        banco = esquema_schlieren(n_rayos=7, ancho=4.2, alto=1.5,
                                  font_size=10)
        banco.move_to(RIGHT * 4.2 + UP * 1.2)
        self.play(FadeIn(xt), FadeIn(pc), FadeIn(banco), run_time=0.9)
        marcas = VGroup(Dot(xt.coalescencia(), radius=0.05,
                            color=COLOR_SUPERSONICO), xt.choque)
        self.add(marcas)
        self.wait(0.3)

        saltos = curvas_choque(grupo="saltos", m_max=3.0, ancho=2.6,
                               alto=1.6, font_size=11, hueco_etiquetas=0.55)
        saltos.move_to(LEFT * 4.6 + DOWN * 1.6)
        anemo = curva_anemometro(ancho=2.4, alto=1.5, font_size=10)
        anemo.move_to(LEFT * 0.9 + DOWN * 1.6)
        velocidades = escalera_velocidades(ancho=2.4, alto=0.24,
                                           separacion=0.16, font_size=12)
        velocidades.move_to(RIGHT * 3.9 + DOWN * 1.5)
        self.play(FadeIn(saltos), FadeIn(anemo), FadeIn(velocidades),
                  run_time=0.9)
        self.wait(0.5)
        self.play(FadeOut(VGroup(xt, pc, banco, marcas, saltos, anemo,
                                 velocidades)), run_time=0.4)

        # --- acto 8: el area manda, y la tobera decide ---
        areas = curva_area_mach(ancho=3.0, alto=1.9, font_size=11)
        areas.move_to(LEFT * 4.2 + UP * 0.1)
        recta = areas.horizontal_en(1.6875)
        dobles = VGroup(*[Dot(areas.punto_de(areas.mach_de(1.6875, rama)),
                              radius=0.05,
                              color=COLOR_SUBSONICO if rama == "sub"
                              else COLOR_SUPERSONICO)
                          for rama in ("sub", "super")])
        self.play(FadeIn(areas), Create(recta), run_time=0.7)
        self.add(dobles)

        tobera = perfil_tobera(ancho=4.6, alto_tubo=1.2, alto_grafico=1.8,
                               hueco=0.35, font_size=11)
        tobera.move_to(RIGHT * 2.4)
        self.play(FadeIn(tobera.tubo), FadeIn(tobera.ejes), run_time=0.6)
        self.play(*[Create(tobera.curva(k)) for k, _e, _c in REGIMENES_TOBERA],
                  run_time=1.0)
        self.add(*[m for m in tobera.choques.values()])
        self.wait(0.8)

        self.play(FadeOut(VGroup(areas, recta, dobles, tobera)),
                  run_time=0.4)

        # --- acto 9: el aire de lado ---
        oblicua = onda_oblicua(2.0, 12.0, largo=1.9, entrada=1.4)
        oblicua.move_to(LEFT * 4.5 + UP * 1.15)
        mapa = diagrama_theta_beta(machs=(2.0, 3.0), ancho=2.6, alto=1.7,
                                   font_size=11)
        mapa.move_to(LEFT * 0.9 + UP * 1.15)
        fan = abanico_expansion(2.0, 15.0, n_lineas=6, largo=1.6,
                                entrada=1.2)
        fan.move_to(RIGHT * 3.8 + UP * 1.15)
        self.play(FadeIn(oblicua), FadeIn(mapa), FadeIn(fan), run_time=0.9)
        vertices = VGroup(*[Dot(mapa.punto_maximo(i), radius=0.05,
                                color=COLOR_SUPERSONICO) for i in range(2)])
        self.add(vertices)
        self.wait(0.4)

        rebote = reflexion_onda(tipo="libre", ancho=3.4, alto=1.4)
        rebote.move_to(LEFT * 4.3 + DOWN * 1.5)
        cruce = interseccion_choques(ancho=3.4, alto=1.4)
        cruce.move_to(LEFT * 0.5 + DOWN * 1.5)
        rombo = perfil_supersonico("rombo", 2.0, 8.0, cuerda=1.9,
                                   largo_onda=0.9)
        rombo.move_to(RIGHT * 3.9 + DOWN * 1.5)
        self.play(FadeIn(rebote), FadeIn(cruce), FadeIn(rombo), run_time=0.9)
        self.add(VGroup(*[rombo.barra_presion(c, escala=0.5)
                          for c in rombo.caras]))
        self.wait(0.8)

        self.play(FadeOut(VGroup(oblicua, mapa, fan, vertices, rebote, cruce,
                                 rombo)), run_time=0.4)

        # --- acto 10: corregir, y saber donde deja de valer ---
        correcciones = curvas_correcciones(ancho=2.9, alto=1.7, font_size=10,
                                           hueco_etiquetas=0.50)
        correcciones.move_to(LEFT * 4.3 + UP * 1.2)
        critico = curva_mach_critico(ancho=2.7, alto=1.7, font_size=10)
        critico.move_to(LEFT * 0.2 + UP * 1.2)
        arrastre = curva_arrastre_transonico(ancho=2.7, alto=1.7,
                                             font_size=10)
        arrastre.move_to(RIGHT * 4.0 + UP * 1.2)
        self.play(FadeIn(correcciones), FadeIn(critico), FadeIn(arrastre),
                  run_time=1.0)
        self.add(Dot(critico.punto_cruce(), radius=0.05,
                     color=COLOR_TRANSONICO))
        self.wait(0.4)

        # Cuatro piezas en la fila de abajo, repartidas para que ninguna
        # invada a su vecina ni se salga por la derecha.
        ala = ala_flecha(0.85, 35.0, envergadura=1.3, cuerda=0.7,
                         escala_v=0.9)
        ala.move_to(LEFT * 5.4 + DOWN * 1.7)
        perfiles = perfiles_transonicos(cuerda=1.5, alto_cp=0.45,
                                        separacion=0.60, escala_perfil=2.0,
                                        font_size=10)
        perfiles.move_to(LEFT * 2.1 + DOWN * 1.7)
        area = distribucion_area(ancho=2.0, alto=1.1, font_size=9)
        area.move_to(RIGHT * 1.6 + DOWN * 1.7)
        teorias = comparacion_teorias(ancho=1.9, alto=1.2, font_size=9,
                                      muestras=30)
        teorias.move_to(RIGHT * 5.2 + DOWN * 1.7)
        self.play(FadeIn(ala), FadeIn(perfiles), FadeIn(area),
                  FadeIn(teorias), run_time=1.0)
        self.wait(0.9)
