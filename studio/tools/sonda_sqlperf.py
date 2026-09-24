"""Sonda de invariantes de manim_extensions/sqlperf.py (curso 37).

Corre EN EL CONTENEDOR, antes de escribir un solo clip:

    docker run --rm --user $(id -u):$(id -g) -v "$PWD":/workspace \
      -w /workspace codeaerospace_contenido-manim \
      python3 studio/tools/sonda_sqlperf.py

Cada comprobacion es una propiedad que la reproduccion solo cumple si esta
bien, con su contraejemplo (la variante rota tiene que FALLAR). Los modelos
(lookup, punto de inflexion, filas por pagina) se contrastan con lo que
midio el motor: si no caen cerca, no van a pantalla.
"""
import math
import sys

import numpy as np

sys.path.insert(0, "studio/content/manim_extensions")
import sqlperf as S  # noqa: E402

M = S.MEDIDO
fallos = []


def ok(cond, que, valor=""):
    print(("  ok  " if cond else "  XX  ") + que + (f"  -> {valor}" if valor != "" else ""))
    if not cond:
        fallos.append(que)


def cerca(a, b, tol):
    return abs(a - b) <= tol * abs(b)


print("== Reproduccion de TiendaPerf ==")
p = S.pedidos()
ok(len(p["id_cliente"]) == 1_500_000, "1.5 M pedidos")
c1 = S.filas_cliente(1)
ok(c1 == M["eq_rows_c1"], "cliente 1 = EQ_ROWS del motor (149,970)", c1)
c501 = S.filas_cliente(501)
ok(185 <= c501 <= 195, "cliente 501 ~190 filas", c501)
# contraejemplo: el INT en little-endian no reproduce el EQ_ROWS
h = np.array([np.frombuffer(__import__("hashlib").md5((k + 1_000_000_000).to_bytes(4, "little")).digest(), dtype=np.uint8) for k in range(1, 1_500_001)])
r1 = S._sub3(h, 0)
ok(int((r1 % 10 == 0).sum()) != c1, "contraejemplo: little-endian NO da 149,970",
   int((r1 % 10 == 0).sum()))
dist = S.clientes_distintos()
ok(188_000 <= dist <= 190_000, "clientes con pedidos ~189 k", dist)
ok(p["dia"].max() == S.dia("2026-09-19"), "ultimo pedido 2026-09-19")
ok(np.all(np.diff(p["dia"] * 86400 + p["seg"]) >= 0), "id_pedido sigue el orden de fecha")
det = S.detalle_total()
ok(det == M["filas_detalle"], "detalle = 3,750,000 (CHECKSUM(int) = int)", det)
x = (np.arange(1, 1_500_001, dtype=np.int64) * 7) & 0x7FFFFFFF
ok(True, "(nota) con *7 tambien da 2.5 de media: el total solo no discrimina", int((1 + x % 4).sum()))

print("== Estatus y fechas ==")
fr = S.fraccion_estatus()
ok(0.91 < fr["entregado"] < 0.93, "entregado ~92 %", round(fr["entregado"], 4))
pend = S.filas_estatus("pendiente")
ok(pend / 1.5e6 < 0.002, "pendientes < 0.2 %", pend)
r2025 = S.filas_rango("2025-01-01", "2026-01-01")
cn2025 = S.filas_rango("2025-01-01", "2026-01-01", "cancelado")
print(f"      2025: {r2025}  cancelados 2025: {cn2025}")
# El orden de llaves: las lecturas son proporcionales a las filas que recorre el seek
ok(cerca(r2025 / cn2025, M["canc2025_fecha_estatus"] / M["canc2025_estatus_fecha"], 0.06),
   "razon filas (fecha,est)/(est,fecha) ~ razon de lecturas",
   f"{r2025 / cn2025:.2f} vs {M['canc2025_fecha_estatus'] / M['canc2025_estatus_fecha']:.2f}")
fpp_fecha = r2025 / M["year_rango"]
print(f"      filas por pagina del indice por fecha: {fpp_fecha:.1f}")
ok(cerca(1.5e6 / fpp_fecha, M["year_scan"], 0.03), "scan del indice por fecha = 1.5 M / filas por pagina",
   round(1.5e6 / fpp_fecha))
ult30 = int((p["dia"] > S.dia("2026-08-16")).sum())
ok(cerca(ult30 / fpp_fecha, M["dateadd_bien"], 0.08), "DATEADD bien ~ filas del rango / filas por pagina",
   f"{ult30} filas -> {ult30 / fpp_fecha:.0f} vs {M['dateadd_bien']}")
