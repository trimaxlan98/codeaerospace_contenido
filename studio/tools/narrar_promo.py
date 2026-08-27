#!/usr/bin/env python3
"""Narra un promo de redes: el texto lo escribimos nosotros, Gemini lo dice.

Diferencia con `guiones.py`: alli Gemini ESCRIBE el guion de un clip de
curso a partir del script y lo ajusta a la duracion. Un promo dura 12
segundos y cada palabra esta contada, asi que el texto va escrito a mano en
el manifiesto y aqui solo se sintetiza y se ALINEA: cada seccion cae en el
instante visual que le toca (`t_inicio`), no de corrido.

    studio/backend/venv/bin/python studio/tools/narrar_promo.py \
        studio/content/promos/<slug> voz.wav
    ... --video video.mp4   ajusta el limite a la duracion real del render
    ... --limite 12.0       el mismo limite sin tener que subir el mp4
    ... --voz Kore          voz prebuilt (defecto: la del manifiesto/Charon)

Necesita las credenciales de Vertex (`/etc/manimstudio/gcp-key.json`), que
solo estan en el VPS: la sintesis se hace alli y el wav se baja.

El manifiesto lleva el bloque:

    "voz": {
      "voz": "Charon",
      "secciones": [{"t_inicio": 0.9, "texto": "Cada semilla ..."}]
    }
"""

import argparse
import json
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

from app.narracion import VertexNarrador, duracion_mp4, sintetizar  # noqa: E402

DEFAULT_KEY = "/etc/manimstudio/gcp-key.json"


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("promo_dir", type=Path)
    p.add_argument("salida", type=Path, help="wav de destino")
    p.add_argument("--video", type=Path, default=None)
    p.add_argument("--limite", type=float, default=None,
                   help="duracion del video en segundos (evita subir el mp4)")
    p.add_argument("--voz", default=None)
    args = p.parse_args()

    manifiesto = json.loads((args.promo_dir / "promo.json").read_text())
    spec = manifiesto.get("voz")
    if not spec or not spec.get("secciones"):
        sys.exit(f"{args.promo_dir}/promo.json no tiene bloque 'voz'")

    secciones = [{"texto": s["texto"], "t_inicio": float(s["t_inicio"])}
                 for s in spec["secciones"]]
    limite = args.limite
    if limite is None and args.video:
        limite = duracion_mp4(args.video)
    if limite is None:
        limite = manifiesto.get("duracion_objetivo")

    key_path = Path(os.environ.get("MS_GCP_KEY_PATH", DEFAULT_KEY))
    vertex = VertexNarrador(
        key_path,
        os.environ.get("MS_GCP_LOCATION", "us-central1"),
        os.environ.get("MS_GEMINI_MODEL_DEEP", "gemini-2.5-pro"),
        os.environ.get("MS_GEMINI_MODEL_TTS",
                       "gemini-2.5-flash-preview-tts"))

    voz = args.voz or spec.get("voz") or os.environ.get("MS_TTS_VOICE",
                                                        "Charon")
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    dur = sintetizar(vertex, secciones, voz, args.salida,
                     limite_s=float(limite) if limite else None)
    print(f"{args.salida}  {dur:.2f} s  (voz {voz}, limite "
          f"{float(limite):.2f} s)" if limite else
          f"{args.salida}  {dur:.2f} s  (voz {voz})")
    if limite and dur > float(limite) + 0.05:
        print(f"AVISO: la voz ({dur:.2f} s) no cabe en el video "
              f"({float(limite):.2f} s): acorta el texto del manifiesto")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
