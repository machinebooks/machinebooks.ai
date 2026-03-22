# Extraído de: LibroBugBounty/cap-13-vm-escape-rpc.md
# Dentro de la VM (via spawn)
$ ls -la /mnt/host/Windows/System32/config/
total 0
# Directorio vacío o acceso denegado

$ cat /mnt/host/Windows/System32/config/SAM
cat: /mnt/host/Windows/System32/config/SAM: Permission denied
