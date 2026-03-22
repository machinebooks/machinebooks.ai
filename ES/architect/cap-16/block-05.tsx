// Extraído de: LibroTecnico/cap-16-react-ia.md
// Prompt estructurado: "Genera un formulario de creación de propuesta
// con react-hook-form + zod. El tipo de propuesta determina los campos
// visibles. Los tipos son: 'ejecutiva', 'base', 'técnica', 'marco', 'express'.
// El campo presupuesto_estimado es obligatorio solo para tipo 'ejecutiva' y 'marco'.
// El cliente se selecciona de un combo con búsqueda. Validar que la fecha
// de entrega sea al menos 5 días posterior a la fecha actual."

import { useForm, Controller } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { addDays, isAfter } from 'date-fns'

const proposalTypes = ['ejecutiva', 'base', 'técnica', 'marco', 'express'] as const

const proposalSchema = z.object({
  title: z.string().min(10, 'El título debe tener al menos 10 caracteres'),
  type: z.enum(proposalTypes),
  client_id: z.number({ required_error: 'Selecciona un cliente' }),
  deadline: z.string().refine(
    (val) => isAfter(new Date(val), addDays(new Date(), 5)),
    'La fecha de entrega debe ser al menos 5 días posterior a hoy'
  ),
  estimated_budget: z.number().optional(),
  description: z.string().max(2000, 'Máximo 2.000 caracteres'),
}).refine(
  // Regla de negocio: presupuesto obligatorio para ejecutiva y marco
  (data) => {
    if (['ejecutiva', 'marco'].includes(data.type)) {
      return data.estimated_budget !== undefined && data.estimated_budget > 0
    }
    return true
  },
  { message: 'El presupuesto es obligatorio para propuestas ejecutivas y marco',
    path: ['estimated_budget'] }
)

type ProposalForm = z.infer<typeof proposalSchema>

export function CreateProposalForm({ onSuccess }: { onSuccess: () => void }) {
  const { register, control, handleSubmit, watch, formState: { errors } } =
    useForm<ProposalForm>({ resolver: zodResolver(proposalSchema) })

  const selectedType = watch('type')
  const showBudget = ['ejecutiva', 'marco'].includes(selectedType)

  // React Query mutation para enviar al backend
  const mutation = useCreateProposal({ onSuccess })

  return (
    <form onSubmit={handleSubmit((data) => mutation.mutate(data))}
          className="space-y-6 max-w-2xl">
      {/* Campos del formulario con validación visual inline */}
      <FormField label="Título" error={errors.title?.message}>
        <input {...register('title')}
               className="w-full rounded-md border-gray-300 shadow-sm" />
      </FormField>

      <FormField label="Tipo de propuesta" error={errors.type?.message}>
        <select {...register('type')} className="w-full rounded-md border-gray-300">
          {proposalTypes.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
      </FormField>

      <Controller name="client_id" control={control}
        render={({ field }) => (
          <FormField label="Cliente" error={errors.client_id?.message}>
            <ClientSearchCombo value={field.value} onChange={field.onChange} />
          </FormField>
        )}
      />

      {showBudget && (
        <FormField label="Presupuesto estimado (€)"
                   error={errors.estimated_budget?.message}>
          <input type="number" {...register('estimated_budget', { valueAsNumber: true })}
                 className="w-full rounded-md border-gray-300" />
        </FormField>
      )}

      <SubmitButton loading={mutation.isPending} label="Crear propuesta" />
    </form>
  )
}
