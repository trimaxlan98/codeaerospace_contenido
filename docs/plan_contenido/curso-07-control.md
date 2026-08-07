# Curso 07 — Control: domar sistemas que se resisten

- **Proyecto**: name `Control: domar sistemas que se resisten`,
  quality `qh`.
- **Fuente**: Academy, Señales y sistemas L11 (Laplace y estabilidad en
  el plano s), L12 (segundo orden, motor DC), L13 (Bode, solo
  pincelada) + Sistemas APT L6 (PID, error de arrastre, windup) y L7
  (sintonizacion y metricas).
- **Slug**: `control-domar-sistemas-que-se-resisten`.
- **Publico**: divulgacion; profundiza lo que el curso 05 (Apuntado)
  solo insinuo en su clip 7.
- **Hilo narrativo**: los sistemas responden tarde y a su manera → el
  plano s como mapa del destino → segundo orden (ζ, ωn) → cerrar el
  lazo → PID con analogos fisicos → la rampa y el error de arrastre →
  saturacion y windup → sintonizar y cierre.
- **Numeros ancla (de la Academy, usar tal cual)**: montura J=2 kg m²,
  b=0.5; kp=10 → ζ=0.056, sobreimpulso 84%, establecimiento 32 s;
  kd=5.76 → ζ=0.7, sobreimpulso 4.6%, establecimiento 2.6 s;
  e_ss = v·b/kp (rampa 5°/s → 0.25° de rezago con kp=10).

## Paleta del curso

| Constante | Valor | Rol |
|-----------|-------|-----|
| `C_REF` | `#f59e0b` ambar | la referencia, lo que se ordena |
| `C_SIS` | `#22d3ee` cian | el sistema/planta y su respuesta |
| `C_CTRL` | `#a78bfa` violeta | el controlador y sus señales |
| `C_MAL` | `#f43f5e` rojo | inestabilidad, error, saturacion |
| `C_OK` | `#34d399` verde | estable, amortiguado, meta |
| `C_EJE` | `#31414f` | mobiliario |

Regla: la REFERENCIA es ambar, el SISTEMA cian, el CONTROLADOR
violeta, lo INESTABLE rojo, lo LOGRADO verde.

## Contrato de la libreria `studio/content/manim_extensions/control.py`

Determinista, sin red, sin archivos. Estilo radio.py/apuntado.py
(subclases VGroup, localizadores sobre geometria actual). Topes:
`MUESTRAS_MAX = 400`, `POLOS_MAX = 8`.

