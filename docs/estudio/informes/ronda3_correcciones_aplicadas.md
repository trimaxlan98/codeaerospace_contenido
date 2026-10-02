# Ronda 3: correcciones aplicadas

Origen: `exports/estudio/informes/ronda3_verificacion.md`. Specs en `redes/carruseles/specs/`. Todos los specs cambiados se re-renderizaron con `motor_carrusel.py --estricto` (sin fallos) y se revisaron las hojas de contacto clave (un-pase-1, un-pase-5, modelo-autofinancia, sdr-e-iq-en-simple, leo-meo-geo, mito-ia-pilotea, mito-quietos-y-basura).

Notas de la tabla: «Antes» muestra el texto sustituido (fragmento) o el valor completo; los índices de lámina son del JSON (0 = primera). Los `sello` nuevos aparecen como «(sin campo)». Ajustes propios además de los del informe: ver sección «Añadidos».

## Correcciones

| Sev. | ID | Spec | Campo | Antes | Después |
|---|---|---|---|---|---|
| ALTA | AUTO-3 | modelo-autofinancia | `laminas[5].items[2]` (láminas 0-indexadas) | Avanzamos proyecto a proyecto, sin rondas de inversión | Cada proyecto digital financia investigación aeroespacial real |
| ALTA | AUTO-3 | modelo-autofinancia | `laminas[0].subtitulo` (láminas 0-indexadas) | Un modelo que se autofinancia, proyecto a proyecto | Proyectos digitales que financian investigación, uno a uno |
| ALTA | AUTO-3 | modelo-autofinancia | `cuidado[1]` (láminas 0-indexadas) | «Sin fondos de gobierno ni rondas de inversión» viene de la presentación institucional (2026-09-30), no de /services; confirmar que sigue vigente. | La relación proyecto digital → investigación viene de /services y de la presentación institucional (2026-09-30); la presentación también menciona inversores ángel y fondeo institucional, por eso no se afirma «sin rondas de inversión». Confirmar que sigue vigente. |
| MEDIA | CF-1 | cifras-con-fecha | `laminas[3].der.t` (láminas 0-indexadas) | Se mantienen | Cambian más despacio |
| MEDIA | IA-1 | ia-acotada | `laminas[0].titulo` (láminas 0-indexadas) | La IA explica y redacta. No decide ni actúa. | Nuestros copilotos de IA explican y redactan. |
| MEDIA | IA-1 | ia-acotada | `laminas[5].frase` (láminas 0-indexadas) | La IA explica y redacta; no decide ni actúa. | El copiloto de IA explica y redacta; no decide ni actúa. |
| MEDIA | IA-2 | ia-acotada | `laminas[1].cuerpo` (láminas 0-indexadas) | el diseño es siempre el mismo: | el diseño es casi siempre el mismo (la excepción es PiStation, que usa el CLI local): |
| MEDIA | IA-2 | ia-acotada | `pie_texto` (láminas 0-indexadas) | Gemini 2.5 sobre Vertex AI, acotado | casi siempre Gemini 2.5 sobre Vertex AI (PiStation es la excepción), acotado |
| MEDIA | IA-1 | ia-acotada | `pie_texto` (láminas 0-indexadas) | Nuestro patrón de IA en una frase: explica y redacta; no decide ni actúa. | Nuestros copilotos de IA, en una frase: explican y redactan; no deciden ni actúan. |
| MEDIA | MC-1 | manimstudio-cursos | `laminas[6].cuerpo` (láminas 0-indexadas) | al 2026-09-18. | al 2026-09-18. CO.DE Academy está en beta. |
| MEDIA | MC-1 | manimstudio-cursos | `laminas[6].sello` (láminas 0-indexadas) | (sin sello) | beta |
| MEDIA | MC-1 | manimstudio-cursos | `laminas[7].texto` (láminas 0-indexadas) | Cursos en codeaerospace.com | Cursos de CO.DE Academy (plataforma en beta) |
| MEDIA | MC-2 | manimstudio-cursos | `pie_texto` (láminas 0-indexadas) | animaciones de CO.DE Academy: | animaciones de CO.DE Academy (plataforma en beta): |
| MEDIA | AUTO-5 | modelo-autofinancia | `laminas[4].unidad` (láminas 0-indexadas) | plataformas desplegadas | plataformas en el catálogo |
| MEDIA | AUTO-5 | modelo-autofinancia | `laminas[4].nota` (láminas 0-indexadas) | codeaerospace.com/plataformas: cifras verificadas el 30 de julio de 2026. | Fichas del catálogo de codeaerospace.com/plataformas al 2026-07-30; incluyen herramientas internas y plataformas en beta. |
| MEDIA | AUTO-5 | modelo-autofinancia | `laminas[4].titulo` (láminas 0-indexadas) | Sistemas en operación, no maquetas | Con código, pruebas y fecha, no maquetas |
| MEDIA | AUTO-5 | modelo-autofinancia | `laminas[3].pasos[3].d` (láminas 0-indexadas) | Sistemas en operación, con código y pruebas | Con código y pruebas, no maquetas |
| MEDIA | CP-3 | cifras-pruebas-y-decisiones | `laminas[5].der.t` (láminas 0-indexadas) | Se mantienen | Cambian más despacio |
| MEDIA | CP-1 | cifras-pruebas-y-decisiones | `laminas[6].items[1]` (láminas 0-indexadas) | Sus pruebas automatizadas | Sus pruebas (o la aclaración de que no las tiene) |
| MEDIA | CP-2 | cifras-pruebas-y-decisiones | `pie_texto` (láminas 0-indexadas) | cada ficha de nuestras plataformas lleva su fecha y dice qué no prueba | varias fichas de nuestras plataformas llevan su fecha y aclaran qué no prueban |
| MEDIA | KE-1 | basura-espacial-kessler | `laminas[0].subtitulo` (láminas 0-indexadas) | Un choque a 15 km/s no se queda en uno | Choques a más de 10 km/s: cada uno suma fragmentos |
| MEDIA | KE-2 | basura-espacial-kessler | `laminas[1].cuerpo` (láminas 0-indexadas) | En LEO todo viaja a ≈ 7.7 km/s. En un choque frontal la velocidad relativa se acerca a 15 km/s: hasta un fragmento diminuto trae energía de sobra para dañar un satélite. | A 400 km un satélite viaja a ≈ 7.7 km/s. En un choque frontal la velocidad relativa puede acercarse a 15 km/s (el choque de 2009 fue a ≈ 11.7 km/s): hasta un fragmento diminuto trae energía de sobra para dañar un satélite. |
| MEDIA | DO-1 | doppler-curva-en-s | `laminas[7].texto` (láminas 0-indexadas) | CO.DE Orbit Eye corrige el Doppler | Orbit Eye (obra derivada de ground-station, GPL-3.0) corrige el Doppler |
| MEDIA | LMG-1 | leo-meo-geo | `laminas[1].pie` (láminas 0-indexadas) | Esquema no a escala. En medio, MEO: los satélites GPS orbitan a ≈ 20 200 km con periodo de ≈ 12 h. | Esquema no a escala: LEO dibujado a 550 km (95 min). En medio, MEO: los satélites GPS orbitan a ≈ 20 200 km con periodo de ≈ 12 h. |
| MEDIA | FFT-1 | fft-y-cascada | `laminas[6].nota` (láminas 0-indexadas) | Test intacto de 731 observaciones; 0.806 en estaciones no vistas. Cifras verificadas el 2026-07-30 en codeaerospace.com/plataformas. | Test intacto de 731 observaciones (el pronóstico de calidad de la plataforma llega a 0.806 en estaciones no vistas). Cifras verificadas el 2026-07-30 en codeaerospace.com/plataformas. |
| MEDIA | LAT-1 | latencia-orbita-baja | `laminas[2].pie` (láminas 0-indexadas) | Tiempo mínimo de ida por un satélite en LEO, MEO y GEO. Las cifras de la ilustración son aproximadas. | La ilustración cuenta ida y vuelta completa (4·d/c): ≈ 7, 107 y 477 ms (MEO a 8 000 km). Luego: solo subir y bajar (2·d/c). |
| MEDIA | SDR-1 | sdr-e-iq-en-simple | `laminas[6].titulo` (láminas 0-indexadas) | Así lo usamos en Co.De | Un ejemplo: CO.DE Orbit Eye |
| MEDIA | SDR-1 | sdr-e-iq-en-simple | `laminas[6].cuerpo` (láminas 0-indexadas) | Orbit Eye opera receptores SDR con FFT, cascada y varios decodificadores. En esta demostración no hay receptor conectado: la recepción se muestra con [[grabaciones IQ]]. | Orbit Eye, obra derivada del proyecto ground-station (GPL-3.0), opera receptores SDR con FFT, cascada y varios decodificadores. Este despliegue no tiene receptor conectado: la recepción se muestra con [[grabaciones IQ]]. |
| MEDIA | SDR-1 | sdr-e-iq-en-simple | `laminas[6].sello` (láminas 0-indexadas) | (sin sello) | grabacion |
| MEDIA | GG-1 | glosario-gemelos-control | `laminas[4].cuerpo` (láminas 0-indexadas) | un diseño apunta a 0.1° de error | un diseño se propone un presupuesto de 0.1° de error |
| MEDIA | MI-1 | mito-ia-pilotea | `laminas[0].subtitulo` (láminas 0-indexadas) | Y por qué en Co.De la IA no decide | Y por qué en Co.De nuestros copilotos no deciden |
| MEDIA | MI-1 | mito-ia-pilotea | `laminas[1].der.items[1]` (láminas 0-indexadas) | La IA ayuda a explicar | Nuestros copilotos solo explican |
| MEDIA | MI-2 | mito-ia-pilotea | `laminas[5].titulo` (láminas 0-indexadas) | Un copiloto con límites | El patrón habitual de nuestros copilotos |
| MEDIA | MI-2 | mito-ia-pilotea | `laminas[5].items[0]` (láminas 0-indexadas) | Gemini 2.5 sobre Vertex AI | Casi siempre Gemini 2.5 sobre Vertex AI (PiStation usa el CLI local) |
| MEDIA | MI-1 | mito-ia-pilotea | `laminas[4].frase` (láminas 0-indexadas) | La IA explica y redacta; no decide ni actúa. | El copiloto de IA explica y redacta; no decide ni actúa. |
| MEDIA | AT-1 | plataformas-atp-dt | `laminas[1].cuerpo` (láminas 0-indexadas) | con un error de apenas 0.1° | con un presupuesto de error de 0.1° |
| MEDIA | AT-2 | plataformas-atp-dt | `laminas[5].sello` (láminas 0-indexadas) | (sin campo) | meta |
| MEDIA | NX-1 | plataformas-code-nexus | `laminas[3].kicker` (láminas 0-indexadas) | En el bus hoy | En el bus (al 2026-07-30) |
| MEDIA | NX-2 | plataformas-code-nexus | `laminas[2].cuerpo` (láminas 0-indexadas) | y si falla la entrega queda en una cola de reintento. | y si la entrega falla, el evento pasa a una cola **dead-letter**. |
| MEDIA | PI-1 | plataformas-pistation | `laminas[0].titulo` (láminas 0-indexadas) | Una consola de misión en una Raspberry Pi 5 | Una consola de misión para flotas de Raspberry Pi 5 |
| MEDIA | PI-1 | plataformas-pistation | `pie_texto` (láminas 0-indexadas) | ¿Una consola de misión en una Raspberry Pi 5? | ¿Una consola de misión para flotas de Raspberry Pi 5? |
| MEDIA | PI-2 | plataformas-pistation | `laminas[2].cuerpo` (láminas 0-indexadas) | Si se sale de ±3σ, es una anomalía: aviso antes de que falle. | Si se sale de ±3σ, se marca como anomalía. |
| MEDIA | SD-1 | plataformas-sat-dt | `laminas[1].cuerpo` (láminas 0-indexadas) | se comporta como el sistema real | modela el sistema real |
| MEDIA | SD-2 | plataformas-sat-dt | `laminas[2].cuerpo` (láminas 0-indexadas) | Verás los satélites donde realmente están, en un globo 3D. | Muestra posiciones calculadas con SGP4 a partir de TLE reales, en un globo 3D. |
| MEDIA | TR-1 | plataformas-triage | `laminas[5].cuerpo` (láminas 0-indexadas) | El pronóstico de calidad, que corre entero en tu navegador, llega a **0.806** en estaciones que no vio al entrenar. Es el dato honesto: fuera de casa, el modelo rinde menos. | El pronóstico de calidad, que corre entero en tu navegador, llega a **0.806** en estaciones que no vio al entrenar. Es otro modelo que el clasificador, y es el dato honesto: con estaciones nuevas, rinde menos. |
| MEDIA | TR-2 | plataformas-triage | `laminas[4].nota` (láminas 0-indexadas) | AUC: qué tan bien ordena los pases buenos por encima de los malos (1.0 = perfecto). Medido sobre un test intacto. | AUC: qué tan bien ordena los pases buenos por encima de los malos (1.0 = perfecto). Test intacto; cifra verificada el 2026-07-30 en codeaerospace.com/plataformas. |
| MEDIA | TR-1 | plataformas-triage | `pie_texto` (láminas 0-indexadas) | y 0.806 en estaciones que no vio al entrenar. | y su pronóstico de calidad llega a 0.806 en estaciones que no vio al entrenar. |
| MEDIA | UP1-1 | un-pase-1-orbit-eye | `pie_texto` (láminas 0-indexadas) | Guarda la serie | Orbit Eye es obra derivada del proyecto ground-station (GPL-3.0, Stratos Goudelis). Guarda la serie |
| MEDIA | SERIE | un-pase-1-orbit-eye | `laminas[0].subtitulo` (láminas 0-indexadas) | Cinco plataformas, un mismo pase. Parte 1: rastrearlo y escucharlo | Recorrido didáctico con un pase imaginario · Parte 1: rastrear y escuchar |
| MEDIA | SERIE | un-pase-1-orbit-eye | `laminas[6].texto` (láminas 0-indexadas) | Ya sabemos cuándo pasa y cómo se escucha. Falta lo difícil: saber si ese pase trae señal. Parte 2: CO.DE Triage. | Ya sabemos cuándo pasa y cómo se escucha. Falta saber si ese pase trae señal (Parte 2: Triage). Recorrido didáctico: un pase imaginario para explicar cinco plataformas; no es un flujo automático de un pase real. |
| MEDIA | SERIE | un-pase-1-orbit-eye | `pie_texto` (láminas 0-indexadas) | Arrancamos una serie de 5 partes con un mismo pase. | Arrancamos una serie didáctica de 5 partes con un pase imaginario (no es un flujo automático de un pase real). |
| MEDIA | UP1-2 | un-pase-1-orbit-eye | `laminas[3].sello` (láminas 0-indexadas) | (sin campo) | ilustracion |
| MEDIA | SERIE | un-pase-1-orbit-eye | `laminas[0].sello` (láminas 0-indexadas) | (sin campo) | ilustracion |
| MEDIA | UP2-1 | un-pase-2-triage | `laminas[4].der.t` (láminas 0-indexadas) | Estaciones no vistas | Pronóstico en estaciones no vistas |
| MEDIA | UP2-1 | un-pase-2-triage | `laminas[4].der.items` (láminas 0-indexadas) | ["AUC 0.806", "Más difícil de generalizar"] | ["AUC 0.806", "Es el pronóstico de calidad, no la CNN"] |
| MEDIA | UP2-1 | un-pase-2-triage | `laminas[4].titulo` (láminas 0-indexadas) | Dos números, dos situaciones | Dos números, dos modelos |
| MEDIA | UP2-2 | un-pase-2-triage | `laminas[0].titulo` (láminas 0-indexadas) | Escuchaste un pase. ¿Tenía señal? | Un pase deja una cascada. ¿Tenía señal? |
| MEDIA | UP2-1 | un-pase-2-triage | `pie_texto` (láminas 0-indexadas) | 0.806 en estaciones no vistas) | el pronóstico de calidad llega a 0.806 en estaciones no vistas) |
| MEDIA | UP2-2 | un-pase-2-triage | `pie_texto` (láminas 0-indexadas) | Escuchaste un pase. ¿Tenía señal? | Un pase deja una cascada. ¿Tenía señal? |
| MEDIA | SERIE | un-pase-2-triage | `pie_texto` (láminas 0-indexadas) | Guarda y sigue con la Parte 3. | Recorrido didáctico con un pase imaginario, no un flujo real. Guarda y sigue con la Parte 3. |
| MEDIA | SERIE | un-pase-3-code-nexus | `pie_texto` (láminas 0-indexadas) | Guarda y sigue con la Parte 4. | Recorrido didáctico: un pase imaginario para explicar cinco plataformas; no es un flujo automático de un pase real. Guarda y sigue con la Parte 4. |
| MEDIA | SERIE | un-pase-4-sat-dt | `pie_texto` (láminas 0-indexadas) | Guarda y sigue con la Parte 5. | Recorrido didáctico: un pase imaginario para explicar cinco plataformas; no es un flujo automático de un pase real. Guarda y sigue con la Parte 5. |
| MEDIA | UP5-1 | un-pase-5-atp-dt | `laminas[1].cuerpo` (láminas 0-indexadas) | con un error de apenas 0.1° | con un presupuesto de error de 0.1° |
| MEDIA | SERIE | un-pase-5-atp-dt | `laminas[5].cuerpo` (láminas 0-indexadas) | Rastrear y escuchar, clasificar, firmar y distribuir, ensayar la flota, apuntar la antena. Cada pieza resuelve una pregunta distinta del mismo pase. | Rastrear y escuchar, clasificar, firmar, ensayar la flota, apuntar la antena. Recorrido didáctico: un pase imaginario para explicar cinco plataformas; no es un flujo automático de un pase real. |
| MEDIA | SERIE | un-pase-5-atp-dt | `laminas[5].sello` (láminas 0-indexadas) | (sin campo) | ilustracion |
| BAJA | CF-2 | cifras-con-fecha | `laminas[5].items[2]` (láminas 0-indexadas) | Su alcance: qué mide y qué no | Su fecha, su origen y [[cómo se midió]] |
| BAJA | AUTO-6 | modelo-autofinancia | `pie_texto` (láminas 0-indexadas) | con quien crea que la ingeniería espacial solo se financia con subsidios | con quien se pregunte cómo se financia la investigación espacial |
| BAJA | BAN-1 | banco-que-rompe-la-red | `laminas[1].cuerpo` (láminas 0-indexadas) | sobre un Swarm de [[tres máquinas]] reales: satélite, | sobre un Swarm de [[tres máquinas]] reales, en nueve servicios. Entre los roles: satélite, |
| BAJA | KE-3 | basura-espacial-kessler | `laminas[4].nota` (láminas 0-indexadas) | Ocurrió el 10 de febrero de 2009, a unos 790 km de altitud. Hecho histórico documentado. | 10 de febrero de 2009, a unos 790 km de altitud, a ≈ 11.7 km/s de velocidad relativa. Hecho histórico documentado (NASA). |
| BAJA | LMG-2 | leo-meo-geo | `laminas[6].der.items[2]` (láminas 0-indexadas) | Con tres cubres casi todo | Con tres cubres casi todo el planeta, salvo los polos |
| BAJA | LMG-1 | leo-meo-geo | `laminas[1].sello` (láminas 0-indexadas) | (sin campo) | ilustracion |
| BAJA | SN-1 | satelite-no-se-cae | `laminas[5].der.items[0]` (láminas 0-indexadas) | ~90 % | ≈ 89 % |
| BAJA | SN-1 | satelite-no-se-cae | `variantes[0].portada.subtitulo` (láminas 0-indexadas) | cerca del 90 % | ≈ 89 % |
| BAJA | VC-1 | ventana-de-contacto | `laminas[7].texto` (láminas 0-indexadas) | CO.DE Orbit Eye rastrea con SGP4/Skyfield y predice pases AOS/LOS por umbral de elevación. | Orbit Eye (obra derivada de ground-station, GPL-3.0) rastrea con SGP4/Skyfield y predice pases AOS/LOS por umbral de elevación. |
| BAJA | FFT-2 | fft-y-cascada | `variantes[0].portada.imagen` (láminas 0-indexadas) | sticker:antenas_robots/EspectroFourier | sticker:antenas_robots/SDRAntenaANumero |
| BAJA | CE-1 | certificado-verificable | `laminas[4].der.items[0]` (láminas 0-indexadas) | Firmado criptográficamente | Firma HMAC-SHA256 |
| BAJA | CE-1 | certificado-verificable | `laminas[4].der.items[1]` (láminas 0-indexadas) | Se comprueba sin pedir permiso | Se comprueba en una URL pública |
| BAJA | CE-2 | certificado-verificable | `laminas[0].subtitulo` (láminas 0-indexadas) | La respuesta es una URL | La respuesta: una firma y una URL pública |
| BAJA | MO-1 | mecanica-orbital-en-el-navegador | `laminas[6].titulo` (láminas 0-indexadas) | Practicar es la mejor forma de entender | Practicar ayuda a entender |
| BAJA | RU-1 | ruta-ingenieria-espacial | `laminas[1].cuerpo` (láminas 0-indexadas) | Orbitas, | Órbitas, |
| BAJA | GE-1 | glosario-estacion-terrena | `laminas[0].titulo` (láminas 0-indexadas) | 6 siglas que oirás en una estación terrena | 6 términos que oirás en una estación terrena |
| BAJA | GE-1 | glosario-estacion-terrena | `laminas[7].titulo` (láminas 0-indexadas) | Seis siglas, un pase completo | Seis términos, un pase completo |
| BAJA | MQ-1 | mito-quietos-y-basura | `laminas[2].cuerpo` (láminas 0-indexadas) | (sin aclaración) | … + « El esquema dibuja LEO a 550 km.» |
| BAJA | MG-1 | mito-sin-gravedad | `laminas[2].cifra` (láminas 0-indexadas) | ~90 % | ≈ 89 % |
| BAJA | MG-1 | mito-sin-gravedad | `pie_texto` (láminas 0-indexadas) | cerca del 90 % | ≈ 89 % |
| BAJA | AT-3 | plataformas-atp-dt | `laminas[2].sello` (láminas 0-indexadas) | (sin campo) | ilustracion |
| BAJA | NX-3 | plataformas-code-nexus | `laminas[3].nota` (láminas 0-indexadas) | Cifra de codeaerospace.com/plataformas del 2026-07-30; envejece sola. 6 de 6 servicios registrados en línea. | Cifra de codeaerospace.com/plataformas del 2026-07-30; envejece sola. Es el volumen de un clúster de seis aplicaciones propias, no de una red de terceros. |
| BAJA | PI-3 | plataformas-pistation | `pie_texto` (láminas 0-indexadas) | telemetría en vivo | telemetría |
| BAJA | PI-3 | plataformas-pistation | `laminas[1].sello` (láminas 0-indexadas) | (sin campo) | ilustracion |
| BAJA | SD-3 | plataformas-sat-dt | `variantes[0].portada.titulo` (láminas 0-indexadas) | Ensaya fallas | Se pueden ensayar fallas |
| BAJA | TR-3 | plataformas-triage | `laminas[2].pasos[3].d` (láminas 0-indexadas) | La persona ve solo los pases con señal | La persona revisa los pases que el clasificador marca con señal |

