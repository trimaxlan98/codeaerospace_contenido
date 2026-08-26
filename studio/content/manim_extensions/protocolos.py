"""Protocolos de Internet: la red que nadie manda.

Libreria de la familia "Protocolos de Internet" (curso 25): la capa de
PAQUETES. Donde `comunicaciones.py` llevaba bits por UN enlace, aqui hay
muchos enlaces y ningun jefe: trocear, rotular, perder, reintentar,
enrutar y acordar.

Todo el calculo es python/numpy puro y DETERMINISTA (el unico azar va con
`np.random.default_rng(semilla)` fija): mismo script, mismo render —
condicion necesaria para `--disable_caching`. Sin red, sin disco, sin
scipy.

La regla de color de la familia: **el color dice el papel**.
    C_PAQUETE  ambar    el paquete, el datagrama, la trama: el dato
    C_CIFRA    cian     TODA cifra calculada
    C_RED      azul     nodos, enlaces, topologia, el medio
    C_PERDIDA  rojo     perdida, error, congestion, descarte, ataque
    C_OK       verde    entregado, confirmado, ACK
    C_CAPA     violeta  capas, cabeceras, jerarquia, nombres
    C_CLAVE    fucsia   seguridad: claves, certificados, lo cifrado
    C_COLA     naranja  colas, buferes, espera, ancho de banda

Numeros de los LOTES 1, 2 y 3 (modulos 1 a 6). Toda cifra en pantalla sale
de aqui o de la tabla del style_block, nunca escrita a mano:
    troceado / conmutacion / mux_estadistico / cola_mm1 / little
    encapsular / crc32_trama / trama_ethernet / csma_cd
    switch_aprende / arp_resolver
    checksum_ip / cabecera_ipv4 / cabecera_ipv6 / fragmentar / ttl_camino
    cidr / mascara_bits / prefijo_mas_largo / agregar_rutas
    ipv6_expandir / ipv6_comprimir / eui64 / espacio_direcciones
    grafo_de / bellman_ford / conteo_al_infinito
    dijkstra / camino_dijkstra / inundacion
    bgp_mejor_ruta / secuestro_bgp
    demux / handshake_tcp / bdp / ventana / rtt_jacobson
    arranque_lento / aimd / cubic / colapso_congestion
    recuperacion_tras_perdida
    resolver_dns / cache_dns / dhcp_dora / es_privada
    nat_traducir / nat_entrante / ping / traceroute / pmtud
    http_peticion / cache_condicional / http_transferencia
    tls_viajes / dh_pequeno / cadena_certificados
    hol_bloqueo / quic_migracion

Piezas (VGroup con localizadores que siguen move_to/shift, NO scale;
todo lo que cambia tiene gemela `con_*` de estructura IDENTICA):
    paquete        capsula de campos; .campo(n) .iluminar(n); .con_valores()
    cabecera       tabla de campos por filas de 32 bits; .con_valores()
    nodo           host / switch / router / servidor / satelite
    enlace         linea entre nodos; .punto_en(frac)
    topologia      grafo dibujado; .nodo(n) .enlace(a,b) .resaltar_camino()
                   .camino(nombres) da la ruta para MoveAlongPath;
                   .ocultar_etiquetas() para que una ficha no las pise
    cola           bufer con ranuras; .con_ocupacion(n)
    pila           torre de capas; .capa(i); .con_encapsulado(k)
    tabla          filas x columnas de texto HUD; .con_filas();
                   `filas_max` reserva sitio para que la tabla CREZCA
    reloj          contador de milisegundos en cian; .con_ms()
    barra_bits     32/128 bits con raya movil red|host; .con_prefijo(n)
    ficha          token cuadrado del datagrama; .con_texto()
    bus            cable compartido con estaciones; .punto(i) .estacion(i)
    ranuras        regla de ranuras de tiempo; .con_colores()
    escalera       diagrama de tiempo (handshake, DNS, TLS); .paso(k)
    sierra         cwnd frente al tiempo; .marcas .media; .con_traza()
    arbol          jerarquia por niveles (DNS, cadena de certificados);
                   .nodo(nivel, i); .con_marcados()

Uso en un clip (el style_block de la familia ya importa todo):
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from protocolos import *
"""
import math
import zlib

import numpy as np
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Arrow, Circle,
                   DashedLine, Dot, Line, Polygon, Rectangle,
                   RoundedRectangle, Square, Triangle, VGroup,
                   VMobject)

from algebra_lineal import (C_AREA, C_EJE, C_I, C_IMG, C_J, C_K, C_PROPIO,
                            C_REJILLA, C_VEC, C_VIVA, _Anclada, _texto_hud,
                            fmt)

# --- roles de la familia ------------------------------------------------
C_PAQUETE = C_I        # ambar: el dato que viaja
C_CIFRA = C_J          # cian: cifras calculadas
C_RED = C_VIVA         # azul: nodos, enlaces, topologia
C_PERDIDA = C_VEC      # rojo: perdida, error, congestion
C_OK = C_IMG           # verde: entregado, confirmado
C_CAPA = C_K           # violeta: capas, cabeceras, jerarquia
C_CLAVE = C_PROPIO     # fucsia: seguridad
C_COLA = C_AREA        # naranja: colas, buferes, espera

_LUZ_KM_S = 299792.458
_FIBRA_KM_S = 2.0 * _LUZ_KM_S / 3.0   # ~200 000 km/s: la luz en vidrio


# =====================================================================
# Modulo 1.1 — Trocear: conmutacion, multiplexacion y colas
# =====================================================================
def troceado(n_bytes, mtu=1500, cabeceras=40):
    """Trocear `n_bytes` en paquetes de MTU. -> dict MEDIDO.

    `cabeceras` = bytes de cabecera por paquete (20 IP + 20 TCP por
    defecto). La carga util por paquete es mtu - cabeceras.
    """
    n_bytes = int(n_bytes)
    util = int(mtu) - int(cabeceras)
    n = int(math.ceil(n_bytes / util))
    ultimo = n_bytes - util * (n - 1)
    total = n_bytes + n * int(cabeceras)
    return {"paquetes": n, "util_por_paquete": util, "ultimo": ultimo,
            "bytes_datos": n_bytes, "bytes_cabecera": n * int(cabeceras),
            "bytes_total": total,
            "sobrecosto_pct": 100.0 * n * int(cabeceras) / total}


def conmutacion(n_bits, tasa_mbps=10.0, saltos=3, km_por_salto=500.0,
                establecer_ms=250.0, tam_paquete_bits=12000):
    """Latencia de circuito vs paquetes para el MISMO mensaje. -> dict.

    Circuito: establecer + transmitir todo + propagacion.
    Paquetes (store-and-forward): el primer paquete cruza los N saltos y
    los demas van en tuberia -> (N + k - 1) transmisiones de paquete.
    """
    r = float(tasa_mbps) * 1e6
    prop_ms = 1000.0 * float(saltos) * float(km_por_salto) / _FIBRA_KM_S
    tx_total_ms = 1000.0 * float(n_bits) / r
    circuito = float(establecer_ms) + tx_total_ms + prop_ms
    k = int(math.ceil(float(n_bits) / float(tam_paquete_bits)))
    tx_pkt_ms = 1000.0 * float(tam_paquete_bits) / r
    paquetes = (int(saltos) + k - 1) * tx_pkt_ms + prop_ms
    return {"circuito_ms": circuito, "paquetes_ms": paquetes,
            "establecer_ms": float(establecer_ms), "propagacion_ms": prop_ms,
            "tx_total_ms": tx_total_ms, "tx_paquete_ms": tx_pkt_ms,
            "n_paquetes": k, "saltos": int(saltos),
            "ganancia": circuito / paquetes if paquetes else float("nan")}


def mux_estadistico(n_flujos=10, pico_mbps=2.0, ciclo_activo=0.15,
                    capacidad_mbps=6.0, pasos=600, semilla=11):
    """Flujos a rafagas sobre un enlace compartido. -> dict MEDIDO.

    Compara reservar el pico (circuito) contra dejarlos competir. Cada
    flujo esta activo con probabilidad `ciclo_activo` en cada paso.
    """
    rng = np.random.default_rng(int(semilla))
    activos = rng.random((int(pasos), int(n_flujos))) < float(ciclo_activo)
    demanda = activos.sum(axis=1) * float(pico_mbps)
    cabe_reserva = int(math.floor(float(capacidad_mbps) / float(pico_mbps)))
    excede = int(np.count_nonzero(demanda > float(capacidad_mbps)))
    return {"demanda": demanda, "activos": activos.sum(axis=1),
            "capacidad_mbps": float(capacidad_mbps),
            "n_flujos": int(n_flujos),
            "flujos_con_reserva": cabe_reserva,
            "demanda_media_mbps": float(demanda.mean()),
            "demanda_pico_mbps": float(demanda.max()),
            "pasos_excedidos": excede,
            "pct_excedido": 100.0 * excede / float(pasos),
            "ganancia": float(n_flujos) / cabe_reserva if cabe_reserva else
            float("nan")}


def cola_mm1(lmbda=0.85, mu=1.0, n_llegadas=4000, capacidad=8, semilla=3):
    """Cola de un servidor con bufer FINITO, por eventos. -> dict MEDIDO.

    `lmbda` y `mu` en paquetes por unidad de tiempo. Devuelve la traza de
    ocupacion, la espera media MEDIDA y los descartes CONTADOS.
    """
    rng = np.random.default_rng(int(semilla))
    n = int(n_llegadas)
    entre = rng.exponential(1.0 / float(lmbda), n)
    servicio = rng.exponential(1.0 / float(mu), n)
    t_llegada = np.cumsum(entre)
    libre_en = 0.0
    en_cola = []          # instantes de salida de los que siguen dentro
    esperas, descartes = [], 0
    traza_t, traza_n = [], []
    for i in range(n):
        t = t_llegada[i]
        en_cola = [s for s in en_cola if s > t]
        ocupacion = len(en_cola)
        traza_t.append(t)
        traza_n.append(ocupacion)
        if ocupacion >= int(capacidad):
            descartes += 1
            continue
        inicio = max(t, libre_en)
        fin = inicio + servicio[i]
        libre_en = fin
        en_cola.append(fin)
        esperas.append(inicio - t)
    esperas = np.array(esperas)
    return {"t": np.array(traza_t), "ocupacion": np.array(traza_n),
            "espera_media": float(esperas.mean()),
            "espera_max": float(esperas.max()),
            "servicio_medio": float(servicio[:len(esperas)].mean()),
            "ocupacion_media": float(np.mean(traza_n)),
            "descartes": int(descartes), "llegadas": n,
            "pct_descarte": 100.0 * descartes / n,
            "utilizacion": float(lmbda) / float(mu),
            "capacidad": int(capacidad)}


def little(lmbda, w):
    """La ley de Little: L = lambda * W (paquetes en el sistema)."""
    return float(lmbda) * float(w)


# =====================================================================
# Modulo 1.2 — Capas y encapsulacion
# =====================================================================
CAPAS_TCPIP = (("Aplicacion", "HTTP", 0),
               ("Transporte", "TCP", 20),
               ("Red", "IP", 20),
               ("Enlace", "Ethernet", 18))


def encapsular(datos_bytes, capas=CAPAS_TCPIP):
    """El dato baja por la pila y cada capa le pega su cabecera. -> dict.

    Devuelve el tamano acumulado tras cada capa y el sobrecosto MEDIDO.
    """
    d = int(datos_bytes)
    pasos, tam = [], d
    for nombre, protocolo, cab in capas:
        tam += int(cab)
        pasos.append({"capa": nombre, "protocolo": protocolo,
                      "cabecera": int(cab), "tamano": tam})
    cab_total = tam - d
    return {"datos": d, "total": tam, "cabeceras": cab_total,
            "pasos": pasos,
            "sobrecosto_pct": 100.0 * cab_total / tam,
            "eficiencia_pct": 100.0 * d / tam}


# =====================================================================
# Modulo 1.3 — Ethernet, MAC, colisiones y ARP
# =====================================================================
def _mac_bytes(mac):
    return bytes(int(p, 16) for p in mac.split(":"))


def crc32_trama(datos):
    """CRC-32 REAL (el de Ethernet) de `datos` (bytes o str). -> int."""
    if isinstance(datos, str):
        datos = datos.encode("utf-8")
    return zlib.crc32(bytes(datos)) & 0xFFFFFFFF


def trama_ethernet(destino, origen, carga, tipo=0x0800):
    """Una trama Ethernet II REAL con su FCS. -> dict.

    `carga` en bytes o str; se rellena a 46 B (minimo del estandar).
    """
    if isinstance(carga, str):
        carga = carga.encode("utf-8")
    carga = bytes(carga)
    relleno = max(0, 46 - len(carga))
    cuerpo = (_mac_bytes(destino) + _mac_bytes(origen) +
              tipo.to_bytes(2, "big") + carga + b"\x00" * relleno)
    return {"destino": destino, "origen": origen, "tipo": tipo,
            "carga": carga, "relleno": relleno,
            "bytes": cuerpo, "fcs": crc32_trama(cuerpo),
            "longitud": 8 + len(cuerpo) + 4}   # preambulo + cuerpo + FCS


