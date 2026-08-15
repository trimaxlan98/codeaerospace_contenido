// Configuracion — el unico sitio donde se ajusta la consola (encargo 8).
//
// Antes el tema y la sesion colgaban de la barra superior: un desplegable de
// temas que se abria sobre el contenido y un boton "Salir" a un clic de
// distancia de la navegacion. La barra vuelve a ser solo navegacion + estado,
// y todo lo que el usuario configura vive aqui, en secciones con nombre.
//
// Trampa de esta app: la navegacion es por hash (`router.js`), asi que los
// anclajes clasicos (<a href="#cuenta">) cambiarian de vista. El indice
// lateral navega con scrollIntoView sobre refs, sin tocar la URL.

import { useEffect, useRef, useState } from 'react'
import {
  Check, LogOut, Monitor, Palette, ShieldCheck, Sparkles, Trash2, User,
} from 'lucide-react'
import { THEMES, applyTheme, currentTheme } from './themes.js'
import { LANDING_VIEWS, clearLocal, localUsage, motionAllowed, setPref, usePref } from './prefs.js'
import { PasswordChangeFields, useChangePassword } from './components/PasswordChange.jsx'
import { Switch, SettingRow } from './components/ui/switch.jsx'
import { Button } from './components/ui/button.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select.jsx'
import { BrandMark, Wordmark } from './components/Brand.jsx'
import { cn } from '@/lib/utils'

const SECTIONS = [
  { id: 'apariencia', label: 'Apariencia', icon: Palette },
  { id: 'interfaz', label: 'Interfaz', icon: Monitor },
  { id: 'cuenta', label: 'Cuenta y sesión', icon: User },
  { id: 'datos', label: 'Datos locales', icon: Trash2 },
  { id: 'acerca', label: 'Acerca de', icon: Sparkles },
]

function Section({ id, title, description, innerRef, children }) {
  return (
    <section ref={innerRef} aria-labelledby={`sec-${id}`} className="panel shrink-0 scroll-mt-4">
      <header className="border-b border-line px-4 py-3">
        <h2 id={`sec-${id}`} className="font-display text-[15px] font-semibold tracking-tight text-ink">
          {title}
        </h2>
        {description && <p className="mt-1 max-w-[70ch] text-[12.5px] leading-relaxed text-muted">{description}</p>}
      </header>
      <div className="relative z-[2]">{children}</div>
    </section>
  )
}

/** Muestra viva del tema: el propio `data-theme` sobre un contenedor hace que
 *  los tokens de `theme.css` se apliquen a su subarbol, asi que la miniatura
 *  se pinta con los colores reales del tema — sin copiar valores a un tercer
 *  sitio que luego se desincroniza. */
function ThemeCard({ theme, active, onPick }) {
  return (
    <button
      type="button"
      role="radio"
      aria-checked={active}
      onClick={() => onPick(theme.id)}
      className={cn(
        'group flex flex-col overflow-hidden rounded-lg border text-left transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan focus-visible:ring-offset-2 focus-visible:ring-offset-canvas',
        active ? 'border-accent' : 'border-line hover:border-line-strong',
      )}
    >
      <span data-theme={theme.id} className="block h-[74px] w-full bg-canvas p-2.5" aria-hidden="true">
        <span className="flex h-full w-full flex-col gap-1.5 rounded-md border border-line bg-surface p-2">
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-accent" />
            <span className="h-1.5 w-10 rounded-full bg-ink opacity-80" />
            <span className="ml-auto h-1.5 w-4 rounded-full bg-brand" />
          </span>
          <span className="h-1.5 w-full rounded-full bg-muted opacity-50" />
          <span className="h-1.5 w-2/3 rounded-full bg-muted opacity-30" />
          <span className="mt-auto h-2.5 w-12 rounded-sm bg-accent" />
        </span>
      </span>
      <span className="flex items-center gap-2 border-t border-line px-3 py-2">
        <span className={cn('flex-1 text-[13px]', active ? 'text-accent' : 'text-ink')}>{theme.name}</span>
        {active && <Check className="h-4 w-4 text-accent" aria-hidden="true" />}
      </span>
    </button>
  )
}

