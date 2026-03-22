# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
    def __enter__(self):
        """Context manager: inicializa el driver al entrar."""
        self.driver = self._create_driver()
        self.wait = WebDriverWait(self.driver, self.DEFAULT_WAIT)
        logger.info(f"[{self.task_id}] Driver iniciado en el Grid")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: cierra el driver al salir, siempre."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info(f"[{self.task_id}] Driver cerrado correctamente")
            except Exception as e:
                logger.warning(f"[{self.task_id}] Error cerrando driver: {e}")

    def wait_for_element(self, locator, timeout: int = None):
        """Espera a que un elemento sea visible y devuelve la referencia."""
        t = timeout or self.DEFAULT_WAIT
        try:
            return WebDriverWait(self.driver, t).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            # Captura screenshot para diagnóstico antes de propagar el error
            self._capture_screenshot(f"timeout_{locator[1][:20]}")
            raise

    def _capture_screenshot(self, name: str):
        """Guarda un screenshot para diagnóstico de fallos."""
        try:
            # NOTA: No capturar screenshots durante introducción de credenciales
            path = f"/tmp/bot_screenshot_{self.task_id}_{name}.png"
            self.driver.save_screenshot(path)
            logger.info(f"[{self.task_id}] Screenshot guardado: {path}")
        except Exception:
            pass  # No propagar errores de diagnóstico
