"""Curva Doppler de un pase: f_rx = f0·(1 − ṙ/c), con ṙ > 0 cuando el satélite se aleja."""
import numpy as np

from .observador import trayectoria

C_KM_S = 299_792.458


def curva_doppler(el, obs, pase, f0_hz, n=240):
    """t (s), df (Hz; positivo al acercarse), f_rx, df_max, t_cruce (s en que df=0), pendiente_max (Hz/s)."""
    tr = trayectoria(el, obs, pase, n)
    df = -f0_hz * tr["rangedot"] / C_KM_S
    k = np.where(np.diff(np.sign(df)) != 0)[0]
    if len(k):
        i = k[0]
        t_cruce = float(tr["t"][i] - df[i] * (tr["t"][i + 1] - tr["t"][i]) / (df[i + 1] - df[i]))
    else:
        t_cruce = float(tr["t"][int(np.argmin(np.abs(df)))])
    pend = np.abs(np.gradient(df, tr["t"]))
    return {"t": tr["t"], "df": df, "f_rx": f0_hz + df, "df_max": float(np.abs(df).max()), "t_cruce": t_cruce,
            "pendiente_max": float(pend.max()), "el": tr["el"], "az": tr["az"]}
