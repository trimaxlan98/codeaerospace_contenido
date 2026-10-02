# Ronda 3: verificación adversarial de los carruseles (38 specs)

Alcance: los 38 JSON de `redes/carruseles/specs/*/*.json` (y sus variantes A/B), contra `redes/fuentes/*_2026-10-01.txt`, `animaciones/presentaciones/que_es_code.json` y las reglas de `ESQUEMA.md`.
Cálculos físicos rehechos con GM = 398 600 km³/s². Iridium 33–Cosmos 2251 contrastado en la web (10-feb-2009, 789 km, velocidad relativa 11.7 km/s: NASA/Wikipedia).

## Hallazgos globales

- Material prohibido: no hay nada de la tesis, ni nombres de clientes, ni la matriz de capacidad como dato en ningún spec. El nombre «PADA NTN Testbed» solo aparece en `fuentes` de `banco-que-rompe-la-red`, nunca en una lámina. La física está bien en casi todo: Hohmann (Δv 2.40 + 1.46 = 3.85 → 3.9 km/s; 5.3 h; 3.07 km/s), v = 7.67 km/s, 5 m cada 8 km, λ = 2.19 m, 0.2387 s, 3.67 ms, Doppler ≈ 3.2 kHz, (R/(R+h))² = 0.885.
- Fallos reales:
  1. `orbit-eye.json` omite en láminas el aviso de «sin receptor» y atribuye a México un software derivado.
  2. `modelo-autofinancia` afirma «sin rondas de inversión», y la presentación institucional dice lo contrario (busca inversores ángel y fondeo institucional).
  3. El 0.806 de Triage (que la fuente atribuye al **pronóstico** de calidad) se presenta como si fuera del clasificador.
  4. Las cifras de los stickers `ComparaLatencia` (7/107/477 ms) y `OrbitasLEOMEOGEO` (550 km, 95 min) chocan con el texto de las láminas vecinas.
  5. La serie «un pase» presenta como flujo real una cadena que es solo narrativa.
  6. «La IA no decide» se generaliza a todo Co.De, pero la propia fuente tiene QMIX piloto y un clasificador que emite veredictos.
- Nota: la propia ESQUEMA.md repite la conflación «0.949 … 0.806 en estaciones no vistas». Conviene corregir la regla 2 de ESQUEMA: «0.806 = pronóstico de calidad (Score Your Pass) en estaciones no vistas».

## Tabla resumen

| id | Veredicto | Problemas (A/M/B) |
|---|---|---|
| cifras-con-fecha | CORREGIR | 2 (0/1/1) |
| cuatro-fases | LISTO | 1 (0/0/1) |
| ia-acotada | CORREGIR | 2 (0/2/0) |
| manimstudio-cursos | CORREGIR | 2 (0/2/0) |
| modelo-autofinancia | CORREGIR | 3 (1/1/1) |
| animacion-cientifica-en-codigo | LISTO | 0 |
| banco-que-rompe-la-red | LISTO | 2 (0/0/2) |
| cifras-pruebas-y-decisiones | CORREGIR | 3 (0/3/0) |
| basura-espacial-kessler | CORREGIR | 3 (0/2/1) |
| doppler-curva-en-s | CORREGIR | 1 (0/1/0) |
| leo-meo-geo | CORREGIR | 2 (0/1/1) |
| satelite-no-se-cae | LISTO | 1 (0/0/1) |
| transferencia-hohmann | LISTO | 0 |
| ventana-de-contacto | LISTO | 1 (0/0/1) |
| espectro-recurso-escaso | LISTO | 0 |
| fft-y-cascada | CORREGIR | 2 (0/1/1) |
| interferencia-ngso-geo | LISTO | 0 |
| latencia-orbita-baja | CORREGIR | 1 (0/1/0) |
| sdr-e-iq-en-simple | CORREGIR | 1 (0/1/0) |
| certificado-verificable | LISTO | 2 (0/0/2) |
| mecanica-orbital-en-el-navegador | LISTO | 1 (0/0/1) |
| ruta-ingenieria-espacial | LISTO | 1 (0/0/1) |
| glosario-constelaciones | LISTO | 0 |
| glosario-estacion-terrena | LISTO | 1 (0/0/1) |
| glosario-gemelos-control | CORREGIR | 1 (0/1/0) |
| mito-ia-pilotea | CORREGIR | 2 (0/2/0) |
| mito-quietos-y-basura | LISTO | 1 (0/0/1) |
| mito-sin-gravedad | LISTO | 1 (0/0/1) |
| plataformas-atp-dt | CORREGIR | 3 (0/2/1) |
| plataformas-code-nexus | CORREGIR | 3 (0/2/1) |
| plataformas-pistation | CORREGIR | 3 (0/2/1) |
| plataformas-sat-dt | CORREGIR | 3 (0/2/1) |
| plataformas-triage | CORREGIR | 3 (0/2/1) |
| orbit-eye (prueba) | NO PUBLICAR | 5 (2/2/1) |
| un-pase-1-orbit-eye | CORREGIR | 3 (0/3/0) |
| un-pase-2-triage | CORREGIR | 3 (0/3/0) |
| un-pase-3-code-nexus | CORREGIR | 1 (0/1/0) |
| un-pase-4-sat-dt | CORREGIR | 2 (0/1/1) |
| un-pase-5-atp-dt | CORREGIR | 2 (0/2/0) |

