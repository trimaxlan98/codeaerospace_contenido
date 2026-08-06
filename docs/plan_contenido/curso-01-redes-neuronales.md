# Curso 01 — Redes neuronales: la maquina que aprende

- **Proyecto**: name `Redes neuronales: la máquina que aprende`, quality `qh`.
- **Fuente**: Academy, curso Inteligencia Artificial, lecciones 2-6
  (`prisma/seed-data/inteligencia-artificial.ts`).
- **Slug**: `redes-neuronales-la-maquina-que-aprende`.
- **Publico**: divulgacion estilo 3Blue1Brown en español; estudiante de
  ingenieria sin experiencia previa en ML.
- **Hilo narrativo**: error → gradiente → recta que aprende → neurona →
  el muro de XOR → capas ocultas → backpropagation → sobreajuste.

## Paleta del curso (se suma a la marca CO.DE)

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_DATO_A` | `#22d3ee` cian | datos clase A / flujo hacia adelante |
| `C_DATO_B` | `#a78bfa` violeta | datos clase B |
| `C_PERDIDA` | `#f43f5e` rojo | error, perdida, divergencia, mal clasificado |
| `C_OK` | `#34d399` verde | acierto, modelo que generaliza |
| `C_ACENTO` | `#f59e0b` ambar | el MODELO: rectas, fronteras, bola de gradiente, pesos |
| `C_EJE` | `#31414f` | ejes y rejilla |

Regla de color: los **datos** son cian/violeta, el **modelo** es ambar, el
**error** es rojo, el **acierto** es verde. No mezclar roles.

## Contrato de la libreria `studio/content/manim_extensions/aprendizaje.py`

Todo determinista (semillas fijas), sin red, sin archivos. numpy puro para el
calculo; mobjects de Manim para la parte visual. Topes: `RES_MAX = 512`,
`EPOCAS_MAX = 4000`, `PUNTOS_MAX = 400`.

```python
# --- datasets: devuelven (X, y) con X (n,2) en [-2, 2]^2, y en {0, 1} ---
datos_dos_nubes(n=60, separacion=1.5, semilla=7)
datos_circulos(n=90, radio=1.25, ruido=0.14, semilla=7)   # anillo vs centro
datos_xor(n=56, ruido=0.16, semilla=7)                    # 4 racimos alternos
datos_recta(n=26, pendiente=0.55, ordenada=0.25, ruido=0.28, semilla=7)
    # -> (xs, ys) 1D para regresion, xs en [-2, 2]

# --- calculo ---
class MLP:            # 2 -> ocultas (tanh) -> 1 (sigmoide)
    predecir(self, X) # -> probabilidades (n,)

entrenar_mlp(X, y, ocultas=4, epocas=1200, lr=0.9, semilla=3,
             instantaneas=12)
    # -> Entrenamiento con .perdidas (list[float], una por epoca) y
    #    .modelos (list[MLP], `instantaneas` copias espaciadas, la primera
    #    es el modelo inicial y la ultima el final)

entrenar_regresion(xs, ys, epocas=60, lr=0.08)
    # -> list[(m, b, mse)] por epoca (descenso de gradiente sobre MSE)

descenso_1d(df, x0=1.8, lr=0.3, pasos=8)
    # -> list[float] trayectoria x_k (df = derivada de la funcion de perdida)

# --- mobjects (siempre reciben los ejes y usan ejes.c2p) ---
puntos_datos(ejes, X, y, color_a=C_DATO_A, color_b=C_DATO_B, radio=0.055)
    # -> VGroup de Dots
frontera_imagen(ejes, modelo, color_a=C_DATO_A, color_b=C_DATO_B,
                res=(200, 200), opacidad=0.5)
    # -> ImageMobject del mapa de probabilidad, posicionado y escalado
    #    exactamente sobre el area de `ejes` (mezcla cada color con el fondo
    #    CODE_BG segun la probabilidad; z_index bajo para quedar bajo los
    #    puntos). Patron de colocacion: como fractales.imagen_mandelbrot.
recta_modelo(ejes, m, b, color=C_ACENTO, grosor=3.5)
    # -> Line recortada al rango x de los ejes
curva_perdida(ejes, perdidas, color=C_PERDIDA, grosor=3.0)
    # -> VMobject por esquinas, x = epoca normalizada al rango del eje,
    #    y = perdida normalizada al y_max de los ejes
camino_descenso(ejes, f, xs, color=C_ACENTO, radio=0.09)
    # -> (bola: Dot en xs[0], saltos: VGroup de arcos/segmentos entre
    #    (x_k, f(x_k)) consecutivos, para animar con Create + MoveAlongPath
    #    o hop a hop)
retropropagacion(red, color=C_PERDIDA, ancho=4.5, cola=0.5)
    # -> Succession como RedNeuronal.activacion pero recorriendo las
    #    conexiones DE SALIDA A ENTRADA (lineas invertidas)
```

