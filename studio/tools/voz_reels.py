#!/usr/bin/env python3
"""Voz en off (TTS local, Piper) para los 3 reels promocionales en loop de 12 s.

Genera, para cada reel, dos mezclas que empalman sin costura a las 12.000 s:
  A «voz libre»   — la voz queda entera entre 0.35 s y 11.4 s.
  B «lazo de frase» — la última frase queda INCOMPLETA y se completa con el principio al repetirse el loop.
Las dos mantienen exactamente 12.000 s, el desfase del reel y el colchón/efectos de sonido_reels.py (que
bajan 9 dB mientras habla, con rampas de ~120 ms).

Uso:   python3 voz_reels.py                  # todo (sintetiza solo lo que falte en studio/content/voz/wav)
       python3 voz_reels.py --resintetizar   # vuelve a sintetizar las voces (Piper no es bit a bit repetible)
       python3 voz_reels.py ReelATP          # solo uno
Salida: studio/content/voz/guiones/<Reel>.md · studio/content/voz/wav/<Reel>_{A,B}_voz.wav (voz sin mezclar,
        circular, 48 kHz mono) · exports/marca-codeaerospace/reels-promo/con_voz/<Reel>_voz{,B}.{wav,mp4}
Requisitos: ver studio/content/voz/LEEME.md (piper-tts y el modelo es_MX-ald-medium en ~/.local/share/piper).
La mezcla es determinista: con los WAV de voz en caché, el resultado es idéntico en cada corrida.
"""
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, resample_poly, sosfilt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sonido_marca as sm                      # noqa: E402
import sonido_reels as sr                      # noqa: E402

SR = sm.SR
RAIZ = Path(__file__).resolve().parents[2]
VOZ = RAIZ / "studio/content/voz"
SALIDA = RAIZ / "exports/marca-codeaerospace/reels-promo"
MODELO = Path.home() / ".local/share/piper/es_MX-ald-medium.onnx"
T = 12.0
DUCK_DB = -9.0            # bajada del colchón y efectos mientras habla
PAUSA_LAZO = 0.40         # pausa en el empalme de la variante B
RAMPA = 0.24              # ancho de la rampa de ducking (Hann): ≈120 ms por lado
LUFS_OBJ, PICO_MAX = -16.0, -2.0

# ── Guiones ───────────────────────────────────────────────────────────────────────────────────────
# Tiempos en segundos DEL VIDEO (t=0 es el primer cuadro; ya incluyen el desfase). `t` = inicio de la frase,
# `tts` = ortografía para el sintetizador (siglas deletreadas), `ls` = length_scale de Piper (<1 = más rápido).
# `ve` = qué se ve en ese momento. En B, la frase con `lazo` lleva `partes` (antes del loop | después).
# Fuentes: redes/fuentes/codeaerospace_plataformas_2026-10-01.txt y servicios; advertencias en redes/carruseles/ESQUEMA.md.

