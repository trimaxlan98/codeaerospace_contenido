# Entorno de desarrollo local

Cómo levantar ManimStudio en una máquina de trabajo. El despliegue real (VPS
`coderesearch.space`) es otra cosa: systemd + nginx, documentado en
[`studio/docs/README.md`](../../studio/docs/README.md). Esto es solo para
desarrollar.

La diferencia de fondo: en el VPS hay un usuario `manimstudio` sin privilegios,
un runner corriendo como root y el repo en `/var/www/codeaerospace_contenido`.
En local no existe nada de eso — los tres procesos corren como tu usuario y el
repo está donde lo hayas clonado. Todo lo que cambia entre ambos entornos pasa
por variables `MS_*`; no hay ramas de código separadas.

## Requisitos

| Pieza | Versión probada | Nota |
|---|---|---|
| Python (host) | 3.14.4 | solo para el backend; el render usa el del contenedor |
| Node | 24.18 | |
| Docker | 29.6 + Compose v5.3 | tu usuario debe estar en el grupo `docker` |
| Python (imagen) | 3.12.11 | fijado por el `Dockerfile` |
| Manim Community | 0.20.1 | dentro de la imagen |

El backend corre sobre el Python del host y solo necesita las dependencias de
`studio/backend/requirements.txt` (FastAPI, uvicorn, bcrypt, psutil…). Manim,
LaTeX y ffmpeg **no** se instalan en el host: viven en la imagen de render.

## Puesta en marcha

```bash
git clone https://github.com/trimaxlan98/codeaerospace_contenido
cd codeaerospace_contenido
```

### 1. Backend

```bash
cd studio/backend
python3 -m venv venv          # ver "venv en Debian/Ubuntu" más abajo
venv/bin/pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
```

Rellena el `.env`. Los tres obligatorios (sin ellos el proceso no arranca, por
diseño de `app/config.py`):

```bash
venv/bin/python -c "import bcrypt;print(bcrypt.hashpw(b'TU_PASSWORD', bcrypt.gensalt(12)).decode())"
venv/bin/python -c "import secrets;print(secrets.token_hex(32))"
```

```ini
MS_ADMIN_USER=admin
MS_ADMIN_PASSWORD_HASH='$2b$12$...'   # ← comillas simples, ver abajo
MS_SECRET_KEY=<token_hex(32)>

MS_WORKSPACE=/ruta/absoluta/al/clon
MS_DB_PATH=/ruta/absoluta/al/clon/studio/backend/manimstudio.db
MS_RUNNER_SOCKET=/ruta/absoluta/al/clon/.run/runner.sock
MS_COOKIE_SECURE=0                    # ← obligatorio en http://localhost
```

**Las comillas simples del hash no son opcionales.** bcrypt genera
`$2b$12$...` y `source .env` en bash expande cada `$…` como variable, dejando
un hash truncado. El síntoma es un 401 con la contraseña correcta y ningún
error en el log. systemd (`EnvironmentFile`) también quita las comillas
simples, así que el mismo `.env` sirve en ambos entornos.

`MS_COOKIE_SECURE=0` es igual de necesario: con el default (`1`) el navegador
descarta la cookie de sesión sobre HTTP y el login "funciona" pero nunca queda
autenticado.

### 2. Frontend

```bash
cd studio/frontend && npm ci
```

En dev se usa el servidor de Vite (puerto 5173), que ya trae el proxy de `/api`
hacia `127.0.0.1:3002` configurado en `vite.config.js`. En producción nginx
sirve `dist/` estático; no hace falta `vite build` para desarrollar.

### 3. Imagen de render

```bash
docker compose build manim
```

Tarda unos minutos (arrastra `texlive` completo) y pesa ~1.4 GB. El servicio
`manim-render` del compose reutiliza esta misma imagen.

### 4. Arrancar

```bash
studio/dev.sh
```

Levanta runner + backend + Vite y los tumba juntos con Ctrl-C. Luego
<http://127.0.0.1:5173>.

A mano, si prefieres cada proceso en su terminal:

```bash
# runner (necesita MS_WORKSPACE y MS_RUNNER_SOCKET en el entorno)
studio/backend/venv/bin/python studio/runner/manim_runner.py

# backend
cd studio/backend && set -a && . ./.env && set +a && \
  venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 3002 --reload

# frontend
cd studio/frontend && npx vite
```

## El runner en local

Es la única pieza que no es idéntica entre entornos. En el VPS corre como root
porque necesita el socket de Docker, y ajusta el socket Unix a
`root:manimstudio 0660` para que el backend sin privilegios pueda hablarle.

En local nada de eso aplica: tu usuario ya está en el grupo `docker`, no existe
el grupo `manimstudio` y no hay root. El runner detecta la situación y cae a un
socket `0600` propiedad de tu usuario — que es el mismo que corre el backend,
así que el permiso sigue siendo correcto. Lo verás en su log:

```
manim-runner escuchando en …/.run/runner.sock (modo dev, solo el usuario actual: …)
```

Variables que acepta (los defaults son los del VPS, y systemd no le pasa
ninguna, así que producción no cambia):

| Variable | Default | Para qué |
|---|---|---|
| `MS_WORKSPACE` | `/var/www/codeaerospace_contenido` | raíz del repo |
| `MS_COMPOSE_FILE` | `$MS_WORKSPACE/docker-compose.yml` | compose a invocar |
| `MS_RUNNER_SOCKET` | `/run/manimstudio/runner.sock` | socket de control |
| `MS_RUNNER_USER` | `manimstudio` | uid:gid de los contenedores de render |
| `MS_RUNNER_SOCKET_GROUP` | `manimstudio` | grupo dueño del socket |

**Sin el runner la app arranca igual**: la UI, las lecciones y la biblioteca
funcionan, y los renders fallan con `runner no disponible: [Errno 2]…` en vez
de tumbar nada. Es un modo válido para trabajar solo en frontend.

## Tests

```bash
cd studio/backend && venv/bin/python -m pytest tests/ -q
```

86 tests, ~21 s. No tocan Docker ni la API de Vertex (los de IA mockean el
cliente) y corren sobre un workspace temporal, así que son seguros con la app
levantada.

## Problemas conocidos

**`ensurepip is not available` al crear el venv.** Debian y Ubuntu parten la
stdlib: `python3 -m venv` necesita el paquete `python3.X-venv`, que no viene
con el intérprete. O lo instalas (`sudo apt install python3.14-venv`, ajustando
la versión) o usas `virtualenv`, que no depende de ensurepip:

```bash
virtualenv -q venv && venv/bin/pip install -r requirements.txt
```

**Login que devuelve 401 con la contraseña correcta.** Casi siempre es el hash
sin comillas simples en el `.env` (ver arriba). Compruébalo con:

```bash
set -a && . studio/backend/.env && set +a && echo "$MS_ADMIN_PASSWORD_HASH"
```

Si no ves los tres `$` del formato `$2b$12$…`, ese es el problema.

**Login que devuelve 200 pero `/api/me` sigue en `authenticated:false`.** Falta
`MS_COOKIE_SECURE=0`.

**El asistente IA no aparece.** Es un feature-flag, no un fallo: sin
`gcp-key.json` (Vertex) la UI de IA se oculta, y sin `MS_ANTHROPIC_API_KEY` se
oculta la de primitivas con Fable 5. `/api/me` te dice el estado en
`ai_enabled` y `fable_enabled`.

## Rendimiento

Medido en una laptop de 4 núcleos: qué tarda un render, por qué subir el límite
de CPU del compose no sirve, y cuál es la palanca que sí. Ver
[`rendimiento.md`](rendimiento.md).
