# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
import boto3

# Credenciales via variables de entorno o perfil IAM:
#   AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN
# O via IAM role en EC2/ECS/Lambda (recomendado en produccion)

ce = boto3.client("ce", region_name="us-east-1")
