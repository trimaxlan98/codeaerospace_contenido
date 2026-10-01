"""Tema «Luna» (por materia). Fondo procedural: fondos_tematicos.lunar()."""
import fondos_tematicos  # noqa: F401  (registra los generadores de fondo por materia)
from temas_espaciales import Tema

TEMA = Tema(
    id="lunar", nombre="Luna", modo="oscuro", video="fundido", pantalla="#0A0B0F", generador="lunar",
    descripcion="Horizonte regolítico con cráteres y la Tierra saliendo sobre un cielo negro; gris neutro con acento azul hielo.",
    fuentes=dict(titulo="Outfit", display="Outfit", cuerpo="Outfit", etiqueta="IBM Plex Mono"),
    ancho_car=dict(titulo=0.48, cuerpo=0.5), k_titulo=1.04, portada_ancho=7.4,
    color={'tinta': '#F2F4F7', 'tenue': '#9BA3AF', 'acento': '#8FD3FF', 'acento2': '#E5E7EB', 'calido': '#FBD38D', 'linea': '#8FD3FF', 'panel': '#0A0B0F'},
    manim={'FUENTE': 'Outfit', 'FUENTE_CIFRA': 'Outfit', 'PESO_CIFRA': 'BOLD', 'ESCALA_TEXTO': 0.91, 'FONDO': '#0A0B0F', 'TINTA': '#F2F4F7', 'TENUE': '#9BA3AF', 'C_EJE': '#3A3F4A', 'C_TIERRA': '#3B82C4', 'C_TIERRA_2': '#1E4E8C', 'C_SAT': '#FBD38D', 'C_ANT': '#8FD3FF', 'C_CIELO': '#B9A7F0', 'C_MAL': '#FF7A7A', 'C_OK': '#8EE3B0', 'C_PANEL': '#171A21'})
