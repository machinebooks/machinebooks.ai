// Extraído de: LibroBugBounty/cap-11-kernel-rw.md
// Pseudocódigo del handler de IOCTL 0x222400 (reconstruido)
NTSTATUS HandleMapPhysicalMemory(PIRP Irp) {
    PIO_STACK_LOCATION stack = IoGetCurrentIrpStackLocation(Irp);
    PASIO3_MAP_REQUEST req = Irp->AssociatedIrp.SystemBuffer;

    // NO hay verificación de privilegios del caller
    // NO hay validación del rango de dirección física
    // NO hay límite en el tamaño del mapeo

    PVOID mapped = MmMapIoSpace(
        req->PhysicalAddress,
        req->NumberOfBytes,
        req->CacheType
    );

    // Devolver dirección virtual al caller
    *(PVOID*)Irp->AssociatedIrp.SystemBuffer = mapped;
    Irp->IoStatus.Information = sizeof(PVOID);
    Irp->IoStatus.Status = STATUS_SUCCESS;
    IoCompleteRequest(Irp, IO_NO_INCREMENT);
    return STATUS_SUCCESS;
}
