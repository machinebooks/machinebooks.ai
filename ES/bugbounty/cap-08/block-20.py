# Extraído de: LibroBugBounty/cap-08-analisis-drivers.md
def archive_analysis(driver_path, results, session_id):
    """Archiva resultados con metadata de reproducibilidad."""
    import datetime
    archive = {
        "session_id": session_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "driver": {
            "name": driver_path.name,
            "hashes": hash_file(driver_path),
        },
        "environment": {
            "dockerfile_tag": "v2.1",
            "radare2_version": subprocess.getoutput("r2 -v"),
            "python_version": sys.version,
        },
        "results": results,
    }
    output = Path(f"/lab/results/archive/{session_id}_{driver_path.stem}.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w') as f:
        json.dump(archive, f, indent=2, default=str)
    return output
