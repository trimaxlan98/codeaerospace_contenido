#!/usr/bin/env python3
"""musica.py - camas musicales sintetizadas para los videos de CO.DE Academy.

Hasta hoy ManimStudio no tenia musica: `unir_vertical.py --mudo` existe
*precisamente* porque el dueno se la ponia fuera, en un editor. La paleta de
`sfx.py` da EFECTOS (18) y dos ambientes (`pad`, `nebulosa`), pero un ambiente
no es una cama: no tiene tonalidad, ni pulso, ni progresion.

Aqui viven los TEMAS: musica procedural, con numpy, sin un solo asset, con
semillas fijas y determinista al byte, que corre DENTRO del contenedor de
render (sin red). Comparte formato con la narracion y con los SFX -- 24000 Hz
mono -- para que el `concat -c copy` de una pelicula no encuentre dos audios
distintos.

Criterio sonoro (el mismo que el dueno verifico para la marca, ver
docs/plan_contenido/marca-intro-y-cierre.md): «espacial pero tranquilo». En
cifras, eso es la mayoria de la energia por debajo de 300 Hz y casi nada por
encima de 950. Un tema no es una cancion: es un fondo que se oye sin
escucharse, tres octavas por debajo de donde vive la voz.

Tres capas, todas opcionales por tema y con su nivel:

  drone     colchon aditivo: una voz por nota del acorde (fundamental +
            quinta + octava muy tenues), vibrato en FASE (no en frecuencia:
            multiplicarlo por t llena el colchon de laterales asperos, ver
            `sfx.pad`), y un batido lento entre dos capas desafinadas.
  arpegio   cuerdas pulsadas (Karplus-Strong, como `sfx.cuerda`) en las
            subdivisiones del bpm, con un patron ciclico determinista y
            acento en la cabeza de cada tiempo.
  sub       sub-bajo senoidal en la fundamental del acorde, articulado a
            cada tiempo con una envolvente suave. Es lo que da el PULSO
            medible: la autocorrelacion de la envolvente pica en 60/bpm.

La progresion se repite y se recorta: `tema()` dura EXACTAMENTE lo que se le
pide, al sample, y termina con una caida suave (una cama que corta en seco
chasquea al empalmar, y en un promo que va en bucle se oye el salto).

API (la usan `sfx.promo` y `ensamblar.py`):

  tema(nombre, dur)            ndarray de EXACTAMENTE dur segundos, a -3 dBFS
  cama(nombre, dur, db)        lo mismo, al nivel de mezcla: se suma y ya
  escribe_cama(ruta, ...)      wav por bloques, para una pelicula entera,
                               con la ganancia de *ducking* ya aplicada
  catalogo()                   los temas como los sirve la API

Uso:
  musica.py banco [dir]              vista previa de cada tema (12 s)
                                     (defecto: exports/musica)
  musica.py catalogo                 los temas como JSON (con esto se
                                     regenera TEMAS_INFO de audio_promo.py)
  musica.py tema <nombre> <dur> <salida.wav>
  musica.py aplicar <video> <tema> <db> <salida.mp4>
                                     pega la cama sola bajo el video

Corre en el host o en el contenedor manim; el canario de main() verifica el
numpy antes de sintetizar (ver la historia en el docstring de sfx.py). Si
aborta:

  docker run --rm --network none --user $(id -u):$(id -g) \\
    -v "$PWD":/workspace -w /workspace codeaerospace_contenido-manim \\
    python3 studio/tools/musica.py banco
"""
from __future__ import annotations

import json
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sfx import (SR, _env, _filtra, _norm, _numpy_sano,  # noqa: E402
                 _reverbera, aplicar, dur_video, escribe_wav)

REPO = Path(__file__).resolve().parents[2]
BANCO = REPO / "exports" / "musica"

