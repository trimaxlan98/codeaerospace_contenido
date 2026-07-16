// Borrado en dos toques: el primero arma, el segundo confirma (se desarma
// solo tras un rato). Compartido por Library y Projects.

import { useEffect, useState } from 'react'
import { Button } from './ui/button.jsx'

export default function DeleteButton({ onDelete }) {
  const [arming, setArming] = useState(false)
  useEffect(() => {
    if (!arming) return
    const t = setTimeout(() => setArming(false), 3500)
    return () => clearTimeout(t)
  }, [arming])
  return arming ? (
    <Button size="xs" variant="danger" onClick={onDelete}>¿Confirmar?</Button>
  ) : (
    <Button size="xs" variant="ghost" onClick={() => setArming(true)}>Borrar</Button>
  )
}
