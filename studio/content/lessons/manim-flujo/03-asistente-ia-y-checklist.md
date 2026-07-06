---
title: Asistente IA y checklist final
level: intro
summary: Cómo sacar el máximo del asistente (explicar, corregir, generar) ahora que conoce las primitivas y estas lecciones, y el checklist antes del render final.
tags: [asistente, ia, checklist, workflow]
minutes: 7
order: 3
---

## Qué sabe el asistente

El asistente IA del Estudio (botones **Explicar**, **Corregir** y **Generar** en la pestaña Studio) recibe con cada petición, además de tu texto:

- El **código fuente completo de las primitivas** de `manim_extensions` (las 10).
- Las **convenciones del canal** (paleta, estructura de 4 actos, límites de duración).
- **Ejemplos reales** de la categoría Experimentación.

Consecuencia práctica: puedes pedirle directamente *"una constelación de 5 planos con enlaces ISL y un pulso de señal entre dos satélites"* y usará `ConstelacionLEO` y `PulsoDeSenal` con sus imports correctos, en lugar de inventar la rueda (o una API inexistente).

## Cómo pedir bien

- **Generar**: describe fenómeno + protagonista + duración: *"órbita excéntrica e=0.7 con estela, marca perigeo y apogeo, 12 segundos"*. Cuanto más concreta la física, mejor el resultado.
- **Corregir**: úsalo con el log del render fallido ya cargado (el botón lo adjunta solo). No edites a mano errores de LaTeX: Corregir los resuelve casi siempre a la primera.
- **Explicar**: para entender un traceback antes de decidir si corriges tú o el asistente.
- Itera: si el primer script no convence, pide el ajuste concreto ("más lento el tramo final", "los nodos en columna") en vez de regenerar desde cero.
- El asistente puede equivocarse: SIEMPRE renderiza en `ql` antes de confiar.

## Checklist antes del render final (qh)

1. ✅ Renderizado en `ql` y visto completo — ritmo, solapes, textos legibles.
2. ✅ Sin updaters vivos al final (`clear_updaters()` tras las animaciones que los usan).
3. ✅ Duración total razonable (10–20 s por escena; `qh` tarda ~8× el `ql`).
4. ✅ Textos: tildes, tamaño ≥17, nada cortado por los bordes (`to_edge`/`next_to` con `buff`).
5. ✅ Paleta del canal y glow solo en protagonistas.
6. ✅ Nombre de clase descriptivo (es el nombre en la Biblioteca).
7. ✅ Si usa primitivas: las 2 líneas de bootstrap arriba del todo.
8. ✅ `self.wait(1)` final para el corte de edición.

## Mantenimiento de la biblioteca

Cuando una animación nueva repita un patrón por tercera vez, conviértelo en primitiva: archivo en `manim_extensions/` (con las reglas de la lección *Cómo usar la biblioteca*), demo en Experimentación, y commit. Así la biblioteca crece con el canal y el asistente la aprende automáticamente en su siguiente petición.
