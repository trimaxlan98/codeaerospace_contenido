"""Tema «Electromagnetismo» (por materia). Fondo procedural: fondos_tematicos.electromagnetismo()."""
import fondos_tematicos  # noqa: F401  (registra los generadores de fondo por materia)
from temas_espaciales import Tema

TEMA = Tema(
    id="electromagnetismo", nombre="Electromagnetismo", modo="oscuro", video="tarjeta", pantalla="#0A1124", generador="electromagnetismo",
    descripcion="Campo de un dipolo (líneas E en magenta, equipotenciales azules), cargas brillantes y onda EM con E y B perpendiculares.",
    fuentes=dict(titulo="Jura", display="Jura", cuerpo="Figtree", etiqueta="Overpass Mono"),
    ancho_car=dict(titulo=0.56, cuerpo=0.5), k_titulo=0.9, portada_ancho=7.4,
    color={'tinta': '#EAF1FF', 'tenue': '#8CA0C8', 'acento': '#3B9CFF', 'acento2': '#FF4D7A', 'calido': '#FFC857', 'linea': '#3B9CFF', 'panel': '#0A1124'},
    manim={'FUENTE': 'Jura Medium', 'FUENTE_CIFRA': 'Jura', 'PESO_CIFRA': 'BOLD', 'ESCALA_TEXTO': 0.83, 'FONDO': '#0A1124', 'TINTA': '#EAF1FF', 'TENUE': '#8CA0C8', 'C_EJE': '#2A3B62', 'C_TIERRA': '#3B9CFF', 'C_TIERRA_2': '#1D4E89', 'C_SAT': '#FFC857', 'C_ANT': '#3B9CFF', 'C_CIELO': '#B28DFF', 'C_MAL': '#FF4D7A', 'C_OK': '#3DDC97', 'C_PANEL': '#121C38'})