# Nivel de una cama recien sintetizada. -3 dBFS deja margen para sumarla a
# los SFX y a la voz antes de normalizar la mezcla entera.
PICO = -3.0
# Nivel por defecto de la cama DENTRO de una mezcla. Medido sobre el promo de
# filotaxis con una voz a -1.5 dBFS: la voz queda 15.0 dB por encima de la
# musica a -24 dB, 9.0 a -18 y 3.0 a -12. El minimo de la casa son 12 dB, que
# se rompe en -21 (de ahi el aviso del manifiesto).
MUSICA_DB = -24.0

# Fundidos globales del tema. Generosos a proposito: en un promo en bucle el
# salto del final al principio solo es invisible si los dos extremos callan.
FADE_IN_MAX, FADE_OUT_MAX = 1.2, 1.8
FADE_IN_FRAC, FADE_OUT_FRAC = 0.10, 0.16

# Pasabanda: «espacial pero tranquilo» es, medido, esto. El arpegio va por
# una banda propia y mas estrecha por abajo — sus fundamentales viven donde
# vive el sub-bajo, y dejarlas pasar enturbiaba el grave sin anadir nada que
# se oyera. Recortadas, la cuerda aporta su presencia (300-900 Hz) y el
# grave sigue siendo del sub.
BANDA_LO, BANDA_HI = 30.0, 900.0
ARPEGIO_LO, ARPEGIO_HI = 90.0, 950.0

# Sintesis por bloques para una pelicula larga: un curso de media hora son
# 43 millones de muestras y el pasabanda por FFT pediria ~1.4 GB. Cada bloque
# se sintetiza sobre el reloj ABSOLUTO con una entradilla que se descarta,
# asi que las costuras no se oyen (ver `_bloques`).
BLOQUE_S = 90.0
# Guardas que se sintetizan y se TIRAN a cada lado del bloque. La de entrada
# recupera las cuerdas que empezaron antes de la costura y parte de la cola de
# reverberacion; la de salida existe por una razon menos evidente: `_filtra`
# es una convolucion CIRCULAR (FFT de la longitud exacta), asi que el final de
# cada bloque se contamina con su propio principio. Medido sin ella, el salto
# entre muestras vecinas en la costura era 0.0089 sobre un pico de 0.063 — el
# mayor salto de todo el archivo, es decir, un clic.
ENTRADILLA_S = 3.0
COLA_S = 1.0

# Patron ciclico del arpegio: indices sobre las notas del acorde (extendidas
# con dos octavas altas). Fijo y sin azar — el azar en el ritmo se oye como
# error, no como variacion.
PATRON = (0, 3, 1, 4, 2, 5, 1, 3, 0, 4, 2, 5)


