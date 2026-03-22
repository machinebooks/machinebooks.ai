// Extraído de: LibroBugBounty/cap-27-caso-whatsapp.md
// Hook fetch para capturar descargas de medios
var origFetch = window.fetch;
window.fetch = function(url, opts) {
    var u = String(url);
    // Detectar descargas del CDN de WhatsApp
    if (u.indexOf('mmg.whatsapp.net') > -1 ||
        u.indexOf('media') > -1) {
        send({type:'MEDIA_DOWNLOAD', url:u.substring(0,300)});

        return origFetch.apply(this, arguments)
            .then(function(resp) {
                var cloned = resp.clone();
                cloned.blob().then(function(blob) {
                    if (blob.size > 0 && blob.size < 5000000) {
                        var reader = new FileReader();
                        reader.onload = function() {
                            send({
                                type:'MEDIA_CAPTURED',
                                size: blob.size,
                                mimeType: blob.type,
                                // Solo el primer KB como prueba
                                preview: reader.result
                                    .substring(0, 1000)
                            });
                        };
                        reader.readAsDataURL(blob);
                    }
                });
                return resp;
            });
    }
    return origFetch.apply(this, arguments);
};