```python
masa_resorte(ancho=2.8, color_masa="#22d3ee", color_resorte="#a78bfa",
             color_amortiguador="#a78bfa")
    # -> MasaResorte(VGroup): pared izquierda + resorte en zigzag +
    #    amortiguador (cilindro/piston) en paralelo + caja "m". Metodo
    #    .estirar(dx) que desplaza la masa y deforma resorte y
    #    amortiguador (redibuja internamente). Atributos .masa,
    #    .resorte, .amortiguador, .x (desplazamiento actual).
plano_s(ancho=4.6, alto=3.2, color="#31414f", font_size=15)
    # -> PlanoS(VGroup): ejes Re/Im con el semiplano izquierdo
    #    sombreado verde translucido y el derecho rojo translucido
    #    (opacity 0.10), etiquetas HUD "estable"/"inestable" chicas en
    #    la parte alta de cada semiplano. Metodo .punto(re, im) ->
    #    np.array (unidades: 1 = un cuarto del semiancho). Atributos
    #    .zona_estable, .zona_inestable.
polo(plano, re, im, color="#22d3ee")
    # -> VGroup marca "x" en plano.punto(re, im); atributos .re/.im.
respuesta_escalon(zeta=0.056, wn=2.24, ancho=4.8, alto=2.3,
                  color="#22d3ee", color_ref="#f59e0b", t_max=10.0)
    # -> Respuesta(VGroup): ejes minimos + linea punteada ambar en el
    #    valor final (la referencia escalon) + curva de respuesta de
    #    2o orden con ese zeta/wn (subamortiguada oscila, zeta>=1 sube
    #    suave). Metodo .punto_en(t_rel) sobre la curva. Atributos
    #    .curva, .linea_ref, .ejes.
lazo_cerrado(ancho=6.4, font_size=16)
    # -> LazoCerrado(VGroup): diagrama de bloques r -> (+/-) ->
    #    [CONTROL] -> [PLANTA] -> y, con rama de realimentacion por
    #    debajo volviendo al sumador (flecha con signo "-"). Bloques
    #    con los colores de paleta (CONTROL violeta, PLANTA cian).
    #    Atributos .sumador, .control, .planta, .flechas (VGroup),
    #    .rama_retro; metodo .camino() -> lista de VMobjects en orden
    #    (para flujo/destello).
rampa_con_rezago(ancho=5.4, alto=2.4, rezago=0.14, muestras=120,
                 color_ref="#f59e0b", color_sis="#22d3ee")
    # -> Rampa(VGroup): referencia rampa + respuesta desplazada
    #    `rezago` constante (paralela, nunca converge). Con rezago=0
    #    coinciden. Metodo .brecha_en(t_rel) -> (p_ref, p_sis).
curva_windup(ancho=5.4, alto=2.4, con_antiwindup=False,
             color="#22d3ee", color_ref="#f59e0b", color_mal="#f43f5e")
    # -> Windup(VGroup): referencia escalon + respuesta que, sin
    #    anti-windup, se pasa MUCHO de largo y tarda en volver
    #    (sobreimpulso grande tardio, tramo del exceso en rojo); con
    #    con_antiwindup=True llega limpia. Mismos ejes/escala en ambos
    #    modos (para ReplacementTransform). Atributos .curva, .exceso
    #    (VMobject del tramo rojo; vacio si antiwindup), .linea_ref.
barras_metricas(valores, etiquetas=("RMS", "SOBREIMPULSO", "T. EST."),
                ancho=3.6, alto=1.9, color="#22d3ee")
    # -> VGroup: 3 barras verticales con etiquetas HUD debajo
    #    (valores en [0,1]). Para comparar sintonizaciones. .barras
```

Demo obligatoria:
`studio/content/animations/experimentacion/19-control.py` con
`DemoControl(Scene)` (~15 s): masa_resorte estirandose y soltandose,
plano_s con un polo cruzando al semiplano derecho, respuesta_escalon
zeta 0.056 vs 0.7 (transform), lazo_cerrado con flujo, rampa_con_rezago
0.14→0, curva_windup sin y con anti-windup, barras_metricas.

## Reglas duras para los clips

Identicas a los cursos previos: solo `class ClipN(Scene)`; Rotulos;
28-45 s tope INVIOLABLE; pies >= 5 s; determinismo; solo paleta;
`# --- momento ---`; final_state literal; el pie cambia ANTES del
transform que ilustra.

## Storyboard clip a clip

### Clip 1 — `1 · Sistemas que se resisten` (~35 s, `Clip1`)
Portada `titulo_marca("Control", 46)` + subtitulo ambar «domar sistemas
que se resisten». Titulo «Sistemas que se resisten». `masa_resorte`
centrada (y≈-0.2): se estira (animar .estirar) y al soltarse OSCILA
largo (secuencia de .estirar decrecientes alternados). Pie: «Ordenas
"muévete un metro"... y el mundo responde tarde, se pasa y rebota.»
Pie: «Una antena, un dron, un brazo robótico: todos son este resorte.»
Pie gancho: «Controlar es domar esta respuesta.»
**final_state**: masa-resorte en reposo centrada.

