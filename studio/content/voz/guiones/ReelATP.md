# Guion de voz · CO.DE ATP-DT · ¿0.1° alcanza?  (ReelATP.mp4, 12.000 s, loop)

Tiempos en segundos del VIDEO (t = 0 es el primer cuadro; el desfase del reel ya está aplicado).
Voz: Piper `es_MX-ald-medium` (ver `LEEME.md`). Si grabas tú, respeta los tiempos de inicio: el video no cambia.
Estilo: español neutro, tuteo, claro y entusiasta sin exagerar, ritmo de unas 2 palabras por segundo.
Siglas: se leen por letras (V-F-O, S-S-T-V, I-Q).

## Variante A · «voz libre» (24 palabras; la voz cabe entre 0.35 s y 11.4 s)

| Tiempo (s) | Frase (lo que se dice) | Qué se ve |
|---|---|---|
| 0.40 → 3.07 | ¿Puede una antena apuntar a 0.1 grados? | Título fijo «¿Puede una antena apuntar a 0.1°?»; la antena sigue al satélite; chip LQR encendido (0.4–2.6 s) |
| 3.40 → 7.17 | Este banco de pruebas, en beta, prueba cinco controladores. | Chip H∞ (2.6–4.8 s) y luego Lazo abierto (4.8–7.0 s); la traza del error en el osciloscopio con la banda de ±0.1° |
| 7.45 → 11.05 | Es un presupuesto de diseño, con trazas ilustrativas. | La antena se reposiciona (7–8 s); chip PD (7.5–10.2 s); chip ámbar fijo «Trazas ilustrativas» |

## Variante B · «lazo de frase» (28 palabras; la última frase se completa con la primera al repetirse el loop)

| Tiempo (s) | Frase (lo que se dice) | Qué se ve |
|---|---|---|
| 3.10 → 6.98 | Este banco de pruebas, en beta, prueba cinco controladores. | Chip H∞ (2.6–4.8 s) y Lazo abierto (4.8–7.0 s); osciloscopio con la banda de ±0.1° |
| 7.15 → 10.64 | Es un presupuesto de diseño, con trazas ilustrativas. | Reposicionamiento (7–8 s) y chip PD (7.5–10.2 s); chip ámbar «Trazas ilustrativas» |
| 10.78 → (empalme) → 2.97 | Y la pregunta es: [loop] ¿puede una antena apuntar a 0.1 grados? | Chip PID (10.2–12.4 s) → al repetirse, título «¿Puede una antena apuntar a 0.1°?» con la antena siguiendo |

**Cómo grabar la B:** di la última frase hasta el corte («[loop]»), deja correr la grabación por el empalme de las
12.000 s y retoma la misma frase al volver a empezar. Si grabas en una sola toma, empieza la frase en el segundo
indicado y deja que cruce el final del archivo.

## Reglas de honestidad que respeta este guion

- ATP-DT es beta; 0.1° es un presupuesto de diseño (no un resultado medido).
- Las curvas del osciloscopio son ilustrativas, y así se dice.
