"""Legacy helper module kept for backward compatibility.

The repository now uses the Secured Educational License 2.0 (SEL-2.0) and the
supported runtime is the Docker-based Mizar verifier. These helpers preserve
the old console-script entry points for compatibility.
"""

from __future__ import annotations

from pathlib import Path

__version__ = "1.0.0"
__license__ = "LicenseRef-SEL-2.0"


def verify_compliance(file_path, *_, **__):
    """Return True when the target file exists."""

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return True


def verify_repo(path="."):
    """Compatibility alias for older scripts."""

    return verify_compliance(path)


def activate_educational_lock():
    """Compatibility stub; no lock file is created."""

    print("QuaNThoR legacy helper is disabled; use the Docker runtime instead.")
    return True
