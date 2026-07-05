// Cliente API — rutas relativas /api, cookies de sesion same-origin.

export class ApiError extends Error {
  constructor(status, detail) {
    super(detail || `HTTP ${status}`)
    this.status = status
  }
}

async function request(method, path, body) {
  const res = await fetch(path, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  let data = null
  try { data = await res.json() } catch { /* respuestas no-JSON */ }
  if (!res.ok) throw new ApiError(res.status, data?.detail)
  return data
}

export const api = {
  me: () => request('GET', '/api/me'),
  login: (username, password) => request('POST', '/api/login', { username, password }),
  logout: () => request('POST', '/api/logout'),
  scenes: (script) => request('POST', '/api/scenes', { script }),
  createJob: (payload) => request('POST', '/api/jobs', payload),
  listJobs: () => request('GET', '/api/jobs'),
  getJob: (id) => request('GET', `/api/jobs/${id}`),
  getScript: (id) => request('GET', `/api/jobs/${id}/script`),
  cancelJob: (id) => request('POST', `/api/jobs/${id}/cancel`),
  deleteJob: (id) => request('DELETE', `/api/jobs/${id}`),
  deleteFailedJobs: () => request('DELETE', '/api/jobs/failed'),
  purgeJobsOlderThan: (days) => request('DELETE', `/api/jobs/older-than/${days}`),
  metrics: () => request('GET', '/api/metrics'),
  metricsHistory: () => request('GET', '/api/metrics/history'),
  aiExplain: (payload) => request('POST', '/api/ai/explain', payload),
  aiFix: (payload) => request('POST', '/api/ai/fix', payload),
  aiGenerate: (payload) => request('POST', '/api/ai/generate', payload),
}

export function videoUrl(id) {
  return `/api/jobs/${id}/video`
}

export function thumbUrl(id) {
  return `/api/jobs/${id}/thumb`
}
