"""Paquete de conocimiento del proyecto para el asistente IA.

Reúne en un solo texto lo que el modelo necesita para generar animaciones
fieles al canal: las convenciones de estilo, el código fuente completo de
las primitivas de manim_extensions y un ejemplo real de la categoría
Experimentación. Se inyecta en los prompts de generar/corregir (ai.py).

Cacheado por mtime del árbol de contenido: editar una primitiva o añadir
una demo actualiza el contexto en la siguiente petición, sin reiniciar.
"""

from pathlib import Path

from .config import Settings

MAX_MODULO_CHARS = 7_000     # por archivo de primitiva
MAX_EJEMPLO_CHARS = 4_000    # por demo de ejemplo
MAX_TOTAL_CHARS = 60_000     # techo duro del paquete completo

GUIA = """\
GUIA DEL PROYECTO (ManimStudio — canal educativo de espacio/telecom/IA):

- Manim Community Edition v0.20. UNA clase Scene por script, metodo
  construct, sin red y sin leer/escribir archivos (sandbox de solo lectura).
- Las primitivas del proyecto se importan asi, SIEMPRE al inicio del script:
    import sys
    sys.path.insert(0, "/workspace/studio/content/manim_extensions")
  y despues `from <modulo> import <nombre>` (modulos abajo, con su fuente).
- Usa las primitivas del proyecto en lugar de reinventar sus efectos:
  brillo (glow), particulas (desintegrar/materializar), kepler (orbitas
  fisicas), senal (pulsos por caminos), neuronal (redes), constelacion
  (shells LEO), bloques (diagramas con flujo), laser (disparos/rafagas),
  pizarra3d (superficies y solidos proyectados en 2D, sin ThreeDScene).
- TRANSICIONES entre bloques de contenido: NO encadenes diapositivas con
  `FadeOut(viejo)` + `FadeIn(nuevo)` — en un video de 40 s eso parpadea
  diez veces. Usa `transiciones.py`, que despacha por nombre:
    from transiciones import transicion
    self.play(transicion("barrido", bloque_viejo, bloque_nuevo))
  Las diez: deslizar y empujar (dos momentos del mismo tema), zoom (entrar
  en un detalle), barrido (banda ambar = cambio de seccion), fundido_negro
  (cambio de TEMA, el respiro mas fuerte), persiana y rejilla (textura),
  difuminar (algo se deshace: ruido, perdida), conmutar (Transform de
  verdad: el mismo objeto en otro estado) y trazar (Uncreate+Create, para
  diagramas y ejes). `conmutar` deja convertido el objeto SALIENTE: sigue
  usando ese, no el entrante.
- IDENTIDAD CO.DE ACADEMY — es el MINIMO VISUAL, no una opcion. Todo video
  del canal sale con ella; ManimStudio la anexa al render aunque el script
  no la pida, pero un script que la usa explicitamente queda mejor:
    from code_brand import (registrar_fuentes, aplicar_marca, Rotulos,
                            titulo_marca, etiqueta_hud, CODE_ACCENT,
                            CODE_INK, CODE_MUTED, CODE_BG)
    registrar_fuentes()          # una vez, antes de crear cualquier Text
  - Paleta: fondo CODE_BG #05070a, texto CODE_INK #e8edf3, secundario
    CODE_MUTED #94a0b0, acento ambar CODE_ACCENT #f59e0b (y #ea580c para el
    cierre del degradado). NO uses GOLD/BLUE_B/TEAL_B/YELLOW de Manim ni
    inventes paletas: el ambar sobre casi-negro es la marca.
  - Tipografia propia: titulos con `titulo_marca(...)` (Rajdhani), etiquetas
    de telemetria con `etiqueta_hud(...)` (Space Mono, MAYUSCULAS). Nunca
    Text() con la fuente por defecto para un titulo.
  - Textos que se relevan: `Rotulos(self).mostrar(mob, zona="abajo")` — asi
    el nuevo desvanece al anterior de esa zona y NUNCA se enciman.
  - No dibujes tu propia marca de agua ni cambies el fondo a otro color: la
    marca de agua y las esquinas HUD las pone `aplicar_marca(self)`.
  Textos en espanol con tildes.
- Estructura: titulo (1 s) -> construccion (3-5 s) -> UN fenomeno
  protagonista (5-8 s) -> cierre con self.wait(1). Total 10-20 s.
- MathTex siempre con raw string (r"..."); LaTeX completo disponible.
- rate_func=linear para movimiento orbital/mecanico; there_and_back para
  pulsos; smooth (defecto) para el resto.
- Aleatoriedad solo con semilla fija (np.random.default_rng(n)).
- Si usas updaters, clear_updaters() al terminar la animacion que los usa.
- ReplacementTransform en lugar de Transform salvo razon concreta.
"""


class Conocimiento:
    def __init__(self, cfg: Settings) -> None:
        self.cfg = cfg
        self._texto: str | None = None
        self._mtime: float = -1.0

    # ── API ──────────────────────────────────────────────────────────────

    def contexto(self) -> str:
        """Texto completo del paquete, cacheado por mtime del contenido."""
        mtime = self._tree_mtime()
        if self._texto is None or mtime != self._mtime:
            self._texto = self._construir()
            self._mtime = mtime
        return self._texto

    # ── internos ─────────────────────────────────────────────────────────

    def _dirs(self) -> list[Path]:
        return [self.cfg.manim_extensions_dir,
                self.cfg.animations_dir / "experimentacion"]

    def _tree_mtime(self) -> float:
        latest = 0.0
        for d in self._dirs():
            try:
                latest = max(latest, d.stat().st_mtime)
                for p in d.glob("*.py"):
                    latest = max(latest, p.stat().st_mtime)
            except OSError:
                continue
        return latest

    def _construir(self) -> str:
        partes = [GUIA]

        modulos = sorted(self.cfg.manim_extensions_dir.glob("*.py"))
        if modulos:
            partes.append("\nFUENTE DE LAS PRIMITIVAS (manim_extensions):\n")
            for mod in modulos:
                try:
                    fuente = mod.read_text(encoding="utf-8")
                except OSError:
                    continue
                partes.append(f"\n### {mod.name}\n```python\n"
                              f"{_clip(fuente, MAX_MODULO_CHARS)}\n```\n")

        ejemplo = self._ejemplo_mas_corto()
        if ejemplo is not None:
            nombre, fuente = ejemplo
            partes.append(
                "\nEJEMPLO REAL DEL CANAL (demo de Experimentacion, "
                f"{nombre}) — imita su estructura y estilo:\n"
                f"```python\n{_clip(fuente, MAX_EJEMPLO_CHARS)}\n```\n")

        return _clip("".join(partes), MAX_TOTAL_CHARS)

    def _ejemplo_mas_corto(self) -> tuple[str, str] | None:
        demos = []
        for p in (self.cfg.animations_dir / "experimentacion").glob("*.py"):
            try:
                demos.append((p.name, p.read_text(encoding="utf-8")))
            except OSError:
                continue
        if not demos:
            return None
        return min(demos, key=lambda d: len(d[1]))


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n… [truncado]"
