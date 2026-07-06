// Temas: conjuntos de variables CSS aplicados via data-theme en <html>.
// Curados a 4 (antes 7) para no diluir la identidad. 'orbital' = :root.
// swatch = [lienzo, acento, secundario] para la muestra del selector.

export const THEMES = [
  { id: 'orbital', name: 'Orbital', swatch: ['#0a0d13', '#f2b347', '#56c7df'] },
  { id: 'ion', name: 'Ion', swatch: ['#04121c', '#2fd4ff', '#45e0c0'] },
  { id: 'nebula', name: 'Nebula', swatch: ['#0d0716', '#b388ff', '#ff8fd4'] },
  { id: 'daylight', name: 'Daylight', swatch: ['#f2efe7', '#a56a12', '#1f6f8b'] },
]

export function currentTheme() {
  const saved = localStorage.getItem('ms_theme')
  return THEMES.some((t) => t.id === saved) ? saved : 'orbital'
}

export function applyTheme(id) {
  document.documentElement.dataset.theme = id
  localStorage.setItem('ms_theme', id)
}
