"""python -m datos_orbitales [NORAD=25544]: próximos pases visibles sobre Ciudad de México (demo)."""
import sys
from datetime import datetime, timezone

from . import CDMX, obtener, pases, sello

norad = int(sys.argv[1]) if len(sys.argv) > 1 else 25544
el = obtener(norad)
print(el.nombre, "—", sello(el)["texto"], "(caché vieja)" if el.cache_vieja else "")
for p in pases(el, CDMX, datetime.now(timezone.utc), dias=3, el_min=10)[:8]:
    print(f"{CDMX.local(p.aos):%a %d %H:%M}–{CDMX.local(p.los):%H:%M} (hora local)  el_max {p.el_max:4.1f}°  {'VISIBLE' if p.visible else ''}")