### Clip 2 — `2 · El plano s: el mapa del destino` (~36 s, `Clip2`)
Titulo «El plano s: el mapa del destino». `plano_s` a la izquierda
(x≈-2.9). Pie: «Cada sistema esconde sus polos: puntos en este mapa
que dictan su destino.» `polo` verde en (-1.2, ±0.9) (dos marcas);
derecha (x≈+2.9, y≈-0.1) `respuesta_escalon(zeta=0.7)` chica. Pie:
«Polos a la izquierda: la respuesta se calma. Estable.» Acto 2: los
polos se MUEVEN hacia el eje (animar move_to a re=-0.1): la respuesta
se transforma en zeta=0.08 (oscilona). Pie: «Cerca del borde: oscila
sin ganas de parar.» Acto 3: un polo cruza al semiplano derecho
(re=+0.5) y pulsa rojo; la respuesta se transforma en una que crece
(usar respuesta_escalon con zeta... para inestable el agente dibuja
una curva creciente con FunctionGraph exponencial roja del mismo
tamaño). Pie: «Del lado derecho, el sistema explota. Inestable.» Pie
cierre: «Controlar es mover los polos al lugar correcto.»
**final_state**: plano s con un polo rojo a la derecha, respuesta
creciente roja al lado.

### Clip 3 — `3 · Zeta: el caracter del sistema` (~36 s, `Clip3`)
Titulo «ζ: el carácter del sistema». `respuesta_escalon(zeta=0.056)`
centrada (y≈-0.1) con su linea de referencia. Pie: «Un solo número
resume el temperamento: el amortiguamiento.»
`formula_pie("\\zeta = 0.056")` → pie: «Casi cero: 84% de sobreimpulso
y medio minuto de bamboleo.» Transform a zeta=0.7 (pie ANTES): «En
0.7, el clásico compromiso: rápido y casi sin pasarse.»
`formula_pie("\\zeta = 0.7")`. Transform a zeta=1.6: pie: «Demasiado
amortiguado: seguro... pero lento como un trámite.» Pie cierre: «El
arte está en elegir cuánto freno.» **final_state**: respuesta
sobreamortiguada (zeta 1.6) con su referencia.

### Clip 4 — `4 · Cerrar el lazo` (~36 s, `Clip4`)
Titulo «Cerrar el lazo». `lazo_cerrado` centrado (y≈+0.2) construido
por partes: primero r→CONTROL→PLANTA→y (lazo abierto). Pie: «A ciegas:
ordenas y rezas. Cualquier viento arruina el plan.» Acto 2: la rama de
realimentacion se dibuja (Create) y el sumador marca "-". Pie: «Cerrar
el lazo: medir lo que pasó, restarlo de lo pedido...» `flujo` por
.camino() completo, 2 vueltas. Pie: «...y corregir con el error. Cien
veces por segundo.» Acto 3: `etiqueta_hud("e = r - y")` bajo el
diagrama (y≈-1.5). Pie cierre: «Ese pequeño resto, el error, es la
señal más importante del sistema.»
**final_state**: lazo cerrado completo con la etiqueta e = r - y.

### Clip 5 — `5 · PID: resorte, amortiguador, memoria` (~38 s, `Clip5`)
Titulo «PID: resorte, amortiguador y memoria». Izquierda (x≈-3.1,
y≈-0.1) `masa_resorte` chica; derecha (x≈+2.7, y≈-0.1)
`respuesta_escalon(zeta=0.056)`. Pie: «P es un resorte: tira más
fuerte cuanto más lejos estás.» (el resorte pulsa violeta). Pie: «Pero
un resorte solo... oscila.» (la respuesta oscilante pulsa). Acto 2: el
amortiguador pulsa violeta; la respuesta se transforma (pie ANTES) en
zeta=0.7: «D es el amortiguador: frena antes de llegar. El bamboleo
muere.» Acto 3: `formula_pie("u = k_p e + k_i \\int e + k_d \\dot{e}")`.
Pie: «I es la memoria: acumula lo que falta hasta borrarlo del todo.»
Pie cierre: «Tres perillas. Con eso se apunta una antena de media
tonelada.» **final_state**: masa-resorte a la izquierda, respuesta
amortiguada a la derecha, formula PID en el pie.

