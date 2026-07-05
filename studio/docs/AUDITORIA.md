# ManimStudio — Reporte de auto-auditoría (2026-07-05)

## Fases ejecutadas

1. **Planificación** — reconocimiento de infra existente (compose, vhost, puertos, 19
   contenedores de producción), elección de stack documentada en README.
2. **Delegación** — los tres perfiles (frontend, backend/cola, seguridad/sandbox) se ejecutaron
   secuencialmente en esta misma sesión. *Excepción 3 del protocolo (fallback a Opus 4.8): NO se
   activó — no existe tal mecanismo de derivación entre modelos; los módulos de auth y sandbox
   son desarrollo defensivo estándar y se implementaron aquí sin bloqueo.*
3. **Ejecución** — código completo + pruebas (abajo).
4. **Auto-auditoría** — este documento, con verificación visual por capturas reales.
5. **Entrega** — sistema desplegado y verificado en producción.

## Evidencia de pruebas

### Unitarias/integración (pytest, 20/20 en verde)
- Auth: login ok/mal, cookie firmada y manipulada, logout, **bloqueo tras 5 fallos incluso con
  password correcta**, timing-safe con hash dummy.
- Escenas: herencia directa/transitiva/atributo, error de sintaxis, herencia circular, y
  **canario que demuestra que el script NO se ejecuta** al detectar escenas.
- Jobs API: validaciones (calidad, escena inexistente, inyección en nombre de escena, timeout,
  tamaño 413), escritura del script en ruta canónica, error limpio sin runner, 404 con
  path traversal (`/api/jobs/../../etc/passwd`).

### End-to-end en el VPS real
| Prueba | Resultado |
|---|---|
| Render `ql` completo vía API | `done`, MP4 válido descargable (`ISO Media`) |
| Red dentro del contenedor de render | **bloqueada** (`RED_BLOQUEADA_BIEN: URLError` con `urlopen 1.1.1.1`) |
| Cancelación de render en curso | contenedor `manimstudio-render-*` eliminado, job `cancelled` |
| Auth perimetral vía nginx | `/api/jobs`, `/api/metrics`, `/api/events` → 401 sin cookie |
| SSE a través de nginx | stream de métricas fluye sin buffering |
| `sudo -u manimstudio docker ps` | **permission denied** (el web-facing no toca docker.sock) |
| Dominios vecinos tras reload de nginx | spot-check codefinance.space → 200 |
| Contenedores de otros proyectos | intactos (solo lectura de métricas agregadas) |

### Verificación visual (capturas reales del sitio en producción)
- Login: tarjeta centrada, glifo orbital, foco visible — coincide con el objetivo.
- Estudio: editor + cola con estados reales (listo/error/cancelado) + logs en vivo del render.
- Monitoreo: 4 medidores de host correctos contra `free`/`df`, tabla completa de contenedores
  con estado/CPU/MEM y nota de solo-lectura.
- Móvil (390px): apila en una columna, usable.

## Fallas encontradas y corregidas durante la auditoría
1. `pids_limit` + ancla `deploy` compartida → compose inválido. Corregido con merge YAML
   (`pids` dentro de `deploy.resources.limits` del servicio render). Detectado por el primer
   render de prueba fallido.
2. `/run/manimstudio` root:root 0750 impedía al backend alcanzar el socket. El runner ahora
   ajusta grupo/permisos del directorio al arrancar.
3. Duplicación potencial de líneas de log (solape snapshot HTTP + stream SSE) en el frontend.
   Corregido: el stream vivo se reinicia tras cada snapshot.

## Riesgos residuales (aceptados, documentados)
- El contenedor de render escribe como root en `render_jobs/` (bind mount); el backend solo
  necesita leer. Aceptable; alternativa futura: `user:` en el servicio render.
- Escape de contenedor Docker: mitigado (sin red, sin privilegios nuevos, límites pids/cpu/mem,
  timeout, sin montajes fuera del workspace), no eliminable al 100% sin gVisor/kata.
- El runner corre como root: es el punto de diseño (en vez de exponer docker.sock al proceso
  web); su superficie son 4 comandos validados por regex sobre un compose file fijo.
- Rate-limit global puede permitir que un tercero (sin credenciales) bloquee el login 15 min
  (DoS de login). Umbral global x3 mitiga; aceptable para un sitio no indexado de un usuario.

## Cumplimiento de excepciones del protocolo
- Excepción 1 (costo/irreversible): no se activó — no se contrató nada, no se tocó producción ajena.
- Excepción 2 (bloqueo total): no se activó.
- Excepción 3 (fallback Opus 4.8): no se activó (ver Fase 2).
