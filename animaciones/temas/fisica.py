"""Tema «Física» (por materia). Fondo procedural: fondos_tematicos.fisica()."""
import fondos_tematicos  # noqa: F401  (registra los generadores de fondo por materia)
from temas_espaciales import Tema

TEMA = Tema(
    id="fisica", nombre="Física", modo="oscuro", video="fundido", pantalla="#06060F", generador="fisica",
    descripcion="Espacio-tiempo: rejilla curvada por masas, agujero negro con disco de acreción y lente gravitacional, trazas de partículas; violeta y oro.",
    fuentes=dict(titulo="Titillium Web", display="Titillium Web", cuerpo="Work Sans", etiqueta="Space Mono"),
    ancho_car=dict(titulo=0.46, cuerpo=0.56), k_titulo=1.1, portada_ancho=7.4,
    color={'tinta': '#F0F0FA', 'tenue': '#9A9AC0', 'acento': '#8B8CFF', 'acento2': '#22D3EE', 'calido': '#FDE68A', 'linea': '#8B8CFF', 'panel': '#06060F'},
    manim={'FUENTE': 'Titillium Web', 'FUENTE_CIFRA': 'Titillium Web', 'PESO_CIFRA': 'BOLD', 'ESCALA_TEXTO': 0.96, 'FONDO': '#06060F', 'TINTA': '#F0F0FA', 'TENUE': '#9A9AC0', 'C_EJE': '#34345E', 'C_TIERRA': '#4F5BD5', 'C_TIERRA_2': '#262A7A', 'C_SAT': '#FDE68A', 'C_ANT': '#22D3EE', 'C_CIELO': '#C4B5FD', 'C_MAL': '#FF6B8B', 'C_OK': '#6EE7B7', 'C_PANEL': '#14142E'})