## Añadidos propios (coherencia con lo corregido)

- AUTO-5: título de la lámina 5 y último paso de la lámina 4 de modelo-autofinancia («Sistemas en operación…») cambiados para no contradecir «en el catálogo / incluyen betas».
- IA-1 / MI-1: la frase «Nuestro patrón de IA…» del pie de ia-acotada y la cita de la lámina 5 de mito-ia-pilotea se alinearon con «copiloto» (regla 9).
- UP2-1: título de la comparación de un-pase-2 («Dos números, dos modelos») para no sugerir una sola situación.
- SERIE-UNPASE: el aviso de recorrido didáctico quedó VISIBLE en láminas: un-pase-1 (subtítulo de portada con sello ilustración + texto del cierre) y un-pase-5 (lámina 6 con sello ilustración); en 1, 2, 3 y 4 además en `pie_texto`.
- MQ-1: la lámina de texto no admite `pie`; la aclaración «El esquema dibuja LEO a 550 km» se añadió al cuerpo.
- Regla 8: LMG-1 (sello ilustración + pie), LAT-1 (pie del sticker), MQ-1 (aclaración) cumplen que el sticker no contradiga el texto vecino. Regla 9: IA-1, IA-2, MI-1, MI-2. Regla 2: Orbit Eye (obra derivada GPL-3.0 y sin receptor) en DO-1, SDR-1, VC-1, UP1-1; Triage 0.806 = pronóstico (FFT-1, TR-1, TR-2, UP2-1); ATP-DT 0.1° = presupuesto (AT-1, AT-2, UP5-1, GG-1).

