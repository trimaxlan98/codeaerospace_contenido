"""Tema «Cálculo» (por materia). Fondo procedural: fondos_tematicos.calculo()."""
import fondos_tematicos  # noqa: F401  (registra los generadores de fondo por materia)
from temas_espaciales import Tema

TEMA = Tema(
    id="calculo", nombre="Cálculo", modo="oscuro", video="fundido", pantalla="#080C1B", generador="calculo",
    descripcion="Medianoche con curvas de nivel de un paisaje, ejes, derivada con tangente y secante, sumas de Riemann; tiza cálida y ámbar, títulos serif.",
    fuentes=dict(titulo="Fraunces", display="Fraunces", cuerpo="Source Sans 3", etiqueta="IBM Plex Mono"),
    ancho_car=dict(titulo=0.53, cuerpo=0.47), k_titulo=0.95, portada_ancho=7.4,
    color={'tinta': '#F3EFE6', 'tenue': '#9AA3C0', 'acento': '#FBBF24', 'acento2': '#A5B4FC', 'calido': '#FB923C', 'linea': '#FBBF24', 'panel': '#080C1B'},
    manim={'FUENTE': 'Fraunces', 'FUENTE_CIFRA': 'Fraunces', 'PESO_CIFRA': 'BOLD', 'ESCALA_TEXTO': 0.86, 'FONDO': '#080C1B', 'TINTA': '#F3EFE6', 'TENUE': '#9AA3C0', 'C_EJE': '#3A4370', 'C_TIERRA': '#6366F1', 'C_TIERRA_2': '#312E81', 'C_SAT': '#FBBF24', 'C_ANT': '#A5B4FC', 'C_CIELO': '#C084FC', 'C_MAL': '#FB7185', 'C_OK': '#86EFAC', 'C_PANEL': '#151C3A'})
