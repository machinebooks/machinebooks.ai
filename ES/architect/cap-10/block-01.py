# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
# Ejemplo didáctico: patrones/automation/base_bot.py

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

class BaseBot:
    """Clase base para todos los bots de automatización RPA.

    Gestiona el ciclo de vida del driver, los reintentos y el logging
    de forma centralizada para evitar duplicación entre bots.
    """

    SELENIUM_HUB_URL = "http://selenium-hub:4444/wd/hub"
    DEFAULT_WAIT = 15    # segundos de espera para elementos
    PAGE_LOAD_TIMEOUT = 30

    def __init__(self, task_id: str, headless: bool = True):
        self.task_id = task_id
        self.headless = headless
        self.driver = None
        self.wait = None

    def _create_driver(self) -> webdriver.Remote:
        """Crea una sesión Chrome en el Grid con las opciones estándar."""
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")

        # Opciones de estabilidad críticas para entornos contenedorizados
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")

        # User agent corporativo para evitar detección como bot en algunos sistemas
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )

        driver = webdriver.Remote(
            command_executor=self.SELENIUM_HUB_URL,
            options=options
        )
        driver.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)
        return driver

