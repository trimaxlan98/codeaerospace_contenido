// Cambio de contraseña — logica y campos compartidos.
//
// Se usa en dos sitios con marcos distintos: la pantalla obligatoria del
// primer login (`ChangePassword.jsx`, dentro de AuthCard) y la seccion Cuenta
// de Configuracion. Duplicar validacion y manejo de errores en ambos los
// desincroniza en cuanto uno de los dos cambie, asi que aqui viven el estado
// y los tres campos, y cada sitio pone su propio envoltorio y sus botones.

import { useState } from 'react'
import { PasswordInput } from './ui/input.jsx'
import { Field } from './AuthCard.jsx'
import { api } from '../api.js'

export function useChangePassword(onDone) {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const reset = () => {
    setCurrentPassword(''); setNewPassword(''); setConfirmPassword(''); setError('')
  }

  const submit = async (e) => {
    e.preventDefault()
    if (busy) return
    if (newPassword !== confirmPassword) {
      setError('Las contraseñas nuevas no coinciden')
      return
    }
    setBusy(true)
    setError('')
    try {
      await api.changePassword(currentPassword, newPassword)
      reset()
      onDone?.()
    } catch (err) {
      // 422 trae el motivo real del backend (longitud, contraseña actual
      // incorrecta); el resto se traduce para no enseñar un codigo pelado.
      if (!err.status) setError('No se pudo conectar con el servidor')
      else if (err.status === 422) setError(err.message)
      else setError(`Error del servidor (${err.status})`)
    } finally {
      setBusy(false)
    }
  }

  return {
    values: { currentPassword, newPassword, confirmPassword },
    set: { setCurrentPassword, setNewPassword, setConfirmPassword },
    error, busy, submit, reset,
  }
}

export function PasswordChangeFields({ state, autoFocus }) {
  const { values, set } = state
  return (
    <>
      <Field label="Contraseña actual">
        <PasswordInput
          label="la contraseña actual"
          value={values.currentPassword}
          onChange={(e) => set.setCurrentPassword(e.target.value)}
          autoComplete="current-password"
          autoFocus={autoFocus}
          required
        />
      </Field>

      <Field label="Contraseña nueva" hint="Al menos 8 caracteres.">
        <PasswordInput
          label="la contraseña nueva"
          value={values.newPassword}
          onChange={(e) => set.setNewPassword(e.target.value)}
          autoComplete="new-password"
          minLength={8}
          required
        />
      </Field>

      <Field label="Repite la contraseña nueva">
        <PasswordInput
          label="la repetición de la contraseña"
          value={values.confirmPassword}
          onChange={(e) => set.setConfirmPassword(e.target.value)}
          autoComplete="new-password"
          minLength={8}
          required
        />
      </Field>
    </>
  )
}
