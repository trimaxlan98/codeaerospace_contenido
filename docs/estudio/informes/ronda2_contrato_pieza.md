# Ronda 2: el contrato `pieza.json` y la CLI `codeae`

Fecha: 2026-10-02. Rol: arquitectura. Alcance: solo lectura del repo; este documento es lo único escrito. No se implementó nada y no se ejecutó ningún render.

Qué se leyó: `exports/estudio/informes/ronda1_motor.md` y `ronda1_producto.md`; `studio/content/animations/experimentacion/33-reels-promo.py` y `34-logo-entornos.py`; `studio/content/manim_extensions/{reels_promo,marca_aerospace,marca_vertical}.py` (funciones citadas); `studio/tools/{sonido_marca,sonido_reels,verificar_loop}.py`; `redes/carruseles/{ESQUEMA.md,motor_carrusel.py}` y `specs/divulgacion-orbital/doppler-curva-en-s.json`; `animaciones/{presentaciones_usuario,fondos_a_medida,decks_espaciales,temas_espaciales}.py` y `presentaciones/que_es_code.json`; `marca/{paleta.json,logo_entornos.py,renderizar_*.sh}`.

Estado del entorno verificado: `manim 0.21.0` instalado; **`pytest` y `jsonschema` NO están instalados** en el Python del sistema (el plan de pruebas lo tiene en cuenta, paso 0). `exports/CIFRAS_A_REVISAR.md` existe (es la semilla del registro de cifras).

Observación sobre el árbol actual frente a la ronda 1: `sonido_reels.py` ya usa semilla por reel (`zlib.crc32(nombre)`, `main()` l. ~152) y un colchón de ciclos enteros (`colchon`, l. ~52), y `sonido_marca.mezclar` también siembra por escena. Este diseño da por hecho ese arreglo (ronda 1, M1) y no lo repite. Lo que sigue vigente de la ronda 1: D1 a D4 (los tiempos del audio se escriben dos veces), D8 (tres zonas seguras), D10 (tres `una()` copiados) y el `RNG` global de módulo (`sm.RNG`, `RNG`), que el contrato resuelve pasando el generador explícito.

---

## 0. Decisiones de diseño (lo que condiciona todo lo demás)

1. **Una pieza es una fuente; un entregable es una derivación.** `pieza.json` describe la idea (qué se dice, con qué cifras, en qué tiempos). El entregable es `pieza × formato × idioma × variante` y se identifica por una huella (hash) de sus entradas. Nada se edita en el entregable.
2. **El contrato declara lo que audio y video comparten; no intenta declarar el dibujo.** Los dibujos generativos (cascada del Doppler, osciloscopio, antena) seguirán siendo Python; el JSON entrega los parámetros y los tiempos. Esto es lo que hace viable migrar sin reescribir (ronda 1, M10: «un hueco `capa_central` en Python»).
3. **Una sola línea de tiempo, dos consumidores.** El compilador `codeae.tiempo` resuelve la cronología (anclas, ciclos, repeticiones) a segundos en un `cronologia.json`. Manim (vía `codeae.runtime`) y el sintetizador de audio leen ese mismo objeto. Para los bloques de marca cuyo interior no se declara (`animar_entrada`), el video publica **marcas medidas** y el audio las consume (ronda 1, M3); la pieza ancla sus eventos a esas marcas por nombre.
4. **Tres niveles de adopción de la línea de tiempo**, para migrar sin romper: nivel 0 (adaptador: la pieza apunta a la escena y al guion de audio existentes, sin eventos), nivel 1 (la pieza declara ventanas y eventos; escena y audio los leen), nivel 2 (los sonidos se anclan a hitos de bloques de marca). Cada pieza declara su nivel en `motor.nivel_tiempo` y el validador exige coherencia.
5. **Rigor como dato, no como prosa.** Cada cifra visible es una entrada del registro `cifras` con valor, unidad, tipo, fuente, fecha de consulta y revisor. Los textos la citan con `{{cifra:id}}`. El estado `aprobada` y `publicar-paquete` se bloquean si falta algo. Sustituye a `validar()` de `motor_carrusel.py` (que solo busca `20\d\d` en la nota, l. ~575) y a la lista libre `cuidado`.
6. **Formatos por catálogo, no por pieza.** `9x16`, `4x5`, `16x9` están definidos una vez (`codeae/formatos.json`: píxeles, fps, zona segura, adaptación). Esto elimina D8 (tres zonas seguras) y el truco `-r 1080,1920` de los `.sh`.
7. **Compatibilidad total hacia atrás.** Los formatos existentes (spec de carrusel, `presentaciones/*.json`, escenas `30–34`) no se reescriben: se importan con adaptadores y se exportan de vuelta idénticos (prueba de ida y vuelta). Las salidas antiguas se mantienen como enlaces (`--compat`).
8. **Determinismo por clave.** Toda aleatoriedad (audio, fondos, ráfagas) se siembra con `crc32(f"{pieza.id}/{evento.id}")` y se pasa explícita. Rehacer un entregable no cambia otro.

---

## 1. Modelo conceptual

```
piezas/<serie>/<id>.json  ──validar──►  pieza resuelta (variante + idioma + formato aplicados, textos y cifras sustituidos)
                                              │
              ┌───────────────────────────────┼─────────────────────────────────┐
              ▼                               ▼                                 ▼
     codeae.tiempo.compilar            fondo (fondo_a_medida)           kit de marca (kit.json)
     → cronologia.json (segundos)             │                                 │
        │               │                     └────────────┬────────────────────┘
        ▼               ▼                                  ▼
 codeae.runtime     codeae.audio                    render (adaptador por tipo)
 (lo leen las       (sfx registrados,               manim | carrusel | pptx | poster
  escenas Manim)     RNG por evento)                       │
        │               │                                  ▼
        └──► video mudo + marcas.json ──► audio ──► mux ──► verificar ──► miniatura ──► paquete
```

### 1.1 Tipos de pieza

| `tipo` | Qué es hoy | Contenido | Adaptador |
|---|---|---|---|
| `reel_loop` | `ReelOrbitEye`, `ReelATP`, `ReelModelo` (`33-reels-promo.py`) | `lineatiempo` cíclica | `manim` |
| `video_marca` | `30`, `32`, `34` (logo, rótulos, `LogoEntorno*`) | `lineatiempo` lineal | `manim` |
| `video` | cursos, promos (`render_promo.py`, `render_vertical.py`) | `lineatiempo` lineal | `manim` |
| `carrusel` | `redes/carruseles/specs/**/*.json` (28 specs) | `unidades` (láminas) | `carrusel` (`motor_carrusel.renderizar`) |
| `presentacion` | `animaciones/presentaciones/*.json` | `unidades` (diapositivas) | `pptx` (`decks_espaciales.construir`) |
| `poster` | `fondos_a_medida` + `marca/logo_entornos.py` | una `unidad` (imagen fija) | `poster` |

### 1.2 Coordenadas de tiempo

`tiempo.reloj` puede ser `"video"` (los tiempos son segundos desde el primer cuadro) o `"ciclo"` (los tiempos son fase del ciclo en `[0, T)`, y el video empieza en la fase `desfase`). Es la convención que ya usan `sonido_reels.py` (eventos en fase de ciclo, rotados luego por `master(m, desfase)`) y `reels_promo.Reloj(escena, periodo, desfase)`. Con `reloj:"ciclo"` el instante de video de un evento es `(t − desfase) mod T`, y el compilador guarda ambos (`t_ciclo`, `t_video`).

### 1.3 Anclas

Un evento se ubica con `t` (absoluto en su reloj) o con `ancla: {evento, hito, desfase}`. `hito` es `inicio`, `fin` o el nombre de una marca publicada por un bloque de marca (por ejemplo `entrada.luna_llega`). El compilador ordena topológicamente, falla si hay ciclos de dependencia (E020) y, para los hitos de bloques, usa primero la tabla estática del bloque (`codeae/bloques.json`, validada contra las marcas medidas por una prueba dorada) y luego, en el paso de audio, las marcas reales del video (gana lo medido).

---

## 2. El esquema `pieza.json` (versión 1)

### 2.1 Campos de primer nivel (tabla)

| Campo | Obligatorio | Tipo | Descripción |
|---|---|---|---|
| `esquema` | sí | `1` | Versión del contrato. |
| `id` | sí | kebab `^[a-z0-9][a-z0-9-]{1,60}$` | Identidad única; nombre de carpeta y de archivo. Los ids heredados con `_` (presentaciones) se guardan en `motor.id_legado`. |
| `tipo` | sí | enum | Ver 1.1. |
| `serie` | no | texto kebab | Agrupa (`divulgacion-orbital`, `reels-promo`...). Hoy es la carpeta de `specs/`. |
| `titulo` | sí | Texto | Título interno/editorial (no es necesariamente el rótulo en pantalla). |
| `estado` | no (`borrador`) | enum | `borrador` → `revision` → `aprobada` → `publicada` → `archivada`. |
| `revision` | no | lista | `{quien, fecha, nota}`: bitácora de revisiones. |
| `privacidad` | sí | `publica`/`interna`/`privada` | `publica` activa el filtro anti-tesis (ver 2.7). |
| `idiomas` | sí | `{base, salidas[]}` | `base` es el idioma de los textos literales; `salidas` los que se renderizan. |
| `formatos` | sí | lista de ids (`9x16`, `4x5`, `16x9`) o mapa `id → ajustes` | Los ajustes (`fps`, `calidad`, `adaptacion`) sobrescriben el catálogo. |
| `tema` | no | objeto | Marca, entorno espacial, fondo, modo claro/oscuro, acento. |
| `motor` | sí | objeto | Adaptador y su entrada (escena Manim, spec de carrusel, temas de pptx...). |
| `tiempo` | videos | objeto | `fps`, `duracion`, `reloj`, `ciclo{T, desfase}`. |
| `lineatiempo` | videos | lista de Evento | Eventos con tiempo → visual y sonido. |
| `unidades` | carrusel/presentación/póster | lista de Unidad | Láminas o diapositivas, con los campos que ya usan los motores. |
| `textos` | no | mapa `id → Texto` | Textos reutilizables y bilingües, referenciables como `@id`. |
| `cifras` | no | mapa `id → Cifra` | Registro de rigor (ver 2.4). |
| `fuentes` | no | mapa `id → Fuente` | Documentos de origen (título, URL, fecha de consulta, licencia). |
| `sellos` | no | lista de Sello | Ilustración/simulación/grabación/beta/meta con alcance. |
| `cuidado` | no | lista | `{texto, bloquea, resuelto, fuente}`: lo que había en `cuidado[]`, ahora con consecuencia. |
| `audio` | no | objeto | `modo` (`sintetico`/`voz`/`mudo`), `perfil` de masterización, `semilla_base`. |
| `variantes` | no | lista | A/B (una variable) o catálogo (un eje). |
| `publicacion` | no | objeto | Cuenta, plataformas, pie, hashtags, alt, miniatura, créditos, programación. |
| `verificaciones` | no | objeto | Umbrales propios (loop, duración, costura de audio, zona segura). |
| `x-*` | no | libre | Extensiones (no validadas). |

### 2.2 JSON Schema (draft 2020-12, núcleo)

