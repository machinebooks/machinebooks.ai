# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
# Instalar via Helm
helm install kubecost kubecost/cost-analyzer \
  --namespace kubecost --create-namespace \
  --set kubecostToken="<TU_TOKEN>"
