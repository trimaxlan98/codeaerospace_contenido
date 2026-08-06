# Curso 02 — De la palabra al vector: embeddings y atencion

- **Proyecto**: name `De la palabra al vector: embeddings y atención`,
  quality `qh`.
- **Fuente**: Academy, curso Inteligencia Artificial, lecciones 8-9 (NLP y
  embeddings; transformers y LLMs), con el arranque de la 10 (generacion).
- **Slug**: `de-la-palabra-al-vector-embeddings-y-ate`.
- **Publico**: divulgacion estilo 3Blue1Brown en español; sin prerequisitos
  mas alla de "vector = flecha/punto".
- **Hilo narrativo**: tokens → mapa del significado → similitud coseno →
  el problema del contexto → atencion → Q/K/V → apilar capas (Transformer)
  → predecir la siguiente palabra (LLM).

## Paleta del curso (se suma a la marca CO.DE)

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_TOKEN` | `#22d3ee` cian | tokens, texto crudo |
| `C_VECTOR` | `#a78bfa` violeta | vectores/embeddings, significado |
| `C_ACENTO` | `#f59e0b` ambar | el MECANISMO: atencion, pesos, flechas Q/K/V |
| `C_PROB` | `#34d399` verde | probabilidades, la palabra elegida |
| `C_MAL` | `#f43f5e` rojo | ambiguedad, el embedding que falla |
| `C_EJE` | `#31414f` | ejes y mobiliario |

Regla de color: el TEXTO es cian, el SIGNIFICADO violeta, el MECANISMO
ambar, la PROBABILIDAD verde, el FALLO rojo. No mezclar roles.

## Contrato de la libreria `studio/content/manim_extensions/atencion.py`

Determinista (posiciones y pesos calculados de embeddings 2D FIJOS a mano,
no entrenados), sin red, sin archivos. numpy para el calculo. Topes:
`TOKENS_MAX = 12`, `PALABRAS_MAX = 24`.

```python
# --- vocabulario de demo: embeddings 2D fijos, en [-2, 2]^2 -----------
EMBEDDINGS: dict[str, tuple[float, float]]
    # al menos: gato, perro, felino, pez, rey, reina, hombre, mujer,
    # banco, dinero, parque, sol, luna, comer, dormir
    # agrupados con sentido (animales juntos, realeza junta, etc.)

# --- tokens (mobjects) ------------------------------------------------
ficha_token(texto, color=C_TOKEN, font_size=24, ancho_min=0.72)
    # -> VGroup(caja redondeada, Text) tamano compacto
fila_tokens(frase, color=C_TOKEN, font_size=24, buff=0.18, ancho_max=11.5)
    # -> VGroup de fichas (una por palabra de `frase`), arranged RIGHT,
    #    auto-escala si excede ancho_max. Atributo .fichas (lista).

# --- mapa semantico ---------------------------------------------------
mapa_embeddings(ejes, palabras, colores=None, font_size=17,
                direcciones=None)
    # -> VGroup de (Dot + etiqueta) por palabra, usando EMBEDDINGS y
    #    ejes.c2p. `direcciones` opcional {palabra: direccion next_to}
    #    para separar etiquetas; defecto UR. Atributo .puntos {palabra: Dot}.
flecha_vector(ejes, desde, hasta, color=C_VECTOR, grosor=5.0)
    # -> Arrow de ejes.c2p(*desde) a ejes.c2p(*hasta); desde/hasta pueden
    #    ser tuplas (x, y) o nombres de palabra (usa EMBEDDINGS)
arco_similitud(ejes, palabra_a, palabra_b, color=C_ACENTO, radio=0.55)
    # -> Angle entre los vectores origen->a y origen->b
similitud_coseno(a, b) -> float
    # a, b: nombres de palabra o tuplas

# --- atencion ---------------------------------------------------------
pesos_atencion(frase, idx_query, temperatura=1.0)
    # -> np.ndarray softmax(puntos_query . puntos_k / temperatura) sobre
    #    las palabras de `frase` (usa EMBEDDINGS; palabra fuera del
    #    vocabulario -> (0, 0)). Suma 1.
abanico_atencion(fila, idx_query, pesos, color=C_ACENTO, altura=1.1)
    # -> VGroup de arcos desde la ficha idx_query de `fila` (VGroup de
    #    fichas) hacia cada otra ficha, por ARRIBA de la fila,
    #    stroke_width = 1.0 + 7.0 * peso, stroke_opacity = 0.35 + 0.65 * peso
barras_pesos(pesos, etiquetas, origen=ORIGIN, ancho=0.5, alto_max=1.5,
             color=C_ACENTO, font_size=16)
    # -> VGroup de barras verticales (una por peso) con su etiqueta debajo,
    #    centrado en `origen`
mezcla_ponderada(frase, idx_query, pesos)
    # -> tupla (x, y): suma ponderada de los EMBEDDINGS de la frase (el
    #    "nuevo vector" de la query tras atender)

# --- transformer y generacion -----------------------------------------
bloque_transformer(etiqueta="ATENCION + MLP", ancho=3.4, alto=1.0,
                   color=C_ACENTO)
    # -> VGroup caja estilo bloques.py con la etiqueta HUD dentro
distribucion_siguiente(opciones, probs, ancho_max=4.6, color=C_PROB,
                       font_size=19, resaltar=None)
    # -> VGroup de barras HORIZONTALES (palabra + barra + porcentaje),
    #    ordenadas por prob desc; `resaltar` pinta esa opcion en C_PROB y
    #    el resto en C_TENUE-ish
```