Dos observaciones sobre la tabla:
- **Total.** Hay 3 problemas altos, 41 medios y 22 bajos. Los 3 altos son:
  - ORB-1 (aviso de «sin receptor» omitido).
  - ORB-2 (el «hecho en México» de un software derivado).
  - AUTO-3 (afirmación contradicha por la propia fuente).
- **Veredicto LISTO.** Los LISTO pueden salir tal cual (los bajos son opcionales).

---

## Problemas por carrusel

Formato: ID · lámina · cita · por qué · corrección · severidad.

### orbit-eye (`prueba/orbit-eye.json`): NO PUBLICAR (sustituir por un-pase-1)

- **ORB-1** · láminas 1, 4, 5 y `pie_texto` · «Así se escucha un satélite desde tierra» / «FFT y cascada en vivo» / «Escuchar: La radio corrige el Doppler» / pie «Así funciona una estación terrena definida por software.» · Ninguna lámina ni el pie dicen que **este despliegue no tiene receptor conectado** (la advertencia está solo en `cuidado`). Todo se lee como recepción real y en vivo. · Corrección: lámina 5 `pasos[2].d` → «Corrige el Doppler (aquí, con grabaciones IQ)»; lámina 4 item 1 → «FFT y [[cascada]] (en la demo, con IQ grabado)»; añadir `"sello":"grabacion"` a la lámina 4 o 5; pie → «Así funciona una estación terrena definida por software. CO.DE Orbit Eye es obra derivada de ground-station (GPL-3.0, Stratos Goudelis); este despliegue no tiene receptor de radio conectado: la recepción se demuestra con grabaciones IQ. Guárdalo y compártelo. #satélites #SDR #SGP4 #estaciónterrena #ingenieríaespacial» · **ALTA**
- **ORB-2** · lámina 8 · «Ingeniería espacial hecha en México» (+ «Conoce las 19 plataformas») · Orbit Eye es una obra derivada del proyecto de Stratos Goudelis (GPL-3.0). Atribuirle «hecha en México» es falso y omite la autoría (la fuente solo declara «sistema visual, asistente Orbit Eye AI, accesibilidad y adaptador»). · Corrección: `titulo` → «Código abierto, extendido por Co.De»; `texto` → «Obra derivada de ground-station (GPL-3.0). Más plataformas en codeaerospace.com» · **ALTA**
- **ORB-3** · lámina 3 · nota «El catálogo no lo compilamos nosotros…» (355 satélites) · Cifra sin fecha. · Corrección: nota → «Cifra de codeaerospace.com/plataformas, verificada el 2026-07-30; el catálogo cambia solo. No lo compilamos nosotros: se sincroniza de fuentes abiertas.» · MEDIA
- **ORB-4** · lámina 7 · cita «No son maquetas: son sistemas en operación.» justo después de capacidades sin receptor. · La ficha de Orbit Eye es «Interna / con cuenta» y sin receptor; la cita sin contexto sugiere recepción operativa. · Corrección: eliminar la lámina 7 (o sustituirla por la lámina «Aquí no hay antena conectada» de un-pase-1). · MEDIA
- **ORB-5** · pie · solo 2 hashtags, sin gancho ni llamada a guardar (regla 6 / formato de `pie_texto`). · Cubierto por la corrección ORB-1. · BAJA

### un-pase-1-orbit-eye

- **UP1-1** · `pie_texto` y lámina 2 · «CO.DE Orbit Eye predice el pase con SGP4…» · Falta «obra derivada de ground-station (GPL-3.0, Stratos Goudelis)»; el propio `cuidado` dice «menciónalo si se publica con descripción técnica», y el pie es técnico. · Pie → añadir «Orbit Eye es obra derivada del proyecto ground-station (GPL-3.0, Stratos Goudelis).» antes de «Guarda la serie». · MEDIA
- **UP1-2** · lámina 4 · sticker `DopplerEnS` (137 MHz, ±3 kHz, 21:00–01:00) sin sello. · Los valores del dibujo son ilustrativos y no se avisa en la lámina. · Añadir `"sello":"ilustracion"`. · MEDIA
- **UP1-3** · serie (ver SERIE-UNPASE). · MEDIA

### un-pase-2-triage

- **UP2-1** · lámina 5 y `pie_texto` · «Test intacto AUC 0.949 / Estaciones no vistas AUC 0.806» y «(AUC 0.949 … ; 0.806 en estaciones no vistas)» · La fuente dice «el **pronóstico** alcanza 0.806 en estaciones no vistas» (Score Your Pass, otro modelo). Aquí parece que la CNN cae a 0.806. · Lámina 5 `der.t` → «Pronóstico en estaciones no vistas»; `der.items` → ["AUC 0.806", "Es el pronóstico de calidad, no la CNN"]; pie → «…(AUC 0.949 de Triage en un test intacto de 731 observaciones; el pronóstico de calidad llega a 0.806 en estaciones no vistas)…» · MEDIA
- **UP2-2** · lámina 1 · «Escuchaste un pase. ¿Tenía señal?» · En la Parte 1 se dice que no hay receptor y que es una reproducción; «escuchaste» contradice eso. Además Triage ingiere observaciones de SatNOGS, no lo que reproduce Orbit Eye. · `titulo` → «Un pase deja una cascada. ¿Tenía señal?» · MEDIA
- **UP2-3** · serie (SERIE-UNPASE). · MEDIA