REELS = {
    "ReelOrbitEye": {
        "desfase": 0.0,
        "titulo": "CO.DE Orbit Eye · La cascada",
        "A": [
            dict(t=0.40, ls=0.90, frase="El Doppler dibuja una S.", tts="El Dóppler dibuja una ese.",
                 ve="Leyenda «El Doppler dibuja una S · Rastreo SGP4 y corrección por Hamlib» (hasta 1.5 s); la S asoma en la cascada"),
            dict(t=2.70, ls=0.90, frase="Un VFO la sigue y demodula.", tts="Un V F O la sigue y demodula.",
                 ve="Leyenda «FFT y cascada en vivo · Varios VFO por receptor, cada uno demodula» (1.5–4.5 s); el marco VFO se engancha a la portadora"),
            dict(t=4.95, ls=0.85, frase="Siete decodificadores, de SSTV a Morse.", tts="Siete decodificadores, de S S T V a Morse.",
                 ve="Leyenda «Siete decodificadores · SSTV · AFSK · FSK · GFSK · GMSK · BPSK · Morse» (4.5–7.5 s); cenit del pase hacia 6 s"),
            dict(t=8.20, ls=0.88, frase="Es una demo con grabación IQ.", tts="Es una demo con grabación, i cú.",
                 ve="Leyenda «Graba y reproduce IQ · Formato SigMF» (7.5–10.5 s); chip fijo «Demo con grabación IQ» abajo"),
        ],
        "B": [
            dict(t=2.25, ls=0.90, frase="Un VFO sigue el Doppler.", tts="Un V F O sigue el Dóppler.",
                 ve="Leyenda «FFT y cascada en vivo · Varios VFO por receptor» (1.5–4.5 s); el marco VFO se engancha a la portadora"),
            dict(t=4.20, ls=0.85, frase="Siete decodificadores, de SSTV a Morse.", tts="Siete decodificadores, de S S T V a Morse.",
                 ve="Leyenda «Siete decodificadores…» (4.5–7.5 s); cenit del pase hacia 6 s"),
            dict(t=7.40, ls=0.88, frase="Es una demo con grabación IQ.", tts="Es una demo con grabación, i cú.",
                 ve="Leyenda «Graba y reproduce IQ · Formato SigMF» (7.5–10.5 s); chip «Demo con grabación IQ»"),
            dict(lazo=True, ls=0.90, partes=("Cada pase dibuja,", "una S en la cascada."),
                 tts_partes=("Cada pase dibuja,", "una ese en la cascada."),
                 frase="Cada pase dibuja [loop] una S en la cascada.",
                 ve="Leyenda «El Doppler dibuja una S» (10.5 → 1.5 s, cruza el empalme): la frase cruza el empalme igual que la leyenda"),
        ],
    },
    "ReelATP": {
        "desfase": 4.0,
        "titulo": "CO.DE ATP-DT · ¿0.1° alcanza?",
        "A": [
            dict(t=0.40, ls=0.90, frase="¿Puede una antena apuntar a 0.1 grados?", tts="¿Puede una antena apuntar a cero punto uno grados?",
                 ve="Título fijo «¿Puede una antena apuntar a 0.1°?»; la antena sigue al satélite; chip LQR encendido (0.4–2.6 s)"),
            dict(t=3.40, ls=0.85, frase="Este banco de pruebas, en beta, prueba cinco controladores.", tts="Este banco de pruebas, en beta, prueba cinco controladores.",
                 ve="Chip H∞ (2.6–4.8 s) y luego Lazo abierto (4.8–7.0 s); la traza del error en el osciloscopio con la banda de ±0.1°"),
            dict(t=7.45, ls=0.85, frase="Es un presupuesto de diseño, con trazas ilustrativas.", tts="Es un presupuesto de diseño, con trazas ilustrativas.",
                 ve="La antena se reposiciona (7–8 s); chip PD (7.5–10.2 s); chip ámbar fijo «Trazas ilustrativas»"),
        ],
        "B": [
            dict(t=3.10, ls=0.85, frase="Este banco de pruebas, en beta, prueba cinco controladores.", tts="Este banco de pruebas, en beta, prueba cinco controladores.",
                 ve="Chip H∞ (2.6–4.8 s) y Lazo abierto (4.8–7.0 s); osciloscopio con la banda de ±0.1°"),
            dict(t=7.15, ls=0.85, frase="Es un presupuesto de diseño, con trazas ilustrativas.", tts="Es un presupuesto de diseño, con trazas ilustrativas.",
                 ve="Reposicionamiento (7–8 s) y chip PD (7.5–10.2 s); chip ámbar «Trazas ilustrativas»"),
            dict(lazo=True, ls=0.85, partes=("Y la pregunta es:", "¿puede una antena apuntar a 0.1 grados?"),
                 tts_partes=("Y la pregunta es:", "¿puede una antena apuntar a cero punto uno grados?"),
                 frase="Y la pregunta es: [loop] ¿puede una antena apuntar a 0.1 grados?",
                 ve="Chip PID (10.2–12.4 s) → al repetirse, título «¿Puede una antena apuntar a 0.1°?» con la antena siguiendo"),
        ],
    },
    "ReelModelo": {
        "desfase": 0.0,
        "titulo": "El modelo CO.DE",
        "A": [
            dict(t=0.40, ls=0.84, frase="Proyectos digitales a la medida.", tts="Proyectos digitales a la medida.",
                 ve="Título «El modelo CO.DE»; nodo «CO.DE Strategy» encendido y leyenda «Proyectos digitales a la medida» (10–2 s); el pulso sale del nodo de arriba"),
            dict(t=2.70, ls=0.84, frase="Cada proyecto digital financia investigación aeroespacial real.", tts="Cada proyecto digital financia investigación aeroespacial real.",
                 ve="El pulso llega a «CO.DE Aerospace» (4 s); leyenda «Investigación espacial real» (2–6 s); etiqueta «financian»"),
            dict(t=7.10, ls=0.84, frase="Y las plataformas están en línea, no son maquetas.", tts="Y las plataformas están en línea, no son maquetas.",
                 ve="Leyenda «Plataformas en línea, no maquetas» (6–10 s); nodo «Plataformas» encendido (8 s)"),
        ],
        "B": [
            dict(t=2.90, ls=0.84, frase="Cada proyecto digital financia investigación aeroespacial real.", tts="Cada proyecto digital financia investigación aeroespacial real.",
                 ve="Nodo «CO.DE Aerospace» y leyenda «Investigación espacial real» (2–6 s); etiqueta «financian»"),
            dict(t=7.30, ls=0.84, frase="Y las plataformas están en línea, no son maquetas.", tts="Y las plataformas están en línea, no son maquetas.",
                 ve="Leyenda «Plataformas en línea, no maquetas» (6–10 s); nodo «Plataformas» (8 s)"),
            dict(lazo=True, ls=0.84, partes=("Y todo parte de", "proyectos digitales a la medida."),
                 tts_partes=("Y todo parte de", "proyectos digitales a la medida."),
                 frase="Y todo parte de [loop] proyectos digitales a la medida.",
                 ve="Nodo «Plataformas» (hasta 10 s), luego «CO.DE Strategy» y leyenda «Proyectos digitales a la medida» (10 → 2 s, cruza el empalme)"),
        ],
    },
}


