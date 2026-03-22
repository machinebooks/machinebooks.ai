# Extraído de: LibroPQC/cap-07-analisis-codigo.md
# Mapeo de extensiones a lenguaje
LANGUAGE_EXTENSIONS = {
    'python': ['.py', '.pyw', '.pyi'],
    'javascript': ['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'],
    'java': ['.java'],
    'go': ['.go'],
    'c': ['.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx'],
    'rust': ['.rs'],
}

# Directorios a excluir del escaneo
SKIP_DIRECTORIES = {
    'node_modules', '.git', '.svn', '.hg',
    '__pycache__', '.pytest_cache',
    'venv', 'env', '.venv', '.env', 'virtualenv', '.tox',
    'build', 'dist', 'target', 'bin', 'obj', 'out',
    '.idea', '.vscode', '.vs',
    'vendor', 'third_party', 'external',
}
