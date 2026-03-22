// Extraído de: LibroCISO/cap-19-dashboards-copiloto.md
// Ejemplo didáctico: uso del formulario de brecha con React Hook Form
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

function BreachNotificationForm() {
  const form = useForm<BreachFormData>({
    resolver: zodResolver(breachFormSchema),
    defaultValues: {
      nature: undefined,
      affected_categories: [],
      notify_data_subjects: false,
      detected_at: new Date().toISOString(),
    },
  });

  const onSubmit = async (data: BreachFormData) => {
    // 1. Guardar la brecha en el backend
    const breach = await api.post("/api/v1/privacy/breaches", data);

    // 2. Si se solicita, el copiloto genera el borrador de notificación
    if (data.notify_data_subjects) {
      await api.post(`/api/v1/privacy/breaches/${breach.id}/draft-notification`);
    }
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
      {/* Sección: Naturaleza de la brecha (Art. 33.3.a) */}
      <fieldset className="rounded-lg border p-4">
        <legend className="px-2 text-sm font-semibold text-slate-700">
          Naturaleza de la violación — Art. 33.3.a
        </legend>
        {/* Campos con form.register("nature") etc. */}
      </fieldset>

      {/* Sección: Interesados afectados (Art. 33.3.a) */}
      <fieldset className="rounded-lg border p-4">
        <legend className="px-2 text-sm font-semibold text-slate-700">
          Interesados afectados — Art. 33.3.a
        </legend>
        {/* Campos de categorías y conteo */}
      </fieldset>

      {/* Sección: Consecuencias y medidas (Art. 33.3.c-d) */}
      <fieldset className="rounded-lg border p-4">
        <legend className="px-2 text-sm font-semibold text-slate-700">
          Consecuencias y medidas — Art. 33.3.c-d
        </legend>
        {/* Textareas con asistencia IA opcional */}
      </fieldset>

      <button
        type="submit"
        disabled={form.formState.isSubmitting}
        className="rounded-lg bg-blue-600 px-6 py-2 text-white
                   hover:bg-blue-700 disabled:opacity-50"
      >
        Registrar brecha
      </button>
    </form>
  );
}
