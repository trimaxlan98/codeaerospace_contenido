# install-windows.ps1 — CO.DE Studio en Windows (app nativa + servicios en WSL2).
#
# Guia completa, pensada para que la ejecute un agente: ..\INSTALAR-WINDOWS.md
#
#   powershell -ExecutionPolicy Bypass -File install-windows.ps1 -Paso Verificar
#   powershell -ExecutionPolicy Bypass -File install-windows.ps1 -Paso PrepararWsl
#   powershell -ExecutionPolicy Bypass -File install-windows.ps1 -Paso Compilar
#   powershell -ExecutionPolicy Bypass -File install-windows.ps1 -Paso Instalar
#   powershell -ExecutionPolicy Bypass -File install-windows.ps1 -Paso Todo
#
# Parametros:
#   -Distro   distro de WSL (defecto: Ubuntu)
#   -RepoWsl  ruta del checkout DENTRO de WSL (defecto: ~/codeaerospace_contenido)
#   -RepoUrl  URL de git para clonarlo si no existe
#   -Rama     rama a usar (defecto: main)
#   -Password contraseña del Estudio local, solo si falta studio/backend/.env
#
# Por que asi: el runner de ManimStudio habla por un socket Unix y lanza
# `docker compose`; en Windows eso solo funciona dentro de WSL2. La app de
# escritorio corre en Windows, arranca los servicios con `wsl.exe` y los ve en
# localhost (WSL2 reenvia los puertos). El codigo de la app (Node/Electron) se
# compila en Windows, desde una copia en disco de Windows: node-pty trae
# binarios precompilados para win32-x64, no hace falta Visual Studio.

param(
  [ValidateSet('Verificar', 'PrepararWsl', 'Compilar', 'Instalar', 'Todo')]
  [string]$Paso = 'Verificar',
  [string]$Distro = 'Ubuntu',
  [string]$RepoWsl = '',
  [string]$RepoUrl = 'https://github.com/trimaxlan98/codeaerospace_contenido.git',
  [string]$Rama = 'main',
  # Contraseña del Estudio local (usuario admin). Solo se usa si aun no
  # existe studio/backend/.env dentro de WSL.
  [string]$Password = ''
)

$ErrorActionPreference = 'Stop'
function Paso($t) { Write-Host "`n==> $t" -ForegroundColor Cyan }
function Ok($t) { Write-Host "  OK  $t" -ForegroundColor Green }
function Falta($t) { Write-Host "  FALTA  $t" -ForegroundColor Yellow; $script:faltas++ }

function Wsl([string]$cmd) {
  # bash -lc para que cargue el PATH del usuario (nvm, ~/.local/bin...).
  & wsl.exe -d $Distro -- bash -lc $cmd
  if ($LASTEXITCODE -ne 0) { throw "fallo en WSL: $cmd" }
}

# Como root sin sudo: `sudo` pediria contraseña por teclado y un agente se
# quedaria esperando.
function WslRoot([string]$cmd) {
  & wsl.exe -d $Distro -u root -- bash -lc $cmd
  if ($LASTEXITCODE -ne 0) { throw "fallo en WSL (root): $cmd" }
}

# Los comandos nativos que fallan NO detienen PowerShell por si solos.
function Run([scriptblock]$b, [string]$que) {
  & $b
  if ($LASTEXITCODE -ne 0) { throw "fallo: $que (codigo $LASTEXITCODE)" }
}

function RepoWslPath {
  if ($RepoWsl) { return $RepoWsl }
  $home_ = (& wsl.exe -d $Distro -- bash -lc 'printf %s "$HOME"')
  return "$home_/codeaerospace_contenido"
}

