"""Tema «Marte» (por materia). Fondo procedural: fondos_tematicos.marte()."""
import fondos_tematicos  # noqa: F401  (registra los generadores de fondo por materia)
from temas_espaciales import Tema

TEMA = Tema(
    id="marte", nombre="Marte", modo="oscuro", video="fundido", pantalla="#130A0C", generador="marte",
    descripcion="Cielo de polvo óxido con el atardecer azul de Marte, capas de dunas con luz rasante y estrellas arriba; acento óxido.",
    fuentes=dict(titulo="Teko", display="Teko", cuerpo="Rubik", etiqueta="Overpass Mono"),
    ancho_car=dict(titulo=0.42, cuerpo=0.52), k_titulo=1.2, portada_ancho=7.4,
    color={'tinta': '#FBEDE4', 'tenue': '#C09A88', 'acento': '#FF7043', 'acento2': '#7DD3FC', 'calido': '#FBBF24', 'linea': '#FF7043', 'panel': '#130A0C'},
    manim={'FUENTE': 'Teko', 'FUENTE_CIFRA': 'Teko', 'PESO_CIFRA': 'BOLD', 'ESCALA_TEXTO': 1.06, 'FONDO': '#130A0C', 'TINTA': '#FBEDE4', 'TENUE': '#C09A88', 'C_EJE': '#5A3A33', 'C_TIERRA': '#E2552E', 'C_TIERRA_2': '#8C2F17', 'C_SAT': '#FBBF24', 'C_ANT': '#7DD3FC', 'C_CIELO': '#C4A1FF', 'C_MAL': '#FF4D6D', 'C_OK': '#7EE2A8', 'C_PANEL': '#24130F'})
