# Ronda 2: síntesis del estudio de edición Co.De Aerospace

Fecha: 2026-10-02. Fuentes: ronda1_motor (M), ronda1_producto (P), ronda1_contenido (C) y la retroalimentación de los 5 agentes que produjeron 26 carruseles (R). Solo lectura salvo este informe.
Leyenda: [HECHO] ya resuelto según el contexto recibido, no verificado por mí en el código. [PARCIAL] resuelto en parte.

---

## 1. Resumen ejecutivo

1. El estudio convierte las herramientas sueltas de Co.De (Manim, motor de carruseles, decks espaciales, audio sintético, app Electron) en una línea de producción de divulgación aeroespacial: una idea sale en carrusel 4:5, reel 9:16, video 16:9 y deck, con la misma marca.
2. Lo distinto no es el render, que Canva, Remotion o CapCut ya hacen. Es la verificación: ninguna herramienta de la competencia comprueba el contenido (P §1).
3. Cada cifra de una pieza debe tener fuente, fecha y revisor. Una pieza con cifras sin fuente no pasa a «publicable». Las ilustraciones, simulaciones y grabaciones llevan sello visible.
4. Los visuales salen de ciencia reproducible: Manim para el rigor matemático, y datos reales (TLE de CelesTrak con época visible, efemérides SPICE) en lugar de dibujos genéricos.
5. El audio es sintético y determinista, sin licencias de música, y los loops se verifican por función (mismo reloj en t y t+T), no por compresión de video.
6. El nicho tiene hueco: casi nadie divulga en español la ingeniería del segmento terreno, el espectro y la regulación con rigor de ingeniero (hipótesis de C; falta validarla con 20 cuentas).
7. La honestidad es parte de la marca: lo beta es beta, lo simulado se dice simulado, y las correcciones son públicas y fechadas.
8. El motor ya rinde (carrusel en ~9 s en vez de 1 a 2 min). La deuda está en la base: nada de `marca/` y `redes/` está en git, no hay pruebas automáticas, y audio y video comparten tiempos escritos a mano.
9. Falta la unidad común, la «pieza» (un `pieza.json` con cifras, formatos, idiomas y estado). Es la base para el catálogo, el registro de cifras y el paquete de publicación.
10. Se mide con tasas sobre alcance (guardados, envíos, % visto) en rondas de 4 semanas, y con una métrica de calidad que no se negocia: correcciones por pieza igual a cero.

---

## 2. Hoja de ruta única

Esfuerzo: S (≤ medio día), M (1 a 2 días), L (una semana o más). Origen entre corchetes. Los ítems repetidos entre informes están fusionados.

### 2.1 Hecho

| Qué | Origen | Estado |
|---|---|---|
| Render de carruseles ~9 s (antes 1 a 2 min) | R, M §2.4 (`escribir` lento) | [HECHO] |
| Centrado vertical, imágenes que se amplían, comparación apilada, tipos `termino` y `formula` | R | [HECHO] |
| Sello de rigor en la lámina (Ilustración / Simulación / Grabación) | C pendiente 5, C §4.2 | [HECHO] |
| Variantes A/B de carruseles | C §3.2 | [HECHO] |
| Atenuación de fondos temáticos bajo el texto (neuronal, cálculo, caos, espectro) | R | [HECHO] |
| Audio de reels sin clic en la costura y determinista | M1 (M §2.1) | [HECHO] |
| Loops verificados sin compresión | M2 parcial, P §2.4 | [PARCIAL]: falta confirmar que `verificar_loop.py` ya falla con código ≠ 0 y que el criterio es único (M §2.1). |

### 2.2 Ahora (esta semana y la siguiente)