### un-pase-3-code-nexus

- **UP3-1** · serie (SERIE-UNPASE). Resto verificado (HMAC-SHA256, dead-letter, 6/6 con fecha). · MEDIA

### un-pase-4-sat-dt

- **UP4-1** · serie (SERIE-UNPASE). · MEDIA
- **UP4-2** · lámina 6 · «El control multiagente QMIX existe como piloto de 1.000 episodios, sin validar.» · Permitido por la regla 2 (aviso de piloto) y bien rotulado. Pero `plataformas-sat-dt` lo omite a propósito y esta pieza lo expone, y QMIX es el método de la tesis privada. Política inconsistente. · Preferible omitir la lámina (lo mismo que en plataformas-sat-dt); si se queda, no tocar el texto. · BAJA

### un-pase-5-atp-dt

- **UP5-1** · lámina 2 · «con un error de apenas 0.1°» · Presenta 0.1° como requisito universal. Es el presupuesto de diseño de este banco. · «con un presupuesto de error de 0.1° (el que usa este banco de pruebas)» · MEDIA
- **UP5-2** · serie (SERIE-UNPASE). · MEDIA

### SERIE-UNPASE (aplica a las 5 piezas)

«Cinco plataformas, un mismo pase» / «Cada pieza resuelve una pregunta distinta del mismo pase» / sticker `UnPaseCincoPlataformas`. Ninguna fuente describe un pase único que atraviese las cinco plataformas. Orbit Eye no recibe en vivo; Triage clasifica observaciones de SatNOGS; SAT-DT y ATP-DT son simuladores independientes. El `cuidado` lo admite («síntesis didáctica nuestra»), pero el público no lo ve. Corrección: en la lámina 1 de la Parte 1 y en la lámina 6 de la Parte 5 (campo `texto`), añadir «Recorrido didáctico: un pase imaginario para explicar cinco plataformas; no es un flujo automático de un pase real.» y poner `"sello":"ilustracion"` en esas dos láminas. Severidad MEDIA (estricta: alta si el recorrido se vende como demostración).

### cifras-con-fecha

- **CF-1** · lámina 4 · «Se mantienen: Pruebas en verde, Decisiones de arquitectura» · Contradice el título del carrusel («una cifra sin fecha no es un dato»): un conteo de pruebas cambia al añadir pruebas, y la propia ficha de Academy lleva 911 «al 2026-07-30». · `der.t` → «Cambian más despacio» · MEDIA
- **CF-2** · lámina 6 · «Su alcance: qué mide y qué no» · Regla editorial propia atribuida como «nuestra regla»; la fuente solo garantiza fecha y verificación por comandos (el `cuidado` ya lo admite). · «Su fecha, su origen y [[cómo se midió]]» · BAJA

### cuatro-fases

- **CU-1** · láminas 3, 5 · «Antes de escribir código definimos…» / «Si un supuesto no se sostiene, se descubre aquí.» · Matices añadidos por el redactor; son inferencias razonables y coinciden con la presentación institucional («Nada pasa a la siguiente fase sin haber cumplido la anterior»). · Opcional: quitar «Antes de escribir código». · BAJA

### ia-acotada

- **IA-1** · lámina 1 · «La IA explica y redacta. No decide ni actúa.» (título y cita lámina 6) · La fuente lo dice de los **copilotos**. Co.De también tiene un clasificador que emite veredictos (Triage) y control multiagente QMIX en piloto. Generalizar a «la IA» es engañoso. · `titulo` → «Nuestros copilotos de IA explican y redactan.»; lámina 6 `frase` → «El copiloto de IA explica y redacta; no decide ni actúa.» · MEDIA
- **IA-2** · lámina 2 y `pie_texto` · «el diseño es siempre el mismo: Gemini 2.5 sobre Vertex AI» · La fuente documenta una excepción (el copiloto de PiStation corre sobre CLI local). Hoy solo está en `cuidado`. · Lámina 2 cuerpo → «Donde hay copiloto en nuestras plataformas, el diseño es casi siempre el mismo (la excepción es PiStation, que usa el CLI local): [[Gemini 2.5]] sobre Vertex AI, con tres límites.»; pie: sustituir «Gemini 2.5 sobre Vertex AI, acotado…» por «Casi siempre Gemini 2.5 sobre Vertex AI (PiStation es la excepción), acotado…» · MEDIA

### manimstudio-cursos

- **MC-1** · láminas 7–8 y pie · «La plataforma publicaba 16 cursos al 2026-09-18» / «Cursos en codeaerospace.com» · Omite que CO.DE Academy está en **beta** («sin usuarios externos» según la leyenda de la página) y el dominio de la ficha es canfret.com, no codeaerospace.com. · Lámina 7 cuerpo: añadir «CO.DE Academy está en beta.» + `"sello":"beta"`; lámina 8 `texto` → «Cursos de CO.DE Academy (plataforma en beta)». · MEDIA
- **MC-2** · pie · «Cómo producimos las animaciones de CO.DE Academy» sin mención de beta. · Añadir «(plataforma en beta)». · MEDIA

### modelo-autofinancia

