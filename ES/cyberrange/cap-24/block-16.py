# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Validación de ficheros subidos
# Ejemplo didáctico: patrones/security/file_validation.py

import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'.zip', '.yaml', '.yml', '.json'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

def validate_upload(file) -> tuple[bool, str]:
    """Valida un fichero subido antes de procesarlo.
    Verifica extensión, tamaño y nombre seguro."""

    # 1. Verificar que el fichero tiene nombre
    if not file.filename:
        return False, "Nombre de fichero vacío"

    # 2. Sanitizar el nombre — elimina path traversal (../../etc/passwd)
    safe_name = secure_filename(file.filename)
    if not safe_name:
        return False, "Nombre de fichero no válido"

    # 3. Verificar extensión contra whitelist
    _, ext = os.path.splitext(safe_name)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        return False, f"Extensión {ext} no permitida. Permitidas: {ALLOWED_EXTENSIONS}"

    # 4. Verificar tamaño (leer sin cargar en memoria)
    file.seek(0, 2)  # Mover cursor al final
    size = file.tell()
    file.seek(0)     # Volver al inicio
    if size > MAX_FILE_SIZE:
        return False, f"Fichero demasiado grande ({size // 1024 // 1024} MB). Máximo: 50 MB"

    # 5. Para ficheros ZIP: verificar que no contienen paths absolutos
    #    ni referencias a directorios padre (zip slip attack)
    if ext.lower() == '.zip':
        import zipfile
        try:
            with zipfile.ZipFile(file) as zf:
                for name in zf.namelist():
                    if name.startswith('/') or '..' in name:
                        return False, f"Fichero ZIP contiene path sospechoso: {name}"
        except zipfile.BadZipFile:
            return False, "Fichero ZIP corrupto o no válido"
        file.seek(0)

    return True, safe_name
