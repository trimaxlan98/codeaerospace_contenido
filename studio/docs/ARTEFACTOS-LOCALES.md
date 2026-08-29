# Artefactos locales persistentes

Los videos terminados y los trabajos de render no deben vivir físicamente en
un worktree de Git. En esta máquina, las rutas del repositorio son enlaces al
almacén persistente del segundo disco:

```text
exports     -> /home/alanrosasp/data/codeaerospace/exports
render_jobs -> /home/alanrosasp/data/codeaerospace/render_jobs
```

`exports/` es el archivo canónico. Nunca se elimina al retirar ramas o
worktrees. `render_jobs/` contiene material intermedio regenerable, pero se
mantiene fuera del checkout por la misma razón.

Después de cerrar un lote se ejecutan `inventariar_exports.sh` y
`snapshot_exports.sh`. El segundo crea una instantánea por enlaces duros en
el mismo disco: no duplica los gigabytes de video, pero una eliminación desde
`exports/` no borra los datos de la instantánea.

Antes de limpiar un worktree, se debe comprobar explícitamente que no contiene
directorios reales llamados `exports` o `render_jobs`. Un estado limpio de Git
no basta: ambos están ignorados.

## Organización

```text
exports/
  <slug-de-curso>/                    cursos horizontales
  verticales/<slug>/
    piezas/                           piezas publicables con audio
    voz/                              narraciones WAV
    <slug>_vertical.mp4               montaje completo
  promos/<slug>/
    vertical.mp4                      entrega publicable
  inventario/                         manifiestos y checksums
```

No se debe crear un `exports/` privado dentro de otro checkout. Todas las
herramientas se ejecutan desde el checkout principal y escriben mediante el
enlace persistente.
