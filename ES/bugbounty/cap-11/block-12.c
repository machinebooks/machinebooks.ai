// Extraído de: LibroBugBounty/cap-11-kernel-rw.md
// Ejemplo: handler METHOD_NEITHER vulnerable
NTSTATUS HandleNeitherIoctl(PIRP Irp) {
    PIO_STACK_LOCATION stack = IoGetCurrentIrpStackLocation(Irp);

    // ¡PELIGRO! Estos punteros apuntan directamente a memoria de usuario
    PVOID inputBuffer = stack->Parameters.DeviceIoControl.Type3InputBuffer;
    ULONG inputLen = stack->Parameters.DeviceIoControl.InputBufferLength;

    // Sin ProbeForRead/ProbeForWrite, el driver confía ciegamente
    // en que el puntero es válido y el contenido no cambia
    PHYSICAL_ADDRESS physAddr = *(PHYSICAL_ADDRESS*)inputBuffer;
    // Un thread concurrente podría cambiar physAddr AQUÍ
    PVOID mapped = MmMapIoSpace(physAddr, ...);  // Opera con dato potencialmente modificado
}
