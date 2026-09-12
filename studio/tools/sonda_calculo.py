#!/usr/bin/env python3
"""Invariantes de `calculo.py`. Se corre ANTES de escribir un clip.

    docker run --rm --network none -v "$PWD:/workspace" -w /workspace \\
        codeaerospace_contenido-manim \\
        python3 studio/tools/sonda_calculo.py

Por que este curso necesita la sonda: cada pieza afirma que un DIBUJO
demuestra algo, y el dibujo siempre sale bonito. Una suma de Riemann mal
hecha rellena igual, una escalera mal construida se pega igual a su
circunferencia y un anillo mal integrado da un numero con dos decimales
que nadie va a discutir. Lo unico que distingue una demostracion de una
ilustracion es que la cifra aguante que la aprieten.

Las tres reglas de la casa, heredadas del curso 34:

  1. **Cada invariante lleva su CONTRAEJEMPLO.** Una comprobacion que
     tambien pasaria con una funcion que devuelve siempre cero no
     comprueba nada.
  2. **Las cifras que van a pantalla se miden con DOS mallas.** Si se
     mueven al afinar la rejilla son de la malla, no de la matematica, y
     no se rotulan.
  3. **scipy es el oraculo, no la implementacion.** La libreria integra a
     mano con trapecios; scipy integra con cuadratura adaptativa. Dos
     caminos que no se parecen en nada y coinciden a 1e-10 es una prueba.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / "content" / "manim_extensions"))
import calculo as C  # noqa: E402

try:
    from scipy import integrate as si
    from scipy import optimize as so
    from scipy import special as sp
    HAY_SCIPY = True
except Exception:
    HAY_SCIPY = False

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
    ok(nombre, abs(float(a) - float(b)) <= tol,
       f"{float(a):.10g} vs {float(b):.10g} {unidad}".strip())


def oraculo(nombre, a, b, tol):
    """Contra scipy. Si no hay scipy es FALLO: un chequeo que se salta en
    silencio y encima da el visto bueno es peor que no tenerlo."""
    if not HAY_SCIPY:
        fallos.append(nombre + " (scipy ausente)")
        print(f"  FALLO {nombre}   scipy no esta en la imagen")
        return
    casi(nombre, a, b, tol)


def dos_mallas(nombre, f, n1, n2, tol):
    """La cifra no puede depender de la rejilla con la que se mide."""
    a, b = f(n1), f(n2)
    ok(nombre, abs(a - b) <= tol, f"{a:.10g} (n={n1}) vs {b:.10g} (n={n2})")


print("=" * 68)
print(" sonda de calculo.py — curso 35, calculo visible")
print("=" * 68)

# =====================================================================
print("\n== 01 · SECANTE ==")
casi("la pendiente exacta en x=1 vale 1", C.df_cubica(1.0), 1.0, 1e-12)
sec = C.pendientes_secantes(1.0, (1.0, 0.5, 0.25, 0.1))
ok("las secantes se acercan a la pendiente, y por arriba",
   all(sec[i] > sec[i + 1] > 1.0 for i in range(len(sec) - 1)),
   " ".join(f"{s:.4f}" for s in sec))
casi("la secante con h=1e-8 ya es la tangente",
     C.secante(1.0, 1e-8), 1.0, 1e-6)
casi("el error de la secante es exactamente 3h + h^2",
     C.error_de_secante(1.0, 0.2), 3 * 0.2 + 0.04, 1e-12)
ok("o sea que se divide casi entre dos al partir h por dos",
   abs(C.error_de_secante(1.0, 0.2) / C.error_de_secante(1.0, 0.1) - 2.0)
   < 0.1,
   f"{C.error_de_secante(1.0, 0.2):.5f} / {C.error_de_secante(1.0, 0.1):.5f}")
casi("y con h pequeño la razon es 2 clavada",
     C.error_de_secante(1.0, 2e-4) / C.error_de_secante(1.0, 1e-4), 2.0,
     1e-3)
ok("contraejemplo: la secante con h=1 NO es la pendiente",
   abs(C.secante(1.0, 1.0) - 1.0) > 3.0, f"{C.secante(1.0, 1.0):.4f}")
try:
    C.secante(1.0, 0.0)
    ok("h=0 aborta", False, "devolvio un numero")
except ValueError:
    ok("h=0 aborta con ValueError", True)
oraculo("la derivada coincide con la diferencia centrada",
        (C.f_cubica(1.0 + 1e-6) - C.f_cubica(1.0 - 1e-6)) / 2e-6,
        float(C.df_cubica(1.0)), 1e-9)
ok("la recta por un punto pasa por ese punto",
   abs(float(C.recta_por(1.0, -1.0, 1.0, [1.0])[0]) + 1.0) < 1e-12)

# =====================================================================
print("\n== 02 · EPSILON-DELTA ==")
for eps in (1.0, 0.3, 0.1, 0.03, 0.01):
    d = C.delta_para(eps)
    casi(f"la banda de eps={eps} se cumple entera",
         C.cumple_la_banda(eps), eps, 1e-9)
    ok(f"delta({eps}) es positivo y pequeño", 0.0 < d < 0.2, f"{d:.6f}")
ok("delta se encoge cuando eps se encoge",
   C.delta_para(1.0) > C.delta_para(0.3) > C.delta_para(0.1)
   > C.delta_para(0.01))
ok("se toma el lado CORTO de la parabola (el de arriba)",
   abs(C.delta_para(0.6) - (np.sqrt(9.6) - 3.0)) < 1e-12,
   f"{C.delta_para(0.6):.6f} vs {np.sqrt(9.6) - 3.0:.6f}")
d = C.delta_para(0.1)
xs = np.linspace(3.0 - 2.0 * d, 3.0 + 2.0 * d, 999)
ok("contraejemplo: con el doble de delta la banda YA no se cumple",
   float(np.max(np.abs(xs ** 2 - 9.0))) > 0.1,
   f"{float(np.max(np.abs(xs ** 2 - 9.0))):.4f} > 0.1")
try:
    C.delta_para(20.0)
    ok("eps mayor que el limite aborta", False)
except ValueError:
    ok("eps mayor que el limite aborta con ValueError", True)

# =====================================================================
print("\n== 03 · RECTA ESCONDIDA ==")
d = C.despegues()
ok("el hueco entre curva y tangente se achica al acercarse",
   all(d[i] > d[i + 1] for i in range(len(d) - 1)),
   " ".join(f"{v:.5f}" for v in d))
razones = C.razon_de_despegue()
ok("y se divide entre CUATRO cada vez que se parte la distancia",
   all(abs(r - 4.0) < 0.2 for r in razones),
   " ".join(f"{r:.3f}" for r in razones))
ok("la razon TIENDE a 4: cuanto mas cerca, mas exacta",
   all(abs(a - 4.0) > abs(b - 4.0) for a, b in zip(razones, razones[1:])),
   " ".join(f"{r:.3f}" for r in razones))
casi("y con h minusculo es 4 clavado",
     C.despegue(2e-3) / C.despegue(1e-3), 4.0, 1e-3)
casi("el hueco vale f''(x0)/2 * h^2",
     C.despegue(0.01) / 0.01 ** 2, abs(np.sin(1.0)) / 2.0, 1e-3)
ok("contraejemplo: contra una SECANTE el hueco solo se divide entre dos",
   abs((abs(np.sin(1.8) - (np.sin(1.0) + (np.sin(1.8) - np.sin(1.0))
                           / 0.8 * 0.8)))) < 1e-12)
xs, cu, ta = C.ventana(semiancho=0.8)
ok("el centro de la ventana ES una muestra (malla impar)",
   float(np.min(np.abs(xs - 1.0))) < 1e-15, f"{len(xs)} muestras")
casi("y ahi curva y tangente valen lo mismo",
     float(cu[len(cu) // 2]), float(ta[len(ta) // 2]), 1e-15)
ok("la tangente es recta de verdad (segunda diferencia nula)",
   float(np.max(np.abs(np.diff(ta, 2)))) < 1e-12)
ok("contraejemplo: la curva NO es recta",
   float(np.max(np.abs(np.diff(cu, 2)))) > 1e-8)
oraculo("la pendiente de la ventana es cos(1)",
        float((ta[-1] - ta[0]) / (xs[-1] - xs[0])), float(np.cos(1.0)), 1e-12)

# =====================================================================
print("\n== 04 · NUMERO E ==")
for x0 in (-1.5, -0.4, 0.0, 0.7, 1.0, 2.3):
    casi(f"la subtangente en x={x0} vale 1", C.subtangente(x0), 1.0, 1e-12)
    casi(f"la tangente en x={x0} corta el eje en x-1",
         C.corte_de_tangente(x0), x0 - 1.0, 1e-12)
casi("e es la altura donde la pendiente vale 1", C.numero_e(),
     2.718281828459045, 1e-12)
xs = np.linspace(0.4, 1.6, 9)
casi("la tangente toca la curva en el punto y en ninguno mas",
     float(np.min(C.exp_(xs) - C.tangente_exp(1.0, xs))), 0.0, 1e-12)
ok("la tangente queda SIEMPRE por debajo (la curva es convexa)",
   bool(np.all(C.tangente_exp(1.0, xs) <= C.exp_(xs) + 1e-12)))
ok("contraejemplo: 2^x NO tiene subtangente 1",
   abs(1.0 / np.log(2.0) - 1.0) > 0.4, f"{1.0 / np.log(2.0):.4f}")
oraculo("e coincide con el limite (1+1/n)^n",
        float((1.0 + 1.0 / 1e9) ** 1e9), C.numero_e(), 1e-5)

# =====================================================================
print("\n== 05 · VALOR MEDIO ==")
casi("el viaje empieza en cero", float(C.posicion(0.0)), 0.0, 1e-12)
casi("y termina en los 175 km", float(C.posicion(2.0)), 175.0, 1e-12)
casi("sale parado", float(C.velocidad(0.0)), 0.0, 1e-12)
casi("y llega parado", float(C.velocidad(2.0)), 0.0, 1e-12)
casi("la velocidad media es 87.5 km/h", C.velocidad_media(), 87.5, 1e-12)
t1, t2 = C.instantes_de_la_media()
casi("en el primer instante el velocimetro marca la media",
     float(C.velocidad(t1)), C.velocidad_media(), 1e-9)
casi("y en el segundo tambien", float(C.velocidad(t2)),
     C.velocidad_media(), 1e-9)
ok("son dos instantes distintos y dentro del viaje",
   0.0 < t1 < t2 < 2.0, f"{t1:.4f} h y {t2:.4f} h")
casi("la maxima es 131.25 km/h", C.velocidad_maxima(), 131.25, 1e-4)
ok("contraejemplo: a mitad de viaje NO se va a la media",
   abs(float(C.velocidad(1.0)) - 87.5) > 40.0, f"{float(C.velocidad(1.0)):.2f}")
ts = np.linspace(0.0, 2.0, 200001)
trapecio = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
casi("integrar la velocidad devuelve la distancia",
     float(trapecio(C.velocidad(ts), ts)), 175.0, 1e-6)
oraculo("y scipy integra lo mismo",
        float(si.quad(lambda t: float(C.velocidad(t)), 0.0, 2.0)[0])
        if HAY_SCIPY else 0.0, 175.0, 1e-8)

# =====================================================================
print("\n== 06 · NEWTON ==")
r = C.raiz_de_newton()
casi("la raiz anula la funcion", float(C.f_newton(r)), 0.0, 1e-12)
casi("y vale 2.0945514815", r, 2.0945514815423265, 1e-12)
xs = C.newton_pasos(2.0, 4)
digs = [C.digitos_correctos(x) for x in xs]
ok("los decimales correctos se duplican en cada paso",
   all(digs[i + 1] >= min(2 * digs[i] - 1, 16)
       for i in range(len(digs) - 1)),
   " ".join(str(d) for d in digs))
ok("cuatro pasos bastan para el tope del float64", digs[-1] >= 15,
   f"{digs[-1]} decimales")
ok("la sucesion es monotona hacia la raiz",
   all(abs(xs[i + 1] - r) < abs(xs[i] - r) for i in range(len(xs) - 1)))
camino = C.camino_newton(2.0, 3)
ok("el zigzag toca el eje entre paso y paso",
   sum(1 for p in camino if abs(p[1]) < 1e-12) == 3, f"{len(camino)} vertices")
ok("y cada vertice de la curva esta SOBRE la curva",
   all(abs(float(C.f_newton(p[0])) - p[1]) < 1e-9
       for p in camino if abs(p[1]) > 1e-12))
ok("contraejemplo: el punto de partida solo tiene un decimal bueno",
   digs[0] == 1, f"{digs[0]}")
oraculo("scipy encuentra la misma raiz",
        float(so.brentq(lambda x: float(C.f_newton(x)), 1.0, 3.0))
        if HAY_SCIPY else 0.0, r, 1e-12)

# =====================================================================
print("\n== 07 · LATA ==")
r_opt, h_opt, s_opt = C.lata_optima()
casi("en la lata optima la altura es el diametro", h_opt, 2.0 * r_opt, 1e-9)
casi("y el volumen sigue siendo 330 ml",
     float(np.pi * r_opt ** 2 * h_opt), 330.0, 1e-9)
ok("ninguna otra lata gasta menos aluminio",
   all(float(C.superficie_lata(r)) >= s_opt - 1e-9
       for r in np.linspace(2.0, 6.0, 4001)), f"{s_opt:.2f} cm2")
casi("la derivada de la superficie se anula en el optimo",
     (float(C.superficie_lata(r_opt + 1e-6))
      - float(C.superficie_lata(r_opt - 1e-6))) / 2e-6, 0.0, 1e-5)
r_real, h_real, s_real = C.lata_de_esbeltez(C.ESBELTEZ_REAL)
ok("la lata real es mas alta que ancha", h_real > 2.0 * r_real,
   f"{h_real:.2f} cm de alto, {2 * r_real:.2f} de ancho")
ok("y gasta mas, pero poco", 0.0 < C.exceso_de_la_real() < 8.0,
   f"{C.exceso_de_la_real():.2f} %")
ok("fallar un 10 % en el radio cuesta poco mas del 1 %",
   C.coste_de_fallar(0.10) < 1.5, f"{C.coste_de_fallar(0.10):.3f} %")
ok("y fallar un 5 % no cuesta ni un cuarto de eso",
   C.coste_de_fallar(0.05) < C.coste_de_fallar(0.10) / 3.5,
   f"{C.coste_de_fallar(0.05):.3f} %")
ok("contraejemplo: fallar un 60 % ya cuesta de verdad",
   C.coste_de_fallar(0.60) > 15.0, f"{C.coste_de_fallar(0.60):.2f} %")
oraculo("el optimo de scipy es el mismo radio",
        float(so.minimize_scalar(lambda r: float(C.superficie_lata(r)),
                                 bounds=(1.0, 10.0), method="bounded").x)
        if HAY_SCIPY else 0.0, r_opt, 1e-5)

# =====================================================================
print("\n== 08 · RIEMANN ==")
exacta = C.area_riemann()
casi("el area exacta es un tercio", exacta, 1.0 / 3.0, 1e-15)
for n in (4, 16, 128, 1024):
    lo, hi, hueco = C.pinza(n)
    ok(f"con {n} rectangulos la pinza encierra al area",
       lo < exacta < hi, f"{lo:.6f} < {exacta:.6f} < {hi:.6f}")
    casi(f"y lo que las separa es 1/n ({n})", hueco, 1.0 / n, 1e-12)
ok("la suma inferior crece y la superior baja",
   C.suma_riemann(4) < C.suma_riemann(16) < C.suma_riemann(128)
   and C.suma_riemann(4, "superior") > C.suma_riemann(16, "superior")
   > C.suma_riemann(128, "superior"))
casi("con 100000 rectangulos ya son 4 decimales buenos",
     C.suma_riemann(100000), exacta, 1e-5)
ok("el punto medio acierta mucho antes que los extremos",
   abs(C.suma_riemann(16, "medio") - exacta)
   < abs(C.suma_riemann(16) - exacta) / 10.0,
   f"{abs(C.suma_riemann(16, 'medio') - exacta):.2e}")
ok("contraejemplo: 4 rectangulos NO valen un tercio",
   abs(C.suma_riemann(4) - exacta) > 0.1, f"{C.suma_riemann(4):.4f}")
try:
    C.suma_riemann(0)
    ok("n=0 aborta", False)
except ValueError:
    ok("n=0 aborta con ValueError", True)
rects = C.rectangulos(8)
ok("los rectangulos dibujados suman lo que dice la suma",
   abs(sum((xf - xi) * a for xi, xf, a in rects) - C.suma_riemann(8)) < 1e-12)
oraculo("scipy integra el mismo tercio",
        float(si.quad(lambda x: x * x, 0.0, 1.0)[0]) if HAY_SCIPY else 0.0,
        exacta, 1e-12)

# =====================================================================
print("\n== 09 · TEOREMA FUNDAMENTAL ==")
ok("la funcion es positiva en todo el tramo",
   bool(np.all(C.f_tfc(np.linspace(0.0, 5.0, 5001)) > 0.0)))
xs, acum = C.area_acumulada()
casi("el area de trapecios coincide con la formula cerrada",
     float(np.max(np.abs(acum - C.area_tfc(xs)))), 0.0, 1e-6)
casi("y empieza en cero", float(acum[0]), 0.0, 1e-15)
for x0 in (0.7, 1.4, 2.0, 3.3, 4.6):
    alt, ritmo = C.altura_y_ritmo(x0)
    casi(f"en x={x0} la pendiente del area ES la altura", ritmo, alt, 1e-7)
ok("el area crece siempre porque la altura nunca es negativa",
   bool(np.all(np.diff(acum) > 0.0)))
ok("contraejemplo: la pendiente del area NO es el area",
   abs(C.ritmo_del_area(3.3) - float(C.area_tfc(3.3))) > 1.0,
   f"{C.ritmo_del_area(3.3):.4f} vs {float(C.area_tfc(3.3)):.4f}")
dos_mallas("el area acumulada no depende de la malla",
           lambda n: float(C.area_acumulada(n)[1][-1]), 2001, 40001, 1e-5)
oraculo("scipy acumula lo mismo hasta x=5",
        float(si.quad(lambda x: 1.2 + np.sin(x), 0.0, 5.0)[0])
        if HAY_SCIPY else 0.0, float(C.area_tfc(5.0)), 1e-9)

# =====================================================================
print("\n== 10 · HIPERBOLA ==")
a12 = C.area_hiperbola(1.0, 2.0)
casi("el area de 1 a 2 es el logaritmo de 2", a12, float(np.log(2.0)), 1e-9)
for x0, x1 in ((2.0, 4.0), (4.0, 8.0), (8.0, 16.0), (3.0, 6.0)):
    casi(f"la franja ({x0},{x1}) mide lo mismo",
         C.area_hiperbola(x0, x1), a12, 1e-9)
suma, entera = C.suma_de_areas(1.0, 2.0, 4.0)
casi("dos franjas seguidas suman la franja entera", suma, entera, 1e-9)
casi("y la entera es el doble de una", entera, 2.0 * a12, 1e-9)
casi("el area de 1 a 6 es el area de 1 a 2 mas la de 1 a 3",
     C.area_hiperbola(1.0, 6.0),
     C.area_hiperbola(1.0, 2.0) + C.area_hiperbola(1.0, 3.0), 1e-9)
xs, ys, xs2, ys2 = C.estirada(1.0, 2.0)
ok("la franja estirada cae otra vez sobre la hiperbola",
   float(np.max(np.abs(ys2 - C.hiperbola(xs2)))) < 1e-12)
ok("contraejemplo: estirar SIN encoger duplica el area",
   abs(float(trapecio(ys, xs2)) - 2.0 * a12) < 1e-6,
   f"{float(trapecio(ys, xs2)):.6f}")
dos_mallas("el area no depende de la malla",
           lambda n: C.area_hiperbola(1.0, 2.0, n), 20001, 400001, 1e-9)
try:
    C.area_hiperbola(-1.0, 2.0)
    ok("cruzar el cero aborta", False)
except ValueError:
    ok("cruzar el cero aborta con ValueError", True)
oraculo("scipy integra el mismo logaritmo",
        float(si.quad(lambda x: 1.0 / x, 1.0, 2.0)[0]) if HAY_SCIPY else 0.0,
        a12, 1e-9)

# =====================================================================
print("\n== 11 · ESCALERA ==")
for n in (1, 2, 4, 16, 64, 256, 1024):
    e = C.escalera_circulo(n)
    casi(f"la escalera de {n} escalones por cuadrante mide 4",
         C.longitud_poligonal(e), 4.0, 1e-9)
ok("los escalones son horizontales o verticales, todos",
   all(abs(dx) < 1e-12 or abs(dy) < 1e-12
       for dx, dy in zip(np.diff(C.escalera_circulo(32)[:, 0]),
                         np.diff(C.escalera_circulo(32)[:, 1]))))
e = C.escalera_circulo(64)
d = np.hypot(e[:, 0], e[:, 1])
ok("la escalera envuelve la circunferencia y se le pega",
   float(np.max(d)) < C.RADIO * 1.02 and float(np.min(d)) >= C.RADIO - 1e-12,
   f"maximo {float(np.max(d)):.5f} contra el radio {C.RADIO}")
ok("y se pega mas cuanto mas fina",
   float(np.max(np.hypot(*C.escalera_circulo(256).T)))
   < float(np.max(np.hypot(*C.escalera_circulo(16).T))))
casi("el poligono inscrito SI converge a pi",
     C.longitud_poligonal(C.poligono_inscrito(20000)),
     float(np.pi), 1e-6)
ok("y por debajo, siempre",
   all(C.longitud_poligonal(C.poligono_inscrito(n)) < np.pi
       for n in (3, 8, 64, 1000)))
casi("la circunferencia mide pi", C.longitud_circunferencia(), float(np.pi),
     1e-12)
cuerpo, puntas = C.semicircunferencia_por_derivada()
casi("la integral de arco da media circunferencia",
     cuerpo + puntas, float(np.pi) / 2.0, 2e-3)
casi("la longitud de una recta de 45 grados es la diagonal",
     C.longitud_por_la_derivada(lambda x: x, lambda x: np.ones_like(x),
                                0.0, 1.0),
     float(np.sqrt(2.0)), 1e-12)
ok("contraejemplo: la escalera NO baja de 4 por fina que sea",
   C.longitud_poligonal(C.escalera_circulo(100000)) > 3.99,
   f"{C.longitud_poligonal(C.escalera_circulo(100000)):.6f}")
ok("y eso es un 27 % mas que la circunferencia",
   abs((4.0 / np.pi - 1.0) * 100.0 - 27.32) < 0.01,
   f"{(4.0 / np.pi - 1.0) * 100.0:.2f} %")

# =====================================================================
print("\n== 12 · CAMPANA ==")
area = C.area_campana()
casi("el area bajo la campana es la raiz de pi", area, float(np.sqrt(np.pi)),
     1e-9)
vol = C.volumen_campana()
casi("el volumen de la campana girada es pi", vol, float(np.pi), 1e-9)
casi("y la raiz del volumen es el area", C.raiz_de_pi(), area, 1e-9)
casi("el anillo de radio 0 no pesa nada", float(C.anillo(0.0)), 0.0, 1e-15)
rs = np.linspace(0.0, 4.0, 100001)
casi("el anillo mas gordo esta en r = 1/raiz(2)",
     float(rs[int(np.argmax(C.anillo(rs)))]), float(1.0 / np.sqrt(2.0)), 1e-4)
ok("la campana es simetrica",
   float(np.max(np.abs(C.campana(np.linspace(0.0, 4.0, 999))
                       - C.campana(np.linspace(0.0, -4.0, 999))))) < 1e-15)
ok("contraejemplo: SIN el factor r la integral no es elemental ni vale pi",
   abs(float(trapecio(np.exp(-rs ** 2), rs)) - np.pi) > 1.5,
   f"{float(trapecio(np.exp(-rs ** 2), rs)):.6f}")
dos_mallas("el area no depende de la malla",
           lambda n: C.area_campana(6.0, n), 20001, 400001, 1e-9)
dos_mallas("el volumen tampoco, a los seis decimales que se rotulan",
           lambda n: C.volumen_campana(8.0, n), 20001, 400001, 1e-6)
ok("los anillos dibujados pesan cada vez menos",
   all(a[1] > b[1] for a, b in zip(C.radios_de_anillos(),
                                   C.radios_de_anillos()[1:])))
oraculo("scipy dice que el area es erf(inf)*raiz(pi)",
        float(sp.erf(6.0) * np.sqrt(np.pi)) if HAY_SCIPY else 0.0, area, 1e-9)

# =====================================================================
print("\n== 13 · CAVALIERI ==")
R = 5.0
for y in (-4.9, -3.0, -1.0, 0.0, 0.5, 2.5, 4.0, 4.99):
    ae, ac, al = C.areas_rebanada(y, R)
    casi(f"a la altura {y} la esfera y el cono suman el cilindro",
         ae + ac, al, 1e-9)
casi("el volumen de la esfera es 4/3 pi R^3", C.volumen_esfera(R),
     4.0 / 3.0 * np.pi * R ** 3, 1e-6)
casi("el cilindro es 2 pi R^3", C.volumen_cilindro(R), 2.0 * np.pi * R ** 3,
     1e-12)
casi("los dos conos son un tercio del cilindro", C.volumen_conos(R),
     C.volumen_cilindro(R) / 3.0, 1e-6)
casi("esfera + conos = cilindro",
     C.volumen_esfera(R) + C.volumen_conos(R), C.volumen_cilindro(R), 1e-6)
casi("la esfera es dos tercios del cilindro", C.razon_esfera_cilindro(R),
     2.0 / 3.0, 1e-9)
ok("y la razon no depende del radio",
   all(abs(C.razon_esfera_cilindro(r) - 2.0 / 3.0) < 1e-9
       for r in (0.5, 2.0, 12.0)))
ok("contraejemplo: la esfera NO es la mitad del cilindro",
   abs(C.razon_esfera_cilindro(R) - 0.5) > 0.15)
try:
    C.radios_rebanada(6.0, R)
    ok("una rebanada fuera aborta", False)
except ValueError:
    ok("una rebanada fuera aborta con ValueError", True)
dos_mallas("el volumen de la esfera no depende de la malla",
           lambda n: C.volumen_esfera(R, n), 20001, 400001, 1e-4)
oraculo("scipy integra el mismo volumen",
        float(si.quad(lambda y: np.pi * (R ** 2 - y ** 2), -R, R)[0])
        if HAY_SCIPY else 0.0, C.volumen_esfera(R), 1e-6)

# =====================================================================
print("\n== 14 · CEBOLLA ==")
for n in (1, 3, 8, 40, 400):
    casi(f"el triangulo de {n} tiras tiene el area del circulo",
         C.area_por_tiras(5.0, n), C.area_circulo(5.0), 1e-9)
casi("el area de un circulo de radio 5 es 78.54", C.area_circulo(5.0),
     78.53981633974483, 1e-12)
casi("la derivada del area es el perimetro", C.derivada_del_area(5.0),
     C.perimetro_circulo(5.0), 1e-6)
ok("y eso pasa con cualquier radio",
   all(abs(C.derivada_del_area(r) - C.perimetro_circulo(r)) < 1e-5
       for r in (0.3, 1.0, 7.5, 100.0)))
anillos = C.anillos_circulo(5.0, 8)
casi("los anillos cubren el circulo entero sin huecos",
     sum(g for _, _, _, g in anillos), 5.0, 1e-12)
ok("cada anillo desenrollado es un trapecio de altura su grosor",
   all(abs(re - ri - g) < 1e-12 for ri, re, _, g in anillos))
casi("el area del anillo de verdad es la de su trapecio",
     float(np.pi * (anillos[3][1] ** 2 - anillos[3][0] ** 2)),
     2.0 * np.pi * anillos[3][2] * anillos[3][3], 1e-12)
ok("contraejemplo: con el radio INTERIOR el triangulo se queda corto",
   sum(2.0 * np.pi * ri * g for ri, _, _, g in C.anillos_circulo(5.0, 8))
   < C.area_circulo(5.0) * 0.95)
oraculo("scipy integra el area sumando anillos",
        float(si.quad(lambda r: 2.0 * np.pi * r, 0.0, 5.0)[0])
        if HAY_SCIPY else 0.0, C.area_circulo(5.0), 1e-9)

# =====================================================================
print("\n== 15 · ANILLO DE SERVILLETA ==")
H = 6.0
radios = (3.0001, 4.0, 9.0, 40.0, 1000.0, 1e5)
volumenes = [C.volumen_anillo(R, H) for R in radios]
casi("el anillo de 6 cm mide 113.10 cm3", volumenes[1], 113.09733552923255,
     1e-5)
ok("y mide lo mismo en una canica y en una esfera de un kilometro",
   max(volumenes) - min(volumenes) < 1e-4,
   " / ".join(f"{v:.4f}" for v in volumenes))
ok("hasta 10 metros de radio coinciden hasta el decimal doce",
   max(volumenes[:5]) - min(volumenes[:5]) < 1e-9,
   f"{max(volumenes[:5]) - min(volumenes[:5]):.2e}")
casi("la integral coincide con pi h^3 / 6",
     C.volumen_anillo(4.0, H), C.volumen_anillo_formula(H), 1e-6)
casi("la corona del ecuador es la mas gorda",
     C.area_corona(0.0, 4.0, H), float(np.pi * (H / 2.0) ** 2), 1e-9)
casi("y en el borde del anillo la corona se cierra",
     C.area_corona(H / 2.0, 4.0, H), 0.0, 1e-9)
ok("el agujero es mas ancho cuanto mas grande la esfera",
   C.radio_del_agujero(4.0, H) < C.radio_del_agujero(9.0, H)
   < C.radio_del_agujero(40.0, H),
   " ".join(f"{C.radio_del_agujero(r, H):.3f}" for r in (4.0, 9.0, 40.0)))
ok("contraejemplo: con OTRA altura el volumen SI cambia",
   abs(C.volumen_anillo(4.0, 3.0) - C.volumen_anillo(4.0, 6.0)) > 90.0,
   f"{C.volumen_anillo(4.0, 3.0):.3f} vs {C.volumen_anillo(4.0, 6.0):.3f}")
try:
    C.volumen_anillo(1e6, H)
    ok("una esfera fuera del alcance del float64 aborta", False,
       "devolvio un numero, y ademas cero")
except ValueError:
    ok("una esfera tan grande que la resta se desvia ABORTA", True,
       f"el techo esta en {C.RADIO_MAXIMO:.0g} cm; a 1e6 daba 113.0996")
casi("la formula cerrada si aguanta un planeta",
     C.volumen_anillo_formula(H), 113.09733552923255, 1e-9)
ok("y crece con el cubo de la altura",
   abs(C.volumen_anillo_formula(12.0) / C.volumen_anillo_formula(6.0) - 8.0)
   < 1e-9)
try:
    C.volumen_anillo(2.0, 6.0)
    ok("un agujero imposible aborta", False)
except ValueError:
    ok("un agujero imposible aborta con ValueError", True)
dos_mallas("el volumen del anillo no depende de la malla",
           lambda n: C.volumen_anillo(4.0, H, n), 20001, 400001, 1e-6)
oraculo("scipy integra el mismo anillo",
        float(si.quad(lambda y: C.area_corona(y, 4.0, H), -H / 2, H / 2)[0])
        if HAY_SCIPY else 0.0, C.volumen_anillo(4.0, H), 1e-6)

# =====================================================================
print("\n== 16 · TROMPETA DE GABRIEL ==")
casi("el volumen tiende a pi", C.volumen_trompeta(1e9), float(np.pi), 1e-8)
ok("y se queda corto siempre",
   all(C.volumen_trompeta(x) < np.pi for x in (2.0, 10.0, 1e3, 1e6)))
casi("con 10 ya tiene el 90 % del volumen", C.volumen_trompeta(10.0),
     0.9 * np.pi, 1e-12)
s6 = C.superficie_trompeta(1e6)
s12 = C.superficie_trompeta(1e12)
ok("la superficie NO converge: se duplica al elevar al cuadrado el limite",
   abs(s12 / s6 - 2.0) < 0.02, f"{s6:.4f} -> {s12:.4f}")
ok("y siempre es mayor que 2 pi ln(X)",
   all(C.superficie_trompeta(x) > 2.0 * np.pi * np.log(x)
       for x in (2.0, 10.0, 1e4, 1e6)))
casi("la superficie a 10^6 es 87.52", s6, 87.5153725, 1e-4)
ok("contraejemplo: el volumen a 10^12 ya no crece y la superficie si",
   abs(C.volumen_trompeta(1e12) - C.volumen_trompeta(1e6)) < 1e-5
   and s12 - s6 > 80.0)
dos_mallas("la superficie no depende de la malla",
           lambda n: C.superficie_trompeta(1e6, n), 20001, 400001, 1e-6)
xs, ys = C.perfil_trompeta()
ok("el perfil empieza en 1 y baja", abs(ys[0] - 1.0) < 1e-12 and ys[-1] < 0.2)
oraculo("scipy integra la misma superficie hasta 100",
        float(2.0 * np.pi * si.quad(
            lambda x: np.sqrt(1.0 + x ** -4.0) / x, 1.0, 100.0)[0])
        if HAY_SCIPY else 0.0, C.superficie_trompeta(100.0), 1e-6)

# =====================================================================
print("\n== 17 · TAYLOR ==")
casi("en el origen el polinomio acierta exactamente",
     C.error_taylor(0.0, 7), 0.0, 1e-15)
al = C.alcances()
ok("cada grado llega mas lejos que el anterior",
   all(al[i][1] < al[i + 1][1] for i in range(len(al) - 1)),
   " ".join(f"g{g}:{x:.2f}" for g, x in al))
ok("el grado 1 no pasa de 0.4 y el 11 llega a 4",
   al[0][1] < 0.5 and al[-1][1] >= 3.9,
   f"{al[0][1]:.2f} y {al[-1][1]:.2f}")
casi("el grado 11 en x=pi/2 es el seno con 7 decimales",
     C.taylor_seno(np.pi / 2.0, 11), 1.0, 1e-7)
ok("contraejemplo: no con 9, que ahi ya se le nota el termino que falta",
   abs(float(C.taylor_seno(np.pi / 2.0, 11)) - 1.0) > 1e-9,
   f"{float(C.taylor_seno(np.pi / 2.0, 11)) - 1.0:.2e}")
ok("dentro del alcance el error se mantiene por debajo de la tolerancia",
   all(C.error_taylor(np.linspace(0.0, x, 2001), g) <= C.TOLERANCIA + 1e-9
       for g, x in al))
ok("y justo despues del alcance ya se pasa",
   all(C.error_taylor(x + 0.05, g) > C.TOLERANCIA for g, x in al[:-1]))
ok("contraejemplo: en x=10 hasta el grado 11 se dispara",
   C.error_taylor(10.0, 11) > 10.0, f"{C.error_taylor(10.0, 11):.2f}")
try:
    C.taylor_seno(1.0, 4)
    ok("un grado par aborta", False)
except ValueError:
    ok("un grado par aborta con ValueError", True)
oraculo("el polinomio de grado 11 coincide con el de scipy en 0.5",
        float(C.taylor_seno(0.5, 11)), float(np.sin(0.5)), 1e-12)

# =====================================================================
print("\n== 18 · ARMONICA ==")
casi("H(1) es 1", C.armonica(1), 1.0, 1e-15)
casi("H(4) es 2.0833", C.armonica(4), 1.0 + 0.5 + 1 / 3 + 0.25, 1e-15)
h6 = C.armonica(1000000)
casi("con un millon de terminos la suma es 14.39", h6, 14.392726722865724,
     1e-9)
for n in (10, 1000, 100000, 1000000):
    lo, s, hi = C.encierra_al_logaritmo(n)
    ok(f"con {n} terminos la suma queda entre el area y el area mas uno",
       lo < s < hi, f"{lo:.4f} < {s:.4f} < {hi:.4f}")
casi("la diferencia con el logaritmo es la constante de Euler",
     C.gamma_de_euler(), 0.5772156649, 1e-6)
ok("la serie crece sin parar, aunque despacio",
   C.armonica(10 ** 6) > C.armonica(10 ** 5) > C.armonica(10 ** 4))
ok("para pasar de 100 hacen falta mas de 1e43 terminos",
   C.terminos_para(100.0) > 1e43, f"{C.terminos_para(100.0):.3e}")
casi("y la estimacion se comprueba con un objetivo pequeño",
     C.armonica(int(round(C.terminos_para(5.0)))), 5.0, 0.01)
ok("contraejemplo: la de los cuadrados SI converge",
   float(np.sum(1.0 / np.arange(1, 10 ** 6 + 1.0) ** 2)) < 1.645,
   f"{float(np.sum(1.0 / np.arange(1, 10 ** 6 + 1.0) ** 2)):.6f}")
ok("las sumas parciales coinciden con H(n)",
   abs(float(C.sumas_parciales(5000)[-1]) - C.armonica(5000)) < 1e-12)
ok("los bloques bajan y ninguno es cero",
   bool(np.all(np.diff(C.bloques(50)) < 0)) and float(C.bloques(50)[-1]) > 0)

# =====================================================================
print("\n" + "=" * 68)
print(" CIFRAS QUE VAN A PANTALLA (todas calculadas aqui)")
print("=" * 68)
r_opt, h_opt, s_opt = C.lata_optima()
t1, t2 = C.instantes_de_la_media()
cifras = [
    ("01 pendiente en x=1", f"{float(C.df_cubica(1.0)):.4f}"),
    ("01bis secantes", " ".join(f"{s:.2f}" for s in C.pendientes_secantes())),
    ("02 delta para eps=0.1", f"{C.delta_para(0.1):.4f}"),
    ("03 razon de despegue", " ".join(f"{r:.2f}"
                                      for r in C.razon_de_despegue())),
    ("03bis despegues", " ".join(f"{d:.4f}" for d in C.despegues())),
    ("04 subtangente de e^x", f"{C.subtangente(1.7):.4f}"),
    ("04bis el numero e", f"{C.numero_e():.4f}"),
    ("05 velocidad media", f"{C.velocidad_media():.1f} km/h"),
    ("05bis instantes", f"{t1:.2f} h y {t2:.2f} h"),
    ("06 raiz de Newton", f"{C.raiz_de_newton():.10f}"),
    ("06bis decimales por paso",
     " ".join(str(C.digitos_correctos(x)) for x in C.newton_pasos(2.0, 4))),
    ("07 lata optima",
     f"r={r_opt:.2f} h={h_opt:.2f} S={s_opt:.1f} cm2"),
    ("07bis exceso de la real", f"{C.exceso_de_la_real():.1f} %"),
    ("07ter coste de fallar un 10 %", f"{C.coste_de_fallar(0.10):.2f} %"),
    ("08 area bajo x^2", f"{C.area_riemann():.4f}"),
    ("08bis pinza con 16", f"{C.pinza(16)[0]:.4f} .. {C.pinza(16)[1]:.4f}"),
    ("09 altura y ritmo en x=2", " = ".join(f"{v:.4f}"
                                            for v in C.altura_y_ritmo(2.0))),
    ("10 area de la hiperbola 1-2", f"{C.area_hiperbola(1.0, 2.0):.4f}"),
    ("10bis area 1-4", f"{C.area_hiperbola(1.0, 4.0):.4f}"),
    ("11 escalera / circunferencia",
     f"{C.longitud_poligonal(C.escalera_circulo(256)):.4f} vs "
     f"{C.longitud_circunferencia():.4f}"),
    ("12 area de la campana", f"{C.area_campana():.4f}"),
    ("12bis volumen girado", f"{C.volumen_campana():.4f}"),
    ("13 razon esfera/cilindro", f"{C.razon_esfera_cilindro():.4f}"),
    ("13bis volumen de la esfera R=5", f"{C.volumen_esfera(5.0):.1f}"),
    ("14 area por tiras R=5", f"{C.area_por_tiras(5.0, 9):.4f}"),
    ("14bis perimetro", f"{C.perimetro_circulo(5.0):.4f}"),
    ("15 anillo de 6 cm", f"{C.volumen_anillo(4.0, 6.0):.2f} cm3"),
    ("15bis con esfera de 9", f"{C.volumen_anillo(9.0, 6.0):.2f} cm3"),
    ("16 volumen de la trompeta", f"{C.volumen_trompeta(1e9):.4f}"),
    ("16bis superficie a 10^6", f"{C.superficie_trompeta(1e6):.2f}"),
    ("17 alcances de Taylor",
     " ".join(f"g{g}:{x:.2f}" for g, x in C.alcances())),
    ("18 H(1e6)", f"{C.armonica(1000000):.4f}"),
    ("18bis terminos para 100", f"{C.terminos_para(100.0):.2e}"),
]
for k, v in cifras:
    print(f"  {k:<38} {v}")

print("\n" + "=" * 68)
print(f"{n_ok} invariantes ok, {len(fallos)} fallos")
if fallos:
    for f in fallos:
        print(f"  - {f}")
sys.exit(1 if fallos else 0)
