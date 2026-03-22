# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
    def login(self) -> bool:
        """Realiza el proceso completo de login, incluyendo MFA si es necesario."""
        self.driver.get(self.PORTAL_URL)

        # Página de credenciales
        username_field = self.wait_for_element((By.ID, "username"))
        username_field.send_keys(self.credentials["username"])

        password_field = self.driver.find_element(By.ID, "password")
        password_field.send_keys(self.credentials["password"])
        password_field.submit()

        # Determinar si aparece la pantalla de MFA o se va directo al dashboard
        time.sleep(2)  # Pequeña pausa para que la redirección se resuelva

        if "mfa" in self.driver.current_url or self._is_mfa_screen():
            mfa_code = self.request_mfa_code(
                task_id=self.task_id,
                system_name="Portal Corporativo",
                user_id=self.user_id
            )
            if mfa_code is None:
                raise RuntimeError("Timeout esperando código MFA del usuario")

            mfa_field = self.wait_for_element((By.ID, "otp-input"))
            mfa_field.send_keys(mfa_code)
            mfa_field.submit()

        # Verificar login exitoso comprobando elemento del dashboard
        try:
            self.wait_for_element((By.CSS_SELECTOR, ".dashboard-header"), timeout=10)
            return True
        except Exception:
            return False

    def _is_mfa_screen(self) -> bool:
        """Detecta si estamos en la pantalla de MFA por elementos del DOM."""
        try:
            self.driver.find_element(By.ID, "otp-input")
            return True
        except Exception:
            return False