Demo obligatoria: `studio/content/animations/experimentacion/13-aprendizaje.py`
con una escena corta que ejercite dataset + frontera + curva de perdida.

## Reglas duras para los clips (anti-encimamiento y estilo)

1. El clip define **solo** `class ClipN(Scene)`, sin imports: todo lo demas
   vive en el style_block (que ya importa `aprendizaje`, `neuronal`, etc.).
2. Todo texto narrativo entra por `rot = Rotulos(self)`:
   `rot.mostrar(pie_curso("..."), zona="abajo")` /
   `rot.mostrar(titulo_curso("..."), zona="arriba")`. `formula_pie` comparte
   la zona "abajo" con `pie_curso` — jamas simultaneos.
3. Mobiliario de figura (`tag_eje`, `llave`) se retira (`FadeOut`) antes de
   introducir el siguiente elemento en la misma region.
4. Un solo fenomeno protagonista por clip; 28-45 s; `self.wait(1.5)`+ final.
5. Semillas fijas; nada de `random` sin semilla; `clear_updaters()` si se
   usan updaters.
6. `MathTex` siempre con raw string y formulas CORTAS (una linea).
7. Colores solo de la paleta del curso; prohibidos GOLD/BLUE_B/TEAL_B/YELLOW.
8. Los comentarios del script marcan los momentos visuales (los lee Gemini
   para escribir la narracion): un comentario `# --- momento ---` por beat.

## Storyboard clip a clip

### Clip 1 — `1 · ¿Puede una máquina aprender?` (escena `Clip1`, ~35 s)
Portada: `titulo_marca("Redes neuronales", font_size=46)` + subtitulo ambar
"la máquina que aprende" (font_size=25), centrados, como el Clip1 de
Señales. HUD `Modulo 01`. Sale la portada, entra titulo arriba.
`ejes_plano()` centrado; `datos_dos_nubes` con `puntos_datos` (FadeIn con
lag_ratio). Pie: «¿Cómo distinguirías estos dos grupos?». Entra una
`recta_modelo` claramente mal colocada; en tres `Transform` sucesivos se
ajusta hasta separar las nubes (usar 3 pares (m,b) fijos elegidos a mano,
del malo al bueno). Pie: «Una máquina aprende así: se equivoca y se
corrige.» Destello final sobre la recta (`destello`). Pie gancho: «Ocho
pasos para entender cómo lo hace.»
**final_state**: ejes de plano centrados con las dos nubes y la recta
separadora ambar en su posicion final; titulo arriba, HUD Modulo 01.

