// CO.DE Studio — ManimStudio de escritorio.
//
// Orquesta un checkout real de codeaerospace_contenido: levanta runner +
// backend (scripts/servicios.sh), sirve la interfaz compilada con proxy a
// /api (localServer.cjs), cataloga exports/ por tema y proyecto
// (exports.cjs) y abre terminales con Claude Code en el repo (terminal.cjs).
const { app, BrowserWindow, dialog, ipcMain, shell, clipboard, Menu } = require('electron');
const path = require('node:path');
const fs = require('node:fs');
const os = require('node:os');
const { execFile } = require('node:child_process');

const { Config, isRepo } = require('./config.cjs');
const { Services } = require('./services.cjs');
const { createLocalServer } = require('./localServer.cjs');
const { catalogar, listar } = require('./exports.cjs');
const { Terminals, TAREAS } = require('./terminal.cjs');

const PROD_URL = 'https://coderesearch.space';
const ABRIBLES = new Set([
  '.mp4', '.mov', '.webm', '.mkv', '.wav', '.mp3', '.m4a', '.flac', '.ogg',
  '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.pptx', '.pdf', '.docx',
  '.txt', '.md', '.json', '.srt', '.csv',
]);
const ICON = path.join(__dirname, '..', 'build', 'icon.png');

if (!app.requestSingleInstanceLock()) {
  app.quit();
  process.exit(0);
}

const config = new Config(path.join(app.getPath('userData'), 'config.json'));
let win = null;
let services = null;
let terminals = null;
let local = null;
let uiUrl = null;
let catalogCache = null;
let quitting = false;

function send(channel, ...args) {
  if (win && !win.isDestroyed()) win.webContents.send(channel, ...args);
}

const repo = () => config.get('repoPath');
const exportsDir = () => (repo() ? path.join(repo(), 'exports') : null);

/** Resuelve `rel` dentro de exports/ (sigue el enlace al disco de datos). */
function exportsPath(rel) {
  const base = fs.realpathSync(exportsDir());
  const full = fs.realpathSync(path.resolve(base, rel || '.'));
  if (full !== base && !full.startsWith(base + path.sep)) throw new Error('Ruta fuera de exports');
  return full;
}

function run(file, args, timeout = 8000) {
  return new Promise((resolve) => {
    execFile(file, args, { timeout, windowsHide: true }, (err, stdout) =>
      resolve(err ? null : String(stdout).trim())
    );
  });
}

function newestMtime(paths) {
  let max = 0;
  const walk = (p) => {
    let st;
    try {
      st = fs.statSync(p);
    } catch {
      return;
    }
    if (st.isDirectory()) fs.readdirSync(p).forEach((f) => walk(path.join(p, f)));
    else max = Math.max(max, st.mtimeMs);
  };
  paths.forEach(walk);
  return max || null;
}

/** docker/nvidia-smi: en Windows, docker se consulta dentro de WSL. */
function runtimeCmd(file, args) {
  const rt = config.get('runtime');
  if (rt.mode === 'wsl' && file !== 'nvidia-smi') return run('wsl.exe', ['-d', rt.distro, '--', file, ...args]);
  return run(file, args);
}

async function systemInfo() {
  const [docker, image, gpu] = await Promise.all([
    runtimeCmd('docker', ['info', '--format', '{{.ServerVersion}}']),
    runtimeCmd('docker', ['image', 'inspect', '--format', '{{.Size}}', 'codeaerospace_contenido-manim']),
    run('nvidia-smi', ['--query-gpu=name,memory.total,driver_version', '--format=csv,noheader']),
  ]);
  let disco = null;
  try {
    const st = fs.statfsSync(exportsPath('.'));
    disco = { libre: st.bavail * st.bsize, total: st.blocks * st.bsize };
  } catch {
    /* sin exports todavia */
  }
  const front = repo() && path.join(repo(), 'studio', 'frontend');
  const dist = front && path.join(front, 'dist', 'index.html');
  return {
    docker,
    imagen: image ? Number(image) : null,
    gpu,
    disco,
    uiCompilada: dist && fs.existsSync(dist) ? fs.statSync(dist).mtimeMs : null,
    // Lo mas reciente del codigo de la interfaz: si es posterior al dist, la
    // app esta sirviendo una interfaz vieja (p. ej. tras un `git pull`).
    uiFuente: front ? newestMtime([path.join(front, 'src'), path.join(front, 'index.html')]) : null,
    cpu: os.cpus()[0]?.model,
    nucleos: os.cpus().length,
    memoria: os.totalmem(),
    so: `${os.type()} ${os.release()}`,
  };
}