Lo que no se puede expresar en JSON Schema (referencias cruzadas, aritmética de cifras, ciclos de anclas) está en 2.8 como reglas semánticas con código.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "codeae/pieza/1",
  "title": "Pieza de Co.De Aerospace",
  "type": "object",
  "required": ["esquema", "id", "tipo", "titulo", "privacidad", "idiomas", "formatos", "motor"],
  "additionalProperties": false,
  "patternProperties": { "^x-": {} },
  "properties": {
    "esquema": { "const": 1 },
    "id": { "type": "string", "pattern": "^[a-z0-9][a-z0-9-]{1,60}$" },
    "tipo": { "enum": ["reel_loop", "video_marca", "video", "carrusel", "presentacion", "poster"] },
    "serie": { "type": "string", "pattern": "^[a-z0-9][a-z0-9-]{0,40}$" },
    "titulo": { "$ref": "#/$defs/Texto" },
    "estado": { "enum": ["borrador", "revision", "aprobada", "publicada", "archivada"], "default": "borrador" },
    "revision": { "type": "array", "items": { "type": "object", "required": ["quien", "fecha"],
      "properties": { "quien": { "type": "string" }, "fecha": { "$ref": "#/$defs/Fecha" }, "nota": { "type": "string" } } } },
    "privacidad": { "enum": ["publica", "interna", "privada"] },
    "idiomas": { "type": "object", "required": ["base"], "additionalProperties": false,
      "properties": { "base": { "$ref": "#/$defs/Idioma" },
                      "salidas": { "type": "array", "items": { "$ref": "#/$defs/Idioma" }, "uniqueItems": true, "minItems": 1 } } },
    "formatos": { "oneOf": [
      { "type": "array", "items": { "$ref": "#/$defs/FormatoId" }, "uniqueItems": true, "minItems": 1 },
      { "type": "object", "propertyNames": { "$ref": "#/$defs/FormatoId" },
        "additionalProperties": { "$ref": "#/$defs/AjusteFormato" } } ] },
    "tema": { "$ref": "#/$defs/Tema" },
    "motor": { "$ref": "#/$defs/Motor" },
    "tiempo": { "$ref": "#/$defs/Tiempo" },
    "lineatiempo": { "type": "array", "items": { "$ref": "#/$defs/Evento" } },
    "unidades": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/Unidad" } },
    "textos": { "type": "object", "propertyNames": { "$ref": "#/$defs/IdLocal" }, "additionalProperties": { "$ref": "#/$defs/Texto" } },
    "cifras": { "type": "object", "propertyNames": { "$ref": "#/$defs/IdLocal" }, "additionalProperties": { "$ref": "#/$defs/Cifra" } },
    "fuentes": { "type": "object", "propertyNames": { "$ref": "#/$defs/IdLocal" }, "additionalProperties": { "$ref": "#/$defs/Fuente" } },
    "sellos": { "type": "array", "items": { "$ref": "#/$defs/Sello" } },
    "cuidado": { "type": "array", "items": { "type": "object", "required": ["texto"],
      "properties": { "texto": { "$ref": "#/$defs/Texto" }, "bloquea": { "type": "boolean", "default": false },
                      "resuelto": { "type": "boolean", "default": false }, "fuente": { "type": "string" } } } },
    "audio": { "$ref": "#/$defs/Audio" },
    "variantes": { "type": "array", "items": { "$ref": "#/$defs/Variante" } },
    "publicacion": { "$ref": "#/$defs/Publicacion" },
    "verificaciones": { "$ref": "#/$defs/Verificaciones" }
  },
  "allOf": [
    { "if": { "properties": { "tipo": { "enum": ["reel_loop", "video_marca", "video"] } } },
      "then": { "required": ["tiempo", "lineatiempo"] } },
    { "if": { "properties": { "tipo": { "const": "reel_loop" } } },
      "then": { "properties": { "tiempo": { "required": ["ciclo"] } } } },
    { "if": { "properties": { "tipo": { "enum": ["carrusel", "presentacion", "poster"] } } },
      "then": { "required": ["unidades"] } }
  ],
  "$defs": {
    "Idioma": { "type": "string", "pattern": "^[a-z]{2}$" },
    "FormatoId": { "enum": ["9x16", "4x5", "16x9"] },
    "IdLocal": { "type": "string", "pattern": "^[a-z][a-z0-9_]{0,40}$" },
    "Fecha": { "type": "string", "pattern": "^20\\d\\d-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])$" },
    "Texto": { "description": "Cadena en el idioma base, mapa idioma→cadena, o referencia '@id' a pieza.textos. Admite {{cifra:id}}, [[cian]] y **negrita**.",
      "oneOf": [ { "type": "string" },
                 { "type": "object", "minProperties": 1, "propertyNames": { "$ref": "#/$defs/Idioma" },
                   "additionalProperties": { "type": "string" } } ] },
    "AjusteFormato": { "type": "object", "additionalProperties": false,
      "properties": { "fps": { "type": "integer", "minimum": 1, "maximum": 60 },
                      "calidad": { "enum": ["borrador", "ql", "qm", "qh"] },
                      "adaptacion": { "enum": ["camara", "escena_propia", "recorte", "panoramica"] },
                      "escena": { "type": "string" } } },
    "Tema": { "type": "object", "additionalProperties": false,
      "properties": {
        "marca": { "type": "string", "default": "aerospace" },
        "entorno": { "type": ["string", "null"], "description": "id de temas_espaciales (orbita, nebulosa, fisica...)" },
        "fondo": { "type": "object", "additionalProperties": false,
          "properties": { "tipo": { "enum": ["portada", "seccion", "contenido", "cierre"] },
                          "var": { "type": "integer", "minimum": 0, "maximum": 3 },
                          "ventana": { "type": ["number", "null"] }, "atenuar": { "type": "number" } } },
        "modo": { "enum": ["auto", "oscuro", "claro"], "default": "auto" },
        "acento": { "type": "string", "description": "'auto' (acento del entorno), id del kit o #RRGGBB", "default": "auto" } } },
    "Motor": { "type": "object", "required": ["adaptador"], "additionalProperties": false,
      "properties": {
        "adaptador": { "enum": ["manim", "carrusel", "pptx", "poster"] },
        "nivel_tiempo": { "enum": [0, 1, 2], "default": 1 },
        "archivo": { "type": "string", "description": "Ruta relativa al repo (escena Manim)" },
        "escena": { "oneOf": [ { "type": "string" },
                               { "type": "object", "propertyNames": { "$ref": "#/$defs/FormatoId" }, "additionalProperties": { "type": "string" } } ] },
        "central": { "type": "string", "description": "Función Python del dibujo central, 'modulo:funcion'" },
        "temas": { "type": "array", "items": { "type": "string" } },
        "id_legado": { "type": "string" },
        "legado": { "type": "object", "description": "Rutas de salida antiguas a mantener con --compat",
                    "additionalProperties": { "type": "string" } },
        "extra": { "type": "object" } } },
    "Tiempo": { "type": "object", "required": ["fps"], "additionalProperties": false,
      "properties": {
        "fps": { "type": "integer", "minimum": 1, "maximum": 60 },
        "duracion": { "oneOf": [ { "type": "number", "exclusiveMinimum": 0 }, { "const": "auto" } ] },
        "reloj": { "enum": ["video", "ciclo"], "default": "video" },
        "ciclo": { "type": "object", "required": ["T"], "additionalProperties": false,
                   "properties": { "T": { "type": "number", "exclusiveMinimum": 0 },
                                   "desfase": { "type": "number", "minimum": 0, "default": 0 } } } } },
    "Hito": { "type": "string", "pattern": "^(inicio|fin|[a-z][a-z0-9_]*)$" },
    "Evento": { "type": "object", "required": ["id"], "additionalProperties": false,
      "anyOf": [ { "required": ["t"] }, { "required": ["ancla"] } ],
      "properties": {
        "id": { "$ref": "#/$defs/IdLocal" },
        "t": { "type": "number", "minimum": 0 },
        "ancla": { "type": "object", "required": ["evento"], "additionalProperties": false,
                   "properties": { "evento": { "$ref": "#/$defs/IdLocal" }, "hito": { "$ref": "#/$defs/Hito" },
                                   "desfase": { "type": "number", "default": 0 } } },
        "dur": { "oneOf": [ { "type": "number", "exclusiveMinimum": 0 }, { "enum": ["ciclo", "fin"] } ] },
        "repite": { "type": "object", "required": ["cada", "n"], "additionalProperties": false,
                    "properties": { "cada": { "type": "number", "exclusiveMinimum": 0 }, "n": { "type": "integer", "minimum": 2 } } },
        "visual": { "$ref": "#/$defs/Visual" },
        "sonido": { "type": "array", "items": { "$ref": "#/$defs/Sonido" } },
        "sello": { "enum": ["ilustracion", "simulacion", "grabacion", "beta", "meta"] },
        "nota": { "type": "string" } } },
    "Visual": { "type": "object", "required": ["efecto"], "additionalProperties": false,
      "properties": { "efecto": { "type": "string", "pattern": "^[a-z][a-z0-9_.]*$" },
                      "texto": { "$ref": "#/$defs/Texto" }, "args": { "type": "object" } } },
    "Sonido": { "type": "object", "additionalProperties": false,
      "oneOf": [ { "required": ["sfx"] }, { "required": ["bloque"] } ],
      "properties": {
        "sfx": { "type": "string", "pattern": "^[a-z][a-z0-9_]*$" },
        "bloque": { "type": "string", "description": "Partitura por defecto de un bloque de marca" },
        "dt": { "type": "number", "default": 0 },
        "en": { "type": "string", "description": "Ancla de audio a un hito 'evento.hito' (nivel 2)" },
        "tono": { "type": "object", "additionalProperties": false,
                  "properties": { "penta": { "type": "integer", "minimum": 0, "maximum": 5 },
                                  "semitonos": { "type": "number" }, "octava": { "type": "integer" }, "hz": { "type": "number" } } },
        "d": { "type": "number", "exclusiveMinimum": 0 },
        "vol": { "type": "number", "minimum": 0, "maximum": 1 },
        "pan": { "type": "number", "minimum": -1, "maximum": 1 },
        "args": { "type": "object" } } },
    "Unidad": { "type": "object", "required": ["id", "tipo"],
      "description": "Lámina o diapositiva. Los demás campos son los del motor (titulo, cuerpo, items, imagen, cifra...) y se validan por tipo.",
      "properties": { "id": { "$ref": "#/$defs/IdLocal" }, "tipo": { "type": "string" },
                      "sello": { "enum": ["ilustracion", "simulacion", "grabacion", "beta", "meta"] },
                      "cifra": { "oneOf": [ { "type": "string" }, { "type": "object", "required": ["ref"],
                                 "properties": { "ref": { "$ref": "#/$defs/IdLocal" } } } ] } },
      "additionalProperties": true },
    "Cifra": { "type": "object", "required": ["tipo", "valor", "mostrar"], "additionalProperties": false,
      "properties": {
        "tipo": { "enum": ["medida", "citada", "calculada", "estandar", "ilustrativa", "meta", "propia"] },
        "valor": { "type": ["number", "string"] },
        "unidad": { "type": "string" },
        "mostrar": { "type": "string", "description": "Cómo aparece en pantalla (redondeo incluido)" },
        "cifras_significativas": { "type": "integer", "minimum": 1 },
        "formula": { "type": "string", "description": "Solo calculada: expresión aritmética sobre otras cifras (@id)" },
        "entradas": { "type": "array", "items": { "$ref": "#/$defs/IdLocal" } },
        "fuente": { "$ref": "#/$defs/IdLocal" },
        "fecha_dato": { "$ref": "#/$defs/Fecha" },
        "caduca_dias": { "type": "integer", "minimum": 1 },
        "revisada": { "type": "boolean", "default": false },
        "revisor": { "type": "string" }, "fecha_revision": { "$ref": "#/$defs/Fecha" },
        "nota": { "type": "string" } } },
    "Fuente": { "type": "object", "required": ["titulo"], "additionalProperties": false,
      "properties": { "titulo": { "type": "string" }, "url": { "type": ["string", "null"] },
                      "consultado": { "$ref": "#/$defs/Fecha" }, "licencia": { "type": "string" },
                      "tipo": { "enum": ["web", "tesis", "norma", "dato", "propia", "estandar"] },
                      "nota": { "type": "string" } } },
    "Sello": { "type": "object", "required": ["tipo", "alcance"], "additionalProperties": false,
      "properties": { "tipo": { "enum": ["ilustracion", "simulacion", "grabacion", "beta", "meta"] },
                      "alcance": { "type": "object", "additionalProperties": false,
                                   "properties": { "pieza": { "const": true }, "unidad": { "$ref": "#/$defs/IdLocal" },
                                                   "evento": { "$ref": "#/$defs/IdLocal" } } },
                      "texto": { "$ref": "#/$defs/Texto" } } },
    "Audio": { "type": "object", "additionalProperties": false,
      "properties": {
        "modo": { "enum": ["sintetico", "voz", "mudo"], "default": "sintetico" },
        "perfil": { "enum": ["bucle", "marca"], "description": "bucle = master() de sonido_reels; marca = loudnorm+alimiter de sonido_marca.mezclar" },
        "lufs": { "type": "number", "default": -17 }, "pico_db": { "type": "number", "default": -1.5 },
        "fondo": { "type": "array", "items": { "$ref": "#/$defs/Sonido" }, "description": "Capas continuas (colchón, ruido)" },
        "legado": { "type": "string", "description": "Nivel 0: 'modulo:funcion' del guion existente, p. ej. sonido_reels:atp" } } },
    "Variante": { "type": "object", "required": ["id", "tipo", "parche"], "additionalProperties": false,
      "properties": {
        "id": { "type": "string", "pattern": "^[a-z0-9]{1,12}$" },
        "tipo": { "enum": ["ab", "catalogo"] },
        "hipotesis": { "type": "string" }, "variable": { "type": "string" }, "metrica": { "type": "string" },
        "parche": { "type": "array", "minItems": 1, "items": { "type": "object", "required": ["op", "ruta"],
          "properties": { "op": { "enum": ["set", "merge", "remove"] }, "ruta": { "type": "string" }, "valor": {} } } } } },
    "Publicacion": { "type": "object", "additionalProperties": false,
      "properties": {
        "cuenta": { "type": "string" },
        "plataformas": { "type": "array", "items": { "type": "object", "required": ["id"],
          "properties": { "id": { "enum": ["instagram", "tiktok", "youtube", "x", "web", "linkedin"] },
                          "producto": { "enum": ["reel", "carrusel", "publicacion", "short", "video", "articulo"] },
                          "formato": { "$ref": "#/$defs/FormatoId" } } } },
        "pie": { "$ref": "#/$defs/Texto" },
        "hashtags": { "type": "object", "propertyNames": { "$ref": "#/$defs/Idioma" },
                      "additionalProperties": { "type": "array", "items": { "type": "string", "pattern": "^#\\S+$" }, "uniqueItems": true } },
        "alt": { "$ref": "#/$defs/Texto" },
        "fuentes_en_pie": { "type": "boolean", "default": true },
        "creditos": { "type": "array", "items": { "$ref": "#/$defs/Texto" } },
        "miniatura": { "type": "object", "additionalProperties": false,
                       "properties": { "t": { "type": "number" }, "unidad": { "$ref": "#/$defs/IdLocal" } } },
        "programacion": { "type": "object", "properties": { "no_antes_de": { "type": "string" }, "nota": { "type": "string" } } } } },
    "Verificaciones": { "type": "object", "additionalProperties": false,
      "properties": {
        "loop": { "type": "object", "properties": { "tolerancia_px": { "type": "number", "default": 2 } } },
        "duracion": { "type": "object", "required": ["esperada"], "properties": { "esperada": { "type": "number" }, "tol": { "type": "number", "default": 0.05 } } },
        "audio": { "type": "object", "properties": { "costura_max": { "type": "number", "default": 3 }, "pico_max": { "type": "number", "default": 0.95 }, "lufs_tol": { "type": "number", "default": 1.5 } } },
        "zona_segura": { "type": "boolean", "default": true } } }
  }
}
```

### 2.3 Catálogos que el esquema referencia (archivos del contrato, no de la pieza)

| Archivo | Contenido | Sustituye a |
|---|---|---|
| `codeae/formatos.json` | `9x16` 1080×1920 30 fps zona segura; `4x5` 1080×1350; `16x9` 1920×1080. La zona segura sale de `promo.SEGURA` y del kit, una sola. | `SEGURA_*` de `marca_vertical.py` l. 27–28, `FORMATOS` de `marca/logo_entornos.py`, `W, H, M` de `motor_carrusel.py` l. 39–40, `-r` de los `.sh` |
| `codeae/efectos.json` | Registro de efectos visuales: nombre → función real + esquema de `args`. | las llamadas sueltas en `33-reels-promo.py` |
| `codeae/sfx.json` | Registro de sonidos: nombre → función de `sonido_marca.py`/`sonido_reels.py` + esquema de `args`. | los diccionarios `ESCENAS`/`ESCENAS_V`/`ESCENAS_LE`/`REELS` |
| `codeae/bloques.json` | Bloques de marca: `marca.entrada_orbital` (envuelve `marca_aerospace.animar_entrada`) con sus hitos esperados y su partitura por defecto (`sonido_marca.intro`). | `animar_entrada` + `intro(m)` con tiempos copiados (D1) |
| `marca/kit.json` | Colores (marca y web, con nombres distintos para los dos «tenue»), fuentes con ruta relativa al repo, zonas seguras. | `marca/paleta.json` + constantes duplicadas (ronda 1, M4) |

Registro de efectos inicial, todos con función existente:

| `efecto` | Función real | `args` clave |
|---|---|---|
| `cabecera` | `reels_promo.cabecera(escena, kicker, titulo, n, tam)` | `kicker`, `tam`, `n` |
| `leyenda` | `reels_promo.leyenda(escena, reloj, grande, pequena, a, b, y, f, tam_g, tam_p)` | `y`, `f`, `tam_g`, `tam_p` |
| `linea_ciclica` | `reels_promo.linea_ciclica(escena, reloj, texto, a, b, y, f, tam)` | `y`, `f`, `tam` |
| `chip` | `reels_promo.chip(texto, color, tam)` | `color`, `tam`, `pos` |
| `chip_activo` | el updater `iluminar` de `ReelATP` (generalizado) | `grupo`, `indice` |
| `capa_python` | llama a `motor.central` con los eventos como parámetros | `rol` |
| `zoom_fondo` | `respirar` de `34-logo-entornos.py` | `desde`, `hasta`, `curva` |
| `halo_oscuro` | el `VGroup` de círculos de `34` | `y`, `radios`, `n`, `opacidad` |
| `bloque_marca` | `marca_aerospace.animar_entrada` | `estilo`, `acento`, `ritmo`, `altura_rel`, `y` |
| `texto_entra` | `FadeIn(_texto(...), shift=0.2*UP)` | `y`, `tam`, `peso`, `tracking`, `color` |

Registro de sonidos inicial (de `sonido_marca.py` / `sonido_reels.py`): `pluck(f, d, vol, brillo)`, `whoosh(d, f0, f1, vol, pico, q)`, `glide(f0, f1, d, vol)`, `clic(vol, f)`, `golpe(f, d, vol)`, `gota(f, d, vol)`, `servo(d, f0, f1, vol)`, `brillo(d, vol)`, `acorde(vol, d)`, `pad(d, notas, vol)`, y los continuos `colchon(notas, vol)` y `ruido_circular(lo, hi, vol)` de `sonido_reels.py`. Un sonido que no cabe en parámetros (el servo del reposicionamiento, la cascada FSK) se declara con `{"sfx":"codigo","args":{"ref":"sonido_reels:atp_servo"}}`: escape explícito, visible en el validador como deuda («sonidos en código: n»).

Notación de tono: `{"penta": i}` es `PENTA[i]`; `{"penta": i, "octava": -1}` es `PENTA[i]/2` (así suena la leyenda nueva de `modelo`); `{"semitonos": n}` es `A(n)` (`A = 440·2^(n/12)`); `{"hz": f}` es literal.

### 2.4 Registro de cifras (rigor)

Tipos de cifra y lo que exige cada uno:

| `tipo` | Qué es | Exige |
|---|---|---|
| `citada` | Cifra que da una fuente de Co.De o externa | `fuente` con `consultado`; `revisada` antes de `aprobada` |
| `medida` | Resultado propio medido (benchmark, observación) | `fuente` tipo `propia`, `fecha_dato`, `nota` con alcance (ej.: «una observación, no mediana») |
| `calculada` | Se deriva de otras cifras | `formula` + `entradas`; el validador la recalcula y compara con `valor` |
| `estandar` | Constante o valor de libro | `fuente` tipo `estandar`; sin URL obligatoria |
| `ilustrativa` | Número de un dibujo o simulación que no es dato | sello `ilustracion` o `simulacion` en su alcance; no puede citarse como hecho |
| `meta` | Objetivo, no hecho (WRC-27, metas del sitio) | sello `meta` en su alcance |
| `propia` | Declaración de Co.De sin verificación externa | `cuidado` asociado |

Reglas: toda cifra que aparece en pantalla, en el pie o en un sticker debe estar en el registro (la forma de citarla en textos es `{{cifra:id}}`, que se sustituye por `mostrar`); `mostrar` debe coincidir con `valor` redondeado a `cifras_significativas`; una cifra con `caduca_dias` pasa a aviso al vencer (`fecha_dato`/`consultado` + días), p. ej. las de eventos u observaciones (`ESQUEMA.md`: «las de eventos/observaciones envejecen»); y `estado: aprobada` exige `revisada: true` con `revisor` y `fecha_revision` en todas. Esto cubre la semilla `exports/CIFRAS_A_REVISAR.md` y el aviso «cifra sin fecha» de `motor_carrusel.validar`.

### 2.5 Sellos

El sello tiene alcance: toda la pieza (`pieza:true`), una unidad (lámina/diapositiva) o un evento (intervalo del video). Mapeo a lo existente: en carrusel, `unidad.sello` = `"sello"` de `motor_carrusel.sello()` (etiqueta ámbar abajo a la derecha); en video, el sello de pieza o de evento se dibuja con el efecto `chip` (hoy `chip("Trazas ilustrativas", AMBAR, 22)` en `ReelATP`, `chip("Demo con grabación IQ", CIAN, 24)` en `ReelOrbitEye`). El texto del chip sale de un catálogo por idioma (`codeae/sellos.json`: `ilustracion` → «Ilustración» / «Illustration», etc.) salvo que la pieza dé `texto`. Un sello que depende de una cifra (`ilustrativa`) hace que el validador exija su presencia (E033).

### 2.6 Variantes

Dos clases, ambas como parches (la idea de `motor_carrusel.expandir_variantes`, generalizada a cualquier pieza):

- `ab`: experimento de **una** variable. `variable` nombra qué cambia (`gancho`, `fondo`, `miniatura`, `musica`...), `hipotesis` y `metrica` son obligatorias en la práctica (aviso si faltan). El validador cuenta las rutas tocadas por el parche y las agrupa por variable: tocar dos variables dispara E080 (la regla de `ESQUEMA.md`: «cambia UNA variable por variante»).
- `catalogo`: un eje que genera piezas hermanas (los 10 `LogoEntorno*` de `34-logo-entornos.py` varían solo `tema.entorno`). No es un experimento; no exige hipótesis.

Rutas del parche: notación de puntos con selector por id, `unidades[id=u1].titulo`, `lineatiempo[id=ley1].visual.texto`, `tema.entorno`. Los selectores por id sobreviven a reordenar. Cada variante produce una pieza `<id>-<sufijo>` con `variante_de`, su propia carpeta de salida y su propia huella (compatible con `<id>-b` de `ESQUEMA.md`).

### 2.7 Privacidad

`privacidad: "publica"` activa dos filtros en el validador, que sustituyen al `PROHIBIDO_IMAGEN` de subcadenas de `motor_carrusel.py` l. 63 (débil según ronda 1, §2.4):

- E040: cualquier recurso (sticker, imagen, video, texto) cuyo **hash** esté en `codeae/privado.json` (lista generada a partir de los stickers y videos de la tesis, no por nombre) o cuyo origen sea una `fuente` de tipo `tesis`.
- E041: rutas de imagen se resuelven con `Path.resolve()` y deben caer bajo `exports/png/stickers_finales/t_orbita/`, `marca/` o `piezas/_recursos/`; `..` y rutas absolutas ajenas fallan.

### 2.8 Reglas semánticas del validador (códigos estables)

Errores (bloquean el render): E001 id distinto del nombre de archivo; E010 efecto o sfx desconocido; E011 `args` no cumplen el esquema del efecto; E020 ancla irresoluble o ciclo; E021 evento fuera de `[0, T)` en reloj de ciclo; E022 dos textos del mismo carril se solapan (para `leyenda`/`linea_ciclica` se usa `ventana_texto`, que no admite solape); E030 cifra o fuente citada que no existe; E031 `mostrar` no coincide con `valor` redondeado; E032 cifra calculada cuya fórmula no reproduce `valor`; E033 cifra `ilustrativa`/`meta` sin sello en su alcance; E040/E041 privacidad; E050 idioma de salida sin texto; E060 formato sin escena ni adaptación; E070 pie > 2 200 caracteres; E071 hashtags > 30; E080 variante A/B que toca más de una variable; E090 `nivel_tiempo` 1 o 2 sin `lineatiempo` o con eventos sin consumidor (no hay efecto ni sonido).

Avisos: W001 textos largos según tipo de lámina (los límites de `ESQUEMA.md`); W010 cifra caducada o por caducar; W011 cifra sin revisión; W020 sonidos en código (deuda); W030 más de 6 hashtags (recomendación de `ESQUEMA.md`); W040 sin `alt`; W050 `fuente` sin `consultado`.

Gates (los usan `render --para-publicar` y `publicar-paquete`): estado `< aprobada`, E*, cifras sin revisar, `cuidado` con `bloquea:true` y `resuelto:false`, verificación en rojo.

---

## 3. Línea de tiempo declarativa: cómo audio y video salen de la misma fuente

### 3.1 Anatomía de un evento

```json
{ "id": "ctrl_pid", "t": 2.2, "dur": 2.2,
  "visual": { "efecto": "chip_activo", "args": { "grupo": "controladores", "indice": 1 } },
  "sonido": [ { "sfx": "pluck", "dt": 0.1, "tono": { "penta": 1 }, "d": 1.3, "vol": 0.28, "pan": -0.2 },
              { "sfx": "clic", "dt": 0.1, "vol": 0.5 } ] }
