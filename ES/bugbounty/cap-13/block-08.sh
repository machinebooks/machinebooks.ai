# Extraído de: LibroBugBounty/cap-13-vm-escape-rpc.md
# Desde PowerShell
Get-Process -Name "Claude" | Select-Object Id, ProcessName, Path
# Output:
#   Id ProcessName Path
#   -- ----------- ----
# 8472 Claude      C:\Users\hunter\AppData\Local\AnthropicClaude\Claude.exe
