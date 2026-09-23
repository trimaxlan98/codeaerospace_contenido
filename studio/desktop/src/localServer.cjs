// Servidor local de la app (solo 127.0.0.1):
//
//   /api/*          proxy al backend FastAPI (incluye SSE: se hace pipe sin
//                   bufferizar, por eso no se usa un proxy de alto nivel)
//   /__media/<rel>  archivos de exports/ con soporte de Range (seek de video),
//                   protegidos por un token aleatorio por sesion y encerrados
//                   en la raiz real de exports
//   /*              studio/frontend/dist, con fallback a index.html (SPA)
//
// Es lo que en produccion hace nginx.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json',
  '.webmanifest': 'application/manifest+json',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.mp4': 'video/mp4',
  '.webm': 'video/webm',
  '.mov': 'video/quicktime',
  '.wav': 'audio/wav',
  '.mp3': 'audio/mpeg',
  '.m4a': 'audio/mp4',
  '.ogg': 'audio/ogg',
  '.flac': 'audio/flac',
  '.pdf': 'application/pdf',
  '.txt': 'text/plain; charset=utf-8',
  '.md': 'text/plain; charset=utf-8',
  '.srt': 'text/plain; charset=utf-8',
};

/** Resuelve `rel` dentro de `root` o devuelve null si se escapa. */
function jail(root, rel) {
  let realRoot;
  try {
    realRoot = fs.realpathSync(root);
  } catch {
    return null;
  }
  const full = path.resolve(realRoot, rel);
  let real;
  try {
    real = fs.realpathSync(full);
  } catch {
    return null;
  }
  return real === realRoot || real.startsWith(realRoot + path.sep) ? real : null;
}

function sendFile(req, res, file) {
  let stat;
  try {
    stat = fs.statSync(file);
  } catch {
    res.writeHead(404).end();
    return;
  }
  if (!stat.isFile()) {
    res.writeHead(404).end();
    return;
  }
  const type = MIME[path.extname(file).toLowerCase()] || 'application/octet-stream';
  const range = /^bytes=(\d*)-(\d*)$/.exec(req.headers.range || '');
  if (range) {
    let start = range[1] === '' ? stat.size - Number(range[2]) : Number(range[1]);
    let end = range[1] !== '' && range[2] !== '' ? Number(range[2]) : stat.size - 1;
    start = Math.max(0, start);
    end = Math.min(end, stat.size - 1);
    if (start > end) {
      res.writeHead(416, { 'Content-Range': `bytes */${stat.size}` }).end();
      return;
    }
    res.writeHead(206, {
      'Content-Type': type,
      'Content-Length': end - start + 1,
      'Content-Range': `bytes ${start}-${end}/${stat.size}`,
      'Accept-Ranges': 'bytes',
    });
    fs.createReadStream(file, { start, end }).pipe(res);
    return;
  }
  res.writeHead(200, { 'Content-Type': type, 'Content-Length': stat.size, 'Accept-Ranges': 'bytes' });
  if (req.method === 'HEAD') res.end();
  else fs.createReadStream(file).pipe(res);
}

function proxy(req, res, apiPort) {
  const upstream = http.request(
    { host: '127.0.0.1', port: apiPort, path: req.url, method: req.method, headers: req.headers },
    (up) => {
      res.writeHead(up.statusCode, up.headers);
      up.pipe(res);
    }
  );
  upstream.on('error', () => {
    if (!res.headersSent) res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ detail: 'El backend local no responde. Revisa la pestaña Sistema.' }));
  });
  req.pipe(upstream);
}

function createLocalServer({ getDist, getExports, apiPort }) {
  const token = crypto.randomBytes(16).toString('hex');

  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://127.0.0.1');
    let pathname;
    try {
      pathname = decodeURIComponent(url.pathname);
    } catch {
      return res.writeHead(400).end(); // %-escape roto: sin esto, el servidor caeria
    }

    if (pathname === '/api' || pathname.startsWith('/api/')) return proxy(req, res, apiPort());

    if (pathname.startsWith('/__media/')) {
      if (url.searchParams.get('t') !== token) return res.writeHead(403).end();
      const root = getExports();
      const file = root && jail(root, pathname.slice('/__media/'.length));
      if (!file) return res.writeHead(404).end();
      return sendFile(req, res, file);
    }

    const dist = getDist();
    if (!dist || !fs.existsSync(path.join(dist, 'index.html'))) {
      res.writeHead(503, { 'Content-Type': 'text/html; charset=utf-8' });
      return res.end(
        '<body style="background:#05070a;color:#e6eaf2;font:15px system-ui;padding:40px">' +
          '<h2>La interfaz no está compilada</h2><p>Falta <code>studio/frontend/dist</code>. ' +
          'Ábrela desde la pestaña <b>Sistema → Recompilar interfaz</b>.</p></body>'
      );
    }
    const file = jail(dist, pathname.replace(/^\/+/, '')) || path.join(dist, 'index.html');
    const target = fs.statSync(file).isDirectory() ? path.join(dist, 'index.html') : file;
    return sendFile(req, res, target);
  });

  return {
    token,
    listen: (port) =>
      new Promise((resolve, reject) => {
        server.once('error', reject);
        server.listen(port, '127.0.0.1', () => resolve(server.address().port));
      }),
    close: () => server.close(),
  };
}

module.exports = { createLocalServer, jail };
