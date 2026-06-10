"""Legacy helper module kept for backward compatibility.

The repository now uses Apache-2.0 and the supported runtime is the
Docker-based Mizar verifier. These helpers no longer enforce any custom
license scheme; they only preserve the old console-script entry points.
"""

from __future__ import annotations

from pathlib import Path

__version__ = "1.0.0"
__license__ = "Apache-2.0"


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
