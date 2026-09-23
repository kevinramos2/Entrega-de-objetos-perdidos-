export default function PanelPlaceholder() {
  return (
    <div className="rounded-card-lg border border-hairline bg-mist p-10 text-center">
      <p className="font-mono text-caption uppercase tracking-widest text-terracota">Panel de administración</p>
      <h1 className="mt-3 font-display text-heading text-ink">Está en construcción</h1>
      <p className="mx-auto mt-2 max-w-md text-body text-ink-muted">
        El dashboard, la gestión de objetos y solicitudes llegan en la próxima iteración. Por ahora
        puedes seguir usando el panel clásico en <code className="font-mono text-caption">/panel/</code>.
      </p>
    </div>
  )
}
