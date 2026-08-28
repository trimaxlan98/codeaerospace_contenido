# Plantilla del plan maestro

`docs/plan_contenido/curso-NN-<tema>.md`. Es el **único estado que sobrevive
a la sesión**: si la conversación se corta, la siguiente corrida tiene que
poder continuar leyendo solo este archivo. Ojo con la numeración: el número
del **archivo** es correlativo a los archivos de `docs/plan_contenido/`, y el
número del **curso** es el de `PLAN.md` — no siempre coinciden; decláralo.

## Secciones

1. **Cómo reanudar** (arriba del todo, 4 líneas): qué rama/worktree, dónde
   está el tablero, y la frase con la que el dueño reanuda ("continuamos con
   el curso de X").
2. **Formato**: familia o curso de 8 clips; módulos × lecciones = proyectos y
   clips; patrón de nombre y de slug. **Y si el curso lleva subtítulos o no**:
   el defecto es que NO (formato mudo). Si el dueño los pidió, se dice aquí,
   porque es lo que leen los subagentes. Si no los pidió, esta sección lleva
   la tabla de lo que puede aparecer en pantalla y la nota de que el guardián
   del `style_block` aborta el render — ver la §2 del plan del curso 27
   (`curso-24-procesamiento-senales.md`), que sirve de plantilla.
3. **Ángulo editorial**: la idea que hilvana el curso entero, en dos frases.
   Y el arco: dónde empieza y dónde termina.
4. **Público y qué asume**: qué cursos previos da por sabidos.
5. **Qué NO pisa**: curso por curso vecino, qué queda por debajo, qué se
   **usa** sin re-explicar, qué se toca por otro lado. Esto evita el problema
   real de una colección de 25 cursos: repetirse.
6. **Principio visual no negociable**: 5–7 puntos de qué tiene que VERSE
   moverse en pantalla en esta familia. Es lo que distingue una familia de
   otra y lo que citan los subagentes.
7. **Mapa de lecciones**: tabla `lección | proyecto | 4 clips en cuatro
   palabras`.
8. **Paleta por ROL**: alias → color → papel. El color dice el papel, no la
   estética; el cian es siempre "cifra calculada aquí".
9. **Contrato de la librería**: qué reutiliza de otras familias, piezas de
   dibujo (con sus gemelas `con_*`) y funciones numéricas, una línea cada una
   diciendo **qué devuelve medido**.
10. **Lotes de producción**: tabla lote → módulos → lecciones → qué aporta a
    la librería → estado.
11. **Receta de lote**: los 10 pasos del pipeline, concretados con las rutas
    de esta familia.
12. **Tablero de estado**: una fila por lección, columnas
    `plan · librería · clips · ql ✔ frames · PR · subida · qh · narrada · mux`,
    leyenda `— / ~ / ✔`. **Se actualiza tras cada hito, no al final.**
13. **Storyboard por módulo**: por lección, un párrafo de intención y los 4
    clips numerados, cada uno con lo que se ve, la función de la librería que
    da sus cifras, y las cifras que se rotulan (o el pie, si el curso lleva
    subtítulos). El clip 4 lleva el cierre literal, dos líneas.
14. **Cosecha heredada**: las trampas de las familias vecinas que más riesgo
    tienen en ésta.
15. **Cosecha de trampas del lote N**: se escribe DURANTE la producción, con
    lo que midieron los agentes. Es lo que hereda la familia siguiente.
16. **Hitos globales**: fecha + qué quedó publicado, con PR y cifras
    verificadas (lecciones en prod, `qh` adoptados, wavs, duraciones, picos).