function AccountSection({ user, onLogout }) {
  const [open, setOpen] = useState(false)
  const [done, setDone] = useState(false)
  const state = useChangePassword(() => { setDone(true); setOpen(false) })
  const [confirmingLogout, setConfirmingLogout] = useState(false)

  useEffect(() => {
    if (!confirmingLogout) return
    const t = setTimeout(() => setConfirmingLogout(false), 3500)
    return () => clearTimeout(t)
  }, [confirmingLogout])

  return (
    <>
      <SettingRow label="Usuario" hint="El nombre de usuario se fija en el servidor (MS_ADMIN_USER) y no se cambia desde la app.">
        <span className="font-mono text-[13px] text-ink">{user || '—'}</span>
      </SettingRow>

      <SettingRow
        label="Contraseña"
        hint="Se guarda cifrada en la base de datos del servidor, nunca en el repositorio. Al cambiarla, la sesión actual sigue abierta."
      >
        <Button size="sm" variant={open ? 'default' : 'outline'}
          aria-expanded={open}
          onClick={() => { setOpen((v) => !v); setDone(false); state.reset() }}>
          {open ? 'Cancelar' : 'Cambiar contraseña'}
        </Button>
      </SettingRow>

      {open && (
        <form onSubmit={state.submit} className="flex flex-col gap-3.5 border-t border-line bg-canvas/30 px-4 py-4">
          <div className="grid max-w-[560px] gap-3.5">
            <PasswordChangeFields state={state} autoFocus />
          </div>
          {state.error && (
            <p role="alert" className="max-w-[560px] rounded-md border border-err/40 bg-err/10 px-3 py-2 text-[12.5px] text-err">
              {state.error}
            </p>
          )}
          <div>
            <Button variant="primary" size="sm" disabled={state.busy}>
              {state.busy ? 'Guardando…' : 'Guardar contraseña'}
            </Button>
          </div>
        </form>
      )}

      {done && (
        <p role="status" className="flex items-center gap-2 border-t border-line px-4 py-3 text-[12.5px] text-ok">
          <ShieldCheck className="h-4 w-4" aria-hidden="true" />
          Contraseña actualizada.
        </p>
      )}

      <SettingRow
        label="Sesión"
        hint="La sesión es una cookie firmada del servidor. Al cerrarla vuelves al login; lo guardado en este navegador (editor, tema) se conserva."
      >
        {confirmingLogout ? (
          <Button size="sm" variant="danger" onClick={onLogout}>¿Cerrar sesión?</Button>
        ) : (
          <Button size="sm" variant="outline" onClick={() => setConfirmingLogout(true)}>
            <LogOut className="h-3.5 w-3.5" aria-hidden="true" />
            Cerrar sesión
          </Button>
        )}
      </SettingRow>
    </>
  )
}

