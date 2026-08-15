// Pantalla obligatoria de cambio de contraseña: se muestra en vez de la app
// cuando /api/me devuelve must_change_password=true (primer login del
// usuario recien creado). No es un dialogo cerrable — el backend bloquea el
// resto de la API con 403 hasta que la contraseña cambie.

import { useState } from 'react'
import { api } from './api.js'
import { PasswordInput } from './components/ui/input.jsx'
import { Button } from './components/ui/button.jsx'
import { AuthCard, Field } from './components/AuthCard.jsx'

const FACTS = [
  'Se guarda cifrada · nunca en el repo',
  'Minimo 8 caracteres',
  'La cambias cuando quieras',
]

export default function ChangePassword({ onChanged, onLogout }) {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    if (newPassword !== confirmPassword) {
      setError('Las contraseñas nuevas no coinciden')
      return
    }
    setBusy(true)
    setError('')
    try {
      await api.changePassword(currentPassword, newPassword)
      onChanged()
    } catch (err) {
      if (!err.status) setError('No se pudo conectar con el servidor')
      else if (err.status === 422) setError(err.message)
      else setError(`Error del servidor (${err.status})`)
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthCard
      onSubmit={submit}
      shake={Boolean(error)}
      title="Cambia tu contraseña"
      subtitle="Es tu primer inicio de sesión: elige una contraseña nueva antes de entrar a la consola."
      facts={FACTS}
      heading="Contraseña nueva"
    >
      <Field label="Contraseña actual">
        <PasswordInput
          label="la contraseña actual"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          autoComplete="current-password"
          autoFocus
          required
        />
      </Field>

      <Field label="Contraseña nueva" hint="Al menos 8 caracteres.">
        <PasswordInput
          label="la contraseña nueva"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          autoComplete="new-password"
          minLength={8}
          required
        />
      </Field>

      <Field label="Repite la contraseña nueva">
        <PasswordInput
          label="la repetición de la contraseña"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          autoComplete="new-password"
          minLength={8}
          required
        />
      </Field>

      {error && (
        <p role="alert" className="rounded-md border border-err/40 bg-err/10 px-3 py-2 text-[13px] text-err">
          {error}
        </p>
      )}

      <Button variant="primary" size="lg" disabled={busy} className="w-full">
        {busy ? 'Guardando…' : 'Cambiar contraseña'}
      </Button>

      <button
        type="button"
        onClick={onLogout}
        className="rounded text-center text-[12.5px] text-muted transition-colors hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan"
      >
        Cerrar sesión
      </button>
    </AuthCard>
  )
}
