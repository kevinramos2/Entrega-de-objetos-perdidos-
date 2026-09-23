import { Badge, BadgeEstadoObjeto, BadgeEstadoSolicitud } from '../components/Badge'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { CategoryIcon } from '../components/CategoryIcon'
import { Input, Select, Textarea } from '../components/Input'
import { Logo } from '../components/Logo'
import { StatCard } from '../components/StatCard'
import { TopNav } from '../components/TopNav'

function Seccion({ titulo, children }: { titulo: string; children: React.ReactNode }) {
  return (
    <section className="flex flex-col gap-4">
      <h2 className="font-display text-heading-sm font-bold text-ink">{titulo}</h2>
      {children}
    </section>
  )
}

export default function StyleGuide() {
  return (
    <div className="min-h-screen bg-canvas pb-24">
      <TopNav
        enlaces={[{ etiqueta: 'Inicio', activo: true }, { etiqueta: 'Objetos perdidos' }, { etiqueta: 'Mis reclamos' }]}
        acciones={<Button variante="primario" tamano="sm">Iniciar sesión</Button>}
      />

      <header className="mx-auto mt-14 max-w-3xl px-4 text-center">
        <Logo />
        <h1 className="mx-auto mt-6 max-w-xl font-display text-heading-lg font-bold text-ink">
          Sistema de diseño de Perdidos &amp; Encontrados
        </h1>
        <p className="mx-auto mt-3 max-w-xl text-body-lg text-muted">
          Verde esmeralda institucional, Sora + Inter, tarjetas blancas sobre gris claro. El pulido
          de espaciado y bordes viene de las referencias en <code className="font-mono text-caption">desing/</code>,
          la paleta y la tipografía son las que ya tenía la app.
        </p>
      </header>

      <main className="mx-auto mt-14 flex max-w-3xl flex-col gap-16 px-4">
        <Seccion titulo="Hero con degradado de marca">
          <div className="rounded-card-lg bg-hero-gradient p-10 text-center text-white">
            <h3 className="font-display text-heading font-bold">¿Perdiste algo?</h3>
            <p className="mt-2 text-body-lg text-white/85">Aquí puede estar esperándote.</p>
            <Button variante="invertido" className="mt-5">
              Ingresar
            </Button>
          </div>
        </Seccion>

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
            <Badge tono="info">Sede Minas</Badge>
          </div>
        </Seccion>

        <Seccion titulo="Íconos de categoría">
          <div className="flex flex-wrap gap-3">
            {['termo', 'documento', 'cargador', 'tecnologia', 'lonchera', 'llaves', 'ropa', 'otros'].map((clave) => (
              <span key={clave} className="flex h-12 w-12 items-center justify-center rounded-input bg-primary-wash text-primary">
                <CategoryIcon clave={clave} />
              </span>
            ))}
          </div>
        </Seccion>

        <Seccion titulo="Tarjetas">
          <div className="grid gap-4 sm:grid-cols-2">
            <Card className="flex flex-col gap-3">
              <div className="flex items-start justify-between">
                <h3 className="font-display text-body-lg font-bold text-ink">Termo negro 500ml</h3>
                <BadgeEstadoObjeto estado="disponible" etiqueta="Disponible" />
              </div>
              <p className="text-body text-muted">
                Encontrado en la cafetería, Sede Minas. Registrado el 12 de marzo.
              </p>
              <div className="mt-2 flex gap-2">
                <Button variante="primario" tamano="sm">Ver detalles</Button>
                <Button variante="ghost" tamano="sm">Compartir</Button>
              </div>
            </Card>
            <Card tono="oscuro" className="flex flex-col gap-3">
              <div className="flex items-start justify-between">
                <h3 className="font-display text-body-lg font-bold text-on-dark">Panel administrativo</h3>
                <Badge tono="primary">28% recuperados</Badge>
              </div>
              <p className="text-body text-on-dark-muted">
                El panel usa un sidebar oscuro con el mismo verde institucional, para sesiones
                largas de lectura sin perder la identidad de marca.
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
            <StatCard etiqueta="Tasa de recuperación" valor="68%" detalle="del total reportado" />
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
