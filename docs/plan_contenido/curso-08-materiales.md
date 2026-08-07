# Curso 08 — Materiales que van al espacio

- **Proyecto**: name `Materiales que van al espacio`, quality `qh`.
- **Fuente**: Academy, Materiales aeroespaciales M1 (Lennard-Jones,
  enlace→propiedades), M2 (familias), M3 (resistencia especifica,
  fatiga), M4 (avanzados, pincelada), M5 (degradacion) + Elasticidad
  M1 (fundamentos atomicos de rigidez).
- **Slug**: `materiales-que-van-al-espacio`.
- **Publico**: divulgacion; cierra la cola del plan.
- **Hilo narrativo**: todo empieza en un enlace (Lennard-Jones) → del
  pozo a la rigidez (E) → las cuatro familias → fuerte no es rigido
  (curva σ-ε) → el gramo que cuesta oro (σ/ρ, Ashby) → la fatiga →
  el espacio muerde (degradacion) → elegir material y cierre.

## Paleta del curso

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_ATOMO` | `#f59e0b` ambar | atomos, enlaces, la curva del potencial |
| `C_MAT` | `#22d3ee` cian | el material ganador, la propiedad destacada |
| `C_FAM` | `#a78bfa` violeta | familias alternativas, comparaciones |
| `C_FALLA` | `#f43f5e` rojo | fractura, fatiga, degradacion |
| `C_OK` | `#34d399` verde | zona elastica, material apto |
| `C_EJE` | `#31414f` | mobiliario |

Regla: el ATOMO/enlace es ambar, el material PROTAGONISTA cian, las
FAMILIAS violeta, la FALLA roja, lo APTO verde.

## Contrato de la libreria `studio/content/manim_extensions/materia.py`

Determinista, sin red, sin archivos. Estilo radio.py/apuntado.py.
Topes: `ATOMOS_MAX = 60`, `MUESTRAS_MAX = 400`.

```python
pozo_lennard_jones(ancho=4.8, alto=2.8, color="#f59e0b",
                   color_ejes="#31414f", font_size=14)
    # -> PozoLJ(VGroup): ejes (r ->, U ^) con la curva 4eps[(s/r)^12 -
    #    (s/r)^6]; linea punteada vertical en r0 (el minimo). Metodos
    #    .punto_de(r_rel) sobre la curva (r_rel=1 es r0) y
    #    .fondo() -> np.array del minimo. Atributos .curva, .r0_linea.
par_atomos(separacion=1.6, radio=0.28, color="#f59e0b")
    # -> ParAtomos(VGroup): dos circulos con brillo suave unidos por un
    #    resorte zigzag corto. Metodo .separar(d) (redibuja el resorte,
    #    d = separacion nueva en unidades de escena). Atributos .a, .b,
    #    .resorte, .separacion.
red_atomica(filas=4, columnas=6, paso=0.62, color="#f59e0b",
            color_resorte="#31414f")
    # -> RedAtomica(VGroup): malla de atomos unidos por resortes
    #    (lineas zigzag finas). Metodo .cizallar(dx) que desplaza cada
    #    fila proporcionalmente a su altura (deformacion visual
    #    elastica). Atributos .atomos, .resortes.
curva_esfuerzo(familia="metal", ancho=4.6, alto=2.6, color="#22d3ee",
               color_ejes="#31414f", font_size=14)
    # -> CurvaSigmaEps(VGroup): ejes (deformacion ->, esfuerzo ^) con
    #    la curva tipica de la familia: "metal" (recta elastica + codo
    #    de fluencia + meseta ductil + caida), "ceramico" (recta
    #    empinada que se corta en seco, marca X roja al final),
    #    "polimero" (curva baja y muy larga), "compuesto" (recta alta
    #    casi hasta el final, corte seco). Metodo .punto_en(t_rel)
    #    sobre la curva; atributos .curva, .zona_elastica (VMobject
    #    translucido verde bajo el tramo recto inicial, opacity 0 para
    #    FadeIn), .marca_falla (X roja al final o None).
mapa_ashby(ancho=4.9, alto=3.0, font_size=14)
    # -> MapaAshby(VGroup): ejes log-log (densidad ->, resistencia ^)
    #    con 4 burbujas elipticas etiquetadas: POLIMEROS (abajo-izq,
    #    violeta), METALES (centro-der, violeta), CERAMICOS
    #    (arriba-der, violeta), COMPUESTOS (arriba-IZQUIERDA, cian —
    #    el barrio dorado). Metodo .burbuja(nombre) -> VGroup.
    #    Diagonales punteadas de sigma/rho constante (2) en gris.
curva_sn(ancho=4.8, alto=2.4, color="#f43f5e", color_ejes="#31414f",
         font_size=14)
    # -> CurvaSN(VGroup): ejes (ciclos log ->, amplitud de esfuerzo ^)
    #    con la curva de fatiga descendente y linea punteada horizontal
    #    del limite de fatiga. Metodo .punto_en(t_rel) sobre la curva.
    #    Atributos .curva, .limite.
grieta(largo=1.4, dientes=7, color="#f43f5e")
    # -> VMobject zigzag de grieta (para crecer con Create sobre una
    #    pieza); determinista.
placa_con_ciclos(ancho=2.6, alto=1.5, color="#94a0b0")
    # -> VGroup placa redondeada con una flecha doble vertical (carga
    #    ciclica) encima; para el beat de fatiga. Atributos .placa,
    #    .flechas.
```

