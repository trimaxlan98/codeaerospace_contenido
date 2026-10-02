# Ronda 1 — Investigación de producto: Estudio de edición Co.De Aerospace

Fecha: 2026-10-02. Lectura del repo + búsquedas web. Lo marcado (sin fuente) viene de conocimiento general y debe verificarse antes de decidir.

## 0. Lo que ya existe (repo)
- **CO.DE Studio** (Electron, `studio/desktop`): vistas Estudio (webview de ManimStudio), Exports, Terminal, Sistema; en marcha Inicio, Marca y Presentaciones (`presentaciones.cjs`). Plan en `docs/plan_app_codeaerospace.md`.
- **ManimStudio** (`studio/`, FastAPI + React + runner Docker): proyectos, render, asistente.
- **Presentaciones** (`animaciones/`): 18 temas registrables, fondos procedurales, JSON propios, inglés, guion con advertencias, pruebas de calidad, PySide6 (`app/render_launcher.py`).
- **Carruseles** (`redes/carruseles/motor_carrusel.py`): JSON por carrusel, 4:5, fondo panorámico cortado en láminas, `fuentes` y `cuidado` en el spec, hoja de contacto, pie de texto.
- **Marca**: `marca_aerospace.py/.json`, `rotulos_aerospace.py`, `marca_vertical.py`, `reels_promo.py`, `estelas.py`, Montserrat OFL.
- **Audio/herramientas** (`studio/tools/`): `sfx.py`, `musica.py`, `alinear_voz.py`, `narrar_*`, `sonido_marca.py`, `render_vertical.py`, `sellar_duraciones.py`, sondas `sonda_*.py`.
- **Datos**: ya hay `studio/content/datos`, `satelites.py`, `constelacion.py`, `kepler.py`, `seguidor_satelital.py`, `apt_tracking.py` (base para SGP4/efemérides).
- Diagnóstico: son 4 sistemas de "front" (Electron, web, PySide6, scripts) y 3 formatos de spec distintos (JSON de carrusel, JSON de presentación, escenas Python). Falta una unidad común: la **pieza**.

## 1. Qué hacen bien las herramientas y qué no sirve para divulgación rigurosa

