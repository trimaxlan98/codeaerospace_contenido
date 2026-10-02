# Plan de pruebas A/B de carruseles, ronda 1

Fecha: 2026-10-02. Base: `exports/estudio/informes/ronda1_contenido.md` §3 y `redes/carruseles/ESQUEMA.md`.
Nada de esto está publicado. Las variantes se definen en el campo `variantes` de cada spec y salen renderizadas como `<id>-b` y `<id>-c` en `exports/estudio/carruseles/<serie>/`.

## 1. Experimentos (8 carruseles, 5 series, 13 variantes)

Cada variante cambia UNA sola variable de la lámina 1 (o del fondo). El contenido, las cifras, el cierre y el pie de texto son idénticos; el pie arranca igual en todas las versiones (una pequeña fuga del gancho, anotada abajo). El gancho de cada variante es verdadero y fiel a las fuentes del spec.

| # | Id base (serie, pilar) | Variantes | Variable en prueba | Hipótesis | Métrica principal (7 d) |
|---|---|---|---|---|---|
| E1 | `satelite-no-se-cae` (divulgacion-orbital, P1) | A pregunta «¿Por qué un satélite no se cae?»; b dato «Un satélite viaja a 7.7 km/s y aun así está cayendo»; c promesa «Entiende en 8 láminas por qué un satélite no se cae» | Gancho (título y subtítulo) | La promesa concreta saca más guardados; la pregunta, más deslizamientos | guardados/alcance |
| E3 | `latencia-orbita-baja` (espectro-y-senales, P3) | A afirmación «Tu videollamada depende de la velocidad de la luz»; b pregunta «¿Cuánto retrasa la luz tu videollamada?»; c dato «En GEO, la luz tarda unos 240 ms solo en subir y bajar» | Gancho | El dato numérico supera a la afirmación en guardados | guardados/alcance |
| E6 | `plataformas-sat-dt` (plataformas, P2) | A pregunta «¿Y si pudieras probar qué le pasa a toda una constelación?»; b promesa «Ensaya fallas de una constelación sin tocar hardware»; c dato «146 pruebas en verde respaldan este gemelo digital» | Gancho | La promesa concreta gana envíos (la gente lo manda a quien trabaja en el tema) | envíos/alcance |
| E8 | `cifras-con-fecha` (como-trabajamos, P5) | A afirmación «Una cifra sin fecha no es un dato»; b pregunta «¿De cuándo es esa cifra que acabas de leer?»; c promesa «Aprende a leer una cifra: fecha, origen y alcance» | Gancho | La promesa gana guardados (es una regla guardable) | guardados/alcance |
| E4 | `fft-y-cascada` (espectro-y-senales, P3) | A logo (por defecto); b sticker `antenas_robots/EspectroFourier` | Portada con logo vs con sticker | El sticker detiene más el scroll: más alcance a no seguidores | guardados/alcance (secundaria: % de alcance a no seguidores) |
| E5 | `plataformas-triage` (plataformas, P2) | A logo; b sticker `plataformas/TriageCascadas` | Portada con logo vs con sticker | Igual que E4, y el sticker explica el producto de un vistazo | guardados/alcance (secundaria: % no seguidores) |
| E2 | `leo-meo-geo` (divulgacion-orbital, P1) | A `lunar` (base); b `orbita`; c `nebulosa` | Tema de fondo | El fondo no cambia los guardados; solo la detención en el feed | guardados/alcance (secundaria: % no seguidores) |
| E7 | `mito-sin-gravedad` (glosario-y-mitos, P1) | A `marte` (base); b `orbita`; c `mision` | Tema de fondo | Igual que E2; los mitos viven de los envíos | envíos/alcance |

Notas de la tabla:
- La numeración conserva el orden de elección; los experimentos de gancho son E1, E3, E6 y E8.
- Las dos variantes de sticker (E4, E5) comparten variable; los dos de fondo (E2, E7) también.
- Se miraron las portadas de las 13 variantes: se leen bien, ningún título se corta. En E2 las portadas `orbita` y `nebulosa` casi no se distinguen de `lunar` en la lámina 1 (fondo muy oscuro); el efecto del fondo se ve más en las láminas siguientes, así que se espera una diferencia pequeña (la hipótesis nula es razonable).
- Al ser variantes de gancho, el nivel de la base cuenta como un nivel más: pregunta (E1-A, E6-A, E3-b, E8-b), dato (E1-b, E3-c, E6-c), promesa (E1-c, E6-b, E8-c) y afirmación (E3-A, E8-A).
- La métrica principal se fija ahora, antes de publicar. El resto (comentarios, likes, seguidores ganados) se registra pero no decide.
- Hay 8 carruseles pero solo 5 series; por eso hay dos carruseles en `divulgacion-orbital`, `espectro-y-senales` y `plataformas`.

