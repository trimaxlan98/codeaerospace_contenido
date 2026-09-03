#!/usr/bin/env python3
"""Invariantes de `figura.py`. Se corre ANTES de dibujar una figura de paper.

    docker run --rm --network none --user $(id -u):$(id -g) \\
        -v "$PWD":/workspace -w /workspace \\
        codeaerospace_contenido-manim python3 studio/tools/sonda_figura.py

Una figura de paper mal dimensionada NO se ve mal en pantalla: se ve mal
IMPRESA, meses despues, cuando ya esta en el PDF. Asi que aqui no se comprueba
que el codigo corra: se MIDE el lienzo en pulgadas, la tipografia en puntos y
—la unica prueba que de verdad cierra el circulo— el PNG que sale de `-s`,
contando pixeles con PIL. Cada guardian se prueba ademas con un caso que TIENE
que fallar; un guardian que nunca ha abortado no esta demostrado.
"""
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / "content" / "manim_extensions"))
import code_brand  # noqa: E402
import figura as fg  # noqa: E402
from manim import Axes, Scene, Text, tempconfig  # noqa: E402

fallos = []
n_ok = 0


def ok(nombre, condicion, detalle=""):
    global n_ok
    if condicion:
        n_ok += 1
        print(f"  ok   {nombre}" + (f"   [{detalle}]" if detalle else ""))
    else:
        fallos.append(nombre)
        print(f"  FALLO {nombre}   {detalle}")


def casi(nombre, a, b, tol, unidad=""):
    ok(nombre, abs(float(a) - float(b)) <= tol,
       f"{float(a):.6g} vs {float(b):.6g} {unidad}".strip())


TMP = Path(tempfile.mkdtemp(prefix="sonda_figura_"))

# =============================================================================
print("\n== 01 - El lienzo es fisico ==")
una = fg.Figura(tema="paper", columnas=1)
r1 = una.resumen()
ok("una columna IEEE son 3.5 in", r1["ancho_in"] == 3.5, f"{r1['ancho_in']} in")
ok("a 300 dpi son 1050 px de ancho", r1["pixel_width"] == 1050,
   f"{r1['pixel_width']} x {r1['pixel_height']} px")
casi("y 652 px de alto (2.17 in redondeado al par siguiente)",
     r1["pixel_height"], 652, 0)
ok("los dos lados son PARES (si no, libx264 no codifica el video)",
   r1["pixel_width"] % 2 == 0 and r1["pixel_height"] % 2 == 0,
   f"{r1['pixel_width']} x {r1['pixel_height']}")
casi("una unidad de escena son 18 puntos", r1["puntos_por_unidad"], 18.0, 1e-12)
casi("el frame mide 14 unidades de ancho", r1["frame_width"], 14.0, 1e-12)
casi("y 8.6933 de alto (652/300 x 4)", r1["frame_height"], 652 / 300 * 4, 1e-12)

dos = fg.Figura(tema="paper", columnas=2)
r2 = dos.resumen()
ok("dos columnas IEEE son 7.16 in", r2["ancho_in"] == 7.16)
ok("a 300 dpi son 2148 px de ancho", r2["pixel_width"] == 2148,
   f"{r2['pixel_width']} x {r2['pixel_height']} px")
casi("y una unidad sigue siendo 18 puntos", r2["puntos_por_unidad"], 18.0,
     1e-12)
for r in (r1, r2):
    casi(f"la proporcion del frame es la de la imagen ({r['pixel_width']} px)",
         r["frame_width"] / r["frame_height"],
         r["pixel_width"] / r["pixel_height"], 1e-12)
# CONTRAEJEMPLO: fijar solo frame_width deja frame_height como estaba y la
# figura sale deformada. Se comprueba que `aplicar()` escribe LOS DOS.
from manim import config  # noqa: E402
config.frame_height = 3.21
fg.Figura(tema="paper", columnas=1)
casi("aplicar() reescribe tambien frame_height (contraejemplo)",
     config.frame_height, 652 / 300 * 4, 1e-9)
try:
    fg.Figura(columnas=3)
    ok("una columna que no existe tiene que fallar", False)
except ValueError as e:
    ok("una columna que no existe falla y lo dice", "1 o 2" in str(e))