### Clip 2 — `2 · El error como brújula` (escena `Clip2`, ~38 s)
Titulo «El error como brújula». `ejes_curva` con la parabola de perdida
`f(x) = 0.55 x^2` (color `C_TENUE`, grosor 3). Tag de eje: «error» (arriba
del eje y) y «parámetro» (derecha del eje x). `descenso_1d(df, x0=1.8,
lr=0.3, pasos=8)` → `camino_descenso`: la bola ambar baja salto a salto
(cada salto con una mini-tangente que aparece y se desvanece). Pie: «El
error es un paisaje: aprender es bajar la cuesta.» → formula_pie
`x_{k+1} = x_k - \eta \, f'(x_k)` (relevo, no suma). Segundo acto: bola
nueva con `lr=1.06` desde x0=1.6 — los saltos crecen y divergen; la bola y
su camino en rojo (`C_PERDIDA`); pie: «Con pasos demasiado grandes, el
aprendizaje explota.» La bola divergente sale del eje y se desvanece. Pie
cierre: «Elegir el tamaño del paso es un arte: se llama tasa de
aprendizaje.»
**final_state**: parabola con la trayectoria convergente ambar dibujada
(bola en el minimo); la divergente ya retirada.

### Clip 3 — `3 · La recta que aprende` (escena `Clip3`, ~38 s)
Titulo «La recta que aprende». `ejes_plano(lado=4.4)` desplazado 1.7 a la
IZQUIERDA; `datos_recta` como puntos cian. Recta inicial mala (m=-0.4,
b=-0.9) ambar. Segmentos de error verticales rojos (opacidad 0.6) de cada
punto a la recta: crecen con `Create` escalonado. Pie: «El error total: la
suma de todas esas distancias.» A la DERECHA, mini `ejes_curva` (x_length
3.2, centrado en (4.2, -1.2)) con tag «error». Se anima
`entrenar_regresion`: la recta interpola por los (m,b) del historial
(UpdateFromAlphaFunc o Transform por instantaneas: 6 pasos bastan) mientras
`curva_perdida` se dibuja en el mini eje y los segmentos de error encogen.
Pie: «Cada paso: medir el error, corregir la recta.» → formula_pie
`\text{MSE} = \tfrac{1}{n}\sum (y_i - \hat y_i)^2`. Cierre: segmentos ya
minimos, destello sobre la recta; pie: «Esto es regresión: la forma más
simple de aprender.»
**final_state**: recta ajustada sobre los puntos a la izquierda; mini-ejes
con la curva de perdida completa a la derecha (abajo).

### Clip 4 — `4 · La neurona` (escena `Clip4`, ~36 s)
Titulo «La neurona». Esquema centrado arriba (y=+0.9): dos entradas
(MathTex `x_1`, `x_2` en cian) → aristas con pesos (`w_1`, `w_2` en ambar,
etiquetas pequeñas sobre las lineas) → circulo suma `Σ` → caja sigmoide
(curva sigmoide en miniatura dentro de un `bloque`) → salida `ŷ`. Construir
con `Line`/`Circle`/`bloque`; pulso `flujo`/`destello` de entrada a salida.
Pie: «Pesa cada prueba, suma, y decide.» Abajo (y=-1.6) `ejes_plano
(lado=3.6)` con `datos_dos_nubes` y la recta frontera que esa neurona
dibuja (`recta_modelo`). Pie: «Toda neurona traza una única línea recta.»
→ formula_pie `\hat y = \sigma(w_1 x_1 + w_2 x_2 + b)`. Cierre con pie:
«¿Y si una recta no basta?» (siembra el clip 5).
**final_state**: esquema de neurona arriba, plano con nubes y recta abajo.

### Clip 5 — `5 · XOR: el muro` (escena `Clip5`, ~34 s)
Titulo «XOR: el problema imposible». `ejes_plano()` centrado con
`datos_xor` (racimos alternos cian/violeta). Una `recta_modelo` intenta
separar: 3 posiciones sucesivas (Transform); tras cada intento, los puntos
mal clasificados pulsan en rojo (`Indicate` con `C_PERDIDA`) y un contador
HUD pequeño (etiqueta_hud «errores: N», esquina UR) se actualiza (relevo,
no acumulacion). Pie: «Ninguna recta puede separar esto.» → «En 1969 este
problema congeló la investigación en redes por una década.» La recta
fallida se desvanece derrotada (FadeOut hacia abajo). Pie cierre: «Hacía
falta una idea nueva: apilar neuronas.»
**final_state**: datos XOR en el plano, sin recta; contador de errores ya
retirado.

