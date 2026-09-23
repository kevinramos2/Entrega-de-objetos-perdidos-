import { useState } from 'react'
import { SEDES } from '../api/estudiante'
import { CategoryIcon } from '../components/CategoryIcon'
import { ObjetoCard } from '../components/ObjetoCard'
import { useCategorias, useObjetos } from '../hooks/useEstudianteApi'

function Chip({ activo, onClick, children }: { activo: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 rounded-pill border px-4 py-2 text-caption font-semibold transition-colors ${
        activo ? 'border-primary bg-primary text-white' : 'border-line bg-surface text-ink-soft hover:border-primary/40'
      }`}
    >
      {children}
    </button>
  )
}

export default function Objetos() {
  const [q, setQ] = useState('')
  const [categoria, setCategoria] = useState('')
  const [sede, setSede] = useState('')

  const { data: categorias } = useCategorias()
  const { data: objetos, isLoading } = useObjetos({ q, categoria, sede })

  return (
    <div className="flex flex-col gap-6">
      <header>
        <h1 className="font-display text-heading font-bold text-ink">Objetos disponibles</h1>
        <p className="mt-1 text-body text-muted">Busca por nombre, categoría o lugar donde se encontró.</p>
      </header>

      <div className="flex items-center gap-2 rounded-pill border border-line bg-surface px-4 py-1 shadow-card">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="text-muted">
          <circle cx="11" cy="11" r="7" />
          <path d="m21 21-4.35-4.35" />
        </svg>
        <input
          value={q}
          onChange={(evento) => setQ(evento.target.value)}
          placeholder="Buscar por nombre, descripción o lugar…"
          className="w-full bg-transparent py-2.5 text-body text-ink placeholder:text-muted focus:outline-none"
        />
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <span className="text-caption font-semibold text-muted">Sede:</span>
        <Chip activo={sede === ''} onClick={() => setSede('')}>Todas</Chip>
        {SEDES.map((s) => (
          <Chip key={s.value} activo={sede === s.value} onClick={() => setSede(s.value)}>
            {s.label}
          </Chip>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Chip activo={categoria === ''} onClick={() => setCategoria('')}>
          <CategoryIcon clave="otros" size={16} />
          Todas las categorías
        </Chip>
        {categorias?.map((cat) => (
          <Chip key={cat.id} activo={categoria === String(cat.id)} onClick={() => setCategoria(String(cat.id))}>
            <CategoryIcon clave={cat.icono} size={16} />
            {cat.nombre}
          </Chip>
        ))}
      </div>

      {isLoading && <p className="text-body text-muted">Cargando objetos…</p>}

      {objetos && objetos.length === 0 && (
        <p className="rounded-card border border-line bg-surface p-8 text-center text-body text-muted shadow-card">
          No encontramos objetos con esos filtros. Prueba con otra búsqueda.
        </p>
      )}

      {objetos && objetos.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {objetos.map((objeto) => (
            <ObjetoCard key={objeto.id} objeto={objeto} />
          ))}
        </div>
      )}
    </div>
  )
}
