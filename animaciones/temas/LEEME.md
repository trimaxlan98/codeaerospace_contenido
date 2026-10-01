# Temas de las presentaciones espaciales

Cada archivo de esta carpeta (salvo los que empiezan con `_`) registra un tema nuevo al importar `temas_espaciales.py`.
Aparece solo en `python3 decks_espaciales.py --lista`, en la app (pestaña Presentaciones) y en el muestrario.

## 1. Tema derivado (JSON) — lo más rápido
`python3 temas_espaciales.py --nuevo aurora --base orbita --tinte 140 --nombre Aurora` o «Nuevo tema…» en la app.
Genera `aurora.json`. Puedes editarlo a mano:

```json
{
  "id": "aurora", "nombre": "Aurora", "base": "orbita", "tinte": 140,
  "descripcion": "Órbita girada al verde",
  "color": {"acento": "#7CFFB2"},          // opcional: reemplaza colores de la paleta (tinta, tenue, acento, acento2, calido, linea, panel)
  "fuentes": {"titulo": "Orbitron"},       // opcional: titulo, display, cuerpo, etiqueta (nombres de Google Fonts)
  "video": "tarjeta"                       // opcional: fundido | monitor | tarjeta (cómo se enmarca el video)
}
```
`tinte` gira el matiz (grados) del fondo y de la paleta; el color al que se recolorean los videos gira igual, así el video sigue fundido con la diapositiva.
El primer uso genera sus fondos (≈3 min) y recolorea los videos (~17 s cada uno); después queda en caché.

## 2. Tema con fondo propio (Python)
`temas/mi_tema.py`:

```python
import fondos_espaciales as F
from temas_espaciales import Tema
def mi_fondo(tipo, var, zona):        # tipo: portada | seccion | contenido | video | cierre → imagen HxWx3 float (0-1)
    ...                               # mira orbita() en fondos_espaciales.py; con `zona` el rectángulo del video debe quedar en la base exacta
F.registrar_generador("mi_fondo", mi_fondo)
TEMA = Tema(id="mi_tema", nombre="Mi tema", generador="mi_fondo", pantalla="#101010", video="fundido",
            fuentes=dict(titulo="…", display="…", cuerpo="…", etiqueta="…"),
            color=dict(tinta="#…", tenue="#…", acento="#…", acento2="#…", calido="#…", linea="#…", panel="#101010"))
```

## Usarlos
- Un deck: `python3 decks_espaciales.py mi_tema seminario` (añade `--en` para inglés).
- Mezclados: `python3 decks_espaciales.py --mezcla orbita,mi_tema seminario` (uno por sección).
- Instala las fuentes nuevas (`~/.local/share/fonts/codeaerospace/` y `exports/presentaciones/espaciales/fuentes/`).

## Temas por materia (incluidos como plugins Python)
`robotica` · `electronica` · `calculo` · `fisica` · `electromagnetismo` · `lunar` · `marte` · `lanzamiento` — cada uno es un archivo de
esta carpeta que importa `fondos_tematicos.py` (sus generadores de fondo se registran al importarlo) y declara un `Tema(...)`. Sirven de
modelo para uno propio: copia uno, cambia el `generador` (o deriva con JSON) y las fuentes.

## Fuentes de un tema nuevo
`python3 instalar_fuentes.py` instala las de todos los temas registrados que falten (Google Fonts, con el nombre de familia corregido:
400 → «Familia» Regular, 700 → Bold). También `python3 instalar_fuentes.py "Teko:400,700"`. Sin esto PowerPoint, LibreOffice y Manim
no encuentran la familia por su nombre (la API de Google entrega las variables con el nombre de la instancia, «Oxanium ExtraLight»).

## Fuente y colores dentro de los videos (Manim)
`Tema.manim` = `dict(FUENTE, FUENTE_CIFRA, PESO_CIFRA, ESCALA_TEXTO, FONDO, TINTA, TENUE, C_EJE, C_TIERRA, C_TIERRA_2, C_SAT, C_ANT,
C_CIELO, C_MAL, C_OK, C_PANEL)`. `FONDO` debe ser igual a `pantalla`. `ESCALA_TEXTO` = ancho de Carlito / ancho de la fuente (mídelo con PIL
sobre un texto en español; las anchas, como Jura o Fraunces, van de 0.8 a 0.9). Se renderiza con
`TEMA_VISUAL=<id> ./render_todo.sh oscuro <archivo>.py` a `exports/<archivo>/t_<id>/`. El texto de Manim se dibuja 4× más grande y se
reduce (code_lib.py, `_SUPER`) porque a tamaños chicos Pango deja huecos entre letras.

## Medidas del ajuste de texto de las diapositivas
`ancho_car` (titulo, cuerpo) ≈ ancho medio del carácter × 1.10 (título en negrita) y × 1.17 (cuerpo); `k_titulo` ≈ 0.455 / ancho medio del título
(entre 0.9 y 1.25). Mide con `ImageFont.getlength` sobre una frase en español y compara con Rajdhani (0.399 → 0.44) y DM Sans (0.447 → 0.52).
