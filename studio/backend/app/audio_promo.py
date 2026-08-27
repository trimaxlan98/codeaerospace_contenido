"""Audio de un promo: la cama de sonido y la voz, dentro de la app.

Un promo no lleva subtitulos: si no suena, no comunica. Hasta el sprint P2
el mp4 que servia ManimStudio era el que sale de manim — mudo — y el sonido
se montaba fuera, con `studio/tools/sfx.py` a mano.

Aqui vive lo que la app necesita saber para hacerlo sola:

  - el MANIFIESTO (que sonidos, en que instante, a cuantos dB; y el texto de
    la voz con su instante). Tiene la misma forma que el `promo.json` de los
    promos escritos a mano, para que importarlos luego sea copiar y pegar;
  - la VALIDACION, que rechaza lo que sfx.py no sabria interpretar;
  - los AVISOS, que son la parte cara de aprender: cuanta voz cabe y si la
    voz se pega al final (y entonces el bucle chasquea).

Lo que NO vive aqui: la sintesis (narracion.sintetizar) ni la mezcla
(sfx.py dentro del contenedor). Este modulo es puro y se puede probar sin
Vertex, sin Docker y sin ffmpeg.
"""

import hashlib
import json
import re

# Espejo de `PALETA` en studio/tools/sfx.py: son los unicos nombres que la
# mezcla sabe sintetizar. La UI los ofrece en un desplegable en vez de
# texto libre, y `tests/test_audio_promo.py` compara esta tupla con la
# fuente real (la lee con ast) para que no se separen en silencio.
SONIDOS = (
    "barrido", "aire", "aire_largo",
    "blip_grave", "blip_medio", "blip_agudo", "blip_hud",
    "tick", "pad",
    "cuerda_la2", "cuerda_mi3", "cuerda_la3",
    "nebulosa", "nebulosa_intro", "nebulosa_cierre",
    "subrayado", "sting", "pulso",
)

MAX_EVENTOS = 40
MAX_SECCIONES = 12
MAX_TEXTO = 400

# Medido con Charon sobre los diez primeros promos: 2.3-2.6 silabas por
# segundo CONTANDO las pausas. La media se usa para avisar de cuanta voz
# cabe; no se usa para cortar nada.
SILABAS_POR_S = 2.45
# Si la voz termina a menos de esto del final, el salto del bucle se oye.
COLA_SILENCIO_S = 0.6

# Duracion del formato: mas corto no cuenta nada, mas largo se cae de redes.
# Los mismos numeros que usa `studio/tools/promo_verifica.py` al medir (un
# test compara las dos parejas leyendo el archivo).
DUR_MIN, DUR_MAX = 8.0, 15.0

PICO_DB = -3.0            # cama sola
PICO_DB_CON_VOZ = -16.0   # cama por debajo de la voz
FADE_IN = 0.35
FADE_OUT_S = 0.8          # si no se fija: el fundido cubre el ultimo tramo

VOCALES = "aeiouáéíóúüAEIOUÁÉÍÓÚÜ"
RE_VOZ = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,31}$")


def vacio(voz: str = "Charon") -> dict:
    """Manifiesto en blanco: cama sin eventos y sin voz."""
    return {
        "audio": {"pico_db": PICO_DB, "pico_db_con_voz": PICO_DB_CON_VOZ,
                  "fade_in": FADE_IN, "eventos": []},
        "voz": {"voz": voz, "secciones": []},
    }


def normalizar(manifiesto: dict | None, voz_defecto: str = "Charon") -> dict:
    """Manifiesto completo y ordenado a partir de lo que haya guardado.

    Rellena los valores por defecto y ordena eventos y secciones por tiempo:
    el ensamblador de voz alinea sobre `t_inicio` y una seccion fuera de
    orden empuja a la siguiente (asi se pego la voz al ultimo frame dos
    veces en el lote hecho a mano).
    """
    m = manifiesto or {}
    audio = dict(m.get("audio") or {})
    voz = dict(m.get("voz") or {})

    eventos = []
    for ev in audio.get("eventos") or []:
        if isinstance(ev, dict):
            ev = [ev.get("sonido"), ev.get("t"), ev.get("db")]
        nombre, t, db = (list(ev) + [None, None, None])[:3]
        eventos.append([str(nombre), float(t or 0.0), float(db if db is not None else -14.0)])
    eventos.sort(key=lambda e: e[1])

    secciones = []
    for s in voz.get("secciones") or []:
        secciones.append({"t_inicio": float(s.get("t_inicio") or 0.0),
                          "texto": str(s.get("texto") or "").strip()})
    secciones = [s for s in secciones if s["texto"]]
    secciones.sort(key=lambda s: s["t_inicio"])

    salida = {
        "audio": {
            "pico_db": float(audio.get("pico_db", PICO_DB)),
            "pico_db_con_voz": float(audio.get("pico_db_con_voz", PICO_DB_CON_VOZ)),
            "fade_in": float(audio.get("fade_in", FADE_IN)),
            "eventos": eventos,
        },
        "voz": {"voz": str(voz.get("voz") or voz_defecto), "secciones": secciones},
    }
    fade_out = audio.get("fade_out")
    if fade_out:  # ausente = automatico (los ultimos FADE_OUT_S del video)
        salida["audio"]["fade_out"] = [float(fade_out[0]), float(fade_out[1])]
    return salida


