# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
# Nodos
echo "=== NODOS ==="
kubectl get nodes -o custom-columns="\
NAME:.metadata.name,STATUS:.status.conditions[-1].type,\
CPU:.status.capacity.cpu,MEM:.status.capacity.memory,\
VERSION:.status.nodeInfo.kubeletVersion"

# Pods por namespace
echo "=== PODS POR NAMESPACE ==="
kubectl get pods --all-namespaces --no-headers | \
  awk '{ns[$1]++} END {for (n in ns) print ns[n], n}' | sort -rn

# Deployments con problemas
echo "=== DEPLOYMENTS CON PODS NO READY ==="
kubectl get deployments --all-namespaces \
  -o custom-columns="\
NAMESPACE:.metadata.namespace,NAME:.metadata.name,\
READY:.status.readyReplicas,DESIRED:.spec.replicas" | \
  awk 'NR==1 || $3!=$4'

# Consumo de recursos
echo "=== CONSUMO DE RECURSOS ==="
kubectl top nodes
