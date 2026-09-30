---
name: animaciones-code
description: Produce y empaqueta las animaciones ilustrativas de Co.De Aerospace (Manim, sin títulos ni narración) para ponencias — escenas nuevas, videos 1080p en fondo oscuro/claro, PNG transparentes 8K, stickers recortados, hojas de conjunto, presentaciones PowerPoint, ponencias de divulgación con guion a dos voces, compartir al celular, presentaciones de tesis (seminario de divulgación y comité tutorial), videos que no dejan la pantalla en blanco, montajes y guía. Úsala cuando se pida crear/modificar una animación o pieza de la ponencia o de la tesis, armar una presentación nueva con esas piezas o pasarla al celular (constelaciones, seguidor satelital, IA en satélites, banco de pruebas, antenas, robots), renderizar, sacar PNG/stickers, armar el .pptx o revisar que las cifras coincidan con la tesis.
---

# Animaciones Co.De (ponencia)

Todo vive en `animaciones/` del repo `codeaerospace_contenido`. Salidas en `exports/` (fuera de git).
Comandos siempre **desde `animaciones/`** (las escenas hacen `from code_lib import *`).

## Formato de una pieza (regla del dueño)
- **Sin narración, sin títulos, sin subtítulos.** Solo etiquetas imprescindibles de diagrama, **máx. 3 palabras** (las cifras cuentan como una). `et()`, `et_junto()` y `cifra()` de `code_lib.py` abortan si te pasas. Los títulos los pone PowerPoint (ver «Presentación de divulgación»: la regla es de la pieza, no de la diapositiva).
- En **español** con acentos; fuente **Carlito** (`FUENTE`). Cifras vivas con `DecimalNumber` de `code_lib` (ya redefinido en Carlito; el de Manim usa LaTeX y sale serif).
- 13–27 s, arco claro (construir → fenómeno → estado final legible) y termina con `self.cierre()`.
- Sin marca de agua ni HUD: la pieza se funde con el slide.
- Paleta con **roles fijos** (nunca WHITE/BLACK/BLUE sueltos; se invierte sola con `CODE_TEMA=claro`): satélite `C_SAT` ámbar · antena/estación `C_ANT` cian · cielo/referencias `C_CIELO` violeta · falla `C_MAL` rojo · logrado `C_OK` verde · mobiliario `C_EJE` · texto `TINTA`/`TENUE`. Fondo navy `#0B1F3A` (oscuro) o blanco (claro).
- Clases base: `Pieza` (2D) y `Pieza3D`. Una clase = un video. Nombre PascalCase en español. Determinista (numpy con semilla), sin red ni archivos externos.
- Helpers en `code_lib.py`: `tierra`, `satelite`, `estacion`, `antena_parabolica`, `nodo`, `caja`, `flecha`, `haz`, `estrellas`, `esfera_tierra`, `orbita3d`, `punto_orbita3d`. No editar `code_lib.py` para una sola escena: define el helper en el archivo de la escena.

