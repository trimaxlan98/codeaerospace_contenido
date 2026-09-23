// Terminales integradas (node-pty) y tareas del repo.
//
// Toda orden que no sea una shell vacia se escribe primero como script en
// .run/desktop/tareas/ (gitignorado) y la pty ejecuta `bash -l <script>`.
// Asi el prompt de un curso —con comillas, saltos de linea, acentos— nunca
// pasa por el escapado de una linea de comandos, que en Windows (wsl.exe)
// sigue otras reglas que en Linux. Al terminar, el script deja una shell
// abierta en el repo para seguir trabajando en la misma pestaña.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

let pty = null;
function loadPty() {
  if (!pty) pty = require('@lydell/node-pty');
  return pty;
}

// Tareas fijas del repo. `cmd` se ejecuta con el repo como directorio actual.
const TAREAS = {
  'ui-build': {
    titulo: 'Recompilar interfaz',
    cmd: 'cd studio/frontend && { [ -d node_modules ] || npm ci --no-audit --no-fund; } && npm run build',
  },
  'docker-build': { titulo: 'Construir imagen de render', cmd: 'docker compose build manim' },
  'check': { titulo: 'Verificar requisitos', cmd: 'bash studio/desktop/scripts/servicios.sh check' },
  'inventario': {
    titulo: 'Inventariar exports',
    cmd: 'bash studio/tools/inventariar_exports.sh && bash studio/tools/snapshot_exports.sh',
  },
  'tests': { titulo: 'Tests del backend', cmd: 'cd studio/backend && venv/bin/python -m pytest -q' },
  'git': { titulo: 'Estado de git', cmd: 'git status -sb && echo && git log --oneline -12' },
  'claude': { titulo: 'Claude Code', cmd: 'claude' },
  'claude-continue': { titulo: 'Claude · continuar', cmd: 'claude --continue' },
};

const MODOS = new Set(['manual', 'acceptEdits', 'auto', 'plan']);

// Marcadores que deja una sesion de Claude Code en el entorno de sus hijos.
// Si la app se lanzo desde una (p. ej. `npm start` dentro de Claude Code),
// el `claude` de la terminal se creeria sesion hija: no guardaria su
// transcript y "Continuar sesion" no tendria nada que retomar. La
// configuracion del usuario (CLAUDE_CODE_USE_BEDROCK, etc.) si se hereda.
const MARCADORES_SESION = /^(CLAUDECODE|CLAUDE_PID|CLAUDE_EFFORT|CLAUDE_CODE_(CHILD_SESSION|SESSION_ID|SESSION_ATTENDED|ENTRYPOINT|EXECPATH|MESSAGING_SOCKET|MESSAGING_TOKEN|SSE_PORT))$/;

function entornoLimpio() {
  const env = {};
  for (const [k, v] of Object.entries(process.env)) if (!MARCADORES_SESION.test(k)) env[k] = v;
  return { ...env, TERM: 'xterm-256color', COLORTERM: 'truecolor' };
}

class Terminals {
  constructor({ config, send }) {
    this.config = config;
    this.send = send;
    this.ptys = new Map();
  }

  repo() {
    return this.config.get('repoPath');
  }

  /** Escribe el script de una tarea y devuelve su ruta relativa al repo. */
  writeScript(body) {
    const dir = path.join(this.repo(), '.run', 'desktop', 'tareas');
    fs.mkdirSync(dir, { recursive: true });
    const name = `${Date.now()}-${crypto.randomBytes(3).toString('hex')}.sh`;
    const script = [
      '#!/usr/bin/env bash',
      body,
      'code=$?',
      'printf "\\n\\033[2m── terminó (código %s) · la terminal sigue abierta en el repo ──\\033[0m\\n" "$code"',
      'exec bash -l',
      '',
    ].join('\n');
    fs.writeFileSync(path.join(dir, name), script, { encoding: 'utf-8', mode: 0o755 });
    // Limpia scripts de mas de un dia: son desechables.
    for (const f of fs.readdirSync(dir)) {
      const full = path.join(dir, f);
      try {
        if (Date.now() - fs.statSync(full).mtimeMs > 86400000) fs.unlinkSync(full);
      } catch {
        /* no importa */
      }
    }
    return `.run/desktop/tareas/${name}`;
  }

  spawnSpec(scriptRel, perfil) {
    const rt = this.config.get('runtime');
    if (process.platform === 'win32') {
      if (perfil === 'powershell') return { file: 'powershell.exe', args: ['-NoLogo'], cwd: this.repo() };
      const base = ['-d', rt.distro, '--cd', rt.linuxRepo];
      return { file: 'wsl.exe', args: scriptRel ? [...base, '--', 'bash', '-l', scriptRel] : base, cwd: undefined };
    }
    return { file: 'bash', args: scriptRel ? ['-l', scriptRel] : ['-l'], cwd: this.repo() };
  }

  /**
   * opts: { tarea?, prompt?, modo?, perfil?, cols, rows }
   *   tarea  -> clave de TAREAS
   *   prompt -> lanza `claude` con ese prompt inicial
   */
  create(opts = {}) {
    const { spawn } = loadPty();
    let titulo = 'Terminal';
    let body = null;
    if (opts.prompt) {
      const modo = MODOS.has(opts.modo) ? opts.modo : 'manual';
      const flag = modo === 'manual' ? '' : ` --permission-mode ${modo}`;
      const delim = `__PROMPT_${crypto.randomBytes(4).toString('hex')}__`;
      body = `claude${flag} "$(cat <<'${delim}'\n${opts.prompt}\n${delim}\n)"`;
      titulo = opts.titulo || 'Claude · curso';
    } else if (opts.tarea && TAREAS[opts.tarea]) {
      body = TAREAS[opts.tarea].cmd;
      titulo = TAREAS[opts.tarea].titulo;
    }
    const scriptRel = body ? this.writeScript(body) : null;
    const { file, args, cwd } = this.spawnSpec(scriptRel, opts.perfil);

    const id = crypto.randomUUID();
    const p = spawn(file, args, {
      name: 'xterm-256color',
      cols: opts.cols || 120,
      rows: opts.rows || 32,
      cwd,
      env: entornoLimpio(),
      useConpty: true,
    });
    p.onData((d) => this.send('term:data', id, d));
    p.onExit(({ exitCode }) => {
      this.ptys.delete(id);
      this.send('term:exit', id, exitCode);
    });
    this.ptys.set(id, p);
    return { id, titulo };
  }

  write(id, data) {
    this.ptys.get(id)?.write(data);
  }

  resize(id, cols, rows) {
    try {
      this.ptys.get(id)?.resize(Math.max(2, cols), Math.max(2, rows));
    } catch {
      /* la pty pudo cerrarse entre medias */
    }
  }

  kill(id) {
    try {
      this.ptys.get(id)?.kill();
    } catch {
      /* ya cerrada */
    }
    this.ptys.delete(id);
  }

  killAll() {
    for (const id of [...this.ptys.keys()]) this.kill(id);
  }

  count() {
    return this.ptys.size;
  }
}

module.exports = { Terminals, TAREAS };