Demo obligatoria:
`studio/content/animations/experimentacion/20-materia.py` con
`DemoMateria(Scene)` (~15 s): pozo LJ con punto oscilando en el fondo,
par_atomos separandose y volviendo, red_atomica cizallando, curva
sigma-eps de metal vs ceramico (transform), mapa_ashby con la burbuja
de compuestos resaltada, curva S-N con punto y una grieta creciendo
sobre placa_con_ciclos.

## Reglas duras para los clips

Identicas a los cursos previos: solo `class ClipN(Scene)`; Rotulos;
28-45 s tope INVIOLABLE; pies >= 5 s; determinismo; solo paleta;
`# --- momento ---`; final_state literal; el pie cambia ANTES del
transform que ilustra.

## Storyboard clip a clip

### Clip 1 — `1 · Todo empieza en un enlace` (~35 s, `Clip1`)
Portada `titulo_marca("Materiales", 46)` + subtitulo ambar «que van al
espacio». Titulo «Todo empieza en un enlace». `par_atomos` centrado
(y≈+0.8) + `pozo_lennard_jones` debajo (y≈-1.0, ancho 4.4, alto 2.0).
Pie: «Un cohete, un ala, un tornillo: en el fondo, átomos tomados de la
mano.» Un punto brillante en el fondo del pozo. Pie: «Dos fuerzas en
guerra —atracción lejos, repulsión cerca— cavan un pozo.»
`formula_pie` con el LJ compacto:
`U(r) = 4\\varepsilon[(\\sigma/r)^{12} - (\\sigma/r)^6]`. Pie: «El
fondo del pozo es la distancia de equilibrio: ahí viven.» Los atomos
se separan y regresan (2 veces, .separar) sincronizado con el punto
subiendo y bajando la pared del pozo. Pie gancho: «De la forma de ese
pozo sale TODO lo demás.»
**final_state**: par de atomos arriba, pozo LJ abajo con punto en el
fondo.

### Clip 2 — `2 · Del pozo a la rigidez` (~36 s, `Clip2`)
Titulo «Del pozo a la rigidez». `pozo_lennard_jones` a la izquierda
(x≈-2.9, y≈-0.1). Pie: «Cerca del fondo, el pozo parece una parábola:
el átomo está atado a un resorte.» Un arco parabolico verde se
superpone al fondo del pozo (el agente lo dibuja con FunctionGraph
corto). Acto 2: derecha (x≈+2.9, y≈-0.1) `red_atomica`. Pie: «Un
material es una multitud de esos resortes en formación.» La red
`.cizallar` suavemente y regresa (2 veces). Pie: «Pozo profundo y
angosto: resortes duros. Eso, a lo grande, es el módulo de Young.»
`formula_pie("E \\propto U''(r_0)")`. Pie cierre: «La rigidez de un
ala se decidió en un enlace.» **final_state**: pozo con parabola verde
a la izquierda, red atomica a la derecha.

### Clip 3 — `3 · Las cuatro familias` (~37 s, `Clip3`)
Titulo «Las cuatro familias». Cuatro `bloque` en grid 2x2 centrado
(y≈-0.1, separacion generosa): «METALES», «CERÁMICOS», «POLÍMEROS»,
«COMPUESTOS» (violeta; COMPUESTOS cian). Pies en relevo mientras cada
bloque pulsa: «Metales: dúctiles y confiables — se doblan antes de
romper.» → «Cerámicos: durísimos y frágiles — aguantan calor, no
perdonan golpes.» → «Polímeros: ligeros y flexibles — hasta que sube
la temperatura.» → «Compuestos: fibras rígidas en matriz ligera. Lo
mejor de dos mundos.» Pie cierre: «Cuatro caracteres. La misión elige
con cuál casarse.» **final_state**: grid 2x2 con COMPUESTOS resaltado
cian.

### Clip 4 — `4 · Fuerte no es lo mismo que rigido` (~38 s, `Clip4`)
Titulo «Fuerte no es lo mismo que rígido». `curva_esfuerzo("metal")`
centrada (y≈-0.1). Pie: «Estira un metal y dibuja su biografía: la
curva esfuerzo-deformación.» La `.zona_elastica` verde FadeIn; pie:
«La pendiente inicial es la rigidez: aquí todo es reversible.» El
punto recorre hasta el codo; pie: «Pasado el límite elástico, la
deformación se queda: fluencia.» Sigue hasta el final; pie: «Y la
meseta dúctil avisa antes de romper: el metal se queja.» Acto 2: (pie
ANTES) «El cerámico no avisa: rígido, fuerte... y de repente, nada.»;
ReplacementTransform a `curva_esfuerzo("ceramico")` con su X roja
pulsando. Pie cierre: «Rigidez, resistencia y ductilidad: tres
virtudes distintas. Nadie tiene las tres.»
**final_state**: curva del ceramico con su marca de falla roja.

