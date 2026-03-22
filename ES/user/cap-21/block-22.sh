# Extraído de: LibroUsuario/cap-21-la-nube-desde-el-cli.md
# Listar VMs en Azure
az vm list -d --output table \
  --query '[].{Name:name, ResourceGroup:resourceGroup,
    Size:hardwareProfile.vmSize, State:powerState, Location:location}'
