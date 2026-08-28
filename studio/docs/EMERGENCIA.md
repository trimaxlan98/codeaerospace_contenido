# Emergencia: la librería donde el fotograma ES la simulación (2026-08-28)

`studio/content/manim_extensions/emergencia/` es un **paquete**, no un módulo
suelto: un núcleo (`__init__.py`) y trece simuladores, uno por archivo.

La diferencia con todas las librerías anteriores del repo cabe en una frase:
hasta ahora animábamos **objetos vectoriales sobre un fondo**; aquí el fondo
**es** el sistema. Un simulador produce una pila de fotogramas con numpy
(miles de agentes, mallas de cientos de miles de celdas) y el núcleo la
presenta a pantalla completa como un `ImageMobject` que cambia frame a frame.
Los mobjects de manim quedan para lo que de verdad son buenos: la cifra, el
HUD y algún trazo de énfasis **encima** del sistema.

Nació para el curso 29 (vertical 9:16), pero el núcleo no sabe nada de
formatos: sirve igual para 16:9.

---

## 1. Núcleo (`import emergencia as em`)

### `em.Pelicula(frames, alto=None, y=0.0, nearest=False, z=-500, opacidad=1.0)`

La pieza central. `frames` es una pila **uint8 (T, H, W, 3)**.

```python
peli = em.Pelicula(F, alto=config.frame_height)   # o pelicula(F) en el curso 29
self.add(peli.mob)                                # el ImageMobject
self.play(peli.animacion(6.0, desde=0, hasta=300))
```

- `animacion(run_time, desde, hasta, ritmo=None, encuadre=None, rate_func=None)`
  devuelve un `UpdateFromAlphaFunc` — se compone con cualquier otra animación
  en el mismo `self.play`.
- `mostrar(k)` planta un frame concreto (útil para el estado inicial).
- `nearest=True` para autómatas (píxel duro); bicúbico por defecto para campos.

**Dos cosas que el núcleo resuelve y que costaron un render cada una:**