```

Un mismo evento lleva su parte visual y su parte sonora: si se mueve `t` o `dur`, se mueven ambas. Eso es exactamente lo que hoy está escrito dos veces (D1, D2: `CONTROLADORES` en `33-reels-promo.py` l. 138–142 frente a `for i, a in enumerate((11.5, 2.2, 4.4, 6.6, 8.8))` en `sonido_reels.py:atp`). En reloj de ciclo, `dur` con `t + dur > T` envuelve (la ventana de PD, 11.5 a 2.2, es `t=11.5, dur=2.7`).

### 3.2 Compilación

`codeae.tiempo.compilar(pieza, formato, idioma) -> Cronologia` (módulo puro, sin Manim, solo numpy y la biblioteca estándar; ahí se mudan `suave`, `ventana`, `ventana_texto` de `reels_promo.py` y `doppler_d`/`doppler_amp` de `33`, que hoy están copiadas en `sonido_reels.py`: D3):

1. Sustituye textos y cifras, resuelve anclas, expande `repite` (`{cada:1.9, n:6}` → 6 instancias `haz_tics#0..5`), aplica `desfase` del ciclo.
2. Emite `cronologia.json`: lista ordenada de `{id, t_ciclo, t_video, dur, visual, sonido[]}` y la tabla `ventanas` (`id → [a, b]`) que usan los updaters.
3. Fija la semilla por evento: `crc32(f"{pieza.id}/{evento.id}")`. Los sfx reciben `rng` explícito (ya no `sm.RNG` ni `RNG` globales).