### Clip 6 — `6 · Capas ocultas: doblar el espacio` (escena `Clip6`, ~40 s)
Titulo «Capas ocultas: doblar el espacio». A la izquierda (x=-3.6)
`RedNeuronal(capas=(2, 4, 1))` (colores: neuronas cian, conexiones grises);
`Create` + `activacion(color=C_DATO_A)`. Pie: «Dos entradas, cuatro
neuronas ocultas, una salida.» A la derecha (x=+2.6) `ejes_plano(lado=4.2)`
con `datos_xor`. `entrenar_mlp(X, y, ocultas=4)`: aparecen 3
`frontera_imagen` sucesivas (modelo inicial → intermedio → final) con
FadeTransform: la region ambar/violeta se curva hasta encerrar los racimos.
Cada transicion acompañada de `activacion` en la red. Pie: «La red dobla el
espacio hasta que una recta basta.» → «El muro de XOR, derribado.»
**final_state**: red 2-4-1 a la izquierda; plano XOR con la frontera final
curvada a la derecha.

### Clip 7 — `7 · Backpropagation: el error viaja de vuelta` (escena `Clip7`, ~38 s)
Titulo «El error viaja de vuelta». `RedNeuronal(capas=(2, 4, 4, 1))`
centrada, ligeramente arriba (y=+0.35). `activacion(color=C_DATO_A)` hacia
adelante; a la salida aparece `MathTex` pequeño `error` en rojo junto a la
neurona final. Pie: «Hacia adelante: una predicción. Y una medida del
error.» Luego `retropropagacion(red, color=C_PERDIDA)`: destellos rojos
recorren las conexiones al reves. Pie: «Hacia atrás: el error reparte
culpas entre los pesos.» Tercer acto: 4-5 conexiones elegidas engordan y
2-3 adelgazan (animar `set_stroke(width=...)` con ambar las que engordan);
pie: «Cada peso se corrige un poco. Eso es aprender.» → formula_pie
`w \leftarrow w - \eta \, \frac{\partial E}{\partial w}`. Cierre:
`activacion` adelante otra vez, ahora mas "segura" (ancho mayor); pie:
«Repítelo un millón de veces: así se entrena una red.»
**final_state**: red 2-4-4-1 centrada con varias conexiones engrosadas en
ambar.

### Clip 8 — `8 · Aprender de memoria no es aprender` (escena `Clip8`, ~42 s)
Titulo «Aprender de memoria no es aprender». `ejes_plano()` centrado con
`datos_circulos` (anillo violeta, centro cian). Dos modelos de
`entrenar_mlp`: uno suave (`ocultas=3`) y uno sobreajustado (`ocultas=24`,
mas epocas, que memoriza el ruido). Primero aparece la `frontera_imagen`
suave; pie: «Un modelo sencillo captura la forma general.» FadeTransform a
la frontera retorcida; pie: «Uno enorme puede memorizar hasta el ruido.»
Entran 6 puntos de PRUEBA nuevos (contorno blanco): con la frontera
retorcida, 2-3 quedan del lado equivocado y pulsan en rojo; pie: «Y
fracasa justo con lo que nunca vio.» Vuelve la frontera suave; los puntos
de prueba pulsan en verde. Pie: «Generalizar, no memorizar: esa es la
meta.» Todo se desvanece → tarjeta de cierre centrada:
`titulo_marca("Redes neuronales", font_size=46)` + subtitulo ambar
"la máquina que aprende" + subrayado ambar con `con_brillo` (patron del
cierre de Señales). `self.wait(2)`.
**final_state**: tarjeta de cierre del curso centrada, pantalla limpia.

## Descripcion del proyecto (campo description)

Curso de divulgación en 8 clips que explica cómo aprende una red neuronal:
del error y el descenso de gradiente a la regresión, la neurona, el muro de
XOR, las capas ocultas, backpropagation y el sobreajuste. Estilo 3Blue1Brown
en español para estudiantes de ingeniería.
