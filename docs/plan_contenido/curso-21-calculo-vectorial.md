# Curso 23 — Cálculo vectorial (familia de lecciones)

- **Formato**: familia de lecciones, como Álgebra lineal (curso 22). Un
  proyecto de ManimStudio = una **lección** de 4 clips; cada clip = una
  idea. 4 módulos × 3 lecciones = **12 proyectos, 48 clips**.
- **Título de la familia**: `Cálculo vectorial`.
- **Ángulo editorial**: si Álgebra lineal fue *la rejilla que se mueve*,
  esto es **el espacio que fluye**. La materia se pierde en símbolos
  (∇, ∮, dS), así que aquí cada operador se VE: el paisaje escalar con sus
  curvas de nivel, el gradiente subiendo la colina, el campo lleno de
  flechas, las partículas siguiendo la corriente, la ruedecita que gira
  donde hay rotacional, la cajita que se vacía donde la divergencia es
  negativa, y los grandes teoremas COMPROBADOS con números medidos en
  pantalla (los dos lados de Green dan lo mismo y se ve la cuenta).
  Ejemplos con sabor aeroespacial/telecom donde salen solos (viento sobre
  un ala, gravedad de un planeta, la antena que radia, Maxwell como
  cierre), sin forzarlos.
- **Público**: divulgación técnica; asume el plano cartesiano, vectores
  (curso 22) y la idea de derivada. Las fórmulas se muestran, pero lo que
  se explica es lo que DICEN.
- **No pisa** cursos publicados: Electromagnetismo (curso 16) USA los
  campos E y B como protagonistas físicos; aquí el protagonista es el
  LENGUAJE (∇·, ∇×, ∮) y Maxwell aparece solo al final como recompensa.
