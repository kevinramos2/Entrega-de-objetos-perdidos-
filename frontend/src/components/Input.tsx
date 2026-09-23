import { forwardRef, type InputHTMLAttributes, type LabelHTMLAttributes, type SelectHTMLAttributes, type TextareaHTMLAttributes } from 'react'

const CAMPO_BASE =
  'w-full rounded-input border border-line bg-surface px-4 py-2.5 text-body text-ink ' +
  'placeholder:text-muted transition-colors duration-150 ' +
  'focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/15'

interface CampoWrapperProps {
  label?: string
  error?: string
  ayuda?: string
  id: string
}

function Etiqueta({ children, ...props }: LabelHTMLAttributes<HTMLLabelElement>) {
  return (
    <label className="mb-1.5 block text-caption font-medium text-muted" {...props}>
      {children}
    </label>
  )
}

function Mensajes({ error, ayuda }: { error?: string; ayuda?: string }) {
  if (error) return <p className="mt-1.5 text-caption text-danger">{error}</p>
  if (ayuda) return <p className="mt-1.5 text-caption text-muted">{ayuda}</p>
  return null
}

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement> & CampoWrapperProps>(
  ({ label, error, ayuda, id, className = '', ...props }, ref) => (
    <div>
      {label && <Etiqueta htmlFor={id}>{label}</Etiqueta>}
      <input
        id={id}
        ref={ref}
        className={`${CAMPO_BASE} ${error ? 'border-danger' : ''} ${className}`}
        {...props}
      />
      <Mensajes error={error} ayuda={ayuda} />
    </div>
  ),
)
Input.displayName = 'Input'

export const Textarea = forwardRef<
  HTMLTextAreaElement,
  TextareaHTMLAttributes<HTMLTextAreaElement> & CampoWrapperProps
>(({ label, error, ayuda, id, className = '', ...props }, ref) => (
  <div>
    {label && <Etiqueta htmlFor={id}>{label}</Etiqueta>}
    <textarea id={id} ref={ref} className={`${CAMPO_BASE} resize-none ${className}`} {...props} />
    <Mensajes error={error} ayuda={ayuda} />
  </div>
))
Textarea.displayName = 'Textarea'

export const Select = forwardRef<
  HTMLSelectElement,
  SelectHTMLAttributes<HTMLSelectElement> & CampoWrapperProps
>(({ label, error, ayuda, id, className = '', children, ...props }, ref) => (
  <div>
    {label && <Etiqueta htmlFor={id}>{label}</Etiqueta>}
    <select id={id} ref={ref} className={`${CAMPO_BASE} ${className}`} {...props}>
      {children}
    </select>
    <Mensajes error={error} ayuda={ayuda} />
  </div>
))
Select.displayName = 'Select'
