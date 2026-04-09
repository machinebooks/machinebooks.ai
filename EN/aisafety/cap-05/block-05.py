# Extracted from: LibroAISafety/ch-05-system-prompt.md
# System prompt versioning pattern
from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256

@dataclass
class SystemPromptVersion:
    """An immutable version of the system prompt."""
    version: str                  # Semver: "2.3.1"
    content: str                  # The complete prompt
    author: str                   # Who made the change
    reason: str                   # Why it was changed
    created_at: datetime = field(default_factory=datetime.now)
    security_review: bool = False # Did it pass security review?
    tests_passed: bool = False    # Did it pass the regression battery?
    content_hash: str = ""        # Hash for integrity verification

    def __post_init__(self):
        self.content_hash = sha256(
            self.content.encode()
        ).hexdigest()[:16]

@dataclass
class PromptRollbackManager:
    """Manages versions and allows rapid rollback."""
    versions: list[SystemPromptVersion] = field(default_factory=list)
    active_version: str = ""

    def deploy(self, version: str) -> bool:
        """Deploys a specific version as active."""
        target = next((v for v in self.versions if v.version == version), None)
        if not target:
            return False
        if not target.security_review or not target.tests_passed:
            raise ValueError(
                f"Version {version} not approved: "
                f"security={target.security_review}, "
                f"tests={target.tests_passed}"
            )
        self.active_version = version
        return True

    def rollback(self) -> str:
        """Reverts to the previous approved version."""
        approved = [v for v in self.versions
                    if v.security_review and v.tests_passed]
        if len(approved) < 2:
            raise ValueError("No previous approved version available")
        # The second-to-last approved version
        previous = approved[-2]
        self.active_version = previous.version
        return previous.version