# ── Síntesis ──────────────────────────────────────────────────────────────────────────────────────

_voz = None


def sintetizar(texto, ls):
    """Piper (local). Devuelve audio float mono a 48 kHz."""
    global _voz
    if _voz is None:
        from piper import PiperVoice
        if not MODELO.exists():
            sys.exit(f"Falta el modelo {MODELO}. Ver studio/content/voz/LEEME.md")
        _voz = PiperVoice.load(str(MODELO))
    from piper import SynthesisConfig
    cfg = SynthesisConfig(length_scale=ls, noise_scale=0.55, noise_w_scale=0.6, normalize_audio=True)
    x = np.concatenate([c.audio_float_array for c in _voz.synthesize(texto, cfg)])
    return resample_poly(x, 320, 147).astype(np.float64)       # 22 050 → 48 000


def leer_mono(ruta):
    w = wave.open(str(ruta))
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768


def escribir_mono(ruta, x):
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def frase_wav(nombre, variante, i, texto, ls, forzar):
    """Voz de una frase, en caché (studio/content/voz/wav/frases/)."""
    ruta = VOZ / "wav/frases" / f"{nombre}_{variante}{i}.wav"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    meta = ruta.with_suffix(".json")
    if forzar or not ruta.exists() or not meta.exists() or json.loads(meta.read_text()) != dict(texto=texto, ls=ls):
        escribir_mono(ruta, sintetizar(texto, ls))
        meta.write_text(json.dumps(dict(texto=texto, ls=ls), ensure_ascii=False))
    return leer_mono(ruta)


def recortar(x, umbral_db=-45):
    """Quita el silencio de los extremos (deja 10 ms)."""
    e = np.abs(x) > 10 ** (umbral_db / 20)
    idx = np.flatnonzero(e)
    a, b = max(idx[0] - int(0.01 * SR), 0), min(idx[-1] + int(0.01 * SR), len(x))
    return x[a:b]


def punto_de_corte(x, objetivo):
    """Muestra de mínima energía (ventanas de 30 ms) en ±12 % alrededor de `objetivo` (fracción 0–1): el
    límite entre las dos palabras donde cae el empalme del loop."""
    v, h = int(0.03 * SR), int(0.005 * SR)
    lo, hi = int((objetivo - 0.12) * len(x)), int((objetivo + 0.12) * len(x))
    pos = np.arange(lo, hi - v, h)
    rms = np.array([np.sqrt((x[i:i + v] ** 2).mean()) for i in pos])
    k = int(np.argmin(rms))
    return pos[k] + v // 2, 20 * np.log10(max(rms[k], 1e-9))


def acondicionar(x):
    """Filtro pasa-altas (80 Hz), ligera compresión y nivel de habla ≈ −16 dBFS RMS."""
    x = sosfilt(butter(2, 80, "hp", fs=SR, output="sos"), x)
    rms = np.sqrt((x ** 2).mean())
    x = x * 10 ** (-16 / 20) / rms
    return np.tanh(x * 1.6) / 1.6                                # compresión suave de picos


def fundido(x, ms=8):
    n = int(ms / 1000 * SR)
    x = x.copy()
    x[:n] *= np.linspace(0, 1, n)
    x[-n:] *= np.linspace(1, 0, n)
    return x


