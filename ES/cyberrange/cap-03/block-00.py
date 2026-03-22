# Extraído de: LibroCyberrange/cap-03-arquitecto-cyber-range.md
# Configuración de autenticación JWT
# Ejemplo didáctico: patrones/auth/config.py

from datetime import timedelta

# 4 horas, no 24. Un token comprometido durante un ejercicio
# tiene una ventana de ataque limitada.
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=4)

# El refresh token tiene 7 días pero requiere reautenticación
# si el usuario cambia de IP o de user-agent.
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

# Bloqueo de cuenta tras 5 intentos fallidos.
# En un Cyber Range, los participantes NO atacan el sistema de login
# de la plataforma — atacan las VMs del escenario.
# Si alguien está haciendo fuerza bruta al login, no es un participante.
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=30)
