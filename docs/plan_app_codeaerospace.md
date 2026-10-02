# Plan: CO.DE Studio con marca Co.De Aerospace, presentaciones y librerías Manim nuevas

Fecha: 2026-10-01 · Rama: `animaciones/tesis-y-ponencias`

## Punto de partida (validación del 2026-10-01)

**La app** es CO.DE Studio (`studio/desktop`, Electron). Se compiló con `scripts/install-linux.sh`: 8/8 pruebas
unitarias, instalada en `~/.local/opt/code-studio` y con su acceso en el Escritorio.

Tiene cuatro vistas: **Estudio** (la web de ManimStudio en un webview), **Exports**, **Terminal** (con Claude Code y
el asistente de curso) y **Sistema** (servicios, tareas y diagnóstico).

**Presentaciones: sí, pero solo las básicas.** En el Estudio web una presentación es un tipo de proyecto. Cada clip
es una escena Manim que se corta por `presentacion.paso()`, y `PresentacionPanel` arma un `.pptx` con GIF o video.
No hay temas, guion ni notas del orador.

El sistema de presentaciones nuevo vive en `animaciones/` y la app no lo conoce: no aparece nada de
`decks_espaciales`, `presentaciones_usuario` ni `temas_espaciales` en `studio/`. Ese sistema incluye:
- 18 temas;
- las presentaciones propias en JSON;
- el guion con advertencias;
- las pruebas de calidad;
- el editor PySide6.

Hoy solo se llega a él con la app PySide6 `app/render_launcher.py` o por terminal.

**Marca.** La app y el Estudio llevan la identidad CO.DE **Academy**: la «C» con punto ámbar y la paleta
ámbar/cian. El logo de Co.De **Aerospace** no existe en el repo (ni SVG ni PNG), y las presentaciones lo escriben
como texto en Orbitron.

## Objetivos

1. Marca Co.De Aerospace como activo del repo: el logo vectorial, fiel al PNG oficial, utilizable en web, en la app,
   en los PPTX y en Manim.
2. Librerías Manim nuevas, reutilizables y con pruebas.
3. La app de escritorio con la marca y con las funciones que le faltan: presentaciones con temas y un kit de marca.
4. Un experimento: animar el logo en Manim.

## Fases

### F1 · Kit de marca (`marca/`)
- `marca/originales/`: los tres PNG oficiales tal cual (plata transparente, fondo oscuro, negro sobre blanco).
- `marca/vectorizar_logo.py`: potrace a 3×, con las partes separadas por componentes conexos:
  - las órbitas como contorno y además como línea central con su grosor;
  - la luna y el punto como círculos exactos;
  - el satélite, CO.DE y AEROSPACE trazados.
  - Genera `logo-codeaerospace{,-negro,-blanco}.svg`, `emblema-codeaerospace.svg` y la geometría para Manim.
- **Criterio de calidad:** IoU ≥ 0.98 entre el contorno vectorial y el PNG, e IoU ≥ 0.93 con las órbitas como trazo.

### F2 · Librerías Manim nuevas (`studio/content/manim_extensions/`)
- `estelas.py`, trazos con movimiento: dibujar con cometa (la punta brillante que va dibujando), recorrer una
  trayectoria con estela que se desvanece, y estelas parciales. Es genérico; lo usan el logo y cualquier órbita.
- `marca_aerospace.py`, el logo como `VGroup` por partes (`orbitas`, `luna`, `satelite`, `letras`, `aerospace`)
  con plata, una tinta o color libre, y sus animaciones de marca:
  - `entrada_logo` en tres estilos: orbital, trazo y ensamble;
  - `salida_logo`;
  - `marca_agua_aerospace`.
- `rotulos_aerospace.py`, rotulación de video con la marca: tarjeta de título, tercio inferior, cortinilla
  orbital y cierre con el logo. La fuente es Montserrat (OFL), la más cercana a la del logo, versionada en `fonts/`.
- Cada librería lleva su demo en `studio/content/animations/experimentacion/` y su sonda en `studio/tools/`.
  El índice de conocimiento del Estudio las descubre por su docstring.

### F3 · App de escritorio
- **Marca:**
  - ícono nuevo, generado del emblema Co.De Aerospace;
  - el logo en el riel;
  - pantalla de **Inicio** con el logo, accesos rápidos y el estado del sistema;
  - la paleta de la app pasa al fondo del logo (#080F15), con la tinta plata y el acento cian de codeaerospace.com.
- **Presentaciones** (vista nueva), sobre el sistema de `animaciones/` y sin duplicar su lógica (la app llama a sus
  CLI):
  - las presentaciones (incluidas y propias) con diapositivas, minutos y validación;
  - la galería de los 18 temas con su portada;
  - los decks ya construidos con su hoja de contactos;
  - construir en uno o varios temas, en una pestaña de la Terminal;
  - abrir el PPTX y el PDF;
  - leer el guion;
  - abrir el editor.
- **Marca** (vista nueva):
  - el logo en sus variantes, con copiar ruta y abrir;
  - la paleta con copiar el HEX;
  - las animaciones del logo con reproductor;
  - una tarea para renderizarlas.
- **Pruebas:** unitarias del catálogo de presentaciones y de marca (`node --test`), y la prueba de humo
  recorre las vistas nuevas.

### F4 · Marca en las presentaciones
- La portada y el cierre de los decks ponen el logo (PNG plata en temas oscuros, negro en claros) en lugar del texto
  «CO.DE AEROSPACE».
- `pruebas_presentaciones.py` comprueba que el logo está y que no se sale de la diapositiva.

### F5 · Experimento: el logo animado
- La entrada orbital:
  1. las seis órbitas se dibujan con cometa;
  2. la luna llega por su órbita;
  3. el satélite entra por la órbita plana y despliega los paneles;
  4. CO.DE se traza y rellena;
  5. el punto cae;
  6. AEROSPACE se abre en tracking;
  7. pasa un destello.
- Al final las órbitas de trazo se cambian por el contorno exacto, así el último cuadro es el logo.
- Versiones: oscura, clara, vertical 9:16, cierre y una ultra corta (sting).
- **Verificación:** el último cuadro se compara con el PNG oficial (IoU de la silueta ≥ 0.95).

### F6 · Cierre
- La documentación: este plan, `marca/LEEME.md` y las skills `animaciones-code` y `manimstudio`.
- La app reconstruida y reinstalada, con todas las pruebas: unitarias, humo, presentaciones y sondas.
