# Curso 25 — Protocolos de Internet (familia de lecciones)

> **CÓMO REANUDAR ESTE CURSO** — basta decir *"continuamos con el curso de
> protocolos de internet"*. Todo el estado vive aquí:
>
> 1. Worktree `~/Documentos/github/codeaerospace_contenido-algebra`, rama
>    `curso/protocolos-internet` (creada desde `origin/main` 34d5890).
> 2. Mirar el **Tablero de estado** (más abajo): dice lección por lección qué
>    está escrito, validado, subido, renderizado en `qh`, narrado y muxeado.
> 3. Mirar **Lotes de producción**: el curso se entrega por lotes de 6
>    lecciones; cada lote se publica entero (PR → prod → narración → mux)
>    antes de empezar el siguiente. Se puede parar limpio entre lotes.
> 4. El pipeline por lote está en la sección **Receta de lote**. Nada de lo
>    que falta depende de contexto que solo esté en la conversación.

- **Formato**: familia de lecciones, como Álgebra lineal (22), Cálculo
  vectorial (23) y Comunicaciones digitales (24). Un proyecto de ManimStudio
  = una **lección** de 4 clips; cada clip = una idea. **8 módulos × 3
  lecciones = 24 proyectos, 96 clips.** Es el curso más extenso de la
  colección: el dueño pidió explícitamente "tema por tema", y los protocolos
  de Internet son muchos temas de verdad, no uno solo estirado.
- **Título de la familia**: `Protocolos de Internet`.
- **Ángulo editorial**: **la red que nadie manda**. No hay una autoridad que
  entregue los mensajes: hay reglas que millones de máquinas deciden cumplir.
  El hilo es un mensaje que se trocea, se rotula, se pierde, se retransmite,
  se acomoda y llega — y al final se intenta llevar esa misma idea a un sitio
  donde no funciona: el espacio profundo. El curso empieza en un cable de
  cobre y termina en Marte a 22 minutos luz.
- **Público**: divulgación técnica. Asume la idea de bit (curso 21), de
  símbolo sobre un canal ruidoso (curso 24) y de clave pública (curso 19).
  Las cabeceras se muestran byte a byte, pero lo que se explica es qué
  **decide** cada campo.
- **No pisa** los cursos publicados — este es la **CAPA DE PAQUETES**:
  - Comunicaciones digitales (24) llevó los bits de una punta a otra de UN
    enlace. Aquí el enlace ya funciona y el problema nuevo es que hay
    **muchos** enlaces y ningún jefe.
  - Cerrar el enlace (13) y Electromagnetismo (16) están por debajo: aquí no
    se vuelve a calcular ni un dB.
  - Criptografía (19) dio RSA/Diffie-Hellman; aquí TLS los **usa** (el
    apretón, la cadena de certificados) sin re-explicar la matemática.
  - Sistemas distribuidos (18) hizo relojes, quórum y hash consistente; aquí
    el tema es el transporte, no el consenso — CDN y anycast se tocan por su
    lado de red (latencia medida), no por su lado de replicación.
  - Metrología óptica (20) hizo el enlace láser entre satélites; en 8.1 esa
    malla aparece como **topología que se rutea**, con el mismo Dijkstra del
    módulo 3.
- **La marca sonora es de serie**: el mux usa el intro/cierre con SFX
  (validado en los cursos 23 y 24, picos −6 dB). Es posproducción: nada que
  hacer en los clips.

```
familia            ManimStudio
-----------------  ----------------------------------------
módulo   (8)   →   —  (agrupación editorial, no existe en la DB)
lección  (24)  →   proyecto  "Protocolos de Internet · N.M <título>"
idea     (96)  →   clip      "MODULO 0K" en el HUD (K = número de clip)
```

Slugs `protocolos-internet-N-M-<tema>`. Clips de 28–45 s (tope duro), pies
≥ 5 s legibles, el pie cambia ANTES de la animación que ilustra. Un solo
cierre a pantalla limpia por lección (clip 4).

## Principio visual no negociable

1. **El paquete es un objeto en pantalla**, no una metáfora: una cápsula
   ámbar con sus campos rotulados, que se mueve por enlaces, espera en colas,
   se descarta y se retransmite. Si algo "viaja", se ve viajar.
2. **La cabecera se lee**. Cuando un campo decide algo (TTL, puerto, prefijo,
   número de secuencia), ese campo se ilumina y su valor cambia en pantalla
   con la cifra medida. Nada de "el router mira la cabecera": se ve cuál.
3. **Los algoritmos se ejecutan de verdad**. Dijkstra, Bellman-Ford, el
   conteo al infinito, el checksum de IP, el CRC de Ethernet, el CIDR, el
   AIMD de TCP, el estimador de RTT de Jacobson, la resolución DNS, la
   selección de ruta BGP: todo corre en Python/numpy con semilla fija en la
   librería y **lo que se ve en pantalla es su salida**. Cero números
   inventados a mano.
4. **La pérdida y la espera son visibles y contadas**: paquetes en rojo que
   desaparecen, colas que crecen, reintentos numerados, milisegundos que se
   suman en un contador. El costo siempre está a la vista.
5. **Escala honesta**: cuando algo se exagera (un cable de 3 metros que son
   3000 km, una cola de 8 paquetes que son 8000), se declara en el pie.
6. **El tiempo es un eje**. Los diagramas de escalera (handshake, traceroute,
   TLS, DNS) tienen tiempo hacia abajo y RTT acumulado rotulado en cian.
7. Un solo cierre a pantalla limpia por lección (dos líneas, la segunda en
   cian), como en las familias anteriores.

## Mapa de las 24 lecciones

| Lección | Proyecto | Clips |
|---|---|---|
| 1.1 | Trocear el mensaje: conmutación de paquetes | circuito vs paquetes, multiplexación estadística, la cola, store-and-forward |
| 1.2 | El sobre dentro del sobre: capas y encapsulación | las cuatro capas, encapsular, el sobrecosto medido, desencapsular |
| 1.3 | El vecindario: Ethernet, MAC y ARP | la trama y su CRC, colisión y backoff, el switch aprende, ARP |
| 2.1 | IP: la dirección y el datagrama | la cabecera IPv4, el mejor esfuerzo, TTL, fragmentar |
| 2.2 | El prefijo manda: subredes, máscaras y CIDR | máscara y bits, CIDR agrega, tabla de ruteo, prefijo más largo |
| 2.3 | IPv6: el espacio que no se acaba | 2^32 se acabó, 128 bits, la dirección que se autoconfigura, convivir |
| 3.1 | Vector distancia: aprender por rumores | tablas por rumor, Bellman-Ford converge, el enlace cae, conteo al infinito |
| 3.2 | Estado del enlace: el mapa completo | inundar el mapa, Dijkstra paso a paso, el árbol, converger rápido |
| 3.3 | BGP: la política entre países | el mapa de los AS, camino de vectores, la política decide, el secuestro |
| 4.1 | Dos contratos: UDP y TCP | puertos y demultiplexado, UDP desnudo, TCP promete, cuál elegir |
| 4.2 | El apretón y la ventana | los tres mensajes, secuencia y ACK, ventana deslizante, retransmitir a tiempo |
| 4.3 | Congestión: la cortesía que sostiene la red | el colapso, arranque lento, la sierra AIMD, CUBIC y BBR |
| 5.1 | DNS: el directorio del mundo | el árbol de nombres, la resolución paso a paso, la caché y el TTL, la raíz |
| 5.2 | DHCP y NAT: casa prestada, puerta compartida | DORA, una IP para todos, la tabla de traducción, lo que NAT rompió |
| 5.3 | Ver la red: ICMP, ping y traceroute | ICMP, ping mide, traceroute con TTL, el MTU escondido |
| 6.1 | HTTP: pedir y responder | la petición, códigos de estado, una conexión por objeto, el cuello de botella |
| 6.2 | TLS: el candado de la web | el apretón, la clave compartida, el certificado y su cadena, 1.3 en un viaje |
| 6.3 | HTTP/2 y QUIC: el fin de la fila india | multiplexar, el bloqueo de cabeza de línea, QUIC sobre UDP, 0-RTT |
| 7.1 | Acercar el contenido: CDN y anycast | el viaje largo, la caché al borde, anycast, la latencia medida |
| 7.2 | Colas, latencia y bufferbloat | Little, el búfer grande que empeora, AQM/CoDel, prioridad |
| 7.3 | Tiempo real: voz, video y jitter | RTP y el reloj, jitter y el búfer, ABR escoge calidad, en vivo |
| 8.1 | Internet en órbita: GEO, LEO y la malla láser | GEO y sus 240 ms, TCP sufre, LEO y el salto de satélite, rutear la malla |
| 8.2 | DTN: la red que tolera la desconexión | el enlace que no está, el bundle y la custodia, plan de contactos, entrega |
| 8.3 | Internet interplanetario: CCSDS y Marte | 22 minutos luz, la pila del espacio, un archivo a Marte, cierre de familia |

