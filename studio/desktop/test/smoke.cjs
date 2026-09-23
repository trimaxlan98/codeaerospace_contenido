// Prueba de humo con la app real: arranca, espera a los servicios, recorre
// las cuatro vistas, guarda una captura de cada una y sale.
//
//   CODE_STUDIO_SHOTS=/tmp/shots npx electron test/smoke.cjs --no-sandbox
//
// No es parte de `npm test` (necesita pantalla, Docker y el repo real).
const { app, BrowserWindow } = require('electron');
const fs = require('node:fs');
const path = require('node:path');

const out = process.env.CODE_STUDIO_SHOTS || path.join(require('node:os').tmpdir(), 'code-studio-shots');
fs.mkdirSync(out, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

app.on('browser-window-created', (_e, win) => {
  win.webContents.once('did-finish-load', async () => {
    const js = (code) => win.webContents.executeJavaScript(code);
    const shot = async (name) => {
      const img = await win.webContents.capturePage();
      fs.writeFileSync(path.join(out, `${name}.png`), img.toPNG());
      console.log('[smoke] captura', name);
    };
    try {
      const t0 = Date.now();
      let state = '';
      while (Date.now() - t0 < 40000) {
        state = await js('S.svc.state');
        if (state === 'running' || state === 'external' || state === 'error') break;
        await sleep(500);
      }
      console.log('[smoke] servicios:', state);
      await sleep(5000);
      await shot('1-estudio');

      await js("show('exports')");
      await sleep(1500);
      await js("document.querySelector('.proy').click()");
      await sleep(2000);
      await shot('2-exports');
      const cat = await js('({temas: Exports.cat.temas.length, bytes: Exports.cat.bytes})');
      console.log('[smoke] exports:', JSON.stringify(cat));
      const url = await js("Exports.mediaUrl(Exports.proyecto.rel + '/' + Exports.proyecto.entrega)");
      const media = await new Promise((resolve) =>
        require('node:http')
          .get(url, { headers: { Range: 'bytes=0-99' } }, (r) => {
            r.resume();
            resolve(`${r.statusCode} ${r.headers['content-range']}`);
          })
          .on('error', (e) => resolve(e.message))
      );
      const sinToken = await new Promise((resolve) =>
        require('node:http').get(url.replace(/\?t=.*/, ''), (r) => resolve(r.statusCode))
      );
      console.log('[smoke] media range:', media, '| sin token:', sinToken);

      await js("show('terminal'); Term.open({tarea: 'git'})");
      await sleep(3500);
      await shot('3-terminal');

      await js("show('sistema')");
      await sleep(2500);
      await shot('4-sistema');

      if (process.env.CODE_STUDIO_SMOKE_CLAUDE) {
        // El asistente de curso: se rellena y se captura, pero se CANCELA
        // (su encargo pondria a Claude a producir un curso de verdad).
        await js(`show('terminal'); Curso.open();
          Curso.form.elements.tema.value = 'Mecánica orbital: de Kepler a Hohmann';
          Curso.form.elements.area.value = 'Astronáutica';
          Curso.form.elements.formato.value = 'vertical';
          Curso.form.elements.estilo.value = 'LIENZO';
          Curso.form.querySelector('details').open = true;
          Curso.render();`);
        await sleep(800);
        await shot('5-nuevo-curso');
        await js("Curso.dlg.close('cancel')");
        // Claude Code dentro de la pty, con un prompt inocuo con acentos y
        // salto de linea para comprobar que llega intacto.
        await js(`Term.open({ prompt: 'Responde únicamente con la palabra LISTO.\\nNo uses herramientas.', modo: 'plan', titulo: 'Claude · prueba' })`);
        await sleep(25000);
        await shot('6-claude');
      }

      await js('[...Term.tabs.keys()].forEach((id) => Term.close(id))');
      await sleep(500);
    } catch (err) {
      console.error('[smoke] fallo:', err);
      process.exitCode = 1;
    }
    app.quit();
  });
});

// Carpeta de datos propia: ni la de la app instalada ni la generica de Electron.
app.setName('CO.DE Studio smoke');
require('../src/main.cjs');
