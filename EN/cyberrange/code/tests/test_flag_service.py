# Companion code for "The Cyber Range and the Machine" — Testing Chapter
# Pytest tests for flag generation and validation.
# Run: pytest tests/test_flag_service.py -v

import os
import sys

import pytest

# Add backend to path so we can import the service
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from services.flag_service import (
    calculate_dynamic_score,
    generate_flag,
    hash_flag,
    is_valid_flag_format,
    validate_flag,
    validate_flag_by_hash,
)


class TestFlagGeneration:
    """Test dynamic flag generation (Chapter 12)."""

    def test_flag_has_correct_prefix(self):
        flag = generate_flag(challenge_id=1, instance_id=100)
        assert flag.startswith("CYBERRANGE{")
        assert flag.endswith("}")

    def test_flag_is_deterministic_with_same_salt(self):
        """Same inputs + same salt = same flag (for reproducibility)."""
        flag1 = generate_flag(challenge_id=1, instance_id=100, salt="fixed-salt")
        flag2 = generate_flag(challenge_id=1, instance_id=100, salt="fixed-salt")
        assert flag1 == flag2

    def test_different_instances_produce_different_flags(self):
        """Each instance gets a unique flag (Chapter 12: no flag sharing)."""
        flag1 = generate_flag(challenge_id=1, instance_id=100, salt="salt-a")
        flag2 = generate_flag(challenge_id=1, instance_id=200, salt="salt-b")
        assert flag1 != flag2

    def test_flag_length_is_consistent(self):
        flag = generate_flag(challenge_id=1, instance_id=1, salt="test")
        # PREFIX{ + 32 hex chars + }
        expected_len = len("CYBERRANGE") + 1 + 32 + 1
        assert len(flag) == expected_len


class TestFlagValidation:
    """Test flag validation with timing-safe comparison (Chapter 12)."""

    def test_correct_flag_validates(self):
        flag = generate_flag(challenge_id=1, instance_id=1, salt="test")
        assert validate_flag(flag, flag) is True

    def test_wrong_flag_rejects(self):
        flag = generate_flag(challenge_id=1, instance_id=1, salt="test")
        assert validate_flag("CYBERRANGE{wrong}", flag) is False

    def test_whitespace_is_trimmed(self):
        flag = generate_flag(challenge_id=1, instance_id=1, salt="test")
        assert validate_flag(f"  {flag}  ", flag) is True

    def test_hash_validation_works(self):
        flag = generate_flag(challenge_id=1, instance_id=1, salt="test")
        stored_hash = hash_flag(flag)
        assert validate_flag_by_hash(flag, stored_hash) is True

    def test_hash_validation_rejects_wrong_flag(self):
        flag = generate_flag(challenge_id=1, instance_id=1, salt="test")
        stored_hash = hash_flag(flag)
        assert validate_flag_by_hash("CYBERRANGE{wrong}", stored_hash) is False


class TestFlagFormat:
    """Test flag format validation."""

    def test_valid_format_accepted(self):
        flag = generate_flag(challenge_id=1, instance_id=1, salt="test")
        assert is_valid_flag_format(flag) is True

    def test_wrong_prefix_rejected(self):
        assert is_valid_flag_format("FLAG{abcdef1234567890abcdef1234567890}") is False

    def test_empty_string_rejected(self):
        assert is_valid_flag_format("") is False

    def test_missing_braces_rejected(self):
        assert is_valid_flag_format("CYBERRANGEabcdef1234567890") is False


class TestDynamicScoring:
    """Test dynamic score calculation (Chapter 12)."""

    def test_first_solve_gets_full_points(self):
        score = calculate_dynamic_score(base_points=500, total_solves=0)
        assert score == 500

    def test_score_decreases_with_solves(self):
        score_1 = calculate_dynamic_score(base_points=500, total_solves=1)
        score_10 = calculate_dynamic_score(base_points=500, total_solves=10)
        assert score_1 > score_10

    def test_score_never_below_minimum(self):
        score = calculate_dynamic_score(
            base_points=500, total_solves=1000, min_points=50,
        )
        assert score >= 50

    def test_custom_decay_rate(self):
        fast_decay = calculate_dynamic_score(base_points=500, total_solves=5, decay=0.80)
        slow_decay = calculate_dynamic_score(base_points=500, total_solves=5, decay=0.98)
        assert fast_decay < slow_decay