function Verificar {
  $script:faltas = 0
  Paso 'Windows'
  if (Get-Command wsl.exe -ErrorAction SilentlyContinue) { Ok 'wsl.exe' } else { Falta 'WSL: wsl --install (requiere reiniciar)' }
  $distros = (& wsl.exe -l -q 2>$null) -replace "`0", '' | Where-Object { $_.Trim() }
  if ($distros -contains $Distro) { Ok "distro $Distro" } else { Falta "distro ${Distro}: wsl --install -d $Distro" }
  if (Get-Command node.exe -ErrorAction SilentlyContinue) { Ok "Node $(node --version) (Windows)" } else { Falta 'Node.js LTS para Windows: winget install OpenJS.NodeJS.LTS' }
  if (Get-Command git.exe -ErrorAction SilentlyContinue) { Ok 'git (Windows)' } else { Falta 'git para Windows: winget install Git.Git' }
  if (Get-Command nvidia-smi.exe -ErrorAction SilentlyContinue) { Ok "GPU: $(nvidia-smi.exe --query-gpu=name --format=csv,noheader)" } else { Write-Host '  --  sin nvidia-smi (la GPU no es requisito)' }
  if ($distros -contains $Distro) {
    Paso "Dentro de WSL ($Distro)"
    $repo = RepoWslPath
    $check = & wsl.exe -d $Distro -- bash -lc "cd '$repo' 2>/dev/null && bash studio/desktop/scripts/servicios.sh check || echo 'FALTA el repo en $repo'"
    $check | ForEach-Object { if ($_ -match 'FALTA') { Falta $_ } else { Ok $_ } }
    $claude = & wsl.exe -d $Distro -- bash -lc 'command -v claude >/dev/null && claude --version || echo NO'
    if ($claude -ne 'NO') { Ok "Claude Code $claude (WSL)" } else { Falta 'Claude Code en WSL: npm i -g @anthropic-ai/claude-code, luego `claude` para iniciar sesion' }
  }
  Write-Host ''
  if ($script:faltas -eq 0) { Write-Host 'Todo listo.' -ForegroundColor Green } else { Write-Host "$($script:faltas) requisito(s) pendiente(s)." -ForegroundColor Yellow }
}

function PrepararWsl {
  $repo = RepoWslPath
  Paso "Paquetes de sistema en $Distro"
  $usuario = (& wsl.exe -d $Distro -- whoami).Trim()
  WslRoot 'apt-get update && apt-get install -y git curl python3 python3-venv python3-pip rsync build-essential'
  Paso 'Docker dentro de WSL'
  WslRoot "command -v docker >/dev/null || curl -fsSL https://get.docker.com | sh"
  WslRoot "usermod -aG docker '$usuario'"
  # Con systemd (lo normal en Ubuntu de WSL) arranca solo; sin el, se arranca a mano.
  WslRoot 'systemctl enable --now docker 2>/dev/null || service docker start'
  Paso 'Node (nvm) dentro de WSL'
  Wsl 'command -v node >/dev/null || (curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash && . ~/.nvm/nvm.sh && nvm install --lts)'
  Paso "Checkout en $repo"
  Wsl "[ -d '$repo/.git' ] || git clone '$RepoUrl' '$repo'"
  Wsl "cd '$repo' && git fetch origin && git checkout '$Rama' && git pull --ff-only"
  Paso 'Backend: venv y .env local'
  Wsl "cd '$repo/studio/backend' && [ -x venv/bin/python ] || (python3 -m venv venv && venv/bin/pip install -r requirements.txt)"
  $hayEnv = (& wsl.exe -d $Distro -- bash -lc "[ -f '$repo/studio/backend/.env' ] && echo si || echo no").Trim()
  if ($hayEnv -eq 'no') {
    if (-not $Password) { throw 'Falta -Password (contraseña del Estudio local, 8+ caracteres) para crear studio/backend/.env' }
    # WSLENV hace llegar la variable a WSL sin que la contraseña aparezca en la linea de comandos.
    $env:CODE_STUDIO_PASSWORD = $Password
    $env:WSLENV = 'CODE_STUDIO_PASSWORD'
    try { Wsl "cd '$repo' && bash studio/desktop/scripts/crear-env-local.sh" }
    finally { Remove-Item Env:CODE_STUDIO_PASSWORD; Remove-Item Env:WSLENV }
  }
  Paso 'Interfaz del Estudio'
  Wsl "cd '$repo/studio/frontend' && npm ci --no-audit --no-fund && npm run build"
  Paso 'Imagen de render (tarda: LaTeX + Manim, ~5 GB)'
  Wsl "cd '$repo' && sg docker -c 'docker compose build manim'"
  Paso 'Exports'
  Wsl "cd '$repo' && mkdir -p exports render_jobs"
  Write-Host "`nListo. Si Docker se acaba de instalar, ejecuta 'wsl --shutdown' y vuelve a abrir WSL para que el grupo docker tenga efecto."
}

