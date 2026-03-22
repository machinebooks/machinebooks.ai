# Extraído de: LibroBugBounty/cap-11-kernel-rw.md
import subprocess
# Este cmd.exe se abre como NT AUTHORITY\SYSTEM
subprocess.Popen("cmd.exe", creationflags=0x10)  # CREATE_NEW_CONSOLE
