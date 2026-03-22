// Extraído de: LibroCISO/cap-18-react-grc.md
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { dpiaSchema, type DPIAFormData } from './dpia.schema'

export function DPIAForm({ onSubmit }: { onSubmit: (data: DPIAFormData) => void }) {
  const { register, handleSubmit, watch, formState: { errors } } = useForm<DPIAFormData>({
    resolver: zodResolver(dpiaSchema),
    defaultValues: { status: 'draft', involves_special_categories: false },
  })

  // Campo condicional: se muestra solo si involucra categorías especiales
  const involvesSpecial = watch('involves_special_categories')

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Descripción sistemática — Art. 35.7.a */}
      <fieldset>
        <legend className="text-lg font-semibold">
          Descripción sistemática del tratamiento
        </legend>
        <textarea
          {...register('description')}
          aria-describedby="description-error"
          className="w-full min-h-[120px] border rounded-md p-3"
          placeholder="Describa el tratamiento de forma detallada..."
        />
        {errors.description && (
          <p id="description-error" role="alert" className="text-red-600 text-sm mt-1">
            {errors.description.message}
          </p>
        )}
      </fieldset>

      {/* ... resto de campos con el mismo patrón ARIA ... */}

      {/* Campo condicional: categorías especiales */}
      {involvesSpecial && (
        <fieldset>
          <legend>Justificación de categorías especiales (Art. 9 RGPD)</legend>
          <textarea
            {...register('special_categories_justification')}
            aria-required="true"
            className="w-full min-h-[80px] border rounded-md p-3"
          />
          {errors.special_categories_justification && (
            <p role="alert" className="text-red-600 text-sm mt-1">
              {errors.special_categories_justification.message}
            </p>
          )}
        </fieldset>
      )}

      <button type="submit" className="px-6 py-2 bg-blue-700 text-white rounded-md">
        Guardar evaluación
      </button>
    </form>
  )
}
