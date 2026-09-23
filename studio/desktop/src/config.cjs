// Configuracion persistente de la app de escritorio.
//
// La app empaquetada NO lleva dentro el repo (las escenas, el backend en
// Python, el venv, la imagen de Docker): es un orquestador de un checkout
// real de codeaerospace_contenido. Lo unico que guarda es donde esta ese
// checkout y como se ejecutan sus servicios.
//
//   runtime.mode = "native"  Linux: los servicios corren en el propio host.
//   runtime.mode = "wsl"     Windows: el runner usa un socket Unix y
//                            `docker compose`, asi que el backend vive dentro
//                            de WSL2 y la app habla con el por localhost.
//                            `repoPath` es entonces la ruta UNC
//                            (\\wsl.localhost\Ubuntu\home\...) y
//                            `runtime.linuxRepo` la misma ruta vista desde WSL.
const fs = require('node:fs');
const path = require('node:path');

const DEFAULTS = {
  repoPath: null,
  runtime: { mode: process.platform === 'win32' ? 'wsl' : 'native', distro: 'Ubuntu', linuxRepo: null },
  ports: { api: 3002, ui: 5190 },
  // Al cerrar: detener los servicios que arranco la app, o dejarlos vivos.
  stopServicesOnQuit: true,
  window: null,
};

function isRepo(dir) {
  return (
    !!dir &&
    fs.existsSync(path.join(dir, 'studio', 'backend', 'app', 'main.py')) &&
    fs.existsSync(path.join(dir, 'studio', 'runner', 'manim_runner.py'))
  );
}

/** Traduce una ruta UNC de WSL (\\wsl.localhost\Distro\home\x) a /home/x. */
function uncToLinux(p) {
  const m = /^\\\\wsl(?:\.localhost|\$)\\([^\\]+)\\(.*)$/i.exec(p || '');
  if (!m) return null;
  return { distro: m[1], path: '/' + m[2].replace(/\\/g, '/') };
}

class Config {
  constructor(file) {
    this.file = file;
    this.data = structuredClone(DEFAULTS);
    try {
      // Sin BOM: un config.json escrito con PowerShell 5.1 lo lleva y JSON.parse falla.
      const saved = JSON.parse(fs.readFileSync(file, 'utf-8').replace(/^\uFEFF/, ''));
      this.data = {
        ...this.data,
        ...saved,
        runtime: { ...this.data.runtime, ...(saved.runtime || {}) },
        ports: { ...this.data.ports, ...(saved.ports || {}) },
      };
    } catch {
      /* primera ejecucion: se queda con los valores por defecto */
    }
  }

  get(key) {
    return this.data[key];
  }

  set(patch) {
    this.data = { ...this.data, ...patch };
    if (this.data.runtime.mode === 'wsl' && this.data.repoPath) {
      const unc = uncToLinux(this.data.repoPath);
      if (unc) this.data.runtime = { ...this.data.runtime, distro: unc.distro, linuxRepo: unc.path };
    }
    fs.mkdirSync(path.dirname(this.file), { recursive: true });
    fs.writeFileSync(this.file, JSON.stringify(this.data, null, 2), 'utf-8');
  }

  /** Busca el checkout: guardado > variable de entorno > junto a la app en desarrollo. */
  resolveRepo() {
    const candidates = [
      this.data.repoPath,
      process.env.CODE_STUDIO_REPO,
      path.resolve(__dirname, '..', '..', '..'),
    ];
    return candidates.find(isRepo) || null;
  }
}

module.exports = { Config, isRepo, uncToLinux };