### 3.3 Cómo la leen las escenas Manim (contrato `codeae.runtime`)

El render exporta `CODEAE_PIEZA` (ruta de la pieza resuelta), `CODEAE_FORMATO`, `CODEAE_IDIOMA`. La escena queda casi igual; cambian las constantes:

```python
from codeae.runtime import cargar            # la escena añade REPO a sys.path desde __file__ (como ya hace 34)
class ReelATP(Scene):
    def construct(self):
        P = cargar()                         # Cronologia + textos + cifras ya sustituidos
        reloj = Reloj(self, P.T, desfase=P.desfase)
        ...
        for ev in P.eventos("controladores"):                     # antes: CONTROLADORES
            linea_ciclica(self, reloj, ev.texto, *ev.ventana, -7.05, f=0.35, tam=44)
        amp = P.parametro("error_banda.amp")                      # antes: tabla en 33 l. 138–142
```

`P.ventana(id)` devuelve `(a, b)` en fase de ciclo; con `ventana(t, a, b, f, T)` de `codeae.tiempo`. Con `CODEAE_PIEZA` ausente, `cargar()` carga la pieza por defecto de la escena (ejecutar la escena a mano con `manim render` sigue funcionando: mismo comportamiento que hoy).

### 3.4 Cómo lo lee el audio

`codeae.audio.sintetizar(cronologia, marcas=None)` recorre `sonido[]` de cada evento, pone cada sfx con `Circular.poner` (loop) o `Mezcla.poner` (lineal) según `tiempo.reloj`, aplica `audio.fondo` (colchón, ruido), masteriza con el perfil (`bucle` = `sonido_reels.master`; `marca` = `sonido_marca.master` + `loudnorm`) y devuelve `wav`. Si un evento usa `sonido.en = "entrada.luna_llega"`, el audio exige la marca `luna_llega` de `marcas.json` (producida por el render de la entrada orbital, M3 de la ronda 1) y falla con mensaje si falta, en vez de sonar mal.

### 3.5 Qué queda fuera de la línea de tiempo (a propósito)

La geometría de cada escena, la física (`doppler_d`, `error_banda`, `tabla_cascada`) y los sonidos continuos con modulación propia (servo del reposicionamiento) siguen en Python. Los parámetros que el audio también necesita (ventanas, amplitudes por controlador, `T`) viven en la pieza.

---

## 4. Tres ejemplos completos

Convención: `@id` es referencia a `textos`; `{{cifra:id}}` inserta `mostrar`; `\n` es salto de línea de rótulo (los mismos que usa `cabecera`). Los tiempos de ATP están en fase de ciclo.

### 4.1 (a) `ReelATP` (`33-reels-promo.py`, clase `ReelATP`, T2 = 12.0, desfase 4.0)

```json
{
  "esquema": 1,
  "id": "reel-atp-01-grado",
  "tipo": "reel_loop",
  "serie": "reels-promo",
  "titulo": "Reel · ¿Puede una antena apuntar a 0.1°?",
  "estado": "borrador",
  "privacidad": "publica",
  "idiomas": { "base": "es", "salidas": ["es"] },
  "formatos": { "9x16": { "fps": 30, "calidad": "qh", "adaptacion": "escena_propia" } },
  "tema": { "marca": "aerospace", "entorno": null, "modo": "oscuro", "acento": "cian" },
  "motor": {
    "adaptador": "manim",
    "nivel_tiempo": 1,
    "archivo": "studio/content/animations/experimentacion/33-reels-promo.py",
    "escena": { "9x16": "ReelATP" },
    "central": "33-reels-promo:ReelATP",
    "legado": {
      "video": "exports/marca-codeaerospace/reels-promo/ReelATP.mp4",
      "con_sonido": "exports/marca-codeaerospace/reels-promo/con_sonido/ReelATP.mp4"
    }
  },
  "tiempo": { "fps": 30, "duracion": 12.0, "reloj": "ciclo", "ciclo": { "T": 12.0, "desfase": 4.0 } },

  "textos": {
    "kicker": "CO.DE ATP-DT · gemelo digital",
    "titulo": "¿Puede una antena\napuntar a {{cifra:c_banda}}?",
    "montura": "Montura de 2 GDL · SGP4 → acimut/elevación",
    "ejeerror": "ERROR DE APUNTAMIENTO",
    "banda": "±{{cifra:c_banda}}",
    "pd": "Reacciona rápido al error",
    "pid": "Acumula el error pasado",
    "lqr": "Minimiza un costo óptimo",
    "hinf": "Robusto a las perturbaciones",
    "abierto": "Sin realimentación: la referencia",
    "chip_ilus": "Trazas ilustrativas"
  },

  "fuentes": {
    "f_plataformas": {
      "titulo": "codeaerospace.com/plataformas, ficha CO.DE ATP-DT (beta)",
      "url": "https://codeaerospace.com/plataformas",
      "consultado": "2026-10-01",
      "tipo": "web",
      "nota": "Beta; banco de pruebas de diseño con presupuesto de apuntamiento de 0.1°."
    }
  },
  "cifras": {
    "c_banda": {
      "tipo": "citada", "valor": 0.1, "unidad": "°", "mostrar": "0.1°",
      "fuente": "f_plataformas", "fecha_dato": "2026-10-01",
      "nota": "Presupuesto de apuntamiento de diseño del ATP-DT (beta), no un desempeño medido.",
      "revisada": false
    },
    "c_gdl": {
      "tipo": "citada", "valor": 2, "unidad": "GDL", "mostrar": "2 GDL",
      "fuente": "f_plataformas",
      "nota": "Verificar en la ficha antes de aprobar (el texto está en la escena, no se confirmó su origen).",
      "revisada": false
    }
  },
  "sellos": [
    { "tipo": "ilustracion", "alcance": { "pieza": true }, "texto": "@chip_ilus" }
  ],
  "cuidado": [
    { "texto": "ATP-DT es beta: banco de pruebas de diseño. Las trazas de error del osciloscopio son ilustrativas, no medidas.", "bloquea": false },
    { "texto": "Confirmar «2 GDL» y «SGP4» contra la ficha antes de aprobar.", "bloquea": true, "resuelto": false }
  ],

  "audio": {
    "modo": "sintetico",
    "perfil": "bucle",
    "lufs": -17,
    "pico_db": -1.5,
    "fondo": [
      { "sfx": "colchon", "vol": 0.26 },
      { "sfx": "ruido_circular", "args": { "lo": 500, "hi": 2500 }, "vol": 0.03 }
    ]
  },

  "lineatiempo": [
    { "id": "cab", "t": 0, "dur": "ciclo",
      "visual": { "efecto": "cabecera", "args": { "kicker": "@kicker", "titulo": "@titulo" } } },
    { "id": "montura", "t": 0, "dur": "ciclo",
      "visual": { "efecto": "capa_python", "texto": "@montura", "args": { "rol": "montura_y_antena" } } },
    { "id": "osciloscopio", "t": 0, "dur": "ciclo",
      "visual": { "efecto": "capa_python", "args": { "rol": "osciloscopio", "ventana_s": 4.0, "banda": "@banda", "eje": "@ejeerror" } } },
    { "id": "chip_ilus", "t": 0, "dur": "ciclo", "sello": "ilustracion",
      "visual": { "efecto": "chip", "texto": "@chip_ilus", "args": { "color": "ambar", "tam": 22, "pos": "osciloscopio.abajo_der" } } },

    { "id": "ctrl_pd", "t": 11.5, "dur": 2.7,
      "visual": { "efecto": "chip_activo", "args": { "grupo": "controladores", "indice": 0, "nombre": "PD", "amp_error": 1.35 } },
      "sonido": [ { "sfx": "pluck", "dt": 0.1, "tono": { "penta": 0 }, "d": 1.3, "vol": 0.28, "pan": -0.4 },
                  { "sfx": "clic", "dt": 0.1, "vol": 0.5 } ] },
    { "id": "ley_pd", "t": 11.5, "dur": 2.7,
      "visual": { "efecto": "linea_ciclica", "texto": "@pd", "args": { "y": -7.05, "f": 0.35, "tam": 44 } } },

    { "id": "ctrl_pid", "t": 2.2, "dur": 2.2,
      "visual": { "efecto": "chip_activo", "args": { "grupo": "controladores", "indice": 1, "nombre": "PID", "amp_error": 0.95 } },
      "sonido": [ { "sfx": "pluck", "dt": 0.1, "tono": { "penta": 1 }, "d": 1.3, "vol": 0.28, "pan": -0.2 },
                  { "sfx": "clic", "dt": 0.1, "vol": 0.5 } ] },
    { "id": "ley_pid", "t": 2.2, "dur": 2.2,
      "visual": { "efecto": "linea_ciclica", "texto": "@pid", "args": { "y": -7.05, "f": 0.35, "tam": 44 } } },

    { "id": "ctrl_lqr", "t": 4.4, "dur": 2.2,
      "visual": { "efecto": "chip_activo", "args": { "grupo": "controladores", "indice": 2, "nombre": "LQR", "amp_error": 0.50 } },
      "sonido": [ { "sfx": "pluck", "dt": 0.1, "tono": { "penta": 2 }, "d": 1.3, "vol": 0.28, "pan": 0.0 },
                  { "sfx": "clic", "dt": 0.1, "vol": 0.5 } ] },
    { "id": "ley_lqr", "t": 4.4, "dur": 2.2,
      "visual": { "efecto": "linea_ciclica", "texto": "@lqr", "args": { "y": -7.05, "f": 0.35, "tam": 44 } } },

    { "id": "ctrl_hinf", "t": 6.6, "dur": 2.2,
      "visual": { "efecto": "chip_activo", "args": { "grupo": "controladores", "indice": 3, "nombre": "H∞", "amp_error": 0.30 } },
      "sonido": [ { "sfx": "pluck", "dt": 0.1, "tono": { "penta": 3 }, "d": 1.3, "vol": 0.28, "pan": 0.2 },
                  { "sfx": "clic", "dt": 0.1, "vol": 0.5 } ] },
    { "id": "ley_hinf", "t": 6.6, "dur": 2.2,
      "visual": { "efecto": "linea_ciclica", "texto": "@hinf", "args": { "y": -7.05, "f": 0.35, "tam": 44 } } },

    { "id": "ctrl_abierto", "t": 8.8, "dur": 2.2,
      "visual": { "efecto": "chip_activo", "args": { "grupo": "controladores", "indice": 4, "nombre": "Lazo abierto", "amp_error": 0.0, "error_modo": "lazo_abierto" } },
      "sonido": [ { "sfx": "pluck", "dt": 0.1, "tono": { "penta": 4 }, "d": 1.3, "vol": 0.28, "pan": 0.4 },
                  { "sfx": "clic", "dt": 0.1, "vol": 0.5 } ] },
    { "id": "ley_abierto", "t": 8.8, "dur": 2.2,
      "visual": { "efecto": "linea_ciclica", "texto": "@abierto", "args": { "y": -7.05, "f": 0.35, "tam": 44 } } },

    { "id": "reposicion", "t": 11.0, "dur": 1.0,
      "visual": { "efecto": "capa_python", "args": { "rol": "antena_reposiciona", "de_deg": 15, "a_deg": 165 } },
      "sonido": [ { "sfx": "whoosh", "d": 1.0, "args": { "f0": 5500, "f1": 600, "pico": 0.4 }, "vol": 0.10, "pan": 0.0 },
                  { "sfx": "codigo", "args": { "ref": "sonido_reels:atp_servo", "t0": 11.0, "dur": 1.0 } } ] },

    { "id": "haz_tics", "t": 1.0, "repite": { "cada": 1.9, "n": 6 },
      "sonido": [ { "sfx": "glide", "args": { "f0": 1200, "f1": 1800 }, "d": 0.12, "vol": 0.035, "pan": 0.5 } ] }
  ],

  "variantes": [],

  "publicacion": {
    "cuenta": "@co.de_aero",
    "plataformas": [ { "id": "instagram", "producto": "reel", "formato": "9x16" } ],
    "pie": "Una antena sigue a un satélite y cinco controladores pelean por quedarse dentro de ±0.1°. Las trazas son ilustrativas; el ATP-DT es un banco de pruebas de diseño en beta. ¿Cuál crees que gana? Guárdalo si te gusta el control.",
    "hashtags": { "es": ["#control", "#antenas", "#satélites", "#espacio", "#ingeniería"] },
    "alt": "Una antena parabólica sigue a un satélite mientras un osciloscopio muestra el error de apuntamiento dentro de una banda de más o menos 0.1 grados.",
    "fuentes_en_pie": true,
    "miniatura": { "t": 0.0 }
  },

  "verificaciones": {
    "loop": { "tolerancia_px": 2 },
    "duracion": { "esperada": 12.0, "tol": 0.04 },
    "audio": { "costura_max": 3, "pico_max": 0.95, "lufs_tol": 1.5 }
  }
}
```

