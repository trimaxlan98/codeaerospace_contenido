# Rendimiento de los renders (laptop de desarrollo)

Mediciones del 2026-08-05 sobre un clon local, para saber qué esperar al
iterar en local y qué no vale la pena tocar.

**Máquina**: 4 núcleos / 8 hilos, 14 GB RAM, `intel_pstate` en `powersave`
(turbo activo), Docker sobre SSD NVMe.
**Escena**: `src/episodio1/orbit_logic_ep1.py` → `OrbitLogicEp1V2`, una
`ThreeDScene` con campo vectorial gravitatorio (~81 flechas) y dos órbitas.
Es la carga real más pesada del repo.

## Resultados

| Escena | Calidad | Salida | Wall | CPU media/pico | RAM pico |
|---|---|---|---|---|---|
| `Demo` (2D trivial) | 480p15 | 33 KB | 41.7 s | — | — |
| `OrbitLogicEp1V2` | 480p15 | 854×480, 300 fr, 381 KB | 121.2 s | 105% / 130% | 240 MiB |
| `OrbitLogicEp1V2` | 720p30 | 1280×720, 600 fr, 859 KB | 241.2 s | 106% / 123% | 338 MiB |

Reproducibilidad: el de 480p15 repetido dio 118.5 s (±2%).

## Lo que cuesta son los frames, no los píxeles

Las dos calidades rinden **2.5 frames por segundo, idéntico**: 300 fr en
121.2 s y 600 fr en 241.2 s. Duplicar la resolución no costó nada medible. El
2× de tiempo entre `-ql` y `-qm` viene entero de pasar de 15 a 30 fps.

El cuello de botella es el cálculo de geometría por frame — en esta escena,
recalcular el campo vectorial y las posiciones orbitales — no la
rasterización. Por eso la resolución sale casi gratis.

Consecuencias prácticas:

- `-ql` no es "baja calidad barata", es **menos frames**. Si lo que quieres es
  iterar rápido sobre contenido 3D, baja los fps o simplifica la geometría; no
  ganas nada bajando la resolución.
- Estimación rápida: **wall ≈ nº de frames / 2.5** para escenas 3D de este
  tipo. Un video de 20 s a 1080p60 (1200 frames) son unos **8 minutos**.
- Escenas 2D simples son otro mundo (41 s para el `Demo`), así que el número de
  arriba es el peor caso, no el típico.

## Subir el límite de CPU del compose no sirve

`docker-compose.yml` limita los renders a `cpus: "1.5"` y `memory: 2g`, tuneado
para el VPS de 2 vCPU. Es tentador subirlo en una laptop con 8 hilos. No
funciona — misma escena, mismo `-ql`, saltándose la app:

```
cpus=1.5  →  117.25 s
cpus=4    →  116.63 s
```

Sin diferencia. **Manim con el renderer cairo es single-thread**; el 105% de
CPU media es un núcleo saturado más algo de ffmpeg solapado al combinar los
parciales. Los picos de 130% son ese solape, no paralelismo del render.

La RAM tampoco aprieta: 240–338 MiB observados contra un límite de 2 GB. Hay
margen de sobra para subir la calidad sin tocar `memory`.

Conclusión: **deja los límites como están**. Están dimensionados para que el
VPS no se ahogue y en local no cuestan nada.

## Tampoco hay nada que rascar en la CPU

`intel_pstate` con gobernador `powersave` ya escala a 3.6–3.7 GHz sostenidos
bajo carga (máximo 4.0), con turbo activo. Cambiar a `performance` no va a
mover la aguja. Sin throttling térmico durante los 4 minutos del render de
720p30.

## La app no se degrada mientras renderiza

Latencia de `GET /api/jobs`, muestreada cada segundo:

| | mediana | p95 | máx |
|---|---|---|---|
| En reposo | 3 ms | — | 6 ms |
| Durante un render | 2 ms | 5 ms | 7 ms |

Indistinguible. El cgroup del contenedor de render aísla bien la carga y la UI
sigue fluida — no hace falta esperar a que termine un render para navegar.

Otras dos propiedades verificadas:

- **La cola serializa de verdad.** Con dos jobs enviados a la vez, el segundo
  se queda en `queued` y nunca hay dos contenedores de render simultáneos.
- **Los artefactos son pequeños.** 8 renders ocuparon 2.8 MB de los 4 GB de
  cuota (`MS_MAX_STORAGE_MB`). Lo que pesa es la imagen de Docker (1.4 GB), y
  eso es una sola vez.

## Cómo reproducir

```bash
# Render por la API (requiere sesión; la cookie sale de POST /api/login)
curl -s -b cookies.txt -X POST http://127.0.0.1:3002/api/jobs \
  -H 'Content-Type: application/json' \
  -d "{\"script\":$(python3 -c 'import json;print(json.dumps(open("src/episodio1/orbit_logic_ep1.py").read()))'),\"scene\":\"OrbitLogicEp1V2\",\"quality\":\"ql\"}"

# Uso de recursos del contenedor mientras corre
docker stats --no-stream --format '{{.Name}} {{.CPUPerc}} {{.MemUsage}}' \
  | grep manimstudio-render

# Aislar el efecto del límite de CPU, sin la app de por medio
docker run --rm --network none --cpus=1.5 --memory 2g \
  -v "$PWD/bench:/work:rw" -w /work -e HOME=/tmp --user "$(id -u):$(id -g)" \
  codeaerospace_contenido-manim:latest \
  manim render -ql --disable_caching --media_dir /work/media /work/scene.py OrbitLogicEp1V2
```