function Compilar {
  # Copia en disco de Windows solo de studio/desktop: compilar Electron sobre
  # \\wsl.localhost es lento y npm tiene problemas con enlaces en UNC.
  $repo = RepoWslPath
  $src = "\\wsl.localhost\$Distro$($repo -replace '/', '\')\studio\desktop"
  $dst = Join-Path $env:LOCALAPPDATA 'code-studio-build'
  Paso "Copiando $src -> $dst"
  if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
  robocopy $src $dst /E /XD node_modules release /NFL /NDL /NJH /NJS | Out-Null
  Push-Location $dst
  try {
    Paso 'npm ci'
    Run { npm ci --no-audit --no-fund } 'npm ci'
    npm approve-scripts electron 2>$null   # solo existe en npm 11+; en npm 10 no hace falta
    Run { node node_modules/electron/install.js } 'descarga de Electron'
    Paso 'Pruebas'
    Run { npm test } 'npm test'
    Paso 'electron-builder --win nsis'
    Run { npx electron-builder --win nsis } 'electron-builder'
    $exe = Get-ChildItem release -Filter '*Setup*.exe' | Select-Object -First 1
    Write-Host "`nInstalador: $($exe.FullName)" -ForegroundColor Green
  } finally { Pop-Location }
}

function Instalar {
  $dst = Join-Path $env:LOCALAPPDATA 'code-studio-build'
  $exe = Get-ChildItem (Join-Path $dst 'release') -Filter '*Setup*.exe' | Select-Object -First 1
  if (-not $exe) { throw 'No hay instalador: ejecuta primero -Paso Compilar' }
  Paso "Instalando $($exe.Name) (crea acceso directo en el Escritorio y el menu Inicio)"
  Start-Process $exe.FullName -ArgumentList '/S' -Wait

  # Primer arranque sin preguntar: apunta la app al checkout de WSL.
  $repo = RepoWslPath
  $cfgDir = Join-Path $env:APPDATA 'CO.DE Studio'
  New-Item -ItemType Directory -Force $cfgDir | Out-Null
  $cfg = [ordered]@{
    repoPath = "\\wsl.localhost\$Distro$($repo -replace '/', '\')"
    runtime  = [ordered]@{ mode = 'wsl'; distro = $Distro; linuxRepo = $repo }
  }
  # UTF-8 SIN BOM: Set-Content -Encoding UTF8 de PowerShell 5.1 antepone un BOM.
  [IO.File]::WriteAllText((Join-Path $cfgDir 'config.json'), ($cfg | ConvertTo-Json), (New-Object Text.UTF8Encoding $false))
  Ok "config: $(Join-Path $cfgDir 'config.json')"
  Write-Host "`nAbre 'CO.DE Studio' desde el Escritorio." -ForegroundColor Green
}

switch ($Paso) {
  'Verificar' { Verificar }
  'PrepararWsl' { PrepararWsl }
  'Compilar' { Compilar }
  'Instalar' { Instalar }
  'Todo' { PrepararWsl; Compilar; Instalar; Verificar }
}
