# Extraído de: LibroAIGateway/cap-31-adopcion-compliance-portal.md
# Pseudonimización en el ranking — gateway/app/api/v1/leaderboard.py:70-79
if nominal:
    display = (r[2] or r[1])  # display_name (nick) o name real
else:
    display = f"Anonimo #{r[0]}"
    # user_id se pone a null en la respuesta
