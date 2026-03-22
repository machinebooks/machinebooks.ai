// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// TranslationContext.tsx — Sistema de internacionalización
type Language = 'es' | 'en';

const TranslationProvider: React.FC = ({ children }) => {
  const [language, setLanguageState] = useState<Language>('es');

  useEffect(() => {
    // Detectar idioma del navegador al inicializar
    const browserLang = navigator.language.split('-')[0];
    const savedLang = localStorage.getItem('language') as Language;

    if (savedLang && ['es', 'en'].includes(savedLang)) {
      setLanguageState(savedLang);
    } else if (['es', 'en'].includes(browserLang)) {
      setLanguageState(browserLang as Language);
    } else {
      setLanguageState('en'); // Fallback a inglés
    }
  }, []);

  // Función de traducción con notación punto
  const t = (key: string, section?: string): string => {
    const translations = textsData.translations[language];
    const keys = key.split('.');
    let value: any = translations;

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return key; // Si no existe la traducción, devolver la clave
      }
    }
    return typeof value === 'string' ? value : key;
  };
};