| # | Qué | Por qué | Esfuerzo | Hecho cuando |
|---|---|---|---|---|
| A1 | **Versionar el motor**: commit de `marca/`, `redes/`, `marca_*.py`, `reels_promo.py`, `rotulos_aerospace.py`, `estelas.py`, `30` a `34`, `sonido_*`, `verificar_loop`, fuentes Montserrat. Añadir a `SKILL.md` una sección «Marca y redes» y corregir su contradicción (l. 118 y 143). | M12: hoy un `git clean` borra todo el motor. Es barato y evita el riesgo mayor. | S | `git status` sin `??` en esas rutas. `SKILL.md` describe el flujo render, audio y verificación, y la trampa de `-r 1080,1920`. |
| A2 | **Carruseles: que el desborde falle**. `ajustar()` debe avisar si el texto no cabe en `tam_min`, y `validar` debe tratarlo como error. | M §2.4 (severidad A): hoy un carrusel «válido» puede salir con texto fuera de caja. Los 26 de R lo sufrieron como láminas medio vacías o desbordadas. | S | Un título de 70 caracteres en cada tipo de lámina da error claro o cabe. `--validar` no pasa si algo desborda. |
| A3 | **Sticker y ruta seguros**: `cargar_imagen` solo acepta rutas dentro de `STICKERS`/`marca` y rechaza `tesis_*` aunque venga renombrado. Sanear `id` y `serie` con `^[a-z0-9-]+$`. Un `try/except` por spec en `main`, con resumen y código de salida. | M §2.4, C §5 (no filtrar tesis ni clientes). La barrera actual es un `in` de subcadenas. | S | Prueba con una copia renombrada de un sticker de tesis: se rechaza. `--todos` no se detiene por un spec malo. |
| A4 | **Fuentes y rutas portables**: copiar Rajdhani, DM Sans, Space Mono y Orbitron (con OFL) al repo. Quitar `sys.path.insert("/workspace/...")` de `30` a `33`. Llamar a `registrar_fuentes()` en `LogoCoDeCierre`. | M §2.3 y §2.2 (severidad A): en otra máquina el carrusel falla y el cierre sale con otra tipografía sin error. | S a M | `motor_carrusel.py --validar` funciona en una máquina limpia. El cierre del logo usa Montserrat en un contenedor sin la fuente instalada. |
| A5 | **Stickers de plataformas** Nexus, Triage y PiStation, con sus advertencias: PiStation es simulador, Triage con AUC 0.949 en test intacto y 0.806 en estaciones no vistas. | R (falta pedida por los agentes), C §5 (advertencias al pie de la letra). | M | Cada sticker pasa la lista de verificación de C §4.6 y lleva su sello de rigor. Se usa en al menos un carrusel. |
| A6 | **Registro de piezas y métricas desde ya** (CSV en `exports/estudio/`, columnas de C §3.3 con el `id` del JSON del carrusel). Las primeras 4 semanas son línea base. | C pendiente 4. Sin línea base no hay experimento posible. | S | Las 26 piezas ya producidas figuran con `id`, tema de fondo, tipo de portada y variante A/B. |
| A7 | **Hoja de verificación previa a publicar** (2 personas, 10 min, C §4.6) como archivo junto a cada carrusel (ampliar `_CUIDADO.txt`). | C §4, P (rigor). No requiere código nuevo. | S | Ningún carrusel se publica sin la hoja marcada. |
| A8 | **Confirmar en el Centro de ayuda de Instagram** tope de 5 hashtags, Reels hasta 3 min y colaboraciones hasta 5 cuentas. | C pendiente 1: tres datos marcados [R] sin documento oficial. | S | Cada dato queda con su enlace oficial o se descarta. |

### 2.3 Próximo (semanas 3 a 8)

