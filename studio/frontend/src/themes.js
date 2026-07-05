// Temas: conjuntos de variables CSS aplicados via data-theme en <html>.
// El id 'orbital' es el tema por defecto (los valores de :root).

export const THEMES = [
  { id: 'orbital', name: 'Orbital', swatch: ['#070b12', '#e8b84b', '#6fc3df'] },
  { id: 'aurora', name: 'Aurora', swatch: ['#06120f', '#5ee6a8', '#9d7bff'] },
  { id: 'deepspace', name: 'Deep Space', swatch: ['#000000', '#ff5fa2', '#7f7cff'] },
  { id: 'daylight', name: 'Daylight', swatch: ['#f4f1ea', '#a3742c', '#2b7a9e'] },
  { id: 'nebula', name: 'Nebula', swatch: ['#0d0716', '#b388ff', '#ff8fd4'] },
  { id: 'ion', name: 'Ion', swatch: ['#04121c', '#2fd4ff', '#45e0c0'] },
  { id: 'solar', name: 'Solar', swatch: ['#120c06', '#ffb347', '#ff7847'] },
]

export function currentTheme() {
  const saved = localStorage.getItem('ms_theme')
  return THEMES.some((t) => t.id === saved) ? saved : 'orbital'
}

export function applyTheme(id) {
  document.documentElement.dataset.theme = id
  localStorage.setItem('ms_theme', id)
}
