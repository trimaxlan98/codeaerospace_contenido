#!/usr/bin/env python3
"""Genera specs de carruseles a partir de DATOS ORBITALES REALES (datos_orbitales) y los escribe en
specs/datos-reales/. Cada spec lleva la época de los elementos, la fuente con fecha y los avisos de rigor.

    python3 generar_desde_datos.py            # doppler-iss
Luego:  python3 motor_carrusel.py specs/datos-reales/doppler-iss.json
"""
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "studio/content/manim_extensions"))
from datos_orbitales.ejemplos import pase_estrella  # noqa: E402

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def fecha_larga(d):
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]} de {d.year}"


def doppler_iss():
    e = pase_estrella()
    p, d, el, obs = e["pase"], e["doppler"], e["el"], e["obs"].publicable()
    f0_mhz = e["f0"] / 1e6
    epoca = el.epoca.strftime("%Y-%m-%d %H:%M UTC")
    dur = int(round(p.duracion_s))
    hora = f"{e['aos_local']:%H:%M}–{e['los_local']:%H:%M}"
    pico, pend = e["df_pico_khz"], e["pendiente_hz_s"]
    x = [round(float(v), 1) for v in d["t"]]
    y = [round(float(v), 1) for v in d["df"]]
    tc = d["t_cruce"]
    spec = {
        "id": "doppler-real-iss", "serie": "datos-reales",
        "fondo": {"tema": "espectro", "tipo": "contenido", "var": 1, "atenuar": 0.38},
        "laminas": [
            {"tipo": "portada", "kicker": "Datos reales · ISS", "titulo": "La curva en S, calculada con un pase real",
             "subtitulo": f"La Estación Espacial sobre Ciudad de México, {fecha_larga(e['aos_local'])}"},
            {"tipo": "texto", "numero": "01", "titulo": "Qué calculamos", "sello": "dato",
             "cuerpo": f"Tomamos los elementos orbitales de la ISS que publica [[CelesTrak]] (época {epoca}) y propagamos su órbita con **SGP4** para un observador en Ciudad de México."},
            {"tipo": "grafica", "kicker": "El pase más alto de tres días", "titulo": "Cuánto cambia la frecuencia durante el pase",
             "x": x, "y": y, "y_escala": 1000, "y_etiqueta": f"CAMBIO DE FRECUENCIA (kHz) · FRECUENCIA DE EJEMPLO {f0_mhz:.0f} MHz",
             "x_etiqueta": "Tiempo desde que sale sobre el horizonte útil (min:s)", "x_modo": "mmss", "sello": "dato",
             "marcas": [{"x": 0, "texto": f"+{pico:.1f} kHz: se acerca", "lado": "arriba"},
                        {"x": round(tc, 1), "texto": "Cero: punto más cercano", "lado": "der", "dy": -30},
                        {"x": x[-1], "texto": f"−{pico:.1f} kHz: se aleja", "lado": "abajo"}],
             "nota": f"Pase de {hora} (hora de CDMX), {dur // 60} min {dur % 60} s sobre 10° de elevación; máxima de {p.el_max:.0f}°."},
            {"tipo": "dato", "kicker": "Desplazamiento máximo", "cifra": f"±{pico:.1f}", "unidad": "kHz", "sello": "dato",
             "titulo": f"Lo que se mueve la frecuencia en un solo pase (a {f0_mhz:.0f} MHz)",
             "nota": f"Calculado con SGP4 · CelesTrak/18 SDS · época {epoca}. A otra frecuencia, el cambio es proporcional."},
            {"tipo": "formula", "kicker": "De dónde sale", "titulo": "El efecto Doppler, con números de este pase",
             "formula": "f = f₀ · (1 − ṙ / c)",
             "pasos": ["f: frecuencia recibida · f₀: la emitida · ṙ: cuánto cambia la distancia (km/s, positivo si se aleja).",
                       f"Al aparecer: ṙ = {e['rr_aos_kms']:+.2f} km/s, Δf = {e['df_aos_khz']:+.1f} kHz".replace("-", "−"),
                       "En el punto más cercano: ṙ ≈ 0, Δf ≈ 0"],
             "resultado": f"Δf entre ±{pico:.1f} kHz", "nota": "c = 299 792 km/s.", "sello": "dato"},
            {"tipo": "dato", "kicker": "Lo que un receptor debe seguir", "cifra": f"{pend:.0f}", "unidad": "Hz por segundo", "sello": "dato",
             "titulo": "La frecuencia cambia más rápido justo al pasar sobre ti",
             "nota": f"Pendiente máxima de la curva en este pase, a {f0_mhz:.0f} MHz. Por eso se corrige el Doppler por software."},
            {"tipo": "cierre", "titulo": "Un satélite, una curva, un cálculo",
             "texto": "Orbit Eye propone la corrección Doppler por software: conoce sus plataformas en codeaerospace.com"},
        ],
        "fuentes": [f"CelesTrak GP, objeto 25544 (celestrak.org/NORAD/elements/gp.php?CATNR=25544), elementos con época {epoca}; muestra congelada en studio/content/datos_orbitales/muestras/",
                    "Cálculo: SGP4 (paquete sgp4 2.27) + geometría topocéntrica WGS-84; código en studio/content/manim_extensions/datos_orbitales",
                    "codeaerospace.com/plataformas (Orbit Eye: corrección Doppler por Hamlib), consultado 2026-10-01"],
        "pie_texto": (f"La curva en S del Doppler, calculada con un pase real de la ISS sobre Ciudad de México ({fecha_larga(e['aos_local'])}, {hora} hora local). "
                      f"Datos: CelesTrak/18 SDS, época {epoca}. Cálculo: SGP4. La frecuencia (f₀ = {f0_mhz:.0f} MHz) es un ejemplo para ilustrar la magnitud. "
                      "Orbit Eye corrige este efecto por software (el despliegue público no tiene receptor conectado: se demuestra con grabaciones IQ). "
                      "#ISS #Doppler #SDR #satélites #ingenieríaespacial"),
        "cuidado": [f"Elementos orbitales con época {epoca}: una predicción de pase envejece (~1 km por día); si se publica después de {el.epoca.date()} + 3 días, aclararlo como CÁLCULO de ese pase.",
                    f"f₀ = {f0_mhz:.0f} MHz es una frecuencia de EJEMPLO: no se afirma que la ISS transmita ahí en este pase.",
                    "Verificar la hora del pase contra una fuente independiente (NASA Spot the Station / Heavens-Above) antes de presentarlo como «pase de hoy».",
                    f"Ubicación del observador redondeada a 0.1° ({obs.lat}, {obs.lon}); no publicar coordenadas más precisas.",
                    "Orbit Eye es obra derivada de ground-station (GPL-3.0) y su despliegue público no tiene receptor de radio conectado."],
    }
    return spec


def main():
    destino = Path(__file__).parent / "specs" / "datos-reales"
    destino.mkdir(parents=True, exist_ok=True)
    for spec in (doppler_iss(),):
        ruta = destino / f"{spec['id']}.json"
        ruta.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
        print("escrito", ruta)


if __name__ == "__main__":
    main()