| # | Qué | Por qué | Esfuerzo | Hecho cuando |
|---|---|---|---|---|
| B1 | **Serie cruzada «un pase, cinco plataformas»**: un mismo pase de satélite visto desde Orbit Eye, SAT-DT, Nexus, Triage y PiStation. Depende de A5. | R (propuesta de los agentes), C P2 y P6. Es la pieza que muestra la tesis del estudio. | M | 5 carruseles más un reel resumen, con cifras registradas y sello de rigor. Sale en la cadencia normal. |
| B2 | **Módulo `ciclos.py`** (numpy puro) con `Ciclo`, `doppler_*`, `ventana`, y el registro `CICLOS`. Video y audio leen lo mismo. Prueba exacta de periodicidad (reloj en `desfase` y en `desfase+T`, tolerancia ≤ 2). | M2: elimina D2, D3 y D5. Convierte «loop verificado» en garantía permanente. | M | Cambiar una ventana en un solo sitio mueve imagen y sonido. El test pasa en los 3 reels sin ffmpeg. |
| B3 | **Marcas de tiempo: el video las genera, el audio las consume.** `marcar()` en `animar_entrada`, `<escena>.marcas.json`, y `sonido_marca` lee de ahí. | M3 (causa raíz de D1). Hoy `ritmo≠1` o tocar un `play` desincroniza el sonido sin avisar. | M | `animar_entrada(ritmo=0.7)` suena sincronizado sin editar `sonido_marca.py`. Falta una marca da error, no silencio. |
| B4 | **Kit de marca único** `marca/kit.json` (bloques `marca`, `web`, `tipografia`, `zona_segura`) y `marca_kit.py`. Prueba de lint que falla con un hex de marca fuera del kit. | M4, D6 y D8: dos grises «tenue», `LINEA` duplicado y tres definiciones de zona segura. | M | `grep "#00D9FF"` solo da `kit.json` y los temas. Una sola zona segura por formato. |
| B5 | **Catálogo único de piezas y spec `pieza.json`** (id, tipo, tema, formatos, idiomas, guion, cifras, datos, audio, estado). Los specs de carrusel y deck se adaptan, no se reescriben. Vista en la app Electron. | P §3 y §4: hay 4 fronts y 3 formatos de spec sin unidad común. | L | Una pieza existente (un carrusel) se ve en la app con su estado, y los otros dos tipos se importan con adaptadores. |
| B6 | **Registro de cifras con bloqueo**: valor, unidad, fuente, URL, fecha de consulta y revisor. Una pieza con una cifra sin fuente queda en estado «no publicable». Sembrar con `CIFRAS_A_REVISAR.md` y los campos `fuentes`/`cuidado`. | P (diferenciador principal), C §4.1. | M | El comando de verificación falla con una cifra sin fuente. Las 26 piezas pasan o quedan marcadas. |
| B7 | **CLI única y manifiesto** `marca/piezas.json` y `python3 -m marca todo`: reemplaza los 3 `.sh` (logs visibles, `trap` para temporales, salto si el hash no cambió, escritura `.part` y `rename`, código de salida ≠ 0). | M5 más P §4 («una CLI que todos los fronts invocan»). Hoy los errores de Manim van a `/dev/null`. | M | Un render roto da un mensaje legible. Re-renderizar solo lo cambiado. Tabla final con duración, costura y LUFS. |
| B8 | **Suite `pytest` del motor**: humo de render a 270×480, textos con `lienzo.cabe()`, carruseles con texto extremo, audio (costura, duración, pico < 0.95), reproducibilidad, privacidad. | M6 (sin ninguna prueba hoy). Incluye A2, A3 y B2 como casos. | M | Una corrida local. Falla si se reintroduce el clic, el desborde o el sticker prohibido. |
| B9 | **Calendario y cadencia**: 2 carruseles y 1 reel por semana, mezcla de pilares según C §1, un video largo al mes. | C §2. Es lo que sostiene el equipo (2 o 3 personas, 12 a 15 h/semana). | S | 4 semanas cumplidas sin bajar la revisión de rigor. |
| B10 | **Primera ronda de experimentos**: una sola variable (gancho: pregunta, dato o promesa), 5 a 6 piezas por variante, emparejadas por pilar. Trial Reels como criba de reels. | C §3. | M | Decisión escrita (gana, pierde o «sin diferencia detectable») según la regla de C §3.4. |
| B11 | **Fondos robustos**: `tamano()` como context manager, clave de caché con versión del generador, temporal con PID, `cargar_plugins()` una sola vez. | M9 y M §2.3. | S | Dos procesos pidiendo el mismo fondo no se corrompen. Editar un tema invalida su caché. |
| B12 | **Voz humana en reels y video largo** (prueba «con voz vs sin voz»). Depende de la decisión D1 (sección 3). | C §0 y pendiente 3. | M | Dos reels comparables, con y sin voz, medidos a 7 días. |
| B13 | **Subtítulos revisados y alt text por lámina** dentro del flujo, no al final. Añadir `alt` por lámina y validación de `pie_texto` (≤ 2 200 caracteres, ≤ 5 hashtags según A8). | C §4.4, M §2.4. | M | Cada carrusel exporta su alt text. `pie_texto` se valida. |

