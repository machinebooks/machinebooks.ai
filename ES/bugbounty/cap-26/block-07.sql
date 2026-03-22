# Extraído de: LibroBugBounty/cap-26-caso-discord.md
-- Abrir la base de datos de cookies de Discord
-- %APPDATA%\discord\Network\Cookies
SELECT host_key, name, value, encrypted_value
FROM cookies
WHERE host_key LIKE '%discord%';
