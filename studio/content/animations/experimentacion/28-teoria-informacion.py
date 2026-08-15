import sys
sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *
from informacion import (B_TRANSPONDEDOR_HZ, DATOS_HAMMING, HITOS,
                         MENSAJE_HUFFMAN, MODCODS_DVBS2, N_BITS_CANAL,
                         P_BSC, POS_ERROR_HAMMING, SEMILLA_CANAL, SIMBOLOS,
                         TEXTO_ES, COLOR_BIT, COLOR_CODIGO,
                         COLOR_FUENTE, COLOR_LIMITE, COLOR_RUIDO,
                         arbol_huffman, bits_codificados, bits_imagen,
                         bits_para, bits_rle, capacidad_shannon,
                         cuantizar, curva_shannon_hartley, curva_sorpresa,
                         db_a_lineal, entropia_texto, esquema_bsc,
                         frecuencias, hamming_codificar, hamming_corregir,
                         hamming_sindrome, histograma_simbolos, huffman,
                         icono_bits, icono_fuente, imagen_bits,
                         imagen_esfera, imagen_gris, linea_tiempo,
                         plano_shannon, simular_bsc, sorpresa, tira_bits,
                         tira_codigo, venn_hamming, voltear)
from code_brand import FUENTE_HUD, registrar_fuentes