### 2.4 Después (3 a 12 meses)

| # | Qué | Por qué | Esfuerzo | Hecho cuando |
|---|---|---|---|---|
| C1 | **Datos reales como bloques**: módulo `datos/` con TLE (CelesTrak, caché y época visible) y SPICE (kernels fijados). La fuente se acredita sola en el cuadro final. | P §2.1, §2.8 y §4. Aprovecha `satelites.py`, `kepler.py` y `seguidor_satelital.py`. | L | Una escena con TLE muestra «CelesTrak, época AAAA-MM-DD». Alerta si el TLE tiene más de 30 días. |
| C2 | **Plantillas de reel por JSON** (`reels/<id>.json`, con `ReelPlantilla`). Solo después de B2 y B7. | M10: sin ciclo declarativo no hay qué parametrizar. | L | Agregar un reel es un JSON más una función de dibujo. |
| C3 | **Unificar los sistemas paralelos** (`promo.py`, `sfx.py`, `musica.py`, `promo_verifica.py` frente a `reels_promo` y `sonido_*`). Conservar el piso de ruido de la costura y el manifiesto de audio. | M13 y D9. Cuatro generaciones de lo mismo. Solo con B8 como red de seguridad. | L | Un solo camino de audio y de verificación de bucle. |
| C4 | **Unificar rótulos** horizontales y verticales con un `Formato` único (adiós D7). | M7. | M | Se borran unas 90 líneas duplicadas. Un rótulo nuevo sale en 16:9 y 9:16 sin copias. |
| C5 | **Paquete de publicación**: video, miniatura, pie, créditos, alt text y hashtags, con nombre por plataforma. Después, publicación manual con lista de pendientes. | P §3 (1 y 3 meses). | M | Una carpeta por pieza lista para subir. |
| C6 | **Panel de métricas** que importa el CSV y cruza con tipo de pieza, fondo y pilar. | P §3 y C §3. | M | Gráfico de guardados y envíos por alcance, por variable en prueba. |
| C7 | **Versión en inglés con equivalencia de cifras** para carruseles y reels, como ya existe en decks (`verificar_traduccion.py`). | P §2.7. | M | Cifras es y en idénticas, comprobado por script. |
| C8 | **Render distribuido y caché de fotogramas** (VPS ya existe). | M11. Solo con B7 y B8 hechos. | L | Un lote usa varios nodos con caché compartido por hash. |
| C9 | **Colaboración mensual** con un club o universidad de nicho, y medirla como variable «colab sí/no». | C §2. | S por mes | 1 colaboración publicada al mes durante 3 meses. |
| C10 | **Partir `decks_espaciales.py`** (934 líneas) en módulos. | M §1.3. Sin defectos hoy: es higiene. | M | Los módulos pasan `pruebas_presentaciones.py` sin cambios. |

No hacer todavía: un segundo motor (Remotion o Motion Canvas, P §4), publicación automática por API (P §5), fusionar `promo.py` con lo nuevo sin pruebas (M).

---

## 3. Decisiones que necesita tomar el dueño

**D1. Voz humana del proyecto.**
- a) Rostro y voz de una persona (Yuritzi u otra).
- b) Solo voz en off, sin rostro.
- c) Sin voz (solo animación y texto).
Recomendación: b) para empezar. Da identidad sin exponer a nadie, y B12 la contrasta contra c). Se decide con datos a las 4 semanas.

**D2. Versionar el motor y quién firma los commits (A1).**
- a) Commit ahora de todo lo que está sin versionar.
- b) Revisar primero qué entra.
- c) Repositorio aparte para `marca/` y `redes/`.
Recomendación: a), con una revisión rápida de privacidad (que no entre nada de tesis ni clientes). Es el riesgo más barato de eliminar. El repo no tiene `user.name` configurado.

