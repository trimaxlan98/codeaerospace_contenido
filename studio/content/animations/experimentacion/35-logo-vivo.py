import sys
from pathlib import Path

sys.path.insert(0, "/workspace/studio/content/manim_extensions")
_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_REPO / "animaciones"))

from manim import *
from estelas import punta_cometa, remuestrear, tramo
from fondos_a_medida import acento, fondo_a_medida
from marca_aerospace import FONDO, LogoCoDe
from marca_vertical import _texto, marco
from reels_promo import Reloj, suave

# «Logo vivo»: el logo oficial QUIETO y exacto sobre un entorno espacial, con vida periódica encima:
# un destello recorre cada una de sus seis órbitas por turnos (uno cada T/6 s), la luna pulsa y el fondo
# «respira». Todo es función periódica del reloj (T = 8 s): LOOP PERFECTO para historias, portada de
# perfil o fondo de transmisión. 9:16 (renderizar con -r 1080,1920). Audio: sonido_reels.py (logo_vivo).

T = 8.0
TRAVESIA = 0.32            # fracción del periodo que tarda un destello en recorrer su órbita
TEMAS = ["orbita", "nebulosa", "marte", "lunar", "fisica", "espectro"]
Y_LOGO = 1.0


class _LogoVivo(Scene):
    tema = "orbita"

    def construct(self):
        W, H = marco(self)
        self.camera.background_color = FONDO
        reloj = Reloj(self, T)
        fondo = ImageMobject(str(fondo_a_medida(self.tema, "portada", 0, 1080, 1920))).set_z_index(-20)
        fondo.stretch_to_fit_width(W * 1.04).stretch_to_fit_height(H * 1.04)
        base = fondo.copy()

        def respirar(m):
            k = 1.0 + 0.025 * (1 - np.cos(2 * np.pi * reloj.t / T)) / 2
            m.become(base.copy().scale(k).set_z_index(-20))
        fondo.add_updater(respirar)
        self.add(fondo)
        halo = VGroup(*[Circle(radius=r).set_stroke(width=0).set_fill(FONDO, 0.07)
                        for r in np.linspace(3.0, 7.2, 10)]).move_to(UP * Y_LOGO).set_z_index(-10)
        self.add(halo)

        col = acento(self.tema)
        logo = LogoCoDe(altura=W * 0.86 / 1.05, contorno=True).mover_a(UP * Y_LOGO)
        self.add(logo)
        # Las órbitas de TRAZO (no añadidas a la escena) sirven de trayecto; remuestreadas: velocidad uniforme.
        trayectos = [remuestrear(o.copy(), 80) for o in logo.orbitas]
        orden = [0, 3, 1, 4, 2, 5]                       # alterna órbitas de un lado y del otro
        k_esc = logo.escala / 0.0048
        for turno, idx in enumerate(orden):
            tray = trayectos[idx]
            fase = turno / 6
            estela = VMobject().set_z_index(5)
            punta = punta_cometa(color=col, radio=0.065 * k_esc).set_z_index(6)

            def mover(m, tray=tray, fase=fase, estela=estela):
                u = ((reloj.t / T) - fase) % 1.0
                if u >= TRAVESIA:
                    m.set_opacity(0); estela.become(VMobject()); return
                s = suave(u / TRAVESIA)
                f = min(1.0, (TRAVESIA - u) / (TRAVESIA * 0.25), u / (TRAVESIA * 0.08) if u > 0 else 0)
                m.move_to(tray.point_from_proportion(min(max(s, 0.001), 0.999)))
                for capa in m:
                    capa.set_fill(opacity=capa.opacidad_base * f)
                estela.become(tramo(tray, max(0, s - 0.3), s, color=col, ancho=8 * k_esc, opacidad=0.95 * f).set_z_index(5))
            punta.add_updater(mover)
            self.add(estela, punta)
        # La luna pulsa (2 latidos por periodo).
        pulso = VGroup(*[Circle(radius=logo.luna.width * (0.6 + 0.35 * i)).set_stroke(width=0).set_fill(col, 0.0)
                         for i in range(4)]).move_to(logo.luna).set_z_index(4)

        def latir(m):
            a = (1 - np.cos(4 * np.pi * reloj.t / T)) / 2
            for i, c in enumerate(m):
                c.set_fill(opacity=0.10 * a * (1 - i / 4))
        pulso.add_updater(latir)
        self.add(pulso)
        sitio = _texto("codeaerospace.com", 40, "MEDIUM", col, tracking=0.08, ancho_max=W * 0.8).move_to(DOWN * 6.6)
        self.add(sitio)
        self.wait(T)


for _t in TEMAS:
    _n = "LogoVivo" + _t.capitalize()
    globals()[_n] = type(_n, (_LogoVivo,), {"tema": _t, "__doc__": f"Logo vivo en loop sobre «{_t}» (9:16, 8 s)."})
del _t, _n