class DemoInformacion(Scene):
    """Demo de informacion.py: tres fuentes con `icono_fuente` (moneda,
    dado, baraja) y su sorpresa marcada sobre `curva_sorpresa` con
    `.en(p)` (`sorpresa(p)` = -log2 p); el histograma de los 27 simbolos
    del texto de muestra (`histograma_simbolos(frecuencias(TEXTO_ES))`)
    con la linea del uniforme (`.linea_uniforme()`) y la entropia MEDIDA
    (`entropia_texto`); el arbol de Huffman de "ABRACADABRA"
    (`arbol_huffman`, `.hojas`, `.paso(k)`) construido fusion a fusion
    junto a la tira codificada (`tira_codigo`, `bits_codificados`); un
    icono binario (`icono_bits`, `imagen_bits`) con sus bits por tramos
    (`bits_rle`) y una esfera en gris cuantizada
    (`imagen_esfera`, `cuantizar`, `imagen_gris`, `bits_imagen`); el canal
    binario simetrico (`esquema_bsc`) con una tira de 64 bits
    (`tira_bits`) pasada por `simular_bsc` y los volteados marcados y
    CONTADOS con `.marcar_distintos()`; la curva de Shannon-Hartley
    (`curva_shannon_hartley`, `.en(db)`) con los puntos de 10 y 20 dB
    (`capacidad_shannon`); el plano de Shannon (`plano_shannon`,
    `.marca(db, eta)`) con los MODCOD reales de DVB-S2
    (`MODCODS_DVBS2`); el diagrama de Hamming(7,4) (`venn_hamming`,
    `hamming_codificar`, `voltear`) con un bit volteado, su sindrome
    (`hamming_sindrome`) y la correccion (`hamming_corregir`,
    `.con_bits()`, `.colorear_paridad()`); y la linea de tiempo de los
    hitos (`linea_tiempo(HITOS)`).

    Todo el calculo es determinista (el unico azar, la tira de 64 bits
    del canal, va sembrado con `SEMILLA_CANAL`): mismo script, mismo
    render. Sin style_block: los colores salen de las constantes
    `COLOR_*` de `informacion.py`.
    """

    def construct(self):
        registrar_fuentes()
        titulo = Text("Teoría de la información: los bits de Shannon",
                      font_size=26, color=COLOR_BIT)
        titulo.to_edge(UP, buff=0.3)
        self.play(FadeIn(titulo), run_time=0.6)

        # --- acto 1: la sorpresa de tres fuentes ----------------------------
        moneda = icono_fuente("moneda", COLOR_FUENTE)
        dado = icono_fuente("dado", COLOR_FUENTE)
        baraja = icono_fuente("baraja", COLOR_FUENTE)
        fuentes = VGroup(moneda, dado, baraja).arrange(RIGHT, buff=1.1)
        fuentes.move_to(UP * 1.7)
        self.play(FadeIn(fuentes, shift=0.15 * UP), run_time=0.8)

        curva1 = curva_sorpresa()
        curva1.move_to(DOWN * 1.1)
        self.play(Create(curva1.ejes), FadeIn(curva1.ticks),
                  FadeIn(curva1.etiqueta_x), FadeIn(curva1.etiqueta_y),
                  run_time=0.6)
        self.play(Create(curva1.curva), run_time=1.1)
        puntos1 = VGroup(*[Dot(curva1.en(p), radius=0.06, color=COLOR_BIT)
                           for p in (0.5, 1 / 6, 1 / 52)])
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in puntos1],
                              lag_ratio=0.3), run_time=0.9)
        etq1 = Text(f"sorpresa(1/2)={sorpresa(0.5):.2f}  "
                    f"sorpresa(1/6)={sorpresa(1 / 6):.2f}  "
                    f"sorpresa(1/52)={sorpresa(1 / 52):.2f} bits",
                    font=FUENTE_HUD, font_size=14, color=COLOR_BIT)
        etq1.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etq1), run_time=0.4)
        self.wait(2.5)
        self.play(FadeOut(fuentes), FadeOut(curva1), FadeOut(puntos1),
                  FadeOut(etq1), run_time=0.6)

        # --- acto 2: el histograma medido del español ------------------------
        frecs = frecuencias(TEXTO_ES)
        hist = histograma_simbolos(frecs, COLOR_FUENTE, alto=2.2, ancho=9.5)
        hist.move_to(DOWN * 0.2)
        self.play(FadeIn(hist.linea_base), run_time=0.3)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in hist.barras],
                              lag_ratio=0.02), run_time=1.3)
        self.play(FadeIn(hist.etiquetas), run_time=0.4)
        linea_u = hist.linea_uniforme()
        self.play(Create(linea_u), run_time=0.6)
        h_es = entropia_texto(TEXTO_ES)
        etq2 = Text(f"entropia_texto(TEXTO_ES) = {h_es:.2f} bits/simbolo  "
                    f"(uniforme: {bits_para(len(SIMBOLOS)):.2f})",
                    font=FUENTE_HUD, font_size=14, color=COLOR_LIMITE)
        etq2.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etq2), run_time=0.4)
        self.wait(2.5)
        self.play(FadeOut(hist), FadeOut(linea_u), FadeOut(etq2),
                  run_time=0.6)

        # --- acto 3: Huffman construido en vivo -------------------------------
        frec_h = {s: f for s, f in frecuencias(MENSAJE_HUFFMAN).items()
                 if f > 0}
        codigo_h = huffman(frec_h)
        arbol = arbol_huffman(frec_h, ancho=5.5, alto=3.0)
        arbol.scale(0.85)
        arbol.move_to(LEFT * 2.6 + DOWN * 0.3)
        self.play(FadeIn(arbol.hojas, shift=0.1 * UP), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(arbol.paso(k))
                                for k in range(arbol.n_fusiones)],
                              lag_ratio=0.5), run_time=1.6)
        tira = tira_codigo(MENSAJE_HUFFMAN, codigo_h, ancho=5.0, alto=0.4)
        tira.move_to(RIGHT * 3.0 + DOWN * 0.3)
        self.play(LaggedStart(*[FadeIn(seg) for seg in tira.segmentos],
                              lag_ratio=0.06), run_time=1.0)
        etq3 = Text(f'huffman(frecuencias("{MENSAJE_HUFFMAN}")): '
                    f'{bits_codificados(MENSAJE_HUFFMAN, codigo_h)} bits',
                    font=FUENTE_HUD, font_size=14, color=COLOR_CODIGO)
        etq3.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etq3), run_time=0.4)
        self.wait(2.8)
        self.play(FadeOut(arbol), FadeOut(tira), FadeOut(etq3), run_time=0.6)

        # --- acto 4: el icono binario y la esfera cuantizada -------------------
        icono_m = icono_bits(24, 16)
        esfera_m = cuantizar(imagen_esfera(24, 16), 4)
        img_icono = imagen_bits(icono_m, COLOR_FUENTE, celda=0.15)
        img_icono.move_to(LEFT * 2.7)
        img_esfera = imagen_gris(esfera_m, celda=0.15)
        img_esfera.move_to(RIGHT * 2.7)
        self.play(FadeIn(img_icono), run_time=0.7)
        self.play(FadeIn(img_esfera), run_time=0.7)
        etq4 = Text(
            f"icono_bits(24,16): {bits_rle(icono_m.flatten())} bits (RLE)   "
            f"cuantizar(imagen_esfera(24,16), 4): "
            f"{bits_imagen(esfera_m, 2)} bits",
            font=FUENTE_HUD, font_size=13, color=COLOR_CODIGO)
        etq4.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etq4), run_time=0.4)
        self.wait(2.5)
        self.play(FadeOut(img_icono), FadeOut(img_esfera), FadeOut(etq4),
                  run_time=0.6)

        # --- acto 5: el canal con ruido -----------------------------------------
        bsc = esquema_bsc(P_BSC)
        bsc.scale(1.1)
        bsc.move_to(UP * 1.2)
        self.play(FadeIn(bsc), run_time=0.7)

        bits_env = np.random.default_rng(SEMILLA_CANAL).integers(
            0, 2, N_BITS_CANAL)
        recibidos, n_volteados = simular_bsc(bits_env, P_BSC, SEMILLA_CANAL)
        tira_env = tira_bits(bits_env, COLOR_FUENTE, celda=0.20, filas=2)
        tira_env.move_to(DOWN * 1.2)
        self.play(LaggedStart(*[FadeIn(c) for c in tira_env.celdas],
                              lag_ratio=0.01), run_time=1.2)
        tira_rec = tira_bits(recibidos, COLOR_FUENTE, celda=0.20, filas=2)
        tira_rec.move_to(tira_env.get_center())
        n_marcados = tira_rec.marcar_distintos(bits_env, COLOR_RUIDO)
        self.play(Transform(tira_env, tira_rec), run_time=1.0)
        etq5 = Text(f"simular_bsc(bits, p={P_BSC}, semilla={SEMILLA_CANAL}): "
                    f"{n_marcados} de {N_BITS_CANAL} bits volteados",
                    font=FUENTE_HUD, font_size=14, color=COLOR_RUIDO)
        etq5.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etq5), run_time=0.4)
        self.wait(2.5)
        assert n_marcados == n_volteados
        self.play(FadeOut(bsc), FadeOut(tira_env), FadeOut(etq5),
                  run_time=0.6)

        # --- acto 6: Shannon-Hartley, el techo del enlace -----------------------
        curva6 = curva_shannon_hartley()
        curva6.move_to(DOWN * 0.3)
        self.play(Create(curva6.ejes), FadeIn(curva6.ticks),
                  FadeIn(curva6.etiqueta_x), FadeIn(curva6.etiqueta_y),
                  run_time=0.6)
        self.play(Create(curva6.curva), run_time=1.1)
        p10 = Dot(curva6.en(10), radius=0.07, color=COLOR_CODIGO)
        p20 = Dot(curva6.en(20), radius=0.07, color=COLOR_RUIDO)
        self.play(FadeIn(p10, scale=0.6), run_time=0.4)
        self.play(FadeIn(p20, scale=0.6), run_time=0.4)
        c10 = capacidad_shannon(B_TRANSPONDEDOR_HZ, db_a_lineal(10)) / 1e6
        c20 = capacidad_shannon(B_TRANSPONDEDOR_HZ, db_a_lineal(20)) / 1e6
        etq6 = Text(f"capacidad_shannon(36 MHz, 10 dB) = {c10:.1f} Mb/s   "
                    f"capacidad_shannon(36 MHz, 20 dB) = {c20:.1f} Mb/s",
                    font=FUENTE_HUD, font_size=13, color=COLOR_LIMITE)
        etq6.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etq6), run_time=0.4)
        self.wait(2.5)
        self.play(FadeOut(curva6), FadeOut(p10), FadeOut(p20), FadeOut(etq6),
                  run_time=0.6)

        # --- acto 7: el plano de Shannon con DVB-S2 ------------------------------
        plano = plano_shannon()
        plano.move_to(DOWN * 0.3)
        self.play(Create(plano.ejes), FadeIn(plano.ticks),
                  FadeIn(plano.etiqueta_x), FadeIn(plano.etiqueta_y),
                  FadeIn(plano.prohibido), run_time=0.6)
        self.play(Create(plano.curva), run_time=1.1)
        puntos_dvb = VGroup(*[plano.marca(db, eta, COLOR_CODIGO)
                              for _nombre, eta, db in MODCODS_DVBS2])
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in puntos_dvb],
                              lag_ratio=0.2), run_time=1.0)
        etq7 = Text("MODCODS_DVBS2 (ETSI EN 302 307-1, cita): QPSK, 8PSK, "
                    "16APSK, 32APSK", font=FUENTE_HUD, font_size=13,
                    color=COLOR_CODIGO)
        etq7.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etq7), run_time=0.4)
        self.wait(2.5)
        self.play(FadeOut(plano), FadeOut(puntos_dvb), FadeOut(etq7),
                  run_time=0.6)

        # --- acto 8: Hamming(7,4) corrige un error --------------------------------
        palabra = hamming_codificar(DATOS_HAMMING)
        con_error = voltear(palabra, POS_ERROR_HAMMING)
        venn = venn_hamming(con_error)
        venn.scale(1.15)
        venn.move_to(ORIGIN)
        self.play(FadeIn(venn.circulos), FadeIn(venn.letras), run_time=0.6)
        self.play(FadeIn(venn.textos), run_time=0.6)
        venn.colorear_paridad()
        sindrome = hamming_sindrome(con_error)
        etq8 = Text(f"hamming_sindrome(palabra_con_error) = {sindrome}  "
                    f"->  bit {sindrome} volteado", font=FUENTE_HUD,
                    font_size=14, color=COLOR_RUIDO)
        etq8.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etq8), run_time=0.4)
        self.wait(1.2)

        corregida, pos = hamming_corregir(con_error)
        venn_ok = venn.con_bits(corregida)
        venn_ok.colorear_paridad()
        etq8b = Text(f"hamming_corregir(...): corregido en la posición "
                     f"{pos}", font=FUENTE_HUD, font_size=14,
                     color=COLOR_CODIGO)
        etq8b.move_to(etq8.get_center())
        self.play(Transform(venn, venn_ok), Transform(etq8, etq8b),
                  run_time=1.0)
        self.wait(1.8)
        self.play(FadeOut(venn), FadeOut(etq8), run_time=0.6)

        # --- acto 9: la línea de tiempo del cincuentenario -------------------------
        linea = linea_tiempo(HITOS, ancho=9.5)
        linea.move_to(DOWN * 0.1)
        self.play(Create(linea.linea), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(h, shift=0.15 * UP)
                                for h in linea.hitos], lag_ratio=0.15),
                  run_time=1.6)
        etq9 = Text("linea_tiempo(HITOS): del teorema de 1948 al techo de "
                    "hoy", font=FUENTE_HUD, font_size=14, color=COLOR_LIMITE)
        etq9.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(etq9), run_time=0.4)
        self.wait(2.6)
        self.play(FadeOut(linea), FadeOut(etq9), FadeOut(titulo),
                  run_time=0.6)
