"""Tema «Robótica» (por materia). Fondo procedural: fondos_tematicos.robotica()."""
import fondos_tematicos  # noqa: F401  (registra los generadores de fondo por materia)
from temas_espaciales import Tema

TEMA = Tema(
    id="robotica", nombre="Robótica", modo="oscuro", video="tarjeta", pantalla="#111820", generador="robotica",
    descripcion="Taller robótico: grafito con metal cepillado, panal hexagonal, brazo articulado con cotas y engranes; acento naranja de seguridad.",
    fuentes=dict(titulo="Oxanium", display="Oxanium", cuerpo="Barlow", etiqueta="JetBrains Mono"),
    ancho_car=dict(titulo=0.51, cuerpo=0.48), k_titulo=0.99, portada_ancho=7.6,
    color={'tinta': '#EEF2F6', 'tenue': '#8A99AB', 'acento': '#FF7A1A', 'acento2': '#7DD3FC', 'calido': '#FACC15', 'linea': '#FF7A1A', 'panel': '#111820'},
    manim={'FUENTE': 'Oxanium', 'FUENTE_CIFRA': 'Oxanium', 'PESO_CIFRA': 'BOLD', 'ESCALA_TEXTO': 0.87, 'FONDO': '#111820', 'TINTA': '#EEF2F6', 'TENUE': '#8A99AB', 'C_EJE': '#33455A', 'C_TIERRA': '#3B82F6', 'C_TIERRA_2': '#1E3A8A', 'C_SAT': '#FF7A1A', 'C_ANT': '#7DD3FC', 'C_CIELO': '#A78BFA', 'C_MAL': '#FF4D5E', 'C_OK': '#34D399', 'C_PANEL': '#1A2430'})
