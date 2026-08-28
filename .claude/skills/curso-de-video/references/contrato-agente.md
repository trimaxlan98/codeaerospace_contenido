# Producción con subagentes

El patrón lleva funcionando desde el curso 16 y escaló hasta 24 lecciones en
lotes de 6. Regla de reparto:

- **Una lección entera por agente** (sus 4 clips): el agente ve el arco
  completo de la lección y no hay costuras entre clips.
- **Sonnet** para lecciones mecánicas/geométricas; **Opus** para las
  conceptualmente delicadas (las que definen una idea nueva, las que cierran
  la familia, las que llevan cifras que pueden mentir).
- Olas de 4–6 agentes a la vez. Máximo **1 render simultáneo por agente** (la
  máquina renderiza 3 clips en paralelo, no más).
- Los agentes **no tocan la librería ni git**. Si un agente cree que hay un
  bug de librería, lo reporta con la medición que lo demuestra y el
  orquestador decide.
- Antes de lanzarlos: la librería validada, el **molde** escrito y aprobado, y
  los **stubs** de todos los clips creados.

## Plantilla de contrato (un .md en el scratchpad por lección)

```markdown
# Contrato — Lección N.M «<título>»

## Qué produces
Los 4 clips de `<worktree>/studio/content/cursos/<slug>/clips/`:
  01-<tema>.py … 04-<tema>.py, cada uno con `class ClipK(Scene)`.
NO toques: curso.json, style_block.py, la librería, git.

## Contexto obligatorio (léelo antes de escribir)
- Storyboard de tu lección: `docs/plan_contenido/curso-NN-<tema>.md`, sección «N.M».
- Molde de la familia (cópiale el estilo, el ritmo y la estructura):
  `studio/content/cursos/<slug-del-molde>/clips/`.
- Librería: `studio/content/manim_extensions/<tema>.py` (contrato en el plan).
- Trampas: la cosecha del plan + `.claude/skills/curso-de-video/references/trampas.md`.

## Reglas duras
- 28–45 s por clip (tope duro por ambos lados).
- **FORMATO MUDO (por defecto): no hay pie narrativo.** La palabra la pone la
  voz; la pantalla pone la cosa y su cifra. Solo pueden aparecer: título del
  clip (≤ 6 palabras), etiqueta del módulo, rótulos de mobiliario (≤ 4),
  cifras medidas (≤ 5), fórmulas y el cierre del clip 4. `pie_curso` NO existe
  y los helpers ABORTAN el render si escribes una frase — no intentes
  rodearlo con `Text(...)` a mano: si el render pasa pero hay prosa en
  pantalla, el clip se rechaza igual.
  *(Solo si el encargo pidió subtítulos: entonces sí hay `pie_curso`, con pies
  de ≥ 5 s, el pie cambia ANTES de la animación que ilustra y los rótulos
  viejos se apagan antes.)*
- TODA cifra en pantalla sale de la librería (numpy, semilla fija). Cero
  números escritos a mano. Si mides una ventana, la estadística es de la
  ventana.
- Sin acentos en el texto renderizado; superíndices y griegas en MathTex.
- Transform solo entre gemelas de estructura idéntica.
- Nada encimado. Nada de escalar VGroups para que quepan: pasa ancho/alto/fs.
- El clip 4 termina con el cierre a pantalla limpia que dice el storyboard.

## Validación (obligatoria, iterando hasta pasar)
    studio/backend/venv/bin/python studio/tools/render_local.py \
      <worktree>/studio/content/cursos/<slug> --clip K --frames 8
Revisa los 8 frames **uno a uno** con Read. Un frame con dos cosas encimadas,
un rótulo cortado, una cifra que no corresponde o una frase de prosa = no
aprobado, se corrige y se re-renderiza. Comprueba la duración que reporta la herramienta.

## Informe final
Una línea por clip: duración, qué se ve en el último frame, y las cifras que
mediste. Termina con `LECCIÓN N.M APROBADA` solo si los 4 pasaron. Si algo
quedó a medias, dilo explícitamente: el trabajo parcial queda en disco y se
relanza.
```

## Después de que vuelvan

1. **Revisa tú los frames de todas las lecciones**, no solo el informe.
2. Corre `pytest -q` del Studio si se tocó backend o extensiones.
3. Si apareció un bug de librería: corrígelo, re-renderiza los clips
   afectados, revisa los **rodeos** que otros agentes hicieron para
   compensarlo y los `final_state` que citan cifras.
4. Escribe en el plan la **cosecha de trampas del lote**: lo que midieron los
   agentes es la mitad del valor del lote.