print("\n== 02 - Tipografia medida en puntos ==")
fg.Figura(tema="paper", columnas=1)
alturas = [fg.alto(fg._texto_crudo("Hxdp", f_)) for f_ in (10, 25, 50, 100)]
razones = [a / f_ for a, f_ in zip(alturas, (10, 25, 50, 100))]
ok("el alto de tinta es lineal en font_size",
   max(razones) - min(razones) < 1e-4,
   " ".join(f"{x:.6f}" for x in razones))
for pt in (4.5, 6.0, 7.0, 9.0):
    casi(f"texto({pt} pt) se pinta a {pt} pt", fg.alto_pt(fg.texto("Hxdp", pt)),
         pt, 0.02, "pt")
ok("el mismo cuerpo da el mismo font_size para cualquier cadena",
   fg.texto("0", 7.0).font_size == fg.texto("tiempo (s)", 7.0).font_size,
   f"{fg.texto('0', 7.0).font_size:.3f}")
ok("y un digito pinta menos tinta que una linea con descendente",
   fg.alto_pt(fg.texto("0", 7.0)) < fg.alto_pt(fg.texto("Hxdp", 7.0)),
   f"{fg.alto_pt(fg.texto('0', 7.0)):.2f} contra "
   f"{fg.alto_pt(fg.texto('Hxdp', 7.0)):.2f} pt")
fg.Figura(tema="paper", columnas=2)
casi("7 pt en dos columnas siguen siendo 7 pt impresos",
     fg.alto_pt(fg.texto("Hxdp", 7.0)), 7.0, 0.02, "pt")

print("\n== 03 - El espacio infla la caja de manim ==")
fg.Figura(tema="paper", columnas=1)
con_espacio = Text("RTT (ms)", font_size=25)
sin_espacio = Text("RTT(ms)", font_size=25)
h_antes = float(con_espacio.height)
real_antes = fg.alto(con_espacio)
con_espacio.shift(np.array([3.0, -2.0, 0.0]))
sin_espacio.shift(np.array([3.0, -2.0, 0.0]))
ok("un Text CON espacio miente en .height despues de moverse",
   float(con_espacio.height) > 3 * h_antes,
   f"{h_antes:.4f} -> {float(con_espacio.height):.4f} unidades")
ok("uno SIN espacio no (contraejemplo)",
   abs(float(sin_espacio.height) - fg.alto(sin_espacio)) < 1e-9,
   f"{float(sin_espacio.height):.4f}")
casi("y figura.alto() no se inmuta", fg.alto(con_espacio), real_antes, 1e-9)
ok("el espacio es un submobject VACIO: esa es la causa",
   any(not m.has_points() for m in con_espacio.submobjects)
   and all(m.has_points() for m in sin_espacio.submobjects),
   f"{sum(1 for m in con_espacio.submobjects if not m.has_points())} "
   f"submobjects vacios")
# `pegar` tiene que apoyarse en la caja de tinta, no en next_to.
a = fg.texto("uno dos", 7.0)
b = fg.texto("tres", 7.0)
fg.pegar(b, a, fg.DER, 0.1)
casi("pegar deja el hueco pedido", fg.caja(b)[0][0] - fg.caja(a)[1][0], 0.1,
     1e-9, "unidades")

print("\n== 04 - Guardian de legibilidad ==")
ax = fg.ejes_paper((0, 60), (0, 80), "tiempo (s)", "RTT (ms)")
peor = fg.exigir_legible(ax)
ok("unos ejes de 6 pt pasan el guardian", peor >= fg.PT_MINIMO,
   f"el rotulo mas chico se pinta a {peor:.2f} pt")
# CONTRAEJEMPLO 1: el mismo grupo encogido TIENE que abortar.
try:
    fg.exigir_legible(ax.copy().scale(0.3), que="encogido")
    ok("un grupo encogido tiene que abortar (contraejemplo)", False)
except fg.LienzoIlegible as e:
    ok("un grupo encogido aborta (contraejemplo)", "por debajo del suelo" in str(e),
       str(e).split(" en un lienzo")[0][-46:])
# CONTRAEJEMPLO 2: medir GLIFO a glifo daria un falso positivo sobre los MISMOS
# ejes, que se leen perfectamente.
glifos = [fg.alto(g) * 18.0 for t in fg._textos_de(ax)
          for g in t.submobjects if g.has_points()]