Trazabilidad con el código:

- `ctrl_*`/`ley_*` reemplazan `CONTROLADORES` (`33` l. 138–142) y el bucle `for i, a in enumerate((11.5, 2.2, 4.4, 6.6, 8.8))` de `sonido_reels.atp`. El pan `−0.4 + 0.2·i` y el tono `PENTA[i % 5]` del código se explicitan (−0.4, −0.2, 0.0, 0.2, 0.4; `penta` 0 a 4).
- `reposicion` reemplaza el `t < 11` de `theta()` (l. 190–193), el `whoosh(1.0, 5500, 600, 0.10, 0.4)` en 11.0 y la `campana` del servo. Este último queda como `codigo` (W020).
- `haz_tics` reemplaza `for k in range(6): m.poner(1.0 + 1.9*k, glide(1200, 1800, 0.12, 0.035), pan=0.5)`.
- `tiempo.ciclo.desfase: 4.0` reemplaza `Reloj(self, T2, desfase=4.0)` y la tupla `("ReelATP", 12.0, 4.0)` de `REELS`.
- El texto del título pasa a `{{cifra:c_banda}}`: si la cifra cambia, cambian el rótulo, la etiqueta `±0.1°` del osciloscopio y el pie.
- Esta pieza **no** pasaría `aprobada` hoy: `c_banda` y `c_gdl` están sin revisar y hay un `cuidado` que bloquea. Es el comportamiento buscado.

Lo que mostraría el compilador (extracto de `cronologia.json`, `t_video = (t_ciclo − 4.0) mod 12`): `ctrl_pid` en `t_ciclo 2.2` cae en `t_video 10.2`; `ctrl_pd` (11.5) en `t_video 7.5`; `reposicion` (11.0) en `t_video 7.0`.

### 4.2 (b) Carrusel `doppler-curva-en-s` (`redes/carruseles/specs/divulgacion-orbital/doppler-curva-en-s.json`)

Convertido sin pérdida: las láminas conservan sus campos; lo nuevo es el registro de cifras y fuentes, el sello de la lámina de imagen (que `ESQUEMA.md` exige para dibujos ilustrativos y el original no tenía), y los hashtags separados del pie.

```json
{
  "esquema": 1,
  "id": "doppler-curva-en-s",
  "tipo": "carrusel",
  "serie": "divulgacion-orbital",
  "titulo": "La curva en S: el Doppler de un satélite",
  "estado": "borrador",
  "privacidad": "publica",
  "idiomas": { "base": "es", "salidas": ["es"] },
  "formatos": { "4x5": { "adaptacion": "panoramica" } },
  "tema": { "marca": "aerospace", "entorno": "fisica", "fondo": { "tipo": "portada", "var": 3 } },
  "motor": {
    "adaptador": "carrusel",
    "legado": { "carpeta": "exports/estudio/carruseles/divulgacion-orbital/doppler-curva-en-s" }
  },

  "fuentes": {
    "f_doppler": { "titulo": "Física estándar del efecto Doppler: Δf ≈ f·v_r/c", "tipo": "estandar", "url": null },
    "f_c": { "titulo": "Velocidad de la luz en el vacío, valor definido del SI (299 792 458 m/s)", "tipo": "estandar", "url": null },
    "f_calculo": { "titulo": "Cálculo propio: 137 MHz × 7 km/s ÷ 299 792 km/s ≈ 3.2 kHz", "tipo": "propia", "url": null },
    "f_orbiteye": { "titulo": "codeaerospace.com/plataformas, ficha CO.DE Orbit Eye", "url": "https://codeaerospace.com/plataformas",
                    "consultado": "2026-10-01", "tipo": "web" }
  },
  "cifras": {
    "c_c": { "tipo": "estandar", "valor": 299792.458, "unidad": "km/s", "mostrar": "299 792 km/s", "fuente": "f_c", "revisada": true,
             "revisor": "pendiente", "fecha_revision": "2026-10-02" },
    "c_f": { "tipo": "estandar", "valor": 137, "unidad": "MHz", "mostrar": "137 MHz", "fuente": "f_doppler",
             "nota": "Banda típica de satélites meteorológicos en órbita baja; valor de ejemplo, no de un satélite concreto." },
    "c_v": { "tipo": "estandar", "valor": 7, "unidad": "km/s", "mostrar": "7 km/s", "fuente": "f_doppler",
             "nota": "Orden de magnitud de la velocidad orbital en LEO hacia el observador (cerca del horizonte)." },
    "c_dop": {
      "tipo": "calculada", "valor": 3.1989, "unidad": "kHz", "mostrar": "3 kHz", "cifras_significativas": 1,
      "formula": "@c_f * 1000 * @c_v / @c_c", "entradas": ["c_f", "c_v", "c_c"],
      "fuente": "f_calculo",
      "nota": "Corrimiento máximo aproximado; depende de cada pase."
    }
  },
  "cuidado": [
    { "texto": "Orbit Eye es obra derivada de ground-station (GPL-3.0, Stratos Goudelis); este despliegue no tiene receptor de radio conectado.", "fuente": "f_orbiteye", "bloquea": false },
    { "texto": "Los ≈ 3 kHz son un orden de magnitud para 137 MHz; el valor real depende de la altitud y la geometría del pase.", "bloquea": false }
  ],

  "unidades": [
    { "id": "u1", "tipo": "portada", "kicker": "Divulgación orbital",
      "titulo": "La curva en S: el Doppler de un satélite",
      "subtitulo": "Por qué la frecuencia cambia durante un pase" },
    { "id": "u2", "tipo": "texto", "numero": "01", "titulo": "La ambulancia del espacio",
      "cuerpo": "Si la fuente se acerca, las ondas llegan comprimidas (más agudo). Si se aleja, estiradas (más grave). Con una señal de radio pasa igual: cambia la frecuencia que recibes." },
    { "id": "u3", "tipo": "imagen", "sello": "ilustracion", "kicker": "Un pase en LEO", "titulo": "La curva en S",
      "imagen": "sticker:seguidor_satelital/DopplerEnS",
      "pie": "Esquema ilustrativo: frecuencia recibida contra tiempo durante un pase. Las cifras del dibujo son un ejemplo." },
    { "id": "u4", "tipo": "pasos", "titulo": "Leer la S en tres tramos",
      "pasos": [ { "t": "Se acerca", "d": "Frecuencia por encima de la nominal" },
                 { "t": "Punto más cercano", "d": "Frecuencia nominal; la curva cae más rápido" },
                 { "t": "Se aleja", "d": "Frecuencia por debajo de la nominal" } ] },
    { "id": "u5", "tipo": "dato", "kicker": "La regla",
      "cifra": { "ref": "c_dop" }, "unidad": "a {{cifra:c_f}}",
      "titulo": "Corrimiento máximo típico en LEO",
      "nota": "El corrimiento ≈ f · v/c, con v ≈ 7 km/s hacia el observador (cerca del horizonte). Cálculo aproximado; depende de cada pase." },
    { "id": "u6", "tipo": "comparacion", "titulo": "Pase alto vs. pase bajo",
      "izq": { "t": "Pase alto", "items": ["S muy empinada", "Pasa cerca: cambia rápido"] },
      "der": { "t": "Pase bajo", "items": ["S más suave", "Más lejos: cambia lento"] } },
    { "id": "u7", "tipo": "texto", "numero": "02", "titulo": "Por qué importa",
      "cuerpo": "Un receptor de banda estrecha que no corrige el Doppler se sale de la señal. Por eso la estación calcula la curva con la órbita y sintoniza siguiéndola." },
    { "id": "u8", "tipo": "cierre", "titulo": "Una S que se calcula antes del pase",
      "texto": "CO.DE Orbit Eye corrige el Doppler en radio y rotor por Hamlib. Su despliegue no tiene receptor conectado: la recepción se demuestra con grabaciones IQ.",
      "cta": ["Guarda", "Comparte", "Síguenos"] }
  ],

  "variantes": [
    { "id": "b", "tipo": "ab", "variable": "gancho",
      "hipotesis": "Una pregunta en la portada retiene más desliz que una afirmación.",
      "metrica": "deslizamientos hasta la lámina 3 / alcance",
      "parche": [ { "op": "set", "ruta": "unidades[id=u1].titulo", "valor": "¿Por qué la frecuencia de un satélite dibuja una S?" } ] }
  ],

  "publicacion": {
    "cuenta": "@co.de_aero",
    "plataformas": [ { "id": "instagram", "producto": "carrusel", "formato": "4x5" } ],
    "pie": "Cuando un satélite pasa sobre ti, su frecuencia baja dibujando una S: más aguda al acercarse, nominal en el punto más cercano y más grave al alejarse. Esa curva se puede calcular antes del pase. Guárdalo si te gusta la radio y el espacio.",
    "hashtags": { "es": ["#Doppler", "#SDR", "#satélites", "#radioafición", "#espacio"] },
    "alt": "Curva en forma de S: frecuencia recibida contra tiempo durante el pase de un satélite.",
    "fuentes_en_pie": true,
    "miniatura": { "unidad": "u1" }
  }
}
```

