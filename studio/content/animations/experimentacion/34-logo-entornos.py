import sys
from pathlib import Path

sys.path.insert(0, "/workspace/studio/content/manim_extensions")
_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "animaciones"))

from manim import *
from fondos_a_medida import acento, fondo_a_medida
from marca_aerospace import FONDO, LogoCoDe, animar_entrada
from marca_vertical import _texto, marco

# El logo de Co.De Aerospace entrando (estilo orbital) sobre los entornos espaciales de las diapositivas,
# en vertical 9:16 (renderizar con -r 1080,1920). Un fondo procedural del tema a la medida, un acercamiento
# lento (el fondo «respira») y un halo oscuro detrás del logo para que la plata se lea sobre cualquier
# nebulosa. Mismos tiempos que ReelIntro (≈9.3 s): el audio de sonido_marca.py sirve igual.

CLAROS = {"estacion", "cuaderno"}
TEMAS = ["orbita", "nebulosa", "mision", "marte", "lunar", "solar", "espectro", "lanzamiento", "fisica", "caos"]
Y_LOGO = 1.6


class _LogoEntorno(Scene):
    tema = "orbita"

    def construct(self):
        W, H = marco(self)
        claro = self.tema in CLAROS
        self.camera.background_color = "#F4F6F8" if claro else FONDO
        ruta = fondo_a_medida(self.tema, "portada", 0, 1080, 1920)
        fondo = ImageMobject(str(ruta)).set_z_index(-20)
        fondo.stretch_to_fit_width(W).stretch_to_fit_height(H)
        base = fondo.copy()
        reloj = [0.0]

        def respirar(m, dt):
            reloj[0] += dt
            k = 1.0 + 0.05 * min(reloj[0] / 9.3, 1.0)
            m.become(base.copy().scale(k).set_z_index(-20))
        fondo.add_updater(respirar)
        self.add(fondo)
        if not claro:                                   # halo oscuro: plata legible sobre cualquier fondo
            halo = VGroup(*[Circle(radius=r).set_stroke(width=0).set_fill(FONDO, 0.07)
                            for r in np.linspace(3.2, 7.4, 10)]).move_to(UP * Y_LOGO).set_z_index(-10)
            self.add(halo)
        col = acento(self.tema)
        logo = LogoCoDe(altura=W * 0.86 / 1.05, color="negro" if claro else "plata").mover_a(UP * Y_LOGO)
        animar_entrada(self, logo, estilo="orbital", acento=col)
        sitio = _texto("codeaerospace.com", 44, "MEDIUM", col, tracking=0.08, ancho_max=W * 0.8).move_to(DOWN * 6.4)
        self.play(FadeIn(sitio, shift=0.2 * UP), run_time=0.7)
        self.wait(1.6)


for _t in TEMAS:
    _n = "LogoEntorno" + "".join(p.capitalize() for p in _t.split("_"))
    globals()[_n] = type(_n, (_LogoEntorno,), {"tema": _t, "__doc__": f"Entrada orbital del logo sobre el entorno «{_t}» (9:16)."})
del _t, _n
