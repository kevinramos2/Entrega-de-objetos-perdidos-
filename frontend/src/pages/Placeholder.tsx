import { Link } from 'react-router-dom'
import { Button } from '../components/Button'

export default function Placeholder() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-forest px-4 text-center">
      <p className="font-mono text-caption uppercase tracking-widest text-terracota">
        Objetos Perdidos UNAL
      </p>
      <h1 className="max-w-2xl font-display text-heading-lg leading-tight text-cream">
        El frontend en React está en construcción
      </h1>
      <p className="max-w-md text-body-lg text-cream-muted">
        La base de la API y el sistema de diseño ya están listos. Las pantallas de
        estudiante y del panel llegan en la próxima iteración.
      </p>
      <Link to="/dev/styleguide">
        <Button variante="primario">Ver el sistema de diseño</Button>
      </Link>
    </div>
  )
}
