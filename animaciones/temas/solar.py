"""Tema «Solar» (por materia). Fondo procedural: fondos_tematicos_2.solar()."""
import fondos_tematicos_2  # noqa: F401  (registra los generadores de fondo de la segunda tanda)
from temas_espaciales import Tema

TEMA = Tema(
    id="solar", nombre="Solar", modo="oscuro", video="fundido", pantalla="#0C0503", generador="solar",
    descripcion="Heliofísica: limbo del Sol con granulación y oscurecimiento al borde, corona y protuberancias en arco; naranja y oro.",
    fuentes=dict(titulo="Lexend", display="Lexend", cuerpo="Lexend", etiqueta="Space Mono"),
    ancho_car=dict(titulo=0.55, cuerpo=0.55), k_titulo=0.91, portada_ancho=7.4,
    color={'tinta': '#FFF4EA', 'tenue': '#C4A28E', 'acento': '#FB923C', 'acento2': '#FDE68A', 'calido': '#FDE68A', 'linea': '#FB923C', 'panel': '#0C0503'},
    manim={'FUENTE': 'Lexend', 'FUENTE_CIFRA': 'Lexend', 'PESO_CIFRA': 'BOLD', 'ESCALA_TEXTO': 0.84, 'FONDO': '#0C0503', 'TINTA': '#FFF4EA', 'TENUE': '#C4A28E', 'C_EJE': '#4A2A1D', 'C_TIERRA': '#3B82F6', 'C_TIERRA_2': '#1E3A8A', 'C_SAT': '#FDE68A', 'C_ANT': '#FB923C', 'C_CIELO': '#F9A8D4', 'C_MAL': '#EF4444', 'C_OK': '#86EFAC', 'C_PANEL': '#21110A'})
