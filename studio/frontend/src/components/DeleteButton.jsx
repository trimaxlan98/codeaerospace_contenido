// Borrado en dos toques: el primero arma, el segundo confirma (se desarma
// solo tras un rato). Compartido por Renders y Proyectos.

import { useEffect, useState } from 'react'
import { Button } from './ui/button.jsx'

// confirmText: texto opcional del boton de confirmacion (p.ej. avisar que
// el video pertenece a un clip de un proyecto). Por defecto "¿Confirmar?".
export default function DeleteButton({ onDelete, confirmText = '¿Confirmar?' }) {
  const [arming, setArming] = useState(false)
  useEffect(() => {
    if (!arming) return
    const t = setTimeout(() => setArming(false), 3500)
    return () => clearTimeout(t)
  }, [arming])
  return arming ? (
    <Button size="xs" variant="danger" onClick={onDelete}>{confirmText}</Button>
  ) : (
    <Button size="xs" variant="ghost" onClick={() => setArming(true)}>Borrar</Button>
  )
}
