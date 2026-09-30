"""Constructor común de las dos presentaciones de tesis (seminario de divulgación y comité tutorial).

Cada presentación es un módulo con `CFG` (título, lema, archivos de salida, ritmo) y `DIAPOS`.
No renderiza videos: incrusta los mp4 de exports/<archivo>/<tema>/ y les pone título y subtítulo en la
diapositiva; el guion completo va en las notas del orador y en un .md con hora estimada por diapositiva.
El póster de cada video sale de su propio mp4 (fotograma al 60 %), sin depender de los PNG 8K.

Tipos de diapositiva (tuplas):
  ("portada", guion)
  ("seccion", titulo, subtitulo, guion)
  ("video",   pieza, titulo, subtitulo, guion[, cuidado])
  ("texto",   titulo, subtitulo, [viñetas], guion[, cuidado])
  ("cita",    frase, subfrase, guion[, cuidado])            # una sola afirmación grande
  ("cierre",  guion)
  ("respaldo", titulo, subtitulo, [viñetas], guion[, cuidado])  # fuera del tiempo; para preguntas
`cuidado` = advertencia de «lo que no se puede afirmar»: va en las notas y en el .md, nunca en la diapositiva.
"""
import io
import subprocess
import sys
from pathlib import Path

import numpy as np

from PIL import Image
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

sys.path.insert(0, str(Path(__file__).parent))
from catalogo_tesis import BLOQUES  # noqa: E402
from empaquetar_ponencia import ACENTO, EXP, FONDO, H, TINTA, W, diapositiva, nombre_legible, nueva, texto  # noqa: E402

CARPETA = {p[0]: c for _, c, ps in BLOQUES for p in ps}
MUESTRA = {p[0]: p[1] for _, _, ps in BLOQUES for p in ps}
TIPOS_CON_GUION_ULTIMO = {"portada", "seccion", "video", "texto", "cita", "cierre", "respaldo"}


def palabras(t):
    return len(t.split())


def guion_de(d):
    """Texto hablado de la diapositiva y advertencia opcional."""
    t = d[0]
    n = {"portada": 1, "seccion": 3, "video": 4, "texto": 4, "cita": 3, "cierre": 1, "respaldo": 4}[t]
    g = d[n]
    cuidado = d[n + 1] if len(d) > n + 1 else ""
    return g, cuidado


def minutos(d, ritmo):
    return 0.0 if d[0] == "respaldo" else palabras(guion_de(d)[0]) / ritmo


def _duracion(mp4):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)]).decode().strip())


def video_final(tema, clase, carpeta=None):
    """Copia del video SIN el fundido final (`cierre()` deja la pantalla en blanco): termina en el último cuadro legible.

    PowerPoint deja visible el último cuadro al terminar, así que la diapositiva se queda con la imagen completa
    en vez de un fondo vacío. El original no se toca; la copia va en exports/<archivo>/<tema>_final/ (se reutiliza).
    """
    carpeta = carpeta or CARPETA[clase]
    src = EXP / carpeta / tema / f"{clase}.mp4"
    dst = EXP / carpeta / f"{tema}_final" / f"{clase}.mp4"
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    dur = _duracion(src)
    fps, w, h, ventana = 10, 192, 108, 4.0
    ini = max(0.0, dur - ventana)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ini:.2f}", "-i", str(src), "-vf", f"fps={fps},scale={w}:{h}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).astype(int)
    fondo = a[-1, 0, 0]  # la última esquina es el fondo limpio del tema
    contenido = (np.abs(a - fondo).sum(-1) > 30).mean((1, 2))
    pico = contenido.max()
    if pico < 0.01:  # sin contenido al final: no se recorta
        fin = dur
    else:
        ok = np.nonzero(contenido >= 0.985 * pico)[0]
        fin = min(dur, ini + (ok[-1] + 1) / fps)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-t", f"{fin:.2f}", "-an", "-c:v", "libx264", "-crf", "17",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dst)], check=True)
    return dst