## Paleta de la familia (por ROL)

Sobre la paleta de `code_brand`/`algebra_lineal`; **el color dice el papel**,
coherente con los cursos vecinos:

| Alias | Color | Papel |
|---|---|---|
| `C_PAQUETE` | ámbar | el paquete, el datagrama, la trama: el dato que viaja |
| `C_CIFRA` | cian | TODA cifra calculada (regla de la familia) |
| `C_RED` | azul | nodos, enlaces, topología, el medio físico |
| `C_PERDIDA` | rojo | pérdida, error, congestión, descarte, ataque |
| `C_OK` | verde | entregado, confirmado, ACK, lo que sí funcionó |
| `C_CAPA` | violeta | capas, cabeceras, jerarquía, nombres |
| `C_CLAVE` | fucsia | seguridad: claves, certificados, lo cifrado |
| `C_COLA` | naranja | colas, búferes, tiempo de espera, ancho de banda |
| mobiliario | `C_EJE` gris | ejes, rejillas, cajas |

## Librería `manim_extensions/protocolos.py` (contrato)

Importa el sustrato de `algebra_lineal.py` (plano, grafica, vector, fmt,
paleta) como las familias 23 y 24. Reutiliza sin duplicar:
`distribuido.py` (haversine y pisos de RTT), `cripto.py` (hash y RSA chico
para la cadena de certificados), `comunicaciones.py` (`pase_leo` para el
módulo 8). Python/numpy puro y **determinista** (azar solo con
`default_rng(semilla)` fija): mismo script → mismo render.

**Piezas de dibujo** (todas con gemelas `con_*` para Transform entre
estructuras idénticas — regla heredada):

    Paquete(campos, ...)        cápsula con campos rotulados; .campo(nombre)
                                para iluminar uno; .con_valores(...)
    Cabecera(spec, valores)     tabla de bits/bytes (IPv4, TCP, Ethernet)
    Nodo(tipo)                  host / switch / router / satélite / servidor
    Enlace(a, b, capacidad)     con .paquete_en(t) para animar tránsito
    Topologia(grafo)            la red dibujada; .resaltar_camino(camino)
    Cola(cap)                   búfer visible; .ocupacion(n); .descarta()
    Escalera(actores)           diagrama de tiempo (handshake, DNS, TLS)
    Pila(capas)                 la torre de capas; .encapsular()/.abrir()
    Arbol(raiz)                 jerarquía DNS / cadena de certificados
    Tabla(filas)                tabla de ruteo, NAT, MAC, ARP
    Reloj(ms)                   contador de milisegundos en cian
    Sierra(traza)               cwnd vs tiempo (AIMD/CUBIC)

**Números** (validados en el contenedor ANTES de escribir clips):

    troceado(n_bytes, mtu)              paquetes, relleno, sobrecosto %
    conmutacion(modo, saltos, ...)      latencia de circuito vs paquetes
    mux_estadistico(flujos, cap, sem)   ganancia medida vs reserva fija
    cola_mm1(lmbda, mu, t, semilla)     ocupación, espera, descartes contados
    little(lmbda, W)                    L = λ·W verificado sobre la simulación
    encapsular(datos, capas)            bytes por capa, sobrecosto medido
    crc32_trama(bytes)                  CRC real; bit volteado → detectado
    csma_cd(n, semilla)                 colisiones contadas, backoff medido
    switch_aprende(eventos)             tabla MAC, inundaciones → unicast
    checksum_ip(cabecera)               complemento a uno de 16 bits, real
    cabecera_ipv4(**campos)             bytes reales + checksum calculado
    fragmentar(paquete, mtu)            fragmentos con offset y flag MF
    cidr(prefijo)                       red, rango, hosts, máscara en bits
    prefijo_mas_largo(tabla, ip)        la ruta elegida y por qué
    agregar_rutas(prefijos)             cuántas filas ahorra la agregación
    ipv6_comprimir(dir) / expandir      la regla del `::`, real
    eui64(mac)                          la dirección SLAAC derivada
    bellman_ford(grafo, origen)         tablas ronda a ronda
    conteo_al_infinito(grafo, corte)    la secuencia patológica real
    dijkstra(grafo, origen)             orden de fijación, distancias, árbol
    inundacion(grafo, origen)           rondas y mensajes contados
    bgp_mejor_ruta(rutas)               local-pref → AS-path → decisión
    secuestro_bgp(as_grafo, pref, atac) ASes envenenados, contados
    demux(paquete, tabla_sockets)       la 4-tupla que decide el socket
    handshake_tcp()                     eventos con ISN y ACK reales
    ventana(w, perdidas, semilla)       bytes en vuelo, throughput medido
    rtt_jacobson(muestras)              SRTT, RTTVAR y RTO paso a paso
    bdp(mbps, rtt_ms)                   producto ancho de banda × retardo
    aimd(t, perdidas) / cubic(...)      traza de cwnd, media medida
    arranque_lento(ssthresh)            la exponencial hasta el umbral
    bufferbloat(cola_pkts, mbps)        latencia bajo carga, medida
    codel(traza)                        latencia y descartes con AQM
    resolver_dns(nombre, cache)         pasos, RTT acumulado, quién responde
    cache_dns(consultas, ttl, semilla)  tasa de acierto medida
    dhcp_dora()                         los cuatro mensajes con sus campos
    nat_traducir(sesiones)              tabla puerto↔puerto; choques evitados
    traceroute(camino)                  TTL a TTL: quién contesta y en cuánto
    pmtud(camino)                       el MTU mínimo hallado (y el agujero)
    ping(distancia_km, saltos, carga)   propagación + cola, medido
    http_transferencia(objetos, modo)   serial / 6 conexiones / H2 / H3
    hol_bloqueo(perdida, flujos, sem)   flujos parados: TCP vs QUIC, contados
    tls_viajes(version, reanudado)      RTT contados (1.2=2, 1.3=1, 0-RTT=0)
    dh_pequeno(p, g, a, b)              secreto compartido idéntico, real
    cadena_certificados()               firma verificada con `cripto.py`
    anycast(sitios, usuarios)           PoP más cercano (haversine) + latencia
    cdn(peticiones, catalogo, semilla)  aciertos de caché y alivio al origen
    jitter(llegadas)                    jitter medido; búfer y cortes contados
    abr(traza_ancho, escalones)         decisiones de calidad y atascos
    rtt_orbital(h_km)                   LEO 550 ≈ 4 ms ida; GEO ≈ 119 ms ida
    tcp_en_orbita(rtt, ventana)         techo por ventana/RTT; ganancia del PEP
    malla_laser(constelacion)           ruteo por ISL con el MISMO dijkstra
    retardo_marte(ua)                   minutos luz según la distancia
    ventanas_contacto(plan)             cuándo hay enlace y cuándo no
    dtn_custodia(camino, ventanas)      bundles retenidos, entregados, tiempo
    pila_ccsds() vs pila_tcpip()        comparación campo a campo

Regla de piezas mutantes: TODO lo que cambia tiene gemela `con_*` y se anima
con Transform entre estructuras IDÉNTICAS (trampa heredada de 22/23/24).

