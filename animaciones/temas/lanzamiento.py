"""Tema «Lanzamiento» (por materia). Fondo procedural: fondos_tematicos.lanzamiento()."""
import fondos_tematicos  # noqa: F401  (registra los generadores de fondo por materia)
from temas_espaciales import Tema

TEMA = Tema(
    id="lanzamiento", nombre="Lanzamiento", modo="oscuro", video="monitor", pantalla="#07080D", generador="lanzamiento",
    descripcion="Ascenso a órbita: bandas de atmósfera, estela con penacho, escalera de altitud y eventos (MAX-Q, MECO, SEP); monitor con escuadras.",
    fuentes=dict(titulo="Barlow Condensed", display="Barlow Condensed", cuerpo="Manrope", etiqueta="IBM Plex Mono"),
    ancho_car=dict(titulo=0.39, cuerpo=0.51), k_titulo=1.25, portada_ancho=7.4, esquinas=True,
    color={'tinta': '#F5F6FA', 'tenue': '#9499AD', 'acento': '#FF8A3D', 'acento2': '#7DD3FC', 'calido': '#FFD166', 'linea': '#FF8A3D', 'panel': '#07080D'},
    manim={'FUENTE': 'Barlow Condensed', 'FUENTE_CIFRA': 'Barlow Condensed', 'PESO_CIFRA': 'BOLD', 'ESCALA_TEXTO': 1.1, 'FONDO': '#07080D', 'TINTA': '#F5F6FA', 'TENUE': '#9499AD', 'C_EJE': '#33384A', 'C_TIERRA': '#3B82F6', 'C_TIERRA_2': '#1E3A8A', 'C_SAT': '#FF8A3D', 'C_ANT': '#7DD3FC', 'C_CIELO': '#A78BFA', 'C_MAL': '#FF4D5E', 'C_OK': '#4ADE80', 'C_PANEL': '#14171F'})