def circular_poner(buf, t, x):
    n = len(buf)
    i = int(round((t % T) * SR))
    primero = min(len(x), n - i)
    buf[i:i + primero] += x[:primero]
    buf[: len(x) - primero] += x[primero:]


def pista_voz(nombre, variante, frases, forzar):
    """Pista circular de voz (mono, 12 s). Devuelve (pista, eventos[(ini, fin, frase)])."""
    n = int(T * SR)
    pista = np.zeros(n)
    ev = []
    for i, f in enumerate(frases):
        if f.get("lazo"):
            texto = f["tts_partes"][0] + " " + f["tts_partes"][1]
            x = recortar(frase_wav(nombre, variante, i, texto, f["ls"], forzar))
            c, nivel = punto_de_corte(x, len(f["tts_partes"][0]) / len(texto))
            izq, der = fundido(recortar(x[:c]), 10), fundido(recortar(x[c:]), 10)
            # Pausa de PAUSA_LAZO s exactos en el empalme: la 2.ª parte empieza en 0.25 s y la 1.ª termina en 11.85 s.
            x = acondicionar(np.r_[izq, np.zeros(int(PAUSA_LAZO * SR)), der])
            t0 = 0.25 - (len(izq) + int(PAUSA_LAZO * SR)) / SR
            circular_poner(pista, t0, x)
            f["_corte"] = (c / SR, nivel)
            ev.append((t0 % T, (t0 + len(x) / SR) % T, f["frase"], t0 + len(izq) / SR))
            continue
        x = fundido(acondicionar(recortar(frase_wav(nombre, variante, i, f["tts"], f["ls"], forzar))))
        circular_poner(pista, f["t"], x)
        ev.append((f["t"], f["t"] + len(x) / SR, f["frase"], None))
    return pista, ev


# ── Mezcla ────────────────────────────────────────────────────────────────────────────────────────

def base_sonido(nombre):
    """Colchón + efectos del reel (idéntico a con_sonido/<Reel>.wav), sin recodificar."""
    import zlib
    f, Tr, desfase = sr.REELS[nombre]
    semilla = zlib.crc32(nombre.encode())
    sr.RNG = np.random.default_rng(semilla)
    sm.RNG = np.random.default_rng(semilla + 1)
    m = sr.Circular(Tr)
    f(m)
    return sr.master(m, desfase)


def conv_circ(x, k):
    """Convolución circular (el borde final enlaza con el inicial)."""
    p = len(k) // 2
    return fftconvolve(np.r_[x[-p:], x, x[:p]], k, "valid")[: len(x)]


def mascara_duck(pista):
    """Ganancia circular del colchón: 1 sin voz, DUCK_DB mientras hay voz (rampas Hann de ≈120 ms por lado)."""
    paso = int(0.02 * SR)
    env = np.sqrt(np.maximum(conv_circ(pista ** 2, np.ones(paso + 1) / (paso + 1)), 0))
    activo = (env > 10 ** (-48 / 20)).astype(float)
    h = int(0.20 * SR)                                         # cierra pausas < 400 ms entre palabras
    dil = (conv_circ(activo, np.ones(2 * h + 1)) > 0).astype(float)
    cerrado = (conv_circ(dil, np.ones(2 * h + 1)) >= 2 * h + 1 - 0.5).astype(float)
    d = int(0.06 * SR)                                         # margen de 60 ms antes y después
    m = (conv_circ(cerrado, np.ones(2 * d + 1)) > 0).astype(float)
    w = np.hanning(int(RAMPA * SR) | 1)
    suave = conv_circ(m, w / w.sum())
    return 1.0 + (10 ** (DUCK_DB / 20) - 1.0) * suave