Demo obligatoria: `studio/content/animations/experimentacion/14-atencion.py`
con `DemoAtencion(Scene)` (~15 s): fila_tokens + abanico_atencion con
pesos_atencion reales + mapa_embeddings pequeño + distribucion_siguiente.

## Reglas duras para los clips

Identicas al curso 01 (ver `curso-01-redes-neuronales.md`): solo
`class ClipN(Scene)` sin imports; todo texto narrativo via `Rotulos`
(zonas arriba/abajo, pie y formula se relevan); mobiliario se retira antes
del siguiente; un fenomeno por clip; 28-45 s; semillas/valores fijos;
`MathTex` raw y corto; solo colores de la paleta; comentarios
`# --- momento ---` por beat. El style_block del curso ya importa TODO el
contrato de arriba.

## Storyboard clip a clip

### Clip 1 — `1 · ¿Cómo lee una máquina?` (escena `Clip1`, ~34 s)
Portada: `titulo_marca("De la palabra al vector", font_size=46)` +
subtitulo ambar "embeddings y atención" (25). HUD `Modulo 01`. Sale
portada, titulo arriba «¿Cómo lee una máquina?». Aparece un `Text` frase
«el gato duerme en el parque» (cian, centro, font_size=30) →
`Transform` a `fila_tokens` de la misma frase (las fichas). Pie: «Primero,
partir el texto en piezas: tokens.» Debajo de cada ficha aparece un numero
arbitrario (Text pequeño C_TENUE: 4821, 93, 1177...). Pie: «Para la
máquina, cada token es solo un número.» Los numeros de 'gato' y un token
extra 'felino' (ficha que entra a la derecha) pulsan en rojo: numeros
totalmente distintos. Pie: «El problema: 'gato' y 'felino' no se parecen
en nada.» Cierre/gancho: los numeros se desvanecen; pie: «Necesitamos que
el significado viva en los números.»
**final_state**: fila de fichas cian centrada (frase + felino), sin
numeros; titulo y HUD puestos.

