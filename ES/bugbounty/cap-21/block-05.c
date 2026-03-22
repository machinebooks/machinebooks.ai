// Extraído de: LibroBugBounty/cap-21-caso-steam.md
/* Forward de exports a la DLL real del sistema */
#pragma comment(linker, "/export:GetFileVersionInfoA=C:\\Windows\\SysWOW64\\VERSION.GetFileVersionInfoA")
#pragma comment(linker, "/export:GetFileVersionInfoW=C:\\Windows\\SysWOW64\\VERSION.GetFileVersionInfoW")
/* ... 15 exports mas ... */
