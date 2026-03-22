# Extraído de: LibroUsuario/cap-21-la-nube-desde-el-cli.md
# 1. Grupos de seguridad con SSH abierto al mundo
echo "=== SSH abierto a 0.0.0.0/0 ==="
aws ec2 describe-security-groups \
  --filters "Name=ip-permission.from-port,Values=22" \
           "Name=ip-permission.to-port,Values=22" \
           "Name=ip-permission.cidr,Values=0.0.0.0/0" \
  --query 'SecurityGroups[].{ID:GroupId, Name:GroupName, VPC:VpcId}' \
  --output table

# 2. Buckets S3 públicos
echo "=== Buckets S3 con acceso público ==="
aws s3api list-buckets --query 'Buckets[].Name' --output text | \
  tr '\t' '\n' | while read bucket; do
    acl=$(aws s3api get-bucket-acl --bucket "$bucket" 2>/dev/null)
    policy=$(aws s3api get-bucket-policy-status --bucket "$bucket" 2>/dev/null)
    if echo "$policy" | grep -q '"IsPublic": true'; then
      echo "⚠ PÚBLICO: $bucket"
    fi
done

# 3. RDS accesibles desde Internet
echo "=== Bases de datos RDS públicas ==="
aws rds describe-db-instances \
  --query 'DBInstances[?PubliclyAccessible==`true`].{
    ID:DBInstanceIdentifier,
    Engine:Engine,
    Endpoint:Endpoint.Address
  }' --output table

# 4. Claves IAM antiguas
echo "=== Claves IAM > 90 días ==="
aws iam generate-credential-report > /dev/null 2>&1
sleep 2
aws iam get-credential-report --query 'Content' --output text | \
  base64 -d | awk -F, 'NR>1 && $9!="N/A" {
    cmd="date -d \""$9"\" +%s"; cmd | getline created; close(cmd)
    now=systime()
    age=int((now-created)/86400)
    if (age>90) print "⚠ "$1": clave de "age" días"
  }'

# 5. Usuarios sin MFA
echo "=== Usuarios sin MFA ==="
aws iam list-users --query 'Users[].UserName' --output text | \
  tr '\t' '\n' | while read user; do
    mfa=$(aws iam list-mfa-devices --user-name "$user" \
      --query 'MFADevices' --output text)
    if [ -z "$mfa" ]; then
      echo "⚠ Sin MFA: $user"
    fi
done
