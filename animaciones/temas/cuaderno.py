"""Tema «Cuaderno» (por materia). Fondo procedural: fondos_tematicos_2.cuaderno()."""
import fondos_tematicos_2  # noqa: F401  (registra los generadores de fondo de la segunda tanda)
from temas_espaciales import Tema

TEMA = Tema(
    id="cuaderno", nombre="Cuaderno", modo="claro", video="tarjeta", pantalla=None, generador="cuaderno",
    descripcion="Claro: cuaderno de ingeniería en papel milimétrico con bocetos a tinta (órbita Molniya, transferencia de Hohmann) y notas a mano.",
    fuentes=dict(titulo="Crimson Pro", display="Crimson Pro", cuerpo="Work Sans", etiqueta="IBM Plex Mono"),
    ancho_car=dict(titulo=0.45, cuerpo=0.56), k_titulo=1.12, portada_ancho=7.4,
    color={'tinta': '#1B2238', 'tenue': '#5B6478', 'acento': '#1E40AF', 'acento2': '#C2410C', 'calido': '#C2410C', 'linea': '#1E40AF', 'panel': '#FFFFFF'},
    manim={'FUENTE': 'Crimson Pro', 'FUENTE_CIFRA': 'Crimson Pro', 'PESO_CIFRA': 'BOLD', 'ESCALA_TEXTO': 0.98, 'FONDO': '#FFFFFF', 'TINTA': '#1B2238', 'TENUE': '#5B6478', 'C_EJE': '#B7C3D6', 'C_TIERRA': '#1E40AF', 'C_TIERRA_2': '#93B4F5', 'C_SAT': '#C2410C', 'C_ANT': '#0E7490', 'C_CIELO': '#6D28D9', 'C_MAL': '#DC2626', 'C_OK': '#059669', 'C_PANEL': '#EEF2F8'})