## Lotes de producción

El curso se entrega en **4 lotes de 6 lecciones (2 módulos cada uno)**. Cada
lote se publica ENTERO antes de empezar el siguiente: así se puede parar en
cualquier frontera de lote sin dejar nada a medias, y el dueño ya tiene 6
lecciones en producción aunque el resto no se haga nunca.

| Lote | Módulos | Lecciones | Librería que aporta | Estado |
|---|---|---|---|---|
| 1 | 1 y 2 | 1.1–2.3 | núcleo: Paquete/Nodo/Enlace/Cola/Pila/Cabecera + IP/CIDR | **PUBLICADO** (PR #47; 24 qh, narrado y muxeado) |
| 2 | 3 y 4 | 3.1–4.3 | Topologia, grafos, Dijkstra/BF/BGP, Escalera, Sierra, TCP | **PUBLICADO** (PR #48; 24 qh, narrado y muxeado) |
| 3 | 5 y 6 | 5.1–6.3 | Arbol, Tabla, DNS/NAT/traceroute, TLS/HTTP/QUIC | **en curso** (librería lista y validada; 6 agentes escribiendo) |
| 4 | 7 y 8 | 7.1–8.3 | anycast/CDN, colas AQM, ABR, órbita, DTN, CCSDS | pendiente |

## Receta de lote (la misma en los cuatro)

1. **Librería del lote**: añadir a `protocolos.py` solo lo que el lote usa y
   validarlo en el contenedor (script `valida_vis_pi.py` en el scratchpad:
   imprime cifras y guarda PNGs con PIL) ANTES de escribir un solo clip.
2. **Molde**: la primera lección del lote la escribo yo entera (en el lote 1
   es 1.1, y es el molde de TODA la familia).
3. **Esqueletos**: crear los `curso.json` + stubs `class ClipN(Scene): wait(1)`
   de las 6 lecciones — `render_local.py` aborta si falta cualquier clip
   declarado, y sin stubs no se puede paralelizar.
4. **Subagentes**: una lección por agente (Sonnet las mecánicas, Opus las
   delicadas), contrato en el scratchpad con rutas, reglas duras, validación
   `render_local.py <dir> --clip N --frames 8` y revisión de los 8 frames UNO
   A UNO. Máximo 1 render simultáneo por agente. Los agentes NO tocan la
   librería ni git. Informe final `LECCIÓN N.M APROBADA`.
5. **Revisión mía** de los frames de las 6 lecciones + `pytest -q` del Studio.
6. **PR del lote** (`feat(contenido): protocolos de internet — lote N`) y
   merge con `gh pr merge`.
7. **Producción**: en el VPS `git pull` + `subir_curso.py` ×6; `qh` LOCAL con
   3 procesos en paralelo; copiar a `render_jobs/qh/<slug>/`; `scp` al
   staging (en background: ~100 KB/s de subida) + `adoptar_renders.py`.
8. **Narración**: `guiones.py` **SERIAL** (nunca en paralelo: 429 del TTS),
   detached con `setsid nohup ... < /dev/null &`; es idempotente.
9. **Mux local** con intro/cierre de marca; picos > −0.5 dB → re-mux a
   −1.5 dB. Salidas a `exports/protocolos-internet-N-M-*/curso_narrado.mp4`.
10. Actualizar el **Tablero de estado** de este archivo y la memoria
    `familia-protocolos-internet` antes de cerrar el lote.

## Tablero de estado

Leyenda: `—` no empezado · `~` en curso · `✔` hecho.

| Lección | plan | librería | clips | ql ✔ frames | PR | subida | qh | narrada | mux |
|---|---|---|---|---|---|---|---|---|---|
| 1.1 | ✔ | ✔ | ✔ molde | ✔ 30/33/30/31 s | PR #47 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 1.2 | ✔ | ✔ | ✔ | ✔ 30/30/31/32 s | PR #47 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 1.3 | ✔ | ✔ | ✔ | ✔ 29/32/34/35 s | PR #47 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 2.1 | ✔ | ✔ | ✔ | ✔ 32/35/31/34 s | PR #47 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 2.2 | ✔ | ✔ | ✔ | ✔ 29/30/30/34 s | PR #47 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 2.3 | ✔ | ✔ | ✔ | ✔ 30/28/30/33 s | PR #47 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 3.1 | ✔ | ✔ | ✔ | ✔ 32/35/36/41 s | PR #48 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 3.2 | ✔ | ✔ | ✔ | ✔ 31/30/31/29 s | PR #48 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 3.3 | ✔ | ✔ | ✔ | ✔ 32/35/35/40 s | PR #48 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 4.1 | ✔ | ✔ | ✔ | ✔ 30/29/29/35 s | PR #48 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 4.2 | ✔ | ✔ | ✔ | ✔ 30/30/30/33 s | PR #48 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 4.3 | ✔ | ✔ | ✔ | ✔ 31/30/31/37 s | PR #48 (main) | ✔ | ✔ adoptado | ✔ | ✔ exports/ |
| 5.1 | ✔ | ✔ | ✔ | ✔ 29/33/30/30 s | — | — | — | — | — |
| 5.2 | ✔ | ✔ | ~ agentes | — | — | — | — | — | — |
| 5.3 | ✔ | ✔ | ~ agentes | — | — | — | — | — | — |
| 6.1 | ✔ | ✔ | ~ agentes | — | — | — | — | — | — |
| 6.2 | ✔ | ✔ | ~ agentes | — | — | — | — | — | — |
| 6.3 | ✔ | ✔ | ~ agentes | — | — | — | — | — | — |
| 7.1 | ✔ | — | — | — | — | — | — | — | — |
| 7.2 | ✔ | — | — | — | — | — | — | — | — |
| 7.3 | ✔ | — | — | — | — | — | — | — | — |
| 8.1 | ✔ | — | — | — | — | — | — | — | — |
| 8.2 | ✔ | — | — | — | — | — | — | — | — |
| 8.3 | ✔ | — | — | — | — | — | — | — | — |

## Módulo 1 — La red de redes

### 1.1 Trocear el mensaje: conmutación de paquetes  (slug `protocolos-internet-1-1-conmutacion`)
Antes de cualquier protocolo hay una decisión: no reservar un camino, sino
trocear. **Molde de la familia.**
1. **La línea reservada** — una llamada telefónica: un circuito se tiende
   extremo a extremo y queda ocupado aunque nadie hable. Dos usuarios más
   piden línea y **no hay**: bloqueo contado. Pie: el circuito garantiza,
   pero desperdicia lo que no usas.
2. **Trocear y rotular** — el mismo mensaje se parte con `troceado` en N
   `Paquete`s ámbar, cada uno con su rótulo de destino; salen por caminos
   distintos y llegan desordenados. Sobrecosto MEDIDO (cabecera/carga útil).
   Pie: cada trozo lleva su propia dirección; nadie le guarda el sitio.
3. **Compartir sin reservar** — `mux_estadistico`: tres flujos a ráfagas
   sobre un enlace; con reserva fija se desperdicia X %, con multiplexación
   estadística caben los tres y la ganancia MEDIDA aparece en cian. El precio
   aparece a la vez: la `Cola` que crece cuando coinciden las ráfagas.
4. **El precio: la espera** — `cola_mm1` corriendo: ocupación, espera media
   y descartes CONTADOS; un paquete rojo se cae del búfer lleno. Cierre:
   "Internet no te reserva nada. / Te deja competir, y casi siempre alcanza."

### 1.2 El sobre dentro del sobre: capas y encapsulación  (slug `protocolos-internet-1-2-capas`)
Por qué el mensaje viaja dentro de cuatro sobres y quién abre cada uno.
1. **Cuatro capas, cuatro trabajos** — la `Pila` (aplicación, transporte,
   red, enlace) con una frase por capa y el ejemplo de quién hace qué. Pie:
   cada capa solo habla con su igual del otro lado.
2. **Encapsular** — el dato baja y cada capa le pega su cabecera: HTTP →
   TCP → IP → Ethernet, con los bytes REALES de `encapsular` sumándose en el
   contador; el sobrecosto total MEDIDO para 100 B de carga vs 1400 B.
3. **En el camino nadie abre de más** — el paquete cruza un switch (lee solo
   la capa 2) y un router (abre hasta la 3 y **para**); las capas superiores
   se muestran selladas. Pie: el router no sabe qué pediste, y no le importa.
4. **Desencapsular** — en el destino los sobres se abren en orden inverso
   hasta el dato original, byte por byte igual al de partida (comparación en
   pantalla). Cierre: "Nadie entiende la red entera. / Cada capa entiende su
   propio sobre."

### 1.3 El vecindario: Ethernet, MAC y ARP  (slug `protocolos-internet-1-3-ethernet`)
El salto más corto: cómo se habla con quien está en el mismo cable.
1. **La trama y su sello** — `trama_ethernet`: preámbulo, MAC destino, MAC
   origen, tipo, carga y **FCS**. Se voltea un bit y el `crc32_trama`
   recalculado NO coincide: la trama se descarta en rojo. Cifras medidas.
2. **Hablar todos a la vez** — `csma_cd`: escuchar antes de hablar, la
   colisión en rojo, el backoff exponencial con sus reintentos y esperas
   CONTADOS. Pie: el cable compartido se reparte a codazos educados.
3. **El switch aprende** — `switch_aprende`: la primera trama se **inunda**
   por todos los puertos; el switch anota el origen; la respuesta ya sale por
   un solo puerto. Inundaciones vs unicast CONTADAS en la tabla MAC.
4. **ARP: ¿quién tiene esta IP?** — la pregunta a todos y la respuesta de
   uno; la caché ARP se llena y el segundo envío ya no pregunta. Cierre:
   "En tu cable no hay direcciones de Internet. / Hay vecinos que responden."

## Módulo 2 — Direcciones y caminos

### 2.1 IP: la dirección y el datagrama  (slug `protocolos-internet-2-1-ip`)
La capa que hace que todas las redes parezcan una.
1. **La cabecera IPv4** — `cabecera_ipv4` dibujada como `Cabecera` de 20
   bytes con los campos rotulados; se destacan los cuatro que deciden algo:
   origen, destino, TTL y protocolo. El checksum se CALCULA en pantalla.
2. **El mejor esfuerzo** — el datagrama cruza cinco redes distintas (cobre,
   fibra, radio, satélite) y a nadie le promete nada: se muestran los tres
   fracasos legales (perder, duplicar, desordenar), cada uno con su ejemplo
   visible. Pie: IP no promete entregar; promete intentarlo.
3. **TTL: el seguro contra los bucles** — un enrutamiento circular; el TTL
   baja 64 → 0 y el paquete muere; ICMP avisa al origen (adelanto de 5.3).
   Saltos CONTADOS hasta la muerte.
4. **Fragmentar** — `fragmentar`: 4000 B por un enlace de MTU 1500 salen
   como 3 fragmentos con offsets y bandera MF reales; si se pierde uno, se
   pierde el datagrama entero. Cierre: "IP es un acuerdo mínimo. / Por eso
   cupo todo el mundo dentro."

### 2.2 El prefijo manda: subredes, máscaras y CIDR  (slug `protocolos-internet-2-2-cidr`)
La dirección no es un número: son dos, pegadas.
1. **La raya móvil** — 32 bits con una raya que separa red de host; al mover
   la raya, `cidr` recalcula en vivo red, rango, broadcast y número de hosts.
   /24 → 254 hosts, /26 → 62, MEDIDOS.
2. **CIDR: agrupar para no ahogarse** — cuatro /24 contiguos se plegan en un
   /22; `agregar_rutas` cuenta las filas ahorradas. La tabla global cabe
   porque los prefijos se agregan.
3. **La tabla de ruteo** — una `Tabla` real de 5 filas con próximos saltos;
   un paquete llega y se ve el barrido de las filas que **coinciden**.
4. **El prefijo más largo gana** — `prefijo_mas_largo`: dos filas coinciden y
   la más específica manda; se cambia el destino un bit y la decisión cambia
   de salida en pantalla. Cierre: "Un router no conoce el mundo. / Conoce el
   trozo de mundo que le toca."

### 2.3 IPv6: el espacio que no se acaba  (slug `protocolos-internet-2-3-ipv6`)
Por qué hubo que cambiar el número más importante de la red.
1. **2^32 se acabó** — 4294 millones de direcciones frente a la población
   conectada; la barra se llena y las asignaciones se agotan por año
   (cronología real). Pie: la dirección era de 32 bits porque nadie imaginó
   esto.
2. **128 bits** — la comparación honesta: 2^128 con `fmt` en notación
   científica; la escala se declara con una analogía medida, no vaga. La
   dirección se escribe en hex y `ipv6_comprimir` aplica la regla del `::`.
3. **La dirección que se pone sola** — SLAAC: el router anuncia el prefijo,
   la máquina deriva el resto con `eui64` de su MAC y se autoconfigura sin
   servidor. Los bits que vienen de la MAC se iluminan.
4. **Convivir** — la cabecera IPv6 (40 B fijos, sin checksum ni fragmentación
   en tránsito) al lado de la IPv4: campos que se fueron, campos que
   quedaron. Doble pila y túnel, con el porcentaje real de adopción. Cierre:
   "La red nueva ya está aquí. / Lleva veinte años mudándose."

## Módulo 3 — Encontrar el camino

### 3.1 Vector distancia: aprender por rumores  (slug `protocolos-internet-3-1-vector-distancia`)
La primera manera de enrutar: creerle al vecino.
1. **Nadie ve el mapa** — la `Topologia` de 6 nodos con sus costos; cada
   router solo conoce a sus vecinos y su tabla arranca casi vacía.
2. **El rumor converge** — `bellman_ford` ronda a ronda: las tablas se
   rellenan en pantalla, cada celda con la distancia MEDIDA; converge en K
   rondas (K contado) y el camino óptimo se ilumina.
3. **Se cae un enlace** — el enlace clave se corta en rojo; las tablas
   empiezan a corregirse... por rumores de rumores.
4. **Conteo al infinito** — `conteo_al_infinito`: la secuencia patológica
   REAL de costos (2, 3, 4, 5...) subiendo ronda a ronda mientras el destino
   ya no existe; el horizonte dividido lo frena. Cierre: "Si solo repites lo
   que te dicen, / tardas mucho en enterarte de una mala noticia."

### 3.2 Estado del enlace: el mapa completo  (slug `protocolos-internet-3-2-dijkstra`)
La segunda manera: que todos tengan el mismo mapa.
1. **Inundar el mapa** — `inundacion`: cada router anuncia SUS enlaces y el
   anuncio se propaga; rondas y mensajes CONTADOS hasta que los seis tienen
   la misma base de datos idéntica (comparación en pantalla).
2. **Dijkstra paso a paso** — el algoritmo REAL: el conjunto de fijados
   crece, las distancias tentativas bajan, cada nodo se fija en el orden que
   devuelve `dijkstra`. Cada paso rotulado con su cifra.
3. **El árbol de caminos** — el árbol de costo mínimo resaltado sobre la
   topología: desde ese router, a cada destino, un camino y su costo medido.
   Se cambia un costo de enlace y el árbol se re-dibuja distinto.
4. **Converger rápido** — la misma caída de enlace de 3.1: aquí se inunda el
   cambio y todos recalculan; rondas comparadas 1 vs 3.1 con las dos cifras
   juntas. Cierre: "Un mapa compartido cuesta más de mantener. / Y se
   equivoca mucho menos."

### 3.3 BGP: la política entre países  (slug `protocolos-internet-3-3-bgp`)
Dentro de una red manda la distancia; entre redes manda el interés.
1. **El mapa de los AS** — Internet como ~75 000 sistemas autónomos: la
   topología de AS con proveedores, clientes y pares; el tráfico no cruza
   por donde es corto, sino por donde hay contrato.
2. **Camino de vectores** — un anuncio de prefijo viaja y cada AS **se
   añade** al camino; el AS-path crece a la vista y el bucle se detecta
   solo (un AS ve su propio número y descarta).
3. **La política decide** — `bgp_mejor_ruta` con tres rutas al mismo
   prefijo: local-pref primero, luego longitud del AS-path; gana la que
   conviene, no la más corta. Se cambia el local-pref y la elección cambia.
4. **El secuestro** — `secuestro_bgp`: un AS anuncia un prefijo más
   específico que no es suyo; los ASes envenenados se cuentan y se tiñen de
   rojo por la topología. RPKI como el freno. Cierre: "La red que nadie manda
   se sostiene en la palabra. / Y a veces alguien miente."

## Módulo 4 — La entrega confiable

### 4.1 Dos contratos: UDP y TCP  (slug `protocolos-internet-4-1-udp-tcp`)
IP entrega paquetes a máquinas; falta entregarlos a programas.
1. **Puertos: la extensión telefónica** — llegan tres paquetes a la misma IP
   y `demux` los reparte a tres sockets por la 4-tupla; el campo puerto se
   ilumina en cada uno.
2. **UDP desnudo** — 8 bytes de cabecera y nada más: sin apretón, sin
   reintentos, sin orden. Tres datagramas: uno se pierde y **nadie se entera**.
   Para qué sirve eso (DNS, voz, juegos), con su cifra de sobrecosto.
3. **TCP promete** — 20 bytes de cabecera y una máquina de estados: entrega
   fiable, ordenada y sin duplicados. La misma pérdida de arriba, pero aquí
   el hueco se detecta y se rellena.
4. **Cuál elegir** — tabla comparada con cifras medidas (sobrecosto, viajes
   antes del primer byte, comportamiento ante pérdida) y tres casos reales.
   Cierre: "No hay un protocolo mejor. / Hay una promesa que quieres o no."

### 4.2 El apretón y la ventana  (slug `protocolos-internet-4-2-ventana`)
Cómo se construye una promesa sobre un medio que no promete nada.
1. **Los tres mensajes** — `handshake_tcp` en `Escalera`: SYN, SYN-ACK, ACK
   con ISN reales; el RTT acumulado en cian y el estado de cada extremo
   rotulado. Un viaje completo antes del primer byte útil.
2. **Secuencia y ACK** — los bytes se numeran; llegan desordenados y el
   receptor los ordena; un ACK acumulado confirma hasta dónde. Se pierde uno
   y aparecen los ACK duplicados CONTADOS.
3. **La ventana deslizante** — `ventana`: mandar de uno en uno da un
   throughput ridículo; con ventana W el enlace se llena. `bdp` en pantalla:
   para llenar 100 Mb/s con 40 ms de RTT hacen falta 500 kB en vuelo — cifra
   MEDIDA, y la ventana se dimensiona por ahí.
4. **Retransmitir a tiempo** — `rtt_jacobson`: SRTT y RTTVAR sobre muestras
   reales, el RTO calculado y su margen dibujado; un RTO demasiado corto
   retransmite de más (contado), uno largo se duerme. Cierre: "Fiabilidad no
   es no perder nada. / Es darse cuenta a tiempo."

### 4.3 Congestión: la cortesía que sostiene la red  (slug `protocolos-internet-4-3-congestion`)
La red no se cae porque cada emisor decide frenar.
1. **El colapso** — 1986: todos empujan, las colas se llenan, se descarta, se
   retransmite, se empuja más. La `Cola` desbordada y el throughput útil
   cayendo a una fracción MEDIDA de la capacidad.
2. **Arranque lento** — `arranque_lento`: cwnd duplicándose cada RTT hasta
   el umbral; la exponencial dibujada con sus valores; sondear sin creerse
   dueño del enlace.
3. **La sierra** — `aimd`: sumar uno por RTT, partir por la mitad al perder;
   la `Sierra` característica con el throughput medio MEDIDO y el punto exacto
   donde ocurrió cada pérdida marcado en rojo.
4. **CUBIC y BBR** — la sierra de Reno junto a la curva cúbica (la de Linux
   por defecto) y a BBR, que mide el cuello de botella en vez de esperar la
   pérdida; las tres trazas con su media medida y su latencia asociada.
   Cierre: "Nadie obliga a tu computadora a frenar. / Frena porque, si no,
   no funciona para nadie."

## Módulo 5 — Los servicios que hacen usable la red

### 5.1 DNS: el directorio del mundo  (slug `protocolos-internet-5-1-dns`)
Nadie escribe direcciones IP: la red tiene una capa de nombres.
1. **El árbol de nombres** — el `Arbol` invertido: raíz, TLD, dominio,
   subdominio, leído de derecha a izquierda; quién manda en cada nivel.
2. **La resolución paso a paso** — `resolver_dns` en `Escalera`: el resolutor
   pregunta a la raíz, al TLD y al autoritativo; cada salto suma RTT MEDIDO
   hasta la respuesta. Cuatro viajes para una dirección.
3. **La caché y el TTL** — `cache_dns`: la segunda consulta se responde en
   ~0 ms; la tasa de acierto MEDIDA sobre una traza de consultas; el TTL
   expira y el ciclo vuelve a empezar (el precio de cambiar de servidor).
4. **La raíz** — 13 identidades de servidor raíz que son cientos de máquinas
   por anycast (enlace con 7.1); qué pasa cuando el DNS falla aunque la red
   funcione. Cierre: "La red enruta números. / Los nombres son un servicio
   que alguien sostiene."

### 5.2 DHCP y NAT: casa prestada, puerta compartida  (slug `protocolos-internet-5-2-nat`)
Cómo consigue una dirección tu máquina, y por qué la comparte.
1. **DORA** — `dhcp_dora`: Discover a todos, Offer, Request, Ack; la
   concesión con su tiempo de arriendo y qué más llega en el paquete
   (máscara, ruta por defecto, DNS).
2. **Una IP para todos** — la casa con 8 aparatos y una sola dirección
   pública; las direcciones privadas (RFC 1918) marcadas como no ruteables:
   fuera de casa no existen.
3. **La tabla de traducción** — `nat_traducir`: el router reescribe origen y
   **puerto**, anota la fila y deshace la traducción al volver; dos aparatos
   que usan el mismo puerto de origen no chocan porque NAT los renumera.
4. **Lo que NAT rompió** — de fuera hacia dentro no se puede iniciar nada:
   conexiones entrantes bloqueadas CONTADAS; por eso existen STUN, TURN y el
   agujereado de UDP. Cierre: "NAT le regaló veinte años a IPv4. / Y a cambio
   se quedó con la llave de la puerta."

### 5.3 Ver la red: ICMP, ping y traceroute  (slug `protocolos-internet-5-3-icmp`)
La red trae herramientas para diagnosticarse a sí misma.
1. **ICMP: el protocolo que se queja** — no lleva datos: lleva noticias.
   Destino inalcanzable, tiempo excedido, fragmentación necesaria: los tres
   mensajes con la cabecera del paquete culpable dentro.
2. **Ping mide** — `ping`: eco y respuesta; el RTT se descompone en
   propagación (medida por distancia, tope duro c) y espera en cola; el mismo
   ping bajo carga sube su RTT en la cifra medida.
3. **Traceroute** — `traceroute`: TTL=1, 2, 3... cada router va contestando
   "tiempo excedido" y delata su dirección; la `Escalera` se construye salto
   a salto con los tiempos reales, incluidos los `*` de quien no contesta.
4. **El MTU escondido** — `pmtud`: un enlace del camino tiene MTU menor;
   con DF activado el paquete rebota con "fragmentación necesaria" y el
   emisor baja su tamaño; si alguien filtra ICMP, el agujero negro: la
   conexión se cuelga sin motivo aparente. Cierre: "La red no es opaca. /
   Sabe quejarse, si la dejas."

## Módulo 6 — La web y el candado

### 6.1 HTTP: pedir y responder  (slug `protocolos-internet-6-1-http`)
El protocolo más usado del mundo cabe en una línea de texto.
1. **La petición** — `GET /index.html HTTP/1.1` con sus cabeceras, en texto
   plano legible; la respuesta con su estado, sus cabeceras y su cuerpo.
   Bytes CONTADOS: cuánto es protocolo y cuánto es contenido.
2. **Los códigos** — 200, 301, 404, 500 y qué decide cada familia; el
   navegador siguiendo un 301 en pantalla (dos viajes por una redirección).
3. **Sin estado, con memoria** — HTTP no recuerda; la cookie y la caché
   (`If-None-Match` → 304) devuelven la memoria. Bytes ahorrados MEDIDOS.
4. **Una fila para 40 objetos** — `http_transferencia`: una página con 40
   recursos, en serie vs 6 conexiones paralelas; el tiempo total MEDIDO en
   ambas. El cuello de botella no es el ancho de banda: son los viajes.
   Cierre: "Pedir es fácil. / Pedir cuarenta cosas por un solo tubo, no."

### 6.2 TLS: el candado de la web  (slug `protocolos-internet-6-2-tls`)
Cómo se cifra un canal con alguien a quien nunca has visto.
1. **El apretón** — `Escalera` de TLS 1.2: ClientHello, ServerHello,
   certificado, intercambio de claves, Finished; los RTT CONTADOS antes del
   primer byte de HTTP, sumados a los de TCP.
2. **La clave que nadie mandó** — `dh_pequeno`: cada lado combina su secreto
   con el público del otro y ambos llegan al MISMO número en pantalla, sin
   que ese número cruce nunca el cable (se apoya en el curso 19, no lo
   repite).
3. **El certificado y su cadena** — `cadena_certificados`: el certificado del
   sitio firmado por una intermedia firmada por una raíz que ya está en tu
   equipo; la firma se verifica en pantalla y luego se altera un byte y la
   verificación FALLA en rojo.
4. **1.3: un viaje** — `tls_viajes`: 1.2 = 2 RTT, 1.3 = 1 RTT, reanudado
   0-RTT; las tres barras de tiempo comparadas con cifras, y la advertencia
   honesta del 0-RTT (repetible). Cierre: "El candado no lo pone el sitio. /
   Lo pone una cadena de firmas que decidiste creer."

### 6.3 HTTP/2 y QUIC: el fin de la fila india  (slug `protocolos-internet-6-3-quic`)
Veinte años después, el problema seguía siendo la fila.
1. **Multiplexar** — HTTP/2: los 40 objetos como flujos entrelazados en UNA
   conexión, en binario, con las cabeceras comprimidas (HPACK); tiempo total
   MEDIDO frente a las dos formas de 6.1.
2. **El bloqueo de cabeza de línea** — `hol_bloqueo`: se pierde UN segmento
   TCP y **todos** los flujos se paran, porque TCP entrega en orden aunque
   los datos ya estén ahí. Flujos parados CONTADOS.
3. **QUIC sobre UDP** — la misma pérdida, pero cada flujo tiene su propio
   orden: solo se para el afectado (contado al lado del anterior). Y el
   apretón de transporte y el de TLS ocurren juntos.
4. **0-RTT y la mudanza de red** — datos en el primer paquete al reconectar;
   el ID de conexión sobrevive al cambio de wifi a móvil sin reconectar.
   Cierre: "La web no se hizo más rápida cambiando el cable. / Se hizo más
   rápida cambiando la cola."

## Módulo 7 — La red real: escala y tiempo

### 7.1 Acercar el contenido: CDN y anycast  (slug `protocolos-internet-7-1-cdn`)
Contra la velocidad de la luz no se optimiza: se acorta el camino.
1. **El viaje largo** — un usuario en Ciudad de México pidiendo a un
   servidor en Fráncfort: distancia real, RTT mínimo MEDIDO por la velocidad
   de la luz en fibra (2c/3) y el real con saltos. El tope físico se declara.
2. **La caché al borde** — `cdn`: la misma petición servida desde un PoP a
   pocos ms; sobre una traza de peticiones, la tasa de acierto y el alivio al
   origen MEDIDOS; qué se puede cachear y qué no.
3. **Anycast** — `anycast`: la MISMA dirección IP anunciada por BGP desde
   ocho sitios; cada usuario cae en el más cercano por haversine y la
   latencia media baja de X a Y (medido). Es ruteo, no magia.
4. **Cuando el borde falla** — el PoP se cae y BGP re-enruta a los usuarios
   al siguiente sitio: la latencia sube en la cifra medida, pero nadie queda
   sin servicio. Cierre: "No puedes hacer la luz más rápida. / Puedes poner
   la respuesta más cerca."

### 7.2 Colas, latencia y bufferbloat  (slug `protocolos-internet-7-2-bufferbloat`)
Por qué tu videollamada se corta justo cuando alguien descarga algo.
1. **La ley de Little** — `little` verificada sobre la simulación de cola:
   L = λ·W con las tres cifras medidas en pantalla; la ocupación media
   explota cuando la carga se acerca a 1 (curva dibujada).
2. **El búfer grande que empeora** — `bufferbloat`: el mismo enlace con búfer
   de 8 y de 1000 paquetes; con el grande no se pierde casi nada... y la
   latencia sube de decenas de ms a más de un segundo (MEDIDO). El ping bajo
   descarga como demostración.
3. **AQM: descartar a tiempo** — `codel`: descartar temprano y poco mantiene
   la cola corta; latencia y descartes MEDIDOS frente al caso anterior. Es
   preferible perder un paquete que esconder un segundo.
4. **Prioridad** — la videollamada y la descarga compitiendo: sin colas
   separadas la voz sufre; con prioridad/justicia (`fq`) la voz pasa y la
   descarga apenas lo nota. Cifras de ambos. Cierre: "El búfer no te regala
   tiempo. / Te lo cobra en latencia."

### 7.3 Tiempo real: voz, video y jitter  (slug `protocolos-internet-7-3-tiempo-real`)
Hay tráfico al que llegar tarde le sirve tan poco como no llegar.
1. **RTP y el reloj** — la voz troceada en paquetes de 20 ms sobre UDP, cada
   uno con marca de tiempo y número de secuencia; llegar tarde es igual que
   perderse, y se ve.
2. **Jitter y el búfer de reproducción** — `jitter`: llegadas irregulares
   medidas; un búfer pequeño da cortes CONTADOS, uno grande da retardo
   MEDIDO. El compromiso, dibujado.
3. **ABR: escoger calidad** — `abr`: el video en escalones de bitrate; sobre
   una traza real de ancho de banda el algoritmo sube y baja de calidad, y se
   cuentan los atascos y los cambios. Por qué prefiere borroso a parado.
4. **En vivo** — la latencia de un directo: captura, codificación, CDN,
   búfer; dónde se van los segundos (desglose medido) y qué hace WebRTC para
   bajar a decenas de ms. Cierre: "Para la voz, un paquete tarde / es un
   paquete perdido."

## Módulo 8 — Internet fuera de la Tierra

### 8.1 Internet en órbita: GEO, LEO y la malla láser  (slug `protocolos-internet-8-1-orbita`)
Los protocolos de la Tierra, puestos donde el retardo manda.
1. **GEO: 240 ms de ida y vuelta** — `rtt_orbital`: 35 786 km, ~119 ms por
   tramo, RTT MEDIDO; la geometría dibujada a escala declarada. Esa cifra no
   se negocia: es la luz.
2. **TCP sufre** — `tcp_en_orbita`: el arranque lento tarda muchos RTT en
   llenar el tubo y el techo por ventana/RTT es una fracción MEDIDA de la
   capacidad contratada; el PEP que parte la conexión en dos y su ganancia
   medida (y lo que rompe: TLS extremo a extremo).
3. **LEO: bajar la órbita** — 550 km → ~4 ms por tramo (medido) pero el
   satélite no se queda quieto: `pase_leo` (curso 24) da la duración del pase
   y el traspaso; cada handover es una ruta que cambia.
4. **Rutear la malla** — `malla_laser`: la constelación como grafo de enlaces
   ópticos y **el mismo `dijkstra` del módulo 3** buscando el camino a
   Londres; el camino cambia cuando la constelación se mueve. Cierre: "Los
   mismos protocolos, un poco más arriba. / Y de pronto la luz es lenta."

### 8.2 DTN: la red que tolera la desconexión  (slug `protocolos-internet-8-2-dtn`)
Cuando no hay camino completo, ni siquiera hay a quién hacerle el apretón.
1. **El enlace que no está** — un rover al otro lado de Marte: durante horas
   NO existe camino extremo a extremo. Se intenta el apretón de TCP y falla
   por definición: `ventanas_contacto` muestra los huecos.
2. **El bundle y la custodia** — el paquete se vuelve **bundle** y cada nodo
   acepta la CUSTODIA: lo guarda hasta que puede pasarlo. El almacenamiento
   como parte de la red, no como accidente.
3. **Plan de contactos** — `dtn_custodia`: el ruteo por grafo de contactos
   (CGR) sabe CUÁNDO habrá enlace, no solo por dónde; el bundle espera 6
   horas en un orbitador y sigue. Retenciones y tiempos MEDIDOS.
4. **Entregado** — el bundle llega días después, entero y verificado, por una
   ruta que nunca existió completa ni un instante. Comparación de entregas
   TCP vs DTN sobre el mismo plan (contadas). Cierre: "Internet supone que
   siempre hay camino. / Fuera de casa, esa suposición se cae."

### 8.3 Internet interplanetario: CCSDS y Marte  (slug `protocolos-internet-8-3-ccsds`)
El cierre: qué sobrevive del Internet terrestre cuando se va lejos.
1. **22 minutos luz** — `retardo_marte`: de 4 a 24 minutos por tramo según la
   posición orbital; el año sintético con la curva de distancia y su retardo
   asociado, MEDIDOS. Un ping de ida y vuelta a Marte tarda hasta 48 minutos.
2. **La pila del espacio** — `pila_ccsds` frente a `pila_tcpip`: qué capa se
   parece a cuál, qué se cambió y por qué (marcos de telemetría, códigos de
   corrección del curso 24, Proximity-1, BP sobre todo ello).
3. **Un archivo a Marte** — el recorrido completo de una imagen: rover →
   orbitador (Proximity-1, ventana corta) → DSN (banda X, minutos luz) →
   centro de control; cada tramo con su retardo y su tasa MEDIDOS, y el total
   en horas.
4. **La red que nadie manda, tampoco allá** — el cierre de la familia: el
   mismo principio (capas, direcciones, tolerancia al fallo, acuerdos en vez
   de autoridad) resistiendo a 300 millones de kilómetros. Cierre: "Internet
   no es un cable. / Es un acuerdo que sigue funcionando lejos de casa."

## Cosecha heredada (cursos 22, 23 y 24) — vigente para los agentes

Todas las trampas de `curso-20-algebra-lineal.md`, `curso-21-calculo-
vectorial.md` y `curso-22-comunicaciones-digitales.md` SIGUEN VIGENTES.
Las de mayor riesgo en esta familia (mucha tabla, mucho texto, muchas cifras
que cambian):

- Transform solo entre gemelas de estructura IDÉNTICA (glifos rotos si no).
- Transform de cifras dentro de animaciones largas deja dígitos a medio
  morfar: `Succession(Transform corto, Wait)`, y ancho fijo (`03d`) en los
  contadores.
- Rajdhani/Space Mono no traen superíndices ni griegas: `10^-3`, `λ`, `Σ`,
  `≈` van en MathTex; `tag_hud` solo ASCII.
- `set_opacity` enciende el fill; `Indicate` sobre `_con_fondo`.
- `Rotulos.mostrar` cobra ~0.25 s extra de salida en cada relevo: contarlo al
  estimar duraciones (pies ≥ 5 s, clips 28–45 s).
- Un pie mostrado antes de dibujar una rejilla/tabla queda DEBAJO de ella.
- `render_local --frames 8` muestrea: puede caer justo en un relevo de pie;
  para `final_state` extraer el ÚLTIMO frame real con ffmpeg.
- `interpolate_color` exige `ManimColor` (las `C_*` de la familia son `str`).
- Las etiquetas de `Grafica` son hijos internos: no aparecen si se animan
  `.ejes`/`.curva` por separado.
- `render_local.py` aborta si falta CUALQUIER clip declarado en `curso.json`:
  crear stubs antes de paralelizar agentes.
- Riesgo NUEVO de esta familia: **el texto monoespaciado de cabeceras y
  tablas se encima con facilidad**. Toda `Cabecera`/`Tabla` se dimensiona por
  medición (`tag_hud` ≈ 0.0094·font_size por carácter) y nunca a ojo.

## Cosecha de trampas del lote 1 (medida durante la producción)

Propias de esta familia; se suman a la cosecha heredada de arriba.

**De la pieza `Cabecera` / `Paquete` (mucho texto en poco sitio)**
- La cabecera IPv4 de 12 campos **se mide, no se ajusta a ojo**: una sonda
  en el contenedor que imprima campo a campo ancho de caja / de rótulo / de
  valor evita agrandar la pieza por corazonadas. Con `ancho=11.6`,
  `alto_fila=0.55`, `fs=15` ningún rótulo se encoge (2.1).
- **La sonda debe replicar la sombra de `Text` del style_block**: sin ella,
  el glifo del espacio infla el bbox y "Longitud total" mide 3.43 en vez de
  1.37 → falsos positivos de colisión.
- Con nombre **y** valor, la fila necesita ≥ 0.42 de alto; a 0.27 las dos
  líneas se salen de su caja y las filas se enciman (2.3).
- Dos cabeceras lado a lado a 5.0 de ancho dejan los campos estrechos a
  ~6 px: **apiladas a todo el ancho** se leen (2.3).
- Rótulos de campo contiguos se tocan: la pieza los encoge al 0.86 del
  ancho de su caja (corregido en la librería tras el molde).
- Una cabecera que nace **sin valores** tiene textos vacíos (0 glifos): el
  Transform a la versión con valores NO es estructura idéntica. Nacer
  siempre con todos los valores puestos.

**De `Tabla`**
- `con_filas` con distinto **número** de filas deja de ser gemela. Se
  resuelve con `filas_max` (reserva las filas y rellena con guiones).
- El resaltado añade un `Rectangle`: mezclar `resaltar=None` con
  `resaltar=i` entre gemelas también rompe la estructura → `resaltable=True`
  lo reserva en todas las filas. **Es opt-in a propósito**: los rectángulos
  ensanchan el bounding box y moverían las tablas ya aprobadas.
- Una MAC completa (17 caracteres) no cabe junto a una topología: se rotula
  la cola (`MAC[-5:]`), que es lo que distingue a los vecinos.

**De `Topologia` y las fichas que viajan**
- Los rótulos de arista van a +0.26 de la línea y los de nodo a −0.49:
  cualquier ficha que viaje **sobre** el cable los pisa → carriles
  +0.60 / 0.0 / −0.80 y `ocultar_etiquetas()`.
- Una ficha que termina su `MoveAlongPath` en un nodo **se le monta encima**:
  parar en `enlace(a, b).punto_en(0.55)` y marcar la entrega encendiendo el
  nodo.
- Un paquete posado sobre un aparato tapa el aparato y su etiqueta: que
  viaje por encima del cable (`punto(k) + UP*0.6`).
- Un camino resaltado con `Line(punto(a), punto(b))` cruza los círculos de
  los nodos: usar `enlace(a, b).linea.copy()`, que ya trae el buff.

**De composición y ritmo**
- Escalar un VGroup para que quepa **encoge también la letra**: a 0.58 los
  rótulos de una `Pila` se vuelven ilegibles. Pasar `ancho`/`alto`/`fs` a la
  pieza en vez de escalar.
- Los rótulos del momento anterior deben apagarse **antes** del pie nuevo, o
  el frame muestreado enseña pie nuevo + rótulo viejo.
- Los clips que salen en 26–27 s en el primer render se engordan con
  `wait`, no metiendo más contenido: el tope inferior es 28 s.
- `--frames 8` cae a veces en un relevo y muestra un frame casi vacío: no es
  un fallo, pero el `final_state` hay que sacarlo del **último frame real**
  con ffmpeg.

**De honestidad con las cifras**
- Si se dibuja una **ventana** de una simulación más larga, la estadística
  se mide sobre la ventana dibujada: citar la corrida entera mientras se ve
  un trozo es mentir (1.1 clip 3: 3 de 60 = 5.0 %, no el 4.17 % global).
- Los datos que **no** calcula la librería (adopción de IPv6, cronología de
  agotamiento de IPv4) se declaran como medición pública en el propio pie.
- `Paquete` reparte el ancho por pesos normalizados: si los pesos **suman**
  el ancho, cada caja mide exactamente su peso → cabecera constante entre
  fragmentos y carga a escala (declarando la escala en pantalla).

**De tipografía**
- La familia es **estrictamente sin acentos** en todo texto en pantalla (no
  solo en `tag_hud`), como los cursos 22 y 24. Los acentos viven en
  `curso.json` (título y descripción), que no se renderiza.
- `2^32`, `2^128`, `λ` y `≈` solo en `MathTex`.

## Cosecha de trampas del lote 2 (medida durante la producción)

**De honestidad — las tres que había que cazar antes de animarlas**
- **El conteo al infinito solo ocurre si el corte deja el destino
  inalcanzable.** Con otro corte la red converge tranquilamente y no hay
  nada que contar. Con la cadena A—B—C—D cortando C—D salen las series
  reales (3, 5, 7, … 15, 16 = el infinito de RIP), y con horizonte
  dividido muere en 2 rondas.
- **`conteo_al_infinito` devolvía `max_rondas` de historia aunque la red se
  hubiera estabilizado antes**: su corte exigía que el destino fuera
  inalcanzable. Para un corte que sí converge decía 12 cuando lo honesto
  era 7. Corregido en la librería con `rondas_estable` (lo encontró la
  agente de la 3.1 midiendo a mano en vez de fiarse del campo).
- **Comparar la MEDIA de dos sierras cortas hace parecer que CUBIC es peor
  que Reno** (21.06 frente a 27.63). Lo que de verdad los separa es el
  tiempo de recuperación: Reno sube +1 por RTT y depende del RTT, CUBIC no.
  A 20 ms **gana Reno 1.9×**, a 40 ms empatan, a 200 ms gana CUBIC 5.4×.
  La 4.3 enseña las dos cosas y pone el pie "compararlas aquí sería mentir".
- Los datos que la librería no calcula (los ~75 000 AS de Internet) se
  rotulan como medición pública **y en otro color**, para que el cian siga
  significando "esto lo calculó la librería".
- Un camino rechazado por política **no tiene por qué ser más corto**: la
  3.3 lo midió, tenía los mismos saltos, y el pie quedó en "El cable está
  ahí. El contrato, no".

**De `Topologia`**
- Cuelga la etiqueta SIEMPRE debajo del nodo: si dos nodos conectados
  comparten la coordenada x, la arista sale vertical y **tacha la letra**.
  Le pasó a la 3.1 y a la 3.2 por separado. Se arregla separando las
  posiciones o con `etiquetas_a({nodo: UP})`, ya en la librería.
- `enlace(a, b)` devuelve la MISMA línea para (a,b) y (b,a), dibujada en el
  sentido en que se declaró la arista: un `MoveAlongPath` sobre ella va al
  revés la mitad de las veces → `tramo(a, b, desde, hasta)`, ya en la
  librería.
- Una ficha que termina su trayecto en el nodo se monta encima de él y de
  la etiqueta del vecino: parar en 0.66–0.74 y encender el nodo.
- Encadenar tramos a secas **teletransporta** la ficha en cada relevo:
  construir el trayecto desde la posición ACTUAL.
- `resaltar_camino()` también recolorea los NODOS: pisa un color que ya
  hubieras puesto (p. ej. el verde de "fijado" de Dijkstra).
- `grafo_de` exige costo numérico: un `None` revienta con `float(None)`.
  Declarar coste 1 y dibujar con `costos=False`.
- Una ficha sobre el cable tapa los rótulos de coste: si el clip quiere que
  se lean, usar `ShowPassingFlash` sobre la línea.

**De `Tabla`, `Paquete` y las gemelas**
- **`"%2d"` no es ancho fijo**: la sombra de `Text` descarta el glifo del
  espacio, así que `" 3"` tiene 1 glifo y `"16"` tiene 2 → gemelas rotas.
  `"%02d"` sí.
- `Transform` **no actualiza los atributos Python** del objeto original: si
  solo iluminas la copia destino, el `_iluminados` del original queda vacío
  y la siguiente gemela pierde el resaltado.
- `Tabla` pinta la fila entera de un color: para que solo las cifras vayan
  en cian hay que repintar por celda (repintar no toca la estructura, así
  que las gemelas siguen siendo válidas).
- Mantener el **orden de fila FIJO** al animar una tabla que crece:
  reordenar por costo hace saltar de fila a los routers cada ronda.
- Los empates de coste **parecen un bug en pantalla** (la columna
  "siguiente" cambia sin que cambie el costo): elegir los pesos de la red
  para que no haya ninguno.
- `Sierra` fija sus marcas de pérdida en la CONSTRUCCIÓN: pasar los índices
  ya al constructor y diferir solo el `FadeIn` de ese hijo.

**De composición**
- El style_block del **molde** solo importa lo del lote 1: cada lección de
  los módulos 3 y 4 tiene que ampliar su `from protocolos import`.
- `FadeOut(viejo) + FadeIn(nuevo)` en la misma posición dentro de UN solo
  `play` se cruzan y el frame muestreado enseña los dos textos encimados.
- Bajo una topología solo cabe UNA línea de cifras entre los rótulos de
  nodo y el pie.
- Al cortar un enlace hay que apagar su etiqueta de coste: la cruz roja va
  al punto medio y el rótulo está a +0.26.
- Un `tag_hud` largo anclado con `next_to` a un objeto descentrado hereda
  su centro horizontal y se sale del cuadro: `move_to` a un punto fijo.
- A 480p un stroke rojo fino sobre un nodo con aristas encima **parece
  azul**: antes de dar por roto el código, ampliar el frame con ffmpeg.

## Hitos globales

- **2026-08-26**: **LOTE 2 PUBLICADO DE PUNTA A PUNTA.** PR #48 mergeado
  (`d51a673`); 12 proyectos en producción con 48/48 `qh` adoptados;
  narración Charon **serial 6/6 a la primera** (24 wavs, 0 reintentos); 6
  `exports/protocolos-internet-[34]-*/curso_narrado.mp4` de 2:17–2:41 con
  picos ≤ −0.5 dB (9 clips re-muxeados; dos llegaban a −0.0 dB y bajaron
  2 dB). Marca sonora a −6.0 dB exacto dentro de las salidas.
  **Medio curso hecho: 12 de 24 lecciones publicadas.**

- **2026-08-25**: plan maestro escrito (24 lecciones, 8 módulos, 4 lotes) y
  rama `curso/protocolos-internet` creada desde `origin/main` (34d5890).
- **2026-08-26**: **LOTE 1 PUBLICADO DE PUNTA A PUNTA.** PR #47 mergeado
  (`fa3caf4`); 6 proyectos en producción con 24/24 `qh` adoptados; narración
  Charon **serial 6/6 a la primera** (24 wavs, 0 reintentos); 6
  `exports/protocolos-internet-*/curso_narrado.mp4` de 2:18–2:29 con picos
  ≤ −0.5 dB (4 clips re-muxeados a −1.5 dB). **Marca sonora a −6.0 dB
  EXACTO medida dentro de las 6 salidas** (AAC 24 kHz mono continuo):
  tercera familia con la marca, ya es rutina.
- **2026-08-25**: lote 1 escrito y validado en `ql` — 6 lecciones, 24
  clips, todos entre 28 y 35 s, frames revisados uno a uno. Librería
  `protocolos.py` con los números de los módulos 1 y 2 y 13 piezas de
  dibujo. Los 151 tests del Studio en verde.
