#!/usr/bin/env python3
"""Invariantes de `sistemas.py`. Se corre ANTES de escribir un clip.

    docker run --rm --network none -v "$PWD:/workspace" -w /workspace \\
        codeaerospace_contenido-manim \\
        python3 studio/tools/sonda_sistemas.py

Un sistema mal implementado no se ve mal: dibuja una curva razonable y saca
una cifra plausible. Asi que cada propiedad tiene que demostrarse aqui con
una prueba que solo pasa si esta bien, y —lo mas importante de este curso—
con su CONTRAEJEMPLO: una prueba de linealidad que no sepa distinguir un
sistema lineal de uno que satura no esta probando nada.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / "content" / "manim_extensions"))
import sistemas as sis  # noqa: E402

fallos = []
n_ok = 0


def ok(nombre, condicion, detalle=""):
    global n_ok
    if condicion:
        n_ok += 1
        print(f"  ok   {nombre}" + (f"   [{detalle}]" if detalle else ""))
    else:
        fallos.append(nombre)
        print(f"  FALLO {nombre}   {detalle}")


def casi(nombre, a, b, tol, unidad=""):
    ok(nombre, abs(a - b) <= tol, f"{a:.6g} vs {b:.6g} {unidad}".strip())


h = sis.h_amortiguada(48)
rng = np.random.default_rng(sis.SEMILLA)
x1 = rng.standard_normal(40)
x2 = rng.standard_normal(40)

print("\n== 01 · El impulso ==")
areas = [sis.area(*sis.pulso_de_area(a)) for a in (1.0, 0.5, 0.25, 0.1)]
ok("el area no cambia al estrechar el pulso",
   max(areas) - min(areas) < 1e-9, " ".join(f"{v:.4f}" for v in areas))
casi("y vale 1", areas[-1], 1.0, 1e-9)
# La altura sube casi exactamente al doble y al cuadruple, pero NO
# exactamente: el rectangulo se queda en el numero entero de muestras que
# caben, asi que su anchura real se redondea a la malla. La tolerancia del
# 2 % es esa cuantizacion y no una holgura de conveniencia — lo que SI es
# exacto es el area, que es lo que la pieza afirma en pantalla.
alturas = [np.max(sis.pulso_de_area(a)[1]) for a in (1.0, 0.5, 0.25)]
ok("la altura sube en la misma proporcion (salvo la malla)",
   np.allclose(alturas, [alturas[0], 2 * alturas[0], 4 * alturas[0]],
               rtol=0.02),
   " ".join(f"{v:.3f}" for v in alturas))
ok("la delta vale 1 en su sitio y 0 fuera",
   sis.impulso(10, 3)[3] == 1.0 and np.sum(sis.impulso(10, 3)) == 1.0)

print("\n== 02-03 · Respuesta al impulso y convolucion ==")
casi("la convolucion escrita a mano == numpy",
     float(np.max(np.abs(sis.convolucion(x1, h) - np.convolve(x1, h)))),
     0.0, 1e-12)
ok("la salida dura N+M-1", sis.convolucion(x1, h).size
   == sis.largo_convolucion(x1.size, h.size),
   f"{x1.size}+{h.size}-1 = {sis.convolucion(x1, h).size}")
casi("convolucionar con la delta no hace nada",
     float(np.max(np.abs(sis.convolucion(x1, sis.impulso(1))[:x1.size]
                         - x1))), 0.0, 1e-12)
casi("la convolucion conmuta",
     float(np.max(np.abs(sis.convolucion(x1, h)
                         - sis.convolucion(h, x1)))), 0.0, 1e-12)
_, _, s = sis.solape(x1, h, 12)
casi("el deslizamiento que se dibuja da la muestra que sale",
     s, float(sis.convolucion(x1, h)[12]), 1e-12)
ok("la cola de h se mide", 20 < sis.cola(h) <= 48, f"{sis.cola(h)} muestras")

print("\n== 04 · El escalon ==")
esc = sis.escalon(60)
y_esc_conv = sis.convolucion(esc, h)
casi("la respuesta al escalon es la suma acumulada de h",
     float(np.max(np.abs(y_esc_conv[:h.size]
                         - sis.respuesta_escalon(h)))), 0.0, 1e-12)
casi("y se asienta en la suma de h", float(y_esc_conv[59]),
     sis.valor_final(h), 1e-9)
ok("la respuesta al escalon no hace falta medirla aparte",
   y_esc_conv.size == 60 + h.size - 1)

print("\n== 05 · Linealidad (con su contraejemplo) ==")
lin = sis.error_superposicion(h, x1, x2, 1.7, -0.4)
sat = sis.error_superposicion_saturado(0.7, x1, x2, 1.7, -0.4)
casi("un sistema lineal cumple la superposicion exacta", lin, 0.0, 1e-9,
     "%")
ok("y uno que satura NO la cumple", sat > 10.0, f"{sat:.1f} % de error")
ok("la prueba distingue los dos casos", sat > 1e6 * max(lin, 1e-15),
   f"lineal {lin:.2e} % vs saturado {sat:.1f} %")

print("\n== 06 · Invarianza ==")
casi("retrasar la entrada solo retrasa la salida",
     sis.error_invarianza(h, x1, 7), 0.0, 1e-9, "%")

print("\n== 07 · Causalidad ==")
hc = sis.h_amortiguada(48, retardo=0)
hnc = sis.h_no_causal(48, centro=16)
ok("la respuesta causal no tiene nada antes del golpe",
   sis.muestras_antes_de_cero(hc, 0) == 0)
ok("la no causal si", sis.muestras_antes_de_cero(hnc, 16) > 5,
   f"{sis.muestras_antes_de_cero(hnc, 16)} muestras antes del golpe")

print("\n== 08 · Estabilidad BIBO ==")
he, hi = sis.h_geometrica(0.85, 200), sis.h_geometrica(1.05, 200)
casi("suma|h| de una geometrica estable = 1/(1-a)",
     sis.suma_absoluta(he), 1.0 / (1.0 - 0.85), 1e-6)
ok("la inestable no suma", sis.suma_absoluta(hi) > 1e3,
   f"{sis.suma_absoluta(hi):.0f}")
peor = sis.peor_entrada(he)
salida = sis.convolucion(peor, he)
ok("la cota suma|h| SE ALCANZA con la peor entrada",
   float(np.max(np.abs(salida))) <= sis.cota_salida(he) + 1e-9
   and float(np.max(np.abs(salida))) > 0.98 * sis.cota_salida(he),
   f"pico {np.max(np.abs(salida)):.4f} vs cota "
   f"{sis.cota_salida(he):.4f}")

print("\n== 09 · Cascada ==")
h2 = sis.paso_bajo(0.12, 31)
casi("el orden de dos cajas no cambia la salida",
     sis.error_conmutar(h, h2, x1), 0.0, 1e-9, "%")
ok("la cascada dura la suma menos uno",
   sis.cascada(h, h2).size == h.size + h2.size - 1)

print("\n== 10 · Realimentacion ==")
ok("cerrar el lazo mueve el polo",
   sis.ganancia_lazo(1.0, 0.6) < 1.0 < sis.ganancia_lazo(1.8, 0.6),
   f"k=1 -> {sis.ganancia_lazo(1.0, 0.6):.2f}, "
   f"k=1.8 -> {sis.ganancia_lazo(1.8, 0.6):.2f}")
ok("y con el polo fuera, la respuesta no se apaga",
   sis.suma_absoluta(sis.lazo_cerrado(1.8, 60)) > 1e3,
   f"{sis.suma_absoluta(sis.lazo_cerrado(1.8, 60)):.0f}")

print("\n== 11 · La ecuacion en diferencias ==")
b, a = np.array([0.3]), np.array([1.0, -0.7])
hh = sis.h_de_ecuacion(b, a, 60)
casi("la receta recursiva da la geometrica que toca",
     float(np.max(np.abs(hh - 0.3 * sis.h_geometrica(0.7, 60)))), 0.0,
     1e-12)
casi("y filtrar con ella == convolucionar con su h",
     float(np.max(np.abs(sis.filtrar(b, a, x1)
                         - sis.convolucion(x1, hh)[:x1.size]))), 0.0,
     1e-9)

print("\n== 12 · Autofunciones (la bisagra con el curso 32) ==")
for w in (0.3, 0.9, 2.1):
    casi(f"una exponencial de w={w} sale igual salvo un numero",
         sis.error_autofuncion(h, w), 0.0, 1e-6, "%")
casi("y ese numero es H(e^jw), o sea la DFT de h",
     abs(sis.autovalor(h, 0.9)
         - complex(np.sum(h * np.exp(-1j * 0.9 * np.arange(h.size))))),
     0.0, 1e-12)

print("\n== 13 · Respuesta en frecuencia ==")
for w in (0.25, 0.8, 1.9):
    casi(f"la ganancia MEDIDA con un tono == |H| calculada (w={w})",
         sis.ganancia_medida(h, w), abs(sis.autovalor(h, w)), 2e-2)
w_, mag, _ = sis.respuesta_frecuencia(h)
casi("en w=0 la ganancia es la suma de h",
     float(mag[0]), float(np.sum(h)), 1e-9)

print("\n== 14 · Fase y retardo de grupo ==")
hl = sis.paso_bajo(0.15, 61)
wg, tg = sis.retardo_grupo(hl, 2048)
dentro = wg < 2 * np.pi * 0.15
casi("un filtro de fase lineal retrasa (M-1)/2 muestras",
     float(np.median(tg[dentro])), (61 - 1) / 2.0, 0.05, "muestras")
xd = sis.dos_tonos(0.05, 0.11, 400)
mov = sis.deformar_fases(xd, 6.0)
casi("mover las fases NO cambia el espectro de amplitud",
     float(np.max(np.abs(np.abs(np.fft.rfft(xd))
                         - np.abs(np.fft.rfft(mov))))), 0.0, 1e-9)
ok("y aun asi la señal deja de parecerse",
   float(np.max(np.abs(xd - mov)) / np.max(np.abs(xd))) > 0.5,
   f"difieren un {100 * np.max(np.abs(xd - mov)) / np.max(np.abs(xd)):.0f} %")

print("\n== 15 · Resonancia ==")
hr = sis.resonador(0.08, 12.0, 400)
amp = sis.amplificacion(hr, 0.08)
ok("el resonador amplifica su frecuencia", amp > 8, f"x{amp:.1f}")
w_r, mag_r, _ = sis.respuesta_frecuencia(hr, 4096)
casi("y el pico cae donde se le pidio",
     float(w_r[int(np.argmax(mag_r))] / (2 * np.pi)), 0.08, 0.004,
     "ciclos/muestra")
ok("mas Q, mas estrecho",
   sis.amplificacion(sis.resonador(0.08, 40.0, 800), 0.08) > amp,
   f"Q=12 -> x{amp:.1f}, Q=40 -> "
   f"x{sis.amplificacion(sis.resonador(0.08, 40.0, 800), 0.08):.1f}")

print("\n== 16 · Transitorio y permanente ==")
y_esc = np.convolve(sis.escalon(200), hr)[:200]
ta = sis.tiempo_asentamiento(y_esc, 0.02)
ok("el asentamiento se mide y es finito", 5 < ta < 200,
   f"{ta} muestras")
n = np.arange(300)
y_t = np.convolve(np.cos(0.5 * n), hr)[:300]
perm = sis.parte_permanente(hr, 0.5, 300)
ok("al final, la salida ES la parte permanente",
   float(np.max(np.abs(y_t[250:] - perm[250:]))
         / max(np.max(np.abs(perm[250:])), 1e-18)) < 0.02,
   f"{100 * np.max(np.abs(y_t[250:] - perm[250:])) / np.max(np.abs(perm[250:])):.2f} % al final")
ok("y al principio NO", float(np.max(np.abs(y_t[:20] - perm[:20]))) > 0.1)

print("\n== 17 · Un filtro ==")
hf = sis.paso_bajo(0.1, 61)
casi("un paso bajo deja pasar la continua entera",
     abs(sis.autovalor(hf, 0.0)), 1.0, 1e-9)
paso = sis.atenuacion_db(hf, 2 * np.pi * 0.05)
corta = sis.atenuacion_db(hf, 2 * np.pi * 0.25)
ok("deja pasar lo bajo y para lo alto", paso > -1.0 and corta < -40,
   f"{paso:.2f} dB a 0.05 y {corta:.1f} dB a 0.25")
mezcla = sis.dos_tonos(0.05, 0.25, 600)
filtrada = np.convolve(mezcla, hf)[100:500]
a_baja = sis.amplitud_de_tono(filtrada, 0.05)
a_alta = sis.amplitud_de_tono(filtrada, 0.25)
ok("y en la señal se ve: sobrevive uno de los dos tonos",
   a_baja > 0.9 and a_alta < 0.02,
   f"0.05 -> {a_baja:.3f}, 0.25 -> {a_alta:.4f}")

print("\n== 18 · Cuando deja de ser lineal ==")
n = np.arange(600)
tono = np.cos(2 * np.pi * 0.03 * n)
ok("un sistema LINEAL no inventa armonicos",
   sis.distorsion_armonica(np.convolve(tono, hf)[100:500], 0.03) < 0.5,
   f"{sis.distorsion_armonica(np.convolve(tono, hf)[100:500], 0.03):.3f} %")
thd = sis.distorsion_armonica(sis.saturar(tono, 0.7), 0.03)
ok("uno que satura SI", thd > 8.0, f"{thd:.1f} % de distorsion")
arm = sis.armonicos(sis.saturar(tono, 0.7), 0.03, 5)
ok("y los armonicos pares casi no salen (la saturacion es impar)",
   arm[1] < 0.02 * arm[0] and arm[2] > 0.05 * arm[0],
   f"2f0 = {arm[1]:.4f}, 3f0 = {arm[2]:.4f}, f0 = {arm[0]:.4f}")

print("\n" + "=" * 62)
print("LAS CIFRAS QUE VAN A PANTALLA")
print("=" * 62)
cifras = [
    ("01 area del pulso", f"{areas[-1]:.3f}"),
    ("02 cola de la respuesta", f"{sis.cola(h)} muestras"),
    ("03 largo de la salida",
     f"{sis.largo_convolucion(40, 48)} muestras"),
    ("04 valor final del escalon", f"{sis.valor_final(h):.3f}"),
    ("05 error de superposicion", f"{lin:.1e} %"),
    ("06 error de invarianza",
     f"{sis.error_invarianza(h, x1, 7):.1e} %"),
    ("07 muestras antes del golpe",
     f"{sis.muestras_antes_de_cero(hnc, 16)}"),
    ("08 suma|h| estable / inestable",
     f"{sis.suma_absoluta(he):.2f} / {sis.suma_absoluta(hi):.0f}"),
    ("09 error al conmutar", f"{sis.error_conmutar(h, h2, x1):.1e} %"),
    ("10 polo del lazo k=1.8", f"{sis.ganancia_lazo(1.8, 0.6):.2f}"),
    ("12 autovalor en w=0.9", f"{abs(sis.autovalor(h, 0.9)):.3f}"),
    ("13 ganancia medida w=0.8", f"{sis.ganancia_medida(h, 0.8):.3f}"),
    ("14 retardo de grupo", f"{np.median(tg[dentro]):.1f} muestras"),
    ("15 amplificacion Q=12", f"x{amp:.1f}"),
    ("16 tiempo de asentamiento", f"{ta} muestras"),
    ("17 atenuacion a 0.25", f"{corta:.1f} decibelios"),
    ("18 distorsion al saturar", f"{thd:.1f} %"),
]
for k, v in cifras:
    print(f"  {k:<32} {v}")

print("\n" + "=" * 62)
print(f"{n_ok} invariantes ok, {len(fallos)} fallos")
if fallos:
    for f in fallos:
        print(f"  - {f}")
sys.exit(1 if fallos else 0)
