# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
# Estimar coste de un plan Terraform
infracost breakdown --path .

# Comparar coste entre dos estados
infracost diff --path . --compare-to infracost-base.json