- **AUTO-3** · lámina 6 · «Avanzamos proyecto a proyecto, sin rondas de inversión» y portada «Un modelo que se autofinancia» · La diapositiva «¿Cómo colaborar con CO.DE?» de `que_es_code.json` dice: «Alianzas estratégicas, inversores ángel y fondeo institucional alineado con la misión 2027». «Sin rondas de inversión» contradice la propia fuente. · Lámina 6 item 3 → «Cada proyecto digital financia investigación aeroespacial real»; portada `subtitulo` → «Proyectos digitales que financian investigación, uno a uno» · **ALTA**
- **AUTO-5** · lámina 5 · «19 plataformas desplegadas · Sistemas en operación, no maquetas» · El conteo 19 incluye herramientas internas, betas e instalaciones de clientes (que no pueden mencionarse). «Desplegadas» sin matiz exagera. · nota → «Fichas del catálogo de codeaerospace.com/plataformas al 2026-07-30; incluyen herramientas internas y plataformas en beta.»; `unidad` → «plataformas en el catálogo» · MEDIA
- **AUTO-6** · pie · «…con quien crea que la ingeniería espacial solo se financia con subsidios.» · Tono de confrontación, sin fuente. · «…con quien se pregunte cómo se financia la investigación espacial.» · BAJA

### banco-que-rompe-la-red

(Los 5.5 s están bien: una observación, fecha, nota completa en lámina y pie.)
- **BAN-1** · lámina 2 · «Tres máquinas físicas, nueve servicios» + lista de 7 roles · Inconsistencia visible: se enumeran siete roles y se dice nueve (la fuente: «9 servicios en tres máquinas»; los otros dos no están nombrados). · cuerpo → «…sobre un Swarm de [[tres máquinas]] reales, en nueve servicios. Entre los roles: satélite, dos gateways, UE, gobernanza, generador de topología y colector.» · BAJA
- **BAN-2** · lámina 5 · «kill: se mata un proceso / stop: se detiene un servicio / override: se fuerza un estado» · La fuente solo nombra «kill, stop y override»; las definiciones son del redactor. · items → «Campañas declarativas en JSON: kill, stop y override» (un solo item) · BAJA

### cifras-pruebas-y-decisiones

- **CP-1** · lámina 7 · «Cada ficha lleva: … Sus pruebas automatizadas» · Falso: varias fichas del catálogo dicen «No tiene pruebas automatizadas» (Festiva, ADMS Bridge) y Gestión Empresa no lo documenta. · items[1] → «Sus pruebas (o la aclaración de que no las tiene)» · MEDIA
- **CP-2** · `pie_texto` · «cada ficha de nuestras plataformas lleva su fecha y dice qué no prueba» · Solo algunas fichas lo dicen. · «varias fichas de nuestras plataformas llevan su fecha y aclaran qué no prueban» · MEDIA
- **CP-3** · lámina 6 · igual que CF-1 («Se mantienen: Pruebas en verde»). · `der.t` → «Cambian más despacio» · MEDIA

### basura-espacial-kessler

- **KE-1** · lámina 1 · «Un choque a 15 km/s no se queda en uno» · El caso real (Iridium–Cosmos) fue a **11.7 km/s**; 15 km/s es el límite frontal ideal. Además no todo choque desencadena cascada: «no se queda en uno» promete más de lo que se sabe. · `subtitulo` → «Choques a más de 10 km/s: cada uno suma fragmentos» · MEDIA
- **KE-2** · lámina 2 · «En LEO todo viaja a ≈ 7.7 km/s» · «Todo» es falso: en LEO va de ≈ 7.3 a ≈ 7.8 km/s (a 790 km son 7.46). Y «15 km/s» es el máximo ideal. · cuerpo → «A 400 km un satélite viaja a ≈ 7.7 km/s. En un choque frontal la velocidad relativa puede acercarse a 15 km/s (el choque de 2009 fue a ≈ 11.7 km/s): hasta un fragmento diminuto trae energía de sobra para dañar un satélite.» · MEDIA
- **KE-3** · lámina 5 · nota «a unos 790 km de altitud» · Correcto (789 km, 10-feb-2009). Mejorable: añadir la velocidad relativa. · nota → «10 de febrero de 2009, a unos 790 km de altitud, a ≈ 11.7 km/s de velocidad relativa. Hecho histórico documentado (NASA).» · BAJA

### doppler-curva-en-s

- **DO-1** · lámina 8 y `pie_texto` · «CO.DE Orbit Eye corrige el Doppler en radio y rotor por Hamlib» · Falta «obra derivada de ground-station (GPL-3.0)»; la corrección Doppler por Hamlib es del proyecto base. · `texto` → «Orbit Eye (obra derivada de ground-station, GPL-3.0) corrige el Doppler en radio y rotor por Hamlib. Su despliegue no tiene receptor conectado: la recepción se demuestra con grabaciones IQ.» · MEDIA
- (Cifra 3 kHz: ≈ 3.2–3.3 kHz a 400 km, 3.0 kHz a 850 km. Correcta, y está marcada como aproximada.)

### leo-meo-geo

