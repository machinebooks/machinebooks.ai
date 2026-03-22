// Extraído de: LibroTecnico/cap-22-observabilidad.md
// Banner informativo global — EU AI Act Art. 52 (Transparencia)
export default function AIDisclaimerBanner() {
  const [dismissed, setDismissed] = useState(() => {
    return localStorage.getItem('ai_disclaimer_dismissed') === 'true';
  });

  if (dismissed) return null;

  return (
    <div className="bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50
                    border-b border-indigo-100 px-4 py-2">
      <p className="text-xs text-gray-700">
        <strong>Aviso IA:</strong> Esta aplicación utiliza inteligencia artificial
        para análisis, evaluaciones y recomendaciones. Las respuestas generadas
        por IA pueden contener errores — verifique la información antes de
        tomar decisiones.
      </p>
    </div>
  );
}
