// Firma visual de ManimStudio. El estado del render conduce el ornamento:
// idle = orbita lenta cian; rendering = rapida y ambar; error = rojo.
export function OrbitGlyph({ state = 'idle', size = 34 }) {
  return (
    <svg
      className={`orbit orbit--${state}`}
      viewBox="0 0 64 64"
      width={size}
      height={size}
      role="img"
      aria-label={`estado del render: ${state}`}
    >
      <circle cx="32" cy="32" r="30" className="orbit__halo" />
      <ellipse cx="32" cy="32" rx="26" ry="11" className="orbit__path"
        transform="rotate(-20 32 32)" />
      <ellipse cx="32" cy="32" rx="26" ry="11" className="orbit__path orbit__path--b"
        transform="rotate(28 32 32)" />
      <circle cx="32" cy="32" r="7" className="orbit__core" />
      <g className="orbit__spin">
        <circle cx="58" cy="32" r="3.2" className="orbit__sat"
          transform="rotate(-20 32 32)" />
      </g>
    </svg>
  )
}