- **LMG-1** · lámina 2 · sticker `OrbitasLEOMEOGEO` muestra «LEO 550 km · 95 min» mientras el texto usa ISS 400 km · 92 min; el pie solo aclara MEO. · Corrección de `pie`: «Esquema no a escala: LEO dibujado a 550 km (95 min). En medio, MEO: los satélites GPS orbitan a ≈ 20 200 km con periodo de ≈ 12 h.» · MEDIA
- **LMG-2** · lámina 7 · «Con tres cubres casi todo» · No cubre los polos. · «Con tres cubres casi todo el planeta, salvo los polos» · BAJA

### satelite-no-se-cae

- **SN-1** · láminas 6 y variante b · «~90 %» / «cerca del 90 %» · (6371/6771)² = 0.885 → 88.5 %; la propia ficha dice ≈ 89 %. Aceptable, pero inconsistente (~90 vs 89). · «≈ 89 %» en lámina 6 y en el subtítulo de la variante b: «A 400 km todavía hay ≈ 89 % de la gravedad». · BAJA

### ventana-de-contacto

- **VC-1** · lámina 8 · «CO.DE Orbit Eye rastrea con SGP4/Skyfield…» · Sin mención de obra derivada (solo en `cuidado`). · «Orbit Eye (obra derivada de ground-station, GPL-3.0) rastrea con SGP4/Skyfield y predice pases AOS/LOS por umbral de elevación.» · BAJA

### fft-y-cascada

- **FFT-1** · lámina 7 · «0.949 AUC… Test intacto de 731 observaciones; 0.806 en estaciones no vistas.» · Atribuye 0.806 a Triage; es del pronóstico de calidad. · nota → «Test intacto de 731 observaciones (el pronóstico de calidad de la plataforma llega a 0.806 en estaciones no vistas). Cifras verificadas el 2026-07-30 en codeaerospace.com/plataformas.» · MEDIA
- **FFT-2** · portada (variante b) y lámina 2 repiten el mismo sticker `EspectroFourier`. · Variante b duplica imagen; usar otro (p. ej. `antenas_robots/SDRAntenaANumero`). · BAJA

### latencia-orbita-baja

- **LAT-1** · lámina 3 · sticker `ComparaLatencia` muestra 7 / 107 / 477 ms (= 4·d/c, ida y vuelta completa; MEO a 8 000 km) con pie «Tiempo mínimo de ida», mientras las láminas 4–5 y la variante c dicen 240 ms y 4 ms (2·d/c). El lector ve 477 ms junto a «240 ms». · `pie` → «La ilustración cuenta el viaje completo ida y vuelta (4·d/c): ≈ 7, 107 y 477 ms; MEO dibujado a 8 000 km. En las láminas siguientes: solo subir y bajar (2·d/c).» · MEDIA

### sdr-e-iq-en-simple

- **SDR-1** · lámina 7 · «Así lo usamos en Co.De» + «Orbit Eye opera receptores SDR…» · «Lo usamos» sobrestima: no hay receptor conectado; es obra derivada. · titulo → «Un ejemplo: CO.DE Orbit Eye»; cuerpo → «Orbit Eye, obra derivada del proyecto ground-station (GPL-3.0), opera receptores SDR con FFT, cascada y varios decodificadores. Este despliegue no tiene receptor conectado: la recepción se muestra con [[grabaciones IQ]].» + `"sello":"grabacion"` · MEDIA

### certificado-verificable

- **CE-1** · lámina 5 · «Firmado criptográficamente / Se comprueba sin pedir permiso» · HMAC es una firma con clave secreta; solo el servidor puede verificarla. «Sin pedir permiso» es del redactor. · «Firma HMAC-SHA256» / «Se comprueba en una URL pública» · BAJA
- **CE-2** · lámina 1 · «La respuesta es una URL» · Simplifica en exceso (la firma es la que garantiza). · «La respuesta: una firma y una URL pública» · BAJA

### mecanica-orbital-en-el-navegador

- **MO-1** · lámina 7 · «Practicar es la mejor forma de entender» · Superlativo (regla 5). · «Practicar ayuda a entender» · BAJA

### ruta-ingenieria-espacial

- **RU-1** · lámina 2 · «Orbitas, antenas…» · Falta la tilde: «Órbitas». · BAJA

### glosario-estacion-terrena

- **GE-1** · portada · «6 siglas…» · Doppler no es sigla y AOS/LOS son dos. · «6 términos que oirás en una estación terrena» · BAJA

### glosario-gemelos-control

- **GG-1** · lámina 5 · «Ejemplo: un diseño apunta a 0.1° de error.» · Se lee como logro; 0.1° es el presupuesto de diseño de ATP-DT. · «Ejemplo: un diseño se propone un presupuesto de 0.1° de error.» · MEDIA

### mito-ia-pilotea

- **MI-1** · portada y lámina 2 · «“La IA ya pilotea los satélites”» (presentado como mito) / «Y por qué en Co.De la IA no decide» · Declarar «mito» lo general es falso (hay autonomía/IA a bordo en el mundo) y «en Co.De la IA no decide» choca con el clasificador Triage y QMIX piloto. · `subtitulo` → «Y por qué en Co.De nuestros copilotos no deciden»; lámina 2 `der.items[1]` → «Nuestros copilotos solo explican» · MEDIA
- **MI-2** · lámina 6 · «Un copiloto con límites: Gemini 2.5 sobre Vertex AI…» sin excepción. · Añadir al último item: «(salvo PiStation, que usa el CLI local)» o cambiar el título a «El patrón habitual de nuestros copilotos». · MEDIA

