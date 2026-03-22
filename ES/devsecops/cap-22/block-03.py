# Extraído de: LibroDevSecOps/cap-22-compliance-continuo.md
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone


class EvidenceCollector:
    """Recolecta y registra evidencias del pipeline para compliance."""

    def __init__(self, reports_dir: str, evidence_store: str):
        self.reports_dir = Path(reports_dir)
        self.evidence_store = Path(evidence_store)
        self.evidence_store.mkdir(parents=True, exist_ok=True)

    def collect_from_pipeline_run(
        self, run_id: str, commit_sha: str
    ) -> list[Evidence]:
        """Recolecta todas las evidencias de una ejecución del pipeline."""
        evidences = []

        # Recolectar de cada fuente configurada
        collectors = {
            "sast": self._collect_sast,
            "sca": self._collect_sca,
            "trivy": self._collect_trivy,
            "secrets": self._collect_secrets,
            "opa": self._collect_opa,
        }

        for source_name, collector_fn in collectors.items():
            source_dir = self.reports_dir / source_name
            if source_dir.exists():
                for report_file in source_dir.glob("*.json"):
                    evidence = collector_fn(
                        report_file, run_id, commit_sha
                    )
                    if evidence:
                        evidences.append(evidence)

        # Persistir índice de evidencias
        self._store_evidence_index(evidences, run_id)
        return evidences

    def _collect_sast(
        self, report_path: Path, run_id: str, commit_sha: str
    ) -> Evidence:
        """Extrae evidencia de un informe SAST de Semgrep."""
        data = json.loads(report_path.read_text())
        findings = data.get("results", [])
        critical = [f for f in findings if f.get("severity") == "ERROR"]

        return Evidence(
            source=EvidenceSource.SAST_SCAN,
            timestamp=datetime.now(timezone.utc),
            artifact_path=str(report_path),
            pipeline_run_id=run_id,
            commit_sha=commit_sha,
            summary=f"{len(findings)} hallazgos, {len(critical)} críticos",
            passed=len(critical) == 0,
            metadata={
                "tool": "semgrep",
                "total_findings": len(findings),
                "critical_findings": len(critical),
                "file_hash": self._hash_file(report_path),
            },
        )

    def _collect_sca(
        self, report_path: Path, run_id: str, commit_sha: str
    ) -> Evidence:
        """Extrae evidencia de un informe SCA de Grype."""
        data = json.loads(report_path.read_text())
        matches = data.get("matches", [])
        critical = [
            m for m in matches
            if m.get("vulnerability", {}).get("severity") == "Critical"
        ]

        return Evidence(
            source=EvidenceSource.SCA_SCAN,
            timestamp=datetime.now(timezone.utc),
            artifact_path=str(report_path),
            pipeline_run_id=run_id,
            commit_sha=commit_sha,
            summary=f"{len(matches)} vulnerabilidades, "
                    f"{len(critical)} críticas",
            passed=len(critical) == 0,
            metadata={
                "tool": "grype",
                "total_vulnerabilities": len(matches),
                "critical_vulnerabilities": len(critical),
                "file_hash": self._hash_file(report_path),
            },
        )

    def _hash_file(self, path: Path) -> str:
        """SHA-256 del artefacto para garantizar integridad."""
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _store_evidence_index(
        self, evidences: list[Evidence], run_id: str
    ) -> None:
        """Almacena el índice de evidencias de una ejecución."""
        index = {
            "run_id": run_id,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "evidence_count": len(evidences),
            "evidences": [
                {
                    "source": e.source.value,
                    "artifact_path": e.artifact_path,
                    "passed": e.passed,
                    "summary": e.summary,
                    "file_hash": e.metadata.get("file_hash", ""),
                }
                for e in evidences
            ],
        }
        index_path = self.evidence_store / f"evidence-{run_id}.json"
        index_path.write_text(json.dumps(index, indent=2))
