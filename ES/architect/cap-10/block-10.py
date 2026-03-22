# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
    def upload_pricing_data(self, df: pd.DataFrame) -> UploadResult:
        """Carga los datos del DataFrame al configurador de precios por lotes."""
        result = UploadResult(total_rows=len(df))

        # Dividir en lotes
        batches = [df[i:i+self.MAX_BATCH_SIZE] for i in range(0, len(df), self.MAX_BATCH_SIZE)]

        for batch_num, batch in enumerate(batches, 1):
            self._log(f"Procesando lote {batch_num}/{len(batches)} ({len(batch)} filas)")

            for _, row in batch.iterrows():
                try:
                    self._upload_single_row(row)
                    result.successful += 1
                except Exception as e:
                    result.failed += 1
                    result.errors.append(
                        f"Fila {row.name + 2}: {e}"
                    )

            # Pausa entre lotes para no sobrecargar el sistema externo
            if batch_num < len(batches):
                time.sleep(2)

        return result

    def _upload_single_row(self, row: pd.Series):
        """Carga una fila individual en el formulario del configurador."""
        # Navegar al formulario de alta
        add_btn = self.wait_for_element((By.CSS_SELECTOR, "button.btn-add-service"))
        add_btn.click()

        # Rellenar formulario — esperar a que cada campo esté listo
        self.wait_for_element((By.ID, "service-code")).send_keys(row["codigo_servicio"])
        self.driver.find_element(By.ID, "base-price").send_keys(row["precio_base"])

        if pd.notna(row.get("descuento_maximo")):
            self.driver.find_element(By.ID, "max-discount").send_keys(row["descuento_maximo"])

        # Guardar y verificar confirmación
        save_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        save_btn.click()

        # Esperar confirmación de guardado exitoso
        self.wait_for_element(
            (By.CSS_SELECTOR, ".toast-success"),
            timeout=5
        )

    def _log(self, message: str):
        import logging
        logging.getLogger(__name__).info(f"[{self.task_id}] {message}")
