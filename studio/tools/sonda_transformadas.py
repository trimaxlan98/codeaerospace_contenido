#!/usr/bin/env python3
"""Invariantes de `transformadas.py`. Se corre ANTES de escribir un clip.

    docker run --rm --network none -v "$PWD:/workspace" -w /workspace \\
        codeaerospace_contenido-manim \\
        python3 studio/tools/sonda_transformadas.py

Por que existe: una transformada mal implementada no se ve mal. Dibuja
una curva razonable, saca una cifra plausible y nadie lo nota hasta que
alguien que sabe ve el reel. Asi que cada una tiene que demostrar aqui una
propiedad que solo cumple si esta bien:

  - las ortonormales, Parseval (la energia no cambia de base);
  - las invertibles, que la vuelta devuelve la ida;
  - Wigner, que sus dos marginales son la señal y su espectro;
  - Hartley, que su espectro es EL de Fourier y no uno parecido;
  - Radon, que reconstruye el fantasma que se le dio.

Y ademas las cifras que van a salir en pantalla: se imprimen todas, para
poder compararlas con lo que luego se lee en el video.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / "content" / "manim_extensions"))
import transformadas as tr  # noqa: E402

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


print("\n== 01 · Serie de Fourier ==")
g = [tr.gibbs_por_ciento(n) for n in (5, 21, 101, 401)]
ok("Gibbs no baja con mas armonicos", max(g) - min(g) < 0.6,
   " ".join(f"{v:.2f}%" for v in g))
casi("Gibbs tiende al 8.949 %", g[-1], 8.949, 0.12, "%")
e = [tr.error_rms_cuadrada(n) for n in (5, 21, 101)]
ok("el error rms SI baja", e[0] > e[1] > e[2],
   " ".join(f"{v:.4f}" for v in e))
_, suma, _ = tr.serie_cuadrada(21)
ok("la suma parcial es impar", abs(np.mean(suma)) < 1e-9)

print("\n== 02 · Fourier: pulso y espectro ==")
for ancho in (0.5, 1.0, 2.0):
    casi(f"nulo de un pulso de {ancho} s cae en 1/{ancho}",
         tr.primer_nulo(*tr.pulso_y_espectro(ancho)[2:]), 1.0 / ancho, 0.02,
         "Hz")
p = [tr.producto_tiempo_banda(a) for a in (0.5, 1.0, 2.0)]
ok("el producto tiempo-banda no cambia", max(p) - min(p) < 0.02,
   " ".join(f"{v:.4f}" for v in p))
casi("y vale 1", p[1], 1.0, 0.02)

print("\n== 03 · DFT y fuga ==")
entero = tr.dft_tono(8, N=64)
roto = tr.dft_tono(8.5, N=64)
ok("un tono entero enciende 1 bin", tr.bins_encendidos(entero) == 1,
   f"{tr.bins_encendidos(entero)} bins")
ok("un tono a medias derrama", tr.bins_encendidos(roto) > 20,
   f"{tr.bins_encendidos(roto)} bins")
casi("el bin del tono entero cae en k=8",
     float(np.argmax(entero)), 8.0, 0.5)

print("\n== 04 · FFT ==")
ok("N=4096: DFT 16 777 216 productos", tr.coste_dft(4096) == 16777216)
ok("N=4096: FFT 24 576 mariposas", tr.coste_fft(4096) == 24576)
casi("ahorro N=4096", tr.ahorro_fft(4096), 682.67, 0.01, "veces")
ok("12 niveles", tr.niveles_fft(4096) == 12)

print("\n== 05 · DCT ==")
b = tr.bloque_ejemplo(8)
C = tr.dct2(b)
casi("Parseval en 2D", float(np.sum(C ** 2)), float(np.sum(b ** 2)), 1e-9)
casi("idct2(dct2(x)) == x", float(np.max(np.abs(tr.idct2(C) - b))), 0.0,
     1e-10)
fr = [tr.energia_en_mayores(b, k) for k in (1, 6, 64)]
ok("la energia acumulada crece", fr[0] < fr[1] < fr[2],
   " ".join(f"{v * 100:.2f}%" for v in fr))
casi("con los 64 esta toda", fr[2], 1.0, 1e-9)
ok("6 de 64 guardan mas del 99 %", fr[1] > 0.99, f"{fr[1] * 100:.3f}%")

print("\n== 06 · Hartley ==")
x = tr.señal_ejemplo(1024)
H = tr.dht(x)
ok("Hartley es real", np.isrealobj(H))
casi("su espectro ES el de Fourier", tr.error_hartley(x), 0.0, 1e-9)
casi("Parseval de Hartley", float(np.sum(H ** 2)),
     float(np.sum(np.abs(np.fft.fft(x)) ** 2)), 1e-6)
ok("memoria: 2N reales vs N", tr.memoria_real_vs_compleja(1024) == (2048,
                                                                    1024))

print("\n== 07 · Walsh-Hadamard ==")
Hd = tr.hadamard(1024)
ok("Hadamard es +-1", set(np.unique(Hd)) == {-1.0, 1.0})
casi("H H^T = N I", float(np.max(np.abs(Hd @ Hd.T - 1024 * np.eye(1024)))),
     0.0, 1e-9)
xs = tr.señal_ejemplo(1024)
casi("la rapida da lo mismo que la matriz",
     float(np.max(np.abs(tr.fwht(xs) - Hd @ xs))), 0.0, 1e-8)
sec = tr.orden_secuencial(64)
cambios = np.sum(np.abs(np.diff(np.sign(tr.hadamard(64)), axis=1)) > 0,
                 axis=1)[sec]
ok("el orden de Walsh ordena por secuencia",
   bool(np.all(np.diff(cambios) >= 0)))
ok("multiplicaciones = 0", tr.coste_wht(1024) == (10240, 0))

print("\n== 08 · Laplace ==")
pol = tr.polos_segundo_orden(1.0, 0.5)
casi("parte real de los polos", float(np.real(pol[0])), -0.5, 1e-12)
casi("parte imaginaria", float(np.imag(pol[0])), 0.8660254, 1e-6)
med = tr.sobreimpulso_medido(1.0, 0.5)
pre = tr.sobreimpulso_desde_polos(0.5)
casi("los polos PREDICEN el sobreimpulso medido", med, pre, 0.15, "%")
casi("y vale 16.3 %", pre, 16.303, 0.01, "%")
_, y = tr.escalon_segundo_orden(1.0, 0.5)
casi("el escalon acaba en 1", float(y[-1]), 1.0, 1e-3)

print("\n== 09 · Z ==")
casi("polo 0.90: se apaga", tr.crecimiento(0.90), 0.90 ** 59, 1e-9)
ok("polo 1.05: explota", tr.crecimiento(1.05) > 15,
   f"x{tr.crecimiento(1.05):.1f}")
ok("el umbral es el radio 1", tr.radio_polo(0.9) < 1 < tr.radio_polo(1.05))

print("\n== 10 · Chirp-Z ==")
xz = tr.dos_tonos(20.0, 21.6, N=256)
casi("czt sobre la circunferencia entera == DFT",
     float(np.max(np.abs(
         tr.czt(xz, 256, np.exp(-2j * np.pi / 256), 1.0)
         - np.fft.fft(xz)))), 0.0, 1e-8)
dft = np.abs(np.fft.rfft(xz))
ok("el maximo de la DFT cae en un ENTERO y falla",
   abs(float(np.argmax(dft)) - 21.6) > 0.4,
   f"la DFT dice {np.argmax(dft)}, el tono esta en 21.6")
z = tr.zoom_czt(xz, 21.0, 22.0, M=512)
pico = tr.pico_interpolado(z, 21.0, 22.0)
casi("la chirp-Z lo situa donde esta", pico, 21.6, 0.02, "ciclos")
casi("factor de zoom", tr.factor_zoom(256, 19.0, 21.0, 256), 128.0, 1e-9)
zx = tr.zoom_czt(xz, 19.0, 23.0, M=512)
picos = int(np.sum((zx[1:-1] > zx[:-2]) & (zx[1:-1] > zx[2:])
                   & (zx[1:-1] > 0.4 * np.max(zx))))
ok("y en el arco se ven los dos tonos", picos == 2, f"{picos}")

print("\n== 11 · STFT y Gabor ==")
prods = [tr.producto_gabor(L) for L in (64, 128, 256, 512)]
ok("el producto no depende del tamaño de la ventana",
   max(prods) - min(prods) < 1e-3, " ".join(f"{v:.5f}" for v in prods))
casi("y toca el limite de Gabor 1/(4 pi)", prods[2], tr.LIMITE_GABOR,
     2e-3)
st1, sf1 = tr.dispersion_ventana(64)
st2, sf2 = tr.dispersion_ventana(512)
ok("ventana larga: mejor en frecuencia, peor en tiempo",
   st2 > st1 and sf2 < sf1,
   f"64: {st1:.4f}s {sf1:.1f}Hz | 512: {st2:.4f}s {sf2:.1f}Hz")
tt, ff, S = tr.stft(tr.chirp(40, 400)[1], 128, 32)
ok("el espectrograma de un chirp sube",
   float(ff[np.argmax(S[:, -3])]) > float(ff[np.argmax(S[:, 2])]),
   f"{ff[np.argmax(S[:, 2])]:.0f} -> {ff[np.argmax(S[:, -3])]:.0f} Hz")

print("\n== 12 · Wavelet de Haar ==")
xs = tr.señal_con_salto(512)
cf = tr.coeficientes_haar(xs)
casi("Parseval de Haar", float(np.sum(cf ** 2)), float(np.sum(xs ** 2)),
     1e-8)
ok("Haar da N coeficientes", cf.size == 512, f"{cf.size}")
cfo = tr.coefs_fourier_ortonormales(xs)
casi("Parseval de la base de Fourier real", float(np.sum(cfo ** 2)),
     float(np.sum(xs ** 2)), 1e-8)
ok("y tambien N", cfo.size == 512, f"{cfo.size}")
nh = tr.cuantos_para_energia(cf, 0.99)
nf = tr.cuantos_para_energia(cfo, 0.99)
ok("Haar necesita muchos menos que Fourier", nh < nf, f"Haar {nh}, "
   f"Fourier {nf}")

print("\n== 13 · Wigner y la fraccional ==")
nn = np.arange(256)
g13 = np.exp(-0.5 * ((nn - 128) / 18.0) ** 2) * np.cos(2 * np.pi * 0.15 * nn)
z13 = tr.analitica(g13)
W13 = tr.wigner(g13)
ok("la distribucion de Wigner es real", np.isrealobj(W13))
mt = np.sum(W13, axis=0)
casi("marginal en tiempo == |z(t)|^2",
     float(np.max(np.abs(mt - np.abs(z13) ** 2))), 0.0, 1e-9)
for f0 in (0.05, 0.10, 0.20):
    Wt = tr.wigner(np.exp(2j * np.pi * f0 * nn))
    bin_medido = int(np.argmax(np.sum(Wt, axis=1))) - Wt.shape[0] // 2
    casi(f"un tono de {f0} cae donde toca",
         float(bin_medido),
         tr.ESCALA_FRECUENCIA_WIGNER * f0 * Wt.shape[0], 1.0, "bins")
p0 = tr.proyeccion_wigner(W13, 0.0)
casi("la sombra a 0 grados es la señal en el tiempo",
     float(np.corrcoef(p0, np.abs(z13) ** 2)[0, 1]), 1.0, 1e-3)
p90 = tr.proyeccion_wigner(W13, 90.0)
Z13 = np.abs(np.fft.fft(z13)) ** 2
casi("y a 90 grados es su espectro",
     float(abs(np.argmax(p90) - p90.size // 2)),
     tr.ESCALA_FRECUENCIA_WIGNER * (np.argmax(Z13) / Z13.size) * p90.size,
     2.0, "bins")
for beta in (0.3, 0.6, 1.0):
    _, xb = tr.chirp_complejo(256, beta)
    Wb = tr.wigner(xb)
    ang = np.linspace(1.0, 179.0, 179)
    med = float(ang[int(np.argmax(tr.barrido_wigner(Wb, ang)))])
    casi(f"chirp beta={beta}: el giro que lo endereza",
         med, tr.angulo_optimo(beta), 1.2, "grados")
_, x13 = tr.chirp_complejo(256, 0.6)
W6 = tr.wigner(x13)
cr = np.array([np.argmax(W6[:, i]) for i in range(W6.shape[1])])
pend = float(np.polyfit(np.arange(W6.shape[1])[40:-40], cr[40:-40], 1)[0])
casi("la cresta tiene la pendiente deducida", pend,
     tr.pendiente_cresta(0.6), 0.05, "bins/columna")
c_opt = tr.concentracion(tr.proyeccion_wigner(W6, tr.angulo_optimo(0.6)))
c_90 = tr.concentracion(tr.proyeccion_wigner(W6, 90.0))
ok("y ahi concentra muchisimo mas que Fourier", c_opt > 20 * c_90,
   f"{c_opt:.4f} vs {c_90:.4f}")

print("\n== 14 · Hilbert ==")
t14, env, x14 = tr.señal_modulada()
z14 = tr.analitica(x14)
casi("la parte real de la analitica es la señal",
     float(np.max(np.abs(np.real(z14) - x14))), 0.0, 1e-10)
err = tr.error_envolvente()
ok("la envolvente se recupera sin conocerla", 0.2 < err < 6.0,
   f"{err:.2f} %")
ok("la envolvente tiene un ataque abrupto",
   float(np.argmax(env)) / env.size < 0.10,
   f"pico en el {100 * np.argmax(env) / env.size:.0f} % de la nota")
Z = np.fft.fft(z14)
ok("la analitica no tiene frecuencias negativas",
   float(np.max(np.abs(Z[len(Z) // 2 + 1:]))) < 1e-9)

print("\n== 15 · Mellin ==")
f1 = tr.forma_ejemplo(1.0)
f3 = tr.forma_ejemplo(3.0)
pm1, pm3 = tr.pico_mellin(f1), tr.pico_mellin(f3)
pf1, pf3 = tr.pico_fourier(f1), tr.pico_fourier(f3)
ok("el pico de Mellin NO se mueve al escalar x3", pm1 == pm3,
   f"{pm1} vs {pm3}")
ok("el de Fourier SI se mueve", abs(pf1 - pf3) > 0.05,
   f"{pf1:.3f} vs {pf3:.3f} Hz")
m1 = tr.mellin_escala(f1)
m3 = tr.mellin_escala(f3)
rel = float(np.max(np.abs(m1 / max(np.max(m1), 1e-12)
                          - m3 / max(np.max(m3), 1e-12))))
ok("y el modulo entero es casi el mismo", rel < 0.06, f"{rel:.4f}")

print("\n== 16 · Radon ==")
img = tr.fantasma(96)
ang8 = np.linspace(0, 180, 8, endpoint=False)
ang180 = np.linspace(0, 180, 180, endpoint=False)
sino = tr.radon(img, ang180)
ok("el sinograma tiene una columna por angulo", sino.shape == (96, 180),
   str(sino.shape))
casi("cada sombra conserva la masa del objeto",
     float(np.std(np.sum(sino, axis=0)) / np.mean(np.sum(sino, axis=0))),
     0.0, 0.02)
e8 = tr.error_reconstruccion(8, n=96)
e180 = tr.error_reconstruccion(180, n=96)
ok("mas angulos, menos error", e180 < e8 / 2,
   f"8: {e8 * 100:.1f}% | 180: {e180 * 100:.1f}%")
ok("con 180 la reconstruccion es buena", e180 < 0.12,
   f"{e180 * 100:.2f} %")

print("\n== 17 · Hough ==")
px, py = tr.nube_con_recta(24, 60)
th, rho, acc = tr.hough(px, py)
votos, fi, ci = tr.pico_hough(acc)
ok("el pico junta casi todos los puntos de la recta", votos >= 20,
   f"{votos} votos de 24 alineados")
ok("y destaca sobre el ruido", votos > 3 * np.median(acc[acc > 0]),
   f"pico {votos}, mediana {np.median(acc[acc > 0]):.0f}")
m_rec, b_rec = 0.6, -0.2
th_esp = float(np.arctan2(1.0, -m_rec)) % np.pi
casi("y el angulo del pico es el de la recta",
     float(th[ci]), th_esp, 0.05, "rad")

print("\n== 18 · Karhunen-Loeve ==")
nube = tr.nube_correlada(220, giro=28.0)
val, vec, ang = tr.base_kl(nube)
ok("los valores propios vienen ordenados", val[0] > val[1],
   f"{val[0]:.4f} > {val[1]:.4f}")
casi("la base encuentra el giro de la nube", ang, 28.0, 3.0, "grados")
casi("los ejes son perpendiculares", float(vec[:, 0] @ vec[:, 1]), 0.0,
     1e-12)
v1 = tr.varianza_explicada(nube, 1)
ok("una componente guarda casi toda la varianza", v1 > 0.9,
   f"{v1 * 100:.2f} %")
casi("con las dos esta toda", tr.varianza_explicada(nube, 2), 1.0, 1e-12)

print("\n" + "=" * 62)
print("LAS CIFRAS QUE VAN A PANTALLA")
print("=" * 62)
cifras = [
    ("01 Gibbs (21 armonicos)", f"{tr.gibbs_por_ciento(21):.2f} %"),
    ("01 Gibbs (201 armonicos)", f"{tr.gibbs_por_ciento(201):.2f} %"),
    ("02 producto tiempo-banda", f"{tr.producto_tiempo_banda(1.0):.3f}"),
    ("03 bins encendidos k=8", f"{tr.bins_encendidos(tr.dft_tono(8)):d}"),
    ("03 bins encendidos k=8.5",
     f"{tr.bins_encendidos(tr.dft_tono(8.5)):d}"),
    ("04 ahorro FFT N=4096", f"{tr.ahorro_fft(4096):.0f} veces"),
    ("04 productos DFT", f"{tr.coste_dft(4096):,}"),
    ("04 mariposas FFT", f"{tr.coste_fft(4096):,}"),
    ("05 energia en 6 de 64",
     f"{tr.energia_en_mayores(tr.bloque_ejemplo(), 6) * 100:.2f} %"),
    ("06 error Hartley vs Fourier", f"{tr.error_hartley(x):.2e}"),
    ("07 multiplicaciones WHT", f"{tr.coste_wht(1024)[1]:d}"),
    ("07 sumas WHT", f"{tr.coste_wht(1024)[0]:,}"),
    ("08 sobreimpulso medido", f"{tr.sobreimpulso_medido():.2f} %"),
    ("08 sobreimpulso predicho",
     f"{tr.sobreimpulso_desde_polos(0.5):.2f} %"),
    ("09 crecimiento polo 1.05", f"x{tr.crecimiento(1.05):.1f}"),
    ("10 factor de zoom", f"{tr.factor_zoom(256, 19.0, 21.0, 256):.0f}"),
    ("10 pico DFT / chirp-Z", f"{np.argmax(dft)} / {pico:.2f}"),
    ("11 producto de Gabor", f"{tr.producto_gabor(256):.5f}"),
    ("12 coefs Haar / Fourier", f"{nh} / {nf}"),
    ("13 giro optimo (beta=0.6)", f"{tr.angulo_optimo(0.6):.1f} grados"),
    ("13 concentracion ahi / a 90", f"{c_opt:.3f} / {c_90:.3f}"),
    ("14 error de envolvente", f"{tr.error_envolvente():.2f} %"),
    ("15 pico Mellin x1 / x3", f"{pm1} / {pm3}"),
    ("16 error con 180 angulos", f"{e180 * 100:.2f} %"),
    ("17 votos en el pico", f"{votos}"),
    ("18 varianza en 1 componente", f"{v1 * 100:.2f} %"),
]
for k, v in cifras:
    print(f"  {k:<32} {v}")

print("\n" + "=" * 62)
print(f"{n_ok} invariantes ok, {len(fallos)} fallos")
if fallos:
    for f in fallos:
        print(f"  - {f}")
sys.exit(1 if fallos else 0)