### Clip 2 — `2 · El mapa del significado` (escena `Clip2`, ~38 s)
Titulo «El mapa del significado». `ejes_plano()` centrado.
`mapa_embeddings` con: gato, perro, felino, pez (zona animales), rey,
reina, hombre, mujer (zona realeza/personas), sol, luna (zona cielo) —
entra por grupos con FadeIn lag. Pie: «Cada palabra, un punto: cerca =
parecido.» Pulso (`Indicate` violeta) sobre gato-perro-felino juntos.
Pie: «'Gato' y 'felino', vecinos al fin.» Acto 2: flechas
`flecha_vector` origen→rey (violeta) y origen→hombre (tenue); la resta
rey-hombre+mujer se muestra como flecha ambar desde 'mujer' con la misma
direccion que hombre→rey, cuya punta cae junto a 'reina'; `punto_brillante`
en reina. formula_pie `\vec{rey} - \vec{hombre} + \vec{mujer} \approx \vec{reina}`.
Pie cierre: «La geometría captura el significado.»
**final_state**: mapa con ~10 palabras y la flecha ambar hacia 'reina'
aun visible.

### Clip 3 — `3 · Medir parecidos: el coseno` (escena `Clip3`, ~34 s)
Titulo «Medir parecidos: el coseno». Plano a la IZQUIERDA (x≈-2.6,
lado 4.4) con solo: gato, felino, luna. Flechas desde el origen a gato y
felino (violeta) y a luna (tenue). `arco_similitud` gato-felino (ambar,
angulo pequeño). Pie: «Angulo pequeño: significados cercanos.» A la
DERECHA (x≈+3.5) `barras_pesos`-estilo o MathTex: formula_pie NO (es zona
pie) — usar MathTex compacto en el lado derecho como parte de la figura:
`\cos(\theta)` con los valores: cos(gato,felino)=0.98 (verde),
cos(gato,luna)=0.12 (rojo) — dos lineas MathTex apiladas con buff 0.4,
cada una junto a un mini-icono de flechas. Relevo de arco: ahora
gato-luna (angulo grande). Pie: «Angulo grande: nada que ver.» Cierre:
pie «Un número entre -1 y 1: la similitud coseno.»
**final_state**: plano con las tres flechas y el arco gato-luna; valores
cos a la derecha.

### Clip 4 — `4 · El problema del contexto` (escena `Clip4`, ~34 s)
Titulo «El problema del contexto». Arriba (y≈+1.35) `fila_tokens`
«me siento en el banco» ; abajo (y≈-0.15) otra fila «el banco cobra
comisiones» (ambas auto-escaladas). La ficha 'banco' de ambas pulsa
(Indicate cian). Pie: «La misma palabra... ¿el mismo significado?» Un Dot
violeta con etiqueta 'banco' aparece entre ambas filas (posicion fija,
representando SU UNICO punto en el mapa) con un `?` ambar encima; el
punto tiembla (wiggle) y se tiñe de rojo. Pie: «Un solo punto no puede
ser dos cosas a la vez.» Las palabras vecinas de cada frase ('siento' /
'comisiones') destellan en verde sucesivamente. Pie: «La pista esta en
las palabras de alrededor.» Cierre: pie gancho «Hace falta que cada
palabra MIRE a las demás.»
**final_state**: dos filas de tokens con el punto rojo 'banco' entre
ambas; sin flechas todavia.

### Clip 5 — `5 · Atención: mirar todo a la vez` (escena `Clip5`, ~38 s)
Titulo «Atención: mirar todo a la vez». Una sola `fila_tokens`
«el banco cobra comisiones al cliente» centrada (y≈-0.6).
`pesos_atencion(frase, idx de 'banco')` → `abanico_atencion` desde
'banco': arcos ambar por encima, grosor = peso. Pie: «Cada palabra
pregunta: ¿quién me importa aquí?» Los pesos como `barras_pesos`
compactas ARRIBA de la fila... no: el abanico ya ocupa arriba — las
barras van ABAJO de la fila (y≈-2.0), etiquetadas por palabra,
auto-compactas. Pie: «'Cobra' y 'comisiones' pesan más: banco de dinero.»
Acto 2: el Dot violeta 'banco' (a un lado, x≈+4.9, y≈+1.3... NO: mejor
centro-derecha limpio) — simplificar: la ficha 'banco' se tiñe de
violeta y de ella sale `flecha` corta hacia una nueva ficha violeta
'banco (dinero)' que aparece ARRIBA de la fila (y≈+1.5), construida como
mezcla: destellos desde las fichas con mas peso convergen en ella
(usar `flujo`/`destello` sobre lineas temporales). Pie: «Su nuevo vector:
mezcla de lo que atendió.» Cierre: pie «Eso es la atención: contexto a
la medida.»
**final_state**: fila de tokens con abanico apagado, ficha violeta
'banco (dinero)' arriba; barras ya retiradas.