function registerIpc() {
  ipcMain.handle('app:info', () => ({
    version: app.getVersion(),
    platform: process.platform,
    repo: repo(),
    exportsDir: exportsDir(),
    uiUrl,
    prodUrl: PROD_URL,
    mediaToken: local?.token,
    runtime: config.get('runtime'),
    stopServicesOnQuit: config.get('stopServicesOnQuit'),
    tareas: Object.fromEntries(Object.entries(TAREAS).map(([k, v]) => [k, v.titulo])),
  }));

  ipcMain.handle('config:chooseRepo', async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog(win, {
      title: 'Selecciona el checkout de codeaerospace_contenido',
      properties: ['openDirectory'],
    });
    if (canceled || !filePaths[0]) return { ok: false };
    if (!isRepo(filePaths[0])) {
      return { ok: false, error: 'Esa carpeta no contiene studio/backend ni studio/runner.' };
    }
    config.set({ repoPath: filePaths[0] });
    app.relaunch();
    quitting = true;
    await services?.stop();
    app.exit(0);
    return { ok: true };
  });

  ipcMain.handle('config:set', (_e, patch) => {
    const allowed = {};
    if (typeof patch?.stopServicesOnQuit === 'boolean') allowed.stopServicesOnQuit = patch.stopServicesOnQuit;
    if (patch?.runtime && typeof patch.runtime === 'object') {
      allowed.runtime = { ...config.get('runtime') };
      for (const k of ['distro', 'linuxRepo']) {
        if (typeof patch.runtime[k] === 'string') allowed.runtime[k] = patch.runtime[k];
      }
    }
    config.set(allowed);
    return true;
  });

  ipcMain.handle('services:status', () => ({ ...services.status(), log: services.log.slice(-400) }));
  ipcMain.handle('services:start', () => services.start());
  ipcMain.handle('services:stop', () => services.stop());
  ipcMain.handle('services:restart', () => services.restart());
  ipcMain.handle('services:check', () => services.check());
  ipcMain.handle('system:info', () => systemInfo());

  ipcMain.handle('exports:catalog', async (_e, refresh) => {
    if (!exportsDir()) return null;
    if (!catalogCache || refresh) catalogCache = await catalogar(repo(), exportsDir());
    return catalogCache;
  });
  ipcMain.handle('exports:list', (_e, rel) => listar(exportsDir(), String(rel || '')));
  ipcMain.handle('exports:open', async (_e, rel) => {
    const full = exportsPath(String(rel || ''));
    // Solo medios y documentos: exports/ tambien guarda scripts (mux.sh) y
    // "abrir" un script con la aplicacion del sistema puede ejecutarlo.
    if (!fs.statSync(full).isDirectory() && !ABRIBLES.has(path.extname(full).toLowerCase())) {
      return { ok: false, error: 'Ese tipo de archivo no se abre desde la app; usa «Mostrar en carpeta».' };
    }
    const err = await shell.openPath(full);
    return err ? { ok: false, error: err } : { ok: true };
  });
  ipcMain.handle('exports:reveal', (_e, rel) => {
    const full = exportsPath(String(rel || ''));
    if (fs.statSync(full).isDirectory()) shell.openPath(full);
    else shell.showItemInFolder(full);
    return true;
  });
  ipcMain.handle('exports:copyPath', (_e, rel) => {
    const full = exportsPath(String(rel || ''));
    clipboard.writeText(full);
    return full;
  });

  ipcMain.handle('shell:openRepo', () => repo() && shell.openPath(repo()));
  ipcMain.handle('shell:openExternal', (_e, url) => {
    if (/^https?:\/\//.test(String(url))) shell.openExternal(String(url));
  });

  ipcMain.handle('term:create', (_e, opts) => terminals.create(opts || {}));
  ipcMain.on('term:write', (_e, id, data) => terminals.write(id, data));
  ipcMain.on('term:resize', (_e, id, cols, rows) => terminals.resize(id, cols, rows));
  ipcMain.on('term:kill', (_e, id) => terminals.kill(id));
}