## 2. Diseño y emparejamiento

- Unidad de bloqueo: el propio carrusel (mismo pilar, mismo contenido). Se compara cada variante contra sus hermanas, no contra otros carruseles. Esto cubre el «mismo pilar y semana» del protocolo de forma más estricta.
- Una variable por ronda: la ronda 1 (semanas 1 a 4, con segunda oleada en 5 a 8) prueba SOLO el gancho. Sticker vs logo es la ronda 2 y fondo es la ronda 3 (sección 4). Mezclarlas en la misma ronda rompería la regla.
- Orden: cada carrusel se publica en tres semanas distintas, una versión por semana, con orden rotado (cuadrado latino aproximado) para que «la semana» y «ver el mismo tema por tercera vez» no favorezcan siempre al mismo gancho.
  - E1: c, A, b (promesa, pregunta, dato)
  - E3: b, c, A (pregunta, dato, afirmación)
  - E6: A, b, c (pregunta, promesa, dato)
  - E8: c, A, b (promesa, afirmación, pregunta)
  - Posición de la pregunta: 2.ª (E1), 1.ª (E3), 1.ª (E6), 3.ª (E8). Con 4 carruseles no se puede equilibrar todo; se anota el orden en cada fila del registro para revisarlo.
- Para E4 a E7 (rondas siguientes) el orden se alterna A-B / B-A entre carruseles: E4 A-B, E5 B-A; E2 `lunar`-`orbita`-`nebulosa` en E2 y `marte`-`mision`-`orbita` en E7.
- Misma hora y día de la semana dentro de cada experimento; todas las piezas en las dos franjas fijas del informe (12:30 y 20:00 CDMX), alternando la franja entre versiones del mismo carrusel.
- Misma longitud de pie y hashtags. El pie arranca con el gancho de la versión A; es un confundido menor y se acepta para no tocar más de una variable. Si se prefiere pureza, reescribir solo la primera frase del pie por variante (`pie_texto` admite parche).
- Registro: la tabla de §3.3 del informe, una fila por pieza, con el `id` de la variante (`<id>-b`) y una columna `orden` (1.ª, 2.ª, 3.ª publicación de ese carrusel).

## 3. Calendario de 4 semanas (oleada 1 de la ronda 1: gancho)

Suposición: 3 carruseles por semana (el informe prevé 2 por semana más reels; la ronda exige 3). Si solo hay 2, el mismo orden se estira a 6 semanas. Reels y el resto de la parrilla siguen igual y no entran en el experimento.

| Semana | Pieza 1 | Pieza 2 | Pieza 3 |
|---|---|---|---|
| 1 | E1 `satelite-no-se-cae-c` (promesa) | E6 `plataformas-sat-dt` (pregunta, A) | E8 `cifras-con-fecha-c` (promesa) |
| 2 | E3 `latencia-orbita-baja-b` (pregunta) | E1 `satelite-no-se-cae` (pregunta, A) | E6 `plataformas-sat-dt-b` (promesa) |
| 3 | E8 `cifras-con-fecha` (afirmación, A) | E3 `latencia-orbita-baja-c` (dato) | E1 `satelite-no-se-cae-b` (dato) |
| 4 | E6 `plataformas-sat-dt-c` (dato) | E8 `cifras-con-fecha-b` (pregunta) | E3 `latencia-orbita-baja` (afirmación, A) |

Cada carrusel queda espaciado una semana entre sus versiones (mínimo 7 días entre dos versiones del mismo tema).

Lectura de resultados: cada pieza se mide a los 7 días exactos de su publicación; la última pieza (semana 4) se mide en la semana 5.

Piezas acumuladas al final de la semana 4: 12, es decir, pregunta 4, dato 3, promesa 3, afirmación 2. Esto NO alcanza las 5 a 6 piezas por variante que pide el protocolo; por eso la semana 5 es de medición y NO se concluye nada todavía (solo se anotan tendencias).