def medir(x):
    """(LUFS integrado, pico real dBTP) con ffmpeg ebur128 sobre el arreglo estéreo."""
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
    r = subprocess.run(["ffmpeg", "-nostats", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af",
                        "ebur128=peak=true", "-f", "null", "-"], input=pcm, capture_output=True)
    txt = r.stderr.decode()
    bloque = txt[txt.rfind("Summary:"):]
    return (float(re.search(r"I:\s+(-?[\d.]+) LUFS", bloque).group(1)),
            float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", bloque).group(1)))


def nivelar(x):
    """Lleva a −16 LUFS con pico real ≤ −2 dBTP (limitador suave y circular; sin recortes duros)."""
    for _ in range(8):
        lufs, pico = medir(x)
        if abs(lufs - LUFS_OBJ) < 0.15 and pico <= PICO_MAX:
            break
        x = x * 10 ** ((LUFS_OBJ - lufs) / 20)
        pk = np.abs(x).max()
        lim = 10 ** ((PICO_MAX - 0.5) / 20)
        if pk > lim:                                           # compresión tanh solo por encima del umbral
            u = 0.7 * lim
            mag = np.abs(x)
            sobre = mag > u
            x = np.where(sobre, np.sign(x) * (u + (lim - u) * np.tanh((mag - u) / (lim - u))), x)
    return x


def validar(nombre, variante, ev):
    """Avisa si las frases se pisan (< 120 ms de hueco) o si A se sale de 0.35–11.4 s."""
    sin_lazo = sorted((e for e in ev if e[3] is None), key=lambda e: e[0])
    for a, b in zip(sin_lazo, sin_lazo[1:]):
        if b[0] - a[1] < 0.12:
            print(f"  AVISO {nombre} {variante}: «{a[2]}» termina {a[1]:.2f} y «{b[2]}» empieza {b[0]:.2f}")
    for e in sin_lazo:
        if e[0] < 0.35 or e[1] > 11.4:
            print(f"  AVISO {nombre} {variante}: «{e[2]}» fuera de 0.35–11.4 s ({e[0]:.2f}–{e[1]:.2f})")
    for ini, fin, _, _ in (e for e in ev if e[3] is not None):
        if not (ini > 9.5 and fin < 4.0):
            print(f"  AVISO {nombre} {variante}: revisar el lazo ({ini:.2f} → {fin:.2f})")
        for o in sin_lazo:
            if (o[0] < 6 and o[0] - fin < 0.12) or (o[1] > 6 and ini - o[1] < 0.12):
                print(f"  AVISO {nombre} {variante}: «{o[2]}» choca con el lazo")


def mezclar(nombre, variante, frases, forzar):
    desfase = REELS[nombre]["desfase"]
    voz, ev = pista_voz(nombre, variante, frases, forzar)
    validar(nombre, variante, ev)
    base = base_sonido(nombre)
    duck = mascara_duck(voz)
    mezcla = base * duck[:, None] + voz[:, None] * np.array([[1.0, 1.0]])
    mezcla = nivelar(mezcla)
    return mezcla, voz, base, duck, ev


def escribir_estereo(ruta, x):
    sm.escribir_wav(ruta, x)


def muxar(nombre, wav, salida):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(SALIDA / f"{nombre}.mp4"), "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-shortest", "-movflags", "+faststart", str(salida)], check=True)


def tabla_md(nombre, ev_a, ev_b):
    r = REELS[nombre]

    def filas(frases, ev):
        out = []
        for f, e in zip(frases, ev):
            ini, fin = e[0], e[1]
            t = f"{ini:.2f} → {fin:.2f}" if not f.get("lazo") else f"{ini:.2f} → 12.00 | 0.00 → {fin:.2f}"
            if f.get("lazo"):
                t = f"{ini:.2f} → (empalme) → {fin:.2f}"
            out.append(f"| {t} | {f['frase']} | {f['ve']} |")
        return "\n".join(out)
    cab = "| Tiempo (s) | Frase (lo que se dice) | Qué se ve |\n|---|---|---|"
    palabras = lambda fr: sum(len(re.sub(r"\[loop\]", "", f["frase"]).split()) for f in fr)
    return f"""# Guion de voz · {r['titulo']}  ({nombre}.mp4, 12.000 s, loop)

Tiempos en segundos del VIDEO (t = 0 es el primer cuadro; el desfase del reel ya está aplicado).
Voz: Piper `es_MX-ald-medium` (ver `LEEME.md`). Si grabas tú, respeta los tiempos de inicio: el video no cambia.
Estilo: español neutro, tuteo, claro y entusiasta sin exagerar, ritmo de unas 2 palabras por segundo.
Siglas: se leen por letras (V-F-O, S-S-T-V, I-Q).

## Variante A · «voz libre» ({palabras(r['A'])} palabras; la voz cabe entre 0.35 s y 11.4 s)

{cab}
{filas(r['A'], ev_a)}

## Variante B · «lazo de frase» ({palabras(r['B'])} palabras; la última frase se completa con la primera al repetirse el loop)

{cab}
{filas(r['B'], ev_b)}

**Cómo grabar la B:** di la última frase hasta el corte («[loop]»), deja correr la grabación por el empalme de las
12.000 s y retoma la misma frase al volver a empezar. Si grabas en una sola toma, empieza la frase en el segundo
indicado y deja que cruce el final del archivo.

## Reglas de honestidad que respeta este guion

{r.get('reglas', '')}"""


