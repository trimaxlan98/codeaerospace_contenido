# Calendario de las primeras 6 semanas (cadencia mínima: 2 carruseles + 1 reel por semana)

Decidido por el dueño el 2026-10-02: la cadencia de 2 carruseles y 1 reel por semana es el MÍNIMO.
Combina el plan de pruebas A/B de ganchos (`experimentos/plan_ab_ronda1.md`, pensado para 3 carruseles por semana; con 2
por semana se estira a 6 semanas) con la prueba de voz en los reels. Nada está publicado: la semana 1 empieza cuando el
dueño apruebe la primera pieza.

Franjas fijas (hora CDMX): carrusel A martes 20:00, carrusel B jueves 12:30, reel sábado 12:30. Misma franja para las
piezas de un mismo experimento solo cuando se compara hora; aquí se alterna como pide el plan.

## Carruseles (12 publicaciones = 4 experimentos de gancho × 3 versiones)

Cada tema se publica cada 2 semanas (≥ 7 días entre versiones) y con el orden rotado del plan.

| Semana | Martes 20:00 | Jueves 12:30 |
|---|---|---|
| 1 | `satelite-no-se-cae-c` (promesa) | `plataformas-sat-dt` (pregunta, A) |
| 2 | `latencia-orbita-baja-b` (pregunta) | `cifras-con-fecha-c` (promesa) |
| 3 | `satelite-no-se-cae` (pregunta, A) | `plataformas-sat-dt-b` (promesa) |
| 4 | `latencia-orbita-baja-c` (dato) | `cifras-con-fecha` (afirmación, A) |
| 5 | `satelite-no-se-cae-b` (dato) | `plataformas-sat-dt-c` (dato) |
| 6 | `latencia-orbita-baja` (afirmación, A) | `cifras-con-fecha-b` (pregunta) |

Se mide cada pieza a los 7 días exactos. Al cierre de la semana 6 hay 12 piezas (pregunta 4, dato 3, promesa 3, afirmación 2):
NO alcanza para concluir (el protocolo pide 5–6 por nivel). Las semanas 7–12 repiten el esquema con 4 carruseles nuevos
(candidatos: `leo-meo-geo`, `ventana-de-contacto`, `espectro-recurso-escaso`, `interferencia-ngso-geo`); recién ahí se aplica
la regla de decisión. Mientras tanto, los otros ~40 carruseles quedan en reserva para rellenar la parrilla sin mezclar
variables (cualquier carrusel NO incluido en un experimento se publica con su versión base).

## Reels (1 por semana) y la prueba de voz

| Semana | Sábado 12:30 | Para qué |
|---|---|---|
| 1 | `ReelOrbitEye` (sin voz) | Línea base de un reel en loop |
| 2 | `ReelDopplerReal` (datos reales, sin voz) | Primer reel con datos reales; ver NOTA de fecha abajo |
| 3 | `ReelATP` (sin voz) | Línea base 2 |
| 4 | `ReelModelo` (sin voz) | Pieza comercial (máx. 1 de cada 8 publicaciones al inicio) |
| 5 | `ReelOrbitEye_voz` (voz libre A) como **Trial Reel** | Voz vs sin voz: comparar con la semana 1 (mismo reel) |
| 6 | `ReelATP_vozB` (lazo de frase) como **Trial Reel** | Lazo de frase vs sin voz: comparar con la semana 3 |

Medir en reels: porcentaje visto, repeticiones y envíos por alcance (ver `informes/ronda1_contenido.md` §3). Los Trial Reels
se muestran primero a no seguidores. Con una muestra tan chica solo se detectan diferencias grandes; «sin diferencia
detectable» es un resultado válido.

## Antes de publicar (cada vez)

1. Leer el `_CUIDADO.txt` de la pieza y resolver cada ⚠️.
2. Voz sintética: Instagram puede pedir la etiqueta de contenido generado con IA para audio realista; revisar la política
   vigente antes de la semana 5. Para voz humana real, regrabar con `studio/content/voz/guiones/<Reel>.md`.
3. Texto alternativo: pegar el `_alt.txt` del carrusel (Instagram → configuración avanzada).
4. Anotar la pieza en `exports/estudio/experimentos/registro_publicaciones.csv` (fecha, hora, variable, alcance a 7 días…).

## NOTA sobre las piezas con datos reales

`doppler-real-iss` y `ReelDopplerReal` calculan el pase de la ISS del **sábado 3 de octubre de 2026, 09:06–09:12 hora de
CDMX** (elementos de CelesTrak con época 2026-10-02 00:19 UTC). Si se publican después de esa fecha, decir que es el
cálculo de ese pase (no «hoy»). Para anunciarlo ANTES, verificar la hora contra una fuente independiente (NASA Spot the
Station o Heavens-Above) y publicar el mismo día. Para piezas siguientes con datos reales: regenerar con elementos nuevos
(`python3 redes/carruseles/generar_desde_datos.py` tras actualizar la muestra con `python3 -m datos_orbitales`).
