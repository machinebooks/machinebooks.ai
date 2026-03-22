// Extraído de: LibroCISO/cap-18-react-grc.md
import { z } from 'zod'

/** Esquema de validación para DPIA — refleja Art. 35 RGPD + criterios AEPD */
export const dpiaSchema = z.object({
  // Identificación del tratamiento evaluado
  name: z.string()
    .min(5, 'El nombre debe tener al menos 5 caracteres')
    .max(200, 'Máximo 200 caracteres'),
  processing_id: z.number({
    required_error: 'Debe vincular la DPIA a un tratamiento existente',
  }),

  // Descripción sistemática (Art. 35.7.a RGPD)
  description: z.string()
    .min(50, 'La descripción debe ser suficientemente detallada (mín. 50 caracteres)')
    .max(5000),
  purpose: z.string().min(10, 'Indique la finalidad del tratamiento'),
  legal_basis: z.string().min(1, 'La base jurídica es obligatoria'),

  // Evaluación de necesidad y proporcionalidad (Art. 35.7.b)
  necessity_assessment: z.string()
    .min(20, 'Evalúe la necesidad del tratamiento'),
  proportionality_assessment: z.string()
    .min(20, 'Evalúe la proporcionalidad del tratamiento'),

  // Riesgos para los derechos y libertades (Art. 35.7.c)
  risk_description: z.string()
    .min(20, 'Describa los riesgos identificados'),
  risk_likelihood: z.enum(['very_low', 'low', 'medium', 'high', 'very_high'], {
    required_error: 'Seleccione la probabilidad del riesgo',
  }),
  risk_severity: z.enum(['very_low', 'low', 'medium', 'high', 'very_high'], {
    required_error: 'Seleccione la severidad del impacto',
  }),

  // Medidas para afrontar los riesgos (Art. 35.7.d)
  mitigation_measures: z.string()
    .min(20, 'Describa las medidas de mitigación previstas'),

  // Campos adicionales de gestión
  status: z.enum(['draft', 'in_progress', 'pending_review', 'approved', 'rejected'])
    .default('draft'),
  reviewer_notes: z.string().max(2000).optional(),
  review_date: z.string().optional(),

  // Campo condicional: si involucra categorías especiales, requiere justificación
  involves_special_categories: z.boolean().default(false),
  special_categories_justification: z.string().optional(),
}).refine(
  (data) => {
    // Si involucra categorías especiales, la justificación es obligatoria
    if (data.involves_special_categories && !data.special_categories_justification) {
      return false
    }
    return true
  },
  {
    message: 'Debe justificar el tratamiento de categorías especiales de datos',
    path: ['special_categories_justification'],
  }
)

/** Tipo TypeScript inferido del esquema — fuente única de verdad */
export type DPIAFormData = z.infer<typeof dpiaSchema>
