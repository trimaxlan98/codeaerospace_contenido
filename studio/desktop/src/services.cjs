// Supervisor de runner + backend (scripts/servicios.sh).
//
// Linux:   bash servicios.sh run, en su propio grupo de procesos.
// Windows: wsl.exe -d <distro> --cd <repo> -- bash servicios.sh run.
//
// Si al arrancar ya hay un backend sano en el puerto (studio/dev.sh abierto
// en otra terminal, o una sesion anterior que se dejo viva), se reutiliza y
// la app no lo toca al salir: no es suyo.
const { spawn, execFile } = require('node:child_process');
const http = require('node:http');
const { EventEmitter } = require('node:events');

const SCRIPT = 'studio/desktop/scripts/servicios.sh';
const MAX_LOG = 2000;

function health(port) {
  return new Promise((resolve) => {
    const req = http.get({ host: '127.0.0.1', port, path: '/api/health', timeout: 1500 }, (res) => {
      let body = '';
      res.on('data', (c) => (body += c));
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch {
          resolve(null);
        }
      });
    });
    req.on('error', () => resolve(null));
    req.on('timeout', () => {
      req.destroy();
      resolve(null);
    });
  });
}

class Services extends EventEmitter {
  constructor(config) {
    super();
    this.config = config;
    this.child = null;
    this.owned = false; // true solo si los arranco esta app
    this.state = 'stopped'; // stopped | starting | running | external | error
    this.detail = '';
    this.log = [];
  }

  get apiPort() {
    return this.config.get('ports').api;
  }

  push(line) {
    for (const l of String(line).split(/\r?\n/)) {
      if (!l) continue;
      this.log.push(l);
      this.emit('log', l);
    }
    if (this.log.length > MAX_LOG) this.log.splice(0, this.log.length - MAX_LOG);
  }

  setState(state, detail = '') {
    this.state = state;
    this.detail = detail;
    this.emit('state', this.status());
  }

  status() {
    return { state: this.state, detail: this.detail, owned: this.owned, apiPort: this.apiPort };
  }

  command(action) {
    const rt = this.config.get('runtime');
    if (rt.mode === 'wsl') {
      return {
        file: 'wsl.exe',
        args: ['-d', rt.distro, '--cd', rt.linuxRepo, '--', 'bash', SCRIPT, action],
        opts: { windowsHide: true },
      };
    }
    return { file: 'bash', args: [SCRIPT, action], opts: { cwd: this.config.get('repoPath') } };
  }

  async start() {
    if (this.child) return this.status();
    const h = await health(this.apiPort);
    if (h?.ok) {
      this.owned = false;
      this.push(`[app] backend ya activo en :${this.apiPort}; se reutiliza`);
      this.setState('external', h.runner ? '' : 'el runner no responde');
      return this.status();
    }

    this.setState('starting');
    const { file, args, opts } = this.command('run');
    const env = { ...process.env, CODE_STUDIO_API_PORT: String(this.apiPort) };
    this.child = spawn(file, args, { ...opts, env, detached: process.platform !== 'win32' });
    this.owned = true;
    this.child.stdout.on('data', (d) => this.push(d.toString()));
    this.child.stderr.on('data', (d) => this.push(d.toString()));
    this.child.on('exit', (code, signal) => {
      this.push(`[app] servicios terminaron (code=${code} signal=${signal ?? '-'})`);
      this.child = null;
      if (this.state !== 'stopped') this.setState('error', `los servicios se cerraron (código ${code})`);
    });
    this.child.on('error', (err) => {
      this.push(`[app] no se pudo lanzar ${file}: ${err.message}`);
      this.child = null;
      this.setState('error', err.message);
    });

    const t0 = Date.now();
    while (Date.now() - t0 < 30000) {
      if (!this.child) return this.status();
      const r = await health(this.apiPort);
      if (r?.ok) {
        this.setState('running', r.runner ? '' : 'el runner no responde');
        return this.status();
      }
      await new Promise((ok) => setTimeout(ok, 400));
    }
    this.setState('error', 'el backend no respondió en 30 s — revisa el registro');
    return this.status();
  }

  async stop() {
    if (!this.owned) {
      this.setState(this.state === 'external' ? 'external' : 'stopped');
      return this.status();
    }
    this.setState('stopped');
    const child = this.child;
    // `stop` del script mata por pidfile: funciona igual dentro de WSL, donde
    // matar wsl.exe no garantiza que la senal llegue al bash de dentro.
    await new Promise((resolve) => {
      const { file, args, opts } = this.command('stop');
      execFile(file, args, { ...opts, timeout: 10000 }, () => resolve());
    });
    if (child && process.platform !== 'win32') {
      try {
        process.kill(-child.pid, 'SIGTERM');
      } catch {
        /* ya no existe */
      }
    }
    this.owned = false;
    return this.status();
  }

  async restart() {
    await this.stop();
    await new Promise((ok) => setTimeout(ok, 800));
    return this.start();
  }

  check() {
    return new Promise((resolve) => {
      const { file, args, opts } = this.command('check');
      execFile(file, args, { ...opts, timeout: 20000 }, (err, stdout, stderr) => {
        resolve({ ok: !err, output: (stdout + stderr).trim() });
      });
    });
  }

  health() {
    return health(this.apiPort);
  }
}

module.exports = { Services, health };