| Herramienta | Fortaleza a copiar | Límite para ciencia rigurosa / para Co.De |
|---|---|---|
| Remotion | Video como código (React), parametrizable por props/JSON, render en servidor/Lambda, plantillas. Licencia gratuita hasta 3 personas; de 4+ pide licencia de empresa ([licencia](https://www.remotion.pro/license), [términos](https://www.remotion.dev/docs/terms), [costo Lambda](https://www.remotion.dev/docs/lambda/cost-example)) | Sin matemática/figuras científicas nativas; coste de licencia si el equipo crece; stack JS distinto al de Manim |
| Motion Canvas | Animación vectorial en TypeScript con generadores, editor con preview en vivo, alinea audio de narración con la línea de tiempo; MIT ([repo](https://github.com/motion-canvas/motion-canvas), [sitio](https://motioncanvas.io/)) | Un segundo motor; sin LaTeX/ciencia del nivel de Manim; ecosistema pequeño |
| Manim CE / ManimGL | Matemática y figuras científicas exactas, MIT; CE estable y documentado, GL interactivo y experimental; son incompatibles entre sí ([CE](https://github.com/manimCommunity/manim), [GL](https://github.com/3b1b/manim), [comparación](https://animo.video/what-is-manimce)) | Sin interfaz de edición, sin temporización visual, sin plantillas de marca ni multiformato: eso lo agrega Co.De. Mantener CE |
| Blender + Geometry Nodes | Procedural, parametrizable, renders 3D fotorrealistas; GPL pero la salida es libre (sin fuente) | Curva de aprendizaje, render pesado, difícil automatizar con rigor de datos; útil solo para planos hero |
| After Effects + MOGRT | Plantillas con solo los parámetros expuestos editables (Essential Graphics) ([Adobe](https://helpx.adobe.com/after-effects/using/creating-motion-graphics-templates.html)) | Propietario, por suscripción, no reproducible por script; el patrón "exponer solo lo editable" sí se copia |
| Canva / Adobe Express | Plantillas, kit de marca, multiformato por "magic resize" (sin fuente) | Sin datos ni verificación de cifras; contenido genérico; dependencia de nube |
| Rive / Lottie | Runtime ligero; Rive con máquinas de estado interactivas, `.riv` 10-15x menor que Lottie JSON; dotLottie ya tiene máquinas de estado ([comparación](https://lottiefiles.com/blog/lottie-animations/lottiefiles-or-rive)) | Pensados para UI; no para ciencia ni para video de redes. Útiles solo para la web interactiva |
| Descript | Edición por texto: se edita la transcripción y el video sigue ([Descript](https://www.descript.com/tools/video-caption-generator)) | Pensado para voz hablada; no sirve para animación generada |
| CapCut | Plantillas, subtítulos automáticos (23 idiomas), formato corto ([comparativa](https://www.ngram.com/blog/capcut-vs-descript)) | Subtítulos automáticos exigen corregir a mano; términos técnicos se transcriben mal; sin rigor |
| Figma + plugins | Componentes y variables de marca, colaboración (sin fuente) | Estático; el movimiento es débil |
| Jitter | Motion para diseñadores con plantillas sociales (sin fuente) | Sin datos, sin exportación reproducible por código |

Patrón común: **plantilla + parámetros expuestos + render por lote**. Ninguna ofrece **verificación de contenido**: ahí está el hueco.

## 1b. Fuentes de datos y visuales espaciales

| Fuente | Qué aporta | Condiciones |
|---|---|---|
| NASA SPICE / NAIF | Efemérides y trayectorias de cuerpos y misiones ([NAIF](https://naif.jpl.nasa.gov/naif/rules.html), [intro](https://nasa-pds.github.io/naif-pds4-bundler/13_spice.html)) | Reglas en NAIF; se alienta reconocer a NAIF/PDS |
| OpenSpace | MIT, usa SPICE, exporta sesiones como fotogramas ([sitio](https://www.openspaceproject.com/), [repo](https://github.com/OpenSpace/OpenSpace)) | Muy pesado (GPU); sirve para planos reales de sistema solar si se quiere realismo |
| Cesium / CesiumJS | CesiumJS Apache 2.0; terreno y teselas de Cesium ion con atribución obligatoria ([guía](https://cesium.com/learn/ion/content-usage-and-attribution-guide/)) | No se puede quitar la atribución; los activos de ion son comerciales |
| Stellarium | GPLv2, API de scripts con capturas de pantalla ([API](https://stellarium.org/doc/1.x/classStelMainScriptAPI.html)) | GPL: usarlo como herramienta externa para capturar cielos, no incrustar código |
| NASA Eyes | Visualización de misiones en tiempo real (no pude confirmar sus condiciones: **verificar**) | — |
| CelesTrak / Space-Track | TLE; Space-Track exige registro y limita la redistribución masiva; CelesTrak tiene autorización para redistribuir ([notas](http://celestrak.org/norad/elements/notice.php), [resumen](https://orbitalradar.com/glossary/space-track)) | Publicar piezas derivadas, no espejar el catálogo |
| Imágenes NASA | Generalmente sin derechos de autor; no cubren el logo/insignia de NASA; no insinuar aval comercial ([guía](https://nasa.gov/nasa-brand-center/images-and-media)) | Citar la fuente; revisar créditos de terceros |

## 2. Diferenciadores posibles
1. **Visuales desde datos reales**: órbitas con SGP4 desde TLE (con fecha de época visible), planetas desde SPICE/JPL. Ya hay base en `satelites.py`/`kepler.py`.
2. **Rigor verificable**: cada cifra de una pieza es una entrada en un registro (valor, unidad, fuente, URL, fecha de consulta, quién la revisó). La pieza no pasa a "publicable" si hay cifras sin fuente. Ya existe la semilla: `exports/CIFRAS_A_REVISAR.md`, `fuentes`/`cuidado` en carruseles, `verificar_traduccion.py`.
3. **Plantillas de marca** con parámetros expuestos al estilo MOGRT (tema, textos, color), no código.
4. **Loops perfectos verificados**: prueba automática primer cuadro = último cuadro (diferencia por píxel bajo umbral) antes de exportar. Hoy `sellar_duraciones.py` y `promo_verifica.py` apuntan a eso.
5. **Multiformato desde una fuente**: 16:9, 4:5 y 9:16 con una sola escena y reglas de "zona segura"; ya hay `marca_vertical.py`, `render_vertical.py` y el carrusel 4:5.
6. **Audio sintético sincronizado**: SFX/música/voz generados y alineados con cuadros (`sfx.py`, `musica.py`, `alinear_voz.py`). Diferencial real: sin licencias de música.
7. **Bilingüe es/en** con comprobación de equivalencia de cifras (`traducciones_en.py`, `verificar_traduccion.py`).
8. **Procedencia en la pieza**: crédito de datos en el cuadro final o en el pie ("TLE CelesTrak, época 2026-10-01") generado, no escrito a mano.

## 3. Funciones por horizonte

**Flujo del creador**: idea → guion → piezas → revisión de rigor → render multiformato → publicación → métricas.

| Paso | 1 mes | 3 meses | 1 año |
|---|---|---|---|
| Idea | Banco de ideas como archivos `idea/*.md` con tema y público | Sugerencias a partir de métricas | Calendario editorial con series |
| Guion | Un guion (JSON/Markdown) por pieza con cifras marcadas `{{cifra:id}}` | Editor de guion con conteo de duración por voz | Guion es/en con traducción asistida y revisión de cifras |
| Piezas | **Catálogo único de piezas** (animación, carrusel, deck, reel) en una vista; plantillas de marca (portada, tercio inferior, cierre) con parámetros | Biblioteca de escenas con datos reales (TLE/SPICE) como bloques arrastrables | Plantillas propias de cada serie; piezas con datos en vivo |
| Revisión de rigor | **Registro de cifras** (valor, unidad, fuente, fecha) y bloqueo si falta; lista de "cuidado" visible | Alertas de datos viejos (TLE > 30 días), comparación contra la tesis, revisor 2 con aprobación | Informe de procedencia exportable por pieza; versiones fechadas |
| Render multiformato | 16:9 + 9:16 + 4:5 con un botón desde el spec; prueba de loop; hoja de contacto | Cola de render con prioridades, caché de escenas, previsualización de baja calidad | Render distribuido opcional (VPS ya existe) |
| Publicación | Paquete listo: video, miniatura, pie, créditos, hashtags | Exportación nombrada por plataforma; programación manual con lista de pendientes | Publicación vía API de las redes (revisar condiciones de cada API) |
| Métricas | Hoja manual (CSV) de alcance por pieza | Importar métricas y compararlas con tipo de pieza | Panel de qué formatos y temas funcionan |

Prioridad del primer mes (en orden): 1) catálogo único y spec de pieza; 2) registro de cifras con fuentes; 3) botón de render multiformato; 4) verificación de loop; 5) paquete de publicación.

## 4. Arquitectura sugerida
- **Unidad central: la "pieza"** = un `pieza.json` con `id, tipo, tema, formatos[], idioma[], guion, cifras[{id,valor,unidad,fuente,url,fecha,revisor}], datos[{tipo:tle|spice, ref, época}], audio, estado`. Los specs actuales de carrusel y presentación se vuelven tipos de pieza (adaptadores, no reescritura).
- **Reutilizar**: motor Manim + `manim_extensions` (animaciones y marca), `motor_carrusel.py`, `decks_espaciales`/temas/fondos procedurales, herramientas de audio, `render_vertical`, runner Docker y VPS para render pesado.
- **Unificar**: 
  - Un solo front: la app Electron (ya llama a CLI Python de `animaciones/`); dejar PySide6 como respaldo y no seguir invirtiendo en él.
  - Una CLI Python única (`estudio render|verificar|empaquetar <pieza>`) que todos los fronts invocan; la app solo orquesta.
  - Un módulo `datos/` (TLE con caché y época, SPICE con kernels fijados) que alimenta las escenas Manim y registra la fuente automáticamente.
  - Un módulo `rigor/` (registro de cifras, verificador, informe de procedencia).
  - Un módulo `formatos/` (zonas seguras, 16:9/4:5/9:16, prueba de loop).
- **No adoptar** un segundo motor (Remotion o Motion Canvas) ahora: duplican el mantenimiento. Observarlos para la capa web interactiva futura. Blender/OpenSpace solo como renderizadores externos de planos hero, con resultado entrando como activo.
- Fondo estético: ya existen fondos procedurales y temas; mantenerlos como "tema de pieza".

## 5. Riesgos
- **Licencias de datos**: Space-Track limita la redistribución masiva; usar CelesTrak y publicar solo derivados con crédito ([notas](http://celestrak.org/norad/elements/notice.php)). SPICE: reconocer a NAIF ([reglas](https://naif.jpl.nasa.gov/naif/rules.html)).
- **Obras derivadas e imágenes**: material NASA suele estar libre, pero no el logo/insignia y puede traer créditos de terceros; no sugerir aval de NASA en piezas de marca ([guía NASA](https://nasa.gov/nasa-brand-center/images-and-media)). Cesium obliga a mostrar atribución ([guía](https://cesium.com/learn/ion/content-usage-and-attribution-guide/)). Stellarium es GPLv2: usarlo como programa externo, no copiar su código al repo ([wiki](https://github.com/Stellarium/stellarium/wiki/FAQ)).
- **Licencias de software**: Manim MIT sin problema; Remotion exige licencia de empresa desde 4 personas ([licencia](https://www.remotion.pro/license)); fuentes: Montserrat es OFL (versionada con su texto, bien); música y SFX sintéticos evitan derechos, pero comprobar que cualquier modelo de voz permita uso comercial (por revisar).
- **Costos de render**: Manim 1080p/8K y 3D son lentos; mitigar con caché por escena, previsualización baja, render local por defecto y VPS para lotes; multiformato multiplica el costo, así que el 9:16 debe reutilizar la misma escena con otra cámara y no volver a simular.
- **Mantenimiento**: 4 fronts y 3 formatos de spec ya crean deuda; riesgo de que la app Electron envuelva CLI frágiles. Mitigar con pruebas de humo en CI, sondas por librería (ya hay) y un único contrato `pieza.json`.
- **Rigor**: un registro de cifras mal mantenido da falsa seguridad. Que el bloqueo sea real (no publicable sin fuente) y que cada fuente lleve fecha de consulta.
- **Datos que caducan**: un TLE tiene vida corta; mostrar siempre la época en la pieza.
- **Plataformas sociales**: formatos y APIs cambian; no depender de publicación automática en el primer año.
- **Límites de esta investigación**: Canva, Figma, Jitter, Blender y NASA Eyes no tienen fuente web verificada en este informe.
