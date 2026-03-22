// Extraído de: LibroBugBounty/cap-07-firma-codigo.md
// Modelo de seguridad de VS Code (simplificado)
// Cada punto corresponde a un vector de bypass

// 1. Contra ASAR tampering: fuses habilitados
// OnlyLoadAppFromAsar: true
// EnableEmbeddedAsarIntegrityValidation: true

// 2. Contra DLL sideloading: directorio protegido
// InstalaciÃ³n en C:\Program Files\Microsoft VS Code
// Requiere admin para modificar

// 3. Contra NODE_OPTIONS injection: fuse deshabilitado
// EnableNodeOptionsEnvironmentVariable: false
// El proceso ignora NODE_OPTIONS completamente

// 4. Contra abuso de Squirrel: actualizaciÃ³n segura
// VS Code usa su propio mecanismo de actualizaciÃ³n
// con verificaciÃ³n de firma del paquete descargado

// 5. Contra bypass de WINTRUST: no aplica
// VS Code no ejecuta servicios como SYSTEM
// que necesiten verificar firmas de terceros

// 6. VerificaciÃ³n de integridad runtime
// VS Code tiene un mecanismo de verificaciÃ³n de integridad
// que detecta modificaciones en los ficheros de la app
// Muestra un warning "Your Code installation appears to be corrupt"
