// Extraído de: LibroCISO/cap-18-react-grc.md
import { useTranslation } from 'react-i18next'

export function ProcessingStatusBadge({ status }: { status: string }) {
  const { t } = useTranslation('privacy')
  return (
    <span className={`badge badge-${status}`}>
      {t(`processing.status.${status}`)}
    </span>
  )
}
