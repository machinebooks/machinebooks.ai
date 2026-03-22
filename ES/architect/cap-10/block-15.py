# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
    def list_changed_files(self, site_id: str, drive_id: str, since: datetime) -> list[dict]:
        """Lista ficheros modificados desde una fecha dada en un drive de SharePoint."""
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Usar delta query de Graph para detectar cambios eficientemente
        delta_url = (
            f"{self.GRAPH_BASE_URL}/sites/{site_id}/drives/{drive_id}/root/delta"
        )

        changed_files = []
        while delta_url:
            response = httpx.get(delta_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            for item in data.get("value", []):
                # Filtrar solo ficheros (no carpetas) modificados desde `since`
                if "file" in item and not item.get("deleted"):
                    modified = datetime.fromisoformat(
                        item["lastModifiedDateTime"].replace("Z", "+00:00")
                    )
                    if modified.replace(tzinfo=None) > since:
                        changed_files.append({
                            "id": item["id"],
                            "name": item["name"],
                            "path": item.get("parentReference", {}).get("path", ""),
                            "modified_at": modified,
                            "size": item["size"],
                            "download_url": item.get("@microsoft.graph.downloadUrl")
                        })

            # Paginación y delta link para la próxima ejecución
            delta_url = data.get("@odata.nextLink")

        return changed_files