# ------------------------------------------------------------------- temas
# raiz     Hz de la tonica (donde vive el sub-bajo)
# grados   progresion: semitonos sobre la raiz, una lista por acorde
# bpm      pulso; `compas` tiempos por acorde, `div` notas por tiempo
# drone/arpegio/sub  nivel de cada capa (0 = apagada)
# semilla  el azar (excitacion de las cuerdas) es solo suyo
TEMAS = {
    "orbita": {
        "raiz": 55.00, "bpm": 52, "compas": 4, "div": 2,
        "grados": [[12, 15, 19, 24], [8, 12, 17, 24],
                   [15, 19, 22, 27], [10, 14, 17, 26]],
        "drone": 1.00, "arpegio": 0.30, "sub": 0.85, "semilla": 2101,
        "descripcion": "Menor abierto y lento; la cama por defecto de un "
                       "curso. Gira sin llegar a ninguna parte.",
    },
    "deriva": {
        "raiz": 49.00, "bpm": 44, "compas": 4, "div": 2,
        "grados": [[12, 19, 24, 26], [12, 17, 24, 29],
                   [10, 17, 22, 26], [12, 19, 24, 31]],
        "drone": 1.00, "arpegio": 0.16, "sub": 0.90, "semilla": 4409,
        "descripcion": "Casi sin acordes: dos armonias que se turnan muy "
                       "despacio. Para planos largos y contemplativos.",
    },
    "pulso_lento": {
        "raiz": 61.74, "bpm": 60, "compas": 2, "div": 2,
        "grados": [[12, 15, 19, 22], [10, 15, 19, 24],
                   [8, 15, 20, 24], [7, 14, 19, 22]],
        "drone": 0.80, "arpegio": 0.22, "sub": 1.00, "semilla": 6011,
        "descripcion": "El sub-bajo manda: un latido por segundo bajo un "
                       "colchon tenue. Sostiene sin llamar la atencion.",
    },
    "aurora": {
        "raiz": 65.41, "bpm": 66, "compas": 4, "div": 3,
        "grados": [[12, 16, 19, 23], [14, 17, 21, 26],
                   [9, 16, 21, 24], [11, 14, 19, 23]],
        "drone": 0.90, "arpegio": 0.40, "sub": 0.70, "semilla": 6613,
        "descripcion": "Mayor con septimas y tresillos: luminoso sin ser "
                       "alegre. Para lo que se abre o se descubre.",
    },
    "telemetria": {
        "raiz": 58.27, "bpm": 84, "compas": 4, "div": 4,
        "grados": [[12, 17, 19, 24], [12, 15, 19, 22],
                   [14, 17, 21, 24], [7, 14, 19, 24]],
        "drone": 0.45, "arpegio": 0.65, "sub": 0.60, "semilla": 8419,
        "descripcion": "Arpegio menudo y regular, como un enlace que llega. "
                       "La cama de lo tecnico: datos, orbitas, senales.",
    },
    "cuerdas_frias": {
        "raiz": 51.91, "bpm": 48, "compas": 4, "div": 2,
        "grados": [[12, 15, 22, 27], [10, 15, 20, 27],
                   [8, 15, 20, 24], [12, 17, 22, 24]],
        "drone": 0.45, "arpegio": 0.60, "sub": 0.75, "semilla": 4801,
        "descripcion": "Las cuerdas pulsadas por delante y el colchon "
                       "detras. Intima, casi de camara.",
    },
    "amanecer": {
        "raiz": 73.42, "bpm": 72, "compas": 4, "div": 2,
        "grados": [[12, 16, 19, 24], [10, 14, 17, 22],
                   [5, 12, 17, 21], [7, 14, 19, 23]],
        "drone": 0.95, "arpegio": 0.35, "sub": 0.65, "semilla": 7207,
        "descripcion": "Mayor sencillo y ascendente. Para un cierre o para "
                       "una leccion que termina bien.",
    },
    "marcha": {
        "raiz": 43.65, "bpm": 96, "compas": 4, "div": 2,
        "grados": [[12, 15, 19, 24], [12, 15, 20, 24],
                   [10, 15, 19, 22], [12, 17, 19, 24]],
        "drone": 0.70, "arpegio": 0.30, "sub": 1.00, "semilla": 9601,
        "descripcion": "El pulso mas rapido del banco, todavia por debajo "
                       "de 100 bpm. Empuja sin correr.",
    },
}

BPM_MIN, BPM_MAX = 30, 180


def caracter(cfg: dict) -> str:
    """Las capas encendidas de un tema, de mas fuerte a mas floja."""
    capas = [(cfg[k], n) for k, n in
             (("drone", "drone"), ("arpegio", "arpegio"), ("sub", "sub-bajo"))
             if cfg[k] > 0]
    # Orden estable: a igual nivel manda el orden de declaracion, no el
    # alfabetico. Un desempate por nombre pondria «drone» delante de
    # «arpegio» en un tema cuyo asunto es el arpegio.
    return " + ".join(n for _, n in sorted(capas, key=lambda c: -c[0]))


def catalogo() -> list[dict]:
    """Los temas como los sirve la API (sin numpy del otro lado)."""
    return [{"nombre": n, "bpm": c["bpm"], "raiz": round(c["raiz"], 2),
             "acordes": len(c["grados"]), "caracter": caracter(c),
             "descripcion": c["descripcion"]}
            for n, c in TEMAS.items()]


