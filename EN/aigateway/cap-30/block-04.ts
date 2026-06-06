// Extracted from: LibroAIGateway/cap-30-user-portal.md
// admin-panel/src/portal/pages/Account.tsx (excerpt)
<InfoTile label={t('portal.account.organization')}
          value={portal.organization.name || '-'} />
<InfoTile label={t('portal.account.access')}
          value={portal.user.auth_source?.toUpperCase() || 'LOCAL'} />
<InfoTile label={portal.account.mfa'}
          value={portal.user.mfa_enabled ? 'ON' : 'OFF'} />