**D3. Qué sistema de audio y bucle se conserva (M13).**
- a) `promo.py`, `sfx.py` y `musica.py`.
- b) `reels_promo` y `sonido_*`.
- c) Fusión gradual.
Recomendación: c). Conservar el piso de ruido de `promo_verifica` y el manifiesto de audio. Migrar la síntesis nueva a `sfx.py` solo después de B8.

**D4. Un solo front.**
- a) La app Electron como única interfaz y PySide6 en respaldo.
- b) Seguir con ambas.
Recomendación: a). P señala 4 fronts y 3 formatos de spec; no invertir más en PySide6.

**D5. Cadencia de publicación.**
- a) 2 carruseles y 1 reel por semana (12 piezas al mes).
- b) 1 carrusel y 1 reel por semana.
- c) Diario.
Recomendación: a). C cita a Mosseri: lo sostenible gana. Si la calidad baja, bajar a b), nunca recortar la revisión de rigor.

**D6. Qué plataformas se muestran y con qué advertencias (serie cruzada B1).**
- a) Las cinco (Orbit Eye, SAT-DT, Nexus, Triage, PiStation), cada una con su sello.
- b) Solo las tres con respaldo medido.
- c) Aplazar la serie hasta tener Nexus y Triage con datos propios.
Recomendación: a), siempre que cada una lleve la advertencia de C §5 (sin receptor, telemetría simulada, simulador, una sola observación, AUC con su contexto). Orbit Eye exige además atribuir a Stratos Goudelis y la licencia GPL-3.0.

**D7. Cuánto vender.**
- a) Una de cada cuatro piezas con llamada comercial (C §4.9).
- b) Una de cada ocho.
- c) Ninguna al inicio.
Recomendación: b) los dos primeros meses para construir confianza, luego a). Hay que fijarlo por escrito para que no derive.

**D8. Política de corrección pública (C §4.7).**
- a) Adoptarla como está: corregir en menos de 24 h, nota «Corrección:» fechada, `CORRECCIONES.md` interno.
- b) Versión ligera: solo nota en el pie.
Recomendación: a). Es parte del producto, y con ella cada pieza se vuelve más creíble que las de la competencia.

---

## 4. Riesgos principales y mitigación

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Motor sin versionar (`marca/`, `redes/`, módulos Manim) | Pérdida total ante un `git clean` o un fallo de disco | A1 inmediato. Después, copia del repo en el VPS. |
| Cifra sin fuente o ilustración tomada por dato | Pérdida de la credibilidad, que es el producto | B6 con bloqueo real. Sello de rigor [HECHO]. Hoja de verificación (A7). Los números dentro de stickers son ilustrativos y no se citan nunca. |
| Filtrar tesis o clientes | Daño legal y de confianza | A3 (barrera de rutas sólida). B8 incluye una prueba de privacidad. Revisión humana antes de A1. |
| Vender lo beta o simulado como logro | Reclamo público | Advertencias al pie de la letra (C §5). Una observación se llama «una medición». |
| Licencias: Orbit Eye es obra derivada GPL-3.0. Space-Track limita la redistribución. NASA no avala. Fuentes OFL. | Incumplimiento | Atribuir siempre. Usar CelesTrak y publicar solo derivados con época. No usar insignia de NASA. Copiar OFL junto a cada fuente (A4). |
| Desincronía audio y video | Banda sonora rota sin aviso | B3 y B2. Mientras tanto, no cambiar `ritmo` en piezas con audio. |
| Entorno frágil (rutas de `/workspace`, fuentes en `~/.local`) | Falla o tipografía distinta en otra máquina o CI | A4 y B4. |
| Conclusiones con muestras pequeñas | Cambiar la línea editorial por ruido | Protocolo de C §3.4: 5 a 6 piezas por variante, dirección repetida en 4 de 6, diferencia ≥ 30 %. «Sin diferencia detectable» es un resultado válido. |
| Dependencia de Instagram y de datos [R] sin confirmar | Decisiones sobre un algoritmo que cambia | A8. Replicar a YouTube y TikTok. Construir lista (newsletter o comunidad). No afirmar en público «el algoritmo premia X». |
| Agotamiento del equipo (2 o 3 personas) | Calidad a la baja | Cadencia D5. Producir en lotes. Reutilizar cada carrusel como reel. |
| Deuda de mantenimiento: 4 fronts, 3 formatos, 4 generaciones de audio | Cada mes cuesta más unificar | D4, D3 y B5. No crear una quinta variante. |
| Memoria en panorámicas de 10 láminas (estimado, ~2 GB, sin medir) | Cierre del proceso en equipos chicos | Medir con una panorámica de 10 láminas. Limitar a 8 si pasa de 2 GB. |
| Datos que caducan (TLE, fechas de eventos, «T-402d») | Pieza vieja con dato falso | Mostrar siempre la época. Alerta a 30 días (C1). Eventos del cielo solo con fecha de fuente oficial. |
| Copiar de otras cuentas o subir con marca de agua | Menor alcance según Meta [O] | Publicar originales sin marca de agua en cada plataforma. |