- **Primer curso con la marca sonora**: el mux usa el intro/cierre con SFX
  espaciales (PRs #39–#41); nada que hacer en los clips — es posproducción.

```
familia            ManimStudio
-----------------  ----------------------------------------
módulo   (4)   →   —  (agrupación editorial, no existe en la DB)
lección  (12)  →   proyecto  "Cálculo vectorial · N.M <título>"
idea     (48)  →   clip      "MODULO 0K" en el HUD (K = número de clip)
```

Slugs `calculo-vectorial-N-M-<tema>`. Clips de 28–45 s (tope duro), pies
≥ 5 s legibles, el pie cambia ANTES de la animación que ilustra. Un solo
cierre a pantalla limpia por lección (clip 4).

## Principio visual no negociable

1. En cada clip se ve **el espacio** (plano con rejilla, o espacio3): los
   campos no flotan en el vacío. La rejilla es mobiliario (gris); lo que
   se mueve son las flechas del campo, las partículas y las curvas.
2. Todo operador se presenta **primero como movimiento, luego como
   fórmula**: el gradiente ES la flecha que sube; la divergencia ES la
   cajita por la que sale más de lo que entra; el rotacional ES la
   ruedecita que gira aunque el flujo vaya recto.
3. **Cada número en pantalla se calcula con numpy** en la librería o en el
   `style_block` (`fmt()`); nada escrito a mano. La flecha dibujada y la
   cifra rotulada salen del MISMO array. Los teoremas se COMPRUEBAN: los
   dos lados se miden por separado y coinciden en pantalla.
4. Los campos se muestran con **flechas escaladas y coloreadas por
   magnitud** (paleta fría→cálida) sobre una malla regular; las líneas de
   flujo se integran con RK4 (nada dibujado a ojo).
5. Un solo cierre a pantalla limpia por lección (dos líneas, la segunda en
   cian), como en Álgebra lineal.

## Mapa de las 12 lecciones

| Lección | Proyecto | Modelo | Clips |
|---------|----------|--------|-------|
| 1.1 | El paisaje: funciones de dos variables | Fable (molde) | 4 |
| 1.2 | Derivadas parciales: cortar el paisaje | Sonnet | 4 |
| 1.3 | El gradiente: la flecha que sube | Opus | 4 |
| 2.1 | El campo vectorial: flechas por todas partes | Sonnet | 4 |
| 2.2 | Líneas de flujo: seguir la corriente | Sonnet | 4 |
| 2.3 | La integral de línea: el trabajo de un camino | Opus | 4 |
| 3.1 | La divergencia: fuentes y sumideros | Sonnet | 4 |
| 3.2 | El rotacional: el remolino local | Sonnet | 4 |
| 3.3 | Campos conservativos: el camino no importa | Opus | 4 |
| 4.1 | El teorema de Green: el borde cuenta lo de dentro | Opus | 4 |
| 4.2 | Flujo y el teorema de la divergencia | Opus | 4 |
| 4.3 | Stokes y Maxwell: los campos que nos comunican | Opus | 4 |

Arco: el módulo 1 construye el paisaje escalar y su brújula (∇f); el 2
llena el espacio de flechas y aprende a recorrerlas (flujo, trabajo); el 3
mide lo local (∇·, ∇× y el premio de los conservativos); el 4 une lo local
con lo global (Green, divergencia, Stokes) y cierra leyendo Maxwell.

## Paleta de la familia (por ROL)

Hereda los hexes de la familia Álgebra lineal (marca única), con roles
adaptados al cálculo vectorial:

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_GRAD` | `#f59e0b` ámbar | el gradiente, la normal, la dirección estrella |
| `C_CIFRA` | `#22d3ee` cian | CIFRAS calculadas, tangentes, dt |
| `C_CAMPO` | `#3b82f6` azul | las flechas del campo (base; la magnitud las gradúa) |
| `C_VEC` | `#f43f5e` rojo | la partícula / el camino protagonista |
| `C_RES` | `#34d399` verde | el resultado medido: trabajo, flujo, ambos lados |
| `C_FLUJO` | `#e879f9` fucsia | líneas de flujo / corriente |
| `C_REGION` | `#fb923c` naranja | la región de integración sombreada, su borde |
| `C_REJILLA` | `#31414f` | rejilla fija (mobiliario) |
| `C_EJE` | `#94a0b0` muted | ejes |
| `C_NIVEL_*` | frío→cálido | curvas de nivel por altura (azul bajo → ámbar alto) |

Regla: **el color dice el papel**. Ámbar es SIEMPRE la dirección
privilegiada (∇f, la normal n̂); rojo el camino o la partícula de la que se
habla; verde lo que sale de la cuenta; fucsia la corriente; naranja la
región y su borde; cian las cifras.

## Librería `manim_extensions/calculo_vectorial.py` (contrato)

Determinista, numpy puro, sin red/disco/azar. **Importa de
`algebra_lineal`** (mismo sys.path) el sustrato: `plano`, `espacio3`,
`vector`, `flecha_libre`, `fmt`, `grafica` y la paleta. Piezas `VGroup`
con localizadores que siguen `move_to` (no `scale`).

```python
# --- números (validados en el contenedor antes de escribir clips) ----
parcial(f, p, i, h=1e-5)              # derivada parcial central
grad_num(f, p)                        # gradiente numérico (2D o 3D)
div_num(F, p) / rot_num(F, p)         # divergencia y rotacional escalar (2D)
rot3_num(F, p)                        # rotacional vector (3D)
integral_linea(F, curva, a, b, n=2000)     # ∫ F·dr por Simpson sobre r(t)
integral_linea_escalar(f, curva, a, b)     # ∫ f ds
circulacion(F, curva_cerrada)              # ∮ F·dr
flujo_curva(F, curva_cerrada)              # ∮ F·n ds (2D)
integral_doble(g, region, n=400)           # ∬ g dA (malla regular)
flujo_caja3(F, centro, lado, n=40)         # ∯ F·dS por las 6 caras
flujo_parche(F, S, ...)                    # ∬ F·dS sobre parche paramétrico
potencial_comprobado(F, phi, puntos)       # max |∇φ−F| en una malla (≈0)
# --- catálogo de campos y paisajes (cerrado y con cifras cabeza) -----
paisaje_colinas / paisaje_silla / paisaje_valle      # f(x,y) suaves
campo_radial   F=(x,y)        div=2   rot=0
campo_rotor    F=(-y,x)       div=0   rot=2
campo_silla    F=(x,-y)       div=0   rot=0
campo_cizalla  F=(y,0)        div=0   rot=-1
campo_remolino_amortiguado / campo_viento (para líneas de flujo bonitas)
campo_gravedad F=-r/|r|^3 (2D, conservativo: phi=-1/r)
campo_fuente   F=r/|r|^2  (2D: div=0 fuera del origen; flujo=2*pi si encierra)
campo_dipolo3, campo_radial3  (3D para Gauss/Stokes)
# --- piezas 2D (sobre plano de algebra_lineal) -----------------------
campo_flechas(pl, F, paso=1.0, escala=0.35)   # malla de flechas, color por |F|; .en(x,y)
curvas_nivel(pl, f, niveles)                  # marching squares; color por nivel
linea_flujo(pl, F, p0, T, color=C_FLUJO)      # streamline RK4; .curva (para Create)
particulas(pl, F, semillas, T)                # Dots + trayectorias para MoveAlongPath
camino(pl, r, a, b, color=C_VEC)              # curva paramétrica; .punto(t), .tangente_en(t)
rueda(pl, p, radio=0.42)                      # ruedecita de paletas (rotacional); girar con Rotate
caja_conteo(pl, p, lado=1.2)                  # cajita con flechas entrando/saliendo (divergencia)
region_rect(pl, x0, x1, y0, y1)               # región sombreada + borde orientado con flechas
normales_borde(pl, curva)                     # flechitas n̂ hacia fuera
# --- piezas 3D (sobre espacio3 de algebra_lineal) --------------------
superficie3(esp, f, ...)                      # malla de alambre z=f(x,y), color por altura
flechas3(esp, F, paso)                        # campo 3D disperso
parche3(esp, S, ...)                          # parche paramétrico + normales ámbar
```

Cifras cabeza (validar EN el contenedor antes de escribir clips):
rot del rotor = 2 y su circulación en el círculo r=1.5 es 2·π·1.5² =
14.137; div del radial = 2 y su flujo por ese círculo también 14.137
(¡el mismo número, cada teorema con el suyo!); el trabajo de F=∇φ con
φ=x²y entre (0,0) y (2,1) da 4.0 por tres caminos distintos; Green sobre
el cuadrado [−1,1]² con F=(x²−y, x+y²): ambos lados 8.0 (rot=2, área 4); flujo de
F=(x,y,z) por el cubo unidad = 3.0 = ∭ div; Stokes con F=(−y,x,0) sobre el
parche z=0: ∮ = 2·área.

## Contrato para los subagentes (una lección por agente)

Idéntico al de Álgebra lineal (mismo worktree, mismas reglas duras, misma
validación `render_local.py <curso_dir> --clip N --frames 8` + revisión de
los 8 frames con Read), con el molde en
`studio/content/cursos/calculo-vectorial-1-1-el-paisaje/`. Los agentes NO
tocan la librería; reportan lo que falte.

## Tablero de estado

Columnas: storyboard · clips escritos · validada ql · en repo/PR · qh
local · adoptada en prod · narrada · muxeada.

| Lección | storyboard | clips | ql | repo/PR | qh | prod | narrada | mux |
|---------|-----------|-------|----|---------|----|------|---------|-----|
| 1.1 | ✔ | ✔ | ✔ 30.3/30.5/29.9/29.9 s | — | — | — | — | — |
| 1.2 | ✔ | ✔ | ✔ 31.0/29.7/35.3/32.9 s | — | — | — | — | — |
| 1.3 | ✔ | ✔ | ✔ 31.5/37.1/32.1/39.9 s | — | — | — | — | — |
| 2.1 | ✔ | ✔ | ✔ 31.7/39.7/30.9/30.1 s | — | — | — | — | — |
| 2.2 | ✔ | ✔ | ✔ 33.9/30.8/29.5/35.7 s | — | — | — | — | — |
| 2.3 | ✔ | — | — | — | — | — | — | — |
| 3.1 | ✔ | — | — | — | — | — | — | — |
| 3.2 | ✔ | — | — | — | — | — | — | — |
| 3.3 | ✔ | — | — | — | — | — | — | — |
| 4.1 | ✔ | — | — | — | — | — | — | — |
| 4.2 | ✔ | — | — | — | — | — | — | — |
| 4.3 | ✔ | — | — | — | — | — | — | — |

## Módulo 1 — El paisaje escalar

### 1.1 El paisaje: funciones de dos variables  (slug `calculo-vectorial-1-1-el-paisaje`)

Hilo: una función de dos variables es un paisaje → se puede ver como
superficie o como mapa → las curvas de nivel son el mapa topográfico →
subir rápido o lento depende de la dirección.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Un número para cada punto | plano con rejilla; en varios puntos aparece su altura f(x,y) como cifra; el paisaje como tabla imposible | plano salpicado de alturas medidas |
| 2 | La superficie | espacio3: la malla z=f(x,y) se levanta desde el plano; colinas y valle | superficie de alambre coloreada por altura |
| 3 | El mapa: curvas de nivel | de la superficie 3D al mapa 2D; las curvas de nivel aparecen nivel a nivel, frío→cálido | mapa de curvas de nivel completo con leyenda de alturas |
| 4 | Caminar el paisaje | una partícula recorre el mapa: cruzando niveles sube, siguiendo un nivel no; cierre | cierre «Una función de dos variables es un paisaje. / Las curvas de nivel son su mapa.» |

### 1.2 Derivadas parciales: cortar el paisaje  (slug `calculo-vectorial-1-2-parciales`)

Hilo: para derivar en 2D se corta el paisaje con un plano → ∂f/∂x es la
pendiente del corte en x → ∂f/∂y la del corte en y → juntas forman el
plano tangente (la mejor aproximación lineal).

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | ¿Pendiente de qué dirección? | en el mapa, desde un punto salen varias direcciones con distinta subida medida | punto con varias flechas y sus pendientes |
| 2 | Cortar con x: ∂f/∂x | espacio3: el plano y=cte rebana la superficie; la curva del corte pasa a una grafica 2D con su tangente | corte y pendiente ∂f/∂x medida |
| 3 | Cortar con y: ∂f/∂y | el corte perpendicular; mismas dos vistas; las dos parciales juntas en el panel | ambas parciales en el panel, cifras de la librería |
| 4 | El plano tangente | cerca del punto, la superficie y su plano tangente casi coinciden (zoom del error); cierre | cierre «Derivar en 2D es cortar. / Dos cortes bastan.» |

### 1.3 El gradiente: la flecha que sube  (slug `calculo-vectorial-1-3-gradiente`)

Hilo: las dos parciales forman un vector → ∇f apunta a la máxima subida →
es perpendicular a las curvas de nivel → la derivada direccional es
∇f·û (el coseno manda).

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Dos números, una flecha | (∂f/∂x, ∂f/∂y) se ensambla como vector ámbar en el mapa | ∇f en un punto con sus componentes |
| 2 | La máxima subida | abanico de direcciones desde el punto con su subida medida; la mayor coincide con ∇f | abanico + ∇f ganador con cifra |
| 3 | Perpendicular al nivel | en varios puntos del mapa, ∇f sale perpendicular a la curva de nivel local | mapa con gradientes perpendiculares a los niveles |
| 4 | La brújula del paisaje | una partícula sigue ∇f y sube al pico (ascenso por gradiente); cierre | cierre «El gradiente apunta a la subida. / Seguirlo es escalar.» |

## Módulo 2 — Campos y caminos

### 2.1 El campo vectorial: flechas por todas partes  (slug `calculo-vectorial-2-1-campo`)

Hilo: un campo asigna una flecha a cada punto → se dibuja muestreando una
malla → hay familias con carácter (radial, rotor, silla, cizalla) → el
gradiente de un paisaje ES un campo.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Una flecha en cada punto | el plano se llena de flechas (campo viento); en 3 puntos se lee F(x,y) con cifras | campo completo con tres lecturas |
| 2 | El catálogo | radial, rotor, silla y cizalla desfilan con su fórmula | los cuatro carácteres vistos |
| 3 | El campo gradiente | del paisaje 1.1: en cada punto ∇f; las flechas apuntan cuesta arriba, grandes donde empina | mapa de niveles + campo ∇f encima |
| 4 | Campos de verdad | viento sobre un perfil de ala (cizalla + remolino), gravedad de un planeta (radial hacia dentro); cierre | cierre «Un campo es una flecha en cada punto. / El espacio entero, hablando.» |

### 2.2 Líneas de flujo: seguir la corriente  (slug `calculo-vectorial-2-2-lineas-de-flujo`)

Hilo: suelta una partícula y el campo la lleva → su trayectoria es la
línea de flujo (tangente al campo en cada punto) → se calcula paso a paso
(RK4) → la familia de líneas retrata el campo mejor que las flechas.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Suelta una partícula | en el campo viento, un punto rojo avanza tangente a las flechas; su rastro fucsia queda | una línea de flujo trazada |
| 2 | Paso a paso | zoom: avanzar un poquito en la dirección de la flecha, releer, avanzar (Euler→RK4 como refinamiento) | poligonal de pasos vs curva suave |
| 3 | La familia entera | muchas semillas a la vez: el retrato de fase del remolino amortiguado | familia de líneas de flujo en fucsia |
| 4 | Retratos con carácter | radial: rectas que huyen; rotor: círculos; silla: hipérbolas; cierre | cierre «El campo es un mapa de corrientes. / Las líneas de flujo son sus ríos.» |

### 2.3 La integral de línea: el trabajo de un camino  (slug `calculo-vectorial-2-3-integral-de-linea`)

Hilo: mover una partícula contra el campo cuesta → en cada tramito cuenta
F·dr (solo la componente tangente) → sumar tramitos es ∫F·dr → el signo
dice si el campo ayuda o estorba.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | El campo cobra peaje | un camino rojo cruza el campo; en varios puntos, F y el paso dr con su ángulo | camino con F y dr comparados |
| 2 | Solo cuenta lo tangente | en un punto del camino: F se descompone en tangente (cuenta) y normal (no); F·dr como cifra | descomposición con la cifra F·dr |
| 3 | Sumar tramitos | el camino se trocea; la suma parcial crece en un contador hasta ∫F·dr (Simpson de la librería) | camino barrido + trabajo total medido |
| 4 | A favor o en contra | el mismo camino recorrido al revés cambia el signo; en el rotor, un circuito cerrado acumula 14.14; cierre | cierre «El trabajo se paga por tramos. / El camino y el sentido importan.» |

## Módulo 3 — Lo local: fuentes y remolinos

### 3.1 La divergencia: fuentes y sumideros  (slug `calculo-vectorial-3-1-divergencia`)

Hilo: pon una cajita en el campo → ¿sale más de lo que entra? → ese
balance por unidad de área es ∇·F → positivo fuente, negativo sumidero,
cero incompresible.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | La cajita contable | cajita en el campo radial: flechas salen por los 4 lados; el balance medido es positivo | caja con flujos por lado y balance |
| 2 | Fuente, sumidero, neutro | la misma cajita en radial (+), radial invertido (−) y rotor (0) | tres cajitas con sus cifras |
| 3 | La fórmula | ∂Fx/∂x + ∂Fy/∂y: cada término como estirón horizontal/vertical de la cajita | fórmula conectada al dibujo, div medida |
| 4 | El mapa de la divergencia | el plano coloreado por ∇·F (remolino amortiguado: sumidero al centro); las partículas se acumulan; cierre | cierre «La divergencia es el balance de la cajita. / Fuentes y sumideros, punto a punto.» |

### 3.2 El rotacional: el remolino local  (slug `calculo-vectorial-3-2-rotacional`)

Hilo: pon una ruedecita de paletas en el campo → si gira, hay rotacional →
gira incluso en flujos "rectos" (cizalla) → ∂Fy/∂x − ∂Fx/∂y mide ese giro
con signo.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | La ruedecita | en el rotor, la ruedecita gira; su velocidad de giro medida = rot/2 | ruedecita girando con cifra |
| 2 | El engaño del flujo recto | en la cizalla F=(y,0) todo va horizontal ¡y la ruedecita gira! (arriba empuja más) | cizalla con ruedecita girando y por qué |
| 3 | La fórmula del giro | ∂Fy/∂x − ∂Fx/∂y término a término sobre el dibujo; el radial da 0 | fórmula conectada, rot medido en dos campos |
| 4 | El mapa del giro | plano coloreado por ∇×F; ruedecitas sembradas giran donde toca; cierre | cierre «El rotacional es la ruedecita. / Gira aunque el río vaya recto.» |

### 3.3 Campos conservativos: el camino no importa  (slug `calculo-vectorial-3-3-conservativos`)

Hilo: en el campo gradiente el trabajo solo depende de los extremos →
tres caminos, el mismo número → ∮=0 y rot=0 → existe potencial φ y
∫∇φ·dr = φ(B)−φ(A) (el teorema fundamental).

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Tres caminos, un número | de A a B por recta, arco y escalera: el contador da 4.0 las tres veces | tres caminos con el mismo trabajo |
| 2 | El circuito gratis | ida por un camino, vuelta por otro: ∮=0; en el rotor NO (14.14) | dos circuitos comparados |
| 3 | El potencial | el paisaje φ reaparece: F=∇φ; el trabajo es bajar de nivel: φ(B)−φ(A) medido | mapa de φ con A, B y la resta |
| 4 | El test del rotacional | rot(∇φ)=0 comprobado; la gravedad es conservativa: la órbita no cobra peaje; cierre | cierre «Si el campo es un gradiente, el camino da igual. / Solo cuentan los extremos.» |

## Módulo 4 — Lo global: los grandes teoremas

### 4.1 El teorema de Green: el borde cuenta lo de dentro  (slug `calculo-vectorial-4-1-green`)

Hilo: las ruedecitas interiores se cancelan entre sí → solo sobrevive el
borde → ∮F·dr = ∬rot dA → se comprueba con números y se usa para medir
áreas.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Ruedecitas que se cancelan | la región naranja embaldosada de circulaciones; las flechas interiores se anulan por pares | mosaico con cancelación interior |
| 2 | Solo queda el borde | las baldosas se funden: sobrevive el circuito del borde orientado | región + borde con flechas |
| 3 | La comprobación | ∮ por el borde (medido) y ∬rot (medido): 8.0 = 8.0 en pantalla | los dos lados iguales, en verde |
| 4 | Medir áreas caminando | con F=(−y/2, x/2), ∮ = área: el planímetro; el área de una figura medida por su contorno; cierre | cierre «Lo de dentro se cancela. / El borde lo cuenta todo.» |

### 4.2 Flujo y el teorema de la divergencia  (slug `calculo-vectorial-4-2-teorema-divergencia`)

Hilo: el flujo por una curva/superficie cuenta lo que la cruza → las
cajitas interiores se cancelan → ∯F·dS = ∭∇·F dV → comprobado en el cubo;
la ley de Gauss es esto.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | El flujo: contar cruces | curva cerrada en el campo radial; las normales n̂ ámbar; F·n̂ sumado = 14.14 | curva con normales y flujo medido |
| 2 | Cajitas que se cancelan | la región embaldosada: lo que sale de una cajita entra en la vecina; queda el borde | mosaico de cajitas con cancelación |
| 3 | En 3D: el cubo | espacio3: F=(x,y,z) por el cubo unidad: 6 caras medidas, total 3.0 = ∭div | cubo con flujos por cara y la igualdad |
| 4 | La ley de Gauss | el campo fuente r/|r|²: el flujo solo ve lo ENCERRADO (2π si encierra, 0 si no); cierre | cierre «Suma las fuentes de dentro. / O cuenta lo que cruza la frontera.» |

### 4.3 Stokes y Maxwell: los campos que nos comunican  (slug `calculo-vectorial-4-3-stokes-maxwell`)

Hilo: Green en 3D es Stokes (la circulación del borde = el rotacional que
atraviesa el parche) → con ∇·, ∇× y los teoremas se LEEN las cuatro
ecuaciones de Maxwell → el rotacional encadenado E↔B es la onda que baja
del satélite. Cierre de familia.

| Clip | Título | Visual | `final_state` |
|------|--------|--------|---------------|
| 1 | Green se levanta: Stokes | espacio3: el circuito plano se abomba en parche; ∮ = ∬(∇×F)·dS medido en ambos | parche con normales y la igualdad |
| 2 | Leer a Maxwell I | ∇·E = ρ/ε0 y ∇·B = 0 LEÍDAS: cargas como fuentes (radial), B sin fuentes (dipolo cerrado) | las dos leyes de divergencia con sus dibujos |
| 3 | Leer a Maxwell II | ∇×E = −∂B/∂t y ∇×B = μ0ε0 ∂E/∂t: el remolino de E abraza al B que cambia, y al revés | las dos leyes de rotacional encadenadas |
| 4 | La onda | E y B perpendiculares avanzando (c calculada de μ0ε0); la señal llega a la antena; cierre de familia | cierre «Cuatro renglones de ∇. / Toda la luz, toda la radio.» |