d1 = S.filas_dia("2026-09-01")
ok(d1 / fpp_fecha + 3 < M["cast_date"] < 3 * d1 / fpp_fecha + 3,
   "CAST a DATE: rango dinamico MAS ANCHO que un dia (entre 1 y 3 dias)",
   f"{d1} filas/dia -> {d1 / fpp_fecha + 3:.1f} < {M['cast_date']} < {3 * d1 / fpp_fecha + 3:.1f}")
ok(pend / M["pendientes_paginas"] > 100, "indice filtrado: filas por pagina razonables",
   round(pend / M["pendientes_paginas"]))

print("== Modelos de lecturas ==")
fpp = S.filas_por_pagina(1_500_000, M["paginas_pedidos"])
ok(60 < fpp < 75, "pedidos: filas por pagina", round(fpp, 1))
fo = S.fanout_int(4)
prof = S.profundidad(1_500_000, fpp, fo)
ok(prof == M["pk_seek"], "profundidad del agrupado = lecturas del seek por PK", prof)
ok(S.profundidad(1_500_000, fpp, 2) != prof, "contraejemplo: con fanout 2 no son 3 niveles",
   S.profundidad(1_500_000, fpp, 2))
m501 = S.lecturas_seek_lookup(c501)
ok(cerca(m501, M["c501_lookup"], 0.05), "modelo seek+lookup del 501 ~ 597", m501)
m1 = S.lecturas_seek_lookup(c1)
ok(cerca(m1, M["variable_local"], 0.01), "modelo lookups del cliente 1 ~ 450,173", m1)
ok(cerca(m1, M["sniff_501_luego_1"][1], 0.03), "... y ~ 459,555 del sniffing", m1)
pi = S.punto_inflexion()
ok(c501 < pi["filas"] < c1, "501 debajo y 1 encima del punto de inflexion", round(pi["filas"]))
ok(0.004 < pi["fraccion"] < 0.006, "punto de inflexion ~0.5 % de la tabla", round(pi["fraccion"] * 100, 3))
cub = M["c1_cubriente"] - 3
ok(150 < c1 / cub < 250, "indice cubriente: filas por hoja razonables", round(c1 / cub))
ok(S.rowgroups() == 4, "columnstore: 3.75 M -> 4 rowgroups", S.rowgroups())

print("== Estimaciones ==")
est = S.estimado_variable()
ok(7.5 < est < 8.5, "variable local: estima ~8 filas", round(est, 2))
ok(c1 / est > 10_000, "error de estimacion del cliente 1 > 10,000x", round(c1 / est))
u = int(S.umbral_estadisticas(1_500_000))
ok(u == 38_729, "umbral RAIZ(1000 n) = 38,729 (CAST AS INT)", u)
ok(S.umbral_estadisticas_viejo(1_500_000) > 7 * u, "el umbral viejo (20 %) es ~8x mayor",
   S.umbral_estadisticas_viejo(1_500_000))
hi = S.histograma()
ok(len(hi) <= 200, "histograma <= 200 pasos", len(hi))
ok(S.paso_de(hi, 1)["eq"] == c1 and S.paso_de(hi, 1)["hi"] == 1, "paso propio del cliente 1 con EQ_ROWS exacto")
ok(sum(s["eq"] + s["range"] for s in hi) == 1_500_000, "el histograma suma 1.5 M filas")
p501 = S.paso_de(hi, 501)
print(f"      paso del 501: hi={p501['hi']} eq={p501['eq']} range={p501['range']} distinct={p501['distinct']}")

print("== Clientes (sargabilidad) ==")
g = S.filas_apellido("Garcia")
ok(9_000 < g < 11_000, "apellido Garcia ~1/20", g)
ok(S.telefonos_nulos() / 2e5 > 0.18, "telefono NULL ~20 %", S.telefonos_nulos())
print(f"      telefono 5500000000: {S.filas_telefono(5_500_000_000)} filas; email 4242: {S.email(4242)}")

print("== Razones que ira a pantalla ==")
print(f"      scan / filas utiles 501: {M['scan_pedidos'] / c501:.0f} paginas por fila")
print(f"      597 -> 4: {M['c501_lookup'] / M['c501_cubriente']:.0f}x ; 22,363 -> 785: {M['c1_scan'] / M['c1_cubriente']:.1f}x")
print(f"      caso: {M['caso_antes_s'] / M['caso_despues_s']:.1f}x ; UDF {M['udf_140_s'] / M['udf_170_s']:.1f}x ; tvar {M['tvar_140_s'] / M['tvar_170_s']:.1f}x")
print(f"      ticket 18,016 -> 3: {M['ticket_sin_indice'] / 3:.0f}x ; email {M['email_nvarchar'] / 3:.0f}x")

print()
print("FALLOS:", len(fallos))
for f in fallos:
    print("  -", f)
sys.exit(1 if fallos else 0)
