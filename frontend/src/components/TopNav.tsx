import type { ReactNode } from 'react'
import { Logo } from './Logo'

interface EnlaceNav {
  etiqueta: string
  activo?: boolean
  destacado?: boolean
  onClick?: () => void
}

interface TopNavProps {
  enlaces: EnlaceNav[]
  acciones?: ReactNode
}

export function TopNav({ enlaces, acciones }: TopNavProps) {
  return (
    <header className="border-b border-line bg-surface">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3">
        <Logo />
        <nav className="hidden items-center gap-1 sm:flex">
          {enlaces.map((enlace) => (
            <button
              key={enlace.etiqueta}
              onClick={enlace.onClick}
              className={`rounded-pill px-4 py-2 text-caption font-semibold transition-colors ${
                enlace.activo || enlace.destacado
                  ? 'bg-primary text-white'
                  : 'text-ink-soft hover:bg-surface-hover'
              }`}
            >
              {enlace.etiqueta}
            </button>
          ))}
        </nav>
        <div className="flex items-center gap-3">{acciones}</div>
      </div>
    </header>
  )
}
