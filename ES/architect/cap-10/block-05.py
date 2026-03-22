# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
# Ejemplo didáctico: patrones/automation/bots/portal_bot.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

class PortalBot(BaseBot, MFAWaitMixin):
    """Bot de automatización para el portal corporativo.

    Gestiona el login con MFA, la navegación y la extracción
    de datos de proyectos y recursos del portal.
    """

    PORTAL_URL = "https://portal.ejemplo.com"  # En producción: cargar desde os.environ o CredentialVault

    def __init__(self, task_id: str, credentials: dict, redis_client, user_id: int):
        BaseBot.__init__(self, task_id)
        MFAWaitMixin.__init__(self, redis_client)
        self.credentials = credentials
        self.user_id = user_id

