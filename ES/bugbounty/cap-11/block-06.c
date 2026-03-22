// Extraído de: LibroBugBounty/cap-11-kernel-rw.md
// Estructura del buffer de entrada para IOCTL 0x222400
typedef struct _ASIO3_MAP_REQUEST {
    PHYSICAL_ADDRESS PhysicalAddress;  // offset 0, 8 bytes
    ULONG            NumberOfBytes;    // offset 8, 4 bytes
    ULONG            CacheType;        // offset 12, 4 bytes
} ASIO3_MAP_REQUEST;
// Total: 16 bytes
// El buffer de salida (8 bytes) contiene la dirección virtual mapeada
