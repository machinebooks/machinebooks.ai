# Companion code for "The Cyber Range and the Machine" — Testing Chapter
# Network isolation verification tests.
# Run: pytest tests/test_network_isolation.py -v
#
# These tests verify that workzone network isolation is correctly enforced.
# In a real deployment, some tests require actual network infrastructure.

import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from services.red_team_agent import AgentGuardrails


# -- Unit tests: guardrail logic -------------------------------------------

class TestGuardrailNetworkScope:
    """Test that the agent guardrails correctly enforce network scope."""

    def setup_method(self):
        self.guardrails = AgentGuardrails(
            allowed_networks=["10.100.0.0/16"],
            max_iterations=10,
        )

    def test_target_in_scope_allowed(self):
        assert self.guardrails.check_target("10.100.1.50") is True

    def test_target_out_of_scope_blocked(self):
        """Targets outside the workzone network must be rejected."""
        assert self.guardrails.check_target("192.168.1.1") is False

    def test_management_network_blocked(self):
        """Management network (10.0.0.x) should not be in attack scope."""
        guardrails = AgentGuardrails(allowed_networks=["10.100.0.0/16"])
        assert guardrails.check_target("10.0.0.1") is False

    def test_localhost_blocked(self):
        assert self.guardrails.check_target("127.0.0.1") is False

    def test_public_ip_blocked(self):
        """No external targets — Cyber Range is isolated."""
        assert self.guardrails.check_target("8.8.8.8") is False


class TestGuardrailIterationLimit:
    """Test iteration budget enforcement."""

    def test_within_budget(self):
        guardrails = AgentGuardrails(max_iterations=5)
        guardrails.current_iteration = 3
        assert guardrails.check_iteration_limit() is True

    def test_at_budget_limit(self):
        guardrails = AgentGuardrails(max_iterations=5)
        guardrails.current_iteration = 5
        assert guardrails.check_iteration_limit() is False

    def test_over_budget(self):
        guardrails = AgentGuardrails(max_iterations=5)
        guardrails.current_iteration = 10
        assert guardrails.check_iteration_limit() is False


class TestGuardrailKillSwitch:
    """Test emergency kill switch."""

    def test_kill_switch_default_off(self):
        guardrails = AgentGuardrails()
        assert guardrails.kill_switch is False

    def test_kill_switch_activation(self):
        guardrails = AgentGuardrails()
        guardrails.activate_kill_switch()
        assert guardrails.kill_switch is True


class TestGuardrailAuditLog:
    """Test that all actions are logged for audit trail."""

    def test_action_logging(self):
        guardrails = AgentGuardrails()
        guardrails.log_action("nmap_scan", "10.100.1.50", "3 open ports found")
        assert len(guardrails.action_log) == 1
        assert guardrails.action_log[0]["tool"] == "nmap_scan"

    def test_log_truncates_long_results(self):
        guardrails = AgentGuardrails()
        long_result = "x" * 1000
        guardrails.log_action("exploit", "10.100.1.50", long_result)
        assert len(guardrails.action_log[0]["result_summary"]) <= 500


# -- Integration tests (require network infrastructure) --------------------
# These are marked with @pytest.mark.integration and skipped by default.
# Run with: pytest -m integration

@pytest.mark.integration
class TestVLANIsolation:
    """
    Verify VLAN-level isolation between workzones.

    Chapter 8: each workzone runs on a separate VLAN.
    VMs in VLAN 101 should NOT be able to reach VMs in VLAN 102.
    """

    @pytest.mark.skip(reason="Requires live network infrastructure")
    def test_cross_vlan_ping_blocked(self):
        """VMs in different VLANs cannot reach each other."""
        # In a real test, this would SSH into a VM and attempt a ping
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", "10.100.102.10"],
            capture_output=True,
            timeout=5,
        )
        assert result.returncode != 0, "Cross-VLAN traffic should be blocked"

    @pytest.mark.skip(reason="Requires live network infrastructure")
    def test_same_vlan_ping_allowed(self):
        """VMs in the same VLAN can communicate."""
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", "10.100.101.10"],
            capture_output=True,
            timeout=5,
        )
        assert result.returncode == 0, "Same-VLAN traffic should be allowed"

    @pytest.mark.skip(reason="Requires live network infrastructure")
    def test_management_network_reachable(self):
        """Management network can reach workzone VMs (for provisioning)."""
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "2", "10.100.101.10"],
            capture_output=True,
            timeout=5,
        )
        assert result.returncode == 0
