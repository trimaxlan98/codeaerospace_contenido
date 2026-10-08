"""Datos y línea de tiempo de la serie de reels «Inteligencia artificial» (41-reels-ia.py). Tema: Neuronal, fondo vertical propio.

Divulgación de las ideas de base de la IA (neurona artificial, aprender bajando el error, palabras como vectores, atención,
predecir la siguiente palabra, sobreajuste, sesgo, alucinaciones) y un caso espacial real (Φ-sat-1 de la ESA).
Regla del dueño (2026-10-07): pocas cifras, todas traducidas a comparaciones cotidianas. Todo lo numérico de los diagramas es
ILUSTRATIVO (chip «Ilustración»): pesos, curvas y probabilidades se construyen a mano y con semilla.
NADA de aprendizaje por refuerzo multiagente ni de redes NTN (tema de la tesis doctoral). Sin clientes.
"""
import numpy as np

import divulgacion_fisica as F

# Hechos con fuente pública
NUBES_FRACCION = 2 / 3          # ~67 % de la Tierra cubierta de nubes en promedio (NASA Earth Observatory, MODIS)
PHISAT_ANIO = 2020              # Φ-sat-1 (ESA): lanzado el 3-sep-2020; IA a bordo que descarta imágenes nubladas
# (ESA, «Φ-sat-1 reveals first Earth images using on-board AI», 2020)

# Neurona de ejemplo (ilustración): tres entradas con sus pesos y un sesgo
NEURONA_X = (0.9, 0.2, 0.7)
NEURONA_W = (0.8, -0.6, 0.5)
NEURONA_B = -0.3


def neurona():
    z = float(np.dot(NEURONA_X, NEURONA_W) + NEURONA_B)
    return z, 1 / (1 + np.exp(-4 * z))


# Colina del error (descenso por gradiente): curva con un mínimo local y uno global
def error(x):
    x = np.asarray(x, float)
    return 0.18 * x ** 4 - 0.9 * x ** 2 + 0.35 * x + 1.6


def derivada(x):
    return 0.72 * x ** 3 - 1.8 * x + 0.35


def descenso(x0=2.35, paso=0.09, n=40):
    xs = [x0]
    for _ in range(n):
        xs.append(xs[-1] - paso * derivada(xs[-1]))
    return np.array(xs)


# Siguiente palabra (ilustración)
FRASE_SIG = "El satélite gira alrededor de la"
OPCIONES_SIG = [("Tierra", 0.71), ("Luna", 0.14), ("órbita", 0.08), ("estrella", 0.04), ("pizza", 0.01)]

CUERPO = {"ReelIaNeurona": 20.0, "ReelIaAprende": 20.0, "ReelIaPalabras": 20.0, "ReelIaAtencion": 20.0, "ReelIaSiguiente": 20.0,
          "ReelIaPixeles": 19.0, "ReelIaMemoriza": 20.0, "ReelIaSesgo": 20.0, "ReelIaInventa": 20.0, "ReelIaEspacio": 21.0}
LEYENDAS = {"ReelIaNeurona": (0.0, 6.0, 12.5), "ReelIaAprende": (0.0, 5.5, 12.0), "ReelIaPalabras": (0.0, 6.0, 12.5),
            "ReelIaAtencion": (0.0, 6.0, 12.5), "ReelIaSiguiente": (0.0, 6.0, 12.5), "ReelIaPixeles": (0.0, 5.5, 11.5),
            "ReelIaMemoriza": (0.0, 6.0, 12.5), "ReelIaSesgo": (0.0, 6.0, 12.5), "ReelIaInventa": (0.0, 6.0, 12.5),
            "ReelIaEspacio": (0.0, 6.5, 13.0)}
H0 = F.H0


def duracion(nombre):
    return F.duracion_total(CUERPO[nombre])
