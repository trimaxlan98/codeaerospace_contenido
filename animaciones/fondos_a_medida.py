"""Fondo espacial de cualquier tema registrado, a cualquier tamaño, con caché en disco.

Une temas_espaciales (qué generador y qué giro de matiz usa cada tema) con fondos_espaciales.tamano()
(el lienzo de los generadores). Lo usan los carruseles, el logo en entornos y las escenas Manim que
ponen un fondo de tema detrás (ImageMobject).

    from fondos_a_medida import fondo_a_medida
    ruta = fondo_a_medida("nebulosa", "portada", 0, 1080, 1920)   # → Path a un JPEG
"""
from pathlib import Path

CACHE = Path(__file__).resolve().parent.parent / "exports" / "estudio" / "_fondos"


# Temas cuya decoración vive a la derecha del lienzo 16:9 (pensados para portada con título a la izquierda):
# en formatos verticales conviene generarlos anchos y recortar una ventana sobre la decoración.
DECORADOS_A_LA_DERECHA = {"mision", "estacion", "aerodinamica", "calculo", "caos", "cuaderno", "electromagnetismo",
                          "electronica", "espectro", "fisica", "neuronal", "robotica", "solar"}


def ventana_sugerida(tema, ancho, alto):
    """Centro (fracción del ancho 16:9) de la ventana vertical que muestra la decoración, o None."""
    return 0.72 if ancho < alto and tema in DECORADOS_A_LA_DERECHA else None


def fondo_a_medida(tema, tipo="portada", var=0, ancho=1080, alto=1920, rehacer=False, calidad=93, ventana="auto"):
    """ventana: None = el generador pinta directo a ancho×alto; un número = genera a 16:9 de alto `alto` y
    recorta una franja de `ancho` centrada en esa fracción; "auto" = ventana_sugerida()."""
    CACHE.mkdir(parents=True, exist_ok=True)
    if ventana == "auto":
        ventana = ventana_sugerida(tema, ancho, alto)
    sufijo = f"_v{int(ventana * 100)}" if ventana is not None else ""
    ruta = CACHE / f"{tema}_{tipo}_{var}_{ancho}x{alto}{sufijo}.jpg"
    if ruta.exists() and not rehacer:
        return ruta
    if ventana is not None:
        from PIL import Image
        ancho16 = int(round(alto * 16 / 9))
        completo = Image.open(fondo_a_medida(tema, tipo, var, ancho16, alto, rehacer, calidad, ventana=None))
        x0 = int(min(max(ventana * ancho16 - ancho / 2, 0), ancho16 - ancho))
        completo.crop((x0, 0, x0 + ancho, alto)).save(ruta, quality=calidad)
        return ruta
    import fondos_espaciales as FE
    import temas_espaciales as TE
    TE.cargar_plugins()
    t = TE.obtener(tema)
    import os
    previo = FE.tamano(ancho, alto)
    try:
        img = FE.GENERADORES[t.generador](tipo, var, None)
        if t.tinte:
            img = FE.rotar_matiz(img, t.tinte)
        tmp = ruta.with_suffix(f".{os.getpid()}.tmp.jpg")   # escritura atómica y temporal por proceso
        FE.a_imagen(img).save(tmp, quality=calidad)
        tmp.replace(ruta)
    finally:
        FE.tamano(*previo)
    return ruta


def acento(tema):
    import temas_espaciales as TE
    TE.cargar_plugins()
    return TE.obtener(tema).color.get("acento", "#00D9FF")
