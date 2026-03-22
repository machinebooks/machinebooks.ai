# Extraído de: LibroBugBounty/cap-11-kernel-rw.md
# Leer el puerto 0xCF8 (PCI Configuration Address)
# y 0xCFC (PCI Configuration Data) para enumerar hardware
def enumerate_pci_devices(asio):
    """Enumerar todos los dispositivos PCI via puertos I/O."""
    devices = []
    for bus in range(256):
        for dev in range(32):
            for func in range(8):
                addr = (1 << 31) | (bus << 16) | (dev << 11) | (func << 8)
                asio.ASIO_OutPortD(0xCF8, addr)
                vendor_dev = asio.ASIO_InPortD(0xCFC)
                vendor = vendor_dev & 0xFFFF
                device = (vendor_dev >> 16) & 0xFFFF
                if vendor != 0xFFFF:
                    devices.append((bus, dev, func, vendor, device))
    return devices
