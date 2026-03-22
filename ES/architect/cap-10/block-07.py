# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
    def extract_project_list(self) -> list[dict]:
        """Extrae la lista de proyectos activos del portal."""
        # Navegar a la sección de proyectos
        projects_link = self.wait_for_element(
            (By.LINK_TEXT, "Proyectos Activos")
        )
        projects_link.click()

        projects = []
        page = 1

        while True:
            # Esperar a que la tabla esté cargada
            self.wait_for_element((By.CSS_SELECTOR, "table.projects-table tbody tr"))

            rows = self.driver.find_elements(
                By.CSS_SELECTOR, "table.projects-table tbody tr"
            )

            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 4:
                    projects.append({
                        "id": cells[0].text.strip(),
                        "name": cells[1].text.strip(),
                        "status": cells[2].text.strip(),
                        "team": cells[3].text.strip(),
                    })

            # Comprobar si hay página siguiente
            try:
                next_btn = self.driver.find_element(
                    By.CSS_SELECTOR, "button.pagination-next:not([disabled])"
                )
                next_btn.click()
                page += 1
                time.sleep(1)  # Esperar a que la nueva página cargue
            except Exception:
                break  # No hay más páginas

        return projects
