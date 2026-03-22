# Extraído de: LibroDevSecOps/cap-09-agente-triaje.md
#!/usr/bin/env python3
"""check_gate.py — Verifica si el PR supera el gate de seguridad."""
import json
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--max-immediate", type=int, default=0)
    parser.add_argument("--fail-on-immediate", action="store_true")
    args = parser.parse_args()

    with open(args.report) as f:
        report = json.load(f)

    immediate = report.get("immediate_action", [])
    count = len(immediate)

    print(f"Hallazgos de acción inmediata: {count}")
    print(f"Umbral permitido: {args.max_immediate}")

    if args.fail_on_immediate and count > args.max_immediate:
        print("\n GATE BLOQUEADO — Hallazgos que requieren acción:")
        for finding in immediate:
            score = finding["priority_score"]
            title = finding["title"]
            service = finding["service"]
            print(f"  [{score}] {title} ({service})")
        sys.exit(1)

    print("\n GATE SUPERADO")
    sys.exit(0)

if __name__ == "__main__":
    main()
