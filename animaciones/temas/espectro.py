"""Tema «Espectro» (por materia). Fondo procedural: fondos_tematicos_2.espectro()."""
import fondos_tematicos_2  # noqa: F401  (registra los generadores de fondo de la segunda tanda)
from temas_espaciales import Tema

TEMA = Tema(
    id="espectro", nombre="Espectro", modo="oscuro", video="monitor", pantalla="#050A0F", generador="espectro",
    descripcion="SDR: cascada de frecuencias con portadoras, ráfagas y la curva Doppler de un pase, trazo del espectro en dBm; monitor con escuadras.",
    fuentes=dict(titulo="Red Hat Display", display="Red Hat Display", cuerpo="Red Hat Text", etiqueta="JetBrains Mono"),
    ancho_car=dict(titulo=0.49, cuerpo=0.5), k_titulo=1.03, portada_ancho=7.4, esquinas=True,
    color={'tinta': '#E6F4F1', 'tenue': '#7E9AA6', 'acento': '#22D3EE', 'acento2': '#FDE047', 'calido': '#FDE047', 'linea': '#22D3EE', 'panel': '#050A0F'},
    manim={'FUENTE': 'Red Hat Display', 'FUENTE_CIFRA': 'Red Hat Display', 'PESO_CIFRA': 'BOLD', 'ESCALA_TEXTO': 0.91, 'FONDO': '#050A0F', 'TINTA': '#E6F4F1', 'TENUE': '#7E9AA6', 'C_EJE': '#23404F', 'C_TIERRA': '#1D5C7A', 'C_TIERRA_2': '#13234A', 'C_SAT': '#FDE047', 'C_ANT': '#22D3EE', 'C_CIELO': '#73D055', 'C_MAL': '#FF5D73', 'C_OK': '#73D055', 'C_PANEL': '#0D1B26'})
