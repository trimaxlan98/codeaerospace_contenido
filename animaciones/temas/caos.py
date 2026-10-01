"""Tema «Caos» (por materia). Fondo procedural: fondos_tematicos_2.caos()."""
import fondos_tematicos_2  # noqa: F401  (registra los generadores de fondo de la segunda tanda)
from temas_espaciales import Tema

TEMA = Tema(
    id="caos", nombre="Caos", modo="oscuro", video="fundido", pantalla="#07060A", generador="caos",
    descripcion="Atractor de Lorenz con color por tiempo y diagrama de bifurcación del mapa logístico; ámbar, rosa y violeta, títulos serif.",
    fuentes=dict(titulo="Newsreader", display="Newsreader", cuerpo="Source Sans 3", etiqueta="IBM Plex Mono"),
    ancho_car=dict(titulo=0.48, cuerpo=0.47), k_titulo=1.04, portada_ancho=7.4,
    color={'tinta': '#F7EFE9', 'tenue': '#B3A1A8', 'acento': '#FBBF24', 'acento2': '#FB7185', 'calido': '#FB923C', 'linea': '#FBBF24', 'panel': '#07060A'},
    manim={'FUENTE': 'Newsreader', 'FUENTE_CIFRA': 'Newsreader', 'PESO_CIFRA': 'BOLD', 'ESCALA_TEXTO': 0.92, 'FONDO': '#07060A', 'TINTA': '#F7EFE9', 'TENUE': '#B3A1A8', 'C_EJE': '#3B2A33', 'C_TIERRA': '#A78BFA', 'C_TIERRA_2': '#4C1D95', 'C_SAT': '#FBBF24', 'C_ANT': '#FB7185', 'C_CIELO': '#C4B5FD', 'C_MAL': '#F43F5E', 'C_OK': '#86EFAC', 'C_PANEL': '#1A1218'})