def validar(m: dict) -> list[str]:
    """Errores duros: lo que sfx.py no sabria interpretar. Lista vacia = ok."""
    errores = []
    audio, voz = m["audio"], m["voz"]

    if len(audio["eventos"]) > MAX_EVENTOS:
        errores.append(f"demasiados sonidos ({len(audio['eventos'])}, tope {MAX_EVENTOS})")
    for nombre, t, db in audio["eventos"]:
        if nombre not in SONIDOS:
            errores.append(f"sonido desconocido: «{nombre}»")
        if not (0.0 <= t <= 600.0):
            errores.append(f"instante fuera de rango: {t} s")
        if not (-60.0 <= db <= 6.0):
            errores.append(f"nivel fuera de rango: {db} dB")

    if not (-40.0 <= audio["pico_db"] <= 0.0):
        errores.append("el pico de la cama tiene que estar entre -40 y 0 dBFS")
    if not (-40.0 <= audio["pico_db_con_voz"] <= 0.0):
        errores.append("el pico de la cama con voz tiene que estar entre -40 y 0 dBFS")
    if not (0.0 <= audio["fade_in"] <= 5.0):
        errores.append("el fundido de entrada tiene que estar entre 0 y 5 s")
    fade_out = audio.get("fade_out")
    if fade_out is not None and not (0.0 <= fade_out[0] < fade_out[1]):
        errores.append("el fundido de salida tiene que ser [inicio, fin] con inicio < fin")

    if not RE_VOZ.match(voz["voz"]):
        errores.append(f"nombre de voz invalido: «{voz['voz']}»")
    if len(voz["secciones"]) > MAX_SECCIONES:
        errores.append(f"demasiadas frases ({len(voz['secciones'])}, tope {MAX_SECCIONES})")
    for s in voz["secciones"]:
        if len(s["texto"]) > MAX_TEXTO:
            errores.append(f"frase demasiado larga ({len(s['texto'])} caracteres)")
        if s["t_inicio"] < 0:
            errores.append("una frase empieza antes del segundo 0")
    return errores


def silabas(texto: str) -> int:
    """Silabas aproximadas contando grupos de vocales.

    Aproximacion a proposito: los diptongos cuentan como una (que es lo que
    hace la voz al leerlos) y los hiatos se subestiman. Sirve para avisar de
    cuanta voz cabe, no para escandir un verso.
    """
    grupos, dentro = 0, False
    for c in texto:
        if c in VOCALES:
            if not dentro:
                grupos += 1
                dentro = True
        else:
            dentro = False
    return grupos


def duracion_voz(texto: str) -> float:
    """Segundos que tarda la voz en decir `texto`, a la cadencia medida."""
    return silabas(texto) / SILABAS_POR_S


def avisos(m: dict, dur_video: float | None) -> list[str]:
    """Avisos blandos: no impiden mezclar, pero son los errores que ya se
    cometieron a mano y no se ven hasta escuchar el resultado."""
    fuera = []
    secciones = m["voz"]["secciones"]

    for i, s in enumerate(secciones):
        habla = duracion_voz(s["texto"])
        siguiente = (secciones[i + 1]["t_inicio"] if i + 1 < len(secciones)
                     else (dur_video if dur_video else None))
        if siguiente is not None:
            hueco = siguiente - s["t_inicio"]
            if habla > hueco:
                fuera.append(
                    f"la frase de {s['t_inicio']:.1f} s dura ~{habla:.1f} s y solo"
                    f" tiene {hueco:.1f} s: empujara a la siguiente")

    if dur_video and secciones:
        fin = secciones[-1]["t_inicio"] + duracion_voz(secciones[-1]["texto"])
        if fin > dur_video - COLA_SILENCIO_S:
            fuera.append(
                f"la voz termina hacia {fin:.1f} s y el video dura {dur_video:.1f} s:"
                f" deja al menos {COLA_SILENCIO_S} s de silencio o el bucle chasquea")

    if dur_video:
        for nombre, t, _db in m["audio"]["eventos"]:
            if t >= dur_video:
                fuera.append(f"«{nombre}» empieza en {t:.1f} s, despues del final"
                             f" ({dur_video:.1f} s): no se oira")
    return fuera


def _digest(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def hash_voz(m: dict) -> str:
    """Cambia solo si cambia lo que hay que sintetizar (para no re-pedir TTS)."""
    return _digest(m["voz"])


def hash_mezcla(m: dict, job_id: str) -> str:
    """Cambia si cambia el manifiesto O el video: la mezcla queda vieja."""
    return _digest({"m": m, "job": job_id})


def hash_verificacion(job: dict) -> str:
    """Cambia si cambia el ARCHIVO que se mide: otro render, u otra mezcla.

    Un informe medido sobre el mp4 mudo no vale una vez montado el sonido
    (la mitad de lo que comprueba es el audio), y uno de otro render no vale
    nunca."""
    return _digest({"job": job.get("id"), "audio": job.get("audio_hash") or ""})


def para_sfx(m: dict) -> dict:
    """El `promo.json` que lee `sfx.py promo`.

    Sin `duracion_objetivo`: los tiempos del manifiesto estan escritos sobre
    un video que YA existe, asi que sfx.py no debe reescalarlos.
    """
    return {"audio": m["audio"]}
