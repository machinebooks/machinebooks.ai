# Extracted from: LibroAIGateway/cap-34-celery-deployment-config.md
# DRY_RUN=1 lists the tarball without uploading
suspect = [n for n in names
           if n.endswith('.env')
           or 'secret' in n.lower()
           or n.endswith('.pem')
           or n.endswith('.key')]
if suspect:
    print(f"[dry-run] WARN {len(suspect)} potential secrets:")
    for n in suspect:
        print(f"  WARN {n}")