### mito-quietos-y-basura

- **MQ-1** · lámina 3 · sticker `OrbitasLEOMEOGEO` (550 km / 95 min) con texto «400 km … ~92 min». · Añadir `"pie"`/nota de sticker como en LMG-1. · BAJA

### mito-sin-gravedad

- **MG-1** · lámina 3 · «~90 %» · Ver SN-1: 88.5 %, preferible «≈ 89 %». · BAJA

### plataformas-atp-dt

- **AT-1** · lámina 2 · «con un error de apenas 0.1°» · Ver UP5-1. → «con un presupuesto de error de 0.1°» · MEDIA
- **AT-2** · lámina 6 · «La meta del diseño: 0.1°» sin sello. · Añadir `"sello":"meta"`. · MEDIA
- **AT-3** · lámina 3 · sticker `GemeloDigitalATP` (muestra «Error 0.3°»). · Añadir `"sello":"ilustracion"`. · BAJA

### plataformas-code-nexus

- **NX-1** · lámina 4 · kicker «En el bus hoy» · «Hoy» con cifra del 2026-07-30. · kicker → «En el bus (al 2026-07-30)» · MEDIA
- **NX-2** · lámina 3 · «si falla la entrega queda en una cola de reintento» · La fuente dice «dead-letter». Reintento es otra cosa. · «si la entrega falla, el evento pasa a una cola **dead-letter**» · MEDIA
- **NX-3** · lámina 4 · nota sin el matiz de la fuente. · Añadir «Es el volumen de un clúster de seis aplicaciones propias, no de una red de terceros.» · BAJA

### plataformas-pistation

- **PI-1** · portada y pie · «Una consola de misión en una Raspberry Pi 5» · Falso: el agente corre en cada Pi; la consola es una app de escritorio que habla con la Pi por LAN. Fuente: «consola de misión **para** una flota de Raspberry Pi 5». · `titulo` → «Una consola de misión para flotas de Raspberry Pi 5»; pie → «¿Una consola de misión para flotas de Raspberry Pi 5?…» · MEDIA
- **PI-2** · lámina 3 · «es una anomalía: aviso antes de que falle» · La detección de anomalías no predice fallos; «antes de que falle» es una promesa sin fuente. · «Si se sale de ±3σ, se marca como anomalía.» · MEDIA
- **PI-3** · lámina 2 · sticker `TelemetriaEnVivo` sin sello (el nombre dice «en vivo», el modo por defecto es simulador). · Añadir `"sello":"ilustracion"`; pie: «telemetría en vivo» → «telemetría» · BAJA

### plataformas-sat-dt

- **SD-1** · lámina 2 · «una réplica en software que se comporta como el sistema real» · La telemetría es simulada por un modelo determinista. · «una réplica en software que modela el sistema real» · MEDIA
- **SD-2** · lámina 3 · «Verás los satélites donde realmente están» · Son posiciones calculadas con SGP4 desde TLE (error de km) y la consola es con cuenta/beta. · «Muestra posiciones calculadas con SGP4 a partir de TLE reales, en un globo 3D.» · MEDIA
- **SD-3** · variantes b y c · «Ensaya fallas…» invita a usarlo; la plataforma es beta, con cuenta. · Cambiar a «Se pueden ensayar fallas…». · BAJA

### plataformas-triage

- **TR-1** · lámina 6 y `pie_texto` · «Es el dato honesto: fuera de casa, el modelo rinde menos» / «0.806 en estaciones que no vio al entrenar» · Mezcla el pronóstico (0.806) con el clasificador. Hay incoherencia con el kicker de la lámina 5 («Prueba con datos que no vio»). · Lámina 6 cuerpo → «El pronóstico de calidad, que corre entero en tu navegador, llega a **0.806** en estaciones que no vio al entrenar. Es otro modelo que el clasificador, y es el dato honesto: con estaciones nuevas, rinde menos.»; pie → «…y su pronóstico de calidad llega a 0.806 en estaciones que no vio al entrenar.» · MEDIA
- **TR-2** · lámina 5 · nota «Medido sobre un test intacto.» sin fecha. · «…Cifra verificada el 2026-07-30 en codeaerospace.com/plataformas.» · MEDIA
- **TR-3** · lámina 3 · «La persona ve solo los pases con señal» · El clasificador (AUC 0.949) no es perfecto y descarta casos dudosos. · «La persona revisa los pases que el clasificador marca con señal» · BAJA

---

## Correcciones ALTAS y MEDIAS en formato aplicable

Rutas relativas a `redes/carruseles/specs/`. «lam[n]» = `laminas[n-1]`.

### ALTAS