REGLAS = {
    "ReelOrbitEye": "- Orbit Eye NO tiene receptor de radio conectado: se dice «demo con grabación IQ», nunca «en vivo».\n- Los siete decodificadores y SigMF son del código (fuente: plataformas, 2026-10-01).",
    "ReelATP": "- ATP-DT es beta; 0.1° es un presupuesto de diseño (no un resultado medido).\n- Las curvas del osciloscopio son ilustrativas, y así se dice.",
    "ReelModelo": "- «Cada proyecto digital de CO.DE Strategy financia investigación aeroespacial real» es cita de codeaerospace.com/services.\n- «Plataformas en línea, no maquetas» es de codeaerospace.com/plataformas.\n- Sin cifras ni nombres de clientes.",
}


def procesar(nombre, forzar):
    SALIDA_V = SALIDA / "con_voz"
    SALIDA_V.mkdir(exist_ok=True)
    res = {}
    for var, sufijo in (("A", ""), ("B", "B")):
        frases = REELS[nombre][var]
        mezcla, voz, base, duck, ev = mezclar(nombre, var, frases, forzar)
        wav = SALIDA_V / f"{nombre}_voz{sufijo}.wav"
        escribir_estereo(wav, mezcla)
        muxar(nombre, wav, SALIDA_V / f"{nombre}_voz{sufijo}.mp4")
        escribir_mono(VOZ / "wav" / f"{nombre}_{var}_voz.wav", voz)
        res[var] = (ev, mezcla, voz, base, duck)
        print("ok", nombre, var, f"{len(mezcla) / SR:.3f}s")
    for k, v in REGLAS.items():
        REELS[k]["reglas"] = v
    (VOZ / "guiones").mkdir(parents=True, exist_ok=True)
    (VOZ / "guiones" / f"{nombre}.md").write_text(tabla_md(nombre, res["A"][0], res["B"][0]) + "\n", encoding="utf-8")
    return res


def verificar(nombre, res):
    """Costura, nivel, duración y choque voz/efectos de cada mezcla (sin oír)."""
    for var, sufijo in (("A", ""), ("B", "B")):
        ev, mezcla, voz, base, duck = res[var]
        x = mezcla
        paso = np.percentile(np.abs(np.diff(x, axis=0)).max(1), 99)
        costura = np.abs(x[0] - x[-1]).max()
        lufs, pico = medir(x)
        # energía de la voz frente al colchón/efectos YA bajados, en ventanas de 100 ms con voz
        v = int(0.1 * SR)
        n = len(voz) // v
        rv = np.array([np.sqrt((voz[i * v:(i + 1) * v] ** 2).mean()) for i in range(n)])
        bb = base * duck[:, None]
        rb = np.array([np.sqrt((bb[i * v:(i + 1) * v] ** 2).mean()) for i in range(n)])
        con = rv > 10 ** (-28 / 20)
        margen = 20 * np.log10(rv[con] / np.maximum(rb[con], 1e-9))
        peor = np.percentile(margen, 10)
        # el colchón sin voz vs con voz: bajada efectiva
        bajada = 20 * np.log10(np.maximum(np.sqrt((bb[con.repeat(v)[:len(bb)] if False else slice(None)] ** 2).mean()), 1e-9)
                                / np.sqrt((base ** 2).mean()))
        ini = np.flatnonzero(con)
        durmp4 = float(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                                "stream=duration", "-of", "csv=p=0", str(SALIDA / "con_voz" / f"{nombre}_voz{sufijo}.mp4")]))
        print(f"{nombre}_voz{sufijo}: dur WAV {len(x) / SR:.6f}s · MP4 video {durmp4:.3f}s · costura {costura:.4f} "
              f"(paso p99 {paso:.4f}) {'OK' if costura <= paso else 'CLIC'} · {lufs:.1f} LUFS · pico {pico:.2f} dBTP · "
              f"voz sobre efectos+colchón: p10 {peor:.1f} dB, mediana {np.median(margen):.1f} dB · "
              f"1.ª voz {ini[0] * 0.1:.1f}s, última {(ini[-1] + 1) * 0.1:.1f}s")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    forzar = "--resintetizar" in sys.argv
    for nombre in (args or REELS):
        res = procesar(nombre, forzar)
        verificar(nombre, res)


if __name__ == "__main__":
    main()
