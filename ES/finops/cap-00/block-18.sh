# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
# Instalar via Helm
helm install opencost opencost/opencost \
  --namespace opencost --create-namespace

# Consultar coste por namespace (API REST)
curl http://localhost:9003/allocation/compute \
  -d '{"window":"7d","aggregate":"namespace"}'
