# Extracted from: LibroAIGateway/cap-31-adoption-compliance-portal.md
# Pseudonymization in the ranking — gateway/app/api/v1/leaderboard.py:70-79
if nominal:
    display = (r[2] or r[1])  # display_name (nick) or real name
else:
    display = f"Anonimo #{r[0]}"
    # user_id is set to null in the response
