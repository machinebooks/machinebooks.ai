# Extraído de: LibroUsuario/cap-21-la-nube-desde-el-cli.md
aws ec2 describe-instances \
  --query 'Reservations[].Instances[].{
    ID: InstanceId,
    Name: Tags[?Key==`Name`].Value | [0],
    Type: InstanceType,
    State: State.Name,
    Env: Tags[?Key==`Environment`].Value | [0],
    LaunchTime: LaunchTime
  }' \
  --output table