Trazabilidad con el código:

- `motor.legado.carpeta` mantiene la salida donde la deja hoy `motor_carrusel.renderizar` (`SALIDA / serie / id`). El adaptador exporta de vuelta el spec original con `fuentes` (las 3 cadenas), `pie_texto = pie + " " + hashtags` y `cuidado` como cadenas, de modo que `motor_carrusel.validar(spec)` y `renderizar(spec)` siguen funcionando sin cambios.
- `unidad.cifra` pasa de la cadena `"3 kHz"` a una referencia; al exportar vuelve a `"3 kHz"` (`mostrar`). El validador comprueba E031/E032: `137 MHz · 1000 · 7 km/s / 299 792.458 km/s = 3.1989 kHz`, y `round(3.1989, 1 cifra significativa) = 3`.
- Las 3 `fuentes` originales (`fuentes[]`) se parten en tres fuentes con tipo y la tercera con `consultado: 2026-10-01`, que es la fecha que hoy solo aparece en prosa. La regla de `motor_carrusel.validar` («cifra sin fecha de verificación») queda como W050/E030.
- `c_c.revisor: "pendiente"` es deliberado: el validador debe tratar «pendiente» como no revisado (W011). El revisor real lo pone una persona.
- `variantes[0]` equivale al `{"sufijo": "b", "portada": {...}}` de `ESQUEMA.md`; el parche usa el selector por id, no el índice 0.

### 4.3 (c) `LogoEntornoNebulosa` (`34-logo-entornos.py`, clase generada `LogoEntornoNebulosa`)

```json
{
  "esquema": 1,
  "id": "logo-entorno-nebulosa",
  "tipo": "video_marca",
  "serie": "logo-entornos",
  "titulo": "Logo Co.De Aerospace entrando sobre el entorno Nebulosa",
  "estado": "borrador",
  "privacidad": "publica",
  "idiomas": { "base": "es", "salidas": ["es"] },
  "formatos": { "9x16": { "fps": 30, "calidad": "qh", "adaptacion": "escena_propia" } },
  "tema": { "marca": "aerospace", "entorno": "nebulosa", "fondo": { "tipo": "portada", "var": 0 }, "modo": "auto", "acento": "auto" },
  "motor": {
    "adaptador": "manim",
    "nivel_tiempo": 2,
    "archivo": "studio/content/animations/experimentacion/34-logo-entornos.py",
    "escena": { "9x16": "LogoEntornoNebulosa" },
    "legado": {
      "video": "exports/estudio/logo_entornos/animados/LogoEntornoNebulosa.mp4",
      "con_sonido": "exports/estudio/logo_entornos/animados/con_sonido/LogoEntornoNebulosa.mp4"
    }
  },
  "tiempo": { "fps": 30, "duracion": "auto", "reloj": "video" },

  "textos": { "sitio": "codeaerospace.com" },
  "cifras": {},
  "sellos": [],

  "audio": {
    "modo": "sintetico",
    "perfil": "marca",
    "fondo": [ { "bloque": "marca.entrada_orbital/fondo" } ]
  },

  "lineatiempo": [
    { "id": "fondo", "t": 0, "dur": "fin",
      "visual": { "efecto": "zoom_fondo", "args": { "desde": 1.0, "hasta": 1.05, "hasta_en_s": 9.3, "curva": "lineal" } } },
    { "id": "halo", "t": 0, "dur": "fin",
      "visual": { "efecto": "halo_oscuro", "args": { "y": 1.6, "radios": [3.2, 7.4], "n": 10, "opacidad": 0.07, "solo_oscuro": true } } },

    { "id": "entrada", "t": 0,
      "visual": { "efecto": "bloque_marca",
                  "args": { "estilo": "orbital", "acento": "auto", "ritmo": 1.0, "altura_rel_ancho": 0.819, "y": 1.6,
                            "version_logo": "auto" } },
      "sonido": [ { "bloque": "marca.entrada_orbital/intro" } ] },

    { "id": "sitio", "ancla": { "evento": "entrada", "hito": "fin" }, "dur": 2.3,
      "visual": { "efecto": "texto_entra",
                  "texto": "@sitio",
                  "args": { "y": -6.4, "tam": 44, "peso": "MEDIUM", "tracking": 0.08, "ancho_max_rel": 0.8, "color": "acento",
                            "entra_s": 0.7, "espera_s": 1.6 } },
      "sonido": [ { "sfx": "pluck", "dt": 0.1, "tono": { "semitonos": 12 }, "d": 1.2, "vol": 0.2 } ] }
  ],

  "publicacion": {
    "cuenta": "@co.de_aero",
    "plataformas": [ { "id": "instagram", "producto": "reel", "formato": "9x16" } ],
    "pie": "La marca de Co.De Aerospace entrando sobre un entorno espacial. codeaerospace.com",
    "hashtags": { "es": ["#espacio", "#motiongraphics"] },
    "alt": "El logo de Co.De Aerospace se dibuja con órbitas sobre un fondo de nebulosa.",
    "miniatura": { "t": 7.0 }
  },

  "verificaciones": {
    "duracion": { "esperada": 9.3, "tol": 0.3 },
    "audio": { "costura_max": 3, "pico_max": 0.95 }
  }
}
```

Trazabilidad con el código:

- `tema.entorno: "nebulosa"` es el `tema` de la subclase `_LogoEntorno` y la llamada `fondo_a_medida(self.tema, "portada", 0, 1080, 1920)`; el `modo: "auto"` aplica `CLAROS = {"estacion", "cuaderno"}` y el acento sale de `acento(tema)` (`fondos_a_medida.acento`). «nebulosa» no está en `DECORADOS_A_LA_DERECHA`, así que el fondo se genera directo a 1080×1920 (sin ventana).
- `zoom_fondo` es `respirar` (`1.0 + 0.05·min(t/9.3, 1)`); `halo_oscuro` es el `VGroup` de 10 círculos entre 3.2 y 7.4; `bloque_marca` es `LogoCoDe(altura=W*0.86/1.05, ...)` + `animar_entrada(escena, logo, estilo="orbital", acento=col)` (`altura_rel_ancho = 0.86/1.05 = 0.819`).
- `sitio` ancla a `entrada.fin`; la parte visual es el `FadeIn(sitio, shift=0.2*UP)` de 0.7 s más `wait(1.6)`; la parte sonora es `m.poner(6.95, pluck(A(12), 1.2, 0.2))` de `logo_entorno()` en `sonido_marca.py`. Hoy 6.95 es un número copiado; aquí es `fin + 0.1`.
- `entrada.sonido.bloque = "marca.entrada_orbital/intro"` es `intro(m)` de `sonido_marca.py` (órbitas a `0.24·i`, luna y satélite a 2.25 y 2.3, paneles a 2.5, letras desde 3.6, rebotes del punto en 4.93/5.26/5.42/5.47, destello a 5.95, acorde a 6.0) movido al bloque; en el paso 10 esas cifras pasan a leerse de `marcas.json` (M3 ronda 1) y dejan de estar escritas dos veces.
- `duracion: "auto"` con `verificaciones.duracion.esperada: 9.3` documenta lo que el docstring de `34` dice («≈ 9.3 s») y lo convierte en prueba; `ESCENAS_LE` (diccionario por nombre de clase) deja de ser necesario.
- Las otras nueve escenas (`orbita`, `mision`, `marte`, `lunar`, `solar`, `espectro`, `lanzamiento`, `fisica`, `caos`) serían variantes tipo `catalogo` con un parche `tema.entorno`: una pieza base `logo-entorno` y 10 salidas, no 10 escenas generadas con `type(...)` (`34` l. 53–56).

---

## 5. La CLI única `codeae`

Ubicación: paquete `codeae/` en la raíz del repo, `bin/codeae` (shim de tres líneas que agrega el repo a `sys.path`) y `python3 -m codeae`. Dependencias nuevas: ninguna en tiempo de ejecución (numpy, PIL y manim ya están); en desarrollo, `pytest` y `jsonschema` (hoy no instalados, ver paso 0). Todas las órdenes aceptan `--json` (una línea JSON por evento, para que la app Electron, que ya lanza procesos Python desde `studio/desktop/src/presentaciones.cjs`, no tenga que interpretar texto) y `--solo ID[,ID]` o patrones `serie/*`.

Códigos de salida: `0` bien; `1` verificación o gate en rojo; `2` uso o validación de esquema; `3` fallo de render o audio; `4` bloqueo de rigor al publicar.

### 5.1 Subcomandos

**`codeae validar [PIEZA...] [--estricto] [--para-publicar]`**
Valida esquema y reglas semánticas (2.8). `--estricto` convierte avisos en error. `--para-publicar` aplica los gates (estado, cifras revisadas, `cuidado` que bloquea). Salida: tabla `pieza, E, W, estado`. También sirve para los formatos heredados: `codeae validar --heredado redes/carruseles/specs` los importa en memoria y valida el resultado.

**`codeae render [PIEZA...] [--formato 9x16] [--idioma es] [--variante b] [--calidad qh|ql|borrador] [--jobs 4] [--rehacer ETAPA] [--compat] [--para-publicar]`**
Corre el grafo de etapas con caché: `validar → fondo → render → cronologia → audio → mux → verificar → miniatura`. Si la pieza es `carrusel`, `render` llama a `motor_carrusel.renderizar`; `pptx` a `decks_espaciales.construir`; `poster` a `fondos_a_medida` + composición. Si es `manim`, replica y mejora `una()` de los `.sh`: `media_dir` propio por escena y `--disable_caching`, log completo en `logs/render.log` con las últimas 20 líneas en pantalla al fallar, directorio temporal limpiado con `try/finally`, salida con `.part` y `rename`, código `3` si falla. `--rehacer fondo` fuerza esa etapa y las siguientes.

**`codeae audio [PIEZA...] [--marcas ruta] [--solo-wav]`**
Compila la cronología y sintetiza el audio de la pieza sin tocar el video (útil para iterar sonido). Lee `marcas.json` si la pieza está en nivel 2. Escribe `audio.wav` y `cronologia.json`; con `mux` (por defecto) produce el entregable final copiando el video sin recodificar. Respeta `audio.perfil` (`bucle` o `marca`, los dos masters actuales) y la semilla por evento.

**`codeae verificar [PIEZA...] [--en RUTA]`**
Pruebas sobre el entregable (no sobre la fuente), siempre con código de salida real:

| Prueba | Aplica a | Criterio |
|---|---|---|
| Loop exacto (función en `t` y `t+T`, a 270×480, sin compresión) | `reel_loop` | `max |a−b| ≤ tolerancia_px` (ronda 1, M2) |
| Loop por video (respaldo) | cualquier loop ya renderizado | `salto / mediana < 1.6`, un solo criterio (arregla `verificar_loop.py` l. 42 frente a l. 50) |
| Costura de audio | con audio | `|x[0] − x[-1]| < costura_max × mediana|Δx|`, medida sobre el buffer **sin rotar** |
| Duración | videos | `|dur − esperada| ≤ tol`; `audio == video ± 1 muestra` |
| Nivel | con audio | RMS dentro de `lufs_tol` de `lufs`; `pico < pico_max` |
| Zona segura | videos y carruseles | ningún texto fuera de `formatos.zona_segura` (`lienzo.cabe`) |
| Desborde de texto | carruseles | `ajustar()` no cae bajo `tam_min` (hoy devuelve 18 px y sigue: ronda 1, §2.4) |
| Fuentes | todo | cada fuente del kit existe y se resuelve (Montserrat, Rajdhani...) |
| Privacidad | `publica` | E040/E041 sobre los recursos realmente usados, no solo los declarados |
| Equivalencia es/en | bilingües | cifras de `en` equivalentes a las de `es` (usa `verificar_traduccion.py`) |

