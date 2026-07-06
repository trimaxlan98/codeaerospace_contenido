// Ultima linea de defensa: una excepcion de render no debe dejar la pantalla
// en negro absoluto — se muestra el error y un boton de recarga.

import { Component } from 'react'

export default class ErrorBoundary extends Component {
  state = { error: null }

  static getDerivedStateFromError(error) {
    return { error }
  }

  render() {
    if (!this.state.error) return this.props.children
    return (
      <div className="grid min-h-dvh place-items-center bg-canvas p-6">
        <div className="panel w-[min(460px,94vw)] p-6 text-center">
          <p className="eyebrow">Fallo de interfaz</p>
          <h1 className="mt-2 font-display text-lg font-semibold text-ink">
            La consola encontró un error y se detuvo
          </h1>
          <p className="mt-2 break-words font-mono text-[12px] leading-relaxed text-err">
            {String(this.state.error?.message || this.state.error)}
          </p>
          <p className="mt-2 text-[13px] text-muted">
            Los renders en curso no se ven afectados: la cola vive en el servidor.
          </p>
          <button onClick={() => window.location.reload()}
            className="mt-4 rounded-md bg-accent px-4 py-2 text-sm font-semibold text-accent-ink transition-opacity hover:opacity-90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan">
            Recargar la consola
          </button>
        </div>
      </div>
    )
  }
}