function LocalDataSection() {
  const [items, setItems] = useState(localUsage)
  const [arming, setArming] = useState(false)
  const [cleared, setCleared] = useState(false)

  useEffect(() => {
    if (!arming) return
    const t = setTimeout(() => setArming(false), 3500)
    return () => clearTimeout(t)
  }, [arming])

  const stored = items.filter((i) => i.present)
  const total = stored.reduce((acc, i) => acc + i.bytes, 0)

  const wipe = () => {
    // El script del editor es lo unico irrecuperable de la lista: se conserva
    // salvo que se pida borrarlo aparte desde el propio Estudio.
    clearLocal(['ms_studio_script'])
    setItems(localUsage())
    setArming(false)
    setCleared(true)
  }

  return (
    <>
      <div className="px-4 py-3">
        {stored.length === 0 ? (
          <p className="text-[12.5px] text-muted">Este navegador no guarda nada de la app todavía.</p>
        ) : (
          <ul className="flex flex-col gap-1.5">
            {stored.map((i) => (
              <li key={i.key} className="flex items-baseline justify-between gap-4 text-[12.5px]">
                <span className="text-ink">{i.label}</span>
                <span className="font-mono text-[11px] tabular-nums text-faint">
                  {i.bytes >= 1024 ? `${(i.bytes / 1024).toFixed(1)} KB` : `${i.bytes} B`}
                </span>
              </li>
            ))}
            <li className="mt-1 flex items-baseline justify-between gap-4 border-t border-line pt-1.5 text-[12.5px]">
              <span className="text-muted">{stored.length} claves</span>
              <span className="font-mono text-[11px] tabular-nums text-muted">
                {total >= 1024 ? `${(total / 1024).toFixed(1)} KB` : `${total} B`}
              </span>
            </li>
          </ul>
        )}
      </div>
      <SettingRow
        label="Borrar datos locales"
        hint="Restablece tema, preferencias, lecciones leídas y grupos desplegados. El script del editor se conserva. No toca nada del servidor: proyectos, renders y narraciones siguen intactos."
      >
        {cleared && <span role="status" className="text-[12px] text-ok">Restablecido</span>}
        {arming ? (
          <Button size="sm" variant="danger" onClick={wipe}>¿Confirmar borrado?</Button>
        ) : (
          <Button size="sm" variant="outline" onClick={() => { setArming(true); setCleared(false) }}>
            <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
            Borrar
          </Button>
        )}
      </SettingRow>
    </>
  )
}