---

## 5. Métricas

### 5.1 De producción: ¿el estudio funciona?

| Métrica | Meta inicial | Cómo se mide |
|---|---|---|
| Tiempo de idea a carrusel publicable | ≤ 2 h por carrusel (4 en lote) | Marca de tiempo en el registro de piezas. |
| Tiempo de render de un carrusel | ≤ 15 s (hoy ~9 s) | Salida del CLI. |
| Piezas por semana | 3 (2 carruseles y 1 reel) durante 4 semanas seguidas | Registro. |
| Reutilización | ≥ 50 % de los reels nacen de un carrusel o al revés | Columna «origen» del registro. |
| Piezas con cifras 100 % con fuente | 100 % antes de publicar | Verificador de B6. |
| Correcciones por pieza (calidad) | 0. Si no, se detiene la línea | Columna `correcciones` y `CORRECCIONES.md`. |
| Fallos de validación detectados antes de publicar (desborde, sticker prohibido, fuente) | Todo defecto de §2.4 de M detectado por el validador, ninguno por ojo | Suite de B8. |
| Loops con costura sobre el umbral | 0 | Prueba exacta de B2. |
| Reproducibilidad | Mismo spec, mismo PNG o wav bit a bit | Prueba de B8. |
| Cobertura de la hoja de verificación | 100 % de las piezas | Archivo marcado por pieza. |

### 5.2 De audiencia

Siempre en tasas sobre alcance, a los 7 días, separando seguidores de no seguidores. Se fija la métrica principal antes de publicar (C §3.1).

| Formato | Métrica principal | Secundarias |
|---|---|---|
| Carrusel | Guardados por alcance (línea base esperada 2 a 3 % [F]) | Envíos por alcance, % de finalización, alcance de no seguidores |
| Reel | Vistas completas por alcance y envíos por alcance | % visto, repeticiones (bucle), comentarios |
| Todos | Seguidores ganados por pieza | Alcance de no seguidores como %, colaboración sí o no |

- **Descubrimiento**: alcance de no seguidores (%) y envíos por alcance, sobre todo en eventos del cielo (P6).
- **Autoridad**: guardados por alcance en espectro y tecnología Co.De, más mensajes y solicitudes de diagnóstico, con un máximo de 1 de cada 4 piezas comerciales.
- **Confianza**: correcciones por pieza (meta 0) y tiempo medio de corrección (< 24 h).
- Regla de decisión (C §3.4): se cambia una práctica solo si la dirección se repite en ≥ 4 de 6 pares y la diferencia agregada es ≥ 30 % relativo. En caso contrario, «sin diferencia detectable».
- Las 4 primeras semanas son línea base, no experimento. Los benchmarks globales ([F]) no sustituyen los datos propios.
- Hipótesis a contrastar: reel igual a descubrimiento, carrusel igual a guardado y autoridad. El hueco en español de espectro y segmento terreno se valida antes de afirmarlo en público.