ok("medir glifo a glifo daria un falso positivo (contraejemplo)",
   min(glifos) < fg.PT_MINIMO < peor,
   f"el glifo mas chico mide {min(glifos):.2f} pt y el rotulo, {peor:.2f} pt")
ok("encajar() escala y vuelve a comprobar",
   fg.encajar(fg.ejes_paper((0, 10), (0, 1))) is not None)

print("\n== 05 - Ejes: el marco va al borde, no al origen ==")
ax_sin_cero = fg.ejes_paper((10, 40), (-190, -85), "f (Hz)", "fase (grados)")
y_abajo = float(ax_sin_cero.c2p(10, -190)[1])
y_arriba = float(ax_sin_cero.c2p(10, -85)[1])
y_marco = float(fg.centro(ax_sin_cero.marco[0])[1])
casi("con un rango que no contiene el cero, el eje X va ABAJO", y_marco,
     y_abajo, 1e-6)
# CONTRAEJEMPLO: el Axes de manim lo pone en el borde de ARRIBA para ese rango.
crudo = Axes(x_range=[10, 40, 10], y_range=[-190, -85, 25], x_length=4,
             y_length=2, tips=False)
y_manim = float(crudo.x_axis.get_center()[1])
ok("el Axes de manim lo pone arriba, encima de la curva (contraejemplo)",
   abs(y_manim - float(crudo.c2p(10, -85)[1])) < 1e-6,
   f"eje en y={y_manim:.3f}, arriba={float(crudo.c2p(10, -85)[1]):.3f}")
ok("sin cero dentro del rango NO se dibuja linea de cero",
   len(ax_sin_cero.linea_cero) == 0)
ax_con_cero = fg.ejes_paper((0, 10), (-1, 1), "t", "y")
ok("y con el cero dentro, si", len(ax_con_cero.linea_cero) == 1)
casi("y esta en el cero, no en el suelo del cuadro",
     float(fg.centro(ax_con_cero.linea_cero)[1]),
     float(ax_con_cero.c2p(0, 0.0)[1]), 1e-6)

print("\n== 06 - Trazos ==")
ax = fg.ejes_paper((0, 10), (0, 1))
x = np.linspace(0, 10, 200)
y = np.where((x > 4) & (x < 6), 3.0, 0.5)      # una excursion fuera del cuadro
c = fg.curva(ax, x, y)
ok("una curva que se sale del cuadro se parte en tramos", len(c) == 2,
   f"{len(c)} tramos")
puntos = np.vstack([m.points for m in c.family_members_with_points()])
techo = float(ax.c2p(0, 1)[1])
ok("y ningun punto dibujado pasa del techo",
   float(puntos[:, 1].max()) <= techo + 1e-9,
   f"{float(puntos[:, 1].max()):.4f} contra {techo:.4f}")
# CONTRAEJEMPLO: recortar con np.clip habria dejado UN tramo con una meseta
# pegada al borde, que se lee como saturacion.
recortada = fg.curva(ax, x, np.clip(y, 0, 1))
ok("con np.clip habria salido un solo tramo con meseta (contraejemplo)",
   len(recortada) == 1, "una meseta que se leeria como saturacion")
banda = fg.banda_ic(ax, x, np.full_like(x, 0.3), np.full_like(x, 0.7))
ok("la banda IC solo tiene relleno, no trazo",
   float(np.max(banda.get_stroke_opacity())) < 1e-9
   and float(np.max(banda.get_fill_opacity())) > 0.1,
   f"trazo {float(np.max(banda.get_stroke_opacity())):.2f}, relleno "
   f"{float(np.max(banda.get_fill_opacity())):.2f}")
rng = np.random.default_rng(42)
muestras = rng.gamma(2.0, 1.4, 24)
ax2 = fg.ejes_paper((0, float(np.ceil(muestras.max()))), (0, 1))
c2 = fg.cdf(ax2, muestras)
ok("la CDF va de 1/n a 1 y es monotona",
   abs(float(c2.f[-1]) - 1.0) < 1e-12 and np.all(np.diff(c2.f) > 0),
   f"F({c2.x[0]:.2f}) = {c2.f[0]:.3f}")
ok("el percentil 50 es una muestra de verdad",
   float(fg.percentil(muestras, 50)) in set(muestras.tolist()),
   f"p50 = {fg.percentil(muestras, 50):.3f} s, "
   f"p95 = {fg.percentil(muestras, 95):.3f} s")