## Archivos
| Archivo | Qué es |
|---|---|
| `espacio_orbitas.py`, `constelaciones.py`, `ntn_6g.py`, `seguidor_satelital.py`, `ia_satelites.py`, `banco_pruebas.py`, `antenas_robots.py` | Las 65 escenas por tema |
| `catalogo.py` | Bloques en orden narrativo, qué muestra cada pieza, cuándo usarla, ⭐ recomendada. **Toda pieza nueva se registra aquí** |
| `render_todo.sh` | Videos 1080p30 → `exports/<archivo>/{oscuro,claro}/<Pieza>.mp4` |
| `render_fotos.sh` | PNG **transparente 8K** (7680×4320) del instante 60 % de cada pieza → `exports/png/{oscuro,claro}/<tema>/` (necesita los mp4 para conocer la duración) |
| `postproceso_fotos.py` | Stickers recortados (`exports/png/stickers/...`, margen 3 %) + hojas de conjunto 8K (`exports/png/conjunto/`). Incremental |
| `empaquetar_ponencia.py [presentaciones\|stickers\|montajes\|todo]` | `.pptx` completo y selección, biblioteca de stickers, montajes por bloque y `reel_recomendadas` |
| `guia_ponencia.py` | `exports/GUIA_PONENCIA.md` desde `catalogo.py` + duraciones reales |
| `ponencia_divulgacion.py` | Ponencia de divulgación (~30 min, dos voces): reutiliza los mp4 sin renderizar → `exports/presentaciones/redes_orbitales_divulgacion_*.pptx` y `exports/GUION_REDES_ORBITALES.md`. Ver sección siguiente |
| `ponencia_redes_orbitales.py` | Primer borrador (sin guion ni subtítulos). Se conserva; no lo uses de base |
| `tesis_lib.py` | Helpers de las piezas de tesis: chips de estatus (`chip_desarrollo`, `chip_ilustrativo`, `chip_tercero`), `trazo`, `cifra_viva`, `marca_ok/no`, `barra` |
| `tesis_sem_{1_orbita,2_examen,3_resultados}.py` | 21 piezas del seminario de divulgación de la tesis |
| `tesis_com_{1_problema,2_marco,3_evidencia,4_cierre}.py` | 26 piezas del comité tutorial (tono sobrio, esquemático) |
| `catalogo_tesis.py` | Registro de esas 47 piezas (las de la ponencia Co.De siguen en `catalogo.py`); `guia_tesis.py` → `exports/GUIA_TESIS_PIEZAS.md` |
| `tesis_decks.py` + `tesis_seminario.py` + `tesis_comite.py` | Constructor común y contenido (`DIAPOS`, guion) de los dos decks de tesis → `exports/presentaciones/{seminario_agentes_ia_orbita,comite_tutorial_protocolo}_{oscuro,claro}.pptx` y `exports/GUION_*.md` |

## Flujo de una escena nueva
1. Escribirla en el archivo del tema y registrarla en `catalogo.py`.
2. Previsualizar un fotograma barato (sin renderizar todo el video):
   `CODE_FOTO_T=<seg> CODE_FOTO_SALIDA=/ruta/f.png CODE_TEMA=oscuro manim render -s -t -ql --media_dir <tmp> tema.py Clase`
   y **mirar la imagen** (composición, solapes, que se entienda sin texto). Probar también `CODE_TEMA=claro`.
3. Render final: `./render_todo.sh ambos archivo.py` (o `SOLO="ClaseA ClaseB" FORZAR=1 ./render_todo.sh ambos` para rehacer solo algunas; por defecto no pisa lo existente).
4. PNG/stickers: `SOLO="..." FORZAR=1 ./render_fotos.sh ambos` → `python3 postproceso_fotos.py`.
5. Empaquetar: `python3 empaquetar_ponencia.py todo` y `python3 guia_ponencia.py`.

Variables útiles: `JOBS` (paralelo, def. 4), `CALIDAD` (def. `-r 1920,1080 --fps 30`), `RES` (def. `7680,4320`), `FRACCION` (def. 0.6).

## Presentación de divulgación (con guion)
Cuando la charla es para público general, la diapositiva sí lleva **título-afirmación y subtítulo**, y las notas llevan el **guion**; el video no se toca ni se vuelve a renderizar (ahorra mucho cómputo).
- Todo sale de la lista `DIAPOS` de `ponencia_divulgacion.py`: tuplas `portada · texto · seccion · video · cierre`, con quién habla y el guion. `AMPLIA` añade analogías al final del guion de una pieza. Para otra charla, copia el archivo y cambia `TITULO`, `LEMA`, `DIAPOS`; el diseño (título arriba, subtítulo en acento, video 16:9 de 5.5 in, etiqueta de voz abajo) ya está resuelto.
- **Tiempo**: `RITMO` (140 palabras/min) × palabras del guion. El script imprime minutos totales y por voz; ajusta hasta el objetivo (30 min ≈ 4 100 palabras, unas 55 diapositivas). Los videos no suman: se habla encima.
- **Dos voces**: reparte por tema de tesis, con relevos explícitos («le paso la palabra a…»). Pronombres solo si el dueño los dio (ella para Yuritsi); para Alan usar el nombre.
- **Honestidad**: no inventar hechos de una tesis ajena. Lo que no se sepa va como hueco `[NOMBRE: …]` en el guion y se avisa al usuario. Sin cifras de mercado. Marcar lo ilustrativo y decir lo pendiente (G3).
- Genera además `exports/GUION_REDES_ORBITALES.md` con hora estimada por diapositiva. Revisar con `soffice` → PDF → `pdftoppm` → hoja de contacto, y mirar la imagen.
- El título de la charla lo fija el dueño; si lo cambia, edita `TITULO`/`LEMA` y regenera (tarda ~5 min por los videos embebidos).

