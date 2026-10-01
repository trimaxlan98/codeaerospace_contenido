"""Tema «Electrónica» (por materia). Fondo procedural: fondos_tematicos.electronica()."""
import fondos_tematicos  # noqa: F401  (registra los generadores de fondo por materia)
from temas_espaciales import Tema

TEMA = Tema(
    id="electronica", nombre="Electrónica", modo="oscuro", video="monitor", pantalla="#04120D", generador="electronica",
    descripcion="Circuito: verde de PCB casi negro, pistas a 45° en bus, pads de cobre, vías, chip QFP y serigrafía; el video va en un monitor con escuadras.",
    fuentes=dict(titulo="Saira Semi Condensed", display="Saira Semi Condensed", cuerpo="Inter", etiqueta="JetBrains Mono"),
    ancho_car=dict(titulo=0.44, cuerpo=0.53), k_titulo=1.14, portada_ancho=7.4, esquinas=True,
    color={'tinta': '#E8F5EE', 'tenue': '#7FA395', 'acento': '#34E5A0', 'acento2': '#F2B84B', 'calido': '#F2B84B', 'linea': '#34E5A0', 'panel': '#04120D'},
    manim={'FUENTE': 'Saira Semi Condensed', 'FUENTE_CIFRA': 'Saira Semi Condensed', 'PESO_CIFRA': 'BOLD', 'ESCALA_TEXTO': 1.0, 'FONDO': '#04120D', 'TINTA': '#E8F5EE', 'TENUE': '#7FA395', 'C_EJE': '#2A5443', 'C_TIERRA': '#2563EB', 'C_TIERRA_2': '#1E3A8A', 'C_SAT': '#F2B84B', 'C_ANT': '#34E5A0', 'C_CIELO': '#A78BFA', 'C_MAL': '#FF5A5F', 'C_OK': '#34E5A0', 'C_PANEL': '#0B2A1E'})