def voltear_bit(datos, i):
    """Voltea el bit `i` de un bytes. -> bytes (para romper el FCS)."""
    b = bytearray(datos)
    b[i // 8] ^= 1 << (7 - i % 8)
    return bytes(b)


def csma_cd(n_estaciones=3, semilla=5, max_intentos=8):
    """Escuchar, chocar, esperar: CSMA/CD con backoff exponencial.

    Todas quieren transmitir en la ranura 0. -> dict con la historia de
    colisiones y las ranuras de espera SORTEADAS (deterministas).
    """
    rng = np.random.default_rng(int(semilla))
    pendientes = list(range(int(n_estaciones)))
    intentos = {e: 0 for e in pendientes}
    ranura, historia, colisiones = 0, [], 0
    proximo = {e: 0 for e in pendientes}
    while pendientes and ranura < 400:
        quieren = [e for e in pendientes if proximo[e] <= ranura]
        if len(quieren) == 1:
            e = quieren[0]
            historia.append({"ranura": ranura, "evento": "transmite",
                             "estaciones": [e]})
            pendientes.remove(e)
        elif len(quieren) > 1:
            colisiones += 1
            historia.append({"ranura": ranura, "evento": "colision",
                             "estaciones": list(quieren)})
            for e in quieren:
                intentos[e] += 1
                k = min(intentos[e], 10)
                espera = int(rng.integers(0, 2 ** k))
                proximo[e] = ranura + 1 + espera
                historia[-1].setdefault("esperas", {})[e] = espera
        ranura += 1
    return {"historia": historia, "colisiones": colisiones,
            "ranuras": ranura, "n_estaciones": int(n_estaciones),
            "intentos": intentos}


def switch_aprende(eventos, puertos=None):
    """Un switch que aprende MACs. -> dict con la tabla y el conteo.

    `eventos` = [(origen, destino), ...]; `puertos` = {mac: puerto}.
    Cada trama se INUNDA si el destino no esta en la tabla, y va por
    unicast si ya se aprendio.
    """
    puertos = puertos or {}
    tabla, pasos, inundadas, unicast = {}, [], 0, 0
    for origen, destino in eventos:
        if origen not in tabla:      # el puerto se aprende UNA vez
            tabla[origen] = puertos.get(origen, len(tabla) + 1)
        conocido = destino in tabla
        if conocido:
            unicast += 1
        else:
            inundadas += 1
        pasos.append({"origen": origen, "destino": destino,
                      "accion": "unicast" if conocido else "inunda",
                      "puerto": tabla.get(destino),
                      "tabla": dict(tabla)})
    return {"pasos": pasos, "tabla": tabla, "inundadas": inundadas,
            "unicast": unicast, "total": len(eventos)}


def arp_resolver(ip_destino, vecinos, cache=None):
    """ARP: quien tiene esta IP. -> dict con los pasos y la cache nueva."""
    cache = dict(cache or {})
    if ip_destino in cache:
        return {"pasos": [{"tipo": "cache", "ip": ip_destino,
                           "mac": cache[ip_destino]}],
                "mac": cache[ip_destino], "cache": cache, "preguntas": 0}
    pasos = [{"tipo": "peticion", "ip": ip_destino, "a": "ff:ff:ff:ff:ff:ff"}]
    mac = vecinos.get(ip_destino)
    if mac:
        pasos.append({"tipo": "respuesta", "ip": ip_destino, "mac": mac})
        cache[ip_destino] = mac
    return {"pasos": pasos, "mac": mac, "cache": cache, "preguntas": 1}


# =====================================================================
# Modulo 2.1 — IP: cabecera, checksum, TTL y fragmentacion
# =====================================================================
CAMPOS_IPV4 = (("Version", 4), ("IHL", 4), ("DSCP/ECN", 8),
               ("Longitud total", 16), ("Identificacion", 16),
               ("Banderas", 3), ("Desplazamiento", 13),
               ("TTL", 8), ("Protocolo", 8), ("Checksum", 16),
               ("Direccion origen", 32), ("Direccion destino", 32))


def ip_a_bytes(ip):
    return bytes(int(o) for o in str(ip).split("."))


def ip_a_entero(ip):
    b = ip_a_bytes(ip)
    return (b[0] << 24) | (b[1] << 16) | (b[2] << 8) | b[3]


def entero_a_ip(x):
    x = int(x) & 0xFFFFFFFF
    return "%d.%d.%d.%d" % ((x >> 24) & 255, (x >> 16) & 255,
                            (x >> 8) & 255, x & 255)


def checksum_ip(cabecera):
    """Complemento a uno de 16 bits, el REAL de IPv4. -> int."""
    b = bytes(cabecera)
    if len(b) % 2:
        b += b"\x00"
    s = 0
    for i in range(0, len(b), 2):
        s += (b[i] << 8) | b[i + 1]
        s = (s & 0xFFFF) + (s >> 16)
    return (~s) & 0xFFFF


def cabecera_ipv4(origen="10.0.0.7", destino="93.184.216.34", ttl=64,
                  protocolo=6, longitud=1500, ident=0x1c46, banderas=2,
                  desplazamiento=0, dscp=0):
    """Construye una cabecera IPv4 REAL de 20 bytes. -> dict.

    El checksum se CALCULA (no se escribe): `valores["Checksum"]`.
    """
    b = bytearray(20)
    b[0] = 0x45                                   # version 4, IHL 5
    b[1] = int(dscp) & 0xFF
    b[2:4] = int(longitud).to_bytes(2, "big")
    b[4:6] = int(ident).to_bytes(2, "big")
    ff = ((int(banderas) & 0x7) << 13) | (int(desplazamiento) & 0x1FFF)
    b[6:8] = ff.to_bytes(2, "big")
    b[8] = int(ttl) & 0xFF
    b[9] = int(protocolo) & 0xFF
    b[10:12] = b"\x00\x00"                        # checksum a cero
    b[12:16] = ip_a_bytes(origen)
    b[16:20] = ip_a_bytes(destino)
    ck = checksum_ip(bytes(b))
    b[10:12] = ck.to_bytes(2, "big")
    nombres = {"Version": "4", "IHL": "5 (20 B)", "DSCP/ECN": str(dscp),
               "Longitud total": str(longitud), "Identificacion": hex(ident),
               "Banderas": "DF" if banderas == 2 else
               ("MF" if banderas == 1 else "-"),
               "Desplazamiento": str(desplazamiento), "TTL": str(ttl),
               "Protocolo": {6: "6 TCP", 17: "17 UDP", 1: "1 ICMP"}.get(
                   int(protocolo), str(protocolo)),
               "Checksum": "0x%04x" % ck,
               "Direccion origen": origen, "Direccion destino": destino}
    return {"bytes": bytes(b), "checksum": ck, "valores": nombres,
            "campos": CAMPOS_IPV4, "origen": origen, "destino": destino,
            "ttl": int(ttl)}


def verificar_checksum(cabecera_bytes):
    """0 = intacta. Cualquier otro valor = corrupta (la regla real)."""
    return checksum_ip(bytes(cabecera_bytes))


def fragmentar(carga_bytes, mtu=1500, cab=20):
    """Fragmentacion IPv4 REAL: offsets en unidades de 8 bytes. -> dict."""
    util = ((int(mtu) - int(cab)) // 8) * 8
    total, frags, off = int(carga_bytes), [], 0
    while off < total:
        trozo = min(util, total - off)
        frags.append({"offset_bytes": off, "offset_campo": off // 8,
                      "datos": trozo, "mf": 1 if off + trozo < total else 0,
                      "total": trozo + int(cab)})
        off += trozo
    return {"fragmentos": frags, "n": len(frags), "util": util,
            "carga": total, "mtu": int(mtu),
            "bytes_extra": (len(frags) - 1) * int(cab)}


def ttl_camino(ttl0=64, saltos=None, bucle=None):
    """El TTL bajando salto a salto. -> lista de (salto, nodo, ttl).

    Con `bucle=True` el camino se cicla (enrutamiento circular) hasta
    que el TTL llega a 0; sin bucle recorre `saltos` una vez.
    """
    nodos = list(saltos or ["R1", "R2", "R3", "R4"])
    ruta, ttl = [], int(ttl0)
    i = 0
    while ttl > 0 and len(ruta) < 200:
        n = nodos[i % len(nodos)]
        ttl -= 1
        ruta.append({"salto": len(ruta) + 1, "nodo": n, "ttl": ttl})
        if bucle is None and len(ruta) >= len(nodos):
            break
        i += 1
    return {"ruta": ruta, "saltos": len(ruta), "ttl_final": ttl,
            "muerto": ttl == 0}


# =====================================================================
# Modulo 2.2 — CIDR, subredes y prefijo mas largo
# =====================================================================
def mascara_bits(n):
    """La mascara de /n como entero de 32 bits."""
    n = int(n)
    return (0xFFFFFFFF << (32 - n)) & 0xFFFFFFFF if n else 0


def cidr(prefijo):
    """'192.168.10.0/26' -> dict con red, rango, broadcast y hosts."""
    ip, n = str(prefijo).split("/")
    n = int(n)
    m = mascara_bits(n)
    red = ip_a_entero(ip) & m
    bcast = red | (0xFFFFFFFF ^ m)
    hosts = max(0, 2 ** (32 - n) - 2)
    return {"prefijo": "%s/%d" % (entero_a_ip(red), n), "bits": n,
            "mascara": entero_a_ip(m), "red": entero_a_ip(red),
            "broadcast": entero_a_ip(bcast),
            "primero": entero_a_ip(red + 1) if hosts else entero_a_ip(red),
            "ultimo": entero_a_ip(bcast - 1) if hosts else entero_a_ip(bcast),
            "hosts": hosts, "direcciones": 2 ** (32 - n),
            "red_int": red, "mascara_int": m}


def en_prefijo(ip, prefijo):
    c = cidr(prefijo)
    return (ip_a_entero(ip) & c["mascara_int"]) == c["red_int"]


def prefijo_mas_largo(tabla, ip):
    """La regla que gobierna cada router. -> dict.

    `tabla` = [(prefijo, siguiente_salto), ...]. Devuelve TODAS las filas
    que coinciden y cual gana (la de prefijo mas largo).
    """
    coinciden = [(p, s, cidr(p)["bits"]) for p, s in tabla
                 if en_prefijo(ip, p)]
    coinciden.sort(key=lambda x: -x[2])
    gana = coinciden[0] if coinciden else None
    return {"ip": ip, "coinciden": coinciden,
            "elegida": gana[0] if gana else None,
            "siguiente": gana[1] if gana else None,
            "bits": gana[2] if gana else None,
            "n_coinciden": len(coinciden)}


def agregar_rutas(prefijos):
    """Pliega prefijos contiguos del mismo tamano. -> dict MEDIDO."""
    items = sorted((cidr(p) for p in prefijos), key=lambda c: c["red_int"])
    actual = [(c["red_int"], c["bits"]) for c in items]
    cambio = True
    while cambio:
        cambio = False
        salida, i = [], 0
        while i < len(actual):
            if i + 1 < len(actual):
                (r1, b1), (r2, b2) = actual[i], actual[i + 1]
                bloque = 2 ** (32 - b1)
                if b1 == b2 and r2 == r1 + bloque and r1 % (2 * bloque) == 0:
                    salida.append((r1, b1 - 1))
                    i += 2
                    cambio = True
                    continue
            salida.append(actual[i])
            i += 1
        actual = salida
    agregados = ["%s/%d" % (entero_a_ip(r), b) for r, b in actual]
    return {"entrada": list(prefijos), "agregados": agregados,
            "filas_antes": len(prefijos), "filas_despues": len(agregados),
            "ahorro": len(prefijos) - len(agregados)}


# =====================================================================
# Modulo 2.3 — IPv6
# =====================================================================
def espacio_direcciones(bits=32):
    """2^bits y su lectura humana. -> dict."""
    n = 2 ** int(bits)
    return {"bits": int(bits), "total": n,
            "exp10": math.log10(n),
            "por_persona": n / 8.1e9,
            "por_m2_tierra": n / 5.1e14}


def ipv6_expandir(dir6):
    """'2001:db8::1' -> los 8 grupos completos de 4 hex."""
    s = str(dir6)
    if "::" in s:
        izq, der = s.split("::", 1)
        a = [g for g in izq.split(":") if g]
        b = [g for g in der.split(":") if g]
        grupos = a + ["0"] * (8 - len(a) - len(b)) + b
    else:
        grupos = s.split(":")
    return [g.rjust(4, "0").lower() for g in grupos]


def ipv6_comprimir(dir6):
    """La regla del `::`: el hueco de ceros MAS LARGO (y solo uno)."""
    g = [x.lstrip("0") or "0" for x in ipv6_expandir(dir6)]
    mejor_i, mejor_n, i = -1, 0, 0
    while i < 8:
        if g[i] == "0":
            j = i
            while j < 8 and g[j] == "0":
                j += 1
            if j - i > mejor_n:
                mejor_i, mejor_n = i, j - i
            i = j
        else:
            i += 1
    if mejor_n < 2:
        return ":".join(g)
    izq, der = ":".join(g[:mejor_i]), ":".join(g[mejor_i + mejor_n:])
    return izq + "::" + der


def eui64(mac, prefijo="2001:db8:1:1"):
    """SLAAC: la mitad baja de la direccion sale de la MAC. -> dict."""
    b = bytearray(_mac_bytes(mac))
    universal = b[0] ^ 0x02
    trozos = [b[0], b[1], b[2], 0xFF, 0xFE, b[3], b[4], b[5]]
    trozos[0] = universal
    hexs = "".join("%02x" % x for x in trozos)
    baja = ":".join(hexs[i:i + 4] for i in range(0, 16, 4))
    completa = "%s:%s" % (prefijo, baja)
    return {"mac": mac, "interfaz": baja, "direccion": completa,
            "comprimida": ipv6_comprimir(completa),
            "bit_invertido": "0x%02x -> 0x%02x" % (b[0] ^ 0x02 ^ 0x02,
                                                   universal),
            "relleno": "ff:fe"}


CAMPOS_IPV6 = (("Version", 4), ("Clase de trafico", 8),
               ("Etiqueta de flujo", 20), ("Longitud de carga", 16),
               ("Siguiente cabecera", 8), ("Limite de saltos", 8),
               ("Direccion origen", 128), ("Direccion destino", 128))


# =====================================================================
# PIEZAS DE DIBUJO
# =====================================================================
def _hud(t, fs=15, color=C_EJE):
    return _texto_hud(str(t), font_size=fs, color=color)


class Paquete(_Anclada):
    """Capsula con campos rotulados. .campo(n) .valor(n) .iluminar(n)
    .con_valores(dict) GEMELA."""

    def __init__(self, campos, ancho=4.4, alto=0.72, fs=14,
                 color=C_PAQUETE, color_carga=None, **kwargs):
        super().__init__(**kwargs)
        self.campos_spec = [(str(n), float(w), str(v))
                            for n, w, v in campos]
        self.ancho, self.alto, self.fs = float(ancho), float(alto), int(fs)
        self.color = color
        self.color_carga = color_carga or C_CIFRA
        self._poner_ancla(ORIGIN)
        total = sum(w for _, w, _ in self.campos_spec)
        self.cajas, self.nombres, self.valores = VGroup(), VGroup(), VGroup()
        self._idx = {}
        x = -self.ancho / 2.0
        for k, (nom, w, val) in enumerate(self.campos_spec):
            ancho_k = self.ancho * w / total
            es_carga = nom.lower().startswith("carga")
            col = self.color_carga if es_carga else self.color
            caja = Rectangle(width=ancho_k, height=self.alto,
                             stroke_color=col, stroke_width=2.0,
                             fill_color=col,
                             fill_opacity=0.16 if es_carga else 0.07)
            caja.move_to(self._origen() + np.array(
                [x + ancho_k / 2.0, 0.0, 0.0]))
            nt = _hud(nom, self.fs - 3, C_EJE)
            if nt.width > ancho_k * 0.86:   # aire entre campos
                nt.scale(ancho_k * 0.86 / nt.width)
            nt.next_to(caja, UP, buff=0.10)
            vt = _hud(val, self.fs, col)
            if vt.width > ancho_k * 0.92:
                vt.scale(ancho_k * 0.92 / vt.width)
            vt.move_to(caja.get_center())
            self.cajas.add(caja)
            self.nombres.add(nt)
            self.valores.add(vt)
            self._idx[nom] = k
            x += ancho_k
        self.add(self.cajas, self.nombres, self.valores)
        self._iluminados = {}

    def campo(self, nombre):
        return self.cajas[self._idx[nombre]]

    def valor(self, nombre):
        return self.valores[self._idx[nombre]]

    def rotulo(self, nombre):
        return self.nombres[self._idx[nombre]]

    def iluminar(self, nombre, color=C_CIFRA):
        i = self._idx[nombre]
        self.cajas[i].set_stroke(color, width=3.4)
        self.valores[i].set_color(color)
        self.nombres[i].set_color(color)
        self._iluminados[nombre] = color
        return self

    def con_valores(self, nuevos, color=None):
        """Gemela con otros valores. CONSERVA lo iluminado: si no, el campo
        destacado se apaga a mitad del Transform (trampa de la 1.3)."""
        campos = [(n, w, str(nuevos.get(n, v)))
                  for n, w, v in self.campos_spec]
        o = Paquete(campos, self.ancho, self.alto, self.fs,
                    color or self.color, self.color_carga)
        for nombre, col in self._iluminados.items():
            o.iluminar(nombre, col)
        o.shift(self._origen() - o._origen())
        return o


def paquete(campos, ancho=4.4, alto=0.72, fs=14, color=C_PAQUETE,
            color_carga=None):
    """Ver `Paquete`. `campos` = [(nombre, peso, valor), ...]."""
    return Paquete(campos, ancho, alto, fs, color, color_carga)


class Cabecera(_Anclada):
    """Cabecera por filas de 32 bits. .campo(n) .con_valores() GEMELA."""

    def __init__(self, campos, valores=None, ancho=6.4, alto_fila=0.46,
                 fs=13, color=C_CAPA, bits_fila=32, **kwargs):
        super().__init__(**kwargs)
        self.campos_spec = [(str(n), int(b)) for n, b in campos]
        self.valores_spec = dict(valores or {})
        self.ancho, self.alto_fila = float(ancho), float(alto_fila)
        self.fs, self.color = int(fs), color
        self.bits_fila = int(bits_fila)
        self._poner_ancla(ORIGIN)
        self.cajas, self.nombres, self.textos = VGroup(), VGroup(), VGroup()
        self._idx = {}
        fila, usado = 0, 0
        for k, (nom, bits) in enumerate(self.campos_spec):
            if usado and usado + bits > self.bits_fila:
                fila += 1
                usado = 0
            trozo = min(bits, self.bits_fila)
            w = self.ancho * trozo / self.bits_fila
            x = -self.ancho / 2.0 + self.ancho * usado / self.bits_fila
            filas_alto = max(1, int(math.ceil(bits / self.bits_fila)))
            h = self.alto_fila * filas_alto
            caja = Rectangle(width=w, height=h, stroke_color=C_EJE,
                             stroke_width=1.4, fill_color=color,
                             fill_opacity=0.05)
            caja.move_to(self._origen() + np.array(
                [x + w / 2.0,
                 -self.alto_fila * fila - h / 2.0 + self.alto_fila / 2.0,
                 0.0]))
            val = self.valores_spec.get(nom)
            etq = _hud(nom, self.fs - 3, C_EJE)
            if etq.width > w * 0.92:
                etq.scale(w * 0.92 / etq.width)
            txt = _hud(str(val) if val is not None else "", self.fs, color)
            if val is not None:
                if txt.width > w * 0.92:
                    txt.scale(w * 0.92 / txt.width)
                etq.move_to(caja.get_center() + UP * h * 0.22)
                txt.move_to(caja.get_center() + DOWN * h * 0.20)
            else:
                etq.move_to(caja.get_center())
            self.cajas.add(caja)
            self.nombres.add(etq)
            self.textos.add(txt)
            self._idx[nom] = k
            usado += trozo
            if usado >= self.bits_fila or filas_alto > 1:
                fila += filas_alto
                usado = 0
        self.add(self.cajas, self.nombres, self.textos)
        self._iluminados = {}

    def campo(self, nombre):
        return self.cajas[self._idx[nombre]]

    def texto(self, nombre):
        return self.textos[self._idx[nombre]]

    def iluminar(self, nombre, color=C_CIFRA, rotulo=False):
        """Destaca un campo. `rotulo=True` tine tambien su nombre (por
        defecto no, para no cambiar el aspecto de las lecciones ya
        aprobadas)."""
        i = self._idx[nombre]
        self.cajas[i].set_stroke(color, width=3.0)
        self.cajas[i].set_fill(color, opacity=0.16)
        self.textos[i].set_color(color)
        if rotulo:
            self.nombres[i].set_color(color)
        self._iluminados[nombre] = (color, bool(rotulo))
        return self

    def con_valores(self, nuevos):
        """Gemela con otros valores, CONSERVANDO lo iluminado.

        Ojo: una cabecera que nace SIN valores tiene textos vacios (0
        glifos); el Transform a una con valores no es estructura identica.
        Nacer siempre con todos los valores puestos.
        """
        v = dict(self.valores_spec)
        v.update(nuevos)
        o = Cabecera(self.campos_spec, v, self.ancho, self.alto_fila,
                     self.fs, self.color, self.bits_fila)
        for nombre, (col, rot) in self._iluminados.items():
            o.iluminar(nombre, col, rot)
        o.shift(self._origen() - o._origen())
        return o


def cabecera(campos, valores=None, ancho=6.4, alto_fila=0.46, fs=13,
             color=C_CAPA, bits_fila=32):
    """Ver `Cabecera`. `campos` = [(nombre, bits), ...]."""
    return Cabecera(campos, valores, ancho, alto_fila, fs, color, bits_fila)


class Nodo(_Anclada):
    """Un aparato de la red. tipo: host|switch|router|servidor|satelite."""

    _FORMAS = ("host", "switch", "router", "servidor", "satelite", "nube")

    def __init__(self, tipo="host", etiqueta=None, tam=0.52, color=C_RED,
                 fs=14, **kwargs):
        super().__init__(**kwargs)
        self.tipo, self.tam, self.color = str(tipo), float(tam), color
        self._poner_ancla(ORIGIN)
        t, s = self.tipo, self.tam
        if t == "router":
            forma = Circle(radius=s * 0.62, color=color, stroke_width=2.6,
                           fill_color=color, fill_opacity=0.12)
        elif t == "switch":
            forma = Rectangle(width=s * 1.7, height=s * 0.78, color=color,
                              stroke_width=2.4, fill_color=color,
                              fill_opacity=0.10)
        elif t == "servidor":
            forma = Rectangle(width=s * 0.86, height=s * 1.5, color=color,
                              stroke_width=2.4, fill_color=color,
                              fill_opacity=0.10)
        elif t == "satelite":
            forma = Polygon(*[np.array(p) * s for p in
                              ((-0.9, 0.28, 0), (-0.32, 0.28, 0),
                               (-0.32, 0.52, 0), (0.32, 0.52, 0),
                               (0.32, 0.28, 0), (0.9, 0.28, 0),
                               (0.9, -0.28, 0), (0.32, -0.28, 0),
                               (0.32, -0.52, 0), (-0.32, -0.52, 0),
                               (-0.32, -0.28, 0), (-0.9, -0.28, 0))],
                            color=color, stroke_width=2.2,
                            fill_color=color, fill_opacity=0.10)
        elif t == "nube":
            forma = VGroup(*[Circle(radius=s * r, color=color,
                                    stroke_width=2.0, fill_color=color,
                                    fill_opacity=0.08).shift(
                                        np.array([dx, dy, 0]) * s)
                             for r, dx, dy in ((0.52, -0.55, 0.0),
                                               (0.68, 0.0, 0.12),
                                               (0.48, 0.58, -0.02))])
        else:                                     # host
            forma = VGroup(
                Rectangle(width=s * 1.25, height=s * 0.88, color=color,
                          stroke_width=2.4, fill_color=color,
                          fill_opacity=0.10),
                Line(np.array([-s * 0.42, -s * 0.62, 0]),
                     np.array([s * 0.42, -s * 0.62, 0]),
                     color=color, stroke_width=2.4))
        forma.move_to(self._origen())
        self.forma = forma
        self.add(forma)
        self.etiqueta = None
        if etiqueta:
            self.etiqueta = _hud(etiqueta, fs, C_EJE)
            self.etiqueta.next_to(forma, DOWN, buff=0.14)
            self.add(self.etiqueta)

    def centro(self):
        return self.forma.get_center()

    def resaltar(self, color=C_PAQUETE, grosor=3.4):
        self.forma.set_stroke(color, width=grosor)
        return self


def nodo(tipo="host", etiqueta=None, tam=0.52, color=C_RED, fs=14):
    """Ver `Nodo`."""
    return Nodo(tipo, etiqueta, tam, color, fs)


class Enlace(_Anclada):
    """Linea entre dos puntos con rotulo opcional. .punto_en(frac)."""

    def __init__(self, desde, hasta, etiqueta=None, color=C_RED,
                 grosor=2.6, fs=13, punteada=False, buff=0.30, **kwargs):
        super().__init__(**kwargs)
        a, b = np.array(desde, dtype=float), np.array(hasta, dtype=float)
        d = b - a
        n = np.linalg.norm(d)
        u = d / n if n else d
        self.a, self.b = a + u * buff, b - u * buff
        self._poner_ancla((self.a + self.b) / 2.0)
        cls = DashedLine if punteada else Line
        self.linea = cls(self.a, self.b, color=color, stroke_width=grosor)
        self.add(self.linea)
        self.etiqueta = None
        if etiqueta:
            perp = np.array([-u[1], u[0], 0.0])
            self.etiqueta = _hud(etiqueta, fs, C_EJE)
            self.etiqueta.move_to((self.a + self.b) / 2.0 + perp * 0.26)
            self.add(self.etiqueta)

    def punto_en(self, frac):
        return self.linea.point_from_proportion(
            float(min(max(frac, 0.0), 1.0)))

    def resaltar(self, color=C_PAQUETE, grosor=4.2):
        self.linea.set_stroke(color, width=grosor)
        return self


def enlace(desde, hasta, etiqueta=None, color=C_RED, grosor=2.6, fs=13,
           punteada=False, buff=0.30):
    """Ver `Enlace`."""
    return Enlace(desde, hasta, etiqueta, color, grosor, fs, punteada, buff)


class Topologia(_Anclada):
    """Grafo dibujado. .nodo(n) .enlace(a,b) .punto(n) .resaltar_camino()."""

    def __init__(self, posiciones, aristas, tipos=None, costos=True,
                 escala=1.0, tam=0.42, fs=13, color=C_RED, **kwargs):
        super().__init__(**kwargs)
        self.posiciones = {
            k: np.array((list(v) + [0.0, 0.0])[:3], dtype=float) *
            float(escala) for k, v in posiciones.items()}
        self.aristas = {}
        tipos = tipos or {}
        self._poner_ancla(ORIGIN)
        self.enlaces, self.nodos = VGroup(), VGroup()
        self._nod = {}
        for (a, b), costo in dict(aristas).items():
            e = Enlace(self._origen() + self.posiciones[a],
                       self._origen() + self.posiciones[b],
                       str(costo) if costos and costo is not None else None,
                       color, 2.4, fs)
            self.aristas[(a, b)] = e
            self.aristas[(b, a)] = e
            self.enlaces.add(e)
        for k, p in self.posiciones.items():
            n = Nodo(tipos.get(k, "router"), str(k), tam, color, fs)
            n.move_to(self._origen() + p)
            self._nod[k] = n
            self.nodos.add(n)
        self.add(self.enlaces, self.nodos)

    def nodo(self, k):
        return self._nod[k]

    def punto(self, k):
        return self._nod[k].centro()

    def enlace(self, a, b):
        return self.aristas[(a, b)]

    def etiquetas_a(self, direcciones, buff=0.14):
        """Recoloca los rotulos de nodo uno a uno.

        `Topologia` cuelga la etiqueta SIEMPRE debajo del nodo, y en un
        grafo denso las aristas que bajan la cruzan (la letra sale
        tachada). `direcciones` = {nodo: UP|DOWN|LEFT|RIGHT}.
        """
        for k, d in dict(direcciones).items():
            n = self._nod[k]
            if n.etiqueta is not None:
                n.etiqueta.next_to(n.forma, d, buff=buff)
        return self

    def tramo(self, a, b, desde=0.0, hasta=1.0):
        """Trayectoria ORIENTADA de `a` a `b`, recortable, para
        `MoveAlongPath`.

        `enlace(a, b)` devuelve la misma linea para (a, b) y (b, a),
        dibujada en el sentido en que se declaro la arista: animar sobre
        ella va al reves la mitad de las veces. Y parar en 1.0 monta la
        ficha encima del nodo: 0.66-0.74 es el sitio.
        """
        pa, pb = self.punto(a), self.punto(b)
        v = VMobject()
        v.set_points_as_corners([pa + (pb - pa) * float(desde),
                                 pa + (pb - pa) * float(hasta)])
        return v

    def camino(self, nombres):
        """La ruta como VMobject, lista para `MoveAlongPath`.

        `Topologia` sabia resaltar un camino pero no darlo como
        trayectoria; cada leccion lo reconstruia a mano.
        """
        v = VMobject()
        v.set_points_as_corners([self.punto(k) for k in nombres])
        return v

    def ocultar_etiquetas(self, opacidad=0.0):
        """Apaga los rotulos de arista: cualquier ficha que viaje SOBRE el
        cable los pisa (los rotulos van a +0.26 de la linea)."""
        for e in self.enlaces:
            if e.etiqueta is not None:
                e.etiqueta.set_opacity(opacidad)
        return self

    def resaltar_camino(self, camino, color=C_PAQUETE, grosor=4.4):
        for a, b in zip(camino[:-1], camino[1:]):
            self.aristas[(a, b)].resaltar(color, grosor)
        for k in camino:
            self._nod[k].resaltar(color)
        return self


def topologia(posiciones, aristas, tipos=None, costos=True, escala=1.0,
              tam=0.42, fs=13, color=C_RED):
    """Ver `Topologia`. `aristas` = {(a, b): costo}."""
    return Topologia(posiciones, aristas, tipos, costos, escala, tam, fs,
                     color)


class Cola(_Anclada):
    """Bufer de N ranuras. .ranura(i) .con_ocupacion(n) GEMELA."""

    def __init__(self, capacidad=8, ocupacion=0, lado=0.34, fs=13,
                 color=C_COLA, color_lleno=None, etiqueta=None, **kwargs):
        super().__init__(**kwargs)
        self.capacidad, self.ocupacion = int(capacidad), int(ocupacion)
        self.lado, self.fs, self.color = float(lado), int(fs), color
        self.color_lleno = color_lleno or C_PAQUETE
        self.etiqueta_txt = etiqueta
        self._poner_ancla(ORIGIN)
        self.ranuras = VGroup()
        n = self.capacidad
        for i in range(n):
            x = (i - (n - 1) / 2.0) * self.lado
            lleno = i < self.ocupacion
            col = self.color_lleno if lleno else C_EJE
            r = Square(self.lado * 0.92, stroke_color=col,
                       stroke_width=1.8, fill_color=col,
                       fill_opacity=0.55 if lleno else 0.0)
            r.move_to(self._origen() + np.array([x, 0.0, 0.0]))
            self.ranuras.add(r)
        self.marco = Rectangle(width=self.lado * n + 0.10,
                               height=self.lado * 1.10,
                               stroke_color=color, stroke_width=2.0)
        self.marco.move_to(self._origen())
        self.add(self.marco, self.ranuras)
        self.etiqueta = None
        if etiqueta:
            self.etiqueta = _hud(etiqueta, self.fs, C_EJE)
            self.etiqueta.next_to(self.marco, UP, buff=0.14)
            self.add(self.etiqueta)

    def ranura(self, i):
        return self.ranuras[i]

    def con_ocupacion(self, n, color_lleno=None):
        o = Cola(self.capacidad, n, self.lado, self.fs, self.color,
                 color_lleno or self.color_lleno, self.etiqueta_txt)
        o.shift(self._origen() - o._origen())
        return o


def cola(capacidad=8, ocupacion=0, lado=0.34, fs=13, color=C_COLA,
         color_lleno=None, etiqueta=None):
    """Ver `Cola`."""
    return Cola(capacidad, ocupacion, lado, fs, color, color_lleno,
                etiqueta)


class Pila(_Anclada):
    """Torre de capas. .capa(i) .rotulo(i) .con_encapsulado(k) GEMELA."""

    def __init__(self, capas=CAPAS_TCPIP, datos=100, encapsulado=0,
                 ancho=3.2, alto=0.62, fs=14, color=C_CAPA, **kwargs):
        super().__init__(**kwargs)
        self.capas = tuple(capas)
        self.datos, self.encapsulado = int(datos), int(encapsulado)
        self.ancho, self.alto, self.fs = float(ancho), float(alto), int(fs)
        self.color = color
        self._poner_ancla(ORIGIN)
        self.cajas, self.rotulos, self.tamanos = VGroup(), VGroup(), VGroup()
        info = encapsular(self.datos, self.capas)
        n = len(self.capas)
        for i, (nombre, proto, cab) in enumerate(self.capas):
            y = ((n - 1) / 2.0 - i) * (self.alto + 0.14)
            activa = i < self.encapsulado
            col = C_PAQUETE if activa else color
            caja = Rectangle(width=self.ancho, height=self.alto,
                             stroke_color=col, stroke_width=2.4,
                             fill_color=col,
                             fill_opacity=0.18 if activa else 0.06)
            caja.move_to(self._origen() + np.array([0.0, y, 0.0]))
            rot = _hud("%s  %s" % (nombre, proto), self.fs, col)
            if rot.width > self.ancho * 0.9:
                rot.scale(self.ancho * 0.9 / rot.width)
            rot.move_to(caja.get_center())
            tam = _hud("%d B" % info["pasos"][i]["tamano"], self.fs - 1,
                       C_CIFRA if activa else C_EJE)
            tam.next_to(caja, RIGHT, buff=0.18)
            self.cajas.add(caja)
            self.rotulos.add(rot)
            self.tamanos.add(tam)
        self.add(self.cajas, self.rotulos, self.tamanos)
        self.info = info

    def capa(self, i):
        return self.cajas[i]

    def rotulo(self, i):
        return self.rotulos[i]

    def tamano(self, i):
        return self.tamanos[i]

    def con_encapsulado(self, k):
        o = Pila(self.capas, self.datos, k, self.ancho, self.alto, self.fs,
                 self.color)
        o.shift(self._origen() - o._origen())
        return o


def pila(capas=CAPAS_TCPIP, datos=100, encapsulado=0, ancho=3.2, alto=0.62,
         fs=14, color=C_CAPA):
    """Ver `Pila`."""
    return Pila(capas, datos, encapsulado, ancho, alto, fs, color)


class Tabla(_Anclada):
    """Filas x columnas de texto HUD. .celda(i,j) .fila(i) .con_filas()."""

    def __init__(self, cabeceras, filas, anchos=None, alto=0.40, fs=14,
                 color=C_EJE, color_cab=C_CAPA, resaltar=None,
                 filas_max=None, vacio="-", resaltable=False, **kwargs):
        super().__init__(**kwargs)
        self.cabeceras = [str(c) for c in cabeceras]
        self.filas_max = int(filas_max) if filas_max else None
        self.vacio = str(vacio)
        # `resaltable`: reserva el rectangulo de resaltado en TODAS las
        # filas (invisible donde no toca) para que dos gemelas con distinto
        # `resaltar` tengan la misma estructura. Es opt-in porque los
        # rectangulos ensanchan el bounding box y moverian las tablas de
        # las lecciones que ya estan aprobadas.
        self.resaltable = bool(resaltable)
        filas = [[str(c) for c in f] for f in filas]
        if self.filas_max:
            # Una tabla que CRECE: siempre `filas_max` filas, las que aun no
            # existen rellenas con `vacio`. Sin esto, `con_filas` con otro
            # numero de filas deja de ser estructura identica y el Transform
            # rompe los glifos (trampa de la 1.3).
            fila_vacia = [self.vacio] * len(self.cabeceras)
            filas = (filas + [list(fila_vacia)
                              for _ in range(self.filas_max - len(filas))]
                     )[:self.filas_max]
        self.filas_spec = filas
        nc = len(self.cabeceras)
        self.anchos = list(anchos) if anchos else [1.6] * nc
        self.alto, self.fs = float(alto), int(fs)
        self.color, self.color_cab = color, color_cab
        self.resaltar_i = resaltar
        self._poner_ancla(ORIGIN)
        self.celdas, self.textos, self.lineas = VGroup(), VGroup(), VGroup()
        ancho_total = sum(self.anchos)
        nf = len(self.filas_spec)
        for j, cab in enumerate(self.cabeceras):
            x = -ancho_total / 2.0 + sum(self.anchos[:j]) + self.anchos[j] / 2.0
            t = _hud(cab, self.fs - 1, color_cab)
            if t.width > self.anchos[j] * 0.94:
                t.scale(self.anchos[j] * 0.94 / t.width)
            t.move_to(self._origen() + np.array(
                [x, (nf / 2.0) * self.alto + self.alto * 0.55, 0.0]))
            self.textos.add(t)
        sep = Line(self._origen() + np.array(
            [-ancho_total / 2.0, (nf / 2.0) * self.alto + self.alto * 0.15,
             0.0]),
            self._origen() + np.array(
            [ancho_total / 2.0, (nf / 2.0) * self.alto + self.alto * 0.15,
             0.0]), color=C_EJE, stroke_width=1.6)
        self.lineas.add(sep)
        self._celdas = {}
        for i, fila in enumerate(self.filas_spec):
            y = (nf / 2.0 - i - 0.5) * self.alto
            marcada = resaltar is not None and i == resaltar
            col = C_CIFRA if marcada else color
            if marcada or self.resaltable:
                fondo = Rectangle(width=ancho_total + 0.12, height=self.alto,
                                  stroke_width=0.0, fill_color=C_CIFRA,
                                  fill_opacity=0.12 if marcada else 0.0)
                fondo.move_to(self._origen() + np.array([0.0, y, 0.0]))
                self.celdas.add(fondo)
            for j, valor in enumerate(fila):
                x = (-ancho_total / 2.0 + sum(self.anchos[:j]) +
                     self.anchos[j] / 2.0)
                t = _hud(valor, self.fs, col)
                if t.width > self.anchos[j] * 0.94:
                    t.scale(self.anchos[j] * 0.94 / t.width)
                t.move_to(self._origen() + np.array([x, y, 0.0]))
                self._celdas[(i, j)] = t
                self.textos.add(t)
        self.add(self.lineas, self.celdas, self.textos)

    def celda(self, i, j):
        return self._celdas[(i, j)]

    def fila(self, i):
        return VGroup(*[self._celdas[(i, j)]
                        for j in range(len(self.cabeceras))])

    def con_filas(self, filas, resaltar=None):
        """Gemela con otras filas. Con `filas_max` puesto, la tabla puede
        CRECER conservando la estructura (Transform seguro)."""
        o = Tabla(self.cabeceras, filas, self.anchos, self.alto, self.fs,
                  self.color, self.color_cab, resaltar, self.filas_max,
                  self.vacio, self.resaltable)
        o.shift(self._origen() - o._origen())
        return o


def tabla(cabeceras, filas, anchos=None, alto=0.40, fs=14, color=C_EJE,
          color_cab=C_CAPA, resaltar=None, filas_max=None, vacio="-",
          resaltable=False):
    """Ver `Tabla`. `filas_max` reserva sitio para que la tabla crezca;
    `resaltable` reserva el resaltado en todas las filas (gemelas seguras
    cuando el resaltado se mueve de fila)."""
    return Tabla(cabeceras, filas, anchos, alto, fs, color, color_cab,
                 resaltar, filas_max, vacio, resaltable)


class Reloj(_Anclada):
    """Contador de milisegundos en cian. .con_ms(x) GEMELA."""

    def __init__(self, ms=0.0, etiqueta="RTT", dec=1, fs=22,
                 color=C_CIFRA, **kwargs):
        super().__init__(**kwargs)
        self.ms, self.etiqueta_txt = float(ms), str(etiqueta)
        self.dec, self.fs, self.color = int(dec), int(fs), color
        self._poner_ancla(ORIGIN)
        self.texto = _hud("%s %s ms" % (self.etiqueta_txt,
                                        fmt(self.ms, self.dec)),
                          self.fs, color)
        self.texto.move_to(self._origen())
        self.add(self.texto)

    def con_ms(self, ms):
        o = Reloj(ms, self.etiqueta_txt, self.dec, self.fs, self.color)
        o.shift(self._origen() - o._origen())
        return o


def reloj(ms=0.0, etiqueta="RTT", dec=1, fs=22, color=C_CIFRA):
    """Ver `Reloj`."""
    return Reloj(ms, etiqueta, dec, fs, color)


class BarraBits(_Anclada):
    """N bits con una raya movil red|host. .con_prefijo(n) GEMELA."""

    def __init__(self, valor="192.168.10.37", prefijo=24, bits=32,
                 ancho=6.6, alto=0.34, fs=11, color_red=C_CAPA,
                 color_host=C_PAQUETE, mostrar_texto=True, **kwargs):
        super().__init__(**kwargs)
        self.valor, self.prefijo, self.bits = valor, int(prefijo), int(bits)
        self.ancho, self.alto, self.fs = float(ancho), float(alto), int(fs)
        self.color_red, self.color_host = color_red, color_host
        self.mostrar_texto = bool(mostrar_texto)
        self._poner_ancla(ORIGIN)
        if self.bits == 32 and isinstance(valor, str) and "." in valor:
            cadena = "".join(format(int(o), "08b")
                             for o in valor.split("."))
        else:
            cadena = str(valor).rjust(self.bits, "0")[:self.bits]
        self.cadena = cadena
        w = self.ancho / self.bits
        self.celdas, self.digitos = VGroup(), VGroup()
        for i, b in enumerate(cadena):
            col = color_red if i < self.prefijo else color_host
            x = -self.ancho / 2.0 + w * (i + 0.5)
            c = Rectangle(width=w, height=self.alto, stroke_color=col,
                          stroke_width=0.9, fill_color=col,
                          fill_opacity=0.20 if i < self.prefijo else 0.10)
            c.move_to(self._origen() + np.array([x, 0.0, 0.0]))
            self.celdas.add(c)
            if self.bits <= 40:
                d = _hud(b, self.fs, col)
                if d.width > w * 0.8:
                    d.scale(w * 0.8 / d.width)
                d.move_to(c.get_center())
                self.digitos.add(d)
        self.raya = Line(
            self._origen() + np.array(
                [-self.ancho / 2.0 + w * self.prefijo, self.alto * 0.95, 0]),
            self._origen() + np.array(
                [-self.ancho / 2.0 + w * self.prefijo, -self.alto * 0.95, 0]),
            color=C_CIFRA, stroke_width=3.2)
        self.add(self.celdas, self.digitos, self.raya)
        self.rotulo = None
        if self.mostrar_texto:
            self.rotulo = _hud("%s/%d" % (valor, self.prefijo), self.fs + 5,
                               C_CIFRA)
            self.rotulo.next_to(self.celdas, DOWN, buff=0.22)
            self.add(self.rotulo)

    def celda(self, i):
        return self.celdas[i]

    def parte_red(self):
        return VGroup(*self.celdas[:self.prefijo])

    def parte_host(self):
        return VGroup(*self.celdas[self.prefijo:])

    def con_prefijo(self, n, valor=None):
        o = BarraBits(valor or self.valor, n, self.bits, self.ancho,
                      self.alto, self.fs, self.color_red, self.color_host,
                      self.mostrar_texto)
        o.shift(self._origen() - o._origen())
        return o


def barra_bits(valor="192.168.10.37", prefijo=24, bits=32, ancho=6.6,
               alto=0.34, fs=11, color_red=C_CAPA, color_host=C_PAQUETE,
               mostrar_texto=True):
    """Ver `BarraBits`."""
    return BarraBits(valor, prefijo, bits, ancho, alto, fs, color_red,
                     color_host, mostrar_texto)


class Ficha(_Anclada):
    """Token cuadrado para el datagrama cuando NO toca abrir la cabecera.
    .con_texto(t) GEMELA."""

    def __init__(self, texto="", lado=0.50, fs=15, color=C_PAQUETE,
                 **kwargs):
        super().__init__(**kwargs)
        self.texto_str, self.lado = str(texto), float(lado)
        self.fs, self.color = int(fs), color
        self._poner_ancla(ORIGIN)
        self.caja = Square(self.lado, stroke_color=color, stroke_width=2.4,
                           fill_color=color, fill_opacity=0.20)
        self.caja.move_to(self._origen())
        self.texto = _hud(self.texto_str, self.fs, color)
        if self.texto.width > self.lado * 0.88:
            self.texto.scale(self.lado * 0.88 / self.texto.width)
        self.texto.move_to(self.caja.get_center())
        self.add(self.caja, self.texto)

    def con_texto(self, texto, color=None):
        o = Ficha(texto, self.lado, self.fs, color or self.color)
        o.shift(self._origen() - o._origen())
        return o


def ficha(texto="", lado=0.50, fs=15, color=C_PAQUETE):
    """Ver `Ficha`."""
    return Ficha(texto, lado, fs, color)


class Bus(_Anclada):
    """Cable compartido con estaciones colgando. .estacion(i) .punto(i)
    .bajada(i). Para CSMA/CD, acceso al medio y cualquier medio compartido."""

    def __init__(self, n=3, etiquetas=None, ancho=6.2, caida=0.85,
                 tam=0.42, fs=13, color=C_RED, **kwargs):
        super().__init__(**kwargs)
        self.n, self.ancho, self.caida = int(n), float(ancho), float(caida)
        self._poner_ancla(ORIGIN)
        o = self._origen()
        self.cable = Line(o + np.array([-self.ancho / 2.0, 0.0, 0.0]),
                          o + np.array([self.ancho / 2.0, 0.0, 0.0]),
                          color=color, stroke_width=3.2)
        self.estaciones, self.bajadas = VGroup(), VGroup()
        etiquetas = list(etiquetas or ["E%d" % i for i in range(self.n)])
        for i in range(self.n):
            x = self._x(i)
            arriba = o + np.array([x, 0.0, 0.0])
            e = Nodo("host", etiquetas[i], tam, color, fs)
            e.move_to(o + np.array([x, -self.caida, 0.0]))
            b = DashedLine(arriba, e.forma.get_top(), color=C_EJE,
                           stroke_width=1.4, dash_length=0.07)
            self.estaciones.add(e)
            self.bajadas.add(b)
        self.add(self.cable, self.bajadas, self.estaciones)

    def _x(self, i):
        if self.n == 1:
            return 0.0
        return (-self.ancho / 2.0 * 0.82 +
                self.ancho * 0.82 * i / (self.n - 1))

    def estacion(self, i):
        return self.estaciones[i]

    def punto(self, i):
        """El punto del CABLE sobre la estacion i."""
        return self._origen() + np.array([self._x(i), 0.0, 0.0])

    def bajada(self, i):
        return self.bajadas[i]


def bus(n=3, etiquetas=None, ancho=6.2, caida=0.85, tam=0.42, fs=13,
        color=C_RED):
    """Ver `Bus`."""
    return Bus(n, etiquetas, ancho, caida, tam, fs, color)


class Ranuras(_Anclada):
    """Regla de ranuras de tiempo numeradas. .ranura(i) .con_colores(cs)
    GEMELA. Para CSMA/CD, TDMA y cualquier eje de tiempo discreto."""

    def __init__(self, n=8, colores=None, lado=0.46, fs=13, etiqueta=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.n, self.lado, self.fs = int(n), float(lado), int(fs)
        self.colores = list(colores or [None] * self.n)
        self.etiqueta_txt = etiqueta
        self._poner_ancla(ORIGIN)
        self.cajas, self.numeros = VGroup(), VGroup()
        for i in range(self.n):
            x = (i - (self.n - 1) / 2.0) * (self.lado + 0.06)
            col = self.colores[i] if i < len(self.colores) else None
            c = Square(self.lado, stroke_color=col or C_EJE,
                       stroke_width=2.0, fill_color=col or C_EJE,
                       fill_opacity=0.35 if col else 0.0)
            c.move_to(self._origen() + np.array([x, 0.0, 0.0]))
            t = _hud(str(i), self.fs - 2, C_EJE)
            t.next_to(c, DOWN, buff=0.10)
            self.cajas.add(c)
            self.numeros.add(t)
        self.add(self.cajas, self.numeros)
        self.etiqueta = None
        if etiqueta:
            self.etiqueta = _hud(etiqueta, self.fs, C_EJE)
            self.etiqueta.next_to(self.cajas, LEFT, buff=0.30)
            self.add(self.etiqueta)

    def ranura(self, i):
        return self.cajas[i]

    def con_colores(self, colores):
        o = Ranuras(self.n, colores, self.lado, self.fs, self.etiqueta_txt)
        o.shift(self._origen() - o._origen())
        return o


def ranuras(n=8, colores=None, lado=0.46, fs=13, etiqueta=None):
    """Ver `Ranuras`."""
    return Ranuras(n, colores, lado, fs, etiqueta)


def cabecera_ipv6(origen="2001:db8:1:1::7", destino="2001:db8:2:2::20",
                  carga=1440, siguiente=6, saltos=64, clase=0, flujo=0x1a2b3):
    """Los valores de una cabecera IPv6 (40 B fijos). -> dict.

    Analogo a `cabecera_ipv4`, pero IPv6 no lleva checksum ni longitud de
    cabecera: por eso aqui no hay nada que calcular, solo que declarar.
    """
    valores = {"Version": "6", "Clase de trafico": str(clase),
               "Etiqueta de flujo": "0x%05x" % flujo,
               "Longitud de carga": str(carga),
               "Siguiente cabecera": {6: "6 TCP", 17: "17 UDP",
                                      58: "58 ICMPv6"}.get(int(siguiente),
                                                           str(siguiente)),
               "Limite de saltos": str(saltos),
               "Direccion origen": origen, "Direccion destino": destino}
    return {"valores": valores, "campos": CAMPOS_IPV6, "bytes": 40,
            "origen": origen, "destino": destino,
            "sin_checksum": True, "sin_fragmentacion_en_transito": True}


# =====================================================================
# Modulo 3 — Encontrar el camino (ruteo)
# =====================================================================
def grafo_de(aristas):
    """{(a, b): costo} -> {nodo: {vecino: costo}} (no dirigido)."""
    g = {}
    for (a, b), c in dict(aristas).items():
        g.setdefault(a, {})[b] = float(c)
        g.setdefault(b, {})[a] = float(c)
    return g


def bellman_ford(aristas, destino, horizonte_dividido=False, max_rondas=20):
    """Vector distancia DISTRIBUIDO: cada nodo solo sabe de sus vecinos.

    Devuelve la historia ronda a ronda de las tablas {nodo: (costo,
    siguiente)} — lo que se dibuja en pantalla. `horizonte_dividido` no
    anuncia una ruta al vecino por el que se sale.
    """
    g = grafo_de(aristas)
    INF = float("inf")
    tabla = {n: (0.0, n) if n == destino else (INF, None) for n in g}
    historia = [dict(tabla)]
    for _ in range(int(max_rondas)):
        nueva = dict(tabla)
        for n in g:
            if n == destino:
                continue
            mejor, por = INF, None
            for v, c in g[n].items():
                cv, sig = tabla[v]
                if horizonte_dividido and sig == n:
                    continue          # no le devuelvas el rumor a su fuente
                if cv + c < mejor:
                    mejor, por = cv + c, v
            nueva[n] = (mejor, por)
        if nueva == tabla:
            break
        tabla = nueva
        historia.append(dict(tabla))
    return {"historia": historia, "tabla": tabla, "rondas": len(historia) - 1,
            "destino": destino, "nodos": sorted(g)}


def conteo_al_infinito(aristas, destino, corte, max_rondas=12,
                       horizonte_dividido=False, infinito=16):
    """El patologico de verdad: se corta el enlace que sostenia al destino y
    los rumores inflan el costo de uno en uno.

    Para que el conteo ocurra, `corte` tiene que ser el enlace que deja al
    destino inalcanzable (si queda otro camino, la red converge y no hay
    nada que contar). `infinito` es el tope de RIP: 16 saltos = "no llego".
    Devuelve la secuencia MEDIDA de costos por nodo y por ronda.
    """
    base = bellman_ford(aristas, destino, horizonte_dividido)
    restantes = {k: v for k, v in dict(aristas).items()
                 if set(k) != set(corte)}
    g = grafo_de(restantes)
    for n in grafo_de(aristas):
        g.setdefault(n, {})
    tabla = {}
    for n in g:
        costo, sig = base["tabla"].get(n, (float("inf"), None))
        # una ruta cuyo siguiente salto ya no es vecino murio con el enlace
        if n != destino and (sig is None or sig not in g[n]):
            tabla[n] = (float(infinito), None)
        else:
            tabla[n] = (costo, sig)
    tabla[destino] = (0.0, destino)
    huerfano = corte[0] if corte[1] == destino else corte[1]
    historia = [dict(tabla)]
    series = {n: [tabla[n][0]] for n in g}
    alcanzable = destino in g and bool(g[destino])
    for _ in range(int(max_rondas)):
        nueva = dict(tabla)
        for n in g:
            if n == destino:
                continue
            mejor, por = float(infinito), None
            for v, c in g[n].items():
                cv, sig = tabla[v]
                if horizonte_dividido and sig == n:
                    continue
                if cv + c < mejor:
                    mejor, por = cv + c, v
            nueva[n] = (min(mejor, float(infinito)), por)
        tabla = nueva
        historia.append(dict(tabla))
        for n in g:
            series[n].append(tabla[n][0])
        if all(v[0] >= infinito for k, v in tabla.items() if k != destino) \
                and not alcanzable:
            break
    subidas = {n: sum(1 for a, b in zip(s[:-1], s[1:]) if b > a)
               for n, s in series.items()}
    # `rondas` es cuantas se simularon; la HONESTA es en cual dejo de
    # cambiar nada. Cuando el destino sigue alcanzable por otro camino la
    # red converge antes de `max_rondas` y citar el tope seria mentir.
    estable = len(historia) - 1
    for i in range(len(historia) - 1):
        if historia[i] == historia[i + 1]:
            estable = i
            break
    return {"historia": historia, "series": series, "corte": tuple(corte),
            "destino": destino, "huerfano": huerfano,
            "rondas": len(historia) - 1, "rondas_estable": estable,
            "infinito": int(infinito), "subidas": subidas,
            "cuenta": max(subidas.values()) if subidas else 0,
            "alcanzable": alcanzable}


def dijkstra(aristas, origen):
    """Estado del enlace: el algoritmo REAL, con el ORDEN de fijacion y las
    distancias tentativas paso a paso (lo que se anima)."""
    g = grafo_de(aristas)
    INF = float("inf")
    dist = {n: (0.0 if n == origen else INF) for n in g}
    previo, fijados, pasos = {origen: None}, [], []
    pendientes = set(g)
    while pendientes:
        n = min(pendientes, key=lambda x: dist[x])
        if dist[n] == INF:
            break
        pendientes.discard(n)
        fijados.append(n)
        bajaron = {}
        for v, c in g[n].items():
            if v in pendientes and dist[n] + c < dist[v]:
                dist[v] = dist[n] + c
                previo[v] = n
                bajaron[v] = dist[v]
        pasos.append({"fija": n, "coste": dist[n], "bajaron": bajaron,
                      "tentativas": dict(dist)})
    arbol = [(previo[n], n) for n in g if previo.get(n) is not None]
    return {"dist": dist, "previo": previo, "orden": fijados, "pasos": pasos,
            "arbol": arbol, "origen": origen}


def camino_dijkstra(res, destino):
    """La ruta origen->destino que sale del arbol de `dijkstra`."""
    ruta, n = [], destino
    while n is not None:
        ruta.append(n)
        n = res["previo"].get(n)
    return list(reversed(ruta))


def inundacion(aristas, origen):
    """El anuncio de estado de enlace se propaga. -> rondas y mensajes
    CONTADOS hasta que todos tienen la misma base de datos."""
    g = grafo_de(aristas)
    tienen, frontera, rondas, mensajes = {origen}, {origen}, [], 0
    while frontera:
        nueva, envios = set(), 0
        for n in frontera:
            for v in g[n]:
                envios += 1                     # se envia aunque ya lo tenga
                if v not in tienen:
                    nueva.add(v)
        mensajes += envios
        tienen |= nueva
        rondas.append({"ronda": len(rondas) + 1, "nuevos": sorted(nueva),
                       "tienen": sorted(tienen), "mensajes": envios})
        frontera = nueva
    return {"rondas": rondas, "n_rondas": len(rondas), "mensajes": mensajes,
            "nodos": len(g), "todos": len(tienen) == len(g)}


def bgp_mejor_ruta(rutas):
    """El proceso de decision de BGP, en su orden REAL (los tres primeros
    criterios, que son los que deciden en la practica).

    `rutas` = [{"vecino":, "as_path":[...], "local_pref":, "med":}, ...]
    Devuelve la elegida y POR QUE criterio gano.
    """
    rutas = [dict(r) for r in rutas]
    criterios = [("local-pref mas alta", lambda r: -r.get("local_pref", 100)),
                 ("AS-path mas corto", lambda r: len(r["as_path"])),
                 ("MED mas bajo", lambda r: r.get("med", 0))]
    quedan = list(rutas)
    razon = "unica ruta"
    for nombre, clave in criterios:
        if len(quedan) == 1:
            break
        mejor = min(clave(r) for r in quedan)
        filtradas = [r for r in quedan if clave(r) == mejor]
        if len(filtradas) < len(quedan):
            razon = nombre
            quedan = filtradas
    return {"elegida": quedan[0], "razon": razon, "rutas": rutas,
            "descartadas": [r for r in rutas if r is not quedan[0]]}


def secuestro_bgp(aristas_as, origen_legitimo, atacante, prefijo="203.0.113.0/24",
                  mas_especifico=True):
    """Un AS anuncia un prefijo que no es suyo. -> ASes envenenados CONTADOS.

    Modelo de vector de caminos: cada AS se queda con el anuncio de AS-path
    mas corto; un prefijo MAS ESPECIFICO gana siempre (longest prefix match,
    el mismo del modulo 2) sin importar el camino.
    """
    g = grafo_de(aristas_as)

    def propagar(origen):
        dist, orden = {origen: 0}, [origen]
        i = 0
        caminos = {origen: [origen]}
        while i < len(orden):
            n = orden[i]
            i += 1
            for v in g[n]:
                if v not in dist:
                    dist[v] = dist[n] + 1
                    caminos[v] = caminos[n] + [v]
                    orden.append(v)
        return dist, caminos

    d_leg, c_leg = propagar(origen_legitimo)
    d_ata, c_ata = propagar(atacante)
    envenenados, fieles = [], []
    for n in sorted(g):
        if n in (origen_legitimo, atacante):
            continue
        gana_atacante = mas_especifico or d_ata.get(n, 1e9) < d_leg.get(n, 1e9)
        (envenenados if gana_atacante else fieles).append(n)
    return {"prefijo": prefijo, "legitimo": origen_legitimo,
            "atacante": atacante, "envenenados": envenenados,
            "fieles": fieles, "n_envenenados": len(envenenados),
            "n_total": len(g) - 2,
            "pct": 100.0 * len(envenenados) / max(1, len(g) - 2),
            "camino_legitimo": c_leg, "camino_atacante": c_ata,
            "mas_especifico": bool(mas_especifico)}


# =====================================================================
# Modulo 4 — La entrega confiable (transporte)
# =====================================================================
def demux(paquetes, sockets):
    """La 4-tupla decide a que socket va cada paquete. -> lista de pasos.

    `paquetes` = [{"ip_o":, "pto_o":, "ip_d":, "pto_d":}, ...]
    `sockets`  = {(ip_d, pto_d): "nombre del programa"} (escucha pasiva)
    """
    pasos = []
    for p in paquetes:
        clave = (p["ip_d"], p["pto_d"])
        pasos.append({"paquete": dict(p), "socket": sockets.get(clave),
                      "tupla": (p["ip_o"], p["pto_o"], p["ip_d"], p["pto_d"]),
                      "entregado": clave in sockets})
    return {"pasos": pasos, "entregados": sum(1 for x in pasos
                                              if x["entregado"]),
            "total": len(pasos)}


def handshake_tcp(isn_cliente=1000, isn_servidor=5000, rtt_ms=40.0):
    """Los tres mensajes REALES, con sus numeros y el RTT acumulado."""
    mitad = float(rtt_ms) / 2.0
    ev = [
        {"t_ms": 0.0, "de": "cliente", "a": "servidor", "flags": "SYN",
         "seq": isn_cliente, "ack": None, "estado_c": "SYN-SENT",
         "estado_s": "LISTEN"},
        {"t_ms": mitad, "de": "servidor", "a": "cliente", "flags": "SYN-ACK",
         "seq": isn_servidor, "ack": isn_cliente + 1,
         "estado_c": "SYN-SENT", "estado_s": "SYN-RECEIVED"},
        {"t_ms": 2 * mitad, "de": "cliente", "a": "servidor", "flags": "ACK",
         "seq": isn_cliente + 1, "ack": isn_servidor + 1,
         "estado_c": "ESTABLISHED", "estado_s": "SYN-RECEIVED"},
        {"t_ms": 3 * mitad, "de": "cliente", "a": "servidor", "flags": "datos",
         "seq": isn_cliente + 1, "ack": isn_servidor + 1,
         "estado_c": "ESTABLISHED", "estado_s": "ESTABLISHED"},
    ]
    return {"eventos": ev, "rtt_ms": float(rtt_ms),
            "antes_del_primer_byte_ms": 2 * mitad, "viajes": 1.5}


def bdp(mbps, rtt_ms):
    """Producto ancho de banda x retardo: los bytes que caben EN VUELO."""
    bits = float(mbps) * 1e6 * float(rtt_ms) / 1000.0
    return {"bits": bits, "bytes": bits / 8.0, "kb": bits / 8.0 / 1024.0,
            "mbps": float(mbps), "rtt_ms": float(rtt_ms),
            "segmentos_1460": bits / 8.0 / 1460.0}


def ventana(w_segmentos, rtt_ms=40.0, tam_seg=1460, capacidad_mbps=100.0):
    """Throughput MEDIDO de una ventana de W segmentos. -> dict.

    Con W segmentos en vuelo por RTT, el emisor no puede pasar de
    W*tam/RTT — por mucho ancho de banda que haya contratado.
    """
    por_rtt = float(w_segmentos) * float(tam_seg) * 8.0
    mbps = por_rtt / (float(rtt_ms) / 1000.0) / 1e6
    tope = min(mbps, float(capacidad_mbps))
    return {"w": int(w_segmentos), "mbps": mbps, "mbps_real": tope,
            "pct_capacidad": 100.0 * tope / float(capacidad_mbps),
            "limitado_por": "la ventana" if mbps < capacidad_mbps
            else "el enlace"}


def rtt_jacobson(muestras, alfa=0.125, beta=0.25, k=4.0):
    """El estimador REAL de TCP (RFC 6298): SRTT, RTTVAR y RTO paso a paso."""
    m = [float(x) for x in muestras]
    srtt = m[0]
    rttvar = m[0] / 2.0
    pasos = [{"muestra": m[0], "srtt": srtt, "rttvar": rttvar,
              "rto": srtt + k * rttvar}]
    for x in m[1:]:
        rttvar = (1 - beta) * rttvar + beta * abs(srtt - x)
        srtt = (1 - alfa) * srtt + alfa * x
        pasos.append({"muestra": x, "srtt": srtt, "rttvar": rttvar,
                      "rto": srtt + k * rttvar})
    return {"pasos": pasos, "srtt": srtt, "rttvar": rttvar,
            "rto": srtt + k * rttvar,
            "margen": (srtt + k * rttvar) - srtt}


def arranque_lento(ssthresh=16, cwnd0=1, rtts=10):
    """cwnd duplicandose cada RTT hasta el umbral, luego lineal."""
    cwnd, traza, fase = float(cwnd0), [], []
    for r in range(int(rtts)):
        traza.append(cwnd)
        fase.append("exponencial" if cwnd < ssthresh else "lineal")
        cwnd = cwnd * 2.0 if cwnd < ssthresh else cwnd + 1.0
    return {"traza": traza, "fase": fase, "ssthresh": float(ssthresh),
            "rtts_hasta_umbral": sum(1 for f in fase if f == "exponencial")}


def aimd(rtts=60, ssthresh0=32, perdidas=(18, 34, 50), cwnd_max=None):
    """La sierra de TCP Reno: +1 por RTT, /2 al perder. Traza MEDIDA."""
    perdidas = set(int(p) for p in perdidas)
    cwnd, ssthresh = 1.0, float(ssthresh0)
    traza, eventos = [], []
    for r in range(int(rtts)):
        traza.append(cwnd)
        if r in perdidas:
            ssthresh = max(2.0, cwnd / 2.0)
            cwnd = ssthresh
            eventos.append({"rtt": r, "tipo": "perdida", "cwnd_nuevo": cwnd})
        elif cwnd < ssthresh:
            cwnd *= 2.0
        else:
            cwnd += 1.0
        if cwnd_max:
            cwnd = min(cwnd, float(cwnd_max))
    return {"traza": traza, "eventos": eventos, "media": sum(traza) / len(traza),
            "pico": max(traza), "ssthresh0": float(ssthresh0),
            "perdidas": sorted(perdidas)}


def cubic(rtts=60, w_max=32.0, c=0.4, beta=0.7, perdidas=(18, 34, 50),
          rtt_s=0.04):
    """CUBIC (el de Linux): la cubica que se acerca despacio al maximo y
    sondea rapido al pasarlo. W(t) = C(t-K)^3 + W_max."""
    perdidas = set(int(p) for p in perdidas)
    traza, eventos = [], []
    w_ult, t_perdida = float(w_max), 0.0
    cwnd = float(w_max) * beta
    for r in range(int(rtts)):
        traza.append(cwnd)
        if r in perdidas:
            w_ult = cwnd
            cwnd = cwnd * beta
            t_perdida = r
            eventos.append({"rtt": r, "tipo": "perdida", "cwnd_nuevo": cwnd})
        else:
            t = (r - t_perdida) * rtt_s
            k = (w_ult * (1 - beta) / c) ** (1.0 / 3.0)
            cwnd = max(1.0, c * (t - k) ** 3 + w_ult)
    return {"traza": traza, "eventos": eventos,
            "media": sum(traza) / len(traza), "pico": max(traza),
            "w_max": float(w_max), "beta": float(beta)}


def recuperacion_tras_perdida(w_max=342.0, rtt_ms=40.0, beta=0.7, c=0.4):
    """Cuanto tarda cada algoritmo en volver a llenar el tubo tras una
    perdida. -> dict MEDIDO.

    Es LA diferencia entre Reno y CUBIC, y no se ve en la media de una
    sierra corta: Reno sube +1 segmento por RTT, asi que su recuperacion
    depende del RTT; la cubica de CUBIC depende del TIEMPO, no del RTT.
    """
    w_max = float(w_max)
    caida_reno = w_max / 2.0
    rtts_reno = w_max - caida_reno                 # +1 por RTT
    s_reno = rtts_reno * float(rtt_ms) / 1000.0
    s_cubic = (w_max * (1.0 - beta) / c) ** (1.0 / 3.0)   # la K de CUBIC
    return {"w_max": w_max, "rtt_ms": float(rtt_ms),
            "reno_rtts": rtts_reno, "reno_s": s_reno,
            "cubic_s": s_cubic, "cubic_rtts": s_cubic / (rtt_ms / 1000.0),
            "veces": s_reno / s_cubic if s_cubic else float("nan"),
            "caida_reno": caida_reno, "caida_cubic": w_max * beta}


def colapso_congestion(cargas=None, capacidad=1.0, k=2.5):
    """El colapso de 1986: al pasar de la capacidad, el trabajo UTIL cae en
    vez de estancarse (cada perdida se retransmite y empuja mas)."""
    if cargas is None:
        cargas = [0.2 * i for i in range(1, 16)]
    util = []
    for x in float(capacidad) and cargas:
        x = float(x)
        if x <= capacidad:
            util.append(x)
        else:
            exceso = x - capacidad
            util.append(max(0.05, capacidad * math.exp(-k * exceso)))
    return {"carga": [float(x) for x in cargas], "util": util,
            "capacidad": float(capacidad),
            "util_max": max(util), "util_final": util[-1],
            "caida_pct": 100.0 * (1.0 - util[-1] / max(util))}


class Escalera(_Anclada):
    """Diagrama de tiempo: actores en vertical, el tiempo hacia ABAJO.

    .actor(i) .linea_vida(i) .flecha(k) .rotulo(k) .marca_tiempo(k)
    Se construye con todos los eventos y se revelan uno a uno con
    `Create(esc.flecha(k))`, que es como se anima en los clips.
    """

    def __init__(self, actores, eventos, ancho=6.0, alto=3.4, fs=15,
                 color=C_RED, color_msg=C_PAQUETE, mostrar_tiempo=True,
                 **kwargs):
        super().__init__(**kwargs)
        self.actores_txt = [str(a) for a in actores]
        self.eventos = [dict(e) for e in eventos]
        self.ancho, self.alto, self.fs = float(ancho), float(alto), int(fs)
        self._poner_ancla(ORIGIN)
        o = self._origen()
        n = len(self.actores_txt)
        self._xs = [(-self.ancho / 2.0 + self.ancho * i / max(1, n - 1))
                    for i in range(n)]
        self.actores, self.vidas = VGroup(), VGroup()
        for i, nombre in enumerate(self.actores_txt):
            t = _hud(nombre, self.fs, color)
            t.move_to(o + np.array([self._xs[i], self.alto / 2.0 + 0.30, 0]))
            v = DashedLine(o + np.array([self._xs[i], self.alto / 2.0, 0]),
                           o + np.array([self._xs[i], -self.alto / 2.0, 0]),
                           color=C_EJE, stroke_width=1.4, dash_length=0.09)
            self.actores.add(t)
            self.vidas.add(v)
        self.flechas, self.rotulos, self.tiempos = VGroup(), VGroup(), VGroup()
        m = max(1, len(self.eventos) - 1)
        for k, e in enumerate(self.eventos):
            i = self.actores_txt.index(str(e["de"]))
            j = self.actores_txt.index(str(e["a"]))
            y = self.alto / 2.0 - (k + 0.7) * self.alto / (m + 1.2)
            col = e.get("color", color_msg)
            f = Arrow(o + np.array([self._xs[i], y, 0]),
                      o + np.array([self._xs[j], y - 0.16, 0]),
                      color=col, stroke_width=3.0, buff=0.10,
                      max_tip_length_to_length_ratio=0.06)
            r = _hud(str(e.get("texto", "")), self.fs - 2, col)
            r.move_to((f.get_start() + f.get_end()) / 2.0 + UP * 0.20)
            self.flechas.add(f)
            self.rotulos.add(r)
            if mostrar_tiempo and e.get("t_ms") is not None:
                t = _hud("%s ms" % fmt(e["t_ms"], 0), self.fs - 3, C_CIFRA)
                t.move_to(o + np.array([-self.ancho / 2.0 - 0.75, y, 0]))
                self.tiempos.add(t)
        self.add(self.vidas, self.actores, self.flechas, self.rotulos,
                 self.tiempos)

    def actor(self, i):
        return self.actores[i]

    def linea_vida(self, i):
        return self.vidas[i]

    def flecha(self, k):
        return self.flechas[k]

    def rotulo(self, k):
        return self.rotulos[k]

    def marca_tiempo(self, k):
        return self.tiempos[k] if k < len(self.tiempos) else None

    def paso(self, k):
        """Flecha + rotulo + marca de tiempo del evento k (para animarlo)."""
        piezas = [self.flechas[k], self.rotulos[k]]
        if k < len(self.tiempos):
            piezas.append(self.tiempos[k])
        return VGroup(*piezas)


def escalera(actores, eventos, ancho=6.0, alto=3.4, fs=15, color=C_RED,
             color_msg=C_PAQUETE, mostrar_tiempo=True):
    """Ver `Escalera`. `eventos` = [{de, a, texto, t_ms, color}, ...]."""
    return Escalera(actores, eventos, ancho, alto, fs, color, color_msg,
                    mostrar_tiempo)


class Sierra(_Anclada):
    """cwnd frente al tiempo: la sierra de AIMD, la cubica de CUBIC.

    .ejes .curva .marcas (perdidas en rojo) .media (linea punteada)
    .con_traza(t) GEMELA.
    """

    def __init__(self, traza, perdidas=(), ancho=6.4, alto=2.8,
                 color=C_PAQUETE, y_max=None, media=True, etiqueta=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.traza = [float(x) for x in traza]
        self.perdidas = tuple(int(p) for p in perdidas)
        self.ancho, self.alto, self.color = float(ancho), float(alto), color
        self.y_max = float(y_max) if y_max else max(self.traza) * 1.15
        self.mostrar_media = bool(media)
        self.etiqueta_txt = etiqueta
        self._poner_ancla(ORIGIN)
        o = self._origen()
        self.ejes = VGroup(
            Line(o + np.array([-self.ancho / 2.0, -self.alto / 2.0, 0]),
                 o + np.array([self.ancho / 2.0, -self.alto / 2.0, 0]),
                 color=C_EJE, stroke_width=1.8),
            Line(o + np.array([-self.ancho / 2.0, -self.alto / 2.0, 0]),
                 o + np.array([-self.ancho / 2.0, self.alto / 2.0, 0]),
                 color=C_EJE, stroke_width=1.8))
        self.curva = VMobject(color=color, stroke_width=3.0)
        self.curva.set_points_as_corners([self.punto(i)
                                          for i in range(len(self.traza))])
        self.marcas = VGroup(*[Dot(self.punto(p), radius=0.07,
                                   color=C_PERDIDA)
                               for p in self.perdidas
                               if p < len(self.traza)])
        self.media = VGroup()
        if self.mostrar_media and self.traza:
            m = sum(self.traza) / len(self.traza)
            self.valor_medio = m
            y = self._y(m)
            self.media.add(DashedLine(
                o + np.array([-self.ancho / 2.0, y - o[1], 0]) + np.array([0, o[1], 0]),
                o + np.array([self.ancho / 2.0, y - o[1], 0]) + np.array([0, o[1], 0]),
                color=C_CIFRA, stroke_width=1.8, dash_length=0.10))
        else:
            self.valor_medio = 0.0
        self.add(self.ejes, self.curva, self.marcas, self.media)
        self.etiqueta = None
        if etiqueta:
            self.etiqueta = _hud(etiqueta, 15, C_EJE)
            self.etiqueta.next_to(self.ejes, UP, buff=0.16)
            self.add(self.etiqueta)

    def _y(self, v):
        f = float(v) / self.y_max
        return (self._origen()[1] - self.alto / 2.0 +
                min(max(f, 0.0), 1.0) * self.alto)

    def punto(self, i):
        n = max(1, len(self.traza) - 1)
        x = (self._origen()[0] - self.ancho / 2.0 +
             self.ancho * float(i) / n)
        return np.array([x, self._y(self.traza[int(i)]), 0.0])

    def con_traza(self, traza, perdidas=None):
        o = Sierra(traza, self.perdidas if perdidas is None else perdidas,
                   self.ancho, self.alto, self.color, self.y_max,
                   self.mostrar_media, self.etiqueta_txt)
        o.shift(self._origen() - o._origen())
        return o


def sierra(traza, perdidas=(), ancho=6.4, alto=2.8, color=C_PAQUETE,
           y_max=None, media=True, etiqueta=None):
    """Ver `Sierra`."""
    return Sierra(traza, perdidas, ancho, alto, color, y_max, media,
                  etiqueta)


# =====================================================================
# Modulo 5 — Los servicios que hacen usable la red
# =====================================================================
JERARQUIA_DNS = (("raiz", "."),
                 ("TLD", "org"),
                 ("dominio", "ejemplo.org"),
                 ("subdominio", "www.ejemplo.org"))


def resolver_dns(nombre="www.ejemplo.org", cache=None, rtt_local=2.0,
                 rtt_raiz=30.0, rtt_tld=45.0, rtt_auto=60.0):
    """La resolucion PASO A PASO, con el RTT acumulado. -> dict MEDIDO.

    Si el nombre esta en `cache`, se responde en un solo salto local: esa
    es toda la diferencia entre una web que abre y una que se piensa.
    """
    cache = dict(cache or {})
    if nombre in cache:
        return {"nombre": nombre, "pasos": [
            {"de": "cliente", "a": "resolutor", "pregunta": nombre,
             "rtt": rtt_local, "acumulado": rtt_local,
             "responde": "la cache", "respuesta": cache[nombre]}],
            "total_ms": rtt_local, "viajes": 1, "desde_cache": True,
            "ip": cache[nombre], "cache": cache}
    partes = nombre.split(".")
    etapas = [("resolutor", "raiz", ".", rtt_raiz,
               "no la se; pregunta al de .%s" % partes[-1]),
              ("resolutor", "TLD .%s" % partes[-1], ".".join(partes[-1:]),
               rtt_tld, "no la se; pregunta al de %s"
               % ".".join(partes[-2:])),
              ("resolutor", "autoritativo", ".".join(partes[-2:]), rtt_auto,
               "93.184.216.34")]
    pasos = [{"de": "cliente", "a": "resolutor", "pregunta": nombre,
              "rtt": rtt_local, "acumulado": rtt_local,
              "responde": None, "respuesta": None}]
    acc = rtt_local
    for de, a, zona, rtt, resp in etapas:
        acc += rtt
        pasos.append({"de": de, "a": a, "pregunta": nombre, "zona": zona,
                      "rtt": rtt, "acumulado": acc, "responde": a,
                      "respuesta": resp})
    cache[nombre] = "93.184.216.34"
    return {"nombre": nombre, "pasos": pasos, "total_ms": acc,
            "viajes": len(pasos), "desde_cache": False,
            "ip": "93.184.216.34", "cache": cache}


def cache_dns(n_consultas=200, n_nombres=12, ttl=8, semilla=5, zipf=1.4):
    """Traza de consultas con localidad (Zipf) y una cache con TTL.
    -> tasa de acierto MEDIDA, no supuesta."""
    rng = np.random.default_rng(int(semilla))
    pesos = 1.0 / (np.arange(1, int(n_nombres) + 1) ** float(zipf))
    pesos = pesos / pesos.sum()
    consultas = rng.choice(int(n_nombres), size=int(n_consultas), p=pesos)
    expira, aciertos, fallos, historia = {}, 0, 0, []
    for t, n in enumerate(consultas):
        n = int(n)
        vivo = expira.get(n, -1) > t
        if vivo:
            aciertos += 1
        else:
            fallos += 1
            expira[n] = t + int(ttl)
        historia.append({"t": t, "nombre": n, "acierto": vivo})
    return {"consultas": int(n_consultas), "aciertos": aciertos,
            "fallos": fallos, "historia": historia, "ttl": int(ttl),
            "tasa_acierto": 100.0 * aciertos / int(n_consultas),
            "nombres": int(n_nombres)}


def dhcp_dora(mac="aa:bb:cc:11:22:33", ip="192.168.1.37",
              red="192.168.1.0/24", arriendo_s=86400,
              dns="192.168.1.1", puerta="192.168.1.1"):
    """Los cuatro mensajes de DHCP, con lo que viaja en cada uno."""
    c = cidr(red)
    ev = [
        {"n": 1, "mensaje": "DISCOVER", "de": "cliente", "a": "todos",
         "destino": "255.255.255.255", "origen": "0.0.0.0",
         "dice": "hay algun servidor DHCP?"},
        {"n": 2, "mensaje": "OFFER", "de": "servidor", "a": "cliente",
         "destino": "255.255.255.255", "origen": puerta,
         "dice": "te ofrezco %s" % ip},
        {"n": 3, "mensaje": "REQUEST", "de": "cliente", "a": "todos",
         "destino": "255.255.255.255", "origen": "0.0.0.0",
         "dice": "acepto %s" % ip},
        {"n": 4, "mensaje": "ACK", "de": "servidor", "a": "cliente",
         "destino": ip, "origen": puerta,
         "dice": "tuya por %d h" % (arriendo_s // 3600)},
    ]
    return {"eventos": ev, "ip": ip, "mac": mac, "mascara": c["mascara"],
            "puerta": puerta, "dns": dns, "arriendo_s": int(arriendo_s),
            "arriendo_h": arriendo_s // 3600, "red": c["prefijo"]}


RFC1918 = ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")


def es_privada(ip):
    """Las direcciones que NO existen fuera de tu casa."""
    return any(en_prefijo(ip, p) for p in RFC1918)


def nat_traducir(sesiones, ip_publica="203.0.113.7", puerto0=40000):
    """El router reescribe origen Y PUERTO, y anota la fila. -> dict.

    `sesiones` = [(ip_privada, puerto_origen, ip_destino, puerto_destino)].
    Dos aparatos que usan el mismo puerto de origen no chocan porque NAT
    los renumera: eso se ve en la tabla.
    """
    tabla, filas, siguiente, choques = {}, [], int(puerto0), 0
    for ip_o, pto_o, ip_d, pto_d in sesiones:
        clave = (ip_o, pto_o, ip_d, pto_d)
        if clave not in tabla:
            if any(f["pto_o"] == pto_o for f in filas):
                choques += 1        # mismo puerto de origen, distinto host
            tabla[clave] = siguiente
            siguiente += 1
        filas.append({"ip_o": ip_o, "pto_o": pto_o, "ip_d": ip_d,
                      "pto_d": pto_d, "pto_publico": tabla[clave],
                      "ip_publica": ip_publica,
                      "privada": es_privada(ip_o)})
    return {"filas": filas, "tabla": tabla, "ip_publica": ip_publica,
            "sesiones": len(filas), "renumerados": choques,
            "puertos_usados": siguiente - int(puerto0)}


def nat_entrante(intentos, tabla_nat):
    """De fuera hacia dentro no se puede iniciar nada. -> bloqueados
    CONTADOS (por eso existen STUN, TURN y el agujereado de UDP)."""
    validos = set(tabla_nat.values())
    pasos = []
    for pto in intentos:
        pasos.append({"puerto": int(pto), "pasa": int(pto) in validos})
    return {"pasos": pasos, "bloqueados": sum(1 for p in pasos
                                              if not p["pasa"]),
            "total": len(pasos)}


ICMP_TIPOS = {0: "respuesta de eco", 3: "destino inalcanzable",
              8: "peticion de eco", 11: "tiempo excedido",
              (3, 4): "fragmentacion necesaria"}


def ping(distancia_km=9000.0, saltos=8, carga=0.0, ms_por_salto=0.35,
         semilla=2, n=8):
    """RTT = propagacion (tope duro: la luz en fibra) + cola. -> dict.

    `carga` de 0 a 1 encola el enlace: el mismo ping sube su RTT en la
    cifra medida, que es la demostracion del bufferbloat de 7.2.
    """
    rng = np.random.default_rng(int(semilla))
    prop = 2.0 * 1000.0 * float(distancia_km) / _FIBRA_KM_S
    proceso = 2.0 * float(saltos) * float(ms_por_salto)
    espera = 0.0
    if carga > 0:
        espera = float(saltos) * 0.6 * (float(carga) / (1.0 - min(carga,
                                                                  0.98)))
    muestras = prop + proceso + espera + rng.gamma(2.0, 0.6, int(n))
    return {"prop_ms": prop, "proceso_ms": proceso, "espera_ms": espera,
            "muestras": muestras, "min": float(muestras.min()),
            "media": float(muestras.mean()), "max": float(muestras.max()),
            "distancia_km": float(distancia_km), "carga": float(carga),
            "tope_luz_ms": prop}


def traceroute(camino, mudos=(), distancia_km=9000.0, semilla=4):
    """TTL=1, 2, 3... cada router delata su direccion al quejarse. -> dict.

    `mudos` = indices (1-based) de los saltos que no contestan: salen como
    `*`, que es lo que se ve en un traceroute de verdad.
    """
    rng = np.random.default_rng(int(semilla))
    mudos = set(int(m) for m in mudos)
    n = len(camino)
    saltos = []
    for i, nodo in enumerate(camino, start=1):
        frac = i / float(n)
        base = 2.0 * 1000.0 * float(distancia_km) * frac / _FIBRA_KM_S
        ms = base + float(rng.gamma(2.0, 0.5))
        saltos.append({"ttl": i, "nodo": None if i in mudos else nodo,
                       "ms": None if i in mudos else ms,
                       "mudo": i in mudos,
                       "icmp": "tiempo excedido" if i < n
                       else "respuesta de eco"})
    return {"saltos": saltos, "n": n, "mudos": sorted(mudos),
            "total_ms": saltos[-1]["ms"] if not saltos[-1]["mudo"] else None}


def pmtud(mtus, tam=1500, filtra_icmp=False):
    """Descubrir el MTU del camino. -> dict.

    Si alguien FILTRA el ICMP de "fragmentacion necesaria", el emisor no
    se entera y la conexion se cuelga sin motivo aparente: el agujero
    negro. Eso tambien se devuelve medido.
    """
    pasos, actual = [], int(tam)
    for i, m in enumerate(mtus, start=1):
        cabe = actual <= int(m)
        pasos.append({"salto": i, "mtu": int(m), "intento": actual,
                      "cabe": cabe,
                      "icmp": None if cabe else
                      ("filtrado" if filtra_icmp
                       else "fragmentacion necesaria, MTU=%d" % m)})
        if not cabe:
            if filtra_icmp:
                return {"pasos": pasos, "mtu_camino": None,
                        "agujero_negro": True, "intentos": len(pasos),
                        "tam_inicial": int(tam)}
            actual = int(m)
    return {"pasos": pasos, "mtu_camino": actual, "agujero_negro": False,
            "intentos": len(pasos), "tam_inicial": int(tam),
            "reduccion": int(tam) - actual}


# =====================================================================
# Modulo 6 — La web y el candado
# =====================================================================
CODIGOS_HTTP = ((200, "OK", "aqui lo tienes"),
                (301, "Moved Permanently", "ya no vivo aqui, ve alli"),
                (304, "Not Modified", "el que tienes sirve"),
                (404, "Not Found", "eso no existe"),
                (500, "Internal Server Error", "me rompi yo"))


def http_peticion(metodo="GET", ruta="/index.html", host="ejemplo.org",
                  cuerpo=2048, estado=200):
    """Una peticion y su respuesta en texto plano. -> dict con BYTES."""
    pet = ("%s %s HTTP/1.1\r\n"
           "Host: %s\r\n"
           "User-Agent: navegador/1.0\r\n"
           "Accept: text/html\r\n\r\n" % (metodo, ruta, host))
    nombre = dict((c, t) for c, t, _ in CODIGOS_HTTP).get(estado, "")
    cab_resp = ("HTTP/1.1 %d %s\r\n"
                "Content-Type: text/html\r\n"
                "Content-Length: %d\r\n"
                "ETag: \"a1b2c3\"\r\n\r\n" % (estado, nombre, cuerpo))
    total = len(pet) + len(cab_resp) + int(cuerpo)
    return {"peticion": pet, "respuesta_cabecera": cab_resp,
            "bytes_peticion": len(pet), "bytes_cabecera": len(cab_resp),
            "bytes_cuerpo": int(cuerpo), "bytes_total": total,
            "protocolo_pct": 100.0 * (len(pet) + len(cab_resp)) / total,
            "estado": int(estado), "nombre_estado": nombre}


def cache_condicional(bytes_cuerpo=2048, cabecera_304=180):
    """`If-None-Match` -> 304: lo que se ahorra en bytes, MEDIDO."""
    completo = http_peticion(cuerpo=bytes_cuerpo)["bytes_total"]
    corto = http_peticion(cuerpo=0, estado=304)["bytes_peticion"] + \
        int(cabecera_304)
    return {"con_cuerpo": completo, "solo_304": corto,
            "ahorro": completo - corto,
            "ahorro_pct": 100.0 * (completo - corto) / completo}


def http_transferencia(n_objetos=40, modo="serie", rtt_ms=40.0,
                       conexiones=6, tls=True, version_tls="1.3"):
    """Cuanto tarda una pagina de N objetos segun COMO se piden. -> dict.

    El cuello de botella no es el ancho de banda: son los VIAJES. Se
    cuentan los RTT, que es lo unico que no se puede comprar.

    Modos, del peor al mejor:
      serie      HTTP/1.0: una conexion (y un apreton) por cada objeto
      keepalive  HTTP/1.1: UNA conexion reutilizada, pero en fila india
      paralelo   HTTP/1.1: `conexiones` conexiones a la vez (6 tipico)
      h2         HTTP/2: una conexion, todo multiplexado
      h3         HTTP/3: QUIC junta el apreton de transporte y el de TLS
      h3-0rtt    HTTP/3 reanudando: datos en el primer paquete
    """
    rtt = float(rtt_ms)
    apreton = 1.0 + (tls_viajes(version_tls)["rtt"] if tls else 0.0)
    if modo == "serie":                       # HTTP/1.0: una conexion cada uno
        rtts = n_objetos * (apreton + 1.0)
        conex = n_objetos
    elif modo == "keepalive":                 # HTTP/1.1: UNA conexion, en fila
        rtts = apreton + n_objetos * 1.0
        conex = 1
    elif modo == "paralelo":                  # HTTP/1.1: 6 conexiones
        conex = int(conexiones)
        tandas = math.ceil(n_objetos / conex)
        rtts = apreton + tandas * 1.0
    elif modo == "h2":                        # una conexion, multiplexado
        conex = 1
        rtts = apreton + 1.0
    elif modo == "h3":                        # QUIC: transporte y TLS juntos
        conex = 1
        rtts = 1.0 + 1.0
    elif modo == "h3-0rtt":
        conex = 1
        rtts = 0.0 + 1.0
    else:
        raise ValueError("modo desconocido: %s" % modo)
    return {"modo": modo, "objetos": int(n_objetos), "conexiones": conex,
            "rtts": rtts, "ms": rtts * rtt, "rtt_ms": rtt,
            "apreton_rtts": apreton}


def tls_viajes(version="1.3", reanudado=False):
    """Los RTT del apreton de TLS antes del primer byte de HTTP."""
    if reanudado and version == "1.3":
        return {"version": "1.3 (0-RTT)", "rtt": 0.0, "mensajes": 1,
                "aviso": "los datos de 0-RTT son repetibles por un atacante"}
    tabla = {"1.2": 2.0, "1.3": 1.0}
    if version not in tabla:
        raise ValueError("version TLS desconocida: %s" % version)
    return {"version": version, "rtt": tabla[version],
            "mensajes": 4 if version == "1.2" else 2, "aviso": None}


def dh_pequeno(p=23, g=5, a=6, b=15):
    """Diffie-Hellman con numeros de juguete: los dos llegan al MISMO
    numero sin que ese numero cruce nunca el cable. Se apoya en el curso
    19 (`cripto.diffie_hellman`), no lo repite."""
    from cripto import diffie_hellman
    d = diffie_hellman(p, g, a, b)
    d["iguales"] = True
    return d


def cadena_certificados(sitio="ejemplo.org", alterar=False):
    """La cadena raiz -> intermedia -> sitio, con firmas RSA REALES.

    Firmar = elevar el hash a la privada; verificar = elevarlo a la
    publica y comparar. Con `alterar=True` se cambia un byte del
    certificado y la verificacion FALLA.
    """
    from cripto import (E_RSA, rsa_juguete, rsa_cifrar, rsa_descifrar,
                        sha256_hex)
    claves = rsa_juguete()      # devuelve {n, phi, d}: la `e` es E_RSA
    e, d, n = E_RSA, claves["d"], claves["n"]
    eslabones = []
    for nombre, quien in (("raiz", "CA Raiz"), ("intermedia", "CA Intermedia"),
                          ("sitio", sitio)):
        cuerpo = "%s|%s" % (nombre, quien)
        if alterar and nombre == "sitio":
            cuerpo += "!"          # un byte de mas: el hash ya no cuadra
        h = int(sha256_hex(cuerpo)[:4], 16) % n
        firma = rsa_descifrar(h, d, n)          # firmar = con la privada
        eslabones.append({"nivel": nombre, "quien": quien, "cuerpo": cuerpo,
                          "hash": h, "firma": firma,
                          "verifica": rsa_cifrar(firma, e, n) == h})
    if alterar:
        # el certificado alterado se presenta con la firma del original
        original = "sitio|%s" % sitio
        h_bueno = int(sha256_hex(original)[:4], 16) % n
        eslabones[-1]["firma"] = rsa_descifrar(h_bueno, d, n)
        eslabones[-1]["verifica"] = \
            rsa_cifrar(eslabones[-1]["firma"], e, n) == eslabones[-1]["hash"]
    return {"eslabones": eslabones, "e": e, "n": n, "alterado": bool(alterar),
            "cadena_valida": all(x["verifica"] for x in eslabones)}


def hol_bloqueo(n_flujos=4, objetos_por_flujo=6, perdida_en=2, semilla=3):
    """Bloqueo de cabeza de linea: se pierde UN segmento. -> dict MEDIDO.

    Sobre TCP, la entrega EN ORDEN para todos los flujos aunque los datos
    de los demas ya esten ahi; sobre QUIC cada flujo tiene su propio
    orden y solo se para el afectado.
    """
    tcp, quic = [], []
    for f in range(int(n_flujos)):
        parado_tcp = True                      # TCP: se paran todos
        parado_quic = (f == int(perdida_en))   # QUIC: solo el del segmento
        tcp.append({"flujo": f, "parado": parado_tcp})
        quic.append({"flujo": f, "parado": parado_quic})
    return {"tcp": tcp, "quic": quic, "n_flujos": int(n_flujos),
            "parados_tcp": sum(1 for x in tcp if x["parado"]),
            "parados_quic": sum(1 for x in quic if x["parado"]),
            "perdida_en": int(perdida_en),
            "objetos_por_flujo": int(objetos_por_flujo)}


def quic_migracion(id_conexion="0x7a1c", de="wifi", a="movil"):
    """El ID de conexion sobrevive al cambio de red: no hay que
    reconectar (con TCP la 4-tupla cambia y la conexion muere)."""
    return {"id": id_conexion, "de": de, "a": a,
            "tcp": {"sobrevive": False,
                    "por_que": "la conexion es la 4-tupla; al cambiar la IP, muere"},
            "quic": {"sobrevive": True,
                     "por_que": "la conexion es el ID, no la direccion"}}


class Arbol(_Anclada):
    """Jerarquia por niveles (el arbol del DNS, la cadena de
    certificados). .nodo(nivel, i) .rama(nivel, i) .con_marcados()."""

    def __init__(self, niveles, marcados=(), ancho=7.0, alto=3.2, fs=15,
                 color=C_CAPA, color_marca=C_PAQUETE, **kwargs):
        super().__init__(**kwargs)
        self.niveles = [list(n) for n in niveles]
        self.marcados = set(tuple(m) for m in marcados)
        self.ancho, self.alto, self.fs = float(ancho), float(alto), int(fs)
        self.color, self.color_marca = color, color_marca
        self._poner_ancla(ORIGIN)
        o = self._origen()
        nn = len(self.niveles)
        self.cajas, self.textos, self.ramas = VGroup(), VGroup(), VGroup()
        self._pos = {}
        for k, fila in enumerate(self.niveles):
            y = self.alto / 2.0 - (k * self.alto / max(1, nn - 1))
            m = len(fila)
            for i, etq in enumerate(fila):
                x = (-self.ancho / 2.0 + self.ancho * (i + 0.5) / m)
                marcado = (k, i) in self.marcados
                col = color_marca if marcado else color
                t = _hud(str(etq), self.fs, col)
                caja = Rectangle(width=max(t.width + 0.26, 0.6),
                                 height=0.42, stroke_color=col,
                                 stroke_width=2.2, fill_color=col,
                                 fill_opacity=0.18 if marcado else 0.06)
                caja.move_to(o + np.array([x, y, 0.0]))
                t.move_to(caja.get_center())
                self.cajas.add(caja)
                self.textos.add(t)
                self._pos[(k, i)] = len(self.cajas) - 1
        for k in range(nn - 1):
            for i in range(len(self.niveles[k + 1])):
                padre = min(int(i * len(self.niveles[k]) /
                                max(1, len(self.niveles[k + 1]))),
                            len(self.niveles[k]) - 1)
                a = self.cajas[self._pos[(k, padre)]]
                b = self.cajas[self._pos[(k + 1, i)]]
                self.ramas.add(Line(a.get_bottom(), b.get_top(),
                                    color=C_EJE, stroke_width=1.6))
        self.add(self.ramas, self.cajas, self.textos)

    def nodo(self, nivel, i=0):
        return self.cajas[self._pos[(nivel, i)]]

    def texto(self, nivel, i=0):
        return self.textos[self._pos[(nivel, i)]]

    def con_marcados(self, marcados):
        o = Arbol(self.niveles, marcados, self.ancho, self.alto, self.fs,
                  self.color, self.color_marca)
        o.shift(self._origen() - o._origen())
        return o


def arbol(niveles, marcados=(), ancho=7.0, alto=3.2, fs=15, color=C_CAPA,
          color_marca=C_PAQUETE):
    """Ver `Arbol`. `niveles` = [["."], ["org", "com"], ...]."""
    return Arbol(niveles, marcados, ancho, alto, fs, color, color_marca)
