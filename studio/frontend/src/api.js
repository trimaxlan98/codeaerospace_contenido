// Cliente API — rutas relativas /api, cookies de sesion same-origin.

export class ApiError extends Error {
  constructor(status, detail) {
    super(detail || `HTTP ${status}`)
    this.status = status
  }
}

// Un 401 fuera de /api/login significa sesion expirada: avisar a la app para
// volver al login en vez de dejar una interfaz zombi con errores cripticos.
let onUnauthorized = null
export function setUnauthorizedHandler(fn) { onUnauthorized = fn }

async function request(method, path, body) {
  const res = await fetch(path, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  let data = null
  try { data = await res.json() } catch { /* respuestas no-JSON */ }
  if (res.status === 401 && path !== '/api/login') onUnauthorized?.()
  if (!res.ok) throw new ApiError(res.status, data?.detail)
  return data
}

// Subida de un archivo como cuerpo crudo (sin multipart: el backend no lo
// necesita y asi no hay dependencia extra). Mismo manejo de 401 y errores.
async function subirArchivo(path, file) {
  const res = await fetch(path, {
    method: 'PUT',
    headers: { 'Content-Type': file.type || 'application/octet-stream' },
    body: file,
  })
  let data = null
  try { data = await res.json() } catch { /* respuestas no-JSON */ }
  if (res.status === 401) onUnauthorized?.()
  if (!res.ok) throw new ApiError(res.status, data?.detail)
  return data
}

export const api = {
  me: () => request('GET', '/api/me'),
  login: (username, password) => request('POST', '/api/login', { username, password }),
  logout: () => request('POST', '/api/logout'),
  changePassword: (currentPassword, newPassword) => request('POST', '/api/change-password',
    { current_password: currentPassword, new_password: newPassword }),
  scenes: (script) => request('POST', '/api/scenes', { script }),
  createJob: (payload) => request('POST', '/api/jobs', payload),
  listJobs: () => request('GET', '/api/jobs'),
  getJob: (id) => request('GET', `/api/jobs/${id}`),
  getScript: (id) => request('GET', `/api/jobs/${id}/script`),
  cancelJob: (id) => request('POST', `/api/jobs/${id}/cancel`),
  retryJob: (id) => request('POST', `/api/jobs/${id}/retry`),
  deleteJob: (id) => request('DELETE', `/api/jobs/${id}`),
  deleteFailedJobs: () => request('DELETE', '/api/jobs/failed'),
  deleteFinishedJobs: () => request('DELETE', '/api/jobs/finished'),
  purgeJobsOlderThan: (days) => request('DELETE', `/api/jobs/older-than/${days}`),
  metrics: () => request('GET', '/api/metrics'),
  metricsHistory: () => request('GET', '/api/metrics/history'),
  aiExplain: (payload) => request('POST', '/api/ai/explain', payload),
  aiFix: (payload) => request('POST', '/api/ai/fix', payload),
  aiGenerate: (payload) => request('POST', '/api/ai/generate', payload),
  lessonsIndex: () => request('GET', '/api/lessons'),
  getLesson: (id) => request('GET', `/api/lessons/${id}`),
  animationsIndex: () => request('GET', '/api/animations'),
  getAnimation: (id) => request('GET', `/api/animations/${id}`),
  createAnimationCategory: (name) => request('POST', '/api/animations/categories', { name }),
  createAnimation: (body) => request('POST', '/api/animations', body),
  listProjects: () => request('GET', '/api/projects'),
  createProject: (body) => request('POST', '/api/projects', body),
  getProject: (id) => request('GET', `/api/projects/${id}`),
  patchProject: (id, body) => request('PATCH', `/api/projects/${id}`, body),
  deleteProject: (id) => request('DELETE', `/api/projects/${id}`),
  createClip: (pid, body) => request('POST', `/api/projects/${pid}/clips`, body),
  patchClip: (pid, cid, body) => request('PATCH', `/api/projects/${pid}/clips/${cid}`, body),
  deleteClip: (pid, cid) => request('DELETE', `/api/projects/${pid}/clips/${cid}`),
  moveClip: (pid, cid, position) => request('POST', `/api/projects/${pid}/clips/${cid}/move`, { position }),
  renderClip: (pid, cid) => request('POST', `/api/projects/${pid}/clips/${cid}/render`),
  renderStale: (pid) => request('POST', `/api/projects/${pid}/render-stale`),
  getClipScript: (pid, cid) => request('GET', `/api/projects/${pid}/clips/${cid}/script`),
  getAudioPromo: (pid, cid) => request('GET', `/api/projects/${pid}/clips/${cid}/audio`),
  putAudioPromo: (pid, cid, body) => request('PUT', `/api/projects/${pid}/clips/${cid}/audio`, body),
  mezclarAudioPromo: (pid, cid) => request('POST', `/api/projects/${pid}/clips/${cid}/audio/mezclar`),
  verificarPromo: (pid, cid) => request('POST', `/api/projects/${pid}/clips/${cid}/verificar`),
  getNarracion: (pid) => request('GET', `/api/projects/${pid}/narracion`),
  startNarracion: (pid, body = {}) => request('POST', `/api/projects/${pid}/narracion`, body),
  cancelNarracion: (pid) => request('POST', `/api/projects/${pid}/narracion/cancel`),
  getNarracionTexto: (pid, cid) => request('GET', `/api/projects/${pid}/narracion/${cid}/texto`),
  // Voz sin GCP: catalogo de proveedores, guion editable y grabacion propia.
  getVoces: () => request('GET', '/api/narracion/proveedores'),
  getGuion: (pid, cid) => request('GET', `/api/projects/${pid}/narracion/${cid}/guion`),
  putGuion: (pid, cid, secciones) => request('PUT', `/api/projects/${pid}/narracion/${cid}/guion`, { secciones }),
  subirNarracion: (pid, cid, file) => subirArchivo(
    `/api/projects/${pid}/narracion/${cid}/audio?nombre=${encodeURIComponent(file.name || 'voz.wav')}`, file),
  // La pelicula del curso (clips + narracion + marca en un solo archivo).
  getPelicula: (pid) => request('GET', `/api/projects/${pid}/pelicula`),
  montarPelicula: (pid, body = {}) => request('POST', `/api/projects/${pid}/pelicula`, body),
  cancelarPelicula: (pid) => request('POST', `/api/projects/${pid}/pelicula/cancel`),
  verificarPelicula: (pid) => request('POST', `/api/projects/${pid}/pelicula/verificar`),
  borrarPelicula: (pid) => request('DELETE', `/api/projects/${pid}/pelicula`),

  // La presentacion: los renders del proyecto cortados en fragmentos (uno por
  // clic del ponente) y armados en un .pptx.
  getPresentacion: (pid) => request('GET', `/api/projects/${pid}/presentacion`),
  armarPresentacion: (pid, body = {}) => request('POST', `/api/projects/${pid}/presentacion`, body),
  cancelarPresentacion: (pid) => request('POST', `/api/projects/${pid}/presentacion/cancel`),
  borrarPresentacion: (pid) => request('DELETE', `/api/projects/${pid}/presentacion`),
  // Banco de sonidos: los wavs sueltos de la paleta, para poder OIRLOS.
  getSfx: () => request('GET', '/api/sfx'),
  generarSfx: () => request('POST', '/api/sfx'),
}

export function videoUrl(id) {
  return `/api/jobs/${id}/video`
}

export function thumbUrl(id) {
  return `/api/jobs/${id}/thumb`
}

export function projectExportUrl(id) {
  return `/api/projects/${id}/export`
}

export function projectArchiveUrl(id) {
  return `/api/projects/${id}/archive`
}

export function frameVerificacionUrl(jobId, archivo) {
  return `/api/jobs/${jobId}/verificacion/${archivo}`
}

// El mp4 montado se sirve con soporte de Range: el navegador puede saltar
// dentro de una pelicula de media hora sin descargarla entera.
export function peliculaVideoUrl(pid) {
  return `/api/projects/${pid}/pelicula/video`
}

// Un efecto de la paleta, para audicion. El nombre va contra el conjunto
// cerrado en el backend: aqui no hace falta escaparlo mas alla de la URL.
// El .pptx de la presentacion. Es una descarga, no un reproductor: el
// navegador no sabe abrir un PowerPoint.
export function presentacionDeckUrl(pid) {
  return `/api/projects/${pid}/presentacion/deck`
}

export function sfxUrl(nombre) {
  return `/api/sfx/${encodeURIComponent(nombre)}`
}

export function narracionAudioUrl(pid, cid) {
  return `/api/projects/${pid}/narracion/${cid}/audio`
}
