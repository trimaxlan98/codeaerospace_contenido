# Prompt para el agente de la Estación (GPU): serie «Robótica 3D»

Copia el texto de abajo completo al agente Claude de la Estación Windows (WSL2 + GPU, ya validada en `ros2-workspace/docs/GPU.md`).

---

Trabajas en la **Estación** (Windows 11, WSL2 Ubuntu 24.04, NVIDIA Quadro RTX 5000; GPU en WSL2 por Mesa d3d12, ver
`~/ros2-workspace/docs/GPU.md`). Todo en español. Si algo falla, no lo ocultes: repórtalo con la salida.

**Objetivo:** producir la serie de reels **«Robótica 3D»** (Instagram, 1080×1920, 30 fps): el rover planetario de seis ruedas del
`ros2-workspace` recorriendo terreno 3D, dibujado con GPU por `studio/motor3d` (moderngl/EGL, sin pantalla), con **poses que salen de
corridas reales de la simulación** (nada de movimiento inventado). Es la versión 3D de la serie 2D «Robótica» (`42-reels-robotica.py`).

## Repositorios (clónalos DENTRO de WSL, uno junto al otro, `git config core.autocrlf false`)

- `https://github.com/trimaxlan98/codeaerospace_contenido` (**PÚBLICO**) → `~/codeaerospace_contenido`. Rama base:
  `animaciones/tesis-y-ponencias`. Tu rama: `estudio/robotica-3d` (`git fetch && git checkout -B estudio/robotica-3d origin/animaciones/tesis-y-ponencias`).
  Sube tu rama con `git push -u origin estudio/robotica-3d`; **no abras PR** salvo que el dueño lo pida.
- `https://github.com/trimaxlan98/ros2-workspace` (privado) → `~/ros2-workspace`, rama `main`, **solo lectura** (no hagas commits ahí).
- Identidad de git en `codeaerospace_contenido` (config local): `Alan Rosas Palacios <ingalanr@gmail.com>`.

## Lee primero

1. `.claude/skills/estudio-contenido/SKILL.md` (reglas del dueño, formato PELÍCULA, honestidad, CLI `./codeae`).
2. `studio/motor3d/` (GPU, Escena, Camara, mallas; hoy dibuja Tierra/atmósfera/estrellas/satélites).
3. `studio/content/manim_extensions/datos_rob.py` y `docs/estudio/series/robotica_PIES_Y_CUIDADO.md` (pies de la serie 2D y qué NO afirmar).
4. En `ros2-workspace`: `docs/ROVER.md` (R1–R10) y `docs/CONTRATO.md` §18 (formato de `telemetry.jsonl` del rover).

## Tareas

1. **Entorno.** `python3 studio/tools/verificar_entorno_3d.py --ros2 ~/ros2-workspace`. Debe decir `LISTO` y `GL_RENDERER` **no** debe
   ser llvmpipe/swrast (si lo es, revisa `docs/GPU.md` del workspace: `GALLIUM_DRIVER=d3d12`, `/usr/lib/wsl/lib` en `LD_LIBRARY_PATH`).
   Instala lo que falte con `pip install --user --break-system-packages …` y las fuentes con `python3 animaciones/instalar_fuentes.py`.
   Mira `exports/estudio/_prueba3d/prueba_tierra.png`.
2. **Corridas del rover sin ROS** (Python puro, deterministas, ~45 s cada una):
   `cd ~/ros2-workspace/src/atp_rover && python3 -m atp_rover.cli --escena ../../experiments/<escena>.yaml --salida ~/rover3d --id <id>`.
   Usa al menos: `rover-luna-rocoso`, `rover-marte-dunas`, `rover-titan-pendiente`, `rover-luna-escalon` (con `--suspension=rocker_bogie`
   para tener `balancin_deg`/`bogie_deg`/`carga_n`) y `rover-marte-rocas` con `--navegacion=completa`. Congela lo que uses en
   `studio/content/datos_rob3d/` (telemetría submuestreada si pesa > 2 MB, `metrics.json` y un `PROCEDENCIA.md` con commit del
   workspace, escena y argumentos), con un script `studio/tools/rob3d_congelar.py`, para que el render no dependa del otro repo.
