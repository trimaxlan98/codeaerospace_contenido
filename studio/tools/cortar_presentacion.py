#!/usr/bin/env python3
"""Parte el render de una presentacion de presentacion en sus fragmentos.

Una presentacion avanza cuando el ponente hace clic. Eso NO se consigue renderizando
la escena N veces: la escena se renderiza UNA vez, `presentacion.paso()` anota el
instante de cada punto de clic, y este script corta ese unico mp4 en esos
instantes. Asi el ultimo fotograma de un fragmento ES el primero del siguiente
(medido: 0.22/255 de diferencia media) y el salto entre slides no se ve.

Corre DENTRO del contenedor manim, que es el unico sitio con ffmpeg. El .pptx
NO se arma aqui: lo arma el backend, que tiene python-pptx y no necesita
ffmpeg. Dividirlo asi evita meter otra dependencia en la imagen de manim.

Uso:
    cortar_presentacion.py <plan.json>

El plan lo escribe el backend; sus rutas son relativas al workspace:

    {
      "proyecto": "Ventana de contacto",
      "raiz": "/workspace",
      "destino": "exports/presentaciones/<project_id>",
      "gif": true,
      "bucle": false,
      "escenas": [
        {"titulo": "El paso del satelite",
         "video": "render_jobs/ab../media/.../Escena.mp4",
         "pasos_json": "render_jobs/ab../media/pasos.json"},
        ...
      ]
    }

La ultima linea de stdout es un JSON con el informe: un fragmento por slide,
con su duracion medida, su peso y su etiqueta.

Solo stdlib: ni numpy ni manim. Igual que `ensamblar.py` y `promo_verifica.py`.
"""

import json
import subprocess
import sys
from pathlib import Path

# Una cola de menos de medio segundo despues del ultimo paso() es el `wait`
# de cortesia con que termina casi toda escena, no un fragmento: un slide de
# dos decimas seria un parpadeo en la sala.
COLA_MINIMA = 0.5

# El GIF se reescala a este ancho. 960 basta para proyectar (el slide se ve a
# 1024-1920 px de ancho reales) y mantiene el deck en pocos MB.
GIF_ANCHO = 960
GIF_FPS = 15


def ff(*args: str) -> None:
    """ffmpeg, callado salvo que falle."""
    proc = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *args],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg fallo: {proc.stderr.strip()[-400:]}")


def ffprobe(video: Path, campos: str) -> str:
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", campos,
         "-of", "default=nw=1:nokey=1", str(video)],
        capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe fallo sobre {video.name}")
    return proc.stdout.strip()


def duracion(video: Path) -> float:
    return float(ffprobe(video, "format=duration").splitlines()[0])


def resolucion(video: Path) -> str:
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height", "-of", "csv=p=0:s=x", str(video)],
        capture_output=True, text=True).stdout.strip()
    return salida or ""


# ── el reparto ───────────────────────────────────────────────────────────────

def leer_pasos(ruta: Path) -> dict:
    """Lo que el render dejo anotado: el lienzo que uso y sus pasos.

    El fondo se LEE de aqui, no se deduce de lo que se pidio: si la escena
    eligio su propio color en el codigo, el slide tiene que pintarse del que
    de verdad se vio.
    """
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        return {"lienzo": datos.get("lienzo") or {},
                "pasos": datos.get("pasos") or []}
    except (OSError, json.JSONDecodeError, AttributeError):
        return {"lienzo": {}, "pasos": []}


def cortes(pasos: list[dict], dur: float) -> list[dict]:
    """Los tramos [inicio, fin] de cada fragmento.

    Cada `paso()` CIERRA un fragmento. Lo que quede despues del ultimo solo
    es fragmento si dura de verdad (>= COLA_MINIMA).
    """
    if not pasos:
        return [{"inicio": 0.0, "fin": dur, "etiqueta": "Completa"}]
    tramos, prev = [], 0.0
    for i, p in enumerate(pasos, start=1):
        t = float(p["t"])
        tramos.append({"inicio": prev, "fin": t,
                       "etiqueta": p.get("etiqueta") or f"Paso {i}"})
        prev = t
    if dur - prev >= COLA_MINIMA:
        tramos.append({"inicio": prev, "fin": dur, "etiqueta": "Cierre"})
    return tramos


def _rel(path: Path, raiz: Path) -> str:
    """Ruta relativa a la raiz, o absoluta si no cuelga de ella."""
    try:
        return str(path.relative_to(raiz))
    except ValueError:
        return str(path)


def hacer_gif(mp4: Path, destino: Path, bucle: bool = False) -> Path:
    """GIF con paleta propia y SIN difuminado.

    Con `dither=bayer` una zona de fondo liso salia con 14 colores y solo el
    25 % de los pixeles en el color exacto. De cerca no se ve, pero al
    reescalar —un proyector, una exportacion a PDF— ese patron se alia y
    aparecen bandas horizontales. Estas presentaciones son dibujo de linea sobre color
    plano: sin difuminar, el 95 % del fondo queda en un unico color y el GIF
    ademas pesa menos.

    Por defecto NO se repite (`-loop -1`): un fragmento tiene que reproducirse
    una vez y quedarse congelado en su estado final, que es la imagen sobre la
    que el ponente sigue hablando. Repetirlo detras de quien habla distrae.
    """
    paleta = destino.with_suffix(".paleta.png")
    filtro = f"fps={GIF_FPS},scale={GIF_ANCHO}:-1:flags=lanczos"
    ff("-i", str(mp4), "-vf", f"{filtro},palettegen=stats_mode=diff",
       str(paleta))
    ff("-i", str(mp4), "-i", str(paleta), "-lavfi",
       f"{filtro} [x]; [x][1:v] paletteuse=dither=none",
       "-loop", "0" if bucle else "-1", str(destino))
    paleta.unlink(missing_ok=True)
    return destino


