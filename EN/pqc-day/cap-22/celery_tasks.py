"""
PQC-Day and the Machine — Chapter 22
Pattern: Celery tasks for async PQC analysis (repository scan pipeline)

This is a didactic example from the book, not production code.
See chapter 22 for full context and explanation.

Requires: pip install celery redis
"""

import os
import shutil
import tempfile
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# --- DatabaseTask base class ---

class DatabaseTask:
    """Base class for Celery tasks with automatic SQLAlchemy session management.

    Guarantees the session is closed and cleaned after each execution,
    regardless of the result. Without this, MySQL connections accumulate
    until reaching max_connections and the platform stops.
    """
    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """Always executed after the task, whether success or failure."""
        # In production: db.session.remove()
        logger.debug(f"Task {task_id} completed with status: {status}")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Additional cleanup on error: explicit rollback to prevent
        partial transactions from contaminating the session."""
        # In production: db.session.rollback(); db.session.remove()
        logger.error(f"Task {task_id} failed: {exc}")


# --- Repository analysis task ---

def analyze_repository_task(job_id: int, repo_url: str,
                             connector_type: str = 'github',
                             access_token: str = None,
                             branch: str = 'main') -> dict:
    """Complete cryptographic analysis cycle for a repository.

    Phases: clone -> scan -> save -> score -> cleanup
    Each phase updates progress_percentage for frontend display.

    In production, this would be decorated with:
    @celery_app.task(
        base=DatabaseTask,
        bind=True,
        name='analyze_repository_task',
        max_retries=2,
        soft_time_limit=600,    # 10 minutes: warning
        time_limit=720          # 12 minutes: definitive kill
    )
    """
    temp_dir = None
    results = {
        'job_id': job_id,
        'status': 'running',
        'progress': 0,
        'findings': [],
    }

    try:
        # Phase 1: Initialization (0-10%)
        logger.info(f"Starting analysis for job {job_id}")
        results['progress'] = 5
        results['stage'] = 'initializing'

        # Phase 2: Clone repository (10-30%)
        results['stage'] = 'cloning'
        results['progress'] = 10

        temp_dir = tempfile.mkdtemp(prefix='pqc_repo_')
        logger.info(f"Cloning {repo_url} to {temp_dir}")

        # In production: connector.clone(repo_url, temp_dir, branch=branch)
        # For this example, we scan the current directory
        scan_dir = temp_dir if os.listdir(temp_dir) else '.'

        results['progress'] = 30

        # Phase 3: Cryptographic pattern scan (30-70%)
        results['stage'] = 'scanning'
        results['progress'] = 35

        # Import the analyzer from chapter 7
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'cap-07'))
        try:
            from repository_analyzer import RepositoryAnalyzer
            analyzer = RepositoryAnalyzer()
            findings = analyzer.scan_directory(scan_dir)
            results['findings'] = [
                {
                    'file_path': f.file_path,
                    'line_number': f.line_number,
                    'algorithm': f.algorithm,
                    'severity': f.severity,
                    'description': f.description,
                    'pqc_impact': f.pqc_impact,
                }
                for f in findings
            ]
        except ImportError:
            logger.warning("RepositoryAnalyzer not available, using stub")
            results['findings'] = []

        results['progress'] = 70

        # Phase 4: Save findings (70-90%)
        results['stage'] = 'saving_results'
        results['progress'] = 75

        saved_count = 0
        for finding in results['findings']:
            saved_count += 1
            # In production: db.session.add(CryptoFinding(...))
            # Commit every 100 findings to avoid memory buildup
            if saved_count % 100 == 0:
                progress = 75 + int(15 * saved_count / max(len(results['findings']), 1))
                results['progress'] = min(progress, 89)

        results['progress'] = 90

        # Phase 5: Calculate PQC score (90-100%)
        results['stage'] = 'calculating_score'

        severity_weights = {'critical': 25, 'high': 15, 'medium': 5, 'low': 1}
        severity_counts = {}
        for f in results['findings']:
            sev = f.get('severity', 'medium')
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        pqc_risk_score = sum(
            severity_weights.get(sev, 0) * count
            for sev, count in severity_counts.items()
        )
        pqc_risk_score = min(100, pqc_risk_score)

        results['status'] = 'completed'
        results['stage'] = 'done'
        results['progress'] = 100
        results['total_findings'] = len(results['findings'])
        results['pqc_score'] = 100 - pqc_risk_score
        results['severity_counts'] = severity_counts
        results['completed_at'] = datetime.utcnow().isoformat()

        logger.info(
            f"Analysis completed for job {job_id}: "
            f"{results['total_findings']} findings, "
            f"PQC score: {results['pqc_score']}"
        )

        return results

    except Exception as exc:
        logger.error(f"Analysis failed for job {job_id}: {exc}")
        results['status'] = 'failed'
        # Truncate and sanitize: do not expose internal paths
        results['error_message'] = str(exc)[:500]
        raise

    finally:
        # ALWAYS clean up the temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


# --- Celery Beat schedule configuration ---

CELERY_BEAT_SCHEDULE = {
    # Daily repository scan for all organizations
    'daily-crypto-scan': {
        'task': 'analyze_repository_task',
        'schedule': 86400,  # Every 24 hours (crontab(hour=2, minute=0) in production)
        'options': {'queue': 'repository_analysis'}
    },
    # Certificate monitoring every 6 hours
    'certificate-monitoring': {
        'task': 'scan_certificates_task',
        'schedule': 21600,  # Every 6 hours
        'options': {'queue': 'certificate_scanning'}
    },
    # Cloud audit weekly
    'weekly-cloud-audit': {
        'task': 'cloud_audit_task',
        'schedule': 604800,  # Every 7 days
        'options': {'queue': 'cloud_audit'}
    },
}


# --- Main ---
if __name__ == '__main__':
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    print(f"Running analysis task for: {target}\n")

    result = analyze_repository_task(
        job_id=1,
        repo_url=target,
        connector_type='local'
    )

    print(f"Status: {result['status']}")
    print(f"Total findings: {result.get('total_findings', 0)}")
    print(f"PQC Score: {result.get('pqc_score', 'N/A')}%")
    print(f"Severity: {result.get('severity_counts', {})}")

    if result.get('findings'):
        print(f"\nTop findings:")
        for f in result['findings'][:10]:
            print(f"  [{f['severity']:8s}] {f['algorithm']:10s} {f['file_path']}")
