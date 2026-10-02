"""Época visible y sello de rigor: toda pieza con datos orbitales muestra de cuándo son."""
from datetime import timezone

from .fuentes import EpocaCaducada


def sello(el, limite_dias=3.0, ahora=None):
    edad = el.edad_dias(ahora)
    caducado = edad > limite_dias
    return {"texto": f"Datos: CelesTrak/18 SDS · época {el.epoca.astimezone(timezone.utc):%Y-%m-%d %H:%M} UTC",
            "edad_dias": round(edad, 2), "caducado": caducado, "rigor": "simulacion" if caducado else "dato",
            "pie": "Predicción SGP4. Los elementos envejecen; verifica antes de salir."}


def exigir_vigente(el, limite_dias=3.0, ahora=None):
    """Lanza EpocaCaducada si una pieza «en vivo» se intenta armar con elementos demasiado viejos."""
    s = sello(el, limite_dias, ahora)
    if s["caducado"]:
        raise EpocaCaducada(f"{el.nombre}: elementos de hace {s['edad_dias']} días (límite {limite_dias})")
    return s


def atribucion():
    return "Datos orbitales: CelesTrak (18th Space Defense Squadron, US Space Force). Cálculo: SGP4. Co.De Aerospace"
