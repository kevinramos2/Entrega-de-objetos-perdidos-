import { Badge, BadgeEstadoObjeto, BadgeEstadoSolicitud } from '../components/Badge'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { Input, Select, Textarea } from '../components/Input'
import { PillNav } from '../components/PillNav'
import { StatCard } from '../components/StatCard'

function Seccion({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <section className="flex flex-col gap-4">
      <h2 className="font-display text-heading-sm text-ink">{titulo}</h2>
      {children}
    </section>
  )
}

export default function StyleGuide() {
  return (
    <div className="min-h-screen bg-paper pb-24">
      <div className="px-4 pt-6">
        <PillNav
          marca="Objetos Perdidos"
          enlaces={[
            { etiqueta: 'Inicio', activo: true },
            { etiqueta: 'Objetos' },
            { etiqueta: 'Mis solicitudes' },
          ]}
          acciones={<Button variante="primario" tamano="sm">Ingresar</Button>}
        />
      </div>

      <header className="mx-auto mt-12 max-w-3xl px-4 text-center">
        <p className="font-mono text-caption uppercase tracking-widest text-terracota">
          Sistema de diseño · Editorial cálido
        </p>
        <h1 className="mt-3 font-display text-display leading-none text-ink">
          Cada objeto <span className="text-terracota">tiene</span> un dueño
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-body-lg text-ink-muted">
          Fusión propia inspirada en Steep (serif editorial sobre papel) y Tomorro (acentos vivos,
          secciones oscuras alternadas), adaptada a un servicio universitario de objetos
          perdidos y reencontrados.
        </p>
      </header>

      <main className="mx-auto mt-16 flex max-w-3xl flex-col gap-16 px-4">
        <Seccion titulo="Botones">
          <div className="flex flex-wrap items-center gap-3">
            <Button variante="primario">Solicitar reclamo</Button>
            <Button variante="ghost">Ver detalles</Button>
            <Button variante="peligro">Eliminar</Button>
            <Button variante="primario" tamano="sm">Guardar</Button>
            <Button variante="ghost" disabled>Deshabilitado</Button>
          </div>
        </Seccion>

        <Seccion titulo="Insignias de estado">
          <div className="flex flex-wrap gap-3">
            <BadgeEstadoObjeto estado="disponible" etiqueta="Disponible" />
            <BadgeEstadoObjeto estado="reclamado" etiqueta="Reclamado" />
            <BadgeEstadoObjeto estado="entregado" etiqueta="Entregado" />
            <BadgeEstadoSolicitud estado="pendiente" etiqueta="Pendiente" />
            <BadgeEstadoSolicitud estado="apelada" etiqueta="Apelada" />
            <BadgeEstadoSolicitud estado="aprobada" etiqueta="Aprobada" />
            <BadgeEstadoSolicitud estado="rechazada" etiqueta="Rechazada" />
            <Badge tono="neutro">#128</Badge>
          </div>
        </Seccion>

        <Seccion titulo="Tarjetas de objeto">
          <div className="grid gap-4 sm:grid-cols-2">
            <Card className="flex flex-col gap-3">
              <div className="flex items-start justify-between">
                <h3 className="font-display text-heading-sm text-ink">Termo negro 500ml</h3>
                <BadgeEstadoObjeto estado="disponible" etiqueta="Disponible" />
              </div>
              <p className="text-body text-ink-muted">
                Encontrado en la cafetería, Sede Minas. Registrado el 12 de marzo.
              </p>
              <div className="mt-2 flex gap-2">
                <Button variante="primario" tamano="sm">Ver detalles</Button>
                <Button variante="ghost" tamano="sm">Compartir</Button>
              </div>
            </Card>
            <Card tono="oscuro" className="flex flex-col gap-3">
              <div className="flex items-start justify-between">
                <h3 className="font-display text-heading-sm text-cream">Panel administrativo</h3>
                <Badge tono="salvia">28% recuperados</Badge>
              </div>
              <p className="text-body text-cream-muted">
                Las secciones oscuras se usan en el hero público y en el panel de
                administración para sesiones largas de lectura.
              </p>
              <Button variante="ghost-oscuro" tamano="sm" className="mt-2 self-start">
                Ir al panel
              </Button>
            </Card>
          </div>
        </Seccion>

        <Seccion titulo="Indicadores (dashboard)">
          <div className="grid gap-4 sm:grid-cols-3">
            <StatCard etiqueta="Disponibles" valor="42" detalle="objetos esperando dueño" />
            <StatCard etiqueta="Tasa de recuperación" valor="68%" tono="oscuro" detalle="del total reportado" />
            <StatCard etiqueta="Por revisar" valor="5" detalle="solicitudes pendientes" />
          </div>
        </Seccion>

        <Seccion titulo="Formulario">
          <Card className="flex flex-col gap-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <Input id="doc" label="Número de documento" placeholder="1036645213" />
              <Select id="tipo-doc" label="Tipo de documento" defaultValue="CC">
                <option value="CC">Cédula de ciudadanía</option>
                <option value="TI">Tarjeta de identidad</option>
                <option value="CE">Cédula de extranjería</option>
              </Select>
            </div>
            <Textarea
              id="mensaje"
              label="¿Por qué crees que es tuyo?"
              rows={3}
              placeholder="Es azul, tiene un sticker de..."
            />
            <Input id="con-error" label="Teléfono" error="Escribe tu teléfono de contacto." />
            <Button variante="primario" className="self-start">Enviar solicitud</Button>
          </Card>
        </Seccion>
      </main>
    </div>
  )
}
