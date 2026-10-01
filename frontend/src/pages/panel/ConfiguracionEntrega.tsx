import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Badge } from '../../components/Badge'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { Textarea } from '../../components/Input'
import { useActualizarConfiguracionEntrega, useConfiguracionEntrega } from '../../hooks/usePanelApi'
import { useToast } from '../../lib/toast-context'

export default function ConfiguracionEntrega() {
  const { data } = useConfiguracionEntrega()
  const actualizar = useActualizarConfiguracionEntrega()
  const toast = useToast()

  const [textoMinas, setTextoMinas] = useState('')
  const [textoVolador, setTextoVolador] = useState('')

  useEffect(() => {
    if (!data) return
    setTextoMinas(data.texto_minas)
    setTextoVolador(data.texto_volador)
  }, [data])

  async function enviar(evento: FormEvent) {
    evento.preventDefault()
    try {
      await actualizar.mutateAsync({ texto_minas: textoMinas, texto_volador: textoVolador })
      toast.mostrar('Instrucciones de entrega actualizadas.', 'exito')
    } catch {
      toast.mostrar('No pudimos guardar las instrucciones.', 'error')
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <header>
        <p className="text-caption text-muted">Configuración</p>
        <h1 className="font-display text-heading font-bold text-ink">Entrega del objeto</h1>
      </header>

      <Card className="mx-auto w-full max-w-2xl">
        <p className="text-body text-muted">
          Cada sede tiene sus propias instrucciones. El estudiante verá el texto de la sede que elijas al
          aprobar su solicitud (a menos que escribas un texto específico en esa aprobación). Indica dónde,
          cuándo y cómo debe reclamar.
        </p>
        <form onSubmit={enviar} className="mt-4 flex flex-col gap-4">
          <div>
            <label className="mb-1.5 flex items-center gap-2 text-caption font-medium text-muted" htmlFor="texto_minas">
              <Badge tono="info">Sede Minas</Badge> Instrucciones de entrega
            </label>
            <Textarea id="texto_minas" rows={4} value={textoMinas} onChange={(e) => setTextoMinas(e.target.value)} />
          </div>
          <div>
            <label className="mb-1.5 flex items-center gap-2 text-caption font-medium text-muted" htmlFor="texto_volador">
              <Badge tono="accent">Sede El Volador</Badge> Instrucciones de entrega
            </label>
            <Textarea id="texto_volador" rows={4} value={textoVolador} onChange={(e) => setTextoVolador(e.target.value)} />
          </div>
          <div className="flex gap-3">
            <Button type="submit" variante="primario" disabled={actualizar.isPending}>
              {actualizar.isPending ? 'Guardando…' : 'Guardar instrucciones'}
            </Button>
            <Link to="/panel/solicitudes">
              <Button type="button" variante="ghost">Cancelar</Button>
            </Link>
          </div>
        </form>
      </Card>
    </div>
  )
}
