// Extraído de: LibroBugBounty/cap-13-vm-escape-rpc.md
// Estructura de un mensaje RPC
// [4 bytes] Length (Big-Endian) — tamaño del JSON sin contar el prefix
// [N bytes] JSON UTF-8 — el request o response

// Ejemplo: enviar {"method":"isRunning","params":{}}
// JSON tiene 38 bytes
// Message: 00 00 00 26 7B 22 6D 65 74 68 6F 64 22 3A ...
//          ^^^^^^^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
//          length=38   JSON payload

// La respuesta sigue el mismo formato:
// [4 bytes] Length (Big-Endian)
// [N bytes] JSON UTF-8 response
