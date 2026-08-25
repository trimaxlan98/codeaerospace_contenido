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

Numeros del LOTE 1 (modulos 1 y 2). Toda cifra en pantalla sale de aqui
o de la tabla del style_block, nunca escrita a mano:
    troceado / conmutacion / mux_estadistico / cola_mm1 / little
    encapsular / crc32_trama / trama_ethernet / csma_cd
    switch_aprende / arp_resolver
    checksum_ip / cabecera_ipv4 / fragmentar / ttl_camino
    cidr / mascara_bits / prefijo_mas_largo / agregar_rutas
    ipv6_expandir / ipv6_comprimir / eui64 / espacio_direcciones

Piezas (VGroup con localizadores que siguen move_to/shift, NO scale;
todo lo que cambia tiene gemela `con_*` de estructura IDENTICA):
    paquete        capsula de campos; .campo(n) .iluminar(n); .con_valores()
    cabecera       tabla de campos por filas de 32 bits; .con_valores()
    nodo           host / switch / router / servidor / satelite
    enlace         linea entre nodos; .punto_en(frac)
    topologia      grafo dibujado; .nodo(n) .enlace(a,b) .resaltar_camino()
    cola           bufer con ranuras; .con_ocupacion(n)
    pila           torre de capas; .capa(i); .con_encapsulado(k)
    tabla          filas x columnas de texto HUD; .con_filas()
    reloj          contador de milisegundos en cian; .con_ms()
    barra_bits     32/128 bits con raya movil red|host; .con_prefijo(n)

Uso en un clip (el style_block de la familia ya importa todo):
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from protocolos import *
"""
import math
import zlib

import numpy as np
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Circle, DashedLine, Dot,
                   Line, Polygon, Rectangle, RoundedRectangle, Square,
                   Triangle, VGroup)

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
        return self

    def con_valores(self, nuevos, color=None):
        campos = [(n, w, str(nuevos.get(n, v)))
                  for n, w, v in self.campos_spec]
        o = Paquete(campos, self.ancho, self.alto, self.fs,
                    color or self.color, self.color_carga)
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

    def campo(self, nombre):
        return self.cajas[self._idx[nombre]]

    def texto(self, nombre):
        return self.textos[self._idx[nombre]]

    def iluminar(self, nombre, color=C_CIFRA):
        i = self._idx[nombre]
        self.cajas[i].set_stroke(color, width=3.0)
        self.cajas[i].set_fill(color, opacity=0.16)
        self.textos[i].set_color(color)
        return self

    def con_valores(self, nuevos):
        v = dict(self.valores_spec)
        v.update(nuevos)
        o = Cabecera(self.campos_spec, v, self.ancho, self.alto_fila,
                     self.fs, self.color, self.bits_fila)
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
                 color=C_EJE, color_cab=C_CAPA, resaltar=None, **kwargs):
        super().__init__(**kwargs)
        self.cabeceras = [str(c) for c in cabeceras]
        self.filas_spec = [[str(c) for c in f] for f in filas]
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
            col = C_CIFRA if resaltar is not None and i == resaltar else color
            if resaltar is not None and i == resaltar:
                fondo = Rectangle(width=ancho_total + 0.12, height=self.alto,
                                  stroke_width=0.0, fill_color=C_CIFRA,
                                  fill_opacity=0.12)
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
        o = Tabla(self.cabeceras, filas, self.anchos, self.alto, self.fs,
                  self.color, self.color_cab, resaltar)
        o.shift(self._origen() - o._origen())
        return o


def tabla(cabeceras, filas, anchos=None, alto=0.40, fs=14, color=C_EJE,
          color_cab=C_CAPA, resaltar=None):
    """Ver `Tabla`."""
    return Tabla(cabeceras, filas, anchos, alto, fs, color, color_cab,
                 resaltar)


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
