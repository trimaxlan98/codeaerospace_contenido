# Instalar CO.DE Studio en Windows

Guía escrita para que la siga **un agente de Claude Code en la máquina Windows**, paso a paso
y verificando cada uno. Si eres ese agente: lee el documento entero antes de empezar,
ejecuta los pasos en orden y no pases al siguiente si la verificación del anterior falla.

## Encargo para pegarle al agente

En la máquina Windows, abre Claude Code en PowerShell (en cualquier carpeta) y pégale:

> Instala y construye la app de escritorio CO.DE Studio en esta máquina Windows. Las
> instrucciones completas están en el repo `https://github.com/trimaxlan98/codeaerospace_contenido`,
> rama `main`, archivo `studio/desktop/INSTALAR-WINDOWS.md`: léelo entero primero
> (en `https://github.com/trimaxlan98/codeaerospace_contenido/blob/main/studio/desktop/INSTALAR-WINDOWS.md`).
> Sigue los pasos 0 a 5 en orden y verifica cada uno antes de avanzar. Pregúntame la
> contraseña del Estudio local antes del paso 2 y si quiero copiar los exports (paso 6).
> Los pasos que necesiten que yo intervenga (reiniciar tras instalar WSL, crear el usuario de
> Ubuntu, iniciar sesión en Claude Code dentro de WSL) dímelos claramente y espera.
> Al terminar, dame el resultado de `-Paso Verificar` y lo que comprobaste en la app.

La app se construye en esta máquina (paso 4): no hace falta traer ningún instalador desde
Linux.

## Qué se va a instalar y por qué así

CO.DE Studio es la app de escritorio de ManimStudio: el Estudio local, los exports ordenados
por tema y proyecto, y una terminal integrada con Claude Code. En Windows tiene **dos mitades**:

| Mitad | Dónde corre | Qué es |
|---|---|---|
| App de escritorio (Electron) | Windows | ventana, exports, terminal |
| Servicios de ManimStudio | **WSL2 (Ubuntu)** | runner + backend FastAPI + Docker de render |

Los servicios **no pueden** correr en Windows nativo: el runner habla por un socket Unix y
lanza `docker compose run` con un contenedor sin red. Por eso el repo vive **dentro de WSL**
(`~/codeaerospace_contenido`), y la app lo ve como `\\wsl.localhost\Ubuntu\home\<usuario>\codeaerospace_contenido`.
La app arranca los servicios con `wsl.exe` y habla con ellos por `127.0.0.1:3002`.
La terminal integrada abre bash **dentro de WSL**, en el repo: ahí es donde tiene que estar
instalado y con sesión iniciada Claude Code.

Todo lo necesario está en `studio/desktop/scripts/install-windows.ps1`. Este documento dice
cuándo ejecutar cada paso y cómo comprobar que salió bien.

## Datos que hay que pedirle al dueño antes de empezar

1. **Contraseña del Estudio local** (8+ caracteres). Es la del login de la app, usuario `admin`.
   No es la de producción ni tiene que serlo.
2. Si quiere **copiar sus exports** de la máquina Linux (unos 7 GB de cursos terminados) o
   empezar con la carpeta vacía. Ver el paso 6.

No hace falta nada más. No pidas credenciales de GitHub: el repo se clona por HTTPS; si
fuera privado, `git clone` lo dirá y entonces sí hay que pedir que el dueño inicie sesión
con `gh auth login` dentro de WSL.

## Paso 0 — Requisitos de Windows

En PowerShell (no hace falta que sea de administrador salvo para `wsl --install`):

```powershell
wsl --status
node --version     # Node 20 o superior
git --version
```

Si falta algo:

| Falta | Comando | Nota |
|---|---|---|
| WSL | `wsl --install -d Ubuntu` (PowerShell **como administrador**) | pide **reiniciar**; tras reiniciar, Ubuntu pide crear usuario y contraseña: eso lo hace el dueño |
| Node | `winget install OpenJS.NodeJS.LTS` | cerrar y abrir PowerShell después |
| git | `winget install Git.Git` | idem |

Recomendado (evita problemas de puertos entre Windows y WSL): crear `%UserProfile%\.wslconfig` con

```ini
[wsl2]
networkingMode=mirrored
```

y ejecutar `wsl --shutdown`. Con esto, `127.0.0.1` de Windows y de WSL son el mismo.

**Verificación**: `wsl -d Ubuntu -- uname -a` imprime un kernel `...microsoft-standard-WSL2`.

## Paso 1 — Traer el script

El script vive en el repo, que todavía no está en la máquina. Clónalo primero dentro de WSL
(el paso 2 lo detecta y no lo vuelve a clonar):

```powershell
wsl -d Ubuntu -- bash -lc "git clone https://github.com/trimaxlan98/codeaerospace_contenido.git ~/codeaerospace_contenido"
```

La app de escritorio está en `main`. Si hay que probar una rama con cambios a la app,
pasa `-Rama <rama>` a los pasos siguientes.

Copia el script a Windows para ejecutarlo:

```powershell
$repo = "\\wsl.localhost\Ubuntu" + (wsl -d Ubuntu -- bash -lc 'printf %s ~/codeaerospace_contenido').Replace('/', '\')
Copy-Item "$repo\studio\desktop\scripts\install-windows.ps1" $env:TEMP\
cd $env:TEMP
```

## Paso 2 — Preparar WSL (servicios)

```powershell
powershell -ExecutionPolicy Bypass -File .\install-windows.ps1 -Paso PrepararWsl -Password '<la del dueño>'
```