print("\n== 07 - Gantt ==")
g = fg.gantt([("satellite", [(0, 18, "up"), (18, 24, "down"), (24, 40, "up")]),
              ("gateway-a", [(0, 40, "up")]),
              ("ue", [(0, 12, "up"), (12, 16, "hueco"), (16, 40, "up")])],
             eventos=[(18, "loss=100"), (24, "clear")])
casi("el eje empieza en 0", g.x(0), 0.0, 1e-12)
casi("y acaba en el ancho util", g.x(40), g.ancho_util, 1e-12)
casi("la mitad del tiempo es la mitad del ancho", g.x(20),
     g.ancho_util / 2, 1e-12)
ok("cada fila lleva su fondo de 'sin evidencia'",
   sum(1 for r in g.barras if abs(fg.ancho(r) - g.ancho_util) < 1e-9) >= 3,
   "tres fondos a lo ancho de la ventana")
try:
    fg.gantt([("x", [(0, 1, "arriba")])])
    ok("un estado inventado tiene que fallar", False)
except ValueError as e:
    ok("un estado inventado falla y lo dice", "desconocido" in str(e))

print("\n== 08 - Datos: entran, no se transcriben ==")
datos = TMP / "datos"
datos.mkdir(parents=True, exist_ok=True)
(datos / "serie.csv").write_text(
    "tick,delay_ms,estado\n0,12.9,up\n1,10.0,up\n2,,down\n", encoding="utf-8")
(datos / "eventos.jsonl").write_text(
    '{"fila":"sat","t0":0,"t1":18,"estado":"up"}\n'
    '{"fila":"sat","t0":18,"t1":24,"estado":"down"}\n', encoding="utf-8")
os.environ["MS_DATOS_DIR"] = str(datos)
col = fg.leer_csv("serie.csv")
ok("una columna de numeros llega como numpy",
   isinstance(col["delay_ms"], np.ndarray), str(col["delay_ms"].dtype))
ok("un hueco es nan, no cero", bool(np.isnan(col["delay_ms"][2])),
   f"{col['delay_ms']}")
ok("una columna de texto llega como texto", col["estado"] == ["up", "up", "down"])
regs = fg.leer_jsonl("eventos.jsonl")
ok("el JSONL llega entero", len(regs) == 2 and regs[0]["fila"] == "sat")
filas = fg.tramos_de_jsonl(regs)
ok("y se convierte en filas de gantt",
   filas == [("sat", [(0.0, 18.0, "up"), (18.0, 24.0, "down")])], str(filas))
try:
    fg.leer_csv("no_existe.csv")
    ok("un archivo que no esta tiene que fallar", False)
except fg.DatosNoEncontrados as e:
    ok("un archivo que no esta falla diciendo DONDE busco",
       "MS_DATOS_DIR" in str(e) and str(datos) in str(e) and "cwd=" in str(e),
       "el mensaje nombra el directorio, la variable y el cwd")
del os.environ["MS_DATOS_DIR"]
ok("sin MS_DATOS_DIR el directorio por defecto es datos/",
   fg.datos_dir() == Path("datos"))

print("\n== 09 - Sello de proveniencia ==")
for var in ("MS_COMMIT", "MS_SEMILLA", "MS_FECHA"):
    os.environ.pop(var, None)
s_pelado = fg.texto_sello()
ok("sin entorno y sin argumentos dice sin-commit",
   s_pelado.startswith("commit sin-commit"), s_pelado)
ok("y no inventa una semilla", "semilla" not in s_pelado)
ok("pero si estampa la version de la libreria",
   f"figura {fg.VERSION}" in s_pelado)
os.environ["MS_COMMIT"] = "4cec02a1234567890abcdef"
os.environ["MS_SEMILLA"] = "42"
os.environ["MS_FECHA"] = "2026-09-03"
s_env = fg.texto_sello()
ok("con entorno lee las tres variables",
   s_env == "commit 4cec02a12345 | semilla 42 | 2026-09-03 | "
            f"figura {fg.VERSION}", s_env)
ok("el commit se corta a 12 caracteres",
   fg.proveniencia()["commit"] == "4cec02a12345")
ok("y un argumento explicito manda sobre el entorno",
   "semilla 7" in fg.texto_sello(semilla=7))