1. `prueba/orbit-eye.json` · `pie_texto` → «Así funciona una estación terrena definida por software. CO.DE Orbit Eye es obra derivada de ground-station (GPL-3.0, Stratos Goudelis); este despliegue no tiene receptor de radio conectado: la recepción se demuestra con grabaciones IQ. Guárdalo y compártelo. #satélites #SDR #SGP4 #estaciónterrena #ingenieríaespacial». Además `laminas[4].pasos[2].d`: «La radio corrige el Doppler» → «Corrige el Doppler (aquí, con grabaciones IQ)»; `laminas[3].items[0]`: «FFT y [[cascada]] en vivo» → «FFT y [[cascada]] (en la demo, con IQ grabado)»; añadir `"sello":"grabacion"` a `laminas[4]`.
2. `prueba/orbit-eye.json` · `laminas[7].titulo`: «Ingeniería espacial hecha en México» → «Código abierto, extendido por Co.De»; `laminas[7].texto`: «Conoce las 19 plataformas en codeaerospace.com» → «Obra derivada de ground-station (GPL-3.0). Más plataformas en codeaerospace.com». Recomendación: no publicar este spec y usar `un-pase-1-orbit-eye`.
3. `como-trabajamos/modelo-autofinancia.json` · `laminas[5].items[2]`: «Avanzamos proyecto a proyecto, sin rondas de inversión» → «Cada proyecto digital financia investigación aeroespacial real»; `laminas[0].subtitulo`: «Un modelo que se autofinancia, proyecto a proyecto» → «Proyectos digitales que financian investigación, uno a uno»; `cuidado[1]`: borrar la frase «Sin fondos de gobierno ni rondas de inversión…».

### MEDIAS

