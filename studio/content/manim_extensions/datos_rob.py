"""Datos y línea de tiempo de la serie de reels «Robótica» (42-reels-robotica.py). Tema: Robótica, fondo vertical propio.

Fuente: ros2-workspace (Estación ATP / rover planetario, ROS 2 Jazzy), commit 498eb6f; todo SIMULADO (chip en pantalla), ninguna cifra
medida con hardware. Documentos: docs/ROVER.md (R1–R10), docs/ROS2_CONTROL.md, docs/HARDWARE.md, docs/CONTRATO.md.
Regla del dueño (2026-10-07): ciencia de base en lenguaje llano, pocas cifras y cada una con una comparación cotidiana; lo técnico va al ⚠️.
NADA de NTN/RL/compuertas (tesis). Sin clientes.
"""
import numpy as np

import divulgacion_fisica as F

# ── R1 (docs/ROVER.md «Resultados R1»): 1 m/s mandado, 10 s → distancia ideal 10 m (rover de 150 kg, ruedas de 0.25 m) ─────────
MUNDOS = [("Luna", 8.45, 1.62), ("Marte", 8.69, 3.71), ("Tierra", 7.81, 9.80665), ("Titán", 7.03, 1.352), ("Ceres", 4.04, 0.27)]   # nombre, m, g
DISTANCIA_IDEAL = 10.0
# ── R6 §1: reparto de carga en llano 1/6 por rueda (92.75 N en Marte = m·g/6) y escalón máximo por cuerpo (m) ────────────────────
ESCALON_MAX = {"Luna": 0.20, "Marte": 0.15, "Tierra": 0.10}
# ── R2 (seguridad): alarma de vuelco > 35°, de pendiente > 25°; planificador A*: pendiente ≥ 20° o rugosidad ≥ 0.15 m intransitable ──
ALARMA_VUELCO_DEG, ALARMA_PENDIENTE_DEG, INTRANSITABLE_DEG = 35, 25, 20
# ── R8 (operación con retardo): distancia útil por sol en Marte, llano, ventanas reales del orbitador (m), con IC95 muy anchos ──────
OPERACION_MARTE = {"teleoperado": 9, "por metas": 80, "plan de sol": 2040}
SIN_ALARMAS_MARTE = 312                    # el mismo plan de sol sin alarmas locales (m/sol)
TELEOP_MITAD_LUZ_S = 17                    # s de luz de una vía en que la teleoperación rinde la mitad (retardo constante)
LUNA_IDA_VUELTA_S = 2.6
# ── R10 (validación fuera de muestra, 150 casos nuevos): llegada a la meta ────────────────────────────────────────────────────
VAL_BASICA, VAL_COMPLETA, VAL_R10 = 141, 103, 140        # de 150
VAL_EN_AJUSTE = (52, 50)                                  # básica vs completa en el conjunto donde se afinó (de 60): 87 % vs 83 %
# ── R9: con y sin ROS, mismos bytes de telemetría en todos los casos probados (docs/ROVER.md «Resultados R9») ─────────────────────
# ── ros2_control (docs/ROS2_CONTROL.md): el mismo controlador mueve montura simulada, Gazebo o real cambiando el plugin de hardware ─


def por_100(n, de=150):
    return int(round(100 * n / de))


# Rocker-bogie: geometría ilustrativa (lado), unidades de escena
BASE_RUEDAS = (-2.6, 0.0, 2.6)                  # x relativo de rueda trasera, media y delantera
RADIO_RUEDA = 0.5


def terreno_bogie(x):
    """Altura del suelo para el reel del rocker-bogie: llano con una roca grande y un escalón."""
    x = np.asarray(x, float)
    roca = 1.05 * np.exp(-((x - 0.0) / 0.9) ** 2)
    return np.where(x > 6.0, 0.55, 0.0) + roca * (x < 3.5)


CUERPO = {"ReelRobBogie": 20.0, "ReelRobPatina": 19.0, "ReelRobMundos": 20.0, "ReelRobRuta": 20.0, "ReelRobAlarmas": 20.0,
          "ReelRobRetardo": 20.0, "ReelRobAutonomo": 20.0, "ReelRobValidacion": 21.0, "ReelRobROS": 21.0, "ReelRobCerebro": 21.0}
LEYENDAS = {"ReelRobBogie": (0.0, 6.0, 12.5), "ReelRobPatina": (0.0, 5.5, 11.5), "ReelRobMundos": (0.0, 5.5, 12.0),
            "ReelRobRuta": (0.0, 5.5, 12.0), "ReelRobAlarmas": (0.0, 6.0, 12.5), "ReelRobRetardo": (0.0, 6.0, 12.5),
            "ReelRobAutonomo": (0.0, 6.0, 12.5), "ReelRobValidacion": (0.0, 6.0, 13.0), "ReelRobROS": (0.0, 6.5, 13.0),
            "ReelRobCerebro": (0.0, 6.5, 13.5)}
H0 = F.H0


def duracion(nombre):
    return F.duracion_total(CUERPO[nombre])
