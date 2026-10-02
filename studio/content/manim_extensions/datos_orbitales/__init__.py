"""Datos orbitales reales para el estudio de contenido (ver ronda2_datos_reales.md)."""
from .doppler import C_KM_S, curva_doppler
from .fuentes import Elementos, EpocaCaducada, cargar, congelar, obtener
from .observador import CDMX, Observador, Pase, pases, sol_elevacion, topocentrico, trayectoria
from .propagacion import posicion_geodetica
from .sello import atribucion, exigir_vigente, sello
from .traza import huella_radio_km, traza_terrestre