def poster_de_video(tema, clase, carpeta=None):
    """Fotograma opaco 1920x1080 = último cuadro legible del video (la diapositiva se ve completa antes y después de reproducir)."""
    mp4 = video_final(tema, clase, carpeta)
    png = subprocess.run(
        ["ffmpeg", "-v", "error", "-sseof", "-0.1", "-i", str(mp4), "-frames:v", "1", "-f", "image2pipe",
         "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    im = Image.open(io.BytesIO(png)).convert("RGB")
    b = io.BytesIO()
    im.save(b, "JPEG", quality=88)
    b.seek(0)
    return b


def subtexto(s, tema, txt, x, y, w, tam=20):
    return texto(s, txt, x, y, w, Inches(0.6), tam, ACENTO[tema])


def pie(s, tema, cfg, n, total):
    texto(s, cfg["pie"], Inches(0.6), Inches(7.05), Inches(9), Inches(0.35), 12, TINTA[tema])
    tb = texto(s, f"{n} / {total}", Inches(11.4), Inches(7.05), Inches(1.4), Inches(0.35), 12, TINTA[tema])
    tb.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT


def notas(s, d, extra=""):
    g, cuidado = guion_de(d)
    t = g
    if cuidado:
        t += f"\n\n⚠️ CUIDADO: {cuidado}"
    s.notes_slide.notes_text_frame.text = t + extra


def hacer(prs, tema, d, n, total, num_seccion, cfg):
    tipo = d[0]
    s = diapositiva(prs, tema)
    if tipo == "portada":
        texto(s, cfg["kicker"], Inches(0.9), Inches(1.2), Inches(11.5), Inches(0.6), 22, ACENTO[tema], True)
        texto(s, cfg["titulo"], Inches(0.9), Inches(1.9), Inches(11.6), Inches(2.0), cfg["tam_titulo"], TINTA[tema], True)
        texto(s, cfg["lema"], Inches(0.9), Inches(4.1), Inches(11.5), Inches(1.4), 30, ACENTO[tema])
        texto(s, cfg["autor"], Inches(0.9), Inches(5.7), Inches(11.5), Inches(0.6), 24, TINTA[tema])
        texto(s, cfg["instit"], Inches(0.9), Inches(6.25), Inches(11.5), Inches(0.6), 18, TINTA[tema])
        notas(s, d)
        return s
    if tipo == "seccion":
        _, titulo, sub, _g = d[:4]
        texto(s, f"{num_seccion:02d}", Inches(0.9), Inches(2.0), Inches(4), Inches(1.2), 54, ACENTO[tema], True)
        texto(s, titulo, Inches(0.9), Inches(3.1), Inches(11.5), Inches(1.6), 42, TINTA[tema], True)
        subtexto(s, tema, sub, Inches(0.9), Inches(4.9), Inches(11.5), 26)
    elif tipo == "video":
        _, clase, titulo, sub = d[:4]
        assert (EXP / CARPETA[clase] / tema / f"{clase}.mp4").exists(), clase
        mp4 = video_final(tema, clase)
        texto(s, titulo, Inches(0.6), Inches(0.22), Inches(12.1), Inches(0.75), 28, TINTA[tema], True)
        subtexto(s, tema, sub, Inches(0.6), Inches(0.9), Inches(12.1), 19)
        vh = Inches(5.5)
        vw = int(vh * 16 / 9)
        s.shapes.add_movie(str(mp4), int((W - vw) / 2), Inches(1.5), vw, vh,
                           poster_frame_image=poster_de_video(tema, clase), mime_type="video/mp4")
        pie(s, tema, cfg, n, total)
        notas(s, d, f"\n\n(Video: {nombre_legible(clase)} — {MUESTRA[clase]}. Clic para reproducir; al terminar queda el último cuadro.)")
        return s
    elif tipo in ("texto", "respaldo"):
        _, titulo, sub, puntos = d[:4]
        if tipo == "respaldo":
            texto(s, "RESPALDO", Inches(0.7), Inches(0.12), Inches(4), Inches(0.4), 14, ACENTO[tema], True)
        largo = len(titulo) > 50  # un título de dos líneas baja el subtítulo y las viñetas
        texto(s, titulo, Inches(0.7), Inches(0.4), Inches(12), Inches(1.1), 28 if largo else 34, TINTA[tema], True)
        subtexto(s, tema, sub, Inches(0.7), Inches(1.65 if largo else 1.3), Inches(12), 22)
        tb = s.shapes.add_textbox(Inches(0.7), Inches(2.6 if largo else 2.2), Inches(11.9), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True
        for i, t in enumerate(puntos):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_after = Pt(16)
            r = p.add_run()
            r.text = "▪ " + t
            r.font.size, r.font.name = Pt(24), "Carlito"
            r.font.color.rgb = TINTA[tema]
    elif tipo == "cita":
        _, frase, sub, _g = d[:4]
        larga = len(frase) > 100  # la pregunta de investigación es larga: letra menor y subtítulo más abajo
        texto(s, frase, Inches(0.9), Inches(1.3 if larga else 1.9), Inches(11.5), Inches(4.0 if larga else 2.8), 32 if larga else 44, TINTA[tema], True)
        if sub:
            subtexto(s, tema, sub, Inches(0.9), Inches(5.6 if larga else 4.9), Inches(11.5), 28)
    elif tipo == "cierre":
        texto(s, cfg["cierre_titulo"], Inches(0.9), Inches(2.2), Inches(11.5), Inches(1.8), 46, TINTA[tema], True)
        subtexto(s, tema, "Gracias · Preguntas", Inches(0.9), Inches(4.4), Inches(11.5), 30)
        texto(s, f'{cfg["autor"]}  ·  {cfg["instit"]}', Inches(0.9), Inches(6.3), Inches(11.5), Inches(0.6), 18, TINTA[tema])
    if tipo != "cierre":
        pie(s, tema, cfg, n, total)
    notas(s, d)
    return s


def titulo_de(d):
    return {"portada": lambda: "Portada", "seccion": lambda: d[1], "video": lambda: d[2], "texto": lambda: d[1],
            "cita": lambda: d[1], "cierre": lambda: "Cierre", "respaldo": lambda: "Respaldo · " + d[1]}[d[0]]()


def guion_md(cfg, diapos):
    ritmo = cfg["ritmo"]
    principales = [d for d in diapos if d[0] != "respaldo"]
    tot = sum(minutos(d, ritmo) for d in principales)
    pal = sum(palabras(guion_de(d)[0]) for d in principales)
    L = [f"# Guion — {cfg['titulo_plano']}", "",
         f"**{cfg['autor']}** · {cfg['instit']}. Ritmo {ritmo} palabras/min → **{tot:.1f} min** de guion "
         f"({pal} palabras, {len(principales)} diapositivas), más {sum(1 for d in diapos if d[0] == 'respaldo')} "
         f"diapositivas de respaldo para preguntas (fuera del tiempo).", "",
         cfg["nota_md"], "",
         "Los videos ya existen y arrancan con clic; duran 13–27 s y se puede seguir hablando sobre el último cuadro. "
         "Las líneas ⚠️ son advertencias de lo que **no** se puede afirmar: van también en las notas del orador.", "",
         "| # | Hora | Diapositiva |", "|---|---|---|"]
    t, filas, cuerpo, n = 0.0, [], [], 0
    for d in diapos:
        n += 1
        titulo = titulo_de(d)
        if d[0] == "respaldo":
            filas.append(f"| {n} | — | {titulo} |")
            h = "respaldo"
        else:
            h = f"{int(t)}:{int((t % 1) * 60):02d}"
            filas.append(f"| {n} | {h} | {titulo} |")
        g, cuidado = guion_de(d)
        sub = d[3] if d[0] == "video" else d[2] if d[0] in ("seccion", "texto", "cita", "respaldo") else ""
        cuerpo += [f"## {n}. {titulo}", f"*{sub}*  ·  {h}" + (f"  ·  video `{d[1]}`" if d[0] == "video" else ""), "", g, ""]
        if cuidado:
            cuerpo += [f"> ⚠️ **Cuidado:** {cuidado}", ""]
        t += minutos(d, ritmo)
    return "\n".join(L + filas + [""] + cuerpo)


def construir(cfg, diapos, tema):
    prs = nueva(tema)
    total = len(diapos)
    sec = 0
    for n, d in enumerate(diapos, 1):
        if d[0] == "seccion":
            sec += 1
        hacer(prs, tema, d, n, total, sec, cfg)
    destino = EXP / "presentaciones" / f"{cfg['archivo']}_{tema}.pptx"
    prs.save(destino)
    print(destino.name, len(prs.slides), "diapositivas", f"{destino.stat().st_size / 1e6:.0f} MB")


def main(cfg, diapos):
    principales = [d for d in diapos if d[0] != "respaldo"]
    tot = sum(minutos(d, cfg["ritmo"]) for d in principales)
    print(f"{len(principales)} diapositivas + {len(diapos) - len(principales)} de respaldo · "
          f"{sum(palabras(guion_de(d)[0]) for d in principales)} palabras · {tot:.1f} min a {cfg['ritmo']} ppm")
    (EXP / "presentaciones").mkdir(parents=True, exist_ok=True)
    (EXP / cfg["guion"]).write_text(guion_md(cfg, diapos), encoding="utf-8")
    usadas = {d[1] for d in diapos if d[0] == "video"}
    sin_uso = {p[0] for _, c, ps in BLOQUES if c.startswith(cfg["prefijo"]) for p in ps} - usadas
    if sin_uso:
        print("piezas sin diapositiva:", ", ".join(sorted(sin_uso)))
    if "--solo-guion" not in sys.argv:
        for t in ("oscuro", "claro"):
            construir(cfg, diapos, t)