**`codeae publicar-paquete PIEZA [--plataforma instagram] [--formato] [--idioma] [--borrador]`**
Arma `paquete/` listo para subir a mano: el archivo, la miniatura, `pie.txt` (pie + hashtags + fuentes si `fuentes_en_pie`), `alt.txt`, `CUIDADO.txt` (sin emoji; el actual de `motor_carrusel.renderizar` usa `⚠️`), `creditos.txt` (derivado de `fuentes` y de bloques de marca), `procedencia.json` (cifras con su fuente, fecha y revisor) y `LEEME.txt` con la lista de verificación. Se niega (código `4`) si no pasa los gates de `validar --para-publicar`; `--borrador` genera el paquete marcado con `BORRADOR.txt` y no lo permite para estado `aprobada`. No publica en redes (primer año: manual, según la ronda 1 de producto).

**`codeae indice [--regenerar] [--filtro estado=revision] [--cifras]`**
Recorre `piezas/**` y `exports/codeae/**`, recalcula las huellas actuales y las compara con las guardadas: `ok`, `obsoleto` (la fuente cambió), `falta` (nunca se renderizó), `bloqueado` (gate). Escribe `exports/codeae/INDICE.json` (lo lee la app) y `INDICE.md`. `--cifras` produce el índice inverso: cifra → piezas que la usan y su vigencia (alertas de caducidad).

Subcomandos auxiliares (no obligatorios para v1): `codeae importar tipo ruta` (spec de carrusel o presentación → `pieza.json`), `codeae exportar-heredado ID` (pieza → spec original), `codeae expandir` (plantillas y variantes `catalogo`).

### 5.2 Estructura de carpetas de salida

```
exports/codeae/
├── INDICE.json, INDICE.md
├── _cache/<etapa>/<huella[:2]>/<huella>/      almacén por contenido (las salidas son enlaces duros o copias)
└── <pieza-id>/                                una carpeta por pieza (las variantes <id>-b son hermanas)
    ├── pieza.resuelta.json                    la pieza con variante aplicada (la que se renderizó)
    ├── <formato>/                             9x16 | 4x5 | 16x9
    │   └── <idioma>/                          es | en
    │       ├── <id>.mp4                       entregable final (video con audio)
    │       ├── <id>.mudo.mp4                  video sin audio
    │       ├── <id>.wav                       audio sintetizado
    │       ├── cronologia.json                eventos resueltos (la fuente común de audio y video)
    │       ├── marcas.json                    hitos medidos del video (bloques de marca)
    │       ├── etapas.json                    huella de cada etapa, dependencias, versiones, duración
    │       ├── verificacion.json              resultado de cada prueba, con valores
    │       ├── miniatura.jpg
    │       ├── logs/render.log
    │       └── (carrusel) <id>_01.png … <id>_hoja.jpg ·· (pptx) <id>.pptx, GUION_<id>.md
    └── paquete/<plataforma>-<formato>-<idioma>/    lo que genera publicar-paquete
```

Compatibilidad: con `--compat` (o `motor.legado`), cada entregable se enlaza (enlace duro, o copia en otro sistema de archivos) a su ruta antigua: `exports/marca-codeaerospace/reels-promo/{Escena}.mp4` y `.../con_sonido/`, `exports/estudio/logo_entornos/animados/`, `exports/estudio/carruseles/<serie>/<id>/`. La pestaña Exports de la app y el `SKILL.md` siguen funcionando sin tocarse. Los enlaces se retiran cuando la app lea `INDICE.json`.

### 5.3 Caché por hash

Cada etapa tiene su huella (SHA-256 truncado a 16 hex) de la forma `H(versión_etapa ‖ entradas_canónicas ‖ digests_de_archivos)`. Entradas canónicas = JSON ordenado, sin espacios, de la parte de la pieza que la etapa lee (no toda la pieza): cambiar el pie no re-renderiza el video; cambiar un sonido no re-renderiza la imagen.

| Etapa | Entradas | Archivos digeridos |
|---|---|---|
| `fondo` | `tema.entorno`, `fondo.{tipo,var,ventana}`, tamaño | fuente del generador (`inspect.getsource`), JSON/`.py` del tema (arregla ronda 1 §2.3, clave sin versión) |
| `render` (manim) | `tiempo`, `lineatiempo[*].visual`, `textos` y `cifras` sustituidos, `tema`, formato, idioma, calidad, `motor` | escena `.py`, **solo los módulos importados** (se registran en `etapas.json.deps` leyendo `sys.modules` bajo el repo la primera vez; las siguientes huellas se comprueban contra esa lista), `kit.json`, fuentes TTF, versión de manim, huella de `fondo` |
| `render` (carrusel) | `unidades`, `tema`, `textos`/`cifras` | `motor_carrusel.py`, stickers usados, fuentes, huella de `fondo` |
| `cronologia` | `tiempo`, `lineatiempo` completo, parámetros | `codeae/tiempo.py`, `bloques.json` |
| `audio` | `cronologia.json`, `audio`, `marcas.json` (si hay) | `sonido_marca.py`, `sonido_reels.py`, `codeae/audio.py`, `sfx.json` |
| `mux` | huellas de `render` y `audio` | versión de ffmpeg |
| `verificar` | huellas de `mux`, `verificaciones` | versión de las pruebas |
| `miniatura` | huella de `mux`, `publicacion.miniatura` | — |
| `paquete` | `publicacion`, `fuentes`, `cifras`, huella de `verificar` | — |

Reglas: escritura atómica (`.part-<pid>` y `rename`, lo que `fondos_a_medida` ya hace desde que usa el PID); cerrojo por huella (`flock`) para que dos procesos no repitan la misma etapa; un acierto de caché se informa como `cache` en `--json`; `codeae render --sin-cache` y `--rehacer ETAPA` existen para depurar; la caché es seguro borrarla (`codeae limpiar-cache --antiguos 30d`, auxiliar).

Límite conocido: Manim no es determinista bit a bit entre máquinas (Pango, ffmpeg); la huella decide si rehacer, no promete igualdad de bytes. La prueba de equivalencia de la migración compara con tolerancia, no por hash (ver paso 6).

---

## 6. Plan de migración incremental

Principios: cada paso es **aditivo** (nada existente cambia de comportamiento hasta el paso 14), cabe en ≤ 1 día, termina con pruebas automáticas que pasan y deja el repo utilizable. Las pruebas son `unittest`/`pytest` (el sistema no tiene `pytest`: paso 0 lo resuelve). Mientras un paso migra una pieza, se corre el **modo sombra** (`--comparar-legado`): ejecuta el camino antiguo y el nuevo y compara resultados con la tolerancia indicada.

Tamaño: S ≈ medio día, M ≈ 1 día.

**Paso 0 · Cimientos (S).** Entorno de desarrollo y esqueleto. Crear `codeae/` (paquete vacío con `__main__`), `bin/codeae`, `requirements-dev.txt` (`pytest`, `jsonschema`), `tests/` y `codeae/esquema/pieza.schema.json` (2.2). Decisión del dueño (no del agente): versionar `marca/`, `redes/`, `marca_*.py`, `reels_promo.py`, `rotulos_aerospace.py`, `estelas.py`, `30–34`, `sonido_*`, `verificar_loop.py`, que siguen sin versionar según `git status` (ronda 1, M12); sin eso, los pasos siguientes no tienen red de seguridad.
Pruebas: el esquema es un JSON Schema válido (`Draft202012Validator.check_schema`); `python3 -m codeae --version` sale 0; la suite corre vacía en verde.

**Paso 1 · `validar` para piezas nativas (M).** `codeae/validar.py`: esquema + reglas E001, E010–E011, E020–E022, E050, E060, E090 (sin cifras ni privacidad todavía). Catálogos iniciales `formatos.json`, `efectos.json`, `sfx.json` (los registros de 2.3 apuntando a funciones existentes; no se ejecutan, solo se comprueba que existen con `importlib`/`inspect`). Guardar los tres ejemplos de este documento en `tests/fixtures/`.
Pruebas: los tres ejemplos validan sin E (con W20/W11 esperados); 12 mutaciones (efecto inventado, ancla circular, evento ≥ T en ciclo, ventanas de texto solapadas, `id` ≠ archivo, idioma de salida sin texto, etc.) fallan con el código exacto; para cada entrada de `efectos.json`/`sfx.json`, la función destino existe y acepta los `args` declarados (`inspect.signature`).

**Paso 2 · Adaptador de carruseles, ida y vuelta (M).** `codeae/adaptadores/carrusel.py`: `importar(spec) -> pieza` y `exportar(pieza) -> spec` (reglas: `fuentes[]` → registro de fuentes; `pie_texto` ↔ `pie` + `hashtags`; `cuidado[]` ↔ objetos; `laminas` ↔ `unidades` con ids `u1..un`; `fondo` ↔ `tema.entorno/fondo`; `variantes` ↔ parches por id). Cifras todavía no (una cadena `"cifra"` se importa tal cual).
Pruebas: para los 28 specs de `redes/carruseles/specs/**`, `exportar(importar(spec)) == spec` (JSON canónico); `motor_carrusel.validar` da el mismo resultado antes y después; `expandir_variantes` y el equivalente por parches producen el mismo spec en el spec con variante.

**Paso 3 · Registro de cifras y fuentes (M).** Reglas E030–E033, W010, W011, W050 y `codeae/cifras.py` (evaluador aritmético seguro con `ast`, sin `eval`, para `formula`; formateo con `cifras_significativas`; sustitución de `{{cifra:id}}`). Extraer a mano (asistido por un script que lista las láminas `dato` y las líneas de `fuentes`) las cifras de los carruseles `dato` y de `exports/CIFRAS_A_REVISAR.md`; empezar por `doppler-curva-en-s`. El importador del paso 2 pasa a producir `cifra: {ref}` cuando exista el registro.
Pruebas: `c_dop` recalcula a 3.1989 y `mostrar "3 kHz"` pasa E031; cambiar el 7 por 70 falla E032; una cifra `ilustrativa` sin sello falla E033; fecha de caducidad vencida → W010; `{{cifra:x}}` inexistente → E030; ida y vuelta del paso 2 sigue en verde; el evaluador rechaza `__import__('os')` y llamadas.

**Paso 4 · Kit de marca y formatos (M, es el M4 de la ronda 1 acotado).** `marca/kit.json` (bloques `marca`, `web`, `tipografia` con rutas relativas al repo, `zona_segura` por formato) y `marca_kit.py` (`hex`, `rgb`, `rgb255`, `fuente`, `ruta_extensiones`). Solo se **agrega** el kit y se hace que `codeae` lo use; las constantes de `marca_aerospace.py`, `motor_carrusel.py` y `33` se migran en el paso 9 y siguientes, una por vez. Copiar a `marca/fuentes/` las TTF de Rajdhani/DM Sans/Space Mono/Orbitron con sus OFL (varias ya están en `studio/content/manim_extensions/fonts/`).
Pruebas: `kit.hex("cian") == "#00D9FF"`; los 9 colores de `paleta.json` están en el kit; lint informativo (no falla todavía) que lista hex de marca fuera del kit; cada fuente declarada existe en disco.

**Paso 5 · Huellas, caché y `render` de carruseles (M).** `codeae/huella.py`, `codeae/etapas.py` (grafo, cerrojos, escritura atómica, `etapas.json`), y el adaptador de render `carrusel` que llama a `motor_carrusel.renderizar(spec, destino=exports/codeae/<id>/4x5/es)`. `codeae render` y `codeae indice` existen ya (indice solo para carruseles). `--compat` enlaza a `exports/estudio/carruseles/<serie>/<id>/`.
Pruebas: render de `specs/prueba/orbit-eye.json` produce 1 PNG por lámina + hoja; segunda ejecución informa `cache` sin tocar archivos (mtime iguales); cambiar un carácter del `pie` no invalida `render` pero sí `paquete`; cambiar un carácter de una lámina sí invalida; matar el proceso a mitad no deja `.part` huérfanos que cuenten como acierto; dos procesos simultáneos sobre la misma pieza no se pisan (cerrojo).

