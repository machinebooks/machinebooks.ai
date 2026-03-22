// Extraído de: LibroBugBounty/cap-07-firma-codigo.md
// Llamada tÃ­pica a WinVerifyTrust
LONG lStatus;
WINTRUST_DATA WinTrustData;
WINTRUST_FILE_INFO FileData;
GUID WVTPolicyGUID = WINTRUST_ACTION_GENERIC_VERIFY_V2;

// Configurar FileData con la ruta del fichero
FileData.cbStruct = sizeof(WINTRUST_FILE_INFO);
FileData.pcwszFilePath = L"C:\\path\\to\\binary.exe";
FileData.hFile = NULL;
FileData.pgKnownSubject = NULL;

// Configurar WinTrustData
WinTrustData.cbStruct = sizeof(WINTRUST_DATA);
WinTrustData.dwUIChoice = WTD_UI_NONE;  // Sin diÃ¡logo
WinTrustData.fdwRevocationChecks = WTD_REVOKE_NONE;
WinTrustData.dwUnionChoice = WTD_CHOICE_FILE;
WinTrustData.pFile = &FileData;
WinTrustData.dwStateAction = WTD_STATEACTION_VERIFY;
WinTrustData.dwProvFlags = WTD_SAFER_FLAG;

// Verificar
lStatus = WinVerifyTrust(NULL, &WVTPolicyGUID, &WinTrustData);

// lStatus == ERROR_SUCCESS â†’ firma vÃ¡lida
// lStatus == TRUST_E_NOSIGNATURE â†’ sin firma
// lStatus == TRUST_E_BAD_DIGEST â†’ firma rota (fichero modificado)
