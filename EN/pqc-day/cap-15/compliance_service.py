"""
PQC-Day and the Machine — Chapter 15
Pattern: ComplianceService — map findings to regulatory controls

This is a didactic example from the book, not production code.
See chapter 15 for full context and explanation.
"""

import json
from typing import Dict, List, Optional
from dataclasses import asdict

from compliance_models import (
    ComplianceControl, ControlAssessment, FindingControlMapping,
    create_nis2_framework
)


class ComplianceService:
    """Main service for compliance operations."""

    # Deterministic mapping: finding categories -> controls
    FINDING_TO_CONTROL_MAPPING = {
        'crypto': {
            'keywords': ['rsa', 'aes', 'des', 'md5', 'sha1', 'encryption',
                         'cipher', 'key', 'certificate', 'ssl', 'tls'],
            'controls': ['NIS2.RISK.8'],
            'domain': 'Cryptography'
        },
        'weak_crypto': {
            'keywords': ['weak', 'deprecated', 'vulnerable', 'insecure'],
            'controls': ['NIS2.RISK.8'],
            'impact': 'violation'
        },
        'quantum': {
            'keywords': ['quantum', 'post-quantum', 'pqc', 'lattice',
                         'kyber', 'dilithium'],
            'controls': ['NIS2.RISK.8', 'NIS2.RISK.1'],
            'domain': 'Post-Quantum Cryptography'
        },
        'access_control': {
            'keywords': ['access', 'authentication', 'authorization',
                         'mfa', 'password', 'credential'],
            'controls': ['NIS2.RISK.9', 'NIS2.RISK.10'],
            'domain': 'Access Control'
        },
        'supply_chain': {
            'keywords': ['dependency', 'third-party', 'library',
                         'package', 'vendor'],
            'controls': ['NIS2.RISK.4'],
            'domain': 'Supply Chain'
        },
    }

    def __init__(self, controls: List[ComplianceControl]):
        """Initialize with controls indexed by reference."""
        self.controls = {c.reference: c for c in controls}

    def map_finding_to_controls(self, finding: Dict) -> Dict[str, Dict]:
        """Map a finding to relevant controls by keywords."""
        mappings = {}

        # Build normalized finding text
        finding_text = ''
        for field in ['algorithm', 'description', 'title', 'pqc_impact']:
            finding_text += f" {finding.get(field, '')}"
        finding_text = finding_text.lower()

        # Search for matches by category
        for category, rules in self.FINDING_TO_CONTROL_MAPPING.items():
            for keyword in rules.get('keywords', []):
                if keyword.lower() in finding_text:
                    for control_ref in rules.get('controls', []):
                        if control_ref in self.controls:
                            severity = finding.get('severity', 'medium')
                            if severity in ['critical', 'high']:
                                impact = 'violation'
                            elif severity == 'medium':
                                impact = 'partial'
                            else:
                                impact = 'recommendation'

                            mappings[control_ref] = {
                                'impact': rules.get('impact', impact),
                                'domain': rules.get('domain', 'General'),
                                'matched_keyword': keyword,
                                'category': category
                            }
                    break  # Only one match per category

        return mappings

    def process_findings(self, findings: List[Dict]) -> Dict:
        """Process a list of findings and generate control mappings.

        Returns statistics about the mapping process.
        """
        results = {
            'findings_processed': 0,
            'mappings_created': 0,
            'controls_affected': set(),
            'mappings': []
        }

        for finding in findings:
            results['findings_processed'] += 1
            mappings = self.map_finding_to_controls(finding)

            for control_ref, mapping_data in mappings.items():
                results['mappings_created'] += 1
                results['controls_affected'].add(control_ref)

                mapping = FindingControlMapping(
                    finding_type='crypto' if 'algorithm' in finding
                                 else 'vulnerability',
                    finding_id=finding.get('id', 0),
                    control_id=self.controls[control_ref].id,
                    mapping_type=mapping_data['impact'],
                    confidence=0.8,
                    is_auto_mapped=True,
                    notes=f"Keyword: {mapping_data.get('matched_keyword', 'N/A')}"
                )
                results['mappings'].append(mapping)

        results['controls_affected'] = list(results['controls_affected'])
        return results

    def generate_soa(self, assessment_name: str,
                     control_statuses: Dict[str, str]) -> Dict:
        """Generate Statement of Applicability for audit."""
        controls_list = []
        for ref, control in sorted(self.controls.items()):
            status = control_statuses.get(ref, 'not_assessed')
            controls_list.append({
                'reference': ref,
                'title': control.title,
                'domain': control.domain,
                'category': control.category,
                'implementation_status': status,
                'pqc_relevant': control.pqc_relevant,
            })

        # Calculate statistics
        total = len(controls_list)
        implemented = sum(1 for c in controls_list
                          if c['implementation_status'] == 'implemented')
        partial = sum(1 for c in controls_list
                      if c['implementation_status'] == 'partial')
        not_impl = sum(1 for c in controls_list
                       if c['implementation_status'] == 'not_implemented')

        score = ((implemented * 100 + partial * 50) / max(total, 1))

        return {
            'assessment': assessment_name,
            'overall_score': round(score, 1),
            'summary': {
                'total': total,
                'implemented': implemented,
                'partial': partial,
                'not_implemented': not_impl,
            },
            'controls': controls_list
        }