**Paso 6 · `render` de escenas Manim con paridad (M).** Adaptador `manim`: construye el comando de los `.sh` (`manim render -r <px> --fps <fps> --disable_caching --media_dir <tmp> archivo Escena`), `PYTHONPATH` calculado (sin `/workspace`), log, `try/finally`, `.part`→`rename`, código `3`. Registra los módulos importados en `etapas.json.deps`. Modo sombra para `ReelATP`, `ReelModelo`, `ReelOrbitEye` y `LogoEntornoNebulosa` con las piezas de este documento (nivel 0: sin `lineatiempo` consumida; `motor.nivel_tiempo: 0`).
Pruebas: render a `-r 270,480 --fps 10` de `ReelATP` por `codeae` y por `marca/renderizar_reels_promo.sh` (con `CALIDAD` reducida): mismas dimensiones, mismo número de cuadros, diferencia media por píxel ≤ 2/255; una escena que lanza excepción produce código `3` y el log contiene el traceback; no quedan directorios en `/tmp` tras éxito ni fallo.

**Paso 7 · Compilador de línea de tiempo (M).** `codeae/tiempo.py` (puro): resolución de anclas, `repite`, reloj de ciclo/video, `desfase`, tabla de `ventanas`; se mudan `suave`, `ventana`, `ventana_texto` desde `reels_promo.py` (que las reexporta, así nada se rompe), y `doppler_d`/`doppler_amp` (reexportadas desde `33` y `sonido_reels`). Emite `cronologia.json`.
Pruebas: compilar el ejemplo (a) reproduce exactamente `CONTROLADORES` (nombres, `a`, `b`, `amp`) y la lista `(11.5, 2.2, 4.4, 6.6, 8.8)`, las ventanas de leyenda `3*i−1.5` de `ReelOrbitEye` y `4*i−2` de `ReelModelo` (piezas con la misma estructura); `ventana` de dos eventos contiguos suma 1 en todo el fundido (propiedad); periodicidad `f(t) == f(t+T)` para todas las ventanas en 1 000 puntos; las funciones movidas devuelven valores idénticos (bit a bit) a las originales en una malla.

**Paso 8 · Audio desde la cronología con equivalencia (M).** `codeae/audio.py` con el registro `sfx.json` y `Circular`/`Mezcla` reutilizados (importa `sonido_marca` y `sonido_reels`, no los copia); semilla por evento y `rng` explícito (se agrega parámetro `rng=None` a los sfx que usan `RNG` global, con valor por defecto igual al comportamiento actual para no romper `sonido_*.py`). Modo `legado`: `audio.legado = "sonido_reels:atp"` ejecuta el guion existente. Pieza (a) con `audio` declarado.
Pruebas (el centro del paso): el wav compilado desde la pieza (a) es igual **muestra a muestra** (`np.allclose`, `atol=1e-9`) al de `sonido_reels.atp` + `master` con las semillas legadas (`crc32("ReelATP")`; en `--semilla-legada`) — esto prueba que el contrato describe lo mismo que el código; costura < 3 × mediana; mover `ctrl_pid.t` en 0.5 s mueve el pluck del wav exactamente 0.5 s (correlación cruzada) y no cambia el resto; el wav de ATP no depende de qué otras piezas existan.

**Paso 9 · Runtime Manim: las escenas leen la pieza (M).** `codeae/runtime.py` (`cargar()`, `eventos()`, `ventana()`, `parametro()`), y migrar `ReelATP` (solo `ReelATP`) para leer `CONTROLADORES`, ventanas, `T`, `desfase` y el texto de la pieza; si `CODEAE_PIEZA` no está, usa la pieza por defecto (la escena sigue ejecutable a mano). Las constantes de color de esa escena pasan al kit. `nivel_tiempo: 1`.
Pruebas: la prueba de periodicidad exacta (M2 de la ronda 1): se instancia la escena, se fija `reloj.t = desfase` y `desfase + T`, se captura `pixel_array` a 270×480 y `max|a−b| ≤ 2`; mover una ventana en `pieza.json` cambia **a la vez** el cuadro de la imagen en ese instante (captura en `t` dentro de la ventana) y el instante del pluck en el wav (cruce de las dos pruebas en un solo test); sin `CODEAE_PIEZA` el cuadro 0 coincide con el del paso 6 (tolerancia ≤ 2).

**Paso 10 · Marcas y bloque de marca (M).** Ronda 1, M3 acotado: `marcar(escena, nombre)` en `marca_aerospace.animar_entrada` (hitos `orbita_0..5`, `luna_llega`, `satelite_llega`, `paneles`, `letras`, `punto_cae`, `aerospace`, `destello`, `fin`), `marcas.json` escrito en `tear_down` (ruta por variable `MARCAS_DIR`), `bloques.json` con la tabla esperada y `marca.entrada_orbital/intro` leyendo marcas con falla explícita si faltan. Pieza (c) en nivel 2.
Pruebas: render a 270×480 de `LogoEntornoNebulosa`: las marcas coinciden con la tabla dorada ±1 cuadro; el audio por marcas coincide con `sonido_marca.logo_entorno` (tolerancia como paso 8); con `ritmo=0.7` el audio cambia solo por las marcas, sin tocar código; sin `marcas.json`, `codeae audio` sale con código `3` y mensaje claro (no genera un wav mal sincronizado).

**Paso 11 · `verificar` completo (M).** Implementa la tabla de 5.1: loop exacto, loop por video unificado (arregla los dos criterios de `verificar_loop.py`: lo reemplaza por un envoltorio con `main()` y `sys.exit`), costura, duración, nivel, zona segura (`lienzo.cabe`), desborde de texto en carruseles (`ajustar` devuelve `cabe`), fuentes. Salida `verificacion.json`.
Pruebas: fixtures sintéticos que **deben fallar**: un mp4 de 3 s con un corte duro en el empalme (código 1), un wav con salto en la costura, un texto 120 caracteres que desborda en un spec de carrusel, un rótulo fuera de zona segura; y fixtures que deben pasar (los reels reales cuando existan los mp4). Una prueba verifica que la ausencia de `ffmpeg` da error claro (no excepción críptica).

**Paso 12 · `publicar-paquete` e `indice` completo (S).** Generación de `paquete/`, `procedencia.json`, `BORRADOR.txt`, gates (código `4`), `INDICE.json/md` con obsolescencia y vigencia de cifras (`--cifras`).
Pruebas: una pieza con una cifra sin fuente o `cuidado` bloqueante no genera paquete (código 4) y con `--borrador` sí, marcado; pie > 2 200 o > 30 hashtags falla; el índice marca `obsoleto` tras editar una escena importada y `ok` tras re-renderizar; el índice inverso lista a `c_banda` en el reel y en cualquier carrusel que la use.

**Paso 13 · Presentaciones y pósteres (M).** Adaptador `pptx`: `importar(json_de_presentaciones)`/`exportar` (ida y vuelta con `PU.validar`) y llamada a `decks_espaciales.construir(temas, deck, idioma)`; adaptador `poster` con `fondo_a_medida` y la composición de `marca/logo_entornos.componer`. Las diapositivas `video` referencian la clase del catálogo (`clase`) como hoy; la pieza `presentacion` hereda `ritmo`, `guion` y `cuidado` de cada diapositiva.
Pruebas: `que_es_code.json` ida y vuelta idéntico y `presentaciones_usuario.validar` sin cambios; `python3 animaciones/pruebas_presentaciones.py` sigue verde (no se toca `decks_espaciales`); render de la pieza genera el `.pptx` y `GUION_que_es_code.md` con el mismo contenido que `decks_espaciales.py que_es_code`; el póster 9:16 coincide con `marca/logo_entornos.py nebulosa --formatos 9x16` (diferencia ≤ 1/255 de media).

**Paso 14 · Retirar los intermediarios (S).** Los `marca/renderizar_*.sh` pasan a una línea (`exec bin/codeae render ...`), `sonido_marca.py main()`/`sonido_reels.py main()` y `verificar_loop.py` quedan como utilidades que `codeae` llama; se actualiza `SKILL.md` (sección «Marca y redes» + `codeae`, corrigiendo la contradicción de l. 118/143) y `paleta.json` (decir que lo lee el kit). Se migra el resto: `ReelOrbitEye`, `ReelModelo`, los 10 `LogoEntorno*` como variantes `catalogo`, los 8 reels de `32`, los 8 de `30`, y los 28 carruseles.
Pruebas: para cada shim, `bash marca/renderizar_X.sh --seco` imprime el mismo comando que `codeae render --seco`; el lint de marca (paso 4) pasa de informativo a fallo; una prueba de humo recorre `codeae validar piezas/**` (todas verdes) y `codeae indice` sin `falta` para lo ya renderizado.

Resumen de esfuerzo: pasos 0–14 ≈ 11 días de trabajo si se hacen en orden; el valor llega pronto: tras el paso 3 el rigor de cifras ya bloquea en carruseles; tras el paso 5 hay caché y trazabilidad; tras el paso 8 el audio del reel de ATP queda demostrado como derivado del contrato; tras el paso 10 la banda sonora de la marca deja de desincronizarse al tocar `ritmo`.

### 6.1 Riesgos y decisiones abiertas

| Tema | Riesgo | Decisión propuesta |
|---|---|---|
| Alcance del contrato en escenas generativas | Pretender declarar el dibujo lleva a reescribir Manim | El contrato cubre tiempos, textos, cifras y parámetros; el dibujo queda en `motor.central` (decisión 2) |
| Dos masters de audio (`bucle` y `marca`) | Seguir con dos cadenas de loudness | Se conservan como `audio.perfil`; unificar (ronda 1, M13: `sfx.py`/`musica.py`) es posterior |
| Sistema paralelo `promo.py`/`render_promo.py`/`promo_verifica.py` | Una quinta variante | No se migra en esta ronda; se reutilizan `promo.Formato` y `medir_bucle` desde `codeae/formatos` y `verificar` si resultan compatibles (decisión para el dueño) |
| Evaluador de fórmulas | Superficie de ataque si usa `eval` | `ast` restringido a `+ − × ÷ ** ()`, referencias `@id` y números; sin nombres ni llamadas |
| Plugins `.py` de temas (`exec_module`) | Ya existe código arbitrario por diseño | Sin cambio; `codeae` no agrega vías de ejecución nuevas desde JSON (los `ref` de `sfx: codigo` y `central` solo admiten módulos bajo el repo) |
| Huella por trazado de importaciones | La primera ejecución no conoce `deps` | Primera huella usa todo `manim_extensions/` + escena; se refina tras el primer render |
| Cifras `citada` con URL de la página viva | La página cambia (la ficha de `ESQUEMA.md` dice «cifras verificadas el 2026-07-30») | `consultado` es obligatorio; `caduca_dias` por defecto 90 en `citada`/`medida` (a confirmar con el dueño) |
| `revisor` | Un campo de texto no prueba revisión | Es bitácora, no seguridad; el gate exige que no sea vacío ni «pendiente»; la validez real depende de la persona |
| Idioma | Solo `es` y `en` existen hoy (decks y videos) | El esquema admite cualquier par `[a-z]{2}`; el validador exige texto por cada salida (E050) |
| Pytest/jsonschema ausentes | Los tests no corren en el entorno actual | Paso 0 crea el entorno de desarrollo; los tests nuevos se escriben compatibles con `unittest` |

### 6.2 Lo que este diseño no incluye

Publicación automática por API; métricas (la ronda 1 de producto las difiere); datos vivos TLE/SPICE como tipo de cifra (el esquema los admitiría con un `tipo: "dato_vivo"` y época visible, pero no se define aquí); render distribuido (el hash estable de 5.3 lo habilita después); edición visual en la app (la app solo lanza `codeae --json`).