Oleada 2 (semanas 5 a 8, para llegar a 5 a 6 piezas por nivel): repetir el mismo esquema con 4 carruseles nuevos que tengan portada de pregunta, dato y promesa (hay que escribir 8 variantes más; candidatos: `leo-meo-geo`, `ventana-de-contacto`, `doppler-curva-en-s`, `espectro-recurso-escaso`, `interferencia-ngso-geo`, `plataformas-triage`, `plataformas-atp-dt`, `mito-ia-pilotea`). Al final de la semana 8 hay unas 24 piezas, unas 6 por nivel, y se aplica la regla de decisión.

Después (rondas siguientes, una variable por ronda de 4 semanas, mismo calendario):
- Ronda 2 (semanas 9 a 12): sticker vs logo. Ya listas E4 y E5; faltan 3 o 4 pares más (portadas con sticker bueno: `ventana-de-contacto`, `plataformas-pistation`, `plataformas-code-nexus`, `transferencia-hohmann`) para llegar a 5 a 6 pares.
- Ronda 3 (semanas 13 a 16): fondo `orbita` vs `nebulosa` vs `mision`. Ya listas E2 y E7; faltan 3 o 4 carruseles más. Se prueba solo con esos tres temas.
- La hora/día, el número de láminas y el pilar se dejan para otras rondas; no se mezclan.

## 4. Regla de decisión (fijada antes de publicar)

Aplica por variable al final de la oleada que complete 5 a 6 piezas por nivel. Para el gancho, cada carrusel aporta un «emparejamiento»: se ordenan sus versiones por la métrica principal.

1. Métrica principal por experimento (tabla §1), medida a 7 días y calculada sobre el alcance. Se calcula la tasa agregada por nivel (suma de guardados o envíos / suma de alcance) y la mediana de las tasas por pieza.
2. Un nivel gana si cumple las tres: (a) tiene la mejor tasa en al menos 4 de 6 emparejamientos (o la proporción equivalente si hay menos carruseles); (b) su tasa agregada es al menos 30 % mayor (relativa) que la del siguiente nivel; (c) la mediana va en la misma dirección que la agregada.
3. Si no se cumple, el resultado es «sin diferencia detectable» y se elige por criterio de marca (claridad), sin presentarlo como victoria.
4. Con alcances de 1 000 a 5 000 por pieza solo se detectan diferencias grandes (aprox. 2×). Una tasa sobre menos de unos 1 500 de alcance se marca como ruidosa (3 guardados de 50 no es 6 %).
5. Se reporta con y sin la pieza más atípica (viral o compartida por una cuenta grande). Si el resultado cambia de signo al quitarla, no se decide.
6. Seguidores y no seguidores se registran por separado; el desempate para «qué atrae descubrimiento» es la tasa sobre alcance de no seguidores, solo si ese dato está disponible en las 6 piezas.
7. Freno de calidad: «correcciones por pieza» debe ser cero. Si una variante genera una corrección o un comentario de imprecisión, se retira esa variante, pase lo que pase con la métrica.
8. Regresión a la media: nunca se cambia la línea editorial por la mejor pieza de una semana; solo por la regla de arriba, y se reconfirma en la siguiente ronda con otros carruseles antes de adoptar el gancho ganador como estándar.
9. Aviso de diseño: ver el mismo contenido tres veces en cuatro semanas afecta a quien ya lo vio (cansancio). Por eso se rota el orden y se anota la posición; si la 3.ª publicación rinde sistemáticamente peor sin importar el gancho, se trata como efecto de repetición y se corrigen las tasas por posición antes de comparar.

## 5. Lo que hay que revisar antes de publicar

- Avisos del validador (existentes, no nuevos): las cifras de `satelite-no-se-cae`, `leo-meo-geo`, `latencia-orbita-baja` y `mito-sin-gravedad` no tienen fecha de verificación (valores de libro). Los ganchos de E1-b y E3-c reutilizan cifras de esas láminas: 7.7 km/s, ~90 % de gravedad a 400 km (ya marcado en `cuidado`) y 240 ms (mínimo teórico de propagación en GEO).
- E6-c cita «146 pruebas» con la fecha 2026-07-30 y «beta» en el subtítulo, según la fuente (codeaerospace.com/plataformas); reconfirmar antes de publicar porque envejece.
- E6-b y E6-c mantienen la aclaración «telemetría simulada» (subtítulo de b; cierre y láminas de c).
- `cifras-con-fecha`: reconfirmar 149 lecciones / 16 cursos (ya en `cuidado`).
