# Extraído de: LibroBugBounty/cap-13-vm-escape-rpc.md
# Compilar el injector (busca Claude.exe y le inyecta la DLL)
gcc -o injector.exe injector.c -lkernel32

# Compilar la DLL que conecta al pipe
gcc -shared -o pipe_inject.dll pipe_inject.c -lkernel32
