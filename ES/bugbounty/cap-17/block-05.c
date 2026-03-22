// Extraído de: LibroBugBounty/cap-17-poc-impacto.md
// Forwarding via pragma — más simple pero menos control
#pragma comment(linker, "/export:GetFileVersionInfoA=C:\\Windows\\System32\\version.GetFileVersionInfoA")
#pragma comment(linker, "/export:GetFileVersionInfoW=C:\\Windows\\System32\\version.GetFileVersionInfoW")
// ... (17 líneas, una por export)