def _cfg(nombre: str, bpm: float | None = None) -> dict:
    if nombre not in TEMAS:
        raise SystemExit(f"tema desconocido: «{nombre}» "
                         f"(hay {', '.join(TEMAS)})")
    cfg = dict(TEMAS[nombre])
    if bpm:
        bpm = float(bpm)
        if not (BPM_MIN <= bpm <= BPM_MAX):
            raise SystemExit(f"bpm fuera de rango: {bpm}")
        cfg["bpm"] = bpm
    return cfg


# ---------------------------------------------------------------- las capas
def _notas(cfg: dict, acorde: list[int]) -> np.ndarray:
    return cfg["raiz"] * 2.0 ** (np.asarray(acorde, dtype=float) / 12.0)


def _fundamental(cfg: dict, acorde: list[int]) -> float:
    """La nota del sub-bajo: la fundamental del acorde en la octava grave.

    `% 12` a proposito — un acorde escrito dos octavas arriba sigue teniendo
    su raiz abajo, y el sub tiene que quedarse en 40-100 Hz o deja de ser sub.
    """
    return cfg["raiz"] * 2.0 ** ((acorde[0] % 12) / 12.0)


def _drone(cfg: dict, t: np.ndarray, acorde: list[int]) -> np.ndarray:
    """Colchon aditivo de un acorde sobre el reloj ABSOLUTO `t`.

    El vibrato va sumado a la FASE con desviacion fija (~0.18 rad): la
    version que lo multiplica por t hace crecer la desviacion con los
    segundos y suena aspera (feedback del dueno sobre `sfx.pad`, 2026-08-20).
    """
    vib = 0.18 * np.sin(2 * np.pi * 3.1 * t)
    x = np.zeros(len(t))
    for i, f in enumerate(_notas(cfg, acorde)):
        # Dos capas desafinadas 0.25 %: el batido lento (~0.3 Hz a 110 Hz) es
        # lo que hace que el colchon respire. Mas desafine parte el pico
        # espectral de la nota y deja de ser esa nota.
        for det, a in ((1.0, 1.0), (1.0025, 0.85)):
            x += a * np.sin(2 * np.pi * f * det * t + vib + i)
        x += 0.22 * np.sin(2 * np.pi * f * 1.5 * t + vib + i + 1)
        x += 0.10 * np.sin(2 * np.pi * f * 2.0 * t + vib + i + 2)
    return x / (len(acorde) * 2.0)


def _sub(cfg: dict, t: np.ndarray, acorde: list[int]) -> np.ndarray:
    """Sub-bajo articulado a cada tiempo.

    La envolvente es un coseno elevado al cuadrado con suelo: nunca llega a
    cero (un sub que se apaga del todo chasquea) pero baja lo bastante como
    para que la autocorrelacion de la envolvente pique en 60/bpm. Ese es el
    pulso que se puede MEDIR sin escuchar.
    """
    per = 60.0 / cfg["bpm"]
    fase = (0.5 + 0.5 * np.cos(2 * np.pi * t / per)) ** 2
    f = _fundamental(cfg, acorde)
    onda = np.sin(2 * np.pi * f * t) + 0.18 * np.sin(2 * np.pi * f * 2 * t + 1)
    return onda * (0.35 + 0.65 * fase)


