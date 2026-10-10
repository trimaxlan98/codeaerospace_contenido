"""Congela las simulaciones y los datos de la serie «Caos y gravedad» en studio/content/datos_caos/ (el render no recalcula ni
usa la red). Uso: python3 studio/tools/caos_congelar.py [--sin-red]

- figura ocho y su gemela perturbada (N cuerpos, DOP853)
- problema pitagórico de Burrau (masas 3, 4, 5) y su gemela a 1e-6 (suavizado 1e-3 para los encuentros muy cercanos)
- Jano y Epimeteo con masas reales (≈ 8 min de cálculo)
- giro de Hiperión (ω0 = 0.89, e = 0.1) y de una luna regular
- histograma de semiejes del cinturón de asteroides y conteo de troyanos de Júpiter (NASA/JPL SBDB Query API)
"""
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "studio/content/manim_extensions"))
import caos_gravedad as G  # noqa: E402

SALIDA = REPO / "studio/content/datos_caos"
API = "https://ssd-api.jpl.nasa.gov/sbdb_query.api"


def _api(params):
    url = API + "?" + "&".join(f"{k}={v}" for k, v in params.items())
    with urllib.request.urlopen(url, timeout=600) as r:
        return url, json.load(r)


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    m1 = np.ones(3)
    x, v = G.ocho_inicial()
    t, X, _ = G.tres_cuerpos(x, v, m1, G.OCHO_T, 400)
    x2, v2 = G.ocho_inicial((1e-3, 0.0))
    t2, X2, _ = G.tres_cuerpos(x2, v2, m1, 6 * G.OCHO_T, 2400)
    np.savez_compressed(SALIDA / "ocho.npz", t=t, X=X, t_gemela=t2, X_gemela=X2)
    print("ocho ✓")

    m = np.array([3.0, 4.0, 5.0])
    x = np.array([[1.0, 3.0], [-2.0, -1.0], [1.0, -1.0]]); v = np.zeros((3, 2))
    pit = {}
    for nombre, dx in (("a", 0.0), ("b", 1e-6)):
        xx = x.copy(); xx[0, 0] += dx
        t, X, _ = G.tres_cuerpos(xx, v, m, 80.0, 4000, suave=1e-3)
        pit[nombre] = X
    np.savez_compressed(SALIDA / "pitagorico.npz", t=t, A=pit["a"], B=pit["b"], m=m)
    print("pitagórico ✓")

    t, th, w = G.giro_orbita(0.89, 0.1, 0.0, 1.0, 40, 4000)
    _, th_l, w_l = G.giro_orbita(0.2, 0.0549, 0.0, 1.0, 40, 4000)
    np.savez_compressed(SALIDA / "hiperion.npz", t=t, theta=th, w=w, theta_luna=th_l, w_luna=w_l)
    print("Hiperión ✓")

    t, ang, dr = G.coorbitales(anios=9.0, n_puntos=6000)
    np.savez_compressed(SALIDA / "coorbitales.npz", t=t, ang=ang, dr=dr)
    print("Jano y Epimeteo ✓")

    if "--sin-red" not in sys.argv:
        url, d = _api({"fields": "a", "sb-class": "IMB,MBA,OMB"})
        a = np.array([float(r[0]) for r in d["data"] if r[0] is not None])
        bordes = np.arange(2.0, 3.7001, 0.005)
        cuenta, _ = np.histogram(a, bordes)
        url_t, dt_ = _api({"fields": "full_name", "sb-class": "TJN", "limit": "1"})
        json.dump({"fuente": "NASA/JPL Small-Body Database Query API", "consulta": url, "consulta_troyanos": url_t,
                   "fecha_consulta": dt.date.today().isoformat(), "asteroides": int(d["count"]),
                   "troyanos_jupiter": int(dt_["count"]), "bordes_ua": bordes.round(4).tolist(), "cuenta": cuenta.tolist()},
                  open(SALIDA / "kirkwood.json", "w"), indent=0)
        print("Kirkwood ✓", d["count"], "asteroides;", dt_["count"], "troyanos")


if __name__ == "__main__":
    main()
