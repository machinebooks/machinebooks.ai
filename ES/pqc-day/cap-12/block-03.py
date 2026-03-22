# Extraído de: LibroPQC/cap-12-agente-autonomo.md
def _read_file(self, path: str, start_line=None, end_line=None) -> dict:
    """Lee un fichero con validación de ruta obligatoria."""
    file_path = self.repo_path / path

    # Validación de seguridad: ¿la ruta resuelta está dentro del repo?
    try:
        file_path.resolve().relative_to(self.repo_path.resolve())
    except ValueError:
        return {'success': False, 'error': 'Acceso denegado: ruta fuera del repositorio'}

    # Validación de tamaño: prevenir lectura de ficheros enormes
    if file_path.stat().st_size > self.max_file_size:
        return {
            'success': False,
            'error': f'Fichero demasiado grande: {file_path.stat().st_size} bytes'
        }

    # Lectura segura con manejo de encoding
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    # (aplicar start_line / end_line si se proporcionan)
    return {'success': True, 'result': {'path': path, 'content': ''.join(lines)}}