# --- Main ---
if __name__ == '__main__':
    # Create NIS2 framework and service
    framework, controls = create_nis2_framework()
    service = ComplianceService(controls)

    # Sample findings from a PQC scan
    sample_findings = [
        {
            'id': 1, 'algorithm': 'RSA-2048', 'severity': 'critical',
            'description': 'RSA key generation in auth module',
            'pqc_impact': 'Vulnerable to Shor algorithm'
        },
        {
            'id': 2, 'algorithm': 'MD5', 'severity': 'critical',
            'description': 'MD5 hash for password storage',
            'pqc_impact': 'Broken hash algorithm'
        },
        {
            'id': 3, 'algorithm': 'AES-128', 'severity': 'medium',
            'description': 'AES-128 encryption for data at rest',
            'pqc_impact': 'Grover reduces security margin'
        },
        {
            'id': 4, 'severity': 'high',
            'description': 'Third-party dependency with vulnerable crypto',
            'title': 'Vulnerable dependency: cryptography<41.0'
        },
    ]

    # Process findings
    results = service.process_findings(sample_findings)

    print(f"=== Compliance Mapping Results ===\n")
    print(f"Findings processed: {results['findings_processed']}")
    print(f"Mappings created: {results['mappings_created']}")
    print(f"Controls affected: {results['controls_affected']}")

    for m in results['mappings']:
        ctrl = next(c for c in controls if c.id == m.control_id)
        print(f"\n  Finding #{m.finding_id} -> {ctrl.reference}")
        print(f"    Impact: {m.mapping_type}")
        print(f"    {m.notes}")

    # Generate SOA
    soa = service.generate_soa(
        assessment_name="Q1 2025 NIS2 Assessment",
        control_statuses={
            'NIS2.RISK.1': 'partial',
            'NIS2.RISK.4': 'not_implemented',
            'NIS2.RISK.8': 'not_implemented',
            'NIS2.RISK.9': 'implemented',
            'NIS2.RISK.10': 'partial',
        }
    )

    print(f"\n=== Statement of Applicability ===\n")
    print(f"Assessment: {soa['assessment']}")
    print(f"Overall Score: {soa['overall_score']}%")
    print(f"Summary: {soa['summary']}")
    for c in soa['controls']:
        pqc = " [PQC]" if c['pqc_relevant'] else ""
        print(f"  {c['reference']:15s} [{c['implementation_status']:16s}] "
              f"{c['title']}{pqc}")