### Clip 5 — `5 · El gramo que cuesta oro` (~37 s, `Clip5`)
Titulo «El gramo que cuesta oro». Pie: «Poner un kilo en órbita cuesta
miles de dólares: aquí no gana el más fuerte, gana el más fuerte POR
GRAMO.» `formula_pie("\\sigma_{esp} = \\sigma_y / \\rho")`.
`mapa_ashby` centrado (y≈-0.15). Pie: «El mapa de Ashby: densidad
contra resistencia. Cada familia, su barrio.» Las burbujas aparecen
una a una (FadeIn secuencial rapido). Pie: «Las diagonales son lineas
de empate: misma resistencia por kilo.» (las diagonales se dibujan).
La burbuja COMPUESTOS pulsa cian. Pie: «Arriba a la izquierda, el
barrio dorado: fuerte y ligero. Ahí viven la fibra de carbono y el
titanio de las naves.» Pie cierre: «Por eso los aviones dejaron el
acero en el suelo.» **final_state**: mapa de Ashby completo con
COMPUESTOS resaltado.

### Clip 6 — `6 · Morir de mil ciclos` (~37 s, `Clip6`)
Titulo «Fatiga: morir de mil ciclos». Izquierda (x≈-3.0, y≈-0.1)
`placa_con_ciclos`; las flechas pulsan ritmicamente (3 pulsos). Pie:
«Ninguna carga rompe el ala hoy. Pero sube y baja diez mil veces por
vuelo.» `grieta` crece sobre la placa (Create lento, 2 etapas). Pie:
«Cada ciclo empuja una grieta invisible, un paso más.» Acto 2: derecha
(x≈+2.9, y≈-0.1) `curva_sn`. Pie: «La curva S-N dicta la sentencia:
menos carga, más vidas.» La `.limite` punteada pulsa verde; pie:
«Bajo el límite de fatiga, el acero vive para siempre. El aluminio
no lo tiene: todo vuelo le cuesta vida.» Pie cierre: «Por eso los
aviones se retiran por ciclos, no por años.»
**final_state**: placa con grieta a la izquierda, curva S-N con su
limite a la derecha.

### Clip 7 — `7 · El espacio muerde` (~36 s, `Clip7`)
Titulo «El espacio muerde». Placa central (`placa_con_ciclos` sin usar
flechas o RoundedRectangle gris, y≈-0.1) rodeada de cuatro amenazas
que aparecen en relevo (cada una: icono simple + tag_junto, se
atenua a opacity 0.4 antes de entrar la siguiente):
1. arriba-izq: sol estilizado (circulo + rayos cortos) rojo, tag
   «±200 °C por órbita». Pie: «Cada 90 minutos, del horno al
   congelador: el ciclado térmico fatiga sin tocar.»
2. arriba-der: 3 puntitos veloces (lineas con punta) tag «oxígeno
   atómico». Pie: «En órbita baja, oxígeno atómico: lija química que
   adelgaza superficies.»
3. abajo-izq: rayos punteados violeta, tag «radiación UV». Pie: «La
   radiación rompe cadenas de polímero: lo flexible se vuelve
   quebradizo.»
4. abajo-der: punto con estela, tag «micrometeoritos». Pie:
   «Y basura y polvo a 15 km/s: cráteres del tamaño de un grano de
   sal.»
Pie cierre: «En el espacio no hay taller: el material aguanta solo o
la misión muere.» **final_state**: placa central con las cuatro
amenazas alrededor (todas visibles, la ultima plena).

### Clip 8 — `8 · Elegir con qué volar` (~38 s, `Clip8`)
Titulo «Elegir con qué volar». `mapa_ashby` a la izquierda (x≈-2.9,
y≈-0.1, escala 0.85); a la derecha (x≈+3.0) tres etiquetas HUD en
columna, espaciadas, que aparecen una a una: «RÍGIDO Y LIGERO»,
«MIL CICLOS TÉRMICOS», «AÑOS SIN TALLER». Pie: «Una misión es una
lista de exigencias que se contradicen.» Pie: «El material ganador
nunca es el mejor en todo: es el que menos compromete.» La burbuja
COMPUESTOS pulsa y un check verde aparece a su lado. Pie: «Para el
espacio, casi siempre: compuestos y aleaciones ligeras, elegidos
gramo a gramo.» Acto final: todo se desvanece → tarjeta de cierre
`titulo_marca("Materiales", 46)` + subtitulo ambar «que van al
espacio» + subrayado `con_brillo`. `self.wait(2)`.
**final_state**: tarjeta de cierre centrada, pantalla limpia salvo
esquinas HUD y marca de agua.

## Descripcion del proyecto (campo description)

Curso de divulgación en 8 clips sobre materiales aeroespaciales: del
pozo de Lennard-Jones a la rigidez macroscópica, las cuatro familias
de materiales, la curva esfuerzo-deformación, la resistencia
específica y el mapa de Ashby, la fatiga por ciclos, la degradación en
el ambiente espacial y la elección de material de una misión. Estilo
3Blue1Brown en español.