def _karplus(f0: float, dur: float, rng: np.random.Generator,
             dec: float = 0.9975) -> np.ndarray:
    """Cuerda pulsada, vectorizada por pasadas de la tabla de onda.

    `sfx.cuerda` recorre la tabla muestra a muestra en Python: para las ~200
    notas de un bloque de 90 s eso son millones de iteraciones. Aqui cada
    pasada entera de la tabla es un `np.roll`, que da la MISMA cuerda salvo
    en la muestra del envolvimiento (donde el bucle leia un valor ya
    actualizado y aqui lee el viejo): una diferencia de un sample por
    periodo, inaudible y determinista.
    """
    N = max(2, int(round(SR / f0)))
    buf = rng.uniform(-1, 1, N)
    for _ in range(2):  # pua de fieltro: sin ataque metalico
        buf = np.convolve(buf, [0.25, 0.5, 0.25], mode="same")
    n = int(dur * SR)
    pasos = n // N + 1
    out = np.empty(pasos * N)
    for k in range(pasos):
        out[k * N:(k + 1) * N] = buf
        buf = dec * 0.5 * (buf + np.roll(buf, -1))
    return out[:n]


# --------------------------------------------------------------- sintesis
def _sintetiza(cfg: dict, n: int, semilla: int, t0: float) -> np.ndarray:
    """`n` muestras de la cama a partir del segundo absoluto `t0`, sin
    normalizar y sin fundidos globales (eso es cosa de quien la escribe).

    Todo se calcula sobre el reloj absoluto: dos tramos contiguos generados
    por separado coinciden muestra a muestra en su solape, que es lo que
    permite sintetizar una pelicula de media hora por bloques sin costuras.
    """
    if n <= 0:
        return np.zeros(0)
    t = t0 + np.arange(n) / SR
    grados = cfg["grados"]
    per_tiempo = 60.0 / cfg["bpm"]
    dur_ac = cfg["compas"] * per_tiempo          # segundos por acorde
    n_ac = max(1, int(round(dur_ac * SR)))
    cruce = min(n_ac // 3, int(0.5 * SR))        # empalme entre acordes

    drone = np.zeros(n) if cfg["drone"] else None
    sub = np.zeros(n) if cfg["sub"] else None

    # ── acordes: segmentos solapados con fundido LINEAL (dos ventanas que
    # suman 1, asi las notas que dos acordes comparten no se cancelan).
    # `k` es el indice ABSOLUTO del acorde: el primero que toca este tramo es
    # el que contiene a t0 (o el anterior, si su cola de empalme llega aqui).
    k = int(np.floor(t0 * SR / n_ac)) - 1
    while True:
        ini = int(round(k * n_ac - t0 * SR))   # en muestras del tramo
        if ini >= n:
            break
        i0, i1 = max(ini, 0), min(ini + n_ac + cruce, n)
        if i1 > i0 and k >= 0:
            acorde = grados[k % len(grados)]
            tt = t[i0:i1]
            w = np.ones(i1 - i0)
            if cruce:
                idx = np.arange(i0, i1)
                if k > 0:  # rampa de entrada (el primer acorde no la lleva)
                    w = np.minimum(w, np.clip((idx - ini) / cruce, 0, 1))
                w = np.minimum(
                    w, np.clip((ini + n_ac + cruce - idx) / cruce, 0, 1))
            if drone is not None:
                drone[i0:i1] += w * _drone(cfg, tt, acorde)
            if sub is not None:
                sub[i0:i1] += w * _sub(cfg, tt, acorde)
        k += 1

    x = np.zeros(n)
    if drone is not None:
        x += cfg["drone"] * drone
    if sub is not None:
        x += cfg["sub"] * sub
    x = _filtra(x, BANDA_LO, BANDA_HI)

    # ── arpegio: cuerdas en las subdivisiones del pulso. Se suma crudo y se
    # filtra una sola vez (un pasabanda por nota costaria una FFT por nota).
    if cfg["arpegio"]:
        arp = np.zeros(n)
        paso = per_tiempo / cfg["div"]
        dur_nota = min(2.4, paso * cfg["div"] * 1.6)
        j0 = int(np.floor(t0 / paso)) - 1
        j = j0
        while True:
            ini = int(round(j * paso * SR - t0 * SR))
            if ini >= n:
                break
            if ini + int(dur_nota * SR) > 0:
                acorde = grados[(j // (cfg["div"] * cfg["compas"]))
                                % len(grados)]
                notas = list(acorde) + [acorde[0] + 12, acorde[1] + 12]
                g = notas[PATRON[j % len(PATRON)] % len(notas)]
                f = cfg["raiz"] * 2.0 ** (g / 12.0)
                rng = np.random.default_rng((int(semilla) * 1000003 + j)
                                            % (2 ** 32))
                nota = _karplus(f, dur_nota, rng)
                nota *= _env(len(nota), 0.006, dur_nota * 0.55)
                # acento en la cabeza del tiempo: sin el, el pulso no se oye
                nota *= 1.0 if j % cfg["div"] == 0 else 0.55
                a, b = max(ini, 0), min(ini + len(nota), n)
                if b > a:
                    arp[a:b] += nota[a - ini:b - ini]
            j += 1
        x += cfg["arpegio"] * 0.75 * _filtra(arp, ARPEGIO_LO, ARPEGIO_HI)

    # Una sola reverberacion para las tres capas: comparten espacio, como en
    # `sfx.mezclar`. Oscura y corta — una cola larga emborrona el pulso.
    return _reverbera(x, 1.6, 0.22)


def _sobre(i0: int, n: int, n_total: int) -> np.ndarray:
    """Tramo [i0, i0+n) de la envolvente global (entrada y caida suaves)."""
    na = min(int(FADE_IN_MAX * SR), int(n_total * FADE_IN_FRAC))
    nc = min(int(FADE_OUT_MAX * SR), int(n_total * FADE_OUT_FRAC))
    idx = np.arange(i0, i0 + n)
    e = np.ones(n)
    if na > 0:
        m = idx < na
        e[m] *= (1 - np.cos(np.pi * idx[m] / na)) / 2
    if nc > 0:
        m = idx >= n_total - nc
        e[m] *= (1 + np.cos(np.pi * (idx[m] - (n_total - nc)) / nc)) / 2
    return e


def tema(nombre: str, dur: float, semilla: int | None = None,
         bpm: float | None = None) -> np.ndarray:
    """La cama de `nombre`, de EXACTAMENTE `dur` segundos, a -3 dBFS.

    La progresion se repite y se recorta donde caiga; la caida final la pone
    la envolvente, no el acorde. Determinista: misma entrada, mismos bytes.
    """
    cfg = _cfg(nombre, bpm)
    n = int(round(float(dur) * SR))
    if n <= 0:
        return np.zeros(0)
    x = _sintetiza(cfg, n, cfg["semilla"] if semilla is None else int(semilla),
                   0.0)
    return _norm(x, 10 ** (PICO / 20)) * _sobre(0, n, n)


def cama(nombre: str, dur: float, db: float = MUSICA_DB,
         bpm: float | None = None, semilla: int | None = None) -> np.ndarray:
    """La cama lista para SUMAR a una mezcla: pico en `db`, extremos mudos."""
    return _norm(tema(nombre, dur, semilla, bpm), 10 ** (float(db) / 20))


# ------------------------------------------- camas largas (una pelicula)
def _bloques(cfg: dict, n_total: int, semilla: int):
    """(i0, tramo) de la cama entera, en bloques de `BLOQUE_S`.

    Cada bloque se sintetiza con `ENTRADILLA_S` de mas por delante y se
    descarta: asi las cuerdas que empezaron antes de la costura y la cola de
    reverberacion estan donde tienen que estar. Como todo se calcula sobre el
    reloj absoluto, el bloque k+1 continua exactamente donde acaba el k.
    """
    n_bloque = int(BLOQUE_S * SR)
    n_ent, n_cola = int(ENTRADILLA_S * SR), int(COLA_S * SR)
    i0 = 0
    while i0 < n_total:
        n = min(n_bloque, n_total - i0)
        ent = 0 if i0 == 0 else n_ent      # el primer bloque no tiene pasado
        x = _sintetiza(cfg, ent + n + n_cola, semilla, (i0 - ent) / SR)
        yield i0, x[ent:ent + n]
        i0 += n


def _ganancia(spec, i0: int, n: int) -> np.ndarray:
    """Tramo de una curva de ganancia lineal muestreada a `hz`."""
    curva, hz = spec
    t = (i0 + np.arange(n)) / SR
    xp = np.arange(len(curva)) / float(hz)
    return np.interp(t, xp, curva)


def escribe_cama(ruta, nombre: str, dur: float, db: float = MUSICA_DB,
                 bpm: float | None = None, semilla: int | None = None,
                 ganancia=None) -> int:
    """Escribe la cama de `dur` segundos en `ruta` (wav 24 kHz mono).

    Por bloques: la pelicula de un curso son ~43 millones de muestras y el
    pasabanda por FFT pediria mas de un giga. Dos pasadas — la primera solo
    mide el pico — porque una escala por bloque haria saltar el nivel en
    cada costura, que es justo lo que se oiria.

    `ganancia` es `(curva, hz)`: la envolvente de *ducking* que baja la
    musica donde habla la voz. Se aplica DESPUES de la escala, asi que el
    pico escrito nunca pasa de `db`.
    """
    cfg = _cfg(nombre, bpm)
    sem = cfg["semilla"] if semilla is None else int(semilla)
    n_total = int(round(float(dur) * SR))
    if n_total <= 0:
        raise SystemExit("una cama de duracion cero no es una cama")
    if n_total <= int(BLOQUE_S * SR):
        escribe_wav(ruta, cama(nombre, dur, db, bpm, semilla)
                    if ganancia is None else
                    cama(nombre, dur, db, bpm, semilla)
                    * _ganancia(ganancia, 0, n_total))
        return n_total

    maximo = max(float(np.max(np.abs(x))) for _, x in
                 _bloques(cfg, n_total, sem))
    k = (10 ** (float(db) / 20)) / (maximo or 1.0)
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        for i0, x in _bloques(cfg, n_total, sem):
            y = x * k * _sobre(i0, len(x), n_total)
            if ganancia is not None:
                y = y * _ganancia(ganancia, i0, len(y))
            w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    return n_total


# ------------------------------------------------------------------- banco
def banco(destino, dur: float = 12.0) -> list[str]:
    """Vista previa audible de cada tema, para elegir oyendo y no leyendo."""
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    for nombre in TEMAS:
        escribe_wav(destino / f"{nombre}.wav", tema(nombre, dur))
    return sorted(TEMAS)


def main(argv):
    orden = argv[1] if len(argv) > 1 else "banco"
    if orden in ("banco", "tema", "aplicar") and not _numpy_sano():
        print("ERROR: este numpy corrompe la sintesis (combo numpy/python no"
              " soportado).\nEjecuta dentro del contenedor manim:\n"
              '  docker run --rm --network none --user $(id -u):$(id -g)'
              ' -v "$PWD":/workspace \\\n    -w /workspace'
              " codeaerospace_contenido-manim python3"
              f" studio/tools/musica.py {orden}")
        return 2
    if orden == "catalogo":
        # Sin canario: no sintetiza nada, solo lee el dict.
        print(json.dumps(catalogo(), indent=1, ensure_ascii=False))
    elif orden == "banco":
        destino = Path(argv[2]) if len(argv) > 2 else BANCO
        nombres = banco(destino)
        print(f"{len(nombres)} temas en {destino}")
    elif orden == "tema":
        nombre, dur, salida = argv[2], float(argv[3]), argv[4]
        escribe_wav(salida, tema(nombre, dur))
        print(f"{salida}  ({dur:.2f} s, {nombre})")
    elif orden == "aplicar":
        video, nombre, db, salida = argv[2], argv[3], float(argv[4]), argv[5]
        total = dur_video(video)
        wav = Path(salida).with_suffix(".wav")
        escribe_cama(wav, nombre, total, db)
        aplicar(video, wav, salida)
        print(f"{salida}  ({total:.2f} s, {nombre} a {db} dBFS)")
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
