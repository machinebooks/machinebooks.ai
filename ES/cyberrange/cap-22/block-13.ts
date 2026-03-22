// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// Uso del sistema de traducción en componentes
const GamingZone: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('gamingZone.title')}</h1>
      <p>{t('gamingZone.errorLoading')}</p>
      <span>{t('gamingZone.difficulty.hard')}</span>
    </div>
  );
};
