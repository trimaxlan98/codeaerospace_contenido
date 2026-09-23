// Puente minimo entre la interfaz de la app y el proceso principal. El
// Estudio (webview) NO recibe este preload: solo la ventana de la app.
const { contextBridge, ipcRenderer } = require('electron');

const on = (channel) => (fn) => {
  const handler = (_e, ...args) => fn(...args);
  ipcRenderer.on(channel, handler);
  return () => ipcRenderer.removeListener(channel, handler);
};

contextBridge.exposeInMainWorld('studio', {
  info: () => ipcRenderer.invoke('app:info'),
  chooseRepo: () => ipcRenderer.invoke('config:chooseRepo'),
  setConfig: (patch) => ipcRenderer.invoke('config:set', patch),

  services: {
    status: () => ipcRenderer.invoke('services:status'),
    start: () => ipcRenderer.invoke('services:start'),
    stop: () => ipcRenderer.invoke('services:stop'),
    restart: () => ipcRenderer.invoke('services:restart'),
    check: () => ipcRenderer.invoke('services:check'),
    onState: on('services:state'),
    onLog: on('services:log'),
  },
  system: () => ipcRenderer.invoke('system:info'),

  exports: {
    catalog: (refresh) => ipcRenderer.invoke('exports:catalog', !!refresh),
    list: (rel) => ipcRenderer.invoke('exports:list', rel),
    open: (rel) => ipcRenderer.invoke('exports:open', rel),
    reveal: (rel) => ipcRenderer.invoke('exports:reveal', rel),
    copyPath: (rel) => ipcRenderer.invoke('exports:copyPath', rel),
  },
  openRepo: () => ipcRenderer.invoke('shell:openRepo'),
  openExternal: (url) => ipcRenderer.invoke('shell:openExternal', url),

  term: {
    create: (opts) => ipcRenderer.invoke('term:create', opts),
    write: (id, data) => ipcRenderer.send('term:write', id, data),
    resize: (id, cols, rows) => ipcRenderer.send('term:resize', id, cols, rows),
    kill: (id) => ipcRenderer.send('term:kill', id),
    onData: on('term:data'),
    onExit: on('term:exit'),
  },
});
