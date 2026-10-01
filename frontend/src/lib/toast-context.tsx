import { createContext, useCallback, useContext, useRef, useState, type ReactNode } from 'react'

type TipoToast = 'exito' | 'error' | 'info'

interface ToastItem {
  id: number
  tipo: TipoToast
  mensaje: string
}

interface ToastContextValor {
  mostrar: (mensaje: string, tipo?: TipoToast) => void
}

const ToastContext = createContext<ToastContextValor | null>(null)

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])
  const contador = useRef(0)

  const cerrar = useCallback((id: number) => {
    setToasts((previos) => previos.filter((t) => t.id !== id))
  }, [])

  const mostrar = useCallback((mensaje: string, tipo: TipoToast = 'info') => {
    const id = ++contador.current
    setToasts((previos) => [...previos, { id, tipo, mensaje }])
    setTimeout(() => cerrar(id), 6000)
  }, [cerrar])

  return (
    <ToastContext.Provider value={{ mostrar }}>
      {children}
      <div className="toasts">
        {toasts.map((t) => (
          <div key={t.id} className={`toast ${t.tipo}`}>
            <span>{t.mensaje}</span>
            <button className="cerrar" aria-label="Cerrar" onClick={() => cerrar(t.id)}>
              ×
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast debe usarse dentro de <ToastProvider>')
  return ctx
}
