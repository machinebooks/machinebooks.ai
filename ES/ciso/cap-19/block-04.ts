// Extraído de: LibroCISO/cap-19-dashboards-copiloto.md
// Ejemplo didáctico: esquema Zod para formulario de brecha (Art. 33 RGPD)
import { z } from "zod";

export const breachFormSchema = z.object({
  // Art. 33.3.a: naturaleza de la violación de seguridad
  nature: z.enum(
    ["confidentiality", "integrity", "availability", "combined"],
    { required_error: "Obligatorio: Art. 33.3.a RGPD" }
  ),
  description: z
    .string()
    .min(50, "Describa la brecha con suficiente detalle (mín. 50 caracteres)")
    .max(5000),

  // Art. 33.3.a: categorías y número aproximado de interesados
  affected_categories: z
    .array(z.string())
    .min(1, "Indique al menos una categoría de interesados afectados"),
  estimated_affected_count: z
    .number()
    .min(0, "Indique un número estimado de interesados afectados"),

  // Art. 33.3.a: categorías y número aproximado de registros
  affected_record_types: z
    .array(z.string())
    .min(1, "Indique al menos un tipo de registro afectado"),
  estimated_records_count: z.number().min(0),

  // Art. 33.3.b: nombre y datos de contacto del DPO
  dpo_name: z.string().min(1, "El nombre del DPO es obligatorio"),
  dpo_email: z.string().email("Formato de email no válido"),
  dpo_phone: z.string().optional(),

  // Art. 33.3.c: consecuencias probables
  probable_consequences: z
    .string()
    .min(20, "Describa las consecuencias probables de la brecha"),

  // Art. 33.3.d: medidas adoptadas o propuestas
  measures_taken: z
    .string()
    .min(20, "Describa las medidas adoptadas o propuestas para mitigar"),

  // Campos operativos (no requeridos por Art. 33, pero necesarios)
  detected_at: z.string().datetime(),
  detection_source: z.enum([
    "internal_monitoring", "user_report", "external_notification",
    "audit", "automated_alert", "other",
  ]),
  severity: z.enum(["low", "medium", "high", "critical"]),

  // ¿Requiere notificación a interesados? (Art. 34)
  notify_data_subjects: z.boolean().default(false),

  // Tratamientos afectados (relación con el módulo de privacidad)
  affected_treatment_ids: z.array(z.number()).optional(),
});

export type BreachFormData = z.infer<typeof breachFormSchema>;