## Presentaciones de tesis (seminario y comité)
Piezas y decks **propios** de la tesis «Gobernanza autónoma de redes programables» (Alan Rosas Palacios, IPN); los guiones de origen viven en el repo privado de la tesis (`06_PRODUCTOS_CIENTIFICOS/05_PRESENTACIONES_SEMESTRE_2026_S2/GUION_*.md`) y mandan sobre cualquier cifra.
- **Flujo**: guion → lista de piezas (una idea por pieza, metáfora visual propia, distinta de `CicloPADA`/`MargenAdaptativo`/`CompuertasValidacion`) → escenas (se puede repartir entre agentes, un archivo `tesis_*.py` por agente, brief común con reglas + cifras permitidas) → render 1080p oscuro/claro → PNG 8K → `python3 tesis_seminario.py` / `tesis_comite.py` (`--solo-guion` para el tiempo) → revisar con `soffice` → PDF → hoja de contacto.
- **Honestidad en pantalla (regla de la tesis)**: lo propio sin validar a escala (PADA, Margen Adaptativo, NTNEnv-v2, QMIX, compuertas) lleva `chip_desarrollo()`; lo de terceros, `chip_tercero("Autor año")`; lo de ejemplo, `chip_ilustrativo()`; lo no ratificado, `chip("Propuesto", C_CIELO)`. G3/G4 siempre punteadas («Pendiente»). Los datos entran desde el archivo (`G2B_RECUALIFICACION_v7.json`), no se teclean. Las advertencias de «lo que NO se puede afirmar» van en las notas (⚠️ CUIDADO), nunca en la diapositiva. Dudas de ratificación y qué es real/ilustrativo: `exports/CIFRAS_A_REVISAR.md` (sección de tesis).
- **Seminario** (divulgación, una voz, ~27 min, 40 + 5 de respaldo): cero jerga, analogías, primera persona. **Comité** (hostil y metodológico, ~21 min, 31 + 7 de respaldo): tono sobrio, sin analogías cotidianas; las respuestas a P1, P2, P5, P6, P11, P12, P13 van como diapositivas de respaldo fuera del tiempo.
- Tipos de diapositiva de `tesis_decks.py`: `portada · seccion · video · texto · cita · cierre · respaldo`; título largo (>50 caracteres) baja subtítulo y viñetas solo.

## Videos en PowerPoint: nunca pantalla en blanco
`self.cierre()` funde todo a fondo limpio, así que un video que termina deja la diapositiva vacía. `tesis_decks.video_final()` hace una copia **sin el fundido** (detecta dónde empieza midiendo el contenido de los últimos 4 s y recorta con ffmpeg, sin re-renderizar) en `exports/<archivo>/<tema>_final/`, y el póster de la diapositiva es su último cuadro: el diagrama completo se ve antes y después de reproducir. PowerPoint deja visible el último cuadro al terminar. El original no se toca. `ponencia_divulgacion.py` ya lo usa; `empaquetar_ponencia.py` (ponencia_completa/seleccion, a pantalla completa) todavía no.

## Compartir con el celular
El usuario suele pedirlo cuando está lejos de la computadora.
- Una página de Artifact **no admite `.pptx`/`.zip`** (ni partirlos en trozos: sería saltarse la regla). Lo que sí sirve: PDF ligero + diapositivas en JPG + guion `.md`.
- PDF ligero: `soffice -env:UserInstallation=file://<tmp>/perfil --headless --convert-to pdf` (perfil aparte, si no choca con una instancia abierta del usuario) → `pdftoppm -r 96 -jpeg -jpegopt quality=78` → juntar los JPG con Pillow. Sale ~2.5 MB por tema (el PDF directo pesa ~45 MB).
- Página: capacidad `downloads`; el PDF con `fetch` + `downloads.save`, más un enlace «Ver PDF». **Los enlaces `download` no funcionan en el visor** y a veces el guardado falla en el celular, por eso la página también muestra las 55 diapositivas como imágenes (`dia/<tema>-NN.jpg`) y el guion plegable: leer no depende de descargar.
- Publicar solo tras confirmar con el usuario (contenido de tesis); la página es privada, solo su dueño. Pasar `files` como lista de rutas (no acepta carpetas).