function createWindow() {
  const saved = config.get('window') || {};
  win = new BrowserWindow({
    width: saved.width || 1560,
    height: saved.height || 980,
    x: saved.x,
    y: saved.y,
    minWidth: 1080,
    minHeight: 680,
    backgroundColor: '#05070a',
    title: 'CO.DE Studio',
    icon: ICON,
    autoHideMenuBar: true,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webviewTag: true,
    },
  });
  if (saved.maximized) win.maximize();
  win.once('ready-to-show', () => win.show());

  const persistBounds = () => {
    if (!win || win.isDestroyed()) return;
    config.set({ window: { ...win.getNormalBounds(), maximized: win.isMaximized() } });
  };
  win.on('close', persistBounds);

  // El webview del Estudio: sin preload ni Node, y solo hacia el Estudio
  // local o el de produccion.
  win.webContents.on('will-attach-webview', (event, prefs, params) => {
    delete prefs.preload;
    prefs.nodeIntegration = false;
    prefs.contextIsolation = true;
    prefs.sandbox = true;
    if (!(params.src.startsWith(uiUrl) || params.src.startsWith(PROD_URL))) event.preventDefault();
  });

  win.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
}

app.on('web-contents-created', (_e, contents) => {
  // Enlaces que abren ventana nueva (docs, GitHub...) -> navegador del sistema.
  contents.setWindowOpenHandler(({ url }) => {
    if (/^https?:\/\//.test(url)) shell.openExternal(url);
    return { action: 'deny' };
  });
  if (contents.getType() === 'window') {
    contents.on('will-navigate', (ev) => ev.preventDefault());
  }
});

app.on('second-instance', () => {
  if (win) {
    if (win.isMinimized()) win.restore();
    win.focus();
  }
});

app.whenReady().then(async () => {
  Menu.setApplicationMenu(null);
  const found = config.resolveRepo();
  if (found && found !== config.get('repoPath')) config.set({ repoPath: found });

  services = new Services(config);
  services.on('state', (s) => send('services:state', s));
  services.on('log', (l) => send('services:log', l));
  terminals = new Terminals({ config, send });

  local = createLocalServer({
    getDist: () => repo() && path.join(repo(), 'studio', 'frontend', 'dist'),
    getExports: () => exportsDir(),
    apiPort: () => config.get('ports').api,
  });
  let port;
  try {
    port = await local.listen(config.get('ports').ui);
  } catch {
    port = await local.listen(0); // el puerto preferido esta ocupado
  }
  uiUrl = `http://127.0.0.1:${port}`;

  registerIpc();
  createWindow();
  if (repo()) services.start();
});

app.on('before-quit', async (event) => {
  if (quitting) return;
  event.preventDefault();

  if (terminals?.count()) {
    const { response } = await dialog.showMessageBox(win, {
      type: 'question',
      buttons: ['Cerrar de todos modos', 'Cancelar'],
      defaultId: 1,
      cancelId: 1,
      title: 'Hay terminales abiertas',
      message: `Hay ${terminals.count()} terminal(es) abierta(s).`,
      detail: 'Si Claude Code está generando un curso en alguna, se interrumpirá.',
    });
    if (response === 1) return;
  }
  quitting = true;
  terminals?.killAll();
  if (config.get('stopServicesOnQuit')) await services?.stop();
  local?.close();
  app.exit(0);
});

app.on('window-all-closed', () => app.quit());

// Cierre de sesion / apagado: sin esto Electron sale sin pasar por
// before-quit y runner + backend quedarian huerfanos en su grupo de procesos.
for (const sig of ['SIGTERM', 'SIGINT', 'SIGHUP']) {
  process.on(sig, async () => {
    if (quitting) return;
    quitting = true;
    terminals?.killAll();
    if (config.get('stopServicesOnQuit')) await services?.stop();
    app.exit(0);
  });
}
