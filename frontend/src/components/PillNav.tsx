import type { ReactNode } from 'react'

interface EnlaceNav {
  etiqueta: string
  activo?: boolean
  onClick?: () => void
}

interface PillNavProps {
  marca: ReactNode
  enlaces: EnlaceNav[]
  acciones?: ReactNode
}

export function PillNav({ marca, enlaces, acciones }: PillNavProps) {
  return (
    <nav className="mx-auto flex max-w-5xl items-center justify-between gap-4 rounded-pill border border-forest-hairline bg-forest/95 px-3 py-2 backdrop-blur">
      <div className="pl-3 font-display text-body-lg text-cream">{marca}</div>
      <div className="hidden items-center gap-1 sm:flex">
        {enlaces.map((enlace) => (
          <button
            key={enlace.etiqueta}
            onClick={enlace.onClick}
            className={`rounded-pill px-4 py-2 text-caption font-medium transition-colors ${
              enlace.activo
                ? 'bg-cream text-forest'
                : 'text-cream-muted hover:bg-forest-lift hover:text-cream'
            }`}
          >
            {enlace.etiqueta}
          </button>
        ))}
      </div>
      {acciones && <div className="flex items-center gap-2 pr-1">{acciones}</div>}
    </nav>
  )
}
