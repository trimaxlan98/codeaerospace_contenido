// Pantalla obligatoria de cambio de contraseña: se muestra en vez de la app
// cuando /api/me devuelve must_change_password=true (primer login del
// usuario recien creado). No es un dialogo cerrable — el backend bloquea el
// resto de la API con 403 hasta que la contraseña cambie.
//
// La logica y los campos son los mismos que usa Configuracion → Cuenta; aqui
// solo cambia el marco (AuthCard, sin sesion) y el pie con "Cerrar sesión".

import { Button } from './components/ui/button.jsx'
import { AuthCard } from './components/AuthCard.jsx'
import { PasswordChangeFields, useChangePassword } from './components/PasswordChange.jsx'

const FACTS = [
  'Se guarda cifrada · nunca en el repo',
  'Minimo 8 caracteres',
  'La cambias cuando quieras desde Configuracion',
]

export default function ChangePassword({ onChanged, onLogout }) {
  const state = useChangePassword(onChanged)

  return (
    <AuthCard
      onSubmit={state.submit}
      shake={Boolean(state.error)}
      title="Cambia tu contraseña"
      subtitle="Es tu primer inicio de sesión: elige una contraseña nueva antes de entrar a la consola."
      facts={FACTS}
      heading="Contraseña nueva"
    >
      <PasswordChangeFields state={state} autoFocus />

      {state.error && (
        <p role="alert" className="rounded-md border border-err/40 bg-err/10 px-3 py-2 text-[13px] text-err">
          {state.error}
        </p>
      )}

      <Button variant="primary" size="lg" disabled={state.busy} className="w-full">
        {state.busy ? 'Guardando…' : 'Cambiar contraseña'}
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
