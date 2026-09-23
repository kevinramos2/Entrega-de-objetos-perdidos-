export function LogoMark({ size = 34 }: { size?: number }) {
  return (
    <span
      className="inline-flex flex-shrink-0 items-center justify-center rounded-input bg-hero-gradient text-white"
      style={{ width: size, height: size }}
    >
      <svg
        width={size * 0.56}
        height={size * 0.56}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth={1.8}
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M21 8a1 1 0 0 0-.5-.87l-8-4.57a1 1 0 0 0-1 0l-8 4.57A1 1 0 0 0 3 8v8a1 1 0 0 0 .5.87l8 4.56a1 1 0 0 0 1 0l8-4.56A1 1 0 0 0 21 16Z" />
        <path d="m3.3 7 8.7 5 8.7-5" />
        <path d="M12 22V12" />
      </svg>
    </span>
  )
}

export function Logo({ sobreOscuro = false }: { sobreOscuro?: boolean }) {
  return (
    <span className="inline-flex items-center gap-2.5">
      <LogoMark />
      <span className={`font-display text-body-lg font-bold ${sobreOscuro ? 'text-on-dark' : 'text-ink'}`}>
        Perdidos &amp; Encontrados
      </span>
    </span>
  )
}
