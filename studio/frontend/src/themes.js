// Temas: conjuntos de variables CSS aplicados via data-theme en <html>.
// Curados a 4 (antes 7) para no diluir la identidad. 'orbital' = :root.
// swatch = [lienzo, acento, secundario] para la muestra del selector.

export const THEMES = [
  { id: 'orbital', name: 'Liquid Glass', swatch: ['#030712', '#00d8f6', '#3b82f6'] },
  { id: 'ion', name: 'Emerald Glass', swatch: ['#020c08', '#10b981', '#34d399'] },
  { id: 'nebula', name: 'Nebula Glass', swatch: ['#07020d', '#d946ef', '#a855f7'] },
  { id: 'daylight', name: 'Ice Glass', swatch: ['#030f1c', '#38bdf8', '#22d3ee'] },
]

export function currentTheme() {
  const saved = localStorage.getItem('ms_theme')
  return THEMES.some((t) => t.id === saved) ? saved : 'orbital'
}

export function applyTheme(id) {
  document.documentElement.dataset.theme = id
  localStorage.setItem('ms_theme', id)
}
