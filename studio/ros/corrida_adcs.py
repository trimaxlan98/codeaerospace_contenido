"""Lee una corrida de sat_adcs (ROS 2) y la deja lista para dibujar.

La corrida trae la ACTITUD (cuaternión verdadero y estimado, ruedas, modo, eclipse, elevación)
a 1 Hz. La POSICIÓN del satélite no viene en la telemetría: se recalcula con SGP4 y el MISMO
TLE congelado en la carpeta de la corrida, y se comprueba contra la elevación que grabó ROS
(`verificar()`): si no coinciden, el dibujo estaría mintiendo y se aborta.
"""
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from sgp4.api import Satrec, jday

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from motor3d import astro  # noqa: E402

MODOS = {0: "DETUMBLE", 1: "NADIR", 2: "TRACK_GS"}


class CorridaAdcs:
    def __init__(self, carpeta):
        self.dir = Path(carpeta)
        filas = [json.loads(l) for l in open(self.dir / "telemetry.jsonl", encoding="utf-8")]
        self.metricas = json.load(open(self.dir / "metrics.json", encoding="utf-8"))
        self.params = json.load(open(self.dir / "params.json", encoding="utf-8"))
        self.t = np.array([f["t"] for f in filas])
        self.q = np.array([f["q"] for f in filas])
        self.w = np.array([f["w_deg_s"] for f in filas])
        self.modo = np.array([f["mode"] for f in filas])
        self.eclipse = np.array([f["eclipse"] for f in filas])
        self.el = np.array([f["el_deg"] for f in filas])
        self.rango = np.array([f["range_km"] for f in filas])
        self.h = np.array([f["h_nms"] for f in filas])
        self.err = np.array([f.get("err_deg", np.nan) for f in filas])
        self.en_pase = np.array([f["in_pass"] for f in filas])
        self.q_est = np.array([f.get("q_est", [np.nan] * 4) for f in filas])
        lineas = (self.dir / "tle.txt").read_text().splitlines()
        self.nombre_sat = lineas[0].strip()
        self.sat = Satrec.twoline2rv(lineas[1], lineas[2])
        d = self.params["defaults"]
        self.inicio = datetime.fromisoformat(d["start_utc"]).replace(tzinfo=timezone.utc)
        e = self.params["estacion"]
        self.estacion = (e["lat"], e["lon"], e["alt_m"] / 1000.0)

    # ---------- interpolación ----------
    def _i(self, t):
        t = float(np.clip(t, self.t[0], self.t[-1]))
        i = int(min(np.searchsorted(self.t, t, side="right") - 1, len(self.t) - 2))
        return i, (t - self.t[i]) / (self.t[i + 1] - self.t[i])

    def q_en(self, t, estimado=False):
        Q = self.q_est if estimado else self.q
        i, u = self._i(t)
        if np.isnan(Q[i]).any() or np.isnan(Q[i + 1]).any():
            return None
        return astro.slerp(Q[i], Q[i + 1], u)

    def serie(self, nombre, t):
        return float(np.interp(t, self.t, getattr(self, nombre)))

    def modo_en(self, t):
        return int(self.modo[self._i(t)[0]])

    def utc(self, t):
        return self.inicio + timedelta(seconds=float(t))

    def r_teme(self, t):
        """Posición TEME en radios terrestres (SGP4, el TLE de la corrida)."""
        u = self.utc(t)
        jd, fr = jday(u.year, u.month, u.day, u.hour, u.minute, u.second + u.microsecond * 1e-6)
        e, r, v = self.sat.sgp4(jd, fr)
        if e:
            raise RuntimeError(f"SGP4 error {e} en t={t}")
        return np.array(r) / astro.R_TIERRA_KM

    def jd(self, t):
        return astro.jd(self.utc(t))

    def estacion_teme(self, t):
        return astro.rz(astro.gmst(self.jd(t))) @ astro.geodetica_a_ecef(*self.estacion)

    def elevacion_calc(self, t):
        r = self.r_teme(t)
        g = self.estacion_teme(t)
        up = g / np.linalg.norm(g)                 # vertical geocéntrica (aprox. ≤ 0.2° de la geodésica)
        d = r - g
        return math.degrees(math.asin(np.dot(d, up) / np.linalg.norm(d)))

    def verificar(self, tol_el=0.35, tol_ecl=8):
        """Nuestra posición (SGP4 + TLE congelado) contra lo que grabó ROS: elevación y eclipse."""
        idx = np.linspace(0, len(self.t) - 1, 120).astype(int)
        dif = [abs(self.elevacion_calc(self.t[i]) - self.el[i]) for i in idx]
        malos_ecl = 0
        for i in range(0, len(self.t), 5):
            s = astro.sol_teme(self.jd(self.t[i]))
            luz = astro.sombra_cilindrica(self.r_teme(self.t[i]), s)
            malos_ecl += int((luz < 0.5) != bool(self.eclipse[i]))
        ok = max(dif) <= tol_el and malos_ecl <= tol_ecl
        return {"el_max_dif_deg": round(max(dif), 4), "eclipse_discrepancias": malos_ecl, "ok": ok}