- La pila se guarda en **RGB** y el canal alfa se pega al vuelo, porque
  `pixel_array` de manim exige RGBA (con RGB revienta con *"buffer is not
  large enough"*).
- `mostrar()` mantiene `orig_alpha_pixel_array` a la forma del frame
  mostrado. Sin eso, una pieza que **acabe con la cámara ampliada** revienta
  en el `FadeOut` final (`could not broadcast…`) y —lo peor— el contenedor se
  queda colgado a 0 % de CPU **sin escribir el mp4**.

### Cámara y ritmo

```python
em.seguir(posiciones_px, zoom, suavizado=15)   # encuadre que persigue a un agente
em.zoom_hacia(cx, cy, zoom_final, desde=1.0)   # zoom continuo a un punto (0-1)
em.ritmo_por_tramos([(0,0), (0.4,0.5), (0.7,0.55), (1,1)])  # cámara lenta
```

`encuadre(frac, W, H) -> (cx, cy, zoom)` recorta la pila **antes** de
reescalar, así que el zoom no cuesta resolución de simulación; `ritmo(alpha)
-> fracción` remapea el índice de frame (en el ejemplo, entre alpha 0.4 y 0.7
la película avanza sólo un 5 %: eso es la cámara lenta).

### Pintar sobre un lienzo de píxeles

```python
lienzo = np.zeros((H, W, 3), np.float32)
em.estela(lienzo, 0.88)                       # lo anterior se apaga
em.salpicar(lienzo, xy, em.C_VIVO, 0.9, 1.2)  # puntos con núcleo gaussiano
frame = em.a_uint8(lienzo)
em.colorear(campo, em.LUTS["vorticidad"], -1, 1)   # campo escalar -> RGB
```

`salpicar` es **aditivo y de un solo color**: donde se juntan muchos, brilla.
Dos consecuencias medidas: pintar 200 agentes con 200 llamadas cuesta más que
la física entera (píntalos por bandas de color), y con ~20 puntos por píxel
cada canal satura por su cuenta y el ámbar **se vuelve blanco** (acumula
densidad y colorea con una LUT).

### Paleta por ROL

`C_MEDIDO` cian (toda cifra calculada en este render) · `C_REGLA` ámbar (la
regla, el instrumento, el agente que sigue la cámara) · `C_ORDEN` violeta (lo
ordenado, el dominio) · `C_ENERGIA` naranja (energía, vorticidad, lo que
escapa) · `C_VIVO` verde · `C_MOBILIARIO` · `C_EXTERNO` gris (lo que **no**
calcula la librería). `em.LUTS` trae las rampas ya hechas.

### Otros

- `em.mosaico(pilas, columnas, W, H)` — varias simulaciones a la vez.
- `em.converger(objetivos, W, H, ...)` — un enjambre vuela y **se posa** sobre
  unos puntos (así nace el título de la intro del curso 29).
- `em.validar_pila(frames)` — aborta si no es uint8 (T,H,W,3) o si pasa de
  **1 GB**. Se llama solo desde `Pelicula`, pero un simulador debería
  llamarlo antes de devolver.

---

## 2. Los trece simuladores

Todos cumplen el mismo contrato, y **ninguno importa manim** (así la sonda
corre sin él):

```python
simular(..., semilla=1, pasos=P, res=(W, H)) -> dict(
    frames = uint8 (T, H, W, 3),
    cifras = {...},   # lo que el clip pone en pantalla, medido AQUÍ
    extra  = {...},   # trayectorias, instantes clave, series por frame
)
medir(...) -> dict    # sólo las cifras (sin pintar), para la sonda
```

| Módulo | Qué simula | Cifras que devuelve |
|---|---|---|
| `bandada` | 2500 boids con rejilla espacial O(n) | polarización inicial/final, frame del cruce de 0.8 |
| `moho` | Physarum: 60 000 agentes que dejan y siguen rastro | red geodésica / árbol mínimo, comidas conectadas |
| `arena` | pila abeliana, avalancha a avalancha | granos, avalancha mayor, exponente τ y su r² |
| `vida` | Life B3/S23 con el cañón de Gosper | periodo del cañón, planeadores emitidos y por minuto |
| `turing` | Gray-Scott, de manchas a laberinto | longitud de onda de cada fase (FFT), nº de manchas |
| `ondas` | onda 2D por diferencias finitas, doble rendija | separación de franjas medida / Fresnel / λL/d |
| `chladni` | 40 000 granos sobre una placa vibrando | fracción de arena en las líneas nodales por modo |
| `ising` | Metropolis en tablero de ajedrez, enfriando | \|M\| a T alta / en Tc / final, T del cruce de 0.5 |
| `pendulos` | 200 péndulos dobles (RK4) a 1e-6 de distancia | t hasta separarse 1 rad, λ de Lyapunov, deriva de E |
| `cuencas` | un péndulo magnético **por píxel** (230 400) | reparto por imán, dimensión de la frontera |
| `epiciclos` | DFT del contorno de «CO.DE» | error RMS por nº de círculos, N para 1 px |
| `rio` | lattice-Boltzmann D2Q9, calle de vórtices | Reynolds, Strouhal medido, vórtices desprendidos |
| `galaxias` | N cuerpos restringido, dos discos que chocan | deriva de energía, distancia mínima, % capturadas |

`extra` es lo que hace posible el énfasis vectorial: trayectorias en píxeles
(para `em.seguir` o para dibujar encima con `px_a_escena`), el **frame en que
pasa lo interesante** (para poner ahí la cámara lenta) y series por frame
(para contadores vivos y curvas).

### La sonda

```bash
docker run --rm --network none --user $(id -u):$(id -g) \
  -v <repo>:/workspace:ro codeaerospace_contenido-manim \
  python3 /workspace/studio/tools/sonda_emergencia.py [--frames] [--solo ising]
```

Comprueba invariantes físicos (conservación de energía, periodos conocidos,
rangos, que la cifra exista y sea finita), no que el código no reviente.
**Córrela antes de tocar un simulador.** Hoy: 36 ok, 0 fallos.

---

## 3. Cómo se usa desde un clip

Desde la app, la plantilla **«Pieza de simulación»** ya deja el bloque de
estilo y un clip que renderiza. A mano, el patrón es:

```python
r = em.bandada.simular(semilla=1, pasos=600)      # medir ANTES de dibujar
F, cifras, extra = r["frames"], r["cifras"], r["extra"]

peli = em.Pelicula(F, alto=config.frame_height)
self.add(peli.mob)
self.play(peli.animacion(8.0, desde=0, hasta=300))

# la cámara lenta va donde el simulador dice que pasa algo
k = extra["frame_umbral_0_8"] if "frame_umbral_0_8" in extra else 300
self.play(peli.animacion(3.0, desde=k-15, hasta=k+15))
```

Reglas que no se negocian, heredadas del formato:

1. **Toda cifra en pantalla sale de `cifras`/`extra` de ese render** (cian).
   Lo que venga de literatura va en gris y se declara.
2. Los contadores se pre-renderizan y se cambian con `become` **dentro** de
   un `UpdateFromAlphaFunc`; nunca `always_redraw` con `Text`.
3. La simulación se llama **una vez** al principio del `construct`.
4. Presupuesto: simular ≤ 90 s; el render en `qh` va a ~0.29 s/frame
   (una pieza de 35 s ≈ 10 min en esta máquina; en el VPS, mucho más: los
   `qh` de piezas con película conviene hacerlos **en local**).

### Contraste del texto sobre un fondo que se mueve

Cuando la simulación es clara (Gray-Scott, la mandala de arena, el Ising
ordenado) el HUD gris desaparece. El `style_block` del curso 29 resuelve esto
una sola vez con `velos_de_contraste()`: una banda oscura con degradado
detrás del HUD y del pie de cifra, a `z=-450` (encima de la película, debajo
de todo lo demás). Si copias ese bloque, cópialo con el velo; y si bajas su
opacidad, el clip 03 es el primero que lo acusa.

---

## 4. Dónde vive todo

- Librería: `studio/content/manim_extensions/emergencia/`
- Sonda: `studio/tools/sonda_emergencia.py`
- Curso 29 (16 piezas): `studio/content/verticales/emergencia/`
- Plan, cifras medidas y cosecha de trampas:
  `docs/plan_contenido/curso-29-emergencia-vertical.md`
- Herramientas del formato vertical: `render_vertical.py`, `alinear_voz.py`,
  `unir_vertical.py`, `sfx.py`
