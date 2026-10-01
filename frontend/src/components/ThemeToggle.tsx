import { useEffect, useState } from 'react'

function aplicarTema(tema: 'claro' | 'oscuro') {
  const html = document.documentElement
  if (tema === 'oscuro') html.setAttribute('data-tema', 'oscuro')
  else html.removeAttribute('data-tema')
  try {
    localStorage.setItem('tema-aplicacion', tema)
  } catch {
    // almacenamiento no disponible (modo privado, etc.) — el tema solo dura la sesión
  }
}

/** Botón sol/luna que replica el `#tema-toggle` de la app clásica: alterna
 * `data-tema="oscuro"` en <html> (ver tokens.css) y recuerda la elección en
 * localStorage. Si el usuario nunca eligió manualmente, sigue el tema del
 * sistema operativo en vivo. */
export function ThemeToggle({ sobreOscuro = false }: { sobreOscuro?: boolean }) {
  const [oscuro, setOscuro] = useState(() => document.documentElement.hasAttribute('data-tema'))

  useEffect(() => {
    let eligioManualmente = true
    try {
      eligioManualmente = localStorage.getItem('tema-aplicacion') !== null
    } catch {
      eligioManualmente = true
    }
    if (eligioManualmente || !window.matchMedia) return
    const medio = window.matchMedia('(prefers-color-scheme: dark)')
    const seguirSistema = (evento: MediaQueryListEvent) => {
      aplicarTema(evento.matches ? 'oscuro' : 'claro')
      setOscuro(evento.matches)
    }
    medio.addEventListener('change', seguirSistema)
    return () => medio.removeEventListener('change', seguirSistema)
  }, [])

  function alternar() {
    const nuevo = oscuro ? 'claro' : 'oscuro'
    aplicarTema(nuevo)
    setOscuro(!oscuro)
  }

  return (
    <button
      type="button"
      onClick={alternar}
      aria-label="Cambiar tema claro u oscuro"
      title="Cambiar tema"
      className={
        sobreOscuro
          ? 'flex h-9 w-9 flex-none items-center justify-center rounded-input border border-dark-line text-on-dark-muted transition-colors hover:border-on-dark-muted hover:text-on-dark'
          : 'flex h-9 w-9 flex-none items-center justify-center rounded-input border border-line text-ink-soft transition-colors hover:border-primary hover:bg-primary-wash hover:text-primary'
      }
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" className="h-[18px] w-[18px]">
        {oscuro ? (
          <>
            <circle cx="12" cy="12" r="4" />
            <path d="M12 2v2" />
            <path d="M12 20v2" />
            <path d="m4.93 4.93 1.41 1.41" />
            <path d="m17.66 17.66 1.41 1.41" />
            <path d="M2 12h2" />
            <path d="M20 12h2" />
            <path d="m6.34 17.66-1.41 1.41" />
            <path d="m19.07 4.93-1.41 1.41" />
          </>
        ) : (
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        )}
      </svg>
    </button>
  )
}
