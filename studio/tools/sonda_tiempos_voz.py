#!/usr/bin/env python3
"""Mide, SIN renderizar video, en que instante absoluto cae cada self.leer()
de una pieza ya compuesta (scene.py de render_vertical.py --solo-componer).

Parchea Scene.play/Scene.wait para que NO llamen al renderer real (nada de
frames, nada de ffmpeg): solo acumulan el run_time declarado y lo imprimen.
Corre DENTRO del contenedor manim porque Text/MathTex necesitan Pango/LaTeX
para construirse aunque no se dibujen.

Uso (dentro del contenedor):
    python3 sonda_tiempos_voz.py /media/scene.py Clip
Imprime una linea JSON por evento: play/wait/leer con (t0, dur, fin).
"""
import json
import sys
from pathlib import Path


def main():
    scene_path = Path(sys.argv[1])
    clase = sys.argv[2] if len(sys.argv) > 2 else "Clip"

    from manim import Scene, config
    config.media_dir = str(scene_path.parent)
    config.disable_caching = True

    eventos = []
    estado = {"t": 0.0}

    def _registrar(tipo, dur, extra=""):
        t0 = estado["t"]
        dur = float(dur)
        estado["t"] = t0 + dur
        eventos.append({"tipo": tipo, "t0": round(t0, 3),
                        "dur": round(dur, 3), "t1": round(estado["t"], 3),
                        "extra": extra})

    def _play(self, *anims, **kwargs):
        if not anims:
            return
        if "run_time" in kwargs and kwargs["run_time"] is not None:
            dur = kwargs["run_time"]
        else:
            duraciones = []
            for a in anims:
                rt = getattr(a, "run_time", None)
                if rt is not None:
                    duraciones.append(rt)
            dur = max(duraciones) if duraciones else 1.0
        _registrar("play", dur)

    def _wait(self, duration=1.0, **kwargs):
        _registrar("wait", duration)

    Scene.play = _play
    Scene.wait = _wait

    # Pieza.leer llama a self.wait(t) tal cual: se detecta envolviendo leer
    # para anotar el evento como "leer" en vez de "wait" generico, y con el
    # texto de contexto (el guardian LECTURA_MINIMA sigue corriendo).
    import importlib.util
    spec = importlib.util.spec_from_file_location("_scene_probe", scene_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    Pieza = None
    for nombre in ("Pieza",):
        if hasattr(mod, nombre):
            Pieza = getattr(mod, nombre)
            break
    if Pieza is not None and hasattr(Pieza, "leer"):
        _leer_orig = Pieza.leer

        def _leer(self, t=None):
            antes = len(eventos)
            _leer_orig(self, t)
            if len(eventos) > antes:
                eventos[-1]["tipo"] = "leer"

        Pieza.leer = _leer

    ClipCls = getattr(mod, clase)
    escena = ClipCls()
    escena.render()

    print(json.dumps({"eventos": eventos, "total": estado["t"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
