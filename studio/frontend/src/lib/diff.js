// Diff de lineas por LCS (scripts pequeños: O(n·m) es suficiente).
//
// Nacio dentro de `Assistant.jsx` para enseñar la correccion que propone
// Gemini. Desde R5a lo usa tambien el historial de script de un clip
// («restaurar el script del ultimo render que funciono»), asi que vive aqui:
// dos copias del mismo algoritmo se separan en silencio.

export function diffLines(aText, bText) {
  const a = aText.split('\n')
  const b = bText.split('\n')
  const n = a.length
  const m = b.length
  const dp = Array.from({ length: n + 1 }, () => new Uint16Array(m + 1))
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1])
    }
  }
  const out = []
  let i = 0
  let j = 0
  while (i < n && j < m) {
    if (a[i] === b[j]) { out.push({ t: ' ', line: a[i] }); i++; j++ }
    else if (dp[i + 1][j] >= dp[i][j + 1]) { out.push({ t: '-', line: a[i] }); i++ }
    else { out.push({ t: '+', line: b[j] }); j++ }
  }
  while (i < n) out.push({ t: '-', line: a[i++] })
  while (j < m) out.push({ t: '+', line: b[j++] })
  return out
}

/** Cuantas lineas cambian entre los dos textos: {quitadas, anadidas}. */
export function cuentaCambios(filas) {
  return filas.reduce((acc, r) => ({
    quitadas: acc.quitadas + (r.t === '-' ? 1 : 0),
    anadidas: acc.anadidas + (r.t === '+' ? 1 : 0),
  }), { quitadas: 0, anadidas: 0 })
}
