import { useCallback, useState } from 'react'
import { Button } from './Button'

interface OpcionesConfirmar {
  titulo?: string
  mensaje: string
  textoConfirmar?: string
  /** 'peligro' (rojo, por defecto) para acciones destructivas; 'exito' (verde) para
   * confirmaciones constructivas como aprobar o marcar como entregado. */
  tono?: 'peligro' | 'exito'
}

interface EstadoModal extends OpcionesConfirmar {
  resolver: (ok: boolean) => void
}

/** Reemplaza window.confirm con un modal propio (igual que #modal-confirmacion
 * en la app clásica). Uso: const confirmar = useConfirm(); if (await
 * confirmar({ mensaje: '¿Eliminar?' })) { ... } */
export function useConfirmModal() {
  const [estado, setEstado] = useState<EstadoModal | null>(null)

  const confirmar = useCallback((opciones: OpcionesConfirmar) => {
    return new Promise<boolean>((resolver) => {
      setEstado({ ...opciones, resolver })
    })
  }, [])

  function cerrar(ok: boolean) {
    estado?.resolver(ok)
    setEstado(null)
  }

  const esExito = estado?.tono === 'exito'

  const modal = estado ? (
    <div className="modal-overlay" role="presentation" onClick={() => cerrar(false)}>
      <div className="modal" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
        <span className={`modal-ico ${esExito ? 'ok' : ''}`} aria-hidden="true">
          {esExito ? (
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          ) : (
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
              <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
          )}
        </span>
        <h3 className="font-display text-body-lg font-bold text-ink">{estado.titulo ?? '¿Confirmar acción?'}</h3>
        <p className="mt-2 text-body text-muted">{estado.mensaje}</p>
        <div className="modal-acciones">
          <Button variante="ghost" onClick={() => cerrar(false)}>Cancelar</Button>
          <Button variante={esExito ? 'primario' : 'peligro'} onClick={() => cerrar(true)}>
            {estado.textoConfirmar ?? 'Confirmar'}
          </Button>
        </div>
      </div>
    </div>
  ) : null

  return { confirmar, modal }
}
