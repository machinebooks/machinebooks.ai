# Extraído de: LibroUsuario/cap-21-la-nube-desde-el-cli.md
# Listar buckets con tamaño
aws s3api list-buckets --query 'Buckets[].Name' --output text | \
  tr '\t' '\n' | while read bucket; do
    size=$(aws cloudwatch get-metric-statistics \
      --namespace AWS/S3 \
      --metric-name BucketSizeBytes \
      --dimensions Name=BucketName,Value="$bucket" \
                   Name=StorageType,Value=StandardStorage \
      --start-time "$(date -u -d '2 days ago' +%Y-%m-%dT%H:%M:%SZ)" \
      --end-time "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
      --period 86400 --statistics Average \
      --query 'Datapoints[0].Average' --output text 2>/dev/null)

    # Convertir bytes a formato legible
    if [ "$size" != "None" ] && [ ! -z "$size" ]; then
      size_gb=$(echo "scale=2; $size/1073741824" | bc)
      echo "$bucket: ${size_gb} GB"
    else
      echo "$bucket: Sin datos de tamaño"
    fi
done

# Verificar lifecycle policies
aws s3api list-buckets --query 'Buckets[].Name' --output text | \
  tr '\t' '\n' | while read bucket; do
    lifecycle=$(aws s3api get-bucket-lifecycle-configuration \
      --bucket "$bucket" 2>/dev/null)
    if [ -z "$lifecycle" ]; then
      echo "⚠ Sin lifecycle: $bucket"
    fi
done