def fragmentar(video: Path, tramos: list[dict], frag_dir: Path, post_dir: Path,
               prefijo: str, gif: bool, bucle: bool, raiz: Path) -> list[dict]:
    """Corta el mp4 y saca el poster de cada fragmento.

    El poster es el PRIMER fotograma del fragmento, que es el ultimo del
    anterior: en el slide la imagen ya esta puesta antes de que arranque, y el
    salto no se nota.

    Las rutas del informe salen RELATIVAS a `raiz`. Este script corre dentro
    del contenedor, donde la raiz es /workspace; quien lee el informe (el
    backend, para armar el .pptx) esta FUERA, y una ruta absoluta del
    contenedor no existe para el.
    """
    frag_dir.mkdir(parents=True, exist_ok=True)
    post_dir.mkdir(parents=True, exist_ok=True)
    salida = []
    for i, tr in enumerate(tramos, start=1):
        nombre = f"{prefijo}-{i:02d}"
        mp4 = frag_dir / f"{nombre}.mp4"
        # Busqueda de SALIDA (-ss despues de -i): mas lenta que la de entrada
        # pero exacta al fotograma. En un fragmento de segundos la diferencia
        # de tiempo no importa; la de exactitud si, porque de ella depende
        # que el empalme entre slides no se vea.
        ff("-i", str(video), "-ss", f"{tr['inicio']:.3f}",
           "-to", f"{tr['fin']:.3f}", "-c:v", "libx264", "-preset", "medium",
           "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           "-an", str(mp4))
        poster = post_dir / f"{nombre}.png"
        ff("-i", str(mp4), "-frames:v", "1", "-update", "1", str(poster))
        item = {"nombre": nombre, "etiqueta": tr["etiqueta"],
                "inicio": round(tr["inicio"], 3), "fin": round(tr["fin"], 3),
                "duracion": round(duracion(mp4), 3),
                "mp4": _rel(mp4, raiz), "poster": _rel(poster, raiz),
                "peso": mp4.stat().st_size}
        if gif:
            g = hacer_gif(mp4, frag_dir / f"{nombre}.gif", bucle=bucle)
            item["gif"] = _rel(g, raiz)
            item["peso_gif"] = g.stat().st_size
        salida.append(item)
    return salida


# ── main ─────────────────────────────────────────────────────────────────────

def cortar(plan: dict) -> dict:
    raiz = Path(plan.get("raiz") or "/workspace")
    destino = raiz / plan["destino"]
    frag_dir, post_dir = destino / "fragmentos", destino / "posters"
    # Un corte nuevo no puede heredar fragmentos de uno viejo: si la presentacion
    # ahora tiene menos pasos, los sobrantes acabarian en el deck.
    for viejo in list(frag_dir.glob("*")) + list(post_dir.glob("*")):
        viejo.unlink(missing_ok=True)

    escenas, fragmentos, avisos = plan.get("escenas") or [], [], []
    if not escenas:
        return {"ok": False, "error": "el plan no trae ninguna escena"}

    for n, esc in enumerate(escenas, start=1):
        video = raiz / esc["video"]
        if not video.is_file():
            return {"ok": False, "error": f"no existe el video de {esc['titulo']!r}"}
        dur = duracion(video)
        manifiesto = leer_pasos(raiz / esc["pasos_json"]) if esc.get("pasos_json") else {"lienzo": {}, "pasos": []}
        pasos = manifiesto["pasos"]
        if not pasos:
            avisos.append(f"{esc['titulo']}: la escena no llamo a presentacion.paso()"
                          " ni una vez; sale como un solo fragmento")
        tramos = cortes(pasos, dur)
        trozos = fragmentar(video, tramos, frag_dir, post_dir, f"{n:02d}",
                            gif=bool(plan.get("gif", True)),
                            bucle=bool(plan.get("bucle")), raiz=raiz)
        for t in trozos:
            t["escena"] = esc["titulo"]
            t["fondo"] = manifiesto["lienzo"].get("fondo") or ""
        fragmentos.extend(trozos)
        print(f"[{n}/{len(escenas)}] {esc['titulo']}: {len(trozos)} fragmento(s)",
              file=sys.stderr)

    primero = raiz / escenas[0]["video"]
    return {
        "ok": True,
        "proyecto": plan.get("proyecto", ""),
        "total": len(fragmentos),
        "duracion": round(sum(f["duracion"] for f in fragmentos), 3),
        "resolucion": resolucion(primero),
        # El fondo del deck es el de la PRIMERA escena que lo anoto: todas
        # las de un mismo proyecto se renderizan con el mismo.
        "fondo": next((f["fondo"] for f in fragmentos if f["fondo"]), ""),
        "peso": sum(f["peso"] for f in fragmentos),
        "peso_gif": sum(f.get("peso_gif", 0) for f in fragmentos),
        "fragmentos": fragmentos,
        "avisos": avisos,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        plan = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        informe = cortar(plan)
    except Exception as exc:  # noqa: BLE001 - el informe es el canal de error
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    print(json.dumps(informe))
    return 0 if informe.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