ok("el extra se anade al final", fg.texto_sello(extra="G3").endswith("G3"))
sello = fg.sello()
casi("el sello se pinta a 4 pt", fg.puntos_efectivos(sello), 4.0, 0.02, "pt")
c_sello = fg.caja(sello)
fig = fg.activa()
ok("y va abajo a la derecha, dentro del lienzo",
   c_sello[1][0] < fig.frame_width / 2 and c_sello[0][1] > -fig.frame_height / 2,
   f"esquina en ({c_sello[1][0]:.2f}, {c_sello[0][1]:.2f}) de "
   f"({fig.frame_width / 2:.2f}, {-fig.frame_height / 2:.2f})")
for var in ("MS_COMMIT", "MS_SEMILLA", "MS_FECHA"):
    del os.environ[var]

print("\n== 10 - La marca del canal no se cuela en una figura de paper ==")


class _EscenaPaper(Scene):
    def construct(self):
        self.add(fg.texto("Hxdp", 8.0))


class _EscenaCanal(Scene):
    def construct(self):
        self.add(fg.texto("Hxdp", 8.0))


ns = {"__name__": __name__, "_EscenaPaper": _EscenaPaper}
setup_antes = _EscenaPaper.setup
fg.sellar_escenas(ns)
code_brand.marcar_escenas(ns)
ok("una escena sellada NO recibe la marca de agua del canal",
   _EscenaPaper.setup is setup_antes)
# CONTRAEJEMPLO: sin sellar, la marca SI se aplica (y repintaria la figura).
ns2 = {"__name__": __name__, "_EscenaCanal": _EscenaCanal}
setup_canal = _EscenaCanal.setup
code_brand.marcar_escenas(ns2)
ok("y una sin sellar SI (contraejemplo)", _EscenaCanal.setup is not setup_canal)

print("\n== 11 - El PNG que sale de -s, contado con PIL ==")


class _Muestra(Scene):
    def construct(self):
        fg.fondo(self)
        self.add(fg.texto("Hxdp", 8.0))


def render_png(figura, escena_cls, etiqueta):
    """Renderiza con -s (ultimo fotograma) y devuelve la ruta del PNG."""
    figura.aplicar()
    destino = TMP / etiqueta
    with tempconfig({"save_last_frame": True, "write_to_movie": False,
                     "media_dir": str(destino), "disable_caching": True,
                     "verbosity": "ERROR", "output_file": etiqueta}):
        escena_cls().render()
    pngs = sorted(destino.rglob("*.png"))
    if not pngs:
        raise RuntimeError(f"el render con -s no dejo ningun PNG en {destino}")
    return pngs[-1]


png1 = render_png(fg.Figura(tema="paper", columnas=1), _Muestra, "una")
im1 = Image.open(png1).convert("L")
ok("el PNG de una columna mide 1050 x 652 px", im1.size == (1050, 652),
   f"{im1.size[0]} x {im1.size[1]} px")
png2 = render_png(fg.Figura(tema="paper", columnas=2), _Muestra, "dos")
im2 = Image.open(png2).convert("L")
ok("el de dos columnas, 2148 x 1332 px", im2.size == (2148, 1332),
   f"{im2.size[0]} x {im2.size[1]} px")

# La prueba que cierra el circulo: el texto que la libreria declara de 8 pt
# tiene que MEDIR 8 pt en el papel. A 300 dpi son 8/72*300 = 33.33 px de tinta.
arr = np.asarray(im1)
tinta = np.argwhere(arr < 128)
alto_px = int(tinta[:, 0].max() - tinta[:, 0].min() + 1)
esperado_px = 8.0 / 72.0 * 300.0
casi("un texto de 8 pt mide 8 pt impresos (medido en el PNG)", alto_px,
     esperado_px, 2.0, "px")
ok("...o sea, en puntos", abs(alto_px / 300.0 * 72.0 - 8.0) < 0.5,
   f"{alto_px} px = {alto_px / 300.0 * 72.0:.2f} pt")
ok("el fondo de paper es blanco", int(arr[2, 2]) > 250, f"gris {int(arr[2, 2])}")

fg.Figura(tema="marca", columnas=1)
png3 = render_png(fg.activa(), _Muestra, "marca")
arr3 = np.asarray(Image.open(png3).convert("L"))
ok("el fondo del tema marca es casi negro", int(arr3[2, 2]) < 20,
   f"gris {int(arr3[2, 2])}")
