export default function PanelPlaceholder() {
  return (
    <div className="rounded-card-lg border border-line bg-surface p-10 text-center shadow-card">
      <p className="text-caption font-semibold uppercase tracking-widest text-primary">Panel de administración</p>
      <h1 className="mt-3 font-display text-heading font-bold text-ink">Está en construcción</h1>
      <p className="mx-auto mt-2 max-w-md text-body text-muted">
        Esta sección todavía no está conectada en React. Por ahora puedes seguir usando el panel
        clásico en <code className="font-mono text-caption">/panel/</code>.
      </p>
    </div>
  )
}
