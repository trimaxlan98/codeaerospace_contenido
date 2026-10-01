"""Tema «Neuronal» (por materia). Fondo procedural: fondos_tematicos_2.neuronal()."""
import fondos_tematicos_2  # noqa: F401  (registra los generadores de fondo de la segunda tanda)
from temas_espaciales import Tema

TEMA = Tema(
    id="neuronal", nombre="Neuronal", modo="oscuro", video="tarjeta", pantalla="#120C24", generador="neuronal",
    descripcion="Inteligencia artificial: red neuronal con pesos positivos y negativos, pulsos de activación y matriz de atención; violeta y turquesa.",
    fuentes=dict(titulo="Urbanist", display="Urbanist", cuerpo="Inter", etiqueta="Overpass Mono"),
    ancho_car=dict(titulo=0.48, cuerpo=0.54), k_titulo=1.05, portada_ancho=7.4,
    color={'tinta': '#F3EEFF', 'tenue': '#A69CC7', 'acento': '#C084FC', 'acento2': '#2DD4BF', 'calido': '#F9A8D4', 'linea': '#C084FC', 'panel': '#120C24'},
    manim={'FUENTE': 'Urbanist', 'FUENTE_CIFRA': 'Urbanist', 'PESO_CIFRA': 'BOLD', 'ESCALA_TEXTO': 0.92, 'FONDO': '#120C24', 'TINTA': '#F3EEFF', 'TENUE': '#A69CC7', 'C_EJE': '#3A2F5E', 'C_TIERRA': '#7C5CE0', 'C_TIERRA_2': '#3B2A8F', 'C_SAT': '#F9A8D4', 'C_ANT': '#2DD4BF', 'C_CIELO': '#C084FC', 'C_MAL': '#FB7185', 'C_OK': '#5EEAD4', 'C_PANEL': '#1E1438'})
