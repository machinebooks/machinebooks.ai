# Extraído de: LibroAIGateway/cap-34-celery-deployment-config.md
# DRY_RUN=1 lista el tarball sin subir
suspect = [n for n in names
           if n.endswith('.env')
           or 'secret' in n.lower()
           or n.endswith('.pem')
           or n.endswith('.key')]
if suspect:
    print(f"[dry-run] WARN {len(suspect)} potenciales secretos:")
    for n in suspect:
        print(f"  WARN {n}")
