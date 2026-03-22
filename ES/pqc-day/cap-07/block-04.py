# Extraído de: LibroPQC/cap-07-analisis-codigo.md
def scan_directory(self, directory: str) -> List[CodeFinding]:
    """Escanea un directorio completo recursivamente"""
    self.base_path = directory
    self.findings = []
    self.files_scanned = 0
    self.lines_scanned = 0
    self.algorithms_found = set()

    for root, dirs, files in os.walk(directory):
        # Filtrar directorios excluidos IN-PLACE
        # para que os.walk no descienda a ellos
        dirs[:] = [d for d in dirs if d not in SKIP_DIRECTORIES]

        for file in files:
            file_path = os.path.join(root, file)
            file_findings = self._scan_file(file_path)
            self.findings.extend(file_findings)

    return self.findings