### Clip 6 — `6 · Q, K, V: preguntar, etiquetar, responder` (escena `Clip6`, ~36 s)
Titulo «Q, K, V: preguntar, etiquetar, responder». Tres `bloque` en
columna a la IZQUIERDA (x≈-4.3): `Q · consulta` (ambar), `K · llave`
(cian), `V · valor` (violeta), con buff 0.5. Pie: «Cada palabra emite
tres versiones de sí misma.» A la DERECHA (x≈+1.6) mini fila de 4 tokens
«el banco cobra comisiones» (escala 0.85, y≈+1.0). La Q de 'banco'
(flecha ambar) toca la K de cada token (destellos cian secuenciales).
Pie: «La consulta se compara con cada llave.» Debajo (y≈-1.1)
`barras_pesos` con los pesos reales. formula_pie
`\text{softmax}(Q \cdot K) \rightarrow \text{pesos}`. Acto final: las V
(violeta) fluyen (flujo) ponderadas hacia una ficha resultado. Pie: «Y
los valores se mezclan según esos pesos.»
**final_state**: bloques Q/K/V a la izquierda, fila con barras de pesos
y ficha resultado a la derecha.

### Clip 7 — `7 · Apilar capas: el Transformer` (escena `Clip7`, ~36 s)
Titulo «Apilar capas: el Transformer». Fila de 5 tokens abajo (y≈-2.2,
escala 0.85). Encima, DOS `bloque_transformer` apilados (y≈-0.6 y +0.7)
conectados con `conectar`; encima una ficha de salida (y≈+1.9). `flujo` /
`destello` sube por la pila. Pie: «Atención y mezcla, una capa tras
otra.» Con cada pasada (2 pasadas), las fichas de la fila cambian de
matiz cian→violeta (set_color gradual: el significado se refina). Pie:
«Cada capa refina lo que cada palabra significa.» Un contador HUD
pequeño (etiqueta_hud, esquina UR, relevo) «CAPAS: 2» → «CAPAS: 96».
Pie: «Un LLM apila decenas de estas capas.» Cierre: destello completo;
pie «Esto es un Transformer. Nada más... y nada menos.»
**final_state**: pila de 2 bloques transformer con fila de tokens abajo
y ficha de salida arriba; contador retirado.

### Clip 8 — `8 · Predecir la siguiente palabra` (escena `Clip8`, ~40 s)
Titulo «Predecir la siguiente palabra». Fila de tokens «el gato se
subió al» (y≈+0.9). A su derecha, hueco con `?` ambar.
`distribucion_siguiente(["tejado", "árbol", "sofá", "coche"],
[0.46, 0.31, 0.18, 0.05])` centrada abajo (y≈-1.2), resaltar='tejado'.
Pie: «El modelo no sabe: calcula probabilidades.» La opcion 'tejado' se
funde (Transform) en una ficha verde que ocupa el hueco. Pie: «Elige,
añade... y vuelve a empezar.» La fila (ahora mas larga) se desplaza a la
izquierda y aparece un nuevo `?`; nueva distribucion breve (2 opciones)
elige 'y'. Pie: «Así, palabra a palabra, escribe un LLM.» Todo se
desvanece → tarjeta de cierre: `titulo_marca("De la palabra al vector",
46)` + subtitulo ambar "embeddings y atención" + subrayado `Line` con
`con_brillo`. `self.wait(2)`.
**final_state**: tarjeta de cierre del curso centrada, pantalla limpia.

## Descripcion del proyecto (campo description)

Curso de divulgación en 8 clips sobre cómo entienden el lenguaje los
modelos de IA: de los tokens y los embeddings a la similitud coseno, el
problema del contexto, el mecanismo de atención, Q/K/V, el Transformer y
la generación palabra a palabra. Estilo 3Blue1Brown en español.