Instala dentro de Ubuntu: paquetes base, **Docker Engine** (no hace falta Docker Desktop),
Node con nvm, el venv del backend, `studio/backend/.env` local (con un secreto aleatorio y el
hash de la contraseña), compila la interfaz del Estudio y construye la **imagen de render**.
Esto último tarda (LaTeX completo: ~5 GB); es normal que pasen 15–30 minutos.

Si Docker se acaba de instalar, el usuario aún no está en el grupo `docker`:

```powershell
wsl --shutdown
```

y vuelve a ejecutar el mismo comando del paso 2 (es idempotente: lo ya hecho se salta).

**Verificación**:

```powershell
powershell -ExecutionPolicy Bypass -File .\install-windows.ps1 -Paso Verificar
```

Todas las líneas de "Dentro de WSL" deben decir `OK`, salvo quizá Claude Code (paso 3).

## Paso 3 — Claude Code dentro de WSL

La terminal de la app abre bash en WSL, así que Claude Code tiene que estar **en WSL**
(tenerlo en Windows no sirve para esto):

```powershell
wsl -d Ubuntu -- bash -lc "npm install -g @anthropic-ai/claude-code && claude --version"
```

El inicio de sesión lo tiene que hacer **el dueño**, porque abre el navegador: pídele que
abra Ubuntu desde el menú Inicio y ejecute `claude` una vez.

**Verificación**: `-Paso Verificar` muestra `OK  Claude Code <versión> (WSL)`.

## Paso 4 — Compilar la app de escritorio

```powershell
powershell -ExecutionPolicy Bypass -File .\install-windows.ps1 -Paso Compilar
```

Copia `studio/desktop` a `%LOCALAPPDATA%\code-studio-build` (compilar sobre `\\wsl.localhost`
es lento y npm falla con enlaces en rutas UNC), instala dependencias, **corre las pruebas**
y genera el instalador NSIS. No necesita Visual Studio: la terminal (`node-pty`) trae
binarios precompilados para Windows.

**Verificación**: termina imprimiendo `Instalador: ...\release\CO.DE Studio Setup 1.0.0.exe`
y `npm test` mostró `pass 8`, `fail 0`.

## Paso 5 — Instalar

```powershell
powershell -ExecutionPolicy Bypass -File .\install-windows.ps1 -Paso Instalar
```

Instala en silencio para el usuario actual (sin administrador), crea el **acceso directo en
el Escritorio** y en el menú Inicio, y escribe `%APPDATA%\CO.DE Studio\config.json` apuntando
al repo de WSL con `runtime.mode = "wsl"`.

**Verificación**:
1. Existe `CO.DE Studio.lnk` en el Escritorio.
2. Al abrirla, la pestaña **Sistema** muestra *Servicios: en marcha*, Docker con versión e
   *Imagen de render* con su tamaño. La GPU aparece si `nvidia-smi` existe en Windows.
3. La pestaña **Estudio** muestra el login de ManimStudio; entra con `admin` y la contraseña
   del paso 2.
4. **Terminal → Claude Code** abre Claude en `~/codeaerospace_contenido`.
5. Desde PowerShell: `Invoke-RestMethod http://127.0.0.1:3002/api/health` devuelve
   `ok: True, runner: True` mientras la app está abierta.

## Paso 6 — Exports (opcional)

La vista Exports lee `~/codeaerospace_contenido/exports` dentro de WSL. En la máquina Linux
original son ~7 GB. Para traerlos, **desde la máquina Linux**:

```bash
rsync -avh --progress ~/data/codeaerospace/exports/ <usuario>@<ip-windows>:/home/<usuario>/codeaerospace_contenido/exports/
```

(requiere `sudo apt install openssh-server` en WSL), o copiarlos con un disco externo a
`\\wsl.localhost\Ubuntu\home\<usuario>\codeaerospace_contenido\exports`. En WSL `exports`
debe ser una **carpeta real**: un enlace simbólico a una ruta absoluta de Linux no se puede
seguir desde Windows y la vista saldría vacía.

`Tareas → Inventariar exports` solo funciona en la máquina Linux original (el script valida
esa ruta a propósito); en Windows ignóralo.

## Si algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Sistema: *Servicios: error* y el registro dice `FALTA ...` | falta un requisito en WSL | `-Paso Verificar` y repetir el paso 2 |
| `permission denied ... docker.sock` en el registro | el usuario no está en el grupo docker todavía | `wsl --shutdown` y abrir la app de nuevo |
| El backend arranca pero el Estudio no carga (502) | puertos WSL↔Windows | configurar `networkingMode=mirrored` (paso 0) y `wsl --shutdown` |
| La app pide elegir la carpeta del repo | falta o está mal `%APPDATA%\CO.DE Studio\config.json` | repetir el paso 5, o en Sistema → *Cambiar repositorio* elegir `\\wsl.localhost\Ubuntu\home\<usuario>\codeaerospace_contenido` |
| Login del Estudio: 401 | contraseña distinta a la del `.env` | borrar `studio/backend/.env` en WSL y repetir el paso 2 con la contraseña correcta |
| *Interfaz: desactualizada* en Sistema | se hizo `git pull` | Sistema → Tareas → *Recompilar interfaz* |
| La terminal dice `claude: command not found` | Claude Code instalado en Windows y no en WSL | paso 3 |

## Actualizar más adelante

Dentro de WSL `git pull` en el repo; después, en PowerShell, `-Paso Compilar` y `-Paso Instalar`
(el instalador reemplaza la versión anterior y conserva la configuración).