4. `como-trabajamos/cifras-con-fecha.json` · `laminas[3].der.t`: «Se mantienen» → «Cambian más despacio».
5. `detras-de-camaras/cifras-pruebas-y-decisiones.json` · `laminas[5].der.t`: «Se mantienen» → «Cambian más despacio»; `laminas[6].items[1]`: «Sus pruebas automatizadas» → «Sus pruebas (o la aclaración de que no las tiene)»; `pie_texto`: «cada ficha de nuestras plataformas lleva su fecha y dice qué no prueba» → «varias fichas de nuestras plataformas llevan su fecha y aclaran qué no prueban».
6. `como-trabajamos/ia-acotada.json` · `laminas[0].titulo`: «La IA explica y redacta. No decide ni actúa.» → «Nuestros copilotos de IA explican y redactan.»; `laminas[5].frase`: «La IA explica y redacta; no decide ni actúa.» → «El copiloto de IA explica y redacta; no decide ni actúa.»; `laminas[1].cuerpo`: «…el diseño es siempre el mismo:» → «…el diseño es casi siempre el mismo (la excepción es PiStation, que usa el CLI local):»; `pie_texto`: «Gemini 2.5 sobre Vertex AI, acotado a los datos de la organización» → «casi siempre Gemini 2.5 sobre Vertex AI (PiStation es la excepción), acotado a los datos de la organización».
7. `glosario-y-mitos/mito-ia-pilotea.json` · `laminas[0].subtitulo`: «Y por qué en Co.De la IA no decide» → «Y por qué en Co.De nuestros copilotos no deciden»; `laminas[1].der.items[1]`: «La IA ayuda a explicar» → «Nuestros copilotos solo explican»; `laminas[5].titulo`: «Un copiloto con límites» → «El patrón habitual de nuestros copilotos»; `laminas[5].items[1]`: «Gemini 2.5 sobre Vertex AI» → «Casi siempre Gemini 2.5 sobre Vertex AI (PiStation usa el CLI local)».
8. `como-trabajamos/manimstudio-cursos.json` · `laminas[6].cuerpo`: añadir al final «CO.DE Academy está en beta.» y `"sello":"beta"`; `laminas[7].texto`: «Cursos en codeaerospace.com» → «Cursos de CO.DE Academy (plataforma en beta)»; `pie_texto`: «Cómo producimos las animaciones de CO.DE Academy:» → «Cómo producimos las animaciones de CO.DE Academy (plataforma en beta):».
9. `como-trabajamos/modelo-autofinancia.json` · `laminas[4].unidad`: «plataformas desplegadas» → «plataformas en el catálogo»; `laminas[4].nota`: → «Fichas del catálogo de codeaerospace.com/plataformas al 2026-07-30; incluyen herramientas internas y plataformas en beta.»
10. `divulgacion-orbital/basura-espacial-kessler.json` · `laminas[0].subtitulo`: «Un choque a 15 km/s no se queda en uno» → «Choques a más de 10 km/s: cada uno suma fragmentos»; `laminas[1].cuerpo`: «En LEO todo viaja a ≈ 7.7 km/s. En un choque frontal la velocidad relativa se acerca a 15 km/s: hasta un fragmento diminuto trae energía de sobra para dañar un satélite.» → «A 400 km un satélite viaja a ≈ 7.7 km/s. En un choque frontal la velocidad relativa puede acercarse a 15 km/s (el choque de 2009 fue a ≈ 11.7 km/s): hasta un fragmento diminuto trae energía de sobra para dañar un satélite.»
11. `divulgacion-orbital/doppler-curva-en-s.json` · `laminas[7].texto`: «CO.DE Orbit Eye corrige el Doppler en radio y rotor por Hamlib. Su despliegue no tiene receptor conectado: la recepción se demuestra con grabaciones IQ.» → «Orbit Eye (obra derivada de ground-station, GPL-3.0) corrige el Doppler en radio y rotor por Hamlib. Su despliegue no tiene receptor conectado: la recepción se demuestra con grabaciones IQ.»
12. `divulgacion-orbital/leo-meo-geo.json` · `laminas[1].pie`: → «Esquema no a escala: LEO dibujado a 550 km (95 min). En medio, MEO: los satélites GPS orbitan a ≈ 20 200 km con periodo de ≈ 12 h.»
13. `espectro-y-senales/fft-y-cascada.json` · `laminas[6].nota`: → «Test intacto de 731 observaciones (el pronóstico de calidad de la plataforma llega a 0.806 en estaciones no vistas). Cifras verificadas el 2026-07-30 en codeaerospace.com/plataformas.»
14. `espectro-y-senales/latencia-orbita-baja.json` · `laminas[2].pie`: → «La ilustración cuenta el viaje completo ida y vuelta (4·d/c): ≈ 7, 107 y 477 ms; MEO dibujado a 8 000 km. En las láminas siguientes: solo subir y bajar (2·d/c).»
15. `espectro-y-senales/sdr-e-iq-en-simple.json` · `laminas[6].titulo`: «Así lo usamos en Co.De» → «Un ejemplo: CO.DE Orbit Eye»; `laminas[6].cuerpo`: → «Orbit Eye, obra derivada del proyecto ground-station (GPL-3.0), opera receptores SDR con FFT, cascada y varios decodificadores. Este despliegue no tiene receptor conectado: la recepción se muestra con [[grabaciones IQ]].»; añadir `"sello":"grabacion"`.
16. `glosario-y-mitos/glosario-gemelos-control.json` · `laminas[4].cuerpo`: «**Ejemplo:** un diseño apunta a 0.1° de error.» → «**Ejemplo:** un diseño se propone un presupuesto de 0.1° de error.»
17. `plataformas/plataformas-atp-dt.json` · `laminas[1].cuerpo`: «con un error de apenas 0.1°» → «con un presupuesto de error de 0.1°»; `laminas[5]`: añadir `"sello":"meta"`.
18. `plataformas/plataformas-code-nexus.json` · `laminas[3].kicker`: «En el bus hoy» → «En el bus (al 2026-07-30)»; `laminas[2].cuerpo`: «y si falla la entrega queda en una cola de reintento.» → «y si la entrega falla, el evento pasa a una cola **dead-letter**.»
19. `plataformas/plataformas-pistation.json` · `laminas[0].titulo`: «Una consola de misión en una Raspberry Pi 5» → «Una consola de misión para flotas de Raspberry Pi 5»; `pie_texto`: «¿Una consola de misión en una Raspberry Pi 5?» → «¿Una consola de misión para flotas de Raspberry Pi 5?»; `laminas[2].cuerpo`: «Si se sale de ±3σ, es una anomalía: aviso antes de que falle.» → «Si se sale de ±3σ, se marca como anomalía.»
20. `plataformas/plataformas-sat-dt.json` · `laminas[1].cuerpo`: «se comporta como el sistema real» → «modela el sistema real»; `laminas[2].cuerpo`: «Verás los satélites donde realmente están, en un globo 3D.» → «Muestra posiciones calculadas con SGP4 a partir de TLE reales, en un globo 3D.»
21. `plataformas/plataformas-triage.json` · `laminas[5].cuerpo`: → «El pronóstico de calidad, que corre entero en tu navegador, llega a **0.806** en estaciones que no vio al entrenar. Es otro modelo que el clasificador, y es el dato honesto: con estaciones nuevas, rinde menos.»; `laminas[4].nota`: → «AUC: qué tan bien ordena los pases buenos por encima de los malos (1.0 = perfecto). Test intacto; cifra verificada el 2026-07-30 en codeaerospace.com/plataformas.»; `pie_texto`: «y 0.806 en estaciones que no vio al entrenar.» → «y su pronóstico de calidad llega a 0.806 en estaciones que no vio al entrenar.»
22. `un-pase/un-pase-1-orbit-eye.json` · `pie_texto`: añadir antes de «Guarda la serie»: «Orbit Eye es obra derivada del proyecto ground-station (GPL-3.0, Stratos Goudelis).»; `laminas[3]`: añadir `"sello":"ilustracion"`.
23. `un-pase/un-pase-2-triage.json` · `laminas[4].der.t`: «Estaciones no vistas» → «Pronóstico en estaciones no vistas»; `laminas[4].der.items`: → ["AUC 0.806", "Es el pronóstico de calidad, no la CNN"]; `laminas[0].titulo`: «Escuchaste un pase. ¿Tenía señal?» → «Un pase deja una cascada. ¿Tenía señal?»; `pie_texto`: «(AUC 0.949 en un test intacto de 731 observaciones; 0.806 en estaciones no vistas)» → «(AUC 0.949 en un test intacto de 731 observaciones; el pronóstico de calidad llega a 0.806 en estaciones no vistas)».
24. `un-pase/un-pase-5-atp-dt.json` · `laminas[1].cuerpo`: «con un error de apenas 0.1°» → «con un presupuesto de error de 0.1°».
25. SERIE-UNPASE (los 5 archivos de `un-pase/`) · `un-pase-1` `laminas[0]` y `un-pase-5` `laminas[5].cuerpo`: añadir «Recorrido didáctico: un pase imaginario para explicar cinco plataformas; no es un flujo automático de un pase real.» y `"sello":"ilustracion"`. En `un-pase-3` y `un-pase-4` añadir la misma frase al final de `pie_texto`.

Sin cambios necesarios (0 problemas): animacion-cientifica-en-codigo, transferencia-hohmann, espectro-recurso-escaso, interferencia-ngso-geo, glosario-constelaciones.