## Cómo funciona el fotograma
`CODE_FOTO_T` detiene la escena en ese segundo y guarda el PNG con alfa (`-s -t`); el mixin de `code_lib.py` fuerza pasos finos porque en modo salto Manim ejecuta cada animación de golpe. El estado **final** de muchas escenas no sirve (el satélite ya salió, todo se funde): por eso el sticker es el instante ~60 %. Si un sticker no muestra lo esperado, rehacer con otro `FRACCION`.

## Rigor: cifras
- Las cifras en pantalla **no deben contradecir la tesis** (`tesis-doctorado-6g`, repo privado del autor; GATES.md manda). Ejemplos ya corregidos: Margen Adaptativo es propiedad del **banco** (oráculo vs mejor estática; G0 1.7 % → G1 31.8 %), la heurística rinde **por debajo** de la estática, QMIX ≈ +9.5…+16.3 %, compuertas G0/G1/G2a/G2b/G3 (G3 pendiente), validación con **3 agentes**, umbral 25 % = criterio de diseño (no literatura).
- Todo número inventado lleva etiqueta `Ilustrativo`/`Ejemplo` (≤3 palabras) o se quita. No usar los 45.3/210 ms de la defensa predoctoral (banco MVP1-2 desautorizado).
- Registro de qué es REAL / ESTÁNDAR / ILUSTRATIVO: `exports/CIFRAS_A_REVISAR.md`. Actualizarlo al cambiar cifras.

## Trampas conocidas
- **No borrar nada** de `exports/` sin que el usuario lo pida: él revisa y decide. `seleccion` y `⭐` son marcas, no filtros.
- Los PNG de escenas `Pieza3D` y `ArregloFases`/`Tierra3DSatelites`/`CamaraTermoVacio` son lentos; lanzarlas sin saturar los 8 núcleos.
- Renders en paralelo con el mismo `--media_dir` se corrompen (lista de fragmentos y archivos Tex compartidos); los scripts ya usan un tmp por tarea. Si pruebas a mano en paralelo, usa un `--media_dir` distinto por proceso.
- Vigilar procesos en segundo plano con `pgrep -f "[r]ender_todo.sh"` (los corchetes evitan que el `pgrep` se detecte a sí mismo y el bucle nunca termine). No matar procesos del usuario.
- Un `.pptx` con 65 videos pesa ~85 MB; los videos arrancan al clic (no probado el autoplay). Para stickers usar la versión de `png/stickers/<oscuro|claro>` según el fondo del slide: el texto oscuro se pierde sobre navy y viceversa.
- Git: no hay `user.name`/`user.email` configurados en esta máquina; el commit y el push con identidad prestada fueron bloqueados y quedan para el usuario. No configurar git ni forzar el push sin que lo autorice.
- `app/render_launcher.py` solo descubre escenas de la raíz, no de `animaciones/`.
- Un render lanzado con `nohup … &` dentro de la herramienta Bash puede terminar sin producir nada; usar `run_in_background` de la herramienta. Los PNG de `CODE_FOTO_T` salen **transparentes**: para juzgar el tema oscuro, componerlos sobre el fondo del tema (o usar fotogramas del mp4).
- No sobrescribir un `.pptx` que el usuario tenga abierto (LibreOffice deja `.~lock.<nombre>#` en `exports/presentaciones/`); escribir a otro nombre y avisar.

## Dependencias
`manim` (0.21), `numpy`, `Pillow`, `python-pptx`, `ffmpeg`, LaTeX (para `MathTex` puntual), fuente Carlito instalada. `soffice` sirve para revisar los `.pptx` (convertir a PDF y mirar los pósters).