3. **Motor 3D: terreno y rover** (en `studio/motor3d/`, sin romper lo que ya dibuja):
   - `mallas.terreno(funcion_altura, x0, x1, y0, y1, paso)` a partir de `atp_rover.terreno.Terreno(tipo, semilla).altura(x, y)`: el
     **mismo** terreno de la corrida (misma semilla). Material por planeta (regolito gris en la Luna, óxido en Marte, ocre en Titán).
   - `mallas.rover(...)`: cuerpo, mástil con cámara, 6 ruedas, balancín y bogie como piezas separadas para poder girarlas con los
     ángulos de la telemetría. Geometría de `atp_rover` (parámetros del YAML: radio de rueda, vía, batalla); no inventes medidas.
   - Pose por cuadro: `x, y, z, rumbo_deg, cabeceo_deg, alabeo_deg` (y `balancin_deg`, `bogie_deg` si existen), interpoladas de 10 Hz a
     30 fps. Ruedas giradas por la distancia recorrida/radio. Huella (rodadas) en el suelo con `lineas`.
   - Iluminación: sol bajo (sombras largas), cielo negro en la Luna, cielo de Marte rojizo, bruma naranja en Titán. Sombras si da la GPU;
     si no, oclusión ambiental simple. Mide fps de render y anótalos.
4. **Serie: 6–8 reels** de 20–30 s en formato PELÍCULA (título 0.6 s → cuerpo → pausa → logo de Co.De → disolución al título; loop
   exacto). El 3D va de fondo/cuerpo; **título, leyendas, chip «Simulación · ROS 2» y el cierre con logo van en Manim** encima
   (componer con ffmpeg: video 3D + capa Manim con alfa `--transparent`, o cuadros 3D como `ImageMobject` si es más simple). Ideas
   (una por reel, cada cifra sacada del `metrics.json` congelado): mismo rover en cuatro mundos (gravedad y deslizamiento);
   rocker-bogie sobre un escalón (cómo reparte la carga entre las 6 ruedas, **sin** decir que supera a la suspensión simple); duna en
   Marte y deslizamiento; pendiente en Titán; navegación A* esquivando rocas (ruta planificada vs. recorrida); vista de la cámara del
   mástil. Datos y tiempos en `datos_rob3d.py` (escena y audio leen el mismo módulo). Audio sintético con `sonido_reels.py`
   (`REELS_ROB3D`), registro en `codeae._videos()` (grupo `robotica3d`, salida `exports/estudio/reels_robotica3d/`).
5. **Verifica**: prueba baja resolución primero (540×960, 12 fps), hojas de contacto mirando la imagen, luego `./codeae render`; loops
   con PNG (`verificar_loop.py --png`). Escribe `exports/estudio/reels_robotica3d/PIES_Y_CUIDADO.md` (pie, ≤ 5 hashtags y ⚠️ por reel).
6. **Paquete, no subida**: `./codeae paquete … --nombre <fecha>-serie-robotica-3d`. **No subas a Drive**: el dueño lo decide (las
   subidas siempre llevan su confirmación). Los videos NO van a git.

## Reglas que no se negocian

- Todo es **simulación**: chip «Simulación · ROS 2» en pantalla y «en simulación» en los pies. Ninguna cifra es medida con hardware;
  los suelos de Marte/Titán/Ceres son supuestos; la montura real nunca se probó.
- El rocker-bogie **no** mostró ventaja sobre la suspensión simple en el ensayo de escalón (solo reparto de carga); la navegación
  «completa» corregida (R10) **no** supera a la básica; IC95 muy anchos en R8.
- **Nada de la tesis** (NTN, RL/QMIX, compuertas, PADA, Margen Adaptativo) y **sin nombres de clientes**. El repo es público: revisa el
  diff antes de cada push. No subas a git piezas `animaciones/tesis_*` ni `ponencia_redes_*`.
- Fondo mínimo, temas oscuros, sin voz (solo sonido sintético), una sola versión por video.

## Entregables

- Rama `estudio/robotica-3d` subida con: extensiones de `motor3d` (terreno, rover, pose), `datos_rob3d.py` + datos congelados,
  escenas `43-reels-robotica3d.py` (o el número libre siguiente), audio y registro en `codeae`, y una sección «Robótica 3D» en la skill
  `estudio-contenido` (cómo se hizo, trampas, fps medidos).
- Un resumen final: qué reels salieron, rutas y tamaños de los MP4, fps de render con GPU vs. el mismo cuadro por software
  (`LIBGL_ALWAYS_SOFTWARE=1`), qué no se pudo hacer y por qué.