casi("y el mismo cuerpo mide lo mismo en el tema marca",
     int(np.argwhere(arr3 > 128)[:, 0].max()
         - np.argwhere(arr3 > 128)[:, 0].min() + 1),
     esperado_px, 2.5, "px")

print("\n== 12 - Guardian de lo que se sale del cuadro ==")
fg.Figura(tema="paper", columnas=1)
fig_a = fg.activa()
dentro = fg.texto("cabe", 8.0)
ok("algo centrado y chico esta dentro",
   fg.exigir_dentro(dentro, que="chico") is dentro)
# CONTRAEJEMPLO 1: mas ancho que el lienzo.
try:
    fg.exigir_dentro(fg.texto("x" * 200, 8.0), que="larguisimo")
    ok("un texto mas ancho que el lienzo tiene que abortar", False)
except fg.FueraDelLienzo as e:
    ok("un texto mas ancho que el lienzo aborta (contraejemplo)",
       "se sale por" in str(e), str(e)[:58])
# CONTRAEJEMPLO 2 —el que de verdad importa—: algo que CABE por tamano y aun
# asi se sale porque esta mal colocado. Un guardian que solo mide el ancho lo
# deja pasar, y en el PNG sale cortado.
corrido = fg.texto("cabe pero esta fuera", 8.0)
ok("...y cabe de sobra por tamano",
   fg.ancho(corrido) < fig_a.zona(4.0)[0])
fg.poner(corrido, [fig_a.frame_width / 2, 0.0, 0.0], anclaje=fg.IZQ)
try:
    fg.exigir_dentro(corrido, que="corrido")
    ok("algo colocado fuera tiene que abortar aunque quepa", False)
except fg.FueraDelLienzo as e:
    ok("algo colocado fuera aborta aunque quepa (contraejemplo)",
       "derecha" in str(e), str(e)[:58])

largo = "PASE LEO-600 SOBRE UNA ESTACION TERRENA"
crudo_t = fg.texto(largo, 15.0)
t_ajustado = fg.titulo(largo, puntos=15.0)
ok("un titulo que no cabe se encoge solo",
   fg.ancho(t_ajustado) < fg.ancho(crudo_t)
   and fg.ancho(t_ajustado) <= fig_a.zona(4.0)[0] + 1e-9,
   f"{fg.ancho(crudo_t):.2f} -> {fg.ancho(t_ajustado):.2f} de "
   f"{fig_a.zona(4.0)[0]:.2f} unidades")
ok("y sigue dentro del lienzo",
   fg.exigir_dentro(t_ajustado, que="titulo largo") is t_ajustado)
try:
    fg.encoger_a_ancho(fg.texto(largo, 6.0), ancho_max=1.0, minimo_pt=5.0,
                       que="apretado")
    ok("encoger por debajo del suelo tiene que abortar", False)
except fg.LienzoIlegible:
    ok("encoger por debajo del suelo aborta (contraejemplo)", True,
       "de 6 pt a menos de 5 en un ancho de 1 unidad")

# =============================================================================
print("\n" + "=" * 68)
print("LAS CIFRAS DEL LIENZO")
print("=" * 68)
for r, nombre in ((r1, "una columna"), (r2, "dos columnas")):
    print(f"  {nombre:<14} {r['ancho_in']:.2f} x {r['alto_in']:.2f} in @ "
          f"{r['dpi']} dpi  ->  {r['pixel_width']} x {r['pixel_height']} px, "
          f"frame {r['frame_width']:.2f} x {r['frame_height']:.2f} u")
print(f"  {'tipografia':<14} 1 unidad = {r1['puntos_por_unidad']:.1f} pt; "
      f"font_size para 7 pt = {fg.fs_para_pt(7.0):.2f}")
print(f"  {'8 pt medidos':<14} {alto_px} px de tinta en el PNG "
      f"(esperado {esperado_px:.2f})")
print(f"  {'suelo legible':<14} {fg.PT_MINIMO} pt (sello, {fg.PT_MINIMO_SELLO} pt)")

print("\n" + "=" * 68)
print(f"{n_ok} invariantes ok, {len(fallos)} fallos")
if fallos:
    for f_ in fallos:
        print(f"  - {f_}")
sys.exit(1 if fallos else 0)