export default function Settings({ user, aiEnabled, onLogout }) {
  const [theme, setTheme] = useState(currentTheme)
  const landing = usePref('landing')
  const motion = usePref('motion')
  const toasts = usePref('toasts')
  const telemetry = usePref('telemetry')
  const guided = usePref('guided')
  const refs = useRef({})
  const [systemReduces] = useState(() =>
    Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches))

  const pickTheme = (id) => { applyTheme(id); setTheme(id) }

  return (
    <main data-view="settings" className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
      <div className="mx-auto w-full max-w-[1080px]">
        <h1 className="font-display text-[19px] font-semibold tracking-tight text-ink">Configuración</h1>
        <p className="mt-0.5 text-[12.5px] text-muted">
          Apariencia, cuenta y preferencias de la consola. Todo lo que antes vivía en la barra superior.
        </p>
      </div>

      <div className="mx-auto flex min-h-0 w-full max-w-[1080px] flex-1 gap-3">
        {/* Indice: en <lg estorbaria (la vista ya cabe de un scroll). */}
        <nav aria-label="secciones de configuración" className="hidden w-[190px] shrink-0 lg:block">
          <div className="panel sticky top-0 p-1.5">
            {SECTIONS.map((s) => {
              const Icon = s.icon
              return (
                <button key={s.id} type="button"
                  onClick={() => refs.current[s.id]?.scrollIntoView({ behavior: 'smooth', block: 'start' })}
                  className="relative z-[2] flex w-full items-center gap-2 rounded-md px-2.5 py-2 text-[13px] text-muted transition-colors hover:bg-surface-2 hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan"
                >
                  <Icon className="h-3.5 w-3.5" aria-hidden="true" />
                  {s.label}
                </button>
              )
            })}
          </div>
        </nav>

        <div className="flex min-w-0 flex-1 flex-col gap-3 pb-6 ">
          <Section id="apariencia" innerRef={(el) => { refs.current.apariencia = el }}
            title="Apariencia"
            description="El tema se aplica al instante y se recuerda en este navegador. Las miniaturas están pintadas con los colores reales de cada tema.">
            <div role="radiogroup" aria-label="tema de la interfaz"
              className="grid grid-cols-2 gap-2.5 p-4 sm:grid-cols-4">
              {THEMES.map((t) => (
                <ThemeCard key={t.id} theme={t} active={t.id === theme} onPick={pickTheme} />
              ))}
            </div>
            <SettingRow
              label="Fondo animado"
              hint={systemReduces
                ? 'Tu sistema pide reducir el movimiento: en «Automático» el fondo se queda quieto.'
                : 'La red de partículas de fondo. Desactívala si dejas la consola abierta muchas horas o el equipo va justo.'}
            >
              {/* El resultado va junto al control, no en una fila aparte: con
                  `auto` la respuesta depende del sistema y hay que poder
                  verla sin salir de la fila. */}
              <span className="font-mono text-[11px] text-muted">
                {motionAllowed(motion) ? 'animado' : 'estático'}
              </span>
              <Select value={motion} onValueChange={(v) => setPref('motion', v)}>
                <SelectTrigger className="w-[190px]"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="auto">Automático</SelectItem>
                  <SelectItem value="off">Desactivado</SelectItem>
                </SelectContent>
              </Select>
            </SettingRow>
          </Section>

          <Section id="interfaz" innerRef={(el) => { refs.current.interfaz = el }}
            title="Interfaz"
            description="Qué ves al entrar y cuánta información lleva la barra superior.">
            <SettingRow
              label="Vista al abrir"
              hint="A dónde entra la app cuando la abres sin un enlace concreto. Un enlace directo (por ejemplo a un proyecto) siempre manda sobre esto."
            >
              <Select value={landing} onValueChange={(v) => setPref('landing', v)}>
                <SelectTrigger className="w-[190px]"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {LANDING_VIEWS.map((v) => (
                    <SelectItem key={v.id} value={v.id}>{v.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </SettingRow>
            <SettingRow
              label="Avisos de fin de render"
              hint="El recuadro que aparece abajo a la derecha cuando un render termina o falla. El título de la pestaña sigue avisando aunque lo apagues."
            >
              <Switch checked={toasts} onCheckedChange={(v) => setPref('toasts', v)}
                aria-label="avisos de fin de render" />
            </SettingRow>
            <SettingRow
              label="Telemetría en la barra"
              hint="Medidores de CPU y RAM y reloj UTC. Apágalos para una barra más limpia; los datos completos siguen en Admin → Salud."
            >
              <Switch checked={telemetry} onCheckedChange={(v) => setPref('telemetry', v)}
                aria-label="telemetría en la barra superior" />
            </SettingRow>
            <SettingRow
              label="Modo guiado"
              hint="Añade un asistente que escribe el script de un clip a partir de un formulario, para quien no escribe Manim a mano. Apagado, la consola no muestra ni un botón de más y el editor se usa igual que siempre. Las plantillas de curso no dependen de esto: están siempre en «Nuevo proyecto» con «En blanco» por defecto."
            >
              <Switch checked={guided} onCheckedChange={(v) => setPref('guided', v)}
                aria-label="modo guiado" />
            </SettingRow>
          </Section>

          <Section id="cuenta" innerRef={(el) => { refs.current.cuenta = el }}
            title="Cuenta y sesión"
            description="ManimStudio es de un solo usuario: la contraseña vive en el servidor y la sesión es una cookie firmada.">
            <AccountSection user={user} onLogout={onLogout} />
          </Section>

          <Section id="datos" innerRef={(el) => { refs.current.datos = el }}
            title="Datos locales"
            description="Lo que la app guarda en este navegador. Nada de esto sale del equipo.">
            <LocalDataSection />
          </Section>

          <Section id="acerca" innerRef={(el) => { refs.current.acerca = el }}
            title="Acerca de"
            description="Esta consola es parte de CO.DE Academy: la misma identidad que se estampa en cada video renderizado.">
            <div className="flex flex-wrap items-center gap-4 px-4 py-4">
              <BrandMark size={44} />
              <div>
                <div className="font-display text-[15px] font-semibold tracking-tight text-ink">ManimStudio</div>
                <Wordmark size="sm" className="mt-1" />
              </div>
              <div className="ml-auto flex flex-col items-end gap-1 text-[12px] text-muted">
                <span>Asistente IA: {aiEnabled
                  ? <span className="text-ok">disponible</span>
                  : <span className="text-faint">no configurado</span>}</span>
                <a href="#/admin/salud" className="text-cyan underline underline-offset-2 hover:text-ink">
                  Estado del sistema →
                </a>
              </div>
            </div>
          </Section>
        </div>
      </div>
    </main>
  )
}
