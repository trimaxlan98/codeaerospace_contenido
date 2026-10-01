# Presentaciones propias

Cada `<id>.json` de esta carpeta es una presentación completa que `decks_espaciales.py` construye en cualquier tema, igual que
las incluidas (seminario, comité, divulgación). Se crean y editan en la app (pestaña **Nueva presentación**) o a mano.
El formato y las reglas están en `../presentaciones_usuario.py`; los archivos que empiezan con «_» se ignoran.

## Construir
- App: pestaña *Nueva presentación* → elegir tema → **Guardar y construir**. También aparece en la pestaña *Presentaciones*.
- Terminal: `python3 decks_espaciales.py <tema> <id>` (varios temas: `orbita fisica <id>`; todos: `--todos <id>`).
- Salida: `exports/presentaciones/espaciales/<tema>/<id>_<tema>.pptx` y el guion `exports/GUION_<ID>.md`.
- Revisar: `python3 presentaciones_usuario.py --validar <id>` y `python3 pruebas_presentaciones.py --decks <id>`.

## Reglas que valida
- Portada primero, un solo cierre, y después del cierre solo diapositivas de respaldo (fuera del tiempo).
- Campos obligatorios por tipo: sección (título), texto/respaldo (título y puntos), video (pieza y título), cita (frase).
- Las piezas (`clase` y `sticker`) deben estar en el catálogo (`catalogo.py`, `catalogo_tesis.py`) y renderizadas.
- Avisos de diseño: guion vacío, más de 6 puntos, textos largos y diapositivas de solo texto sin sticker.
- `cuidado`: lo que no se puede afirmar en esa diapositiva; va a las notas del orador y al guion con ⚠️.

## Incluida
- `que_es_code.json` — «¿Qué es Co.De Aerospace?», presentación institucional (24 diapositivas, ~7.5 min) con los textos
  públicos de codeaerospace.com (consultado el 2026-09-30). Las metas de la hoja de ruta, las cifras publicadas y la sede
  y fecha de la WRC-27 llevan advertencia: confírmalas antes de presentarlas.