### Clip 6 — `6 · La rampa que nunca alcanzas` (~36 s, `Clip6`)
Titulo «La rampa que nunca alcanzas». `rampa_con_rezago(rezago=0.14)`
centrada (y≈-0.1): referencia ambar y respuesta cian paralela. Pie:
«Un pase de satélite no es un escalón: la orden nunca deja de
moverse.» Flecha roja corta en .brecha_en(0.6) con tag «rezago». Pie:
«Con P puro, el sistema persigue... a distancia constante. Jamás
alcanza.» `formula_pie("e_{ss} = v\\,b\\,/\\,k_p")`. Pie: «Cinco
grados por segundo de rampa: un cuarto de grado de retraso. Fuera de
presupuesto.» Acto 2: (pie ANTES) «La memoria integral acumula ese
error... y lo funde a cero.»; transform a rezago=0.0, la curva cian
termina verde. Pie cierre: «Tipo 2: el perseguidor que sí alcanza.»
**final_state**: rampa con las dos curvas superpuestas (la del sistema
verde).

### Clip 7 — `7 · Windup: la memoria que se emborracha` (~36 s, `Clip7`)
Titulo «Windup: la memoria que se emborracha». `curva_windup` centrada
(y≈-0.1). Pie: «Ningún motor da par infinito: cuando el mando satura,
la antena ya no acelera más.» El tramo rojo `.exceso` se dibuja/pulsa.
Pie: «Pero el integrador sigue acumulando... y al llegar, trae un
sobregiro enorme y tardío.» Acto 2: (pie ANTES) «El remedio son tres
líneas de código: congelar la memoria mientras el actuador esté al
tope.»; ReplacementTransform a `curva_windup(con_antiwindup=True)`.
Pie: «Anti-windup: llega limpio.» `etiqueta_hud("CLAMPING")` junto a
la curva. Pie cierre: «La diferencia entre reenganchar el satélite o
perderlo.» **final_state**: curva con anti-windup limpia con su
etiqueta CLAMPING.

### Clip 8 — `8 · Sintonizar: el arte` (~40 s, `Clip8`)
Titulo «Sintonizar: el arte». Izquierda (x≈-2.9, y≈-0.1)
`respuesta_escalon(zeta=0.056)`; derecha (x≈+3.0, y≈-0.1)
`barras_metricas([0.9, 0.85, 0.95])`. Pie: «Primero P: rápido hasta
que oscile.» Transform respuesta→zeta=0.35 y barras→[0.5,0.5,0.5]
(pie ANTES): «Luego D: amortigua hasta que el motor deje de zumbar.»
Transform final respuesta→zeta=0.7 (curva verde) y
barras→[0.15,0.1,0.12]: «Al final I, apenas: borra el resto sin
despertar al windup.» Pie: «Tres métricas mandan: error RMS,
sobreimpulso, tiempo de establecimiento.» Acto final: todo se
desvanece → tarjeta de cierre `titulo_marca("Control", 46)` +
subtitulo ambar «domar sistemas que se resisten» + subrayado
`con_brillo`. `self.wait(2)`.
**final_state**: tarjeta de cierre centrada, pantalla limpia salvo
esquinas HUD y marca de agua.

## Descripcion del proyecto (campo description)

Curso de divulgación en 8 clips sobre control de sistemas: la
respuesta que oscila, el plano s y sus polos, el amortiguamiento ζ, el
lazo cerrado y el error, el PID con sus análogos físicos (resorte,
amortiguador, memoria), el error de arrastre ante rampas, la
saturación con su windup y el arte de sintonizar. Estilo 3Blue1Brown
en español.
