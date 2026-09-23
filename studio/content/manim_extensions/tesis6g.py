"""Tesis 6G por dentro: piezas limpias para PowerPoint y el curso 36.

La tesis (Alan Rosas Palacios, IPN; «Gobernanza autonoma de redes
programables», instanciada en redes no terrestres 6G) sostiene que aplicar
IA a una red satelital es un problema de INSTRUMENTO antes que de algoritmo:
hay que medir si el entorno premia adaptarse (el Margen Adaptativo) antes de
comparar algoritmos sobre el. Este modulo da lo que las piezas y el curso
necesitan y la casa no tenia:

  - `Paleta`: los roles de color de la tesis (estatica, adaptativa,
    privilegiada, aprobado, invalidado) en la paleta del DECK del seminario
    (navy 0B1F3A / ambar E8A33D), con variante para fondo claro y oscuro.
  - `etiqueta()` / `cifra()`: texto en Carlito (metricamente Calibri, la
    letra del deck), con un guardian que ABORTA si una etiqueta de pieza
    pasa de tres palabras: la frase la pone PowerPoint, no el video.
  - `pieza()` / `aplicar_pieza()`: el lienzo de `presentacion.py` SIN marca
    de agua ni escuadras — lo que mimetiza una pieza con el slide es no
    traer identidad propia.
  - Numerica exacta de la teoria del margen: `juego_coordinacion()` (la
    construccion de holgura no acotada: MA = m-1 con MA_dec = 0),
    `juego_coordinacion_obs()` (observacion con perdida), su Monte Carlo
    `simular_juego()`, y `maldicion_ganador()` (el maximo muestral de las
    politicas estaticas sobreestima: MA sale deprimido con pocos episodios).
  - `datos_tesis()`: las cifras de la tesis LEIDAS de sus JSON (copiados por
    `studio/tools/traer_datos_tesis.py` a un directorio gitignored: el repo
    de la tesis es privado). Nunca se transcribe una cifra de la tesis.

Uso en una pieza:

    import sys
    sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    import presentacion, tesis6g as T6

    LZ, PAL = T6.pieza()

    class Margen(Scene):
        def setup(self):
            T6.aplicar_pieza(self, LZ)

        def construct(self):
            e = T6.etiqueta("Estatica", PAL, color=PAL.estatica)
            ...
            presentacion.paso(self, "La estatica")

Determinista: toda aleatoriedad con `np.random.default_rng(semilla)`.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from manim import Text

import presentacion
from code_brand import registrar_fuentes

VERSION = "1.0"

FUENTE = "Carlito"
# Cuantas palabras admite una etiqueta de PIEZA. Tres cubre "Ruta terrestre
# alterna" y "Mejor politica estatica"; cuatro ya es una frase de titular.
PALABRAS_PIEZA = 3

DATOS_DIR = Path(__file__).resolve().parents[1] / "datos" / "tesis-6g-privado"


# =============================================================================
# Paleta: roles, no colores
# =============================================================================

# Paleta del deck (deck_common.js de la tesis). Los tonos del deck estan
# pensados para fondo BLANCO; sobre el navy varios no se leen (el azul
# 2E6F95 da 2.9:1), asi que la variante oscura aclara el mismo matiz.
DECK = {
    "navy": "#0B1F3A", "azul": "#2E6F95", "ambar": "#E8A33D",
    "ambar_osc": "#A96A12", "verde": "#3E8E7E", "rojo": "#C1443C",
    "gris": "#5A6B7C", "rejilla": "#D8DEE4", "palido": "#EDF2F6",
}
FONDO_OSCURO = DECK["navy"]
FONDO_CLARO = "#FFFFFF"

_ROLES_OSCURO = {
    "tinta": "#F4F7FA",
    "apoyo": "#8EA2B7",
    "tenue": "#2C4262",      # rejilla, lo que casi no esta
    "estatica": "#C8CCD1",
    "adapta": "#E8A33D",
    "priv": "#6CB4E4",
    "ok": "#5CC2A5",
    "no": "#EE6C62",
}
_ROLES_CLARO = {
    "tinta": "#0B1F3A",
    "apoyo": "#5A6B7C",
    "tenue": "#D8DEE4",
    "estatica": "#575757",
    "adapta": "#935B0A",     # el A96A12 del deck da 4.41:1 sobre blanco
    "priv": "#1D63A6",
    "ok": "#2F7A6B",
    "no": "#B23B33",
}


@dataclass(frozen=True)
class Paleta:
    """Los papeles de color de la tesis sobre UN fondo concreto.

    tinta    trazo y texto principal
    apoyo    mobiliario y lo que un agente NO ve
    tenue    rejilla, fondo de una barra
    estatica la gestion estatica (best_static): siempre este color
    adapta   la politica adaptativa o aprendida (QMIX, heuristica)
    priv     la informacion privilegiada (oraculo, techo)
    ok       compuerta aprobada
    no       invalidado, tachado
    """
    fondo: str
    es_claro: bool
    tinta: str
    apoyo: str
    tenue: str
    estatica: str
    adapta: str
    priv: str
    ok: str
    no: str

    @classmethod
    def de(cls, fondo: str) -> "Paleta":
        claro = presentacion._luminancia(fondo) > 0.35
        roles = _ROLES_CLARO if claro else _ROLES_OSCURO
        return cls(fondo=fondo, es_claro=claro, **roles)

    def roles(self) -> dict:
        return {k: getattr(self, k) for k in
                ("tinta", "apoyo", "tenue", "estatica", "adapta", "priv", "ok", "no")}

    def contrastes(self) -> dict:
        """Contraste WCAG de cada rol contra el fondo (la sonda exige >= 4.5
        en los roles que llevan texto y >= 3 en los de solo trazo)."""
        return {k: round(presentacion.contraste(v, self.fondo), 2)
                for k, v in self.roles().items()}


# Roles que llevan TEXTO encima del fondo: se exige 4.5:1. `tenue` es solo
# relleno/rejilla y no se mide.
ROLES_TEXTO = ("tinta", "apoyo", "estatica", "adapta", "priv", "ok", "no")


def pieza(fondo=None, formato=None, calidad=None):
    """Lienzo + paleta de una pieza. Sin argumentos lee el entorno que pone
    `empaquetar_presentacion.py` (PRESENTACION_FONDO, ...); por defecto el
    navy del deck, no el negro de la marca."""
    import os
    fondo = fondo or os.environ.get("PRESENTACION_FONDO") or FONDO_OSCURO
    if fondo == "marca":           # una pieza de la tesis nunca va en negro marca
        fondo = FONDO_OSCURO
    lz = presentacion.lienzo(nombre=formato, fondo=fondo, calidad=calidad)
    return lz, Paleta.de(lz.fondo)


def aplicar_pieza(escena, lz) -> None:
    """Fondo exacto del slide, sin marca de agua ni escuadras."""
    registrar_fuentes()
    presentacion.aplicar(escena, lz, marca_agua=False, esquinas=False)


# =============================================================================
# Texto: pocas palabras, en la letra del deck
# =============================================================================

class LetraProhibida(ValueError):
    pass


def _vigilar(texto: str, maximo: int) -> None:
    n = len(str(texto).split())
    if maximo and n > maximo:
        raise LetraProhibida(
            f"{texto!r} tiene {n} palabras (tope {maximo}): en una pieza el "
            "texto lo pone PowerPoint. Acorta la etiqueta o cambia el dibujo.")


def etiqueta(texto, pal: Paleta, fs=30, color=None, peso="NORMAL",
             palabras=PALABRAS_PIEZA):
    """Rotulo de mapa en Carlito. Aborta si pasa de `palabras`."""
    _vigilar(texto, palabras)
    registrar_fuentes()
    return Text(str(texto), font=FUENTE, weight=peso, font_size=fs,
                color=color or pal.apoyo)


def cifra(texto, pal: Paleta, fs=40, color=None, peso="BOLD"):
    """Un numero (con su unidad corta). Mismo guardian: 3 tokens."""
    return etiqueta(texto, pal, fs=fs, color=color or pal.tinta, peso=peso)


def pct(x, dec=1):
    """0.318 -> '31.8 %'. Sin rstrip: el formateador que se come ceros ya
    escribio un rotulo falso en otro curso."""
    return f"{100 * float(x):.{dec}f} %"


# =============================================================================
# Teoria del margen: numerica exacta
# =============================================================================

def juego_coordinacion(m: int, R: float = 1.0) -> dict:
    """La construccion de §2.2 de TEOREMA_MARGEN_ADAPTATIVO.md.

    Dos agentes eligen entre m casillas; el estado s ~ Unif{1..m} es exogeno;
    la recompensa es R si los dos eligen s y 0 si no; las observaciones no
    informan nada. Valores POR PASO (el horizonte multiplica los tres y no
    cambia los cocientes):

        V_est  = R/m   (la mejor constante acierta 1 de m)
        V_dec  = R/m   (sin observacion, no se puede hacer mejor)
        V_priv = R     (viendo s, se acierta siempre)

    => MA = m-1, arbitrariamente grande, con MA_dec = 0 EXACTO.
    """
    if m < 2:
        raise ValueError("el juego necesita m >= 2 casillas")
    v_est = R / m
    v_dec = R / m
    v_priv = R
    return {"m": m, "V_est": v_est, "V_dec": v_dec, "V_priv": v_priv,
            "MA": (v_priv - v_est) / v_est, "MA_dec": (v_dec - v_est) / v_est}


def juego_coordinacion_obs(m: int, eps: float, R: float = 1.0) -> dict:
    """La variante del mismo documento: cada agente ve s con prob. 1-eps.

    Politica descentralizada optima: jugar s si se ve, una casilla fija k si
    no. Aciertan juntos si los dos ven s (prob (1-eps)^2) o, si alguno no lo
    ve, cuando s cae justo en k (prob 1/m):

        V_dec = R [ (1-eps)^2 + (1 - (1-eps)^2) / m ]
        MA_dec = (m-1)(1-eps)^2        mientras MA sigue en m-1.

    `simular_juego` lo comprueba por Monte Carlo en la sonda.
    """
    if not 0.0 <= eps <= 1.0:
        raise ValueError("eps en [0, 1]")
    ver = (1.0 - eps) ** 2
    v_est = R / m
    v_dec = R * (ver + (1.0 - ver) / m)
    base = juego_coordinacion(m, R)
    base.update({"eps": eps, "V_dec": v_dec, "MA_dec": (v_dec - v_est) / v_est})
    return base


def simular_juego(m: int, eps: float, pasos: int = 200_000, semilla: int = 42,
                  k_fijo: int = 0) -> dict:
    """Monte Carlo del juego con observacion con perdida. Devuelve las tres
    recompensas medias medidas (estatica, descentralizada, privilegiada)."""
    rng = np.random.default_rng(semilla)
    s = rng.integers(0, m, pasos)
    ve1 = rng.random(pasos) >= eps
    ve2 = rng.random(pasos) >= eps
    a1 = np.where(ve1, s, k_fijo)
    a2 = np.where(ve2, s, k_fijo)
    dec = ((a1 == s) & (a2 == s)).mean()
    est = (s == k_fijo).mean()              # los dos juegan k siempre
    priv = 1.0                              # ver s: acierto seguro
    return {"V_est": float(est), "V_dec": float(dec), "V_priv": priv,
            "MA_dec": float((dec - est) / est), "MA": float((priv - est) / est)}


def maldicion_ganador(valores, sigma: float, episodios: int, v_oraculo: float,
                      repeticiones: int = 2000, semilla: int = 42) -> dict:
    """Por que el MA estimado sale DEPRIMIDO con pocos episodios.

    `make_best_static_policy` de la tesis evalua las 27 constantes sobre los
    MISMOS episodios y se queda con la mejor media muestral. El maximo de
    medias ruidosas sobreestima el mejor valor verdadero (sesgo de
    seleccion), el denominador del MA se infla y el MA baja.

    `valores`  valor verdadero de cada politica estatica (por episodio)
    `sigma`    desviacion de la recompensa de un episodio
    Devuelve el mejor valor verdadero, la media del maximo muestral, el
    sesgo, y el MA verdadero frente al MA estimado medio.
    """
    v = np.asarray(valores, dtype=float)
    rng = np.random.default_rng(semilla)
    ruido = rng.normal(0.0, sigma / np.sqrt(episodios), (repeticiones, v.size))
    maximo = (v[None, :] + ruido).max(axis=1)
    mejor = float(v.max())
    ma_vero = (v_oraculo - mejor) / mejor
    ma_est = (v_oraculo - maximo) / maximo
    return {"episodios": episodios, "mejor": mejor,
            "max_muestral": float(maximo.mean()),
            "sesgo": float(maximo.mean() - mejor),
            "MA": float(ma_vero), "MA_est": float(ma_est.mean()),
            "MA_est_std": float(ma_est.std())}


# =============================================================================
# Datos de la tesis, leidos (nunca transcritos)
# =============================================================================

def _leer(nombre):
    ruta = DATOS_DIR / nombre
    if not ruta.exists():
        raise FileNotFoundError(
            f"falta {ruta}. Los resultados de la tesis no se versionan (repo "
            "privado): corre `python3 studio/tools/traer_datos_tesis.py`.")
    return json.loads(ruta.read_text(encoding="utf-8"))


def _num_inicial(texto):
    import re
    m = re.search(r"[-+]?\d+(?:\.\d+)?", texto or "")
    return float(m.group()) if m else None


def datos_tesis() -> dict:
    """Las cifras que dibujan las piezas, con el fichero del que salen.

    g0_ma         MA del entorno v1 (control negativo)       GATES.md G0
    g1_ma         MA de NTNEnv-v2, media de 3 semillas        g1_4x.json
    g1_por_semilla
    umbral        0.25                                        GATES.md G1
    g2b           por semilla: estatica, qmix, oraculo, mejora, frac_oraculo
    piloto_mock   mejor recompensa del piloto invalidado por R5, por semilla
    vdn           mejora sobre estatica del brazo VDN (gate / heldout)
    sensibilidad  [(episodios, ma_media)] incluido el punto de G1 (30)
    compuertas    la lista G0..G4 tal cual la escribe GATES.md
    """
    comp = _leer("compuertas.json")
    por_id = {c["id"]: c for c in comp}
    g1 = [_leer(f"g1_{s}.json") for s in (42, 43, 44)]
    g2 = _leer("g2b_v7.json")
    mock = _leer("g2b_piloto_mock.json")
    vdn = _leer("g2b_vdn.json")
    sens = _leer("ma_sensibilidad.json")
    filas = [(f["episodios"], f["ma_mean"]) for f in sens["filas"]]
    filas.append((sens["referencia_G1"]["episodios"], sens["referencia_G1"]["ma_mean"]))
    umbral = _num_inicial(por_id["G1"]["criterio"].split("≥")[-1])
    gh = _leer("gh_heuristica.json")
    return {
        # G-H: heuristica ingenua (umbral 0.35) y afinada (grid de 270) contra
        # la mejor estatica, por semilla de evaluacion
        "heuristica": [{"semilla": p["seed"], "estatica": p["best_static"]["reward_mean"],
                        "ingenua": p["current"]["reward_mean"], "afinada": p["tuned"]["reward_mean"],
                        "afinada_vs_estatica": p["delta_vs_static_pct"] / 100.0}
                       for p in gh["per_seed"]],
        "heuristica_configs": gh["grid"]["n_configs"],
        "g0_ma": _num_inicial(por_id["G0"]["valor"]),
        "g1_ma": float(np.mean([x["ma"] for x in g1])),
        "g1_por_semilla": {x["seed"]: x["ma"] for x in g1},
        "umbral": umbral,
        "g2b": [{"semilla": p["seed"], "estatica": p["best_static"],
                 "qmix": p["reward_mean"], "oraculo": p["oracle"],
                 "mejora": p["mejora_vs_static_pct"] / 100.0,
                 "frac_oraculo": p["frac_oracle"]} for p in g2["per_seed"]],
        "piloto_mock": {int(k): v["best_reward"] for k, v in mock["resultados"].items()},
        # La semilla 44 del brazo VDN no encontro politica adaptativa: no
        # trae evaluacion. Se conserva como tal, no se rellena.
        "vdn": [{"semilla": p["seed"], "encontrada": bool(p.get("adaptive_found")) and "gate" in p,
                 "gate": p["gate"]["mejora_vs_static_pct"] / 100.0 if "gate" in p else None,
                 "heldout": p["heldout"]["mejora_vs_static_pct"] / 100.0 if "heldout" in p else None}
                for p in vdn["per_seed"]],
        "sensibilidad": filas,
        "compuertas": comp,
    }


# =============================================================================
# Curvas de ilustracion (piezas «margen» y «piso»)
# =============================================================================

def curvas_margen(n=480, vueltas=2.0, periodo_gw=0.37, ciclo_gw=0.30,
                  plano=False) -> dict:
    """Tres acciones cuya recompensa cambia con el tiempo, con la MISMA
    estructura que NTNEnv-v2 (sin ser NTNEnv-v2):

      A  espectro bajo   paga mucho con el satelite a la vista
      B  espectro alto   el complemento (paga cuando A no)
      C  ruta terrestre  estable, pero cae en los picos de congestion del
                         gateway — y aun asi es la MEJOR constante, como la
                         [2,2,2] de la tesis

    Devuelve t, R (3 x n), la mejor constante (indice y serie), la envolvente
    (lo que haria quien ve todo, paso a paso) y el MA de estas curvas.

    `plano=True` da el contraejemplo del Teorema 4.7.1: la misma C domina en
    TODO instante, la envolvente coincide con la estatica y MA = 0.
    """
    t = np.linspace(0.0, 1.0, n)
    vis = 0.5 + 0.5 * np.cos(2 * np.pi * vueltas * t)
    fase = (t % periodo_gw) / periodo_gw
    # pulso suave de congestion: sube y baja con un coseno dentro de su ciclo
    cong = np.where(fase < ciclo_gw, 0.5 - 0.5 * np.cos(2 * np.pi * fase / ciclo_gw), 0.0)
    A = 0.40 + 0.75 * vis
    B = 0.40 + 0.75 * (1.0 - vis)
    C = 1.02 - 0.55 * cong
    if plano:
        A = 0.45 + 0.30 * vis
        B = 0.45 + 0.30 * (1.0 - vis)
        C = np.full_like(t, 0.95)
    R = np.vstack([A, B, C])
    medias = R.mean(axis=1)
    mejor = int(np.argmax(medias))
    env = R.max(axis=0)
    v_est = float(medias[mejor])
    v_priv = float(env.mean())
    return {"t": t, "R": R, "mejor": mejor, "estatica": R[mejor], "envolvente": env,
            "argmax": R.argmax(axis=0), "V_est": v_est, "V_priv": v_priv,
            "MA": (v_priv - v_est) / v_est, "medias": medias}


# =============================================================================
# Datos PUBLICADOS por otros (no se calculan aqui: van en gris / apoyo)
# =============================================================================

# ASTREA (carga IMAGIN-e en la ISS, sep-2025): un LLM de 1.54 B parametros
# aconseja el coeficiente de entropia de un controlador SAC termico. Cambio en
# violaciones termicas frente a la linea base, segun la ventana del consejo.
# Fuente: Mousist, arXiv:2509.13380 v2, §4.3 (re-verificado en la tesis:
# INFORME_REVELADOR_2026-09-02.md, H1). Preprint de un autor, pocos episodios
# y sin intervalos: la tesis pide decirlo al citarlo.
ASTREA = {
    "ventana_rapida_min": 15, "violaciones_rapida": +0.242,
    "ventana_orbital_min": 90, "violaciones_orbital": -0.662,
    "fuente": "Mousist, arXiv:2509.13380 v2, §4.3",
}

# Satelites activos en orbita. Fuente: Jonathan McDowell, corte del
# 13-ago-2026 (GUION_COMITE_TUTORIAL_PROTOCOLO.md de la tesis).
ESCALA = {"activos": 16279, "starlink": 10742, "fuente": "McDowell, 13-ago-2026"}

# Calendario (publico o de la tesis). El freeze de la primera release 6G lo
# da 3GPP como "potentially in early 2029" (INFORME_REVELADOR, H3).
HITOS = [
    {"id": "hoy", "anio": 2026.72, "texto": "Hoy"},
    {"id": "witcom", "anio": 2026.84, "texto": "WITCOM"},
    {"id": "freeze", "anio": 2029.1, "texto": "Freeze 6G"},
    {"id": "defensa", "anio": 2030.1, "texto": "Defensa"},
]
INICIO_DOCTORADO, FIN_DOCTORADO = 2026.08, 2030.1


def muestras_ganador(valores, sigma, episodios, semilla=42):
    """Una realizacion de las medias muestrales de cada politica estatica
    (lo que ve `make_best_static_policy`): para dibujar el sesgo."""
    v = np.asarray(valores, dtype=float)
    rng = np.random.default_rng(semilla)
    return v + rng.normal(0.0, sigma / np.sqrt(episodios), v.size)


def trayectorias(n=6, pasos=120, azar=0.0, semilla=42):
    """Trayectorias del mundo en varios episodios. Con azar=0 todas son la
    MISMA (el banco sin estocasticidad donde una politica de lazo abierto,
    que solo mira el reloj, basta); con azar>0 se abren en abanico."""
    rng = np.random.default_rng(semilla)
    t = np.linspace(0, 1, pasos)
    base = 0.55 * np.sin(2 * np.pi * 1.2 * t) + 0.25 * np.sin(2 * np.pi * 3.1 * t + 0.4)
    out = []
    for _ in range(n):
        paseo = np.cumsum(rng.normal(0, 1, pasos)) / np.sqrt(pasos)
        fase = rng.normal(0, 1)
        out.append(base + azar * (0.9 * paseo + 0.35 * np.sin(2 * np.pi * 2 * t + fase)))
    return t, np.array(out)


def entorno_v2() -> dict:
    """Los parametros de NTNEnv-v2 que dibuja la pieza «red integrada»,
    leidos del YAML de las compuertas (configs/env_v2_dynamic.yaml)."""
    import yaml
    ruta = DATOS_DIR / "entorno_v2.yaml"
    if not ruta.exists():
        _leer("entorno_v2.yaml")                 # mismo mensaje de error
    c = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    return {
        "agentes": c["n_agents"],
        "eclipse_umbral": c["visibility"]["eclipse_threshold"],
        "eclipse_factor": c["visibility"]["eclipse_throughput_factor"],
        "gw_capacidad_pico": 1.0 - c["gw_congestion"]["depth"],
        "gw_periodo": c["gw_congestion"]["period"],
        "canal_factor": c["channel_degradation"]["factor"],
        "canal_observable": c["channel_degradation"]["observable"],
        "orbita_periodo": c["dynamics"]["orbit_period"],
        "canal_periodo": c["channel_degradation"]["period"],
        "gw_ciclo": c["gw_congestion"]["duty_cycle"],
        "gw_jitter": c["gw_congestion"]["jitter"],
        "decaimiento": c["dynamics"]["interference_decay"],
        "tabla_tp": list(c["dynamics"]["throughput_table"]),
        "lat_baja": c["dynamics"]["latency_low"],
        "lat_alta": c["dynamics"]["latency_high"],
        "dim_estado": c["state_dim"], "dim_obs": c["obs_dim"],
        "pasos_episodio": c["max_steps"],
    }


# =============================================================================
# La mecanica de NTNEnv-v2, reproducida (env_adapter.py / env_adapter_v2.py)
# =============================================================================
# Solo lo que dibujan las piezas y el curso, con las MISMAS formulas del
# codigo de la tesis. La sonda las comprueba contra lo que dicen sus
# docstrings (eclipse ~40 % del tiempo, pico del gateway al 30 %...).

def visibilidad_v2(pasos, E=None, fase0=0.0):
    """vis_i(t) = 0.5 (1 + sin(fase + desfase_i)), fase += 2 pi / periodo.
    Desfases linspace(0, pi, 3): satelite 1 = 0, satelite 2 = pi/2 (el
    gateway reporta 1.0 siempre). Devuelve (2, pasos)."""
    E = E or entorno_v2()
    t = np.arange(pasos)
    fase = fase0 + 2 * np.pi * t / E["orbita_periodo"]
    off = np.linspace(0, np.pi, E["agentes"])[:2]
    return 0.5 * (1.0 + np.sin(fase[None, :] + off[:, None]))


def congestion_v2(pasos, E=None, semilla=None):
    """Nivel del gateway en {0,1}: pico de duty*periodo pasos por ciclo. Sin
    semilla el pico empieza al inicio de cada ciclo; con semilla, con el
    jitter de la tesis (inicio ~ U(0, jitter*periodo) en cada ciclo)."""
    E = E or entorno_v2()
    per, duty = E["gw_periodo"], E["gw_ciclo"]
    rng = np.random.default_rng(semilla) if semilla is not None else None
    out = np.zeros(pasos)
    inicio = 0.0
    for t in range(pasos):
        k = t % per
        if k == 0 and rng is not None:
            inicio = float(rng.uniform(0.0, E["gw_jitter"] * per))
        out[t] = 1.0 if inicio <= k < inicio + duty * per else 0.0
    return out


def canal_degradado_v2(pasos, E=None):
    """Indice del canal degradado {0,1}: rota cada `canal_periodo` pasos."""
    E = E or entorno_v2()
    return (np.arange(pasos) // E["canal_periodo"]) % 2


def interferencia_v2(usa_degradado, E=None, bump=0.35, i0=0.0):
    """I <- clip(decaimiento*I + bump*[usa el canal degradado], 0, 1): la
    parte determinista de la interferencia de la tesis (sin colisiones ni
    ruido). Es lo que DELATA al canal que no se observa."""
    E = E or entorno_v2()
    rho = E["decaimiento"]
    out, i = [], float(i0)
    for u in usa_degradado:
        i = min(1.0, max(0.0, rho * i + bump * float(u)))
        out.append(i)
    return np.array(out)