## NO aplicado y por qué

- `prueba/orbit-eye.json` (ORB-1 a ORB-5, 2 ALTAS): excluido por instrucción; ya está marcado `no_publicar`.
- UP4-2 (BAJA): quitar la lámina QMIX de un-pase-4; no es trivial (cambia la estructura de 7 láminas y los números «Parte 4 de 5»). Se deja el texto, que cumple la regla 2 (piloto sin validar, sello beta).
- BAN-2 (BAJA): un solo ítem en la lista violaría el mínimo de 2 ítems del motor; no aplicado.
- CU-1 (BAJA, opcional): sin cambios.
- Regla 2 de `ESQUEMA.md` (nota del informe sobre la conflación 0.949/0.806): ya estaba corregida en el ESQUEMA; no se tocó (fuera de alcance).
- Specs sin problemas: animacion-cientifica-en-codigo, transferencia-hohmann, espectro-recurso-escaso, interferencia-ngso-geo, glosario-constelaciones (no tocados). cuatro-fases: solo CU-1.

## Observaciones

- Avisos del validador «cifra sin fecha de verificación» (doppler, leo-meo-geo, satelite-no-se-cae, latencia, mito-sin-gravedad, atp-dt lámina 6): son cifras de física estándar o de diseño, no de la página; no bloquean (--estricto pasa). No se alteraron.
- Los JSON se reescribieron con sangría de 2 espacios (el contenido no cambió fuera de lo listado).
- Pendiente humano: revisar los `cuidado` de ia-acotada, mito-ia-pilotea y modelo-autofinancia (se actualizó el de modelo-autofinancia; los otros siguen vigentes).
