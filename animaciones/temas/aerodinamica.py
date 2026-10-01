"""Tema «Aerodinámica» (por materia). Fondo procedural: fondos_tematicos_2.aerodinamica()."""
import fondos_tematicos_2  # noqa: F401  (registra los generadores de fondo de la segunda tanda)
from temas_espaciales import Tema

TEMA = Tema(
    id="aerodinamica", nombre="Aerodinámica", modo="oscuro", video="fundido", pantalla="#06101A", generador="aerodinamica",
    descripcion="Flujo potencial sobre un perfil de Joukowski (condición de Kutta) y cono de Mach con su ángulo; azul hielo sobre acero.",
    fuentes=dict(titulo="Tomorrow", display="Tomorrow", cuerpo="IBM Plex Sans", etiqueta="IBM Plex Mono"),
    ancho_car=dict(titulo=0.56, cuerpo=0.51), k_titulo=0.9, portada_ancho=7.4,
    color={'tinta': '#EAF6FF', 'tenue': '#86A3BA', 'acento': '#38BDF8', 'acento2': '#BAE6FD', 'calido': '#FBBF24', 'linea': '#38BDF8', 'panel': '#06101A'},
    manim={'FUENTE': 'Tomorrow', 'FUENTE_CIFRA': 'Tomorrow', 'PESO_CIFRA': 'BOLD', 'ESCALA_TEXTO': 0.83, 'FONDO': '#06101A', 'TINTA': '#EAF6FF', 'TENUE': '#86A3BA', 'C_EJE': '#22405A', 'C_TIERRA': '#2563EB', 'C_TIERRA_2': '#1E3A8A', 'C_SAT': '#FBBF24', 'C_ANT': '#38BDF8', 'C_CIELO': '#A5B4FC', 'C_MAL': '#FB7185', 'C_OK': '#34D399', 'C_PANEL': '#0E2233'})
