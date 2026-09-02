# El estilo LIENZO

Lenguaje visual para piezas verticales (9:16) en las que la pantalla enseña
**una cosa** y **un dato**, y nada más. Vive en
`studio/content/manim_extensions/lienzo.py` y se estrenó en el curso 31
(*ESP32: el chip por dentro*).

No sustituye a nada. Los cursos 26, 28 y 29 usan la estética de consola de
vuelo de la marca (fondo casi negro, escuadras HUD, telemetría en las cuatro
esquinas, pie de cifra de tres renglones). LIENZO es lo contrario y convive
con ella: se elige por curso, no por clip.

## Las cinco reglas

1. **Fondo liso azul marino** (`#0B1B33`), plano, sin degradado ni textura.
   Cuando no hay nada en pantalla, el fotograma es ese color y nada más.
2. **Cuatro carriles y un solo ocupante cada uno**: `numero` (arriba
   izquierda), `escena` (el dibujo), `dato` (cifra + etiqueta) y `marca` (el
   pie). Meter algo en un carril ocupado **apaga primero** lo que había.
   Nada se encima porque no hay dónde encimarlo — es una garantía
   estructural, no una regla que el autor tenga que recordar.
3. **Cuatro colores**: fondo, tinta (`#EAF1F8`), apagado (`#7C8FA6`) y un
   acento ámbar (`#F5A31B`). El cian (`#5AC8D8`) es el quinto y sólo aparece
   cuando hay **dos** señales a la vez que hay que distinguir.
4. **Escala tipográfica cerrada**: 128 / 46 / 30 / 22 / 18. `cifra()` baja de
   peldaño hasta que la cadena entra en la zona segura, pero no hay cuerpos
   intermedios y no se escala el mobject.
5. **La marca no invade**: `co.de academy` en el pie a opacidad 0.32 y el
   número de pieza arriba a la izquierda, apagado. Ni escuadras, ni logotipo,
   ni barra de progreso.

## Procedencia de las cifras, sin gastar un color

La cifra es **siempre** tinta: es la protagonista. Lo que cambia es la
**etiqueta** de debajo:

| Etiqueta | Significa |
|---|---|
| **ámbar** | el número lo calcula la librería durante el render |
| **apagada** | viene de una hoja de datos / literatura |

`lz.etiqueta(texto, medido=True/False)` y `L.dato(valor, texto, medido=...)`.

Las unidades se escriben **con todas sus letras** ("megahercios", no "MHz"):
la etiqueta va en versalitas y `MHZ`, `MS` o `MV` no son la unidad que se
quería escribir.

## Uso mínimo

```python
FMT = lz.formato()                   # a nivel de módulo del style_block

class Clip(Pieza):                   # Pieza monta y funde por ti
    NUMERO = 3

    def pieza(self):
        L = self.L
        dibujo = ...                 # un VGroup cualquiera
        L.escena(dibujo, animacion=Create(dibujo, run_time=1.8))
        L.dato("240", "megahercios de reloj", medido=False)
        self.wait(4.0)
        L.dato("1.25", "metros que viaja la luz")     # releva al anterior
        self.wait(5.0)
```

Contadores: `L.contador_vivo(texto, valor_en, t_final)` lee el **reloj de la
escena**, así que sigue corriendo mientras pasan otras animaciones y el
número que se ve corresponde exactamente a ese segundo de vídeo.
`L.dato_animado(valores, texto, duracion)` para una cifra que corre en un
único `play`.

## Guardianes (abortan el render, y deben hacerlo)

- `cabe(mob)` — más ancho que la zona segura (5.76 unidades). La columna de
  botones de la app se come el 14 % derecho, y un rótulo que se mete ahí no
  se nota en un frame de validación.
- `encajar(mob)` — si para caber hubiera que encoger tanto que un rótulo baje
  de `ALTO_MINIMO` (0.155 unidades ≈ 24 px en el 1080x1920 final).
- `dato()` — si la etiqueta baja hasta la marca de agua.
- `titulo_display()` — Rajdhani por debajo de 40.
- `esp32.barra_apilada()` — si dos rótulos de tramo se encimarían.

Cuando uno salta, **la respuesta es acortar el texto o quitar elementos del
dibujo**, nunca subir el límite ni escalar el grupo a mano.

## Medidas del lienzo (1080x1920, mundo 8.0 × 14.222)

| | |
|---|---|
| techo / suelo útiles | `+5.689` / `-4.267` |
| franja del dibujo | `-0.95` … `+4.639` (alto 5.589) |
| centro de la cifra | `-2.30` |
| marca de agua | `-3.967` |
| ancho seguro centrado | `5.760` |
| cifra a cuerpo 128 | 1.061 unidades por carácter → **5 caracteres** |
| etiqueta a cuerpo 30 | 0.277 por carácter → **20 caracteres** |

Un dibujo que ocupa menos del 60 % del alto de la franja se lee como un
error, no como minimalismo: la cifra queda lejísimos y la composición se
parte en dos.
