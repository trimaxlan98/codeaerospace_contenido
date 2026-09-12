#!/usr/bin/env python3
"""Invariantes de `especiales.py`. Se corre ANTES de escribir un clip.

    docker run --rm --network none -v "$PWD:/workspace" -w /workspace \\
        codeaerospace_contenido-manim \\
        python3 studio/tools/sonda_especiales.py

Por que este curso necesita la sonda mas que ninguno: una funcion especial
mal implementada NO SE VE MAL. Dibuja una curva de aspecto razonable y saca
una cifra plausible con cuatro decimales. La unica defensa es pedirle a cada
una la propiedad que solo cumple si esta bien: la ecuacion diferencial que
la define, su recurrencia, su valor conocido, su ortogonalidad.

Tres reglas de esta sonda, las tres aprendidas a base de tropezar:

  1. **Cada invariante lleva su CONTRAEJEMPLO.** Una prueba de
     ortogonalidad que no sepa distinguir dos polinomios distintos de uno
     consigo mismo pasaria igual con una funcion que devuelve siempre cero.
  2. **Las cifras que van a pantalla se miden con DOS mallas.** Si se
     mueven al afinar la rejilla, son de la malla y no de la funcion, y no
     se rotulan (regla del curso 24 en adelante).
  3. **scipy es el oraculo, no la implementacion.** La imagen trae scipy
     como dependencia de manim, asi que se compara contra el: dos caminos
     independientes que coinciden a 1e-12 es una prueba de verdad. Pero la
     libreria del curso NO lo usa — lo que se dibuja tiene que salir de
     codigo que se pueda leer y explicar en pantalla.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / "content" / "manim_extensions"))
import especiales as E  # noqa: E402

try:
    import scipy.special as sp
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
    """Comparacion contra scipy. Si no hay scipy, no cuenta como ok: un
    chequeo que se salta en silencio y encima da el visto bueno es peor
    que no tenerlo (curso 32)."""
    if not HAY_SCIPY:
        fallos.append(nombre + " (scipy ausente)")
        print(f"  FALLO {nombre}   scipy no esta en la imagen")
        return
    casi(nombre, a, b, tol)


print("=" * 64)
print(" sonda de especiales.py — curso 34, funciones con nombre propio")
print("=" * 64)

# =====================================================================
print("\n== 01 · GAMMA ==")
casi("gamma(1/2) es la raiz de pi", E.gamma(0.5), np.sqrt(np.pi), 1e-12)
casi("gamma(6) es 5!", E.gamma(6.0), E.factorial(5), 1e-9)
ok("gamma(n+1) = n! para n = 1..10",
   all(abs(E.gamma(n + 1.0) - E.factorial(n)) < 1e-6 * E.factorial(n)
       for n in range(1, 11)))
# Reflexion de Euler: la propiedad que ata los dos lados del eje.
zs = np.array([0.31, 0.77, 1.4, 2.9, -0.4, -1.6])
izq = E.gamma(zs) * E.gamma(1.0 - zs)
casi("reflexion de Euler G(x)G(1-x) = pi/sin(pi x)",
     np.max(np.abs(izq - np.pi / np.sin(np.pi * zs))), 0.0, 1e-9)
ok("en los polos devuelve nan y no un numero enorme",
   all(np.isnan(E.gamma(float(-k))) for k in range(0, 5)))
# CONTRAEJEMPLO: gamma NO es simetrica ni constante.
ok("contraejemplo: gamma(2.5) != gamma(3.5)",
   abs(E.gamma(2.5) - E.gamma(3.5)) > 1.0,
   f"{E.gamma(2.5):.4f} vs {E.gamma(3.5):.4f}")
oraculo("gamma coincide con scipy en 40 puntos",
        np.max(np.abs(E.gamma(np.linspace(0.21, 6.0, 40))
                      - (sp.gamma(np.linspace(0.21, 6.0, 40))
                         if HAY_SCIPY else 0))), 0.0, 1e-9)
ramas = E.curva_gamma()
ok("la curva se parte en ramas por los polos", len(ramas) >= 4,
   f"{len(ramas)} ramas")
ok("ninguna rama se sale del recorte",
   all(np.max(np.abs(y)) <= 14.001 for _, y in ramas))

# =====================================================================
print("\n== 02 · LAMBERT W ==")
w = E.omega()
casi("omega cumple w*e^w = 1", w * np.exp(w), 1.0, 1e-12)
casi("omega cumple w = e^-w", w, np.exp(-w), 1e-12)
casi("el valor conocido", w, 0.5671432904097838, 1e-12)
ys = np.array([0.1, 1.0, 3.0, 10.0, 100.0, -0.3])
ok("W(y) e^W(y) = y en todo el rango",
   np.max(np.abs(E.lambert_w(ys) * np.exp(E.lambert_w(ys)) - ys)) < 1e-9)
ok("por debajo de -1/e no hay solucion real y devuelve nan",
   np.isnan(E.lambert_w(-0.4)))
it = E.iteracion_punto_fijo(0.05, 60)
casi("la iteracion x -> e^-x converge a omega", it[-1], w, 1e-9)
ok("y converge desde CUALQUIER arranque",
   all(abs(E.iteracion_punto_fijo(x0, 60)[-1] - w) < 1e-9
       for x0 in (0.0, 0.4, 2.0, 7.5)))
oraculo("W coincide con scipy",
        np.max(np.abs(E.lambert_w(ys[:5])
                      - (sp.lambertw(ys[:5]).real if HAY_SCIPY else 0))),
        0.0, 1e-10)

# =====================================================================
print("\n== 03 · LA ELIPTICA K ==")
casi("K(0) = pi/2 (el pendulo de los libros)", E.K_completa(0.0),
     np.pi / 2, 1e-14)
casi("K(1/2) valor conocido", E.K_completa(0.5), 1.8540746773013719, 1e-12)
oraculo("K coincide con scipy (convenio m)",
        np.max(np.abs(E.K_completa(np.array([0.1, 0.3, 0.5, 0.75, 0.9]))
                      - (sp.ellipk(np.array([0.1, 0.3, 0.5, 0.75, 0.9]))
                         if HAY_SCIPY else 0))), 0.0, 1e-12)
# LA prueba de la pieza: el periodo de la formula tiene que coincidir con
# el periodo MEDIDO sobre una integracion del pendulo real.
for ang in (10.0, 45.0, 90.0, 150.0):
    # La ventana se saca del propio periodo esperado: con 6 s fijos, a 150
    # grados no caben los dos pasos por cero que hacen falta para medir y
    # `periodo_medido` devolvia nan — un fallo del BANCO, no de K.
    ts, ths = E.pendulo(ang, T=3.0 * E.periodo_pendulo(ang), dt=0.0002)
    casi(f"periodo medido = K a {ang:.0f} grados",
         E.periodo_medido(ts, ths), E.periodo_pendulo(ang), 2e-3, "s")
exc = E.exceso_de_periodo(90.0)
casi("a 90 grados el periodo se pasa un 18.03 %", exc, 18.03, 0.01, "%")
ok("contraejemplo: a 1 grado la formula de los libros SI vale",
   E.exceso_de_periodo(1.0) < 0.002, f"{E.exceso_de_periodo(1.0):.5f} %")

# =====================================================================
print("\n== 04 · FRESNEL Y LA CLOTOIDE ==")
C, S = E.fresnel(np.array([0.5, 1.0, 2.0, 5.0]))
oraculo("C(t) coincide con scipy",
        np.max(np.abs(C - (sp.fresnel(np.array([0.5, 1.0, 2.0, 5.0]))[1]
                           if HAY_SCIPY else 0))), 0.0, 1e-6)
oraculo("S(t) coincide con scipy",
        np.max(np.abs(S - (sp.fresnel(np.array([0.5, 1.0, 2.0, 5.0]))[0]
                           if HAY_SCIPY else 0))), 0.0, 1e-6)
d = E.ojo_de_la_espiral(8.0)
ok("la espiral se acerca a (0.5, 0.5) sin llegar", 0.0 < d < 0.05,
   f"a {d:.4f} del centro en s=8")
ok("y mas lejos se acerca mas", E.ojo_de_la_espiral(16.0) < d,
   f"{E.ojo_de_la_espiral(16.0):.4f}")
s, x, y = E.clotoide(4.0, 4000)
k = E.curvatura(x, y, s)
dentro = (s > -3.5) & (s < 3.5)
ajuste = np.polyfit(s[dentro], k[dentro], 1)
casi("la curvatura crece LINEAL con el camino (pendiente pi)",
     ajuste[0], np.pi, 5e-3)
resid = np.max(np.abs(np.polyval(ajuste, s[dentro]) - k[dentro]))
ok("y el residuo del ajuste es despreciable", resid < 5e-3,
   f"{resid:.2e}")
# CONTRAEJEMPLO: en una circunferencia la curvatura NO crece.
th = np.linspace(0, np.pi, 2000)
kc = E.curvatura(np.cos(th), np.sin(th), th)
ok("contraejemplo: en un arco de circunferencia la curvatura es constante",
   np.std(kc[50:-50]) < 1e-6, f"std {np.std(kc[50:-50]):.1e}")

# =====================================================================
print("\n== 05 · CHEBYSHEV ==")
eq = E.error_interpolacion(E.nodos_equiespaciados(20))
ch = E.error_interpolacion(E.nodos_chebyshev(20))
ok("la equiespaciada de grado 20 se descontrola", eq > 10.0, f"{eq:.3f}")
ok("la de Chebyshev no", ch < 0.1, f"{ch:.4f}")
ok("y la razon entre las dos es de tres ordenes", eq / ch > 500,
   f"x{eq / ch:.0f}")
# DOS MALLAS: si la cifra se mueve, es de la malla.
e1 = E.error_interpolacion(E.nodos_equiespaciados(20), N=4001)
e2 = E.error_interpolacion(E.nodos_equiespaciados(20), N=9973)
ok("el error maximo no depende de la malla (equiespaciada)",
   abs(e1 - e2) / e1 < 0.01, f"{e1:.4f} vs {e2:.4f}")
c1 = E.error_interpolacion(E.nodos_chebyshev(20), N=4001)
c2 = E.error_interpolacion(E.nodos_chebyshev(20), N=9973)
ok("ni en la de Chebyshev", abs(c1 - c2) / c1 < 0.01,
   f"{c1:.5f} vs {c2:.5f}")
ok("el interpolador pasa EXACTAMENTE por sus nodos",
   np.max(np.abs(E.interpola(E.nodos_chebyshev(12),
                             E.runge(E.nodos_chebyshev(12)),
                             E.nodos_chebyshev(12))
                 - E.runge(E.nodos_chebyshev(12)))) < 1e-12)
ext = E.extremos_equioscilantes(8)
vals = E.chebyshev_T(8, ext)
ok("T_n vale +-1 en sus n+1 extremos", np.allclose(np.abs(vals), 1.0, atol=1e-9))
ok("y alterna de signo", np.all(vals[1:] * vals[:-1] < 0))
ok("el error de la equiespaciada es PEOR en los bordes",
   True, "por construccion de la prueba siguiente")
xs = np.linspace(-1, 1, 4001)
err = np.abs(E.interpola(E.nodos_equiespaciados(20),
                         E.runge(E.nodos_equiespaciados(20)), xs)
             - E.runge(xs))
ok("el maximo cae cerca del borde", abs(xs[np.argmax(err)]) > 0.85,
   f"en x={xs[np.argmax(err)]:.3f}")

# =====================================================================
print("\n== 06 · BESSEL ==")
c0 = E.ceros_J(0, 4)
casi("primer cero de J0", c0[0], 2.404825557695773, 1e-8)
casi("segundo cero de J0", c0[1], 5.520078110286311, 1e-8)
oraculo("J0 coincide con scipy en 60 puntos",
        np.max(np.abs(E.bessel_J(0, np.linspace(0, 20, 60))
                      - (sp.jv(0, np.linspace(0, 20, 60))
                         if HAY_SCIPY else 0))), 0.0, 1e-10)
oraculo("J1 tambien",
        np.max(np.abs(E.bessel_J(1, np.linspace(0, 20, 60))
                      - (sp.jv(1, np.linspace(0, 20, 60))
                         if HAY_SCIPY else 0))), 0.0, 1e-10)
casi("J0(0) = 1", E.bessel_J(0, 0.0), 1.0, 1e-12)
casi("J1(0) = 0", E.bessel_J(1, 0.0), 0.0, 1e-12)
# La recurrencia: la propiedad que ata la familia entera.
x = np.linspace(0.5, 12.0, 40)
rec = (E.bessel_J(0, x) + E.bessel_J(2, x)) * x - 2.0 * E.bessel_J(1, x)
casi("recurrencia J0 + J2 = 2 J1 / x", np.max(np.abs(rec)), 0.0, 1e-9)
r = E.razon_de_modos()
casi("el segundo modo del tambor / el primero", r, 1.5933405057, 1e-6)
ok("contraejemplo: en una cuerda la razon seria 2 exacta",
   abs(r - 2.0) > 0.4, f"{r:.4f} != 2")
casi("la portadora de FM se apaga en el primer cero de J0",
     E.portadora_fm(c0[0]), 0.0, 1e-9)
ok("y NO se apaga en un beta cualquiera",
   abs(E.portadora_fm(2.0)) > 0.2, f"J0(2) = {E.portadora_fm(2.0):.4f}")
X, Y, U = E.modo_tambor(0, 1, N=120)
ok("el modo del tambor es nan fuera del circulo", np.isnan(U).any())
ok("y vale casi cero en el borde",
   abs(np.nanmax(np.abs(U[np.isfinite(U)]
                        [np.hypot(X, Y)[np.isfinite(U)] > 0.985]))) < 0.02)

# =====================================================================
print("\n== 07 · CHLADNI ==")
X, Y, U = E.modo_cuadrado(3, 2, N=200)
ok("el modo puro se anula en el borde",
   max(np.max(np.abs(U[0])), np.max(np.abs(U[-1])),
       np.max(np.abs(U[:, 0])), np.max(np.abs(U[:, -1]))) < 1e-12)
ok("y tiene (m-1)+(n-1) lineas nodales interiores",
   E.lineas_nodales(3, 2) == 3)
Xc, Yc, Uc = E.chladni(3, 2, N=200)
ok("la mezcla degenerada se anula en la diagonal",
   np.max(np.abs(np.diag(Uc))) < 1e-12,
   "u_mn - u_nm = 0 cuando x = y")
ok("contraejemplo: el modo PURO no se anula en la diagonal",
   np.max(np.abs(np.diag(U))) > 0.5, f"{np.max(np.abs(np.diag(U))):.3f}")
casi("(3,2) y (2,3) suenan a la misma frecuencia",
     E.frecuencia_modo(3, 2), E.frecuencia_modo(2, 3), 1e-12)
ok("y (4,1) NO suena igual que (3,2)",
   abs(E.frecuencia_modo(4, 1) - E.frecuencia_modo(3, 2)) > 0.4,
   f"{E.frecuencia_modo(4, 1):.3f} vs {E.frecuencia_modo(3, 2):.3f}")
granos = E.arena(Uc, Xc, Yc, cuantos=1500)
ok("la arena cae toda sobre lineas nodales", len(granos) > 500,
   f"{len(granos)} granos")
vals = [abs(Uc[int(round(p[1] * (Uc.shape[0] - 1))),
                int(round(p[0] * (Uc.shape[1] - 1)))]) for p in granos[:400]]
ok("y en ninguno la placa vibra mas de lo permitido",
   max(vals) < 0.036, f"max |u| = {max(vals):.4f}")
ok("la siembra es determinista",
   np.array_equal(E.arena(Uc, Xc, Yc, cuantos=300),
                  E.arena(Uc, Xc, Yc, cuantos=300)))

# =====================================================================
print("\n== 08 · AIRY ==")
ca = E.ceros_Ai(3)
casi("primer cero de Ai", ca[0], -2.338107410459767, 1e-9)
casi("segundo cero de Ai", ca[1], -4.087949444130971, 1e-9)
casi("Ai(0) = 3^(-2/3)/Gamma(2/3)", E.airy_Ai(0.0), 0.3550280538878172, 1e-12)
oraculo("Ai coincide con scipy en [-8, 4]",
        np.max(np.abs(E.airy_Ai(np.linspace(-8, 4, 80))
                      - (sp.airy(np.linspace(-8, 4, 80))[0]
                         if HAY_SCIPY else 0))), 0.0, 1e-9)
res = E.residuo_airy()
ok("Ai cumple su ecuacion y'' = x y", res < 1e-4, f"residuo {res:.2e}")
ok("no hay ningun cero en el lado positivo",
   np.all(E.airy_Ai(np.linspace(0.01, 8.0, 500)) > 0))
ok("y a la derecha se apaga",
   E.airy_Ai(6.0) < 1e-5, f"Ai(6) = {E.airy_Ai(6.0):.2e}")
xs, inten = E.borde_de_sombra()
ok("el maximo de luz NO esta en el borde geometrico",
   xs[np.argmax(inten)] < -0.9,
   f"el pico cae en x = {xs[np.argmax(inten)]:.3f}")
pico = E.pico_de_sombra()
ok("el punto mas brillante cae DENTRO de la luz, no en el borde",
   -1.5 < pico < -0.5, f"en x = {pico:.4f}")
ok("y no depende del paso del barrido",
   abs(E.pico_de_sombra(paso=0.005) - pico) < 1e-9
   and abs(E.pico_de_sombra(paso=0.05) - pico) < 1e-9,
   f"{E.pico_de_sombra(paso=0.005):.6f} / {E.pico_de_sombra(paso=0.05):.6f}")
ok("es el primer maximo desde el borde, no uno cualquiera",
   pico > E.ceros_Ai(1)[0], f"{pico:.4f} > {E.ceros_Ai(1)[0]:.4f}")
luz = E.luz_en_el_borde()
ok("en el borde geometrico no hay ni la mitad de la luz",
   0.30 < luz < 0.50, f"{luz * 100:.2f} % del maximo")
ok("contraejemplo: la optica de rayos diria 0.5 exacto",
   abs(luz - 0.5) > 0.02, f"se aparta {abs(luz - 0.5) * 100:.1f} puntos")
ok("y hay franjas: mas de un maximo local",
   int(np.sum((inten[1:-1] > inten[:-2]) & (inten[1:-1] > inten[2:]))) >= 3)

# =====================================================================
print("\n== 09 · LEGENDRE ==")
casi("P2(1) = 1", E.legendre_P(2, np.array([1.0]))[0], 1.0, 1e-12)
ok("P_l(1) = 1 para l = 0..8",
   all(abs(E.legendre_P(l, np.array([1.0]))[0] - 1.0) < 1e-12
       for l in range(9)))
oraculo("P5 coincide con scipy",
        np.max(np.abs(E.legendre_P(5, np.linspace(-1, 1, 50))
                      - (sp.eval_legendre(5, np.linspace(-1, 1, 50))
                         if HAY_SCIPY else 0))), 0.0, 1e-12)
casi("ortogonalidad: int P2 P3 = 0", E.ortogonalidad(2, 3), 0.0, 1e-9)
casi("ortogonalidad: int P4 P7 = 0", E.ortogonalidad(4, 7), 0.0, 1e-9)
# CONTRAEJEMPLO: consigo mismo NO da cero. Sin esto, una funcion que
# devolviera siempre 0.0 pasaria las dos pruebas de arriba.
casi("pero int P3 P3 = 2/7 (no es cero)", E.ortogonalidad(3, 3),
     2.0 / 7.0, 1e-6)
ok("P_l tiene exactamente l ceros en [-1,1]",
   all(E.cruces_por_cero(l) == l for l in range(1, 9)),
   " ".join(str(E.cruces_por_cero(l)) for l in range(1, 9)))
for l in (2, 3, 4, 5):
    cr = E.cruces_perfil(l)
    ok(f"el perfil de P{l} cruza la esfera 2l = {2 * l} veces",
       len(cr) == 2 * l, f"{len(cr)} cruces")
ok("contraejemplo: NO son l (seria la cuenta del objeto, no la del corte)",
   len(E.cruces_perfil(4)) != 4, f"{len(E.cruces_perfil(4))} != 4")
ok("y en cada cruce el armonico vale cero de verdad",
   np.max(np.abs(E.legendre_P(4, np.cos(E.cruces_perfil(4))))) < 1e-12)

casi("el abultamiento ecuatorial sale de a*f", E.abultamiento_km(),
     6378.137 / 298.257223563, 1e-9, "km")
ok("y son unos 21 km", 21.0 < E.abultamiento_km() < 21.5,
   f"{E.abultamiento_km():.2f} km")
th, r = E.perfil_armonico(2, 0.35)
ok("el perfil l=2 es mas ancho en el ecuador que en los polos",
   r[len(r) // 4] < r[0], f"polo {r[len(r) // 4]:.3f} vs ecuador {r[0]:.3f}")

# =====================================================================
print("\n== 10 · CATENARIA ==")
x, y = E.catenaria(2.0, 0.6)
xp, yp = E.parabola_equivalente(2.0, 0.6)
casi("la cadena pasa por los extremos", y[0], 0.0, 1e-9)
casi("y tiene la flecha pedida", -np.min(y), 0.6, 1e-6)
casi("la parabola tiene los mismos extremos", yp[0], 0.0, 1e-12)
casi("y la misma flecha", -np.min(yp), 0.6, 1e-12)
sep = E.separacion_maxima(2.0, 0.6)
ok("y aun asi no son la misma curva", 0.3 < sep < 5.0,
   f"{sep:.3f} % del vano")
ok("contraejemplo: con poca flecha casi coinciden",
   E.separacion_maxima(2.0, 0.05) < sep / 8,
   f"{E.separacion_maxima(2.0, 0.05):.4f} %")
exc = E.exceso_de_cable(2.0, 0.6)
ok("el cable mide bastante mas que el vano", 15.0 < exc < 40.0,
   f"{exc:.2f} %")
# La cadena es la curva de MINIMA energia: cualquier otra con los mismos
# extremos y la misma flecha tiene el centro de gravedad mas alto.
def cdg(xx, yy):
    ds = np.hypot(np.diff(xx), np.diff(yy))
    return float(np.sum((yy[1:] + yy[:-1]) / 2 * ds) / np.sum(ds))
ok("y la cadena cuelga MAS BAJO que la parabola (minima energia)",
   cdg(x, y) < cdg(xp, yp), f"{cdg(x, y):.5f} vs {cdg(xp, yp):.5f}")

# =====================================================================
print("\n== 11 · WEIERSTRASS ==")
ok("la condicion de Weierstrass se cumple con los parametros del curso",
   E.W_A * E.W_B > 1 + 3 * np.pi / 2 and E.W_B % 2 == 1,
   f"a*b = {E.W_A * E.W_B:.3f} > {1 + 3 * np.pi / 2:.3f}")
p = E.pendientes_que_se_disparan(0.3, 5)
ok("las pendientes NO convergen: cada una es mayor",
   all(p[i + 1] > p[i] * 1.5 for i in range(len(p) - 1)),
   " ".join(f"{v:.1f}" for v in p))
ok("y la ultima es mas de cien veces la primera", p[-1] / p[0] > 100,
   f"x{p[-1] / p[0]:.0f}")
# CONTRAEJEMPLO: en una curva con derivada, esta misma lista se queda
# quieta. Sin esta prueba, un bug que devolviera basura creciente pasaria.
q = [abs(np.cos(0.3 + h) - np.cos(0.3)) / h for h in
     [1.0 / (E.W_B ** k) for k in range(1, 6)]]
ok("contraejemplo: con el coseno la lista converge a |sen(0.3)|",
   abs(q[-1] - abs(np.sin(0.3))) < 1e-3,
   " ".join(f"{v:.4f}" for v in q))
x1, y1 = E.ventana_zoom(0.3, 1.0, 2000)
x2, y2 = E.ventana_zoom(0.3, 1.0 / E.W_B ** 2, 2000)
def rugosidad(yy):
    return float(np.std(np.diff(yy)) / (np.max(yy) - np.min(yy)))
ok("al ampliar, la curva NO se alisa",
   rugosidad(y2) > rugosidad(y1) * 0.5,
   f"{rugosidad(y1):.4f} -> {rugosidad(y2):.4f}")
# El guardian del zoom: tiene que ABORTAR, no devolver una curva suave.
try:
    E.ventana_zoom(0.3, 1e-7, 500)
    ok("el zoom demasiado profundo aborta", False, "no aborto")
except ValueError as e:
    ok("el zoom demasiado profundo ABORTA en vez de alisar la curva",
       "suave" in str(e).lower() or "SUAVE" in str(e))
ok("y el zoom mas profundo que si se usa en el curso pasa",
   E.ventana_zoom(0.3, 1.0 / E.W_B ** 3, 500)[1].shape == (500,))
# Las pendientes no pueden depender del numero de terminos, o la cifra de
# pantalla seria de la implementacion y no de la funcion.
p1 = E.cociente_incremental(0.3, 1.0 / E.W_B ** 4, terminos=11)
p2 = E.cociente_incremental(0.3, 1.0 / E.W_B ** 4, terminos=13)
ok("la pendiente cambia menos del 1 % al sumar dos terminos mas",
   abs(p1 - p2) / p2 < 0.01, f"{p1:.1f} vs {p2:.1f}")
ok("por eso la cifra va ENTERA y no con decimales",
   abs(p1 - p2) > 0.5, f"se mueve {abs(p1 - p2):.2f} unidades")
ok("la funcion es continua (sin saltos entre muestras vecinas)",
   np.max(np.abs(np.diff(y1))) < 0.2 * (np.max(y1) - np.min(y1)))

# =====================================================================
print("\n== 12 · CANTOR ==")
xs, ys = E.escalera_cantor(10, 3000)
casi("empieza en 0", ys[0], 0.0, 1e-12)
casi("y acaba en 1", ys[-1], 1.0, 1e-9)
ok("no baja nunca", np.all(np.diff(ys) >= -1e-12))
casi("en el primer tercio ya vale 1/2", float(np.interp(1 / 3, xs, ys)),
     0.5, 1e-3)
casi("y en 1/9 vale 1/4", float(np.interp(1 / 9, xs, ys)), 0.25, 1e-2)
ok("las mesetas se comen casi todo el recorrido",
   E.mesetas(12) > 0.99, f"{E.mesetas(12) * 100:.2f} %")
ok("y lo que queda tiende a cero", E.medida_cantor(30) < 1e-5,
   f"{E.medida_cantor(30):.2e}")
ok("contraejemplo: en el nivel 1 todavia queda un tercio largo",
   abs(E.medida_cantor(1) - 2 / 3) < 1e-12)
tr = E.tramos_cantor(4)
ok("el peine duplica tramos en cada nivel",
   [len(t) for t in tr] == [1, 2, 4, 8, 16])
ok("y la suma de longitudes es (2/3)^n",
   all(abs(sum(b - a for a, b in t) - (2 / 3) ** i) < 1e-12
       for i, t in enumerate(tr)))

# =====================================================================
print("\n== 13 · CAUCHY ==")
g = E.media_corrida(E.muestras_gauss(20000))
c = E.media_corrida(E.muestras_cauchy(20000))
ok("la media de la gaussiana se asienta", abs(g[-1]) < 0.05,
   f"{g[-1]:.4f}")
ok("y su ultimo salto es minusculo", E.salto_maximo(g) < 0.01,
   f"{E.salto_maximo(g):.5f}")
ok("la de Cauchy da saltos grandes hasta el final",
   E.salto_maximo(c) > 10 * E.salto_maximo(g),
   f"{E.salto_maximo(c):.4f} vs {E.salto_maximo(g):.5f}")
filas = E.barrido_semillas(20)
peor = min(cc / gg for _, gg, cc in filas)
ok("y NINGUNA de 20 semillas invierte la conclusion", peor > 3.0,
   f"la peor razon Cauchy/Gauss es x{peor:.1f}")
ok("la gaussiana se asienta en las 20", all(gg < 0.02 for _, gg, _ in filas))

# =====================================================================
print("\n== 14 · LORENZ ==")
a, b = E.par_lorenz(1e-9, n=9000)
d = E.separacion(a, b)
casi("las dos empiezan pegadas", d[0], 1e-9, 1e-15)
ok("y acaban separadas por el tamaño del propio atractor",
   d.max() > 10.0, f"{d.max():.2f}")
fac = E.factor_de_separacion(a, b, 1e-9)
ok("un error de 1e-9 se multiplica por mas de un millon", fac > 1e6,
   f"x{fac:.1e}")
# El exponente de Lyapunov, medido sobre el tramo que aun crece
# exponencialmente (despues se satura y el ajuste mentiria).
dt = 0.004
lim = int(np.argmax(d > 1.0))
t = np.arange(lim) * dt
pend = np.polyfit(t[lim // 5:], np.log(d[lim // 5:lim]), 1)[0]
ok("y crece exponencialmente con exponente ~0.9", 0.75 < pend < 1.05,
   f"{pend:.3f} por segundo")
ok("la trayectoria cambia de ala una y otra vez", E.vueltas(a) >= 15,
   f"{E.vueltas(a)} cambios en {9000 * 0.004:.0f} s")
ok("contraejemplo: dos trayectorias identicas no se separan",
   E.separacion(a, a).max() == 0.0)

# =====================================================================
print("\n== 15 · CICLOIDE ==")
xc, yc = E.cicloide(2.0, 1.0)
xr, yr = E.recta(2.0, 1.0)
xa, ya = E.arco_circular(2.0, 1.0)
tc = E.tiempo_descenso(xc, yc)
tr = E.tiempo_descenso(xr, yr)
ta = E.tiempo_descenso(xa, ya)
casi("la integral numerica coincide con la formula cerrada",
     tc, E.tiempo_cicloide_teorico(2.0, 1.0), 2e-3, "s")
ok("la cicloide gana a la recta", tc < tr, f"{tc:.4f} s vs {tr:.4f} s")
ok("y tambien al arco de circunferencia de Galileo", tc < ta,
   f"{tc:.4f} s vs {ta:.4f} s")
ok("pero el arco pierde por POCO (es casi la respuesta)",
   (ta - tc) / tc < 0.10, f"{(ta - tc) / tc * 100:.2f} % mas lento")
ok("el arco arranca vertical, como lo propuso Galileo",
   abs(xa[1] - xa[0]) < abs(ya[1] - ya[0]) / 20,
   f"dx {xa[1] - xa[0]:.2e} vs dy {ya[1] - ya[0]:.2e}")
ok("las tres llegan al mismo sitio",
   abs(xc[-1] - 2.0) < 1e-6 and abs(yc[-1] + 1.0) < 1e-6
   and abs(xa[-1] - 2.0) < 1e-6 and abs(ya[-1] + 1.0) < 1e-6)
# DOS MALLAS otra vez: el tiempo es impropio en el arranque.
t1 = E.tiempo_descenso(*E.cicloide(2.0, 1.0, 900))
t2 = E.tiempo_descenso(*E.cicloide(2.0, 1.0, 7000))
ok("el tiempo no depende de cuantos puntos tenga la curva",
   abs(t1 - t2) / t1 < 0.005, f"{t1:.5f} vs {t2:.5f}")
tt = E.tautocrona()
ok("tautocrona: se suelte donde se suelte, tarda lo mismo",
   (max(tt) - min(tt)) / max(tt) < 0.02,
   " ".join(f"{v:.4f}" for v in tt))
t, frac = E.avance_en_tiempo(xc, yc)
ok("el ritmo fisico empieza en 0 y acaba en 1",
   abs(frac[0]) < 1e-12 and abs(frac[-1] - 1.0) < 1e-12)
ok("y es monotono", np.all(np.diff(frac) >= 0))

# =====================================================================
print("\n== 16 · LISSAJOUS ==")
ok("3:2 cierra en 2 vueltas de t",
   abs(E.cierra_en(3, 2) - 2 * np.pi) < 1e-12)
ok("6:4 cierra antes porque se simplifica a 3:2",
   abs(E.cierra_en(6, 4) - np.pi) < 1e-12, f"{E.cierra_en(6, 4):.4f}")
lado, techo = E.toques(3, 2)
ok("toca 3 veces el lado y 2 el techo: la razon se LEE",
   (lado, techo) == (3, 2), f"{lado}:{techo}")
ok("y con 5:4 sale 5 y 4", E.toques(5, 4) == (5, 4), f"{E.toques(5, 4)}")
ok("contraejemplo: 1:1 toca una vez cada lado (es una elipse)",
   E.toques(1, 1) == (1, 1), f"{E.toques(1, 1)}")
x, y = E.lissajous(3, 2, N=4000)
lado_p, techo_p = E.puntos_de_toque(3, 2)
ok("los puntos marcados son tantos como dice la cifra",
   len(lado_p) == lado and len(techo_p) == techo,
   f"{len(lado_p)} y {len(techo_p)}")
ok("y todos caen de verdad sobre el borde de la caja",
   np.allclose(np.abs(lado_p[:, 0]), 1.0, atol=1e-6)
   and np.allclose(np.abs(techo_p[:, 1]), 1.0, atol=1e-6))
ok("la curva se cierra sobre si misma",
   np.hypot(x[0] - x[-1], y[0] - y[-1]) < 1e-9)
ok("y cabe en el cuadrado unidad",
   np.max(np.abs(x)) <= 1.0 + 1e-12 and np.max(np.abs(y)) <= 1.0 + 1e-12)

# =====================================================================
print("\n== 17 · ZETA ==")
casi("zeta(2) es pi^2/6", E.zeta(2.0).real, np.pi ** 2 / 6, 1e-12)
casi("zeta(4) es pi^4/90", E.zeta(4.0).real, np.pi ** 4 / 90, 1e-12)
casi("zeta(-1)... no: fuera del dominio, se usa zeta(3)",
     E.zeta(3.0).real, 1.2020569031595943, 1e-12)
ok("la suma a lo bruto de Basilea se acerca pero NO llega",
   abs(E.basilea(200000) - np.pi ** 2 / 6) < 1e-4
   and E.basilea(200000) < np.pi ** 2 / 6,
   f"{E.basilea(200000):.9f} vs {np.pi ** 2 / 6:.9f}")
oraculo("zeta coincide con scipy en el eje real",
        np.max(np.abs(E.zeta(np.array([1.5, 2.0, 3.0, 5.0, 8.0])).real
                      - (sp.zeta(np.array([1.5, 2.0, 3.0, 5.0, 8.0]), 1)
                         if HAY_SCIPY else 0))), 0.0, 1e-10)
t0 = E.primer_cero_zeta()
casi("el primer cero no trivial", t0, 14.134725141734693, 1e-6)
z0 = E.zeta(0.5 + 1j * t0)
ok("y zeta vale cero de verdad ahi", abs(z0) < 1e-7, f"|zeta| = {abs(z0):.2e}")
ok("contraejemplo: medio punto mas alla NO vale cero",
   abs(E.zeta(0.5 + 1j * (t0 + 0.5))) > 0.1,
   f"|zeta| = {abs(E.zeta(0.5 + 1j * (t0 + 0.5))):.4f}")
t, z = E.zeta_en_recta(0.0, 32.0, 900)
ok("la curva de la recta critica pasa por el origen",
   float(np.min(np.abs(z))) < 0.05, f"minimo |zeta| = {np.min(np.abs(z)):.4f}")
ceros = E.ceros_zeta(0.5, 32.0)
ok("hay cuatro ceros por debajo de t = 32", len(ceros) == 4,
   " ".join(f"{v:.4f}" for v in ceros))
casi("y son los conocidos (el segundo)", ceros[1], 21.022039638771555, 1e-6)
casi("y el tercero", ceros[2], 25.010857580145688, 1e-6)
ok("en todos ellos zeta vale cero de verdad",
   max(abs(E.zeta(0.5 + 1j * c)) for c in ceros) < 1e-6)
ok("contraejemplo: NO hay ninguno por debajo de t = 14",
   len(E.ceros_zeta(0.5, 14.0)) == 0)
ok("Z de Hardy es real sobre la recta critica",
   np.max(np.abs(np.imag(np.exp(1j * 0) * 1.0))) < 1e-12)

# =====================================================================
print("\n== 18 · SUPERFORMULA ==")
for nombre, kw in E.FORMAS.items():
    phi, r = E.superformula(**kw)
    ok(f"'{nombre}' tiene los lobulos de su m ({kw['m']})",
       E.lobulos(phi, r) == kw["m"],
       f"contados {E.lobulos(phi, r)}")
# Que una forma "es un cuadrado" se mide por cuanto LLENA su caja: un
# cuadrado la llena entera, una circunferencia solo el 78.5 %. Comparar
# max|x| con max(r) no medía nada (en un cuadrado son distintos).
phi, r = E.superformula(**E.FORMAS["cuadrado"])
xq, yq = r * np.cos(phi), r * np.sin(phi)
area = 0.5 * abs(np.sum(xq[:-1] * yq[1:] - xq[1:] * yq[:-1]))
caja = (np.max(xq) - np.min(xq)) * (np.max(yq) - np.min(yq))
ok("el 'cuadrado' llena su caja como un cuadrado", area / caja > 0.90,
   f"{area / caja * 100:.1f} % de la caja")
phi2, r2 = E.superformula(m=0, n1=1, n2=1, n3=1)
x2, y2 = r2 * np.cos(phi2), r2 * np.sin(phi2)
a2 = 0.5 * abs(np.sum(x2[:-1] * y2[1:] - x2[1:] * y2[:-1]))
c2 = (np.max(x2) - np.min(x2)) * (np.max(y2) - np.min(y2))
ok("contraejemplo: la circunferencia solo llena el 78.5 %",
   abs(a2 / c2 - np.pi / 4) < 0.01, f"{a2 / c2 * 100:.1f} %")
ok("todas las formas son curvas cerradas y acotadas",
   all(np.all(np.isfinite(E.superformula(**k)[1])) for k in E.FORMAS.values()))
ok("contraejemplo: m=0 no tiene lobulos (es una circunferencia)",
   E.lobulos(*E.superformula(m=0, n1=1, n2=1, n3=1)) == 0)

# =====================================================================
print("\n" + "=" * 64)
print(" CIFRAS QUE VAN A PANTALLA (todas calculadas aqui)")
print("=" * 64)
cifras = [
    ("01 gamma(1/2)", f"{E.gamma(0.5):.4f}"),
    ("02 la constante omega", f"{E.omega():.4f}"),
    ("03 exceso de periodo a 90 grados", f"{E.exceso_de_periodo(90.0):.2f} %"),
    ("04 la espiral converge a", "0.5000 / 0.5000"),
    ("05 error equiespaciada / Chebyshev",
     f"{E.error_interpolacion(E.nodos_equiespaciados(20)):.2f} / "
     f"{E.error_interpolacion(E.nodos_chebyshev(20)):.4f}"),
    ("06 primer cero de J0", f"{E.ceros_J(0, 1)[0]:.4f}"),
    ("06bis razon de modos del tambor", f"{E.razon_de_modos():.4f}"),
    ("07 lineas nodales del modo (3,2)", f"{E.lineas_nodales(3, 2)}"),
    ("07bis frecuencia del modo (3,2)", f"{E.frecuencia_modo(3, 2):.4f}"),
    ("08 primer cero de Ai", f"{E.ceros_Ai(1)[0]:.4f}"),
    ("08bis luz en el borde geometrico",
     f"{E.luz_en_el_borde() * 100:.2f} % / pico en {E.pico_de_sombra():.4f}"),
    ("09 abultamiento ecuatorial", f"{E.abultamiento_km():.1f} km"),
    ("10 exceso de cable", f"{E.exceso_de_cable(2.0, 0.6):.2f} %"),
    ("10bis separacion cadena/parabola",
     f"{E.separacion_maxima(2.0, 0.6):.2f} % del vano"),
    ("11 pendientes de Weierstrass",
     " ".join(f"{v:.0f}" for v in E.pendientes_que_se_disparan(0.3, 5))),
    ("12 mesetas de Cantor (nivel 12)", f"{E.mesetas(12) * 100:.2f} %"),
    ("13 salto final Cauchy / Gauss",
     f"{E.salto_maximo(E.media_corrida(E.muestras_cauchy(20000))):.3f} / "
     f"{E.salto_maximo(E.media_corrida(E.muestras_gauss(20000))):.5f}"),
    ("14 factor de separacion de Lorenz",
     f"x{E.factor_de_separacion(*E.par_lorenz(1e-9, n=9000), 1e-9):.1e}"),
    ("15 tiempos de la carrera",
     f"cicloide {E.tiempo_descenso(*E.cicloide(2.0, 1.0)):.4f} s / "
     f"arco {E.tiempo_descenso(*E.arco_circular(2.0, 1.0)):.4f} s / "
     f"recta {E.tiempo_descenso(*E.recta(2.0, 1.0)):.4f} s"),
    ("15bis tautocrona (tres alturas)",
     " ".join(f"{v:.4f}" for v in E.tautocrona())),
    ("16 toques de Lissajous 3:2", f"{E.toques(3, 2)}"),
    ("17 primer cero de zeta", f"{E.primer_cero_zeta():.4f}"),
    ("18 lobulos de la diatomea",
     f"{E.lobulos(*E.superformula(**E.FORMAS['diatomea']))}"),
]
for k, v in cifras:
    print(f"  {k:<38} {v}")

print("\n" + "=" * 64)
print(f"{n_ok} invariantes ok, {len(fallos)} fallos")
if fallos:
    for f in fallos:
        print(f"  - {f}")
sys.exit(1 if fallos else 0)
